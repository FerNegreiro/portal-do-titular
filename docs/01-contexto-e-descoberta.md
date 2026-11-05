# 01 — Contexto e descoberta

## Situação atual

A Aurora Varejo coleta dados pessoais em três frentes: cadastro no programa Aurora+, compras com CPF na nota e campanhas de marketing. Desde a entrada em vigor das sanções da LGPD, o volume de pedidos de titulares cresceu de forma constante:

| Indicador (últimos 6 meses) | Valor |
|---|---|
| Solicitações recebidas por mês | ~1.900 |
| Canais de entrada | e-mail do DPO, SAC 0800, Instagram, lojas |
| Respondidas dentro de 15 dias | 62% |
| Tempo médio de resposta | 11 dias |
| Pessoas dedicadas no time do DPO | 4 |
| Sistemas consultados manualmente por pedido | 5 (CRM, ERP, e-commerce, marketing, BI) |

Dois pedidos tiveram reclamação formal na ANPD no último trimestre. É isso que colocou o tema na pauta da diretoria.

## Stakeholders

| Stakeholder | Interesse principal | Influência | Estratégia |
|---|---|---|---|
| Diretora Jurídica (patrocinadora) | Zerar risco regulatório | Alta | Envolver nas decisões de escopo |
| DPO / Encarregada de Dados | Reduzir trabalho manual e ter auditoria | Alta | Validação semanal |
| Diretor de TI | Não criar mais um sistema difícil de manter | Alta | Revisão de arquitetura |
| Gerente de CRM e Marketing | Não perder base de clientes com exclusões indevidas | Média | Workshop de regras de negócio |
| Coordenação do SAC | Parar de receber pedidos que não sabe tratar | Média | Entrevistas e testes de usabilidade |
| Titular (cliente) | Resolver rápido, sem burocracia | Baixa individual, alta coletiva | Pesquisa e protótipo |

## Entrevistas em profundidade

Foram conduzidas 9 entrevistas de 45 minutos, com roteiro semiestruturado e a técnica dos **5 porquês** para chegar à causa raiz.

### Roteiro base

1. Me conte, passo a passo, como foi o último pedido de titular que você tratou.
2. Em que momento você precisou parar e esperar alguém?
3. O que acontece quando um pedido chega incompleto?
4. Se tivesse uma varinha mágica, qual etapa sumiria?
5. O que te daria segurança para dizer que o pedido foi cumprido?

### Exemplo de 5 porquês (DPO)

> **Por que os pedidos atrasam?** Porque dependem de respostas de outras áreas.
> **Por quê?** Porque cada área tem uma parte dos dados do cliente.
> **Por quê?** Porque não existe um cadastro único consultável.
> **Por quê?** Porque o CRM não recebe as compras feitas sem login no e-commerce.
> **Por quê?** Porque a integração ERP → CRM só envia clientes do programa Aurora+.
>
> **Causa raiz:** falta de uma visão unificada do titular entre sistemas.

### Principais achados

| # | Achado | Evidência | Impacto |
|---|---|---|---|
| A1 | 30% dos pedidos chegam sem dados para identificar o titular | Planilha do DPO | Retrabalho e atraso |
| A2 | Não há validação de identidade, só "confiança" no e-mail | Entrevista SAC | Risco de vazamento para terceiros |
| A3 | Exclusão é feita em 3 sistemas e esquecida no quarto | Entrevista TI | Descumprimento e reincidência |
| A4 | O Marketing exclui o cliente, mas ele volta na próxima importação | Entrevista CRM | Cliente reclama de novo |
| A5 | Não existe registro de quando o pedido foi concluído | Auditoria interna | Sem prova para a ANPD |

## Declaração do problema

> **O problema de** atender pedidos de titulares de forma manual e fragmentada
> **afeta** clientes, o time do DPO e a diretoria jurídica,
> **cujo impacto é** descumprimento de prazos legais, risco de sanções e retrabalho,
> **uma boa solução seria** um portal de autoatendimento com validação de identidade, orquestração automática entre sistemas e trilha de auditoria completa.
