# 03 — Requisitos

## Classificação adotada

| Tipo | Definição usada no projeto | Prefixo |
|---|---|---|
| Requisito funcional | O que o sistema deve fazer | RF |
| Requisito não-funcional | Como o sistema deve se comportar (qualidade) | RNF |
| Regra de negócio | Política da empresa ou da lei que o sistema precisa respeitar | RN |
| Restrição | Limite imposto ao projeto, sem margem de escolha | RES |

Cada requisito tem dono, origem e status de ciclo de vida: **Proposto → Analisado → Aprovado → Implementado → Validado** (ou **Rejeitado / Adiado**).

## Requisitos funcionais

| ID | Requisito | Origem | Prioridade | Status |
|---|---|---|---|---|
| RF01 | O titular deve abrir uma solicitação informando CPF, e-mail e tipo de direito | LGPD art. 18 | Must | Implementado |
| RF02 | O sistema deve enviar um código de verificação para o e-mail informado | Achado A2 | Must | Implementado |
| RF03 | O titular deve validar a identidade digitando o código recebido | Achado A2 | Must | Implementado |
| RF04 | O titular deve consultar o andamento pelo número de protocolo | Persona Carlos | Must | Implementado |
| RF05 | O DPO deve visualizar as solicitações ordenadas por prazo restante | Persona Juliana | Must | Implementado |
| RF06 | O sistema deve propagar a revogação de consentimento para a plataforma de marketing | Achado A4 | Must | Aprovado |
| RF07 | O sistema deve orquestrar a exclusão em CRM, ERP, e-commerce e marketing | Achado A3 | Should | Aprovado |
| RF08 | O DPO deve exportar a trilha de auditoria de uma solicitação em PDF | Achado A5 | Should | Aprovado |
| RF09 | O titular deve baixar seus dados em formato JSON (portabilidade) | LGPD art. 18 V | Could | Adiado |

## Requisitos não-funcionais

| ID | Categoria | Requisito | Como medir |
|---|---|---|---|
| RNF01 | Desempenho | Abertura de solicitação responde em até 800 ms no p95 | APM |
| RNF02 | Disponibilidade | 99,5% mensal | Monitor de uptime |
| RNF03 | Segurança | Tráfego somente via TLS 1.2+; dados pessoais criptografados em repouso | Pentest e revisão de config |
| RNF04 | Segurança | CPF nunca aparece completo em logs (máscara `***.982.247-**`) | Revisão automatizada de logs |
| RNF05 | Usabilidade | Abertura de pedido em no máximo 3 telas no celular | Teste de usabilidade com 5 usuários |
| RNF06 | Acessibilidade | Conformidade WCAG 2.1 AA | Auditoria com leitor de tela |
| RNF07 | Auditabilidade | Registros de auditoria imutáveis e guardados por 5 anos | Teste de alteração bloqueada |
| RNF08 | Escalabilidade | Suportar 10x o volume atual (19 mil pedidos/mês) | Teste de carga |

## Regras de negócio

| ID | Regra | Fundamento |
|---|---|---|
| RN01 | O prazo de resposta é de **15 dias corridos** a partir da validação da identidade | LGPD art. 19, II |
| RN02 | Nenhum dado pessoal é exibido ou enviado antes da validação da identidade | Política de segurança |
| RN03 | O CPF informado deve ser válido (dígitos verificadores) | Qualidade de dados |
| RN04 | Não pode existir mais de uma solicitação **em aberto do mesmo tipo** para o mesmo CPF | Evitar duplicidade |
| RN05 | O código de verificação tem 6 dígitos, vale 10 minutos e aceita no máximo 3 tentativas | Política de segurança |
| RN06 | Pedidos de exclusão **não eliminam** dados com guarda obrigatória (ex.: documentos fiscais por 5 anos); esses dados são bloqueados e o titular é informado | LGPD art. 16, I |
| RN07 | A revogação de consentimento deve ser aplicada em todos os canais em até 48 horas | Acordo com Marketing |
| RN08 | O DPO é alertado quando faltarem 3 dias ou menos para o fim do prazo | Meta de 98% no prazo |
| RN09 | Solicitação sem validação de identidade em 7 dias é encerrada automaticamente | Higiene da fila |
| RN10 | Toda mudança de status gera um registro de auditoria com data, hora, ator e motivo | Prova para a ANPD |

## Restrições

| ID | Restrição |
|---|---|
| RES01 | O CRM corporativo (Salesforce) é a fonte oficial do cadastro do cliente e não será substituído |
| RES02 | A solução deve rodar na nuvem já contratada pela empresa |
| RES03 | O MVP precisa estar em produção em até 12 semanas, antes da auditoria externa |
| RES04 | O orçamento aprovado para a onda 1 é de até R$ 420 mil |
| RES05 | O login do portal deve reutilizar o cadastro do programa Aurora+ quando existir |

## Matriz de rastreabilidade

| Necessidade | Requisito | Regra | História | Teste / Cenário |
|---|---|---|---|---|
| Achado A1 | RF01 | RN03, RN04 | US01 | `abertura_de_solicitacao.feature` |
| Achado A2 | RF02, RF03 | RN02, RN05 | US02 | `validacao_de_identidade.feature` |
| Persona Juliana | RF05 | RN01, RN08 | US05 | `prazos_e_alertas.feature` |
| Achado A4 | RF06 | RN07 | US06 | `revogacao_de_consentimento.feature` |
| Achado A3 | RF07 | RN06 | US07 | `exclusao_de_dados.feature` |
| Achado A5 | RF08 | RN10 | US08 | `prazos_e_alertas.feature` e `test_rn10_trilha_de_auditoria_completa` |

## Gestão de mudanças de requisitos

1. Toda mudança entra como **pedido de mudança** no backlog, com solicitante e justificativa.
2. É feita a **análise de impacto** (ver [05 — Arquitetura](05-arquitetura-e-integracoes.md)): requisitos afetados, sistemas, esforço e risco.
3. O Product Owner decide com a DPO; mudanças que afetam prazo ou orçamento vão para o comitê com a patrocinadora.
4. Aprovada, a mudança atualiza a matriz de rastreabilidade e gera nova versão deste documento.
