# 06 — Backlog e priorização

## Épicos

| Épico | Objetivo | Onda |
|---|---|---|
| EP01 Entrada e identidade | Toda solicitação nasce completa e com titular validado | 1 |
| EP02 Prazos e backoffice | O DPO nunca perde um prazo | 1 |
| EP03 Direitos de baixa complexidade | Acesso e revogação resolvidos sem intervenção manual | 1 |
| EP04 Direitos de alta complexidade | Exclusão e correção orquestradas | 2 |
| EP05 Auditoria e conformidade | Prova completa para a ANPD | 2 |

## Priorização de épicos por tipo de direito (RICE)

Volume trimestral estimado a partir da planilha do DPO (~5.700 pedidos).

| Direito | Reach (pedidos/trim.) | Impact | Confidence | Effort (pessoa-mês) | **RICE** |
|---|---|---|---|---|---|
| Revogação de consentimento | 2.600 | 2 | 90% | 1 | **4.680** |
| Acesso aos dados | 1.500 | 2 | 80% | 2 | **1.200** |
| Exclusão | 1.000 | 3 | 70% | 3 | **700** |
| Correção | 500 | 1 | 80% | 1,5 | **267** |
| Portabilidade | 100 | 1 | 50% | 2 | **25** |

Revogação e acesso somam 72% do volume, o que justificou o recorte do MVP.

## Histórias de usuário

| ID | História | Épico |
|---|---|---|
| US01 | Como titular, quero abrir uma solicitação informando CPF, e-mail e o direito desejado, para não depender do SAC | EP01 |
| US02 | Como titular, quero confirmar minha identidade com um código no e-mail, para ter certeza de que ninguém pede meus dados no meu lugar | EP01 |
| US03 | Como titular, quero consultar o andamento pelo protocolo, para saber quando terei a resposta | EP01 |
| US04 | Como titular, quero receber em um único documento todos os dados que a Aurora tem sobre mim | EP03 |
| US05 | Como DPO, quero ver as solicitações ordenadas pelo prazo restante e ser alertada nos últimos 3 dias, para nunca descumprir a lei | EP02 |
| US06 | Como titular, quero revogar o consentimento de marketing e parar de receber mensagens em até 48h | EP03 |
| US07 | Como titular, quero que meus dados sejam excluídos de todos os sistemas | EP04 |
| US08 | Como DPO, quero exportar a trilha de auditoria de uma solicitação | EP05 |
| US09 | Como titular, quero baixar meus dados em formato aberto | EP04 |

Todas as histórias foram revisadas pelo checklist **INVEST** (Independente, Negociável, Valiosa, Estimável, Pequena, Testável) antes de entrar em sprint.

## Priorização de histórias (WSJF)

**WSJF = Custo do Atraso ÷ Tamanho**, onde Custo do Atraso = Valor de negócio + Criticidade de tempo + Redução de risco. Escala Fibonacci relativa.

| História | Valor de negócio | Criticidade de tempo | Redução de risco | **Custo do Atraso** | Tamanho | **WSJF** | MoSCoW |
|---|---|---|---|---|---|---|---|
| US05 Painel de prazos | 8 | 13 | 8 | 29 | 3 | **9,7** | Must |
| US06 Revogação | 8 | 8 | 5 | 21 | 3 | **7,0** | Must |
| US01 Abertura | 13 | 13 | 8 | 34 | 5 | **6,8** | Must |
| US02 Identidade | 8 | 13 | 13 | 34 | 5 | **6,8** | Must |
| US03 Consulta | 5 | 5 | 3 | 13 | 2 | **6,5** | Must |
| US08 Auditoria | 5 | 3 | 13 | 21 | 5 | **4,2** | Should |
| US04 Acesso consolidado | 13 | 8 | 8 | 29 | 8 | **3,6** | Must |
| US07 Exclusão | 13 | 5 | 13 | 31 | 13 | **2,4** | Should |
| US09 Portabilidade | 3 | 2 | 2 | 7 | 8 | **0,9** | Could |

**Ajuste por dependência:** o WSJF colocou US05 e US06 no topo, mas ambas dependem de existir uma solicitação validada. A ordem real de entrega ficou **US01 → US02 → US05 → US06 → US03 → US04 → US08 → US07 → US09**. O ranking orienta a decisão; as dependências técnicas definem a sequência.

## Fatiamento de escopo — US07 Exclusão (tamanho 13)

Grande demais para uma sprint. Fatiada com a técnica **SPIDR** (Spike, Path, Interface, Data, Rules):

| Fatia | Técnica | Entrega | Tamanho |
|---|---|---|---|
| US07.1 | Spike | Levantar quais tabelas de cada sistema têm dado pessoal e quais têm guarda legal | 3 |
| US07.2 | Data | Exclusão apenas na plataforma de marketing | 3 |
| US07.3 | Data | Exclusão no CRM e no e-commerce | 5 |
| US07.4 | Rules | Bloqueio em vez de exclusão para documentos fiscais (RN06) | 3 |
| US07.5 | Path | Tratamento de falha parcial: um sistema não respondeu | 3 |

Cada fatia entrega valor verificável e pode ir para produção sozinha.

## Critérios de aceite (BDD)

Os critérios estão escritos em Gherkin na pasta [features/](../features/). Exemplo da US02:

```gherkin
Cenário: Bloqueio após três códigos errados
  Dado que abri uma solicitação de acesso
  E recebi um código de verificação
  Quando eu informar um código errado 3 vezes
  Então a solicitação deve ser encerrada sem validação
  E nenhum dado pessoal deve ser exibido
```

## Definition of Ready e Definition of Done

| Definition of Ready | Definition of Done |
|---|---|
| História no formato "Como… quero… para…" | Código revisado por outra pessoa |
| Critérios de aceite em Gherkin | Cenários BDD automatizados e passando |
| Regras de negócio referenciadas (RNxx) | Matriz de rastreabilidade atualizada |
| Dependências de integração mapeadas | Sem dado pessoal completo nos logs (RNF04) |
| Estimada pelo time | Validada pela DPO em homologação |
