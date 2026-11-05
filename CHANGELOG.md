# Changelog

## 1.2.0 — Demonstração visual

- Página em `http://127.0.0.1:5000` para percorrer o fluxo completo sem terminal: cliente, e-mail simulado, backoffice do DPO e trilha de auditoria.
- Painel "Regras de negócio em ação", mostrando o código da regra em cada recusa da API.
- Data simulada ajustável para demonstrar o alerta de prazo (RN08) e o encerramento automático (RN09).
- Modo demonstração ligado por padrão e desligável com `MODO_DEMO=0`; as rotas `/demo/*` não existem fora dele.
- Índice da API movido de `/` para `/v1`.
- 7 testes novos, totalizando 31.

## 1.1.0 — Correções encontradas no teste manual

Durante o teste exploratório da API pelo PowerShell (Windows PowerShell 5.1), foram encontrados três problemas. Cada um ganhou um teste automatizado antes da correção.

| # | Problema observado | Causa | Correção | Teste |
|---|---|---|---|---|
| 1 | `dias_restantes` mostrava 14 logo após a validação, com prazo de 15 dias | A contagem usava períodos completos de 24h e arredondava para baixo | Contagem por data do calendário | `test_dias_restantes_conta_por_data_do_calendario` |
| 2 | Resposta com acento era recusada como "resposta obrigatória" | O PowerShell 5.1 não envia UTF-8 por padrão; o JSON inválido era tratado silenciosamente como corpo vazio, gerando uma mensagem enganosa | Corpo ilegível agora retorna **400 — JSON inválido** | `test_json_invalido_retorna_400`, `test_json_malformado_retorna_400` |
| 3 | Acentos apareciam corrompidos (`relatÃ³rio`) no cliente | As respostas não declaravam o charset, e o cliente assumia outra codificação | Todas as respostas declaram `application/json; charset=utf-8` | `test_respostas_declaram_utf8`, `test_acentos_chegam_intactos` |

**Lição registrada:** erros de validação nunca devem mascarar erros de formato. Uma mensagem de regra de negócio errada custa mais tempo de diagnóstico do que uma mensagem técnica correta.

## 1.0.0 — MVP

Abertura de solicitação, validação de identidade, fila do DPO com alertas de prazo, conclusão e trilha de auditoria.
