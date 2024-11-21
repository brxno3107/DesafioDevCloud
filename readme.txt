PRE REQUISITOS: 
- AMBIENTE PYTHON 3.7 OU SUPERIOR
- Instalar as seguintes bibliotecas no AMBIENTE:
    pip install flask flask-dance authlib matplotlib (copie e cole essa linha no terminal)
!IMPORTANTE: Não é necessário a existência prévia de um dados.json. Na ausência dele o código já cria um nos seus arquivos
--------------------------------------------------------------------------------------------------------
Passo 1:
Crie um projeto no Google Cloud Console. Ative a Google People API, configure credenciais OAuth
para aplicativos Web e obtenha o Client ID e Client Secret para inserir no código

Como executar:
1: Escreva no Console "python DevCloud.py"
2: Acesse http://127.0.0.1:5000/

Funcionamento da aplicação:
Tela incial: Clique para fazer login com o google --> Autentique-se com seu Gmail

Após autenticação, o site te leva ao menu principal, que te dá 4 opções

#1 - CRIAR UMA PESSOA
Ao clicar nessa opção, você é redirecionado a uma tela de criação de pessoa, onde deve inserir:
-Nome Completo
-Data de nascimento, no formato "DD/MM/AAAA"
-Quantia, em dólares 

#2 - LISTA DE PESSOAS
Essa tela exibe uma tabela, contendo todas as informações das pessoas (com um n° de identificação).
Além disso, há os seguintes botões
    2.1 - Editar
        Permite que você edite uma pessoa, seguindo as mesmas regras de criação da tela de criar uma pessoa (#1)
    2.2 - Excluir
        Exclui o usuário da tabela de pessoas e, consequetemente, do arquivo json
    2.3 - Calcular
        Inserindo, de forma válida, o ID de um usuário e uma taxa de câmbio, clicar no botão irá resultar no valor em reais da quantia dessa pessoa sendo exibido na tela
    2.4 - Calcular Total e Média
        Ao ser clicado, exibe nessa tela a quantia total (somatório das quantias das pessoas da tabela) e a méida de quantia
    

#3 - BUSCAR UMA PESSOA
Permite que o usuário efetue uma busca de pessoas pelo nome

#4 - GRÁFICO DE BARRAS
Exibe um gráfico de barras da quantia (em dólares) das pessoas presentes na tabela
---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
COMO CLONAR REPOSITÓRIO AO MEU COMPUTADOR?
1 - No terminal, selecione a pasta em que quer clonar com "cd <PASTA_DESEJADA>"
2 - cole no terminal a seguinte linha:
git clone https://github.com/brxno3107/DesafioDevCloud