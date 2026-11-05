# language: pt
@US07 @RF07 @RN06
Funcionalidade: Exclusão de dados orquestrada
  Como titular de dados
  Quero que meus dados sejam excluídos de todos os sistemas
  Para não ter mais vínculo com a empresa

  Contexto:
    Dado que validei minha identidade em uma solicitação de exclusão

  Cenário: Exclusão em todos os sistemas
    Quando o DPO aprovar a exclusão
    Então meus dados devem ser excluídos do CRM, do e-commerce e da plataforma de marketing
    E cada sistema deve confirmar a exclusão ao orquestrador

  Cenário: Dados com guarda legal são bloqueados, não excluídos
    Dado que tenho notas fiscais emitidas nos últimos 5 anos
    Quando o DPO aprovar a exclusão
    Então as notas fiscais devem ser bloqueadas para qualquer uso que não seja fiscal
    E a resposta ao titular deve explicar quais dados foram mantidos e por quê

  Cenário: Falha parcial em um sistema
    Dado que o ERP não respondeu à ordem de exclusão
    Quando o orquestrador tentar 3 vezes sem sucesso
    Então a solicitação deve continuar "Em andamento"
    E o DPO deve receber uma tarefa manual para o ERP
    E a solicitação não pode ser concluída até a confirmação do ERP
