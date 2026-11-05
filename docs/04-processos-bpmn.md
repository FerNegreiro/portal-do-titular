# 04 — Processos (BPMN)

Os diagramas abaixo usam Mermaid para renderizar direto no GitHub, mantendo a semântica BPMN: cada bloco de raia representa uma **lane**, losangos são **gateways** e círculos são **eventos**.

| Símbolo aqui | Elemento BPMN |
|---|---|
| `(( ))` | Evento de início ou fim |
| `[ ]` | Tarefa |
| `{ }` | Gateway exclusivo (XOR) |
| `{{ }}` | Gateway paralelo (AND) |
| `[/ /]` | Evento intermediário de tempo |

## AS-IS — Atendimento de pedido de titular

```mermaid
flowchart LR
    subgraph Titular
        I((Início)) --> T1[Envia pedido por<br/>e-mail, SAC ou rede social]
        T9[Recebe resposta<br/>por e-mail] --> F((Fim))
    end
    subgraph SAC
        T1 --> S1[Encaminha pedido<br/>ao e-mail do DPO]
    end
    subgraph DPO
        S1 --> D1[Registra na planilha]
        D1 --> G1{Dados suficientes<br/>para identificar?}
        G1 -- Não --> D2[Pede mais dados<br/>ao titular]
        D2 --> D1
        G1 -- Sim --> D3[Envia e-mail para<br/>cada área envolvida]
        D3 --> D4[/Aguarda respostas<br/>sem prazo definido/]
        D4 --> D5[Cobra as áreas<br/>manualmente]
        D5 --> D6[Consolida respostas<br/>em documento]
        D6 --> T9
    end
    subgraph AR[Áreas]
        D3 --> A1[Consultam CRM, ERP,<br/>e-commerce e marketing]
        A1 --> D4
    end
```

### Problemas identificados no AS-IS

| # | Etapa | Problema | Desperdício (Lean) |
|---|---|---|---|
| P1 | Entrada multicanal | Sem protocolo e sem formulário padrão | Defeito |
| P2 | Identificação | Volta e meia com o titular para pedir dados | Retrabalho |
| P3 | Sem validação de identidade | Risco de enviar dados para outra pessoa | Defeito crítico |
| P4 | Envio por e-mail às áreas | Espera sem prazo nem dono | Espera |
| P5 | Cobrança manual | Tempo do DPO gasto em follow-up | Movimentação |
| P6 | Sem registro de conclusão | Nenhuma prova para auditoria | Defeito |

## TO-BE — Portal do Titular

```mermaid
flowchart LR
    subgraph Titular
        I((Início)) --> T1[Abre solicitação<br/>no portal]
        T2[Informa código<br/>de verificação]
        T9[Recebe resposta<br/>e protocolo de conclusão] --> F((Fim))
    end
    subgraph Portal
        T1 --> P1{CPF válido e sem<br/>pedido duplicado?}
        P1 -- Não --> P0[Mostra erro<br/>orientativo] --> T1
        P1 -- Sim --> P2[Gera protocolo e<br/>envia código por e-mail]
        P2 --> T2
        T2 --> P3{Código<br/>correto?}
        P3 -- Não --> P4{Tentativas<br/>esgotadas?}
        P4 -- Não --> T2
        P4 -- Sim --> P5((Encerrada sem<br/>validação))
        P3 -- Sim --> P6[Inicia prazo de<br/>15 dias]
    end
    subgraph Orquestrador
        P6 --> O1{Tipo de<br/>solicitação}
        O1 -- Acesso --> O2{{Consulta em paralelo}}
        O2 --> O3[CRM] & O4[ERP] & O5[E-commerce] & O6[Marketing]
        O3 & O4 & O5 & O6 --> O7{{Consolida}}
        O1 -- Revogação --> O8[Atualiza consentimento<br/>no marketing]
        O1 -- Exclusão --> O9[Elimina ou bloqueia<br/>conforme guarda legal]
    end
    subgraph DPO
        O7 --> D1[Revisa e aprova<br/>resposta]
        O9 --> D1
        O8 --> D2[Registro automático<br/>na auditoria]
        D1 --> D2
        X[/Faltam 3 dias/] -.-> D3[Recebe alerta<br/>de prazo]
    end
    D2 --> T9
```

## Comparativo

| Indicador | AS-IS | TO-BE (meta) |
|---|---|---|
| Etapas manuais | 9 | 2 (revisão e aprovação) |
| Pontos de espera sem dono | 3 | 0 |
| Validação de identidade | Não existe | Código por e-mail |
| Rastreabilidade | Planilha | Auditoria automática por evento |
| Tempo médio | 11 dias | 3 dias |

## Ferramentas

A modelagem de referência foi feita para ser levada ao **Bizagi Modeler** (documentação e simulação de capacidade) e ao **Camunda Modeler**, onde o TO-BE pode virar processo executável com o orquestrador como *service tasks* e o alerta de prazo como *timer boundary event*.
