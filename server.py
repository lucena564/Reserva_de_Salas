from Rdt import *
import time

def start_serv():
    print("\nAbrindo servidor... Por favor, aguarde 10 segundos\n")
    i = 10
    while i != 0:
        print(str(i))
        time.sleep(1)
        i = i - 1
    print('0\n')
    print("Servidor aberto.\n\n")


# Criando o servidor
server = Rdt("server",'s')

# start_serv()
print("Aberto")

server.waiting()