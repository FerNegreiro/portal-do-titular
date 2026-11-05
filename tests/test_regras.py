import unittest
from datetime import datetime, timedelta

from app.main import criar_app
from app.regras import ServicoSolicitacoes, cpf_valido, mascarar_cpf

CPF = "529.982.247-25"
OUTRO_CPF = "111.444.777-35"
TOKEN = "teste"


class Relogio:
    def __init__(self):
        self.atual = datetime(2026, 11, 2, 9, 0, 0)

    def __call__(self):
        return self.atual

    def avancar(self, **kwargs):
        self.atual += timedelta(**kwargs)


class Base(unittest.TestCase):
    def setUp(self):
        self.relogio = Relogio()
        self.emails = []
        self.codigos = iter(["111111", "222222", "333333", "444444"])
        self.servico = ServicoSolicitacoes(
            enviar_email=lambda destino, msg: self.emails.append((destino, msg)),
            relogio=self.relogio,
            gerar_codigo=lambda: next(self.codigos),
        )
        self.cliente = criar_app(self.servico, token_backoffice=TOKEN).test_client()
        self.dpo = {"X-Backoffice-Token": TOKEN}

    def abrir(self, cpf=CPF, tipo="ACESSO", email="ana@email.com"):
        return self.cliente.post("/v1/solicitacoes", json={"cpf": cpf, "email": email, "tipo": tipo})

    def validar(self, protocolo, codigo):
        return self.cliente.post(f"/v1/solicitacoes/{protocolo}/validacao", json={"codigo": codigo})


class TestAbertura(Base):
    def test_rf01_abre_solicitacao_e_envia_codigo(self):
        r = self.abrir()
        self.assertEqual(r.status_code, 201)
        self.assertEqual(r.json["status"], "AGUARDANDO_VALIDACAO")
        self.assertTrue(r.json["protocolo"].startswith("LGPD-2026-"))
        self.assertIn("111111", self.emails[0][1])

    def test_rn03_rejeita_cpf_invalido(self):
        r = self.abrir(cpf="123.456.789-00")
        self.assertEqual(r.status_code, 422)
        self.assertEqual(r.json["regra"], "RN03")

    def test_rn04_bloqueia_duplicidade_do_mesmo_tipo(self):
        primeiro = self.abrir().json["protocolo"]
        r = self.abrir()
        self.assertEqual(r.status_code, 409)
        self.assertEqual(r.json["regra"], "RN04")
        self.assertEqual(r.json["protocolo_existente"], primeiro)

    def test_rn04_permite_tipos_diferentes_para_o_mesmo_cpf(self):
        self.abrir(tipo="ACESSO")
        self.assertEqual(self.abrir(tipo="REVOGACAO_CONSENTIMENTO").status_code, 201)

    def test_rnf04_cpf_nunca_aparece_completo(self):
        r = self.abrir()
        self.assertEqual(r.json["cpf"], "***.982.247-**")
        self.assertNotIn("52998224725", r.get_data(as_text=True))


class TestIdentidade(Base):
    def test_rn01_prazo_de_15_dias_comeca_na_validacao(self):
        p = self.abrir().json["protocolo"]
        self.relogio.avancar(minutes=5)
        r = self.validar(p, "111111")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json["status"], "EM_ANDAMENTO")
        self.assertEqual(r.json["prazo"], "2026-11-17")

    def test_rn05_informa_tentativas_restantes(self):
        p = self.abrir().json["protocolo"]
        r = self.validar(p, "000000")
        self.assertEqual(r.status_code, 422)
        self.assertEqual(r.json["tentativas_restantes"], 2)

    def test_rn05_encerra_apos_tres_erros(self):
        p = self.abrir().json["protocolo"]
        self.validar(p, "000000")
        self.validar(p, "000000")
        r = self.validar(p, "000000")
        self.assertEqual(r.status_code, 423)
        self.assertEqual(self.cliente.get(f"/v1/solicitacoes/{p}").json["status"], "ENCERRADA_SEM_VALIDACAO")
        self.assertEqual(self.validar(p, "111111").status_code, 409)

    def test_rn05_codigo_expira_em_10_minutos(self):
        p = self.abrir().json["protocolo"]
        self.relogio.avancar(minutes=11)
        r = self.validar(p, "111111")
        self.assertEqual(r.status_code, 422)
        self.assertIn("expirado", r.json["erro"])

    def test_rn05_reenvio_gera_novo_codigo_e_invalida_o_anterior(self):
        p = self.abrir().json["protocolo"]
        self.relogio.avancar(minutes=11)
        self.cliente.post(f"/v1/solicitacoes/{p}/reenvio-codigo")
        self.assertEqual(self.validar(p, "111111").status_code, 422)
        self.assertEqual(self.validar(p, "222222").status_code, 200)

    def test_rn09_encerra_apos_7_dias_sem_validacao(self):
        p = self.abrir().json["protocolo"]
        self.relogio.avancar(days=8)
        self.cliente.get("/v1/backoffice/fila", headers=self.dpo)
        self.assertEqual(self.cliente.get(f"/v1/solicitacoes/{p}").json["status"], "ENCERRADA_SEM_VALIDACAO")
        self.assertEqual(self.abrir().status_code, 201)


class TestBackoffice(Base):
    def abrir_validada(self, cpf=CPF, tipo="ACESSO"):
        p = self.abrir(cpf=cpf, tipo=tipo).json["protocolo"]
        codigo = self.emails[-1][1].split()[-1]
        self.validar(p, codigo)
        return p

    def test_backoffice_exige_token(self):
        self.assertEqual(self.cliente.get("/v1/backoffice/fila").status_code, 401)

    def test_rf05_fila_ordenada_pelo_prazo(self):
        antiga = self.abrir_validada(cpf=CPF)
        self.relogio.avancar(days=2)
        nova = self.abrir_validada(cpf=OUTRO_CPF)
        itens = self.cliente.get("/v1/backoffice/fila", headers=self.dpo).json["itens"]
        self.assertEqual([i["protocolo"] for i in itens], [antiga, nova])

    def test_rn08_alerta_quando_faltam_3_dias(self):
        self.abrir_validada()
        self.relogio.avancar(days=11)
        self.assertFalse(self.cliente.get("/v1/backoffice/fila", headers=self.dpo).json["itens"][0]["alerta_prazo"])
        self.relogio.avancar(days=1)
        fila = self.cliente.get("/v1/backoffice/fila", headers=self.dpo).json
        self.assertTrue(fila["itens"][0]["alerta_prazo"])
        self.assertEqual(fila["em_alerta"], 1)

    def test_rn02_nao_conclui_sem_identidade_validada(self):
        p = self.abrir().json["protocolo"]
        r = self.cliente.post(f"/v1/backoffice/solicitacoes/{p}/conclusao", json={"resposta": "ok"}, headers=self.dpo)
        self.assertEqual(r.status_code, 409)
        self.assertEqual(r.json["regra"], "RN02")

    def test_conclusao_entrega_resposta_ao_titular(self):
        p = self.abrir_validada()
        self.cliente.post(f"/v1/backoffice/solicitacoes/{p}/conclusao", json={"resposta": "Segue relatório."}, headers=self.dpo)
        r = self.cliente.get(f"/v1/solicitacoes/{p}").json
        self.assertEqual(r["status"], "CONCLUIDA")
        self.assertEqual(r["resposta"], "Segue relatório.")

    def test_rn10_trilha_de_auditoria_completa(self):
        p = self.abrir_validada()
        self.cliente.post(f"/v1/backoffice/solicitacoes/{p}/conclusao", json={"resposta": "ok"}, headers=self.dpo)
        eventos = self.cliente.get(f"/v1/backoffice/solicitacoes/{p}/auditoria", headers=self.dpo).json["eventos"]
        self.assertEqual(
            [e["acao"] for e in eventos],
            ["ABERTURA", "CODIGO_ENVIADO", "IDENTIDADE_VALIDADA", "CONCLUSAO"],
        )
        self.assertEqual(eventos[-1]["detalhe"], "dentro do prazo")


class TestCorrecoesDoTesteManual(Base):
    def test_dias_restantes_conta_por_data_do_calendario(self):
        p = self.abrir().json["protocolo"]
        self.relogio.avancar(minutes=5)
        self.validar(p, "111111")
        self.relogio.avancar(minutes=5)
        self.assertEqual(self.cliente.get(f"/v1/solicitacoes/{p}").json["dias_restantes"], 15)

    def test_json_invalido_retorna_400(self):
        corpo = '{"cpf":"52998224725","email":"ana@email.com","tipo":"ACESSO","obs":"relatório"}'.encode("latin-1")
        r = self.cliente.post("/v1/solicitacoes", data=corpo, content_type="application/json")
        self.assertEqual(r.status_code, 400)
        self.assertEqual(r.json["regra"], "API")

    def test_json_malformado_retorna_400(self):
        r = self.cliente.post("/v1/solicitacoes", data="{cpf:", content_type="application/json")
        self.assertEqual(r.status_code, 400)

    def test_respostas_declaram_utf8(self):
        r = self.abrir()
        self.assertEqual(r.headers["Content-Type"], "application/json; charset=utf-8")

    def test_acentos_chegam_intactos(self):
        p = self.abrir().json["protocolo"]
        self.validar(p, "111111")
        corpo = '{"resposta":"Segue o relatório."}'.encode("utf-8")
        self.cliente.post(f"/v1/backoffice/solicitacoes/{p}/conclusao", data=corpo, content_type="application/json", headers=self.dpo)
        self.assertEqual(self.cliente.get(f"/v1/solicitacoes/{p}").json["resposta"], "Segue o relatório.")


class TestUtilitarios(unittest.TestCase):
    def test_cpf_valido(self):
        self.assertTrue(cpf_valido(CPF))
        self.assertFalse(cpf_valido("111.111.111-11"))
        self.assertFalse(cpf_valido("123"))

    def test_mascara(self):
        self.assertEqual(mascarar_cpf("52998224725"), "***.982.247-**")


if __name__ == "__main__":
    unittest.main()