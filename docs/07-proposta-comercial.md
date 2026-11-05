# 07 — Pré-venda e proposta comercial

## Levantamento de escopo técnico-comercial

Antes de precificar, o escopo foi fechado em quatro perguntas com a patrocinadora:

| Pergunta | Resposta | Efeito no preço |
|---|---|---|
| O que precisa estar pronto para a auditoria? | Abertura, identidade, prazos, acesso e revogação | Define o MVP |
| Quem mantém a solução depois? | Time interno de TI, com repasse | Inclui documentação e *handover* |
| Os sistemas têm API? | CRM e e-commerce sim; ERP só via fornecedor | Maior risco no ERP |
| Qual o orçamento? | Até R$ 420 mil (RES04) | Força escolha de cenário |

## Estimativa

### Duração

12 semanas = 1 sprint zero (setup, arquitetura, protótipo) + 5 sprints de 2 semanas de construção + 1 semana de estabilização e repasse.

### Risco de integração com o ERP — estimativa de três pontos (PERT)

| Otimista | Mais provável | Pessimista | **Esperado = (O + 4M + P) ÷ 6** |
|---|---|---|---|
| 3 semanas | 5 semanas | 10 semanas | **5,5 semanas** |

O ERP está no caminho crítico. Por isso, o spike de integração entra já na sprint zero.

### Composição do time

Valores de venda por hora.

| Perfil | R$/hora | Cenário A — horas | Cenário A — total | Cenário B — horas | Cenário B — total |
|---|---|---|---|---|---|
| Analista de negócios / PO | 160 | 480 | 76.800 | 480 | 76.800 |
| Tech lead | 190 | 480 | 91.200 | 480 | 91.200 |
| Desenvolvedor pleno | 140 | 1.440 (3 pessoas) | 201.600 | 960 (2 pessoas) | 134.400 |
| QA | 120 | 480 | 57.600 | 360 | 43.200 |
| UX designer | 150 | 240 | 36.000 | 120 | 18.000 |
| Arquiteto de integração | 210 | 240 | 50.400 | 120 | 25.200 |
| **Subtotal** | | | **513.600** | | **388.800** |
| Contingência (10% no A, 8% no B) | | | 51.360 | | 31.104 |
| **Total** | | | **R$ 564.960** | | **R$ 419.904** |

## Cenários apresentados

| | Cenário A — Onda 1 completa | Cenário B — MVP enxuto (recomendado) |
|---|---|---|
| Escopo | US01 a US06 + US08 (auditoria exportável) | US01 a US06 |
| Prazo | 12 semanas | 12 semanas |
| Preço | R$ 564.960 | R$ 419.904 |
| Dentro do orçamento | Não | Sim |
| Risco | Menor folga para o ERP | Auditoria exportável fica para a onda 2, mas os eventos já são gravados desde o primeiro dia |

**Recomendação:** cenário B. Ele cumpre a meta da auditoria externa, respeita o orçamento e não perde dados de auditoria, porque a exportação em PDF é só uma visão sobre eventos que já estarão registrados.

## Modelo comercial

- **Preço fechado por escopo** para o cenário B, com o backlog da onda 1 congelado após a sprint zero.
- Mudanças de escopo seguem o fluxo de pedido de mudança (ver [03 — Requisitos](03-requisitos.md)) e são cobradas por hora, na tabela acima.
- **Pagamento por marco:** 20% na assinatura, 20% no fim da sprint zero, 30% na homologação do MVP, 30% na entrada em produção.

## Premissas

1. A Aurora disponibiliza acesso aos ambientes de homologação de CRM, ERP e e-commerce até o fim da sprint zero.
2. A DPO participa de 4 horas semanais de validação.
3. Infraestrutura de nuvem e licenças ficam por conta da Aurora (RES02).

## Fora do escopo

- Alterações no ERP feitas pelo fornecedor do ERP
- Migração dos pedidos históricos da planilha
- Atendimento ao titular pelo app Aurora+ (onda 3)

## Riscos

| Risco | Probabilidade | Impacto | Resposta |
|---|---|---|---|
| Fornecedor do ERP atrasa liberação da API | Alta | Alto | Spike na sprint zero; plano B com extração diária em arquivo |
| Marketing não aplica revogação em 48h | Média | Alto | Fila com confirmação via webhook (INT06) e alerta |
| Baixa adesão dos titulares ao portal | Média | Médio | SAC passa a abrir pedidos pelo portal em nome do cliente |
| Mudança de escopo da diretoria | Média | Médio | Análise de impacto formal e comitê quinzenal |
