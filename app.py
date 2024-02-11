from flask import Flask, request, render_template, url_for, session, redirect

import mysql.connector

import sys

app = Flask(__name__)
app.config['SECRET_KEY'] = 'asdkjsakdjalsk'

def getDB():
    try:
        db_conexao = mysql.connector.connect(
            host='mysql-21f30ca-aniversario-54d2.a.aivencloud.com',
            port='23956',
            user='avnadmin',
            password='AVNS_j1Z3qwjhD21I-30Z1fN',
            database='banquinho',
        )
        return db_conexao

    except mysql.connector.Error as erro:
        print(f'Erro connection com o BANCO DE DADOS: {erro}')
        sys.exit(1)

@app.route('/')
def index():
    return render_template('home.html')


@app.route('/location/')
def location():
    return render_template('localizacao.html')


@app.route('/login/', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':
        user_login = request.form.get('Login')
        user_password = request.form.get('Senha')

        conexao = getDB()
        cursor = conexao.cursor(dictionary=True)

        cursor.execute(f"SELECT * FROM usuario WHERE Usuario = '{user_login}'")
        usuario = cursor.fetchone()

        if usuario['Senha'] == user_password:

            session['USER'] = usuario['Usuario']

            return redirect(url_for('presentes')), 301

    return render_template('login.html')


@app.route('/cadastro/', methods=['GET', 'POST'])
def cadastro():

    conexao = getDB()
    cursor = conexao.cursor()
    permissao = session.get('USER')

    if permissao == 'anaju':

        if request.method == 'POST':

            nome = request.form.get('Nome')
            valor = request.form.get('Valor')
            foto = request.form.get('Foto')
            link = request.form.get('Link')
            status = 'Disponivel'

            query = "INSERT INTO presentes(Nome, Valor, Imagem, Link, Status) VALUES (%s, %s, %s, %s, %s)"

            cursor.execute(query, (nome, valor, foto, link, status))

            conexao.commit()
            conexao.close()

            return redirect(url_for('presentes')), 301

        return render_template('cadastro.html')

    else:

        return redirect(url_for('login')), 301


@app.route('/presentes/', methods=['GET', 'POST'])
def presentes():

    conexao = getDB()
    cursor = conexao.cursor()

    permissao = session.get('USER')

    if request.method == 'POST':
        session.clear()
        return redirect(url_for('index')), 301

    cursor.execute(
        "SELECT ID, Nome, Valor, Imagem, Link, Status FROM presentes")

    lista_presentes = []

    for row in cursor:
        IDPresente, Nome, Valor, Imagem, Link, Status = row
        lista_presentes.append({
            "ID": IDPresente,
            "Nome": Nome,
            "Valor": Valor,
            "Imagem": Imagem,
            "Link": Link,
            "Status": Status
        })

    return render_template('presentes.html', lista_presentes=lista_presentes, permissao=permissao)


@app.route('/presente/<IDitem>', methods=['GET', 'POST'])
def presente(IDitem):

    conexao = getDB()
    cursor = conexao.cursor()

    permissao = session.get('USER')

    # POST ----------------------------------------------------------------------------------

    if request.method == 'POST':

        if permissao == 'anaju':

            cursor.execute(
                "DELETE FROM presentes WHERE ID = {0}".format(IDitem))
            conexao.commit()
            conexao.close()

            return redirect(url_for('presentes')), 301

        else:

            cursor.execute(
                "UPDATE presentes SET Status = 'Indisponivel' WHERE ID = {0}".format(IDitem))
            conexao.commit()
            conexao.close()

            return redirect(url_for('mensagem', ID=IDitem)), 301

    # RENDER -----------------------------------------------------------------------------

    cursor.execute(
        'SELECT Nome, Valor, Imagem, Link, Status FROM presentes WHERE ID = {0}'.format(IDitem))

    for row in cursor:
        Nome, Valor, Imagem, Link, Status = row
        item = {
            "Nome": Nome,
            "Valor": Valor,
            "Imagem": Imagem,
            "Link": Link,
            "Status": Status
        }

    conexao.close()

    return render_template('presente.html', permissao=permissao, item=item)


@app.route('/mensagem/<ID>', methods=['GET', 'POST'])
def mensagem(ID):

    conexao = getDB()
    cursor = conexao.cursor()

    if request.method == 'POST':

        texto = request.form.get("Texto")
        name = request.form.get("Nome")

        queryNome = "SELECT Nome FROM presentes WHERE ID = {0}".format(ID)
        cursor.execute(queryNome)
        for row in cursor:
            nome = row
            nomeIs = {"nome": nome}

        query = "INSERT INTO mensagens(IDPresente, NomePresente, NomePessoa, Mensagem) VALUES (%s, %s, %s, %s)"
        cursor.execute(query, (ID, nomeIs['nome'][0], name, texto))

        conexao.commit()
        conexao.close()

        return redirect(url_for('index')), 301

    return render_template('mensagem.html')


@app.route('/mensagens/', methods=['GET', 'POST'])
def mensagens():

    conexao = getDB()
    cursor = conexao.cursor()

    permissao = session.get('USER')

    if permissao == 'anaju':

        if request.method == 'POST':
            session.clear()
            return redirect(url_for('index')), 301

        cursor.execute("SELECT NomePresente, NomePessoa, Mensagem FROM mensagens")

        lista_mensagens = []

        for row in cursor:
            NomePresente, NomePessoa, Mensagem = row
            lista_mensagens.append({
                "NomePresente": NomePresente,
                "NomePessoa" : NomePessoa,
                "Mensagem": Mensagem
            })

        return render_template('mensagens.html', lista_mensagens=lista_mensagens)

    else:

        return redirect(url_for('login')), 301


if __name__ == '__main__':
    app.run()
