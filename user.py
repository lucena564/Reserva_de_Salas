from Rdt import *

def main():
    '''Cada user terá um nome e um socket para se comunicar com o servidor.
    Por esse motivo teremos que pensar que todos os usuários, quando forem
    instanciados, terão que se conectar ao servidor.
    
    Levando isso em consideração, todos os users vão rodar o user.py no seu
    terminal e farão o comando connect as <nome_do_usuario> para se conectar,
    depois disso será iremos conectar o usuário ao servidor e ele poderá
    fazer as operações de reservar, cancelar, listar, etc.
    '''

    print("Bem vindo à reserva de salas! Digite --help depois de se conectar ao servidor para ver os comandos disponíveis.")
    flag = True

    while True:
        comando = str(input())

        if comando.lower().startswith("connect as "):
            name = comando[11:]
            User = Rdt(name)

            if User.isSender("SYN") == 24:
                print("Nome já utilizado tente outro")
            else:
                # Verificar o que o user vai fazer aqui dentro.
                User.waiting()

        '''A partir do memento que o usuário for conectado,
        todas as requisições serão feitas via chat, então
        não será mais preciso nenhum outro tratamento.'''

        #     if flag:
        #         print("Conectado ao servidor com sucesso!")  # Added print statement to indicate successful connection
        #         flag = False

        #     break

        # elif comando.lower().startswith("bye"):
        #     break

        # elif comando.lower().startswith("list"):
        #     break

        # elif comando.lower().startswith("reservar "):
        #     '''reservar <numero_da_sala> <dia> <horário>'''
        #     break

        # elif comando.lower().startswith("cancelar "):
        #     '''cancelar <numero_da_sala> <dia> <horário>'''
        #     break

        # elif comando.lower().startswith("check "):
        #     '''check <numero_da_sala> <dia>'''
        #     break

        # elif comando.lower().startswith("--help"):
        #     print("Entrou")
        #     # Envia o comando --help para o servidor 
        #     User.isSender("--help")

        # else:
        #     print("Comando inesistente.")

if __name__ == "__main__":
    main()