# language: pt
@US02 @RF03 @RN05
Funcionalidade: Validação de identidade por código
  Como titular de dados
  Quero confirmar minha identidade com um código enviado ao meu e-mail
  Para ter certeza de que ninguém pede meus dados no meu lugar

  Contexto:
    Dado que abri uma solicitação de acesso
    E recebi um código de verificação de 6 dígitos

  @RN01
  Cenário: Código correto inicia o prazo legal
    Quando eu informar o código correto em até 10 minutos
    Então a solicitação deve passar para "Em andamento"
    E o prazo de resposta deve ser de 15 dias a partir de agora

  Cenário: Código errado informa as tentativas restantes
    Quando eu informar um código errado
    Então devo ver que restam 2 tentativas

  @RN02
  Cenário: Bloqueio após três códigos errados
    Quando eu informar um código errado 3 vezes
    Então a solicitação deve ser encerrada sem validação
    E nenhum dado pessoal deve ser exibido

  Cenário: Código expirado
    Dado que se passaram 11 minutos desde o envio do código
    Quando eu informar o código recebido
    Então devo ver que o código expirou
    E devo poder pedir um novo código

  Cenário: Novo código invalida o anterior
    Dado que pedi um novo código
    Quando eu informar o código antigo
    Então a validação deve falhar
    Mas o novo código deve ser aceito

  @RN09
  Cenário: Solicitação abandonada
    Dado que não validei minha identidade
    Quando se passarem 7 dias desde a abertura
    Então a solicitação deve ser encerrada automaticamente
    E devo poder abrir uma nova solicitação do mesmo tipo
