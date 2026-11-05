# language: pt
@US06 @RF06 @RN07
Funcionalidade: Revogação de consentimento de marketing
  Como titular de dados
  Quero revogar o consentimento de marketing
  Para parar de receber mensagens promocionais sem sair do programa Aurora+

  Contexto:
    Dado que tenho cadastro no programa Aurora+
    E validei minha identidade em uma solicitação de revogação de consentimento

  Cenário: Revogação aplicada em todos os canais
    Quando eu escolher revogar o consentimento para "SMS", "E-mail" e "WhatsApp"
    Então a plataforma de marketing deve receber a revogação dos três canais
    E a revogação deve ser confirmada em até 48 horas
    E meu cadastro no Aurora+ deve continuar ativo

  Cenário: Revogação parcial
    Quando eu escolher revogar o consentimento apenas para "SMS"
    Então só o canal SMS deve ser desativado
    E os demais canais devem continuar como estavam

  Cenário: Plataforma de marketing fora do ar
    Dado que a plataforma de marketing está indisponível
    Quando eu confirmar a revogação
    Então a revogação deve ficar na fila para reprocessamento
    E o DPO deve ser alertado se não houver confirmação em 24 horas

  Cenário: Cliente revogado não volta na próxima importação
    Dado que minha revogação foi confirmada
    Quando o marketing fizer a importação semanal de clientes
    Então eu não devo voltar a receber mensagens promocionais
