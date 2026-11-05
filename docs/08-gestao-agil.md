# 08 — Gestão ágil e facilitação

## Modelo de trabalho

| Fase | Framework | Por quê |
|---|---|---|
| Construção (ondas 1 e 2) | **Scrum** com sprints de 2 semanas | Escopo com valor incremental e prazo fixo da auditoria |
| Sustentação e pedidos do DPO | **Kanban** | Demandas imprevisíveis, foco em fluxo |

### Cerimônias Scrum

| Evento | Duração | Participantes | Saída |
|---|---|---|---|
| Planning | 2h | Time + PO | Meta da sprint e histórias selecionadas |
| Daily | 15 min | Time | Impedimentos visíveis |
| Refinamento | 1h semanal | Time + PO + DPO | Histórias no Definition of Ready |
| Review | 1h | Time + stakeholders | Feedback sobre incremento funcionando |
| Retrospectiva | 1h | Time | Até 2 ações de melhoria |

### Quadro Kanban da sustentação

```
| Entrada | Análise (WIP 2) | Desenvolvimento (WIP 3) | Validação DPO (WIP 2) | Concluído |
```

Classes de serviço: **Expedite** para qualquer pedido com risco de prazo legal; **Padrão** para melhorias.

Métricas acompanhadas: lead time, throughput semanal e idade dos itens em andamento.

## Facilitação e workshops

### Workshop com a alta gestão (2 horas)

Formato usado para tomar a decisão entre os cenários A e B da proposta.

| Tempo | Momento | Técnica |
|---|---|---|
| 10 min | Abertura | Objetivo único na parede: "sair daqui com o escopo da onda 1 decidido" |
| 20 min | Contexto | 3 números: % no prazo hoje, reclamações na ANPD, custo do time do DPO |
| 30 min | Opções | Dois cenários lado a lado com preço, risco e o que fica de fora |
| 30 min | Discussão | **Advogado do diabo**: cada diretor defende o cenário que não prefere |
| 20 min | Decisão | **Fist of five** para medir consenso |
| 10 min | Encerramento | Decisão, dono e prazo registrados na hora |

**Princípio:** com diretoria, nunca levar problema sem opções e nunca levar opção sem preço.

### Dinâmicas de cocriação usadas

| Dinâmica | Quando | Resultado |
|---|---|---|
| **Mapa de empatia** | Dia 2 da Lean Inception | Personas Ana, Carlos e Juliana |
| **Crazy 8s** | Protótipo da tela de abertura | 3 telas no celular (RNF05) |
| **Mapa da história do usuário** | Antes do primeiro refinamento | Visão de ponta a ponta do backlog |
| **Matriz de esforço × impacto** | Brainstorming de funcionalidades | Corte inicial do MVP |
| **Dot voting** | Revisão técnica, de negócio e UX | Prioridade do grupo, sem domínio de quem fala mais alto |

## Ritos de governança

| Rito | Frequência | Participantes | Pauta |
|---|---|---|---|
| Comitê executivo | Quinzenal | Patrocinadora, Diretor de TI, PO | Riscos, pedidos de mudança, orçamento |
| Validação LGPD | Semanal | DPO, PO | Regras de negócio e casos de borda |
| Integração | Semanal | Arquiteto, donos de CRM, ERP e marketing | Status das APIs e bloqueios |
