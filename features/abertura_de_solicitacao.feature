# language: pt
@US01 @RF01
Funcionalidade: Abertura de solicitação pelo titular
  Como titular de dados
  Quero abrir uma solicitação informando CPF, e-mail e o direito desejado
  Para não depender do SAC

  Cenário: Abertura com dados válidos
    Dado que estou na página inicial do Portal do Titular
    Quando eu informar o CPF "529.982.247-25", o e-mail "ana@email.com" e o tipo "Acesso aos dados"
    Então devo receber um número de protocolo
    E a solicitação deve ficar com status "Aguardando validação"
    E devo receber um código de verificação no e-mail informado

  @RN03
  Esquema do Cenário: CPF inválido é recusado
    Quando eu tentar abrir uma solicitação com o CPF "<cpf>"
    Então devo ver a mensagem "CPF inválido"
    E nenhuma solicitação deve ser criada

    Exemplos:
      | cpf            |
      | 123.456.789-00 |
      | 111.111.111-11 |
      | 529.982        |

  @RN04
  Cenário: Solicitação duplicada do mesmo tipo
    Dado que já existe uma solicitação de acesso em aberto para o CPF "529.982.247-25"
    Quando eu abrir outra solicitação de acesso para o mesmo CPF
    Então devo ver que já existe uma solicitação em andamento
    E devo receber o número do protocolo existente

  @RN04
  Cenário: Tipos diferentes para o mesmo CPF são permitidos
    Dado que já existe uma solicitação de acesso em aberto para o CPF "529.982.247-25"
    Quando eu abrir uma solicitação de revogação de consentimento para o mesmo CPF
    Então a nova solicitação deve ser criada normalmente

  @RNF04
  Cenário: CPF mascarado na consulta
    Dado que abri uma solicitação com o CPF "529.982.247-25"
    Quando eu consultar a solicitação pelo protocolo
    Então o CPF deve aparecer como "***.982.247-**"
