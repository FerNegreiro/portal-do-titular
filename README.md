# Portal do Titular — Autoatendimento LGPD da Aurora Varejo

> Estudo de caso completo de **análise de negócios e engenharia de requisitos**: da descoberta com a diretoria até a proposta comercial, a especificação da API e um MVP funcional com critérios de aceite em BDD.

**Empresa fictícia:** Aurora Varejo, rede com 120 lojas e 4,2 milhões de clientes no programa de fidelidade **Aurora+**.

**Problema:** pedidos de titulares de dados (acesso, correção, exclusão, portabilidade, revogação de consentimento) chegam por e-mail, SAC e redes sociais, são tratados manualmente pelo time do DPO numa planilha e **38% estouram o prazo de 15 dias** previsto na LGPD.

**Solução proposta:** um portal de autoatendimento onde o próprio cliente abre, acompanha e recebe a resposta das solicitações, com orquestração automática entre CRM, ERP e plataforma de marketing.

---

## O que este projeto demonstra

| Competência | Onde ver |
|---|---|
| Contexto, stakeholders e entrevistas em profundidade | [01 — Contexto e descoberta](docs/01-contexto-e-descoberta.md) |
| Lean Inception e Design Thinking (workshop com a diretoria) | [02 — Lean Inception](docs/02-lean-inception.md) |
| Requisitos funcionais, não-funcionais, regras de negócio, restrições e rastreabilidade | [03 — Requisitos](docs/03-requisitos.md) |
| Modelagem BPMN AS-IS e TO-BE | [04 — Processos BPMN](docs/04-processos-bpmn.md) |
| Arquitetura funcional, integrações e análise de impacto | [05 — Arquitetura e integrações](docs/05-arquitetura-e-integracoes.md) |
| Backlog, fatiamento, MoSCoW, RICE e WSJF | [06 — Backlog e priorização](docs/06-backlog-e-priorizacao.md) |
| Pré-venda, estimativa, precificação e proposta | [07 — Proposta comercial](docs/07-proposta-comercial.md) |
| Governança Scrum/Kanban e gestão de mudanças | [08 — Gestão ágil](docs/08-gestao-agil.md) |
| Contrato de API (OpenAPI 3) | [api/openapi.yaml](api/openapi.yaml) |
| Critérios de aceite em BDD (Gherkin) | [features/](features/) |
| MVP funcional em Python que implementa as regras de negócio | [app/](app/) e [tests/](tests/) |

---

## Linha do tempo do caso

```mermaid
flowchart TB
    subgraph F1[Descoberta e especificação]
        direction LR
        A[Entrevistas em<br/>profundidade] --> B[Lean Inception<br/>5 dias] --> C[Requisitos e<br/>regras de negócio] --> D[BPMN AS-IS<br/>e TO-BE]
    end
    subgraph F2[Planejamento e entrega]
        direction LR
        E[Arquitetura e<br/>contratos de API] --> F[Backlog priorizado<br/>WSJF] --> G[Proposta<br/>comercial] --> H[MVP + BDD]
    end
    F1 --> F2
```

## Resultados esperados (metas acordadas com a diretoria)

- Solicitações respondidas dentro do prazo legal: **de 62% para 98%**
- Tempo médio de atendimento: **de 11 para 3 dias**
- Esforço manual do time do DPO: **redução de 70%**
- 100% das solicitações com trilha de auditoria para fiscalização da ANPD

---

## Rodando o MVP

Requisitos: Python 3.10+.

### Windows (PowerShell)

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m unittest discover -s tests -v
python -m app.main
```

A API sobe em `http://127.0.0.1:5000`. Deixe esse terminal rodando: ele também faz o papel da caixa de e-mail, mostrando os códigos de verificação. Abra um **segundo terminal** para os comandos abaixo.

```powershell
$base = "http://127.0.0.1:5000/v1"
$h = @{"X-Backoffice-Token"="dev-token"}

$r = Invoke-RestMethod -Method Post -Uri "$base/solicitacoes" -ContentType "application/json" -Body '{"cpf":"52998224725","email":"ana@email.com","tipo":"ACESSO"}'
$r
```

Pegue o código de 6 dígitos no terminal do servidor e valide a identidade:

```powershell
Invoke-RestMethod -Method Post -Uri "$base/solicitacoes/$($r.protocolo)/validacao" -ContentType "application/json" -Body '{"codigo":"123456"}'
```

Fila do DPO, conclusão e trilha de auditoria:

```powershell
Invoke-RestMethod -Uri "$base/backoffice/fila" -Headers $h | ConvertTo-Json -Depth 5

$corpo = [System.Text.Encoding]::UTF8.GetBytes('{"resposta":"Segue o relatório com todos os seus dados."}')
Invoke-RestMethod -Method Post -Uri "$base/backoffice/solicitacoes/$($r.protocolo)/conclusao" -ContentType "application/json; charset=utf-8" -Headers $h -Body $corpo

Invoke-RestMethod -Uri "$base/backoffice/solicitacoes/$($r.protocolo)/auditoria" -Headers $h | ConvertTo-Json -Depth 5
```

> **Atenção ao UTF-8:** o Windows PowerShell 5.1 não envia texto em UTF-8 por padrão. Textos com acento devem ser convertidos com `[System.Text.Encoding]::UTF8.GetBytes(...)`, como no exemplo da conclusão. Sem isso, a API responde **400 — JSON inválido**. Veja o [CHANGELOG](CHANGELOG.md) para o histórico desse problema.

Erros de regra de negócio aparecem em vermelho no PowerShell, com o código da regra violada (ex.: `RN04`). Isso é esperado.

### Linux e macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m unittest discover -s tests -v
python -m app.main
```

```bash
curl -X POST http://127.0.0.1:5000/v1/solicitacoes \
  -H "Content-Type: application/json" \
  -d '{"cpf": "52998224725", "email": "ana@email.com", "tipo": "ACESSO"}'
```

### Testes

São 24 testes automatizados, e cada um referencia a regra de negócio que valida.

> Os dados ficam em memória: ao reiniciar o servidor (inclusive ao salvar um arquivo `.py` com o modo debug ligado), as solicitações são apagadas.

### Cobertura dos critérios de aceite

| Feature | Status no MVP |
|---|---|
| `abertura_de_solicitacao.feature` | Automatizada em `tests/test_regras.py` |
| `validacao_de_identidade.feature` | Automatizada em `tests/test_regras.py` |
| `prazos_e_alertas.feature` | Automatizada em `tests/test_regras.py` |
| `revogacao_de_consentimento.feature` | Especificada; depende da integração INT04 |
| `exclusao_de_dados.feature` | Especificada; onda 2 |

Os nomes dos testes começam com o código do requisito ou da regra (`test_rn05_...`), fechando a rastreabilidade de ponta a ponta: **achado → requisito → regra → história → cenário → teste**.

## Estrutura

```
portal-do-titular/
├── README.md
├── docs/            estudo de caso, requisitos, BPMN, backlog e proposta
├── api/             contrato OpenAPI 3
├── features/        critérios de aceite em Gherkin (BDD)
├── app/             MVP em Flask com as regras de negócio isoladas
└── tests/           testes automatizados rastreados às regras
```

---

**Autor:** Fernando Negreiro — [github.com/FerNegreiro](https://github.com/FerNegreiro)

*Empresa, pessoas e números são fictícios, criados para fins de portfólio.*