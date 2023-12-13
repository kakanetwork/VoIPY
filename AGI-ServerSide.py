#!/usr/bin/python
import mysql.connector
from asterisk.agi import *
import sys, socket


''' FUNCOES RELACIONADAS AO BD E LOGIN DO USUARIO '''

# funcao para realizar a conexao do banco
def connection():
    mydb = mysql.connector.connect(
        host = "XXX.XXX.XXX.XXX",
        user = "XXXXX",
        password = "XXXXX",
        database = "XXXX")

    # e retornado o objeto da conexao
    return mydb

# funcao que realiza a comparacao das senha
def verify_pass(pass_user, pass_db):
    variable = 'invalida'
    pass_user = int(pass_user) # pass_user vem como string, convertendo para int
    agi.verbose(500, pass_user)

    # comparacao das senhas
    if pass_user == pass_db:
        # se a senha tiver correta altera o valor de "variable" para "autenticado"
        variable = 'autenticado'

    # seta a variable, para pegarmos no extensions.conf do asterisk
    agi.set_variable("resultado", variable)

# funcao que realiza a chamada das demais funcoes de login e a consulta das senhas no DB com base no ID
def login(pass_user,id):

    # chama a funcao connection() que realiza conexao no DB
    mydb = connection()
    mycursor = mydb.cursor()

    # consulta na tabela especificada, a senha_voip com base no ID
    mycursor.execute("SELECT senha_voip FROM tabela_teste WHERE id={0}".format(id))

    # fetchone para pegar uma tupla (se fosse fetchall pegaria uma lista de tuplas, mesmo que unica)
    myresult = mycursor.fetchone()

    # verifico se myresult retornou vazia, se sim e porque o ID nao existe
    if myresult:

        # entrando na condicao, transformo o resultado em inteiro
        pass_db = int(myresult[0])
        agi.verbose(400, pass_db)

        # e chamo a funcao que realiza a verificacao, passando a senha digitada e a senha do DB, com base no ID
        verify_pass(pass_user, pass_db)

    # se myresult for vazio, significa que o ID digitado nao existe
    else:
        agi.verbose('entrou no else')
        text = 'invalida'

        # seto a variable como invalida, e envio para o extensions.conf do asterisk
        agi.set_variable('resultado', text)

    # fechando o cursor e conexao do DB, para evitar erros
    mycursor.close()
    mydb.close()

# funcao que realiza a troca da senha
def change(new_pass,id):
    mydb = connection()
    mycursor = mydb.cursor()

    # enviando o comando SQL para trocar a senha na tabela, com base no ID

    mycursor.execute("UPDATE tabela_teste SET senha_voip = {0} WHERE id = {1}".format(new_pass,id))

    # rowcount = conta quantas linhas foram afetadas pelo comando, se = zero e porque nao funcionou
    # utilizo de no caso o ID tiver alguma alteracao durante o periodo de consulta
    if mycursor.rowcount > 0:
        agi.verbose("trocou senha")
        variable = "valido"
    else:
        agi.verbose("nao trocou a senha")
        variable = "invalido"

    agi.set_variable("resultado", variable)
    mycursor.close()
    mydb.close()


''' FUNCOES RELACIONADAS A SOLICITACAO DE SERVICOS DO SERVIDOR (FUNCAO PRINCIPAL)'''


def server(id):
    # COMENTARIO DE AFAZERES: temos que pegar no BD o seu email, e verificar quais os servicos que ele possui no servidor de ASA
    # porque ele pode pode possuir apenas o APACHE, ou apenas o DOVECOT (ja que e ele que determina a criacao)
    # ABAIXO, ja estou pegando o email (com base no id dele) e solicitando os dados do servidor
    # ENTRETANTO, nao estou fazendo nada com eles, apenas pegando para adiantar

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(("192.168.102.128",50005))
    retorno = (s.recv(1024)).decode()


    texto = eval(retorno)
    agi.verbose(texto[0])
    agi.verbose(texto[1])
    agi.verbose(texto[2])
    agi.verbose(texto[3])
    agi.verbose(texto[4])
    agi.verbose(type(texto))
    agi.set_variable('dovecot', texto[0])
    agi.set_variable('named', texto[1])
    agi.set_variable('postfix', texto[2])
    agi.set_variable('apache', texto[3])
    agi.set_variable('ssh', texto[4])


agi = AGI()

msg = agi.get_variable("msg")
id = agi.get_variable("identifier")

agi.verbose(msg)
agi.verbose(id)

if msg == 'login':
        pass_user = agi.get_variable("password")
        agi.verbose(pass_user)
        login(pass_user,id)

elif msg == 'change':
        new_pass = agi.get_variable("new_pass")
        agi.verbose(new_pass)
        change(new_pass,id)

elif msg == 'server':
        server(id)

else:
        print('problema encontrado.', sys.exc_info()[0])

sys.exit()
