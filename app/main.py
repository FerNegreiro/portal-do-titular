import os
from functools import wraps

from flask import Flask, jsonify, render_template, request

from app.demo import CaixaDeEntrada, RelogioAjustavel
from app.regras import RegraViolada, ServicoSolicitacoes, Status, mascarar_cpf


def criar_app(
    servico: ServicoSolicitacoes | None = None,
    token_backoffice: str | None = None,
    modo_demo: bool = False,
) -> Flask:
    app = Flask(__name__)
    app.json.ensure_ascii = False
    app.json.sort_keys = False
    app.json.mimetype = "application/json; charset=utf-8"
    token = token_backoffice or os.environ.get("BACKOFFICE_TOKEN", "dev-token")

    relogio = None
    caixa = None
    if servico is None:
        relogio = RelogioAjustavel()
        caixa = CaixaDeEntrada(relogio)
        servico = ServicoSolicitacoes(enviar_email=caixa, relogio=relogio)
    demo_ativo = modo_demo and caixa is not None

    def ler_json() -> dict:
        if not request.get_data():
            return {}
        dados = request.get_json(silent=True, force=True)
        if not isinstance(dados, dict):
            raise RegraViolada(
                "API",
                "JSON inválido. Envie um objeto JSON codificado em UTF-8.",
                400,
            )
        return dados

    def visao_titular(s):
        agora = servico.agora()
        corpo = {
            "protocolo": s.protocolo,
            "tipo": s.tipo.value,
            "status": s.status.value,
            "cpf": mascarar_cpf(s.cpf),
            "aberta_em": s.criada_em.isoformat(timespec="seconds"),
        }
        if s.prazo:
            corpo["prazo"] = s.prazo.date().isoformat()
            corpo["dias_restantes"] = s.dias_restantes(agora)
        if s.status == Status.CONCLUIDA:
            corpo["resposta"] = s.resposta
        return corpo

    def visao_dpo(s):
        corpo = visao_titular(s)
        corpo["alerta_prazo"] = s.em_alerta(servico.agora())
        return corpo

    def exige_backoffice(rota):
        @wraps(rota)
        def protegida(*args, **kwargs):
            if request.headers.get("X-Backoffice-Token") != token:
                return jsonify({"erro": "Acesso restrito ao backoffice"}), 401
            return rota(*args, **kwargs)
        return protegida

    @app.errorhandler(RegraViolada)
    def tratar_regra(erro: RegraViolada):
        return jsonify({"regra": erro.regra, "erro": erro.mensagem, **erro.extras}), erro.http_status

    @app.post("/v1/solicitacoes")
    def abrir():
        dados = ler_json()
        s = servico.abrir(dados.get("cpf", ""), dados.get("email", ""), dados.get("tipo", ""))
        return jsonify({
            **visao_titular(s),
            "mensagem": "Enviamos um código de verificação para o seu e-mail. Ele vale por 10 minutos.",
        }), 201

    @app.get("/v1/solicitacoes/<protocolo>")
    def consultar(protocolo):
        return jsonify(visao_titular(servico.buscar(protocolo)))

    @app.post("/v1/solicitacoes/<protocolo>/validacao")
    def validar(protocolo):
        dados = ler_json()
        s = servico.validar_identidade(protocolo, str(dados.get("codigo", "")))
        return jsonify(visao_titular(s))

    @app.post("/v1/solicitacoes/<protocolo>/reenvio-codigo")
    def reenviar(protocolo):
        servico.reenviar_codigo(protocolo)
        return jsonify({"mensagem": "Novo código enviado."}), 202

    @app.get("/v1/backoffice/fila")
    @exige_backoffice
    def fila():
        itens = [visao_dpo(s) for s in servico.fila_do_dpo()]
        return jsonify({"total": len(itens), "em_alerta": sum(i["alerta_prazo"] for i in itens), "itens": itens})

    @app.post("/v1/backoffice/solicitacoes/<protocolo>/conclusao")
    @exige_backoffice
    def concluir(protocolo):
        dados = ler_json()
        s = servico.concluir(protocolo, dados.get("resposta", ""))
        return jsonify(visao_dpo(s))

    @app.get("/v1/backoffice/solicitacoes/<protocolo>/auditoria")
    @exige_backoffice
    def auditoria(protocolo):
        s = servico.buscar(protocolo)
        return jsonify({
            "protocolo": s.protocolo,
            "eventos": [
                {"momento": e.momento.isoformat(timespec="seconds"), "ator": e.ator, "acao": e.acao, "detalhe": e.detalhe}
                for e in s.auditoria
            ],
        })

    @app.get("/")
    def pagina_demo():
        return render_template("demo.html", modo_demo=demo_ativo, token=token if demo_ativo else "")

    @app.get("/v1")
    def indice_api():
        return jsonify({
            "projeto": "Portal do Titular — API de Solicitações LGPD",
            "versao": "1.2.0",
            "endpoints": {
                "abrir_solicitacao": "POST /v1/solicitacoes",
                "consultar": "GET /v1/solicitacoes/<protocolo>",
                "validar_identidade": "POST /v1/solicitacoes/<protocolo>/validacao",
                "reenviar_codigo": "POST /v1/solicitacoes/<protocolo>/reenvio-codigo",
                "fila_dpo": "GET /v1/backoffice/fila",
                "concluir": "POST /v1/backoffice/solicitacoes/<protocolo>/conclusao",
                "auditoria": "GET /v1/backoffice/solicitacoes/<protocolo>/auditoria",
            },
            "documentacao": "api/openapi.yaml",
        })

    if demo_ativo:
        @app.get("/demo/caixa-de-entrada")
        def caixa_de_entrada():
            return jsonify({"mensagens": list(caixa.mensagens)})

        @app.get("/demo/tempo")
        def tempo_atual():
            return jsonify({"agora": servico.agora().isoformat(timespec="seconds")})

        @app.post("/demo/tempo")
        def avancar_tempo():
            dados = ler_json()
            dias = dados.get("dias")
            if not isinstance(dias, int) or not 1 <= dias <= 30:
                raise RegraViolada("DEMO", "Informe um número inteiro de dias entre 1 e 30")
            relogio.avancar(dias)
            servico.encerrar_sem_validacao_expiradas()
            return jsonify({"agora": servico.agora().isoformat(timespec="seconds")})

    return app


if __name__ == "__main__":
    demo = os.environ.get("MODO_DEMO", "1") == "1"
    if demo:
        print("Modo demonstração ligado: abra http://127.0.0.1:5000 no navegador.", flush=True)
    criar_app(modo_demo=demo).run(debug=True)
