from Rdt import *
import time

def main():
    print("\nAbrindo servidor... Por favor, aguarde 5 segundos\n")
    i = 5
    while i != 0:
        print(str(i))
        time.sleep(1)
        i = i - 1
    print('0\n')

    # Criando o servidor
    server = Rdt("server",'s')

    print("Servidor aberto.\n\n")

    server.waiting()


if __name__ == "__main__":
    main()