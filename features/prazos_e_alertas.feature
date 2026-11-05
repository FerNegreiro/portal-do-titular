# language: pt
@US05 @RF05
Funcionalidade: Fila de prazos do DPO
  Como encarregada de dados (DPO)
  Quero ver as solicitações ordenadas pelo prazo e ser alertada perto do vencimento
  Para nunca descumprir o prazo legal

  Cenário: Fila ordenada pelo prazo mais próximo
    Dado que existem duas solicitações validadas em dias diferentes
    Quando eu abrir a fila do backoffice
    Então a solicitação com prazo mais próximo deve aparecer primeiro

  @RN08
  Esquema do Cenário: Alerta de prazo
    Dado uma solicitação validada há <dias_corridos> dias
    Quando eu abrir a fila do backoffice
    Então o alerta de prazo deve estar <situacao>

    Exemplos:
      | dias_corridos | situacao   |
      | 5             | desligado  |
      | 11            | desligado  |
      | 12            | ligado     |
      | 15            | ligado     |

  Cenário: Acesso restrito
    Dado que não estou autenticado no backoffice
    Quando eu tentar abrir a fila
    Então o acesso deve ser negado

  @RN10
  Cenário: Conclusão registrada na auditoria
    Dado uma solicitação validada dentro do prazo
    Quando eu concluir a solicitação com a resposta ao titular
    Então o titular deve receber a resposta por e-mail
    E a auditoria deve registrar a conclusão como "dentro do prazo"
