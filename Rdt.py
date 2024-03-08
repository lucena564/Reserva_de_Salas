from socket import *
import struct
import numpy as np
from random import *
from datetime import *
import sys
import select
from math import *


class Rdt:
    def __init__(self, user_name, type = 'u'):
        self.name = user_name
        self.stateR = "waitSeq_0" # Variável de estado - Começa com o estado inicial "waitCall_0"
        self.stateS = "waitCall_0" # Variável de estado do remetente - Inicializa com o estado "waitCall_0"
        self.endFlag = 0
        self.file_bytes = 0  
        self.time = 1
        self.type = type
        # self.counter = 0
        # self.banido = ""
        self.payload = ""
        self.users = {}
        self.addr = (0,0)
        self.rdt_socket = socket(AF_INET, SOCK_DGRAM) # Cria um socket UDP (SOCK_DGRAM) usando IPv4 (AF_INET)
        self.rdt_socket.settimeout(self.time)
        self.fimPck = 0 
        self.flag = 0
        self.friend_list = []
        HOST = "127.0.0.1"  # Endereço IP do servidor
        HOST_PORT = 5000         # Porta do servidor
        self.dest = (HOST,HOST_PORT)
        if type == 'u':
            self.bufferSize = 1020
        else:
            origin = (HOST, HOST_PORT)
            self.rdt_socket.bind(origin)
            self.bufferSize = 1024

    def sendPkt(self, payload, seqNum): # Converte os dados em uma representação de string e codifica em bytes
        tam = len(payload)
        data = bytearray(4 + tam)
        data = struct.pack(f'i {tam}s', seqNum, payload)
        if randint(0,3):   # Taxa de perda de 25%
            if self.type == "s": 
                self.rdt_socket.sendto(data, self.addr) # Envia os dados para o destino
            else: self.rdt_socket.sendto(data, self.dest) # Envia os dados para o destino

    def sendAck(self,ack):
        data = struct.pack('i', ack)
        #self.rdt_socket.sendto(data, self.addr)
        if randint(1,9):     #taxa de perda de 10%
            if self.type == "s":
                self.rdt_socket.sendto(data, self.addr) # Envia os dados para o destino
            else:
                self.rdt_socket.sendto(data, self.dest) # Envia os dados para o destino
        else: 
             self.endFlag = 0      

    def add_user(self, name, addr):
        self.users.update({name : addr})
        self.payload = f"{name} está avaliando reservas!"       
    
    def broadcast(self, msg):
        for addr in self.users.values():
            self.addr = addr 
            self.isSender(msg)

    # def broadcast_ban(self):
    #     if self.counter >= (floor(len(self.users)/2)+1):
    #         msg = f"{self.counter}/{floor(len(self.users)/2)+1}"
    #         self.broadcast(msg)
    #         msg = f"usuario {self.banido} foi banido"
    #         self.addr = self.users[self.banido]
    #         self.isSender("voce foi banido")
    #         del self.users[self.banido]
    #         self.banido = ""
    #         self.counter = 0
    #         self.friend_list.clear()
    #     elif self.counter == 1:
    #         msg = "votacao iniciada: 1/" + str(floor(len(self.users)/2)+1)
    #     else:
    #         msg = f"banimento de {self.banido}: {self.counter}/{str(floor(len(self.users)/2)+1)}"
    #     self.broadcast(msg)

    def isReceptor(self):
        self.time = 10000
        self.rdt_socket.settimeout(self.time)
        while(True): # Loop principal da maquina de estados finitos do receptor
            if self.stateR == "waitSeq_0": # Estado de esperar pelo pacote 0
                try:
                    pckg, self.addr = self.rdt_socket.recvfrom(self.bufferSize) # Recebe o pacote se algum chegar
                except timeout: 
                    pass # Enquanto nao houver pacote para receber, apenas espera
                else: 
                    tam = len(pckg) - 4
                    pckg = struct.unpack_from(f'i {tam}s', pckg)
                    seq = pckg[0]
                    payload = pckg[1]
                    # print("Antes de tudo:    " + str(payload))

                    if seq == 0:
                        #if(payload[0] == b'FIM'): # Se recebeu mensagem final do sender, encerra o loop
                        self.endFlag=1
                        payload = payload.decode()
                        # Quando chega um novo usuário
                        if payload[-5:] == ": SYN":
                            # Se o nome não tiver disponível retorna 24 e é tratado em user.py para escolher outro nome
                            if payload[0:-5] in self.users.keys():
                                return 24
                            # Adiciona um novo usuário
                            self.add_user(payload[0:-5],self.addr)

                        elif payload[-6:] == ": list":
                            self.flag = 1
                            self.payload = str([str(k) for k in self.users.keys()])

                        elif payload[-5:] == ": bye":
                            aux = payload[0:-5]
                            del self.users[payload[0:-5]]
                            self.flag = 0
                            self.payload = f"{aux} saiu do sistema de reservas!"
                            
                        
                        elif payload[-8:] == ": --help":
                            self.flag = 1
                            self.payload =   '''Comandos disponíveis:
                                                Conectar ao aplicativo: connect as <nome_do_usuario>
                                                Sair do aplicativo: bye
                                                Exibir lista de usuários conectados no momento: list
                                                Reservar uma sala: reservar <numero_da_sala> <dia> <horário>
                                                Cancelar uma reserva: cancelar <numero_da_sala> <dia> <horário>
                                                Checar disponibilidade de uma sala: check <numero_da_sala> <dia>  
                                            '''
                        # elif ": ban" in payload:
                        #     string = payload.split(":")
                        #     if string[1][1:4] == "ban": 
                        #         if (string[1][5:] == self.banido and string[0] not in self.friend_list) or (self.banido == "" and string[1][5:] in self.users.keys()):
                        #             self.banido = string[1][5:]
                        #             self.counter += 1
                        #             self.friend_list.append(string[0])
                        #             self.flag = 3
                        # elif "Você foi banido"in payload:
                        #     print(payload)
                        #     self.flag = 666
                        else:
                            if self.type == "s": 
                                date_str = str(datetime.now())
                                payload = f"{self.addr[0]}:{self.addr[1]}/~{payload}" + " " + date_str
                            if "~" in payload and self.type == 'u': 
                                nome1 = payload.split("~")
                                nome2 = nome1[1].split(":")
                                if nome2[0] in self.friend_list:
                                    payload = nome1[0] + "~[Amigo] " + nome1[1]
                            print(payload)
                            print("Teste1")
                            self.payload = payload
                        action = "sendAck0"   # Ao receber pacote, se o número de sequência for zero manda ack correspondente
                    else: 
                        action = "sendAck1" # Se o pacote não é o correto, manda o ack de sequência 1, ao invés disso
                        #if(payload[0] == b'FIM'): # Se recebeu mensagem final do sender, encerra o loop
                        self.endFlag=1
                
            elif self.stateR == "waitSeq_1": # Estado de esperar pelo pacote 1
                try:
                    pckg, self.addr = self.rdt_socket.recvfrom(self.bufferSize) # Recebe o pacote se algum chegar
                except: 
                    pass  # Esperar ate um pacote chegar
                else:
                    tam = len(pckg) - 4
                    pckg = struct.unpack_from(f'i {tam}s', pckg)
                    seq = pckg[0]
                    payload = pckg[1]

                    if seq == 1:
                        #if(payload[0] == b'FIM'): # Se recebeu mensagem final do sender, encerra o loop
                        self.endFlag=1
                        payload = payload.decode()
                        if payload[-5:] == ": SYN":
                            if payload[0:-5] in self.users.keys():
                                return 24
                            self.add_user(payload[0:-5],self.addr)

                        elif payload[-6:] == ": list":
                            self.flag = 1
                            self.payload = str([str(k) for k in self.users.keys()])

                        elif payload[-5:] == ": bye":
                            aux = payload[0:-5]
                            del self.users[payload[0:-5]]
                            self.flag = 0
                            self.payload = f"{aux} saiu do sistema de reservas!"
                        
                        elif payload[-8:] == ": --help":
                            self.flag = 1
                            self.payload =   '''Comandos disponíveis:
                                                Conectar ao aplicativo: connect as <nome_do_usuario>
                                                Sair do aplicativo: bye
                                                Exibir lista de usuários conectados no momento: list
                                                Reservar uma sala: reservar <numero_da_sala> <dia> <horário>
                                                Cancelar uma reserva: cancelar <numero_da_sala> <dia> <horário>
                                                Checar disponibilidade de uma sala: check <numero_da_sala> <dia>  
                                            '''
                        # elif ": ban" in payload:
                        #     string = payload.split(":")
                        #     if string[1][1:4] == "ban": 
                        #         if (string[1][5:] == self.banido and string[0] not in self.friend_list) or (self.banido == "" and string[1][5:] in self.users.keys()):
                        #             self.banido = string[1][5:]
                        #             self.counter += 1
                        #             self.friend_list.append(string[0])
                        #             self.flag = 3
                        # elif "voce foi banido"in payload:
                        #     print(payload)
                        #     self.flag = 666
                        else:
                            if self.type == "s": 
                                date_str = str(datetime.now())
                                payload = f"{self.addr[0]}:{self.addr[1]}/~{payload}" + " " + date_str
                            if "~" in payload and self.type == 'u': 
                                nome1 = payload.split("~")
                                nome2 = nome1[1].split(":")
                                if nome2[0] in self.friend_list:
                                    payload = nome1[0] + "~[Amigo] " + nome1[1]
                            print(payload)
                            print("Entrou no wait_seq_1")
                            self.payload = payload
                        action = "sendAck1"   # Ao receber pacote, se o número de sequência for zero manda ack correspondente
                    else: 
                        action = "sendAck0" # Se seq pacote nao for o esperado, manda o ack de sequencia 0, e deve continuar no mesmo estado 
                        #if(payload[0] == b'FIM'): # Se recebeu mensagem final do sender, encerra o loop
                        self.endFlag=1

            if action == "sendAck0":
                self.sendAck(0)           # Manda o ack de sequência 0
                if self.endFlag: 
                    self.stateR = "waitSeq_0"
                    break
                self.stateR = "waitSeq_1"  # Muda de estado para waitSeq_1
                
            elif action == "sendAck1":
                self.sendAck(1)          # Manda ack de sequencia 1
                if self.endFlag: 
                    self.stateR = "waitSeq_0"
                    break
                self.stateR = "waitSeq_0" # Muda o estado para waitSeq_0

    def isSender(self, mensagem):
        self.time = 1
        self.rdt_socket.settimeout(self.time)
        if self.type != "s":
            mensagem = "" + mensagem + ""
            mensagem = f"{self.name}: {mensagem}"
                                
        while(True): #Loop principal da máquina de estados finitos do remetente
            if self.stateS == "waitCall_0":
            # Estado de esperar para enviar o pacote de sequência 0
                action = "sendPktSeq_0" # Manda o pacote de sequência 0

            elif self.stateS == "waitAck_0":
            # Estado de esperar recebimento do Ack 0 após o pacote 0 ter sido enviado
                try:
                    ack_pck = self.rdt_socket.recv(self.bufferSize) # Se chegar um pacote Ack, recebe o Ack
                except timeout:
                    action = "ReSendPktSeq_0" # Se ocorrer um timeout, manda novamente o pacote de sequência 0
                else:
                    ack_pck = struct.unpack_from('i', ack_pck) # Decodifica o pacote ACK
                    ack = ack_pck[0]             # Obtém o campo ACK do pacote
                    if ack == 0: 
                        action = "stopTimer_0" # Se o ACK for 0, reseta o timer
                        if self.fimPck: 
                            self.stateS = "waitCall_0"
                            break
                    else: 
                        action = "ReSendPktSeq_0" # Se o ack for tiver a sequência errada, manda novamente o pacote 0

            elif self.stateS == "waitCall_1":
            # Estado de esperar para enviar o pacote de sequência 1
                action = "sendPktSeq_1" # Manda o pacote de sequência 1

            elif self.stateS == "waitAck_1":
            # Estado de esperar recebimento do Ack 1 após o pacote 1 ter sido enviado
                try:
                    ack_pck = self.rdt_socket.recv(self.bufferSize) # Se chegar um pacote Ack, recebe o Ack
                except timeout:
                    action = "ReSendPktSeq_1" # Se ocorrer um timeout, manda novamente o pacote de sequência 1
                else:
                    ack_pck = struct.unpack_from('i', ack_pck) # Decodifica o pacote ACK
                    ack = ack_pck[0]             # Obtém o campo ACK do pacote
                    if ack == 1:
                        action = "stopTimer_1" # Se o ACK for 1, reseta o timer
                        if self.fimPck: # Envio encerrou e receiver recebeu tudo
                            self.stateS = "waitCall_0"
                            break
                    else:
                        action = "ReSendPktSeq_1" # Se o ack for tiver a sequência errada, manda novamente o pacote 1

            if action == "sendPktSeq_0":
                data = mensagem.encode()  # Lê 1024 bytes do arquivo
                self.fimPck = 1
                self.sendPkt(data, 0)
                # if not data:
                #     self.fimPck = 1
                #     self.sendPkt(b'FIM', 0)
                # else:
                #     self.sendPkt(data, 0)
                    
                self.stateS = "waitAck_0"

            elif action == "stopTimer_0":
                self.rdt_socket.settimeout(self.time) #reseta timer
                self.stateS = "waitCall_1"

            elif action == "sendPktSeq_1":
                data = mensagem.encode()    # Lê 1024 bytes do arquivo
                self.fimPck = 1
                self.sendPkt(data, 1)
                # if not data: 
                #     self.fimPck = 1
                #     self.sendPkt(b'FIM', 1)
                # else: # ainda há pacotes para enviar
                #     self.sendPkt(data, 1)
                self.stateS = "waitAck_1"

            elif action == "stopTimer_1":
                self.rdt_socket.settimeout(self.time) #reseta timer
                self.stateS = "waitCall_0"

            elif action == "ReSendPktSeq_0":
                self.fimPck = 1
                self.sendPkt(data, 0)
                # if not data: 
                #     self.fimPck = 1
                #     self.sendPkt(b'FIM', 0)
                # else: # ainda há pacotes para enviar
                #     self.sendPkt(data, 0)
                self.stateS = "waitAck_0"
            
            elif action == "ReSendPktSeq_1":
                self.fimPck = 1
                self.sendPkt(data, 1)
                # if not data: 
                #     self.fimPck = 1
                #     self.sendPkt(b'FIM', 1)
                # else: # ainda há pacotes para enviar
                #     self.sendPkt(data, 1)
                self.stateS = "waitAck_1"     
        #file.close()

    def waiting(self):
        while True:
            # Use select para monitorar o socket e a entrada do terminal
            inputs, _, _ = select.select([self.rdt_socket, sys.stdin], [], [])

            for sock in inputs:
                if sock == self.rdt_socket:
                    # Aguarde dados do cliente
                    data, client_address = self.rdt_socket.recvfrom(1024)
                    self.isReceptor()
                    if self.type == "s":
                        if self.flag == 0:
                            self.broadcast(self.payload)
                        elif self.flag == 1:
                            self.isSender(self.payload)
                            self.flag = 0
                        elif self.flag == 2:
                            self.flag = 0
                        else:
                            if(self.counter > 0):
                                # self.broadcast_ban()
                                continue
                            self.flag = 0
                    elif self.flag == 666:
                            return
                        
                           
                elif sock == sys.stdin:
                    # Se o usuário digitou algo no terminal, encerre o servidor
                    input_text = sys.stdin.readline()
                    input_text = input_text.strip()
                    if input_text == "mylist":
                        print(self.friend_list)
                    elif input_text[0:11] == "addtomylist":
                        if (input_text[12:] not in self.friend_list):
                            self.friend_list.append(input_text[12:])
                    elif input_text[0:13] == "rmvfrommylist":
                        if (input_text[14:] in self.friend_list):
                            self.friend_list.remove(input_text[14:])
                    else: self.isSender(input_text)
                    if input_text == "bye": return
                        