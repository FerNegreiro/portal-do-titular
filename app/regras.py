import hashlib
import hmac
import re
import secrets
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Callable, Optional


PRAZO_LEGAL = timedelta(days=15)
JANELA_ALERTA = timedelta(days=3)
VALIDADE_CODIGO = timedelta(minutes=10)
LIMITE_SEM_VALIDACAO = timedelta(days=7)
MAX_TENTATIVAS = 3


class Tipo(str, Enum):
    CONFIRMACAO = "CONFIRMACAO"
    ACESSO = "ACESSO"
    CORRECAO = "CORRECAO"
    EXCLUSAO = "EXCLUSAO"
    PORTABILIDADE = "PORTABILIDADE"
    REVOGACAO_CONSENTIMENTO = "REVOGACAO_CONSENTIMENTO"
    INFO_COMPARTILHAMENTO = "INFO_COMPARTILHAMENTO"


class Status(str, Enum):
    AGUARDANDO_VALIDACAO = "AGUARDANDO_VALIDACAO"
    EM_ANDAMENTO = "EM_ANDAMENTO"
    CONCLUIDA = "CONCLUIDA"
    ENCERRADA_SEM_VALIDACAO = "ENCERRADA_SEM_VALIDACAO"


STATUS_EM_ABERTO = {Status.AGUARDANDO_VALIDACAO, Status.EM_ANDAMENTO}


class RegraViolada(Exception):
    def __init__(self, regra: str, mensagem: str, http_status: int = 422, extras: Optional[dict] = None):
        super().__init__(mensagem)
        self.regra = regra
        self.mensagem = mensagem
        self.http_status = http_status
        self.extras = extras or {}


def cpf_valido(cpf: str) -> bool:
    digitos = re.sub(r"\D", "", cpf or "")
    if len(digitos) != 11 or digitos == digitos[0] * 11:
        return False
    for tamanho in (9, 10):
        soma = sum(int(digitos[i]) * (tamanho + 1 - i) for i in range(tamanho))
        verificador = (soma * 10) % 11 % 10
        if verificador != int(digitos[tamanho]):
            return False
    return True


def mascarar_cpf(cpf: str) -> str:
    d = re.sub(r"\D", "", cpf)
    return f"***.{d[3:6]}.{d[6:9]}-**"


def email_valido(email: str) -> bool:
    return bool(re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email or ""))


def _hash(codigo: str) -> str:
    return hashlib.sha256(codigo.encode()).hexdigest()


@dataclass
class EventoAuditoria:
    momento: datetime
    ator: str
    acao: str
    detalhe: str


@dataclass
class Solicitacao:
    protocolo: str
    cpf: str
    email: str
    tipo: Tipo
    criada_em: datetime
    status: Status = Status.AGUARDANDO_VALIDACAO
    codigo_hash: str = ""
    codigo_expira_em: Optional[datetime] = None
    tentativas: int = 0
    prazo: Optional[datetime] = None
    resposta: Optional[str] = None
    auditoria: list = field(default_factory=list)

    def em_alerta(self, agora: datetime) -> bool:
        return (
            self.status == Status.EM_ANDAMENTO
            and self.prazo is not None
            and self.prazo - agora <= JANELA_ALERTA
        )

    def dias_restantes(self, agora: datetime) -> Optional[int]:
        if self.prazo is None:
            return None
        return (self.prazo.date() - agora.date()).days


class ServicoSolicitacoes:
    def __init__(
        self,
        enviar_email: Callable[[str, str], None],
        relogio: Callable[[], datetime] = datetime.now,
        gerar_codigo: Callable[[], str] = lambda: f"{secrets.randbelow(10**6):06d}",
    ):
        self._enviar_email = enviar_email
        self._relogio = relogio
        self._gerar_codigo = gerar_codigo
        self._solicitacoes: dict[str, Solicitacao] = {}
        self._sequencia = 0

    def _registrar(self, s: Solicitacao, ator: str, acao: str, detalhe: str = "") -> None:
        s.auditoria.append(EventoAuditoria(self._relogio(), ator, acao, detalhe))

    def _novo_protocolo(self) -> str:
        self._sequencia += 1
        return f"LGPD-{self._relogio():%Y}-{self._sequencia:06d}"

    def _emitir_codigo(self, s: Solicitacao) -> None:
        codigo = self._gerar_codigo()
        s.codigo_hash = _hash(codigo)
        s.codigo_expira_em = self._relogio() + VALIDADE_CODIGO
        self._enviar_email(s.email, f"Protocolo {s.protocolo}: seu código de verificação é {codigo}")

    def buscar(self, protocolo: str) -> Solicitacao:
        s = self._solicitacoes.get(protocolo)
        if s is None:
            raise RegraViolada("RF04", "Protocolo não encontrado", 404)
        return s

    def abrir(self, cpf: str, email: str, tipo: str) -> Solicitacao:
        if not cpf_valido(cpf):
            raise RegraViolada("RN03", "CPF inválido")
        if not email_valido(email):
            raise RegraViolada("RF01", "E-mail inválido")
        try:
            tipo_enum = Tipo(tipo)
        except ValueError:
            raise RegraViolada("RF01", f"Tipo de solicitação inválido: {tipo}")

        cpf_limpo = re.sub(r"\D", "", cpf)
        self.encerrar_sem_validacao_expiradas()
        for existente in self._solicitacoes.values():
            if existente.cpf == cpf_limpo and existente.tipo == tipo_enum and existente.status in STATUS_EM_ABERTO:
                raise RegraViolada(
                    "RN04",
                    "Já existe uma solicitação em aberto deste tipo para este CPF",
                    409,
                    {"protocolo_existente": existente.protocolo},
                )

        s = Solicitacao(
            protocolo=self._novo_protocolo(),
            cpf=cpf_limpo,
            email=email,
            tipo=tipo_enum,
            criada_em=self._relogio(),
        )
        self._solicitacoes[s.protocolo] = s
        self._registrar(s, "titular", "ABERTURA", f"tipo={tipo_enum.value}")
        self._emitir_codigo(s)
        self._registrar(s, "sistema", "CODIGO_ENVIADO")
        return s

    def validar_identidade(self, protocolo: str, codigo: str) -> Solicitacao:
        s = self.buscar(protocolo)
        if s.status != Status.AGUARDANDO_VALIDACAO:
            raise RegraViolada("RN05", f"Solicitação não aguarda validação (status {s.status.value})", 409)

        agora = self._relogio()
        expirado = s.codigo_expira_em is None or agora > s.codigo_expira_em
        correto = not expirado and hmac.compare_digest(s.codigo_hash, _hash(codigo or ""))

        if correto:
            s.status = Status.EM_ANDAMENTO
            s.prazo = agora + PRAZO_LEGAL
            s.codigo_hash = ""
            self._registrar(s, "titular", "IDENTIDADE_VALIDADA", f"prazo={s.prazo:%Y-%m-%d}")
            return s

        s.tentativas += 1
        motivo = "código expirado" if expirado else "código incorreto"
        self._registrar(s, "titular", "TENTATIVA_FALHA", f"{motivo}; tentativa {s.tentativas}")

        if s.tentativas >= MAX_TENTATIVAS:
            s.status = Status.ENCERRADA_SEM_VALIDACAO
            s.codigo_hash = ""
            self._registrar(s, "sistema", "ENCERRADA_SEM_VALIDACAO", "tentativas esgotadas")
            raise RegraViolada("RN05", "Tentativas esgotadas. A solicitação foi encerrada.", 423)

        raise RegraViolada(
            "RN05",
            f"Verificação falhou: {motivo}",
            422,
            {"tentativas_restantes": MAX_TENTATIVAS - s.tentativas},
        )

    def reenviar_codigo(self, protocolo: str) -> Solicitacao:
        s = self.buscar(protocolo)
        if s.status != Status.AGUARDANDO_VALIDACAO:
            raise RegraViolada("RN05", "Solicitação não aguarda validação", 409)
        self._emitir_codigo(s)
        self._registrar(s, "titular", "CODIGO_REENVIADO")
        return s

    def concluir(self, protocolo: str, resposta: str, ator: str = "dpo") -> Solicitacao:
        s = self.buscar(protocolo)
        if s.status != Status.EM_ANDAMENTO:
            raise RegraViolada("RN02", "Só é possível concluir solicitações com identidade validada", 409)
        if not (resposta or "").strip():
            raise RegraViolada("RF05", "A resposta ao titular é obrigatória")
        s.status = Status.CONCLUIDA
        s.resposta = resposta.strip()
        self._registrar(s, ator, "CONCLUSAO", "dentro do prazo" if s.prazo is not None and self._relogio() <= s.prazo else "FORA DO PRAZO")
        self._enviar_email(s.email, f"Protocolo {s.protocolo}: sua solicitação foi concluída.")
        return s

    def encerrar_sem_validacao_expiradas(self) -> int:
        agora = self._relogio()
        encerradas = 0
        for s in self._solicitacoes.values():
            if s.status == Status.AGUARDANDO_VALIDACAO and agora - s.criada_em > LIMITE_SEM_VALIDACAO:
                s.status = Status.ENCERRADA_SEM_VALIDACAO
                s.codigo_hash = ""
                self._registrar(s, "sistema", "ENCERRADA_SEM_VALIDACAO", "7 dias sem validação")
                encerradas += 1
        return encerradas

    def fila_do_dpo(self) -> list:
        self.encerrar_sem_validacao_expiradas()
        em_andamento = [s for s in self._solicitacoes.values() if s.status == Status.EM_ANDAMENTO]
        return sorted(em_andamento, key=lambda s: s.prazo or datetime.max)

    def agora(self) -> datetime:
        return self._relogio()
