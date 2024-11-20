import os 
import base64
import re
from io import BytesIO
import matplotlib.pyplot as plt #Para criacao de graficos
import json #Salvar pessoas NoSQL
from flask import Flask, redirect, url_for, request
from flask_dance.contrib.google import make_google_blueprint, google #Para autenticacao oauth google

#permite autenticacao via http, para execução localmente
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

##########################################################
#inicializa o app flask
app = Flask(__name__)
#chave secreta (client secret) gerada no google cloud console
app.secret_key = "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"
#client id gerado no google cloud console
app.config["GOOGLE_OAUTH_CLIENT_ID"] = "49832956609-vsc0kktt7p1pf1qp07shjvkrcl706lqt.apps.googleusercontent.com"
app.config["GOOGLE_OAUTH_CLIENT_SECRET"] = "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"

blueprintLogin = make_google_blueprint(
    client_id=app.config["GOOGLE_OAUTH_CLIENT_ID"],
    client_secret=app.config["GOOGLE_OAUTH_CLIENT_SECRET"],
    redirect_to="pagPrincipal"
)
app.register_blueprint(blueprintLogin, url_prefix="/login")

#func pra carregar pessoas do json
def carregaDados():
    if not os.path.exists("dados.json"):
        return []  #se o arq nao existe, retorna lista vazia
    arq = open("dados.json", "r")
    conteudoArq = arq.read()
    arq.close() 
    if not conteudoArq.strip():
        return [] #se o arq eh vazio, retorna lista vazia
    pessoas = json.loads(conteudoArq)
    if type(pessoas) == list:
        return pessoas
    return []  #se conteudo do arq nao eh lista de pessoas, retorna lista vazia


#func pra salvar pessoas no json
def salvar_dados():
    arq = open("dados.json", "w")  
    json.dump(pessoas, arq, indent=4) 
    arq.close()


#carrega lista de pessoas do json
pessoas = carregaDados()

#pagina inicial (rota /)
@app.route("/")
#func q retorna o html da pagina inicial
def home(): 
    return '''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Pagina Inicial - Desafio DevCloud</title>
            <style>
                body {
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    margin: 0;
                    background-color: lightgray; 
                }
                .container {
                    text-align: center;
                    background: white;
                    padding: 40px;
                    border-radius: 10px;
                }
                .login-button {
                    display: inline-block;
                    padding: 15px 30px;
                    font-size: 1.2em;
                    color: white;
                    background-color: blue;
                    border-radius: 5px;
                    cursor: pointer;
                    transition: background-color 0.3s ease;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Bem-vindo!</h1>
                <a href="/login/google" class="login-button">Login com o Google</a>
            </div>
        </body>
        </html>
    '''

#pagina de autenticacao que caso se autentique com sucesso, redireciona o usuario pra pag principal
@app.route("/profile")
def profile():
    if not google.authorized:
        return redirect(url_for("google.login"))
    return redirect(url_for("pagPrincipal"))

#config da pagina principal
@app.route("/home")
def pagPrincipal():
    if not google.authorized:
        return redirect(url_for("google.login"))
    return '''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Menu - Desafio DevCloud</title>
            <style>
                body {
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    margin: 0;
                    background-color: lightgrey;
                }
                .container {
                    text-align: center;
                    background: white;
                    padding: 30px;
                    border-radius: 10px;
                }
                .button {
                    display: block;
                    margin: 10px auto;
                    padding: 10px 20px;
                    font-size: 1em;
                    color: white;
                    background-color: blue;
                    border: none;
                    border-radius: 5px;
                    text-decoration: none;
                    cursor: pointer;
                    width: 200px;
                    text-align: center;
                }
                .button:hover {
                    background-color: lightblue;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Desafio DevCloud</h1>
                <a href="/criar_uma_pessoa" class="button">Criar Uma Pessoa</a>
                <a href="/pessoas" class="button">Lista de Pessoas</a>
                <a href="/buscar" class="button">Buscar uma Pessoa</a>
                <a href="/grafico" class="button">Gráfico de Barras</a>

            </div>
        </body>
        </html>
    '''

#tela de criar pessoa
@app.route("/criar_uma_pessoa", methods=["GET", "POST"])
def criar_pessoa():
    if not google.authorized:
        return redirect(url_for("google.login")) #necessario autenticacao
    msg = ""
    msgErro = ""
    #criacao de strings de mensagens acima

    #obtendo valor dos campos
    if request.method == "POST":
        nome = request.form["nome"]
        dtNasc = request.form["data_nascimento"]
        quantia = request.form["quantia"]

        #verificacao de formato da data
        if not re.match(r"^\d{2}/\d{2}/\d{4}$", dtNasc):
            msgErro = "Data incorreta/invalida"
        else:
            dia, mes, ano = map(int, dtNasc.split("/"))
            #VERIFICACAO DE VALIDACAO DE DATA
            if ano > 2024 or mes > 12 or dia < 1:
                msgErro = "Data incorreta/invalida"
            elif ano == 2024 and (mes > 11 or (mes == 11 and dia > 21)):
                msgErro = "Data incorreta/invalida"
            elif mes in [1, 3, 5, 7, 8, 10, 12] and dia > 31:
                msgErro = "Data incorreta/invalida"
            elif mes in [4, 6, 9, 11] and dia > 30:
                msgErro = "Data incorreta/invalida"
            elif mes == 2:
                if (ano % 4 == 0 and (ano % 100 != 0 or ano % 400 == 0)):
                    if dia > 29:
                        msgErro = "Data incorreta/invalida"
                else:
                    if dia > 28:
                        msgErro = "Data incorreta/invalida"

        #se data esta certa, verifica a quantia
        if not msgErro:
            if not re.match(r"^\d+(\.\d{1,2})?$", quantia):
                msgErro = "Quantia invalida"
            elif float(quantia) <= 0:
                msgErro = "Quantia invalida"

        #se esta tudo certo, armazena a pessoa no json
        if not msgErro:
            quantia = float(quantia)
            novaPessoa = {
                "id": len(pessoas) + 1,
                "nome": nome,
                "data_nascimento": dtNasc,
                "quantia": quantia
            }
            pessoas.append(novaPessoa)
            salvar_dados()
            msg = "Pessoa criada com sucesso!"

    return f'''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Criar Pessoa</title>
            <style>
                body {{
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    margin: 0;
                    background-color: lightgray;
                }}
                .container {{
                    text-align: center;
                    background: white;
                    padding: 30px;
                    border-radius: 10px;
                }}
                form {{
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                }}
                label {{
                    font-size: 1em;
                    margin-bottom: 5px;
                    color: #555;
                }}
                input {{
                    margin-bottom: 15px;
                    padding: 10px;
                    font-size: 1em;
                    width: 100%;
                    max-width: 300px;
                    border: 1px solid #ccc;
                    border-radius: 5px;
                }}
                button {{
                    padding: 10px 20px;
                    font-size: 1em;
                    color: white;
                    background-color: blue;
                    border: none;
                    border-radius: 5px;
                    cursor: pointer;
                }}
                button:hover {{
                    background-color: #lightblue;
                }}
                .success {{
                    color: green;
                    font-size: 1.2em;
                    margin-bottom: 15px;
                }}
                .error {{
                    color: #d9534f;
                    font-size: 1.2em;
                    margin-bottom: 15px;
                }}
                .links {{
                    margin-top: 20px;
                }}
                .links a {{
                    display: inline-block;
                    margin: 0 auto;
                    padding: 10px 20px;
                    font-size: 1em;
                    color: white;
                    background-color: blue;
                    border-radius: 5px;
                    text-decoration: none;
                    cursor: pointer;
                }}
                .links a:hover {{
                    background-color: lightblue;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Criar Pessoa</h1>
                {f'<p class="success">{msg}</p>' if msg else ''}
                {f'<p class="error">{msgErro}</p>' if msgErro else ''}
                <form method="POST">
                    <label for="nome">Nome Completo</label>
                    <input type="text" name="nome" id="nome" required>
                    <label for="data_nascimento">Data de Nascimento</label>
                    <input type="text" name="data_nascimento" id="data_nascimento" placeholder="DD/MM/AAAA" required>
                    <label for="quantia">Quantia (US$)</label>
                    <input type="text" name="quantia" id="quantia" required>
                    <button type="submit">Criar Pessoa</button>
                </form>
                <div class="links">
                    <a href="/home">Voltar</a>
                </div>
            </div>
        </body>
        </html>
    '''

#tela lista de pessoas
@app.route("/pessoas")
def listarPessoas():
    if not google.authorized:
        return redirect(url_for("google.login"))
    if not pessoas:
        return '''
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Tabela de Pessoas</title>
                <style>
                    body {
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        height: 100vh;
                        margin: 0;
                        background-color: lightgray;
                    }
                    .container {
                        text-align: center;
                        background: white;
                        padding: 30px;
                        border-radius: 10px;
                    }
                    .buttons {
                        margin-top: 20px;
                    }
                    a {
                        display: inline-block;
                        margin: 0 10px;
                        padding: 10px 20px;
                        font-size: 1em;
                        color: white;
                        background-color: #4285f4;
                        border: none;
                        border-radius: 5px;
                        text-decoration: none;
                        cursor: pointer;
                    }
                    a:hover {
                        background-color: #357ae8;
                    }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>Nenhuma pessoa criada</h1>
                    <div class="buttons">
                        <a href="/home">Voltar</a>
                        <a href="/criar_uma_pessoa">Criar Pessoa</a>
                    </div>
                </div>
            </body>
            </html>
        '''
    tabela_template = '''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Tabela de Pessoas</title>
            <style>
                body {{
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    flex-direction: column;
                    margin: 0;
                    background-color: lightgray;
                }}
                .container {{
                    text-align: center;
                    background: white;
                    padding: 30px;
                    border-radius: 10px;
                }}
                table {{
                    width: 100%;
                    max-width: 800px;
                    margin: 0 auto;
                    border-collapse: collapse;
                    margin-bottom: 20px;
                }}
                th, td {{
                    border: 1px solid #ccc;
                    padding: 10px;
                    text-align: center;
                }}
                th {{
                    background-color: blue;
                    color: white;
                }}
                .btn-edit {{
                    display: inline-block;
                    padding: 5px 10px;
                    font-size: 0.9em;
                    color: white;
                    background-color: blue;
                    border: none;
                    border-radius: 5px;
                    text-decoration: none;
                    cursor: pointer;
                }}
                .btn-edit:hover {{
                    background-color: lightblue;
                }}
                .btn-delete {{
                    display: inline-block;
                    padding: 5px 10px;
                    font-size: 0.9em;
                    color: white;
                    background-color: red;
                    border: none;
                    border-radius: 5px;
                    text-decoration: none;
                    cursor: pointer;
                }}
                .btn-delete:hover {{
                    background-color: lightred;
                }}
                a {{
                    display: inline-block;
                    margin-top: 10px;
                    padding: 10px 20px;
                    font-size: 1em;
                    color: white;
                    background-color: blue;
                    border: none;
                    border-radius: 5px;
                    text-decoration: none;
                    cursor: pointer;
                }}
                a:hover {{
                    background-color: #357ae8;
                }}
                #calculation-area {{
                    margin-top: 20px;
                    text-align: center;
                }}
                #result {{
                    color: green;
                    margin-top: 10px;
                }}
            </style>
               <script>
                function totalEMedia() {{
                    const table = document.querySelector('table tbody');
                    const rows = table.getElementsByTagName('tr');
                    let total = 0;
                    let count = 0;

                    for (let row of rows) {{
                        const cells = row.getElementsByTagName('td');
                        const quantia = parseFloat(cells[3].textContent);
                        if (!isNaN(quantia)) {{
                            total += quantia;
                            count++;
                        }}
                    }}

                    const media = total / count;
                    const result = document.getElementById('result');
                    result.innerHTML = `Valor Total: ${{total.toFixed(2)}}<br>Média: ${{media.toFixed(2)}}`;
                }}
            </script>
            <script>
                function conversaoPraReal() {{
                    const id = document.getElementById('id-pessoa').value;
                    const taxaCambio = parseFloat(document.getElementById('taxa-cambio').value);
                    const result = document.getElementById('result');
                    
                    const table = document.querySelector('table tbody');
                    const rows = table.getElementsByTagName('tr');
                    let valorDolar = null;

                    for (let row of rows) {{
                        const cells = row.getElementsByTagName('td');
                        if (cells[0].textContent == id) {{
                            valorDolar = parseFloat(cells[3].textContent);
                            break;
                        }}
                    }}

                    if (!valorDolar) {{
                        result.textContent = 'ID não encontrado/invalido.';
                        result.style.color = 'red';
                        return;
                    }}

                    if (isNaN(taxaCambio) || taxaCambio <= 0) {{
                        result.textContent = 'Taxa de cambio invalida.';
                        result.style.color = 'red';
                        return;
                    }}

                    const valorReais = valorDolar * taxaCambio;
                    result.textContent = 'Valor em reais: R$ ' + valorReais.toFixed(2);
                    result.style.color = 'green';
                }}
            </script>
        </head>
        <body>
            <div class="container">
                <h1>Tabela de Pessoas</h1>
                <table>
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Nome</th>
                            <th>Data de Nascimento</th>
                            <th>Quantia (US$)</th>
                        </tr>
                    </thead>
                    <tbody>
                        {linhas}
                    </tbody>
                </table>
                <a href="/home">Voltar</a>
            </div>
            <div id="calculation-area">
                <input type="text" id="id-pessoa" placeholder="Digite o ID">
                <input type="text" id="taxa-cambio" placeholder="Taxa de câmbio">
                <button onclick="conversaoPraReal()">Calcular</button>
                <p id="result"></p>
                <button onclick="totalEMedia()">Calcular Total e Média</button>
                <p id="result"></p>
            </div>
        </body>
        </html>
    '''
    linhas = ""
    for pessoa in pessoas:
        linhas += f'''
            <tr>
                <td>{pessoa["id"]}</td>
                <td>{pessoa["nome"]}</td>
                <td>{pessoa["data_nascimento"]}</td>
                <td>{pessoa["quantia"]:.2f}</td>
                <td><a class="btn-edit" href="/editar/{pessoa['id']}">Editar</a></td>
                <td><a class="btn-delete" href="/deletar/{pessoa['id']}">Excluir</a></td>
            </tr>
        '''
    return tabela_template.format(linhas=linhas)


#tela de edicao de pessoa
@app.route("/editar/<int:id>", methods=["GET", "POST"])
def editarPessoa(id):
    if not google.authorized:
        return redirect(url_for("google.login"))
    
    pessoa = next((p for p in pessoas if p["id"] == id))
    msg = ""
    msgErro = ""
    if request.method == "POST":
        nome = request.form["nome"]
        dtNasc = request.form["data_nascimento"]
        quantia = request.form["quantia"]

        #mesmas validacoes da criacao de pessoa
        if not re.match(r"^\d{2}/\d{2}/\d{4}$", dtNasc):
            msgErro = "Data incorreta/invalida"
        else:
            dia, mes, ano = map(int, dtNasc.split("/"))
            if ano > 2024 or mes > 12 or dia < 1:
                msgErro = "Data incorreta/invalida"
            elif ano == 2024 and (mes > 11 or (mes == 11 and dia > 21)):
                msgErro = "Data incorreta/invalida"
            elif mes in [1, 3, 5, 7, 8, 10, 12] and dia > 31:
                msgErro = "Data incorreta/invalida"
            elif mes in [4, 6, 9, 11] and dia > 30:
                msgErro = "Data incorreta/invalida"
            elif mes == 2:
                if (ano % 4 == 0 and (ano % 100 != 0 or ano % 400 == 0)):
                    if dia > 29:
                        msgErro = "Data incorreta/invalida"
                else:
                    if dia > 28:
                        msgErro = "Data incorreta/invalida"
        if not msgErro:
            if not re.match(r"^\d+(\.\d{1,2})?$", quantia):
                msgErro = "Quantia invalida"
            elif float(quantia) <= 0:
                msgErro = "Quantia invalida"

        if not msgErro:
            pessoa["nome"] = nome
            pessoa["data_nascimento"] = dtNasc
            pessoa["quantia"] = float(quantia)
            salvar_dados()  #salva dados no json apos edicao
            msg = "Pessoa editada com sucesso!"

    return f'''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Editar Pessoa</title>
            <style>
                body {{
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    margin: 0;
                    background-color: lightgray;
                }}
                .container {{
                    text-align: center;
                    background: white;
                    padding: 30px;
                    border-radius: 10px;
                }}
                form {{
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                }}
                label {{
                    font-size: 1em;
                    margin-bottom: 5px;
                    color: #555;
                }}
                input {{
                    margin-bottom: 15px;
                    padding: 10px;
                    font-size: 1em;
                    width: 100%;
                    max-width: 300px;
                    border: 1px solid #ccc;
                    border-radius: 5px;
                }}
                button {{
                    padding: 10px 20px;
                    font-size: 1em;
                    color: white;
                    background-color: blue;
                    border: none;
                    border-radius: 5px;
                    cursor: pointer;
                }}
                button:hover {{
                    background-color: lightblue;
                }}
                .success {{
                    color: green;
                    font-size: 1.2em;
                    margin-bottom: 15px;
                }}
                .error {{
                    color: #d9534f;
                    font-size: 1em;
                    margin-bottom: 15px;
                }}
                .links {{
                    margin-top: 20px;
                }}
                .links a {{
                    display: inline-block;
                    margin: 0 auto;
                    padding: 10px 20px;
                    font-size: 1em;
                    color: white;
                    background-color: blue;
                    border-radius: 5px;
                    text-decoration: none;
                    cursor: pointer;
                }}
                .links a:hover {{
                    background-color: lightblue;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Editar Pessoa</h1>
                {f'<p class="success">{msg}</p>' if msg else ''}
                {f'<p class="error">{msgErro}</p>' if msgErro else ''}
                <form method="POST">
                    <label for="nome">Nome Completo</label>
                    <input type="text" name="nome" id="nome" value="{pessoa['nome']}" required>
                    <label for="data_nascimento">Data de Nascimento</label>
                    <input type="text" name="data_nascimento" id="data_nascimento" value="{pessoa['data_nascimento']}" required>
                    <label for="quantia">Quantia</label>
                    <input type="text" name="quantia" id="quantia" value="{pessoa['quantia']}" required> 
                    <button type="submit">Salvar</button>
                </form>
                {f'<div class="links"><a href="/pessoas">Voltar</a></div>' if msg else ''}
            </div>
        </body>
        </html>
    '''

#tela de deletar uma pessoa
@app.route("/deletar/<int:id>")
def deletarPessoa(id):
    if not google.authorized:
        return redirect(url_for("google.login"))
    global pessoas
    pessoas = [p for p in pessoas if p["id"] != id]
    #Caso necessário, reajuste no ID das pessoas restantes
    for index, pessoa in enumerate(pessoas):
        pessoa["id"] = index + 1
    salvar_dados()
    return '''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Pessoa excluída com sucesso</title>
            <style>
                body {
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    margin: 0;
                    background-color: lightgray;
                }
                .container {
                    text-align: center;
                    background: white;
                    padding: 30px;
                    border-radius: 10px;
                }
                .links {
                    margin-top: 20px;
                }
                .links a {
                    display: inline-block;
                    margin: 0 auto;
                    padding: 10px 20px;
                    font-size: 1em;
                    color: white;
                    background-color: blue;
                    border-radius: 5px;
                    text-decoration: none;
                    cursor: pointer;
                }
                .links a:hover {
                    background-color: lightblue;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Pessoa Excluída</h1>
                <div class="links">
                    <a href="/pessoas">Voltar</a>
                </div>
            </div>
        </body>
        </html>
    '''

#tela de busca de pessoas
@app.route("/buscar", methods=["GET", "POST"])
def buscarPessoa():
    if not google.authorized:
        return redirect(url_for("google.login"))
    msg = None
    resultados = [] #lista de pessoa(s) com o nome buscado
    if request.method == "POST":
        nome = request.form["nome"].strip().lower()
        resultados = [p for p in pessoas if nome in p["nome"].lower()]
        if not resultados:
            msg = "Pessoa não encontrada."
    return f'''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Buscar Pessoa</title>
            <style>
                body {{
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    margin: 0;
                    background-color: lightgray;
                }}
                .container {{
                    text-align: center;
                    background: white;
                    padding: 30px;
                    border-radius: 10px;
                }}
                form {{
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                }}
                label {{
                    font-size: 1em;
                    margin-bottom: 5px;
                    color: #555;
                }}
                input {{
                    margin-bottom: 15px;
                    padding: 10px;
                    font-size: 1em;
                    width: 100%;
                    max-width: 300px;
                    border: 1px solid #ccc;
                    border-radius: 5px;
                }}
                button {{
                    padding: 10px 20px;
                    font-size: 1em;
                    color: white;
                    background-color: blue;
                    border: none;
                    border-radius: 5px;
                    cursor: pointer;
                }}
                button:hover {{
                    background-color: lightblue;
                }}
                .error {{
                    color: #d9534f;
                    font-size: 1.2em;
                    margin-bottom: 15px;
                }}
                .result {{
                    font-size: 1em;
                    margin-top: 15px;
                    text-align: left;
                }}
                .links {{
                    margin-top: 20px;
                }}
                .links a {{
                    display: inline-block;
                    margin: 0 auto;
                    padding: 10px 20px;
                    font-size: 1em;
                    color: white;
                    background-color: blue;
                    border-radius: 5px;
                    text-decoration: none;
                    cursor: pointer;
                }}
                .links a:hover {{
                    background-color: lightblue;
                }}
                table {{
                    width: 100%;
                    max-width: 600px;
                    margin: 0 auto;
                    border-collapse: collapse;
                }}
                th, td {{
                    border: 1px solid #ccc;
                    padding: 10px;
                    text-align: center;
                }}
                th {{
                    background-color: blue;
                    color: white;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Buscar Pessoa</h1>
                {f'<p class="error">{msg}</p>' if msg else ''}
                <form method="POST">
                    <label for="nome">Digite o Nome</label>
                    <input type="text" name="nome" id="nome" required>
                    <button type="submit">Buscar</button>
                </form>
                {'<table><thead><tr><th>ID</th><th>Nome</th><th>Data de Nascimento</th><th>Quantia (US$)</th></tr></thead><tbody>' + ''.join(f'<tr><td>{p["id"]}</td><td>{p["nome"]}</td><td>{p["data_nascimento"]}</td><td>{p["quantia"]:.2f}</td></tr>' for p in resultados) + '</tbody></table>' if resultados else ''}
                <div class="links">
                    <a href="/home">Voltar</a>
                </div>
            </div>
        </body>
        </html>
    '''


#tela grafico de barras
@app.route("/grafico")
def grafico():
    if not google.authorized:
        return redirect(url_for("google.login"))
    if not pessoas:
        return '''
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Gráfico</title>
                <style>
                    body {
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        height: 100vh;
                        margin: 0;
                        background-color: lightgray;
                    }
                    .container {
                        text-align: center;
                        background: white;
                        padding: 30px;
                        border-radius: 10px;
                        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
                    }
                    a {
                        display: inline-block;
                        margin-top: 20px;
                        padding: 10px 20px;
                        font-size: 1em;
                        color: white;
                        background-color: blue;
                        border-radius: 5px;
                        text-decoration: none;
                        cursor: pointer;
                    }
                    a:hover {
                        background-color: lightblue;
                    }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>Nenhuma pessoa criada</h1>
                    <a href="/home">Voltar</a>
                </div>
            </body>
            </html>
        '''
    #dados para o grafico
    nomes = [p["nome"] for p in pessoas]
    quantias = [p["quantia"] for p in pessoas]
    #grafico
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.bar(nomes, quantias, color="blue")
    ax.set_xlabel("Nome", fontsize=12)
    ax.set_ylabel("Quantia (US$)", fontsize=12)
    #plt.xticks(rotation=45, ha="right")

    #convertendo grafico pra imagem base64
    buf = BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format="png")
    buf.seek(0)
    img_base64 = base64.b64encode(buf.getvalue()).decode("utf-8")
    buf.close()

    return f'''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Gráfico</title>
            <style>
                body {{
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    flex-direction: column;
                    height: 100vh;
                    margin: 0;
                    background-color: lightgray;
                }}
                .container {{
                    text-align: center;
                    background: white;
                    padding: 30px;
                    border-radius: 10px;
                }}
                a {{
                    display: inline-block;
                    margin-top: 20px;
                    padding: 10px 20px;
                    font-size: 1em;
                    color: white;
                    background-color: blue;
                    border-radius: 5px;
                    text-decoration: none;
                    cursor: pointer;
                }}
                a:hover {{
                    background-color:lightblue;
                }}
                img {{
                    max-width: 100%;
                    height: auto;
                    margin-top: 20px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Quantia por Pessoa</h1>
                <img src="data:image/png;base64,{img_base64}" alt="Gráfico">
                <a href="/home">Voltar</a>
            </div>
        </body>
        </html>
    '''
##########################################################################
if __name__ == "__main__":
    app.run(debug=True)
