from socket import *
import struct
import numpy as np
from random import *
from datetime import *
import sys
import select
from math import *
import re


class Rdt:
    # Inicio Duda
    def __init__(self, user_name, type = 'u'):
        self.name = user_name
        self.stateR = "waitSeq_0" # Variável de estado - Começa com o estado inicial "waitCall_0"
        self.stateS = "waitCall_0" # Variável de estado do remetente - Inicializa com o estado "waitCall_0"
        self.endFlag = 0
        self.file_bytes = 0  
        self.time = 1
        self.type = type
        self.payload = ""
        self.users = {}
        self.addr = (0,0)
        self.rdt_socket = socket(AF_INET, SOCK_DGRAM) # Cria um socket UDP (SOCK_DGRAM) usando IPv4 (AF_INET)
        self.rdt_socket.settimeout(self.time)
        self.fimPck = 0 
        self.flag = 0
        HOST = "127.0.0.1"  # Endereço IP do servidor
        HOST_PORT = 5000    # Porta do servidor
        self.dest = (HOST,HOST_PORT)
        if type == 'u':
            self.bufferSize = 1020
        else:
            origin = (HOST, HOST_PORT)
            self.rdt_socket.bind(origin)
            self.bufferSize = 1024

        self.reservas = {sala: {dia: {hora: None for hora in range(8, 18)} for dia in ['SEG', 'TER', 'QUA', 'QUI', 'SEX']} for sala in ['E101', 'E102', 'E103', 'E104', 'E105']}

        self.flag_reservar = False # Utilizado para enviar mensagens diferentes aos conectados no servidor.
        self.flag_cancelar = False
        self.user_name = ''
        self.mensagem_help = '''Comandos disponíveis:
* Conectar ao aplicativo: connect as <nome_do_usuario>
* Sair do aplicativo: bye
* Exibir lista de usuários conectados no momento: list
* Reservar uma sala: reservar <numero_da_sala> <dia> <horário>
* Cancelar uma reserva: cancelar <numero_da_sala> <dia> <horário>
* Checar disponibilidade de uma sala: check <numero_da_sala> <dia>  
'''

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
        if randint(1,9):     # Taxa de perda de 10%
            if self.type == "s":
                self.rdt_socket.sendto(data, self.addr) # Envia os dados para o destino
            else:
                self.rdt_socket.sendto(data, self.dest) # Envia os dados para o destino
        else: 
             self.endFlag = 0      

    def add_user(self, name, addr):
        self.users.update({name : addr})
        self.payload = f"{name} está avaliando reservas!"  

    # Fim Duda

    # Inicio Gabriel     
    
    def broadcast(self, msg):
        for addr in self.users.values():
            self.addr = addr 
            self.isSender(msg)

    def broadcast_dif(self, msg, sender_addr):
        for addr in self.users.values():
            if addr != sender_addr:  # Verificar se o endereço não é do solicitante
                self.addr = addr 
                self.isSender(msg)

    def verificar_disponibilidade(self, sala, dia, hora):
    # Não precisa chamar a função recursivamente
    # Apenas verifique se o valor no dicionário de reservas é None
        return self.reservas[sala][dia][int(hora)] is None
    
    def verificar_condicoes_de_cancelamento(self, sala, dia, hora, quem_solicitou):
        if self.reservas[sala][dia][int(hora)] == quem_solicitou:
            return True
        else:
            return False

    def realizar_reserva(self, user_name, sala, dia, hora):
        if self.verificar_disponibilidade(sala, dia, hora):
            self.reservas[sala][dia][hora] = user_name
            return True
        return False

    def cancelar_reserva(self, sala, dia, hora):
        self.reservas[sala][dia][int(hora)] = None
    
    # Função para pegar o formato do reservar
    def _reservar(self, string):
        padrao = r'\w+:\sreservar\s(E101|E102|E103|E104|E105)\s(SEG|TER|QUA|QUI|SEX)\s(1[0-8]|[89])$'
        if re.match(padrao, string):
            return True
        else:
            return False
        
    def _cancelar(self, string):
        padrao = r'\w+:\scancelar\s(E101|E102|E103|E104|E105)\s(SEG|TER|QUA|QUI|SEX)\s(1[0-8]|[89])$'
        if re.match(padrao, string):
            return True
        else:
            return False
        
    def _check(self, string):
        padrao = r'\w+:\scheck\s(E101|E102|E103|E104|E105)\s(SEG|TER|QUA|QUI|SEX)$'
        if re.match(padrao, string):
            return True
        else:
            return False
    
    # Fim Gabriel
        
    # Inicio Antonio

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

                    if seq == 0:
                        self.endFlag=1
                        payload = payload.decode()

                        # Funções para verificar o formato de
                        reservar = self._reservar(payload)
                        cancelar = self._cancelar(payload)
                        check = self._check(payload) # True or False

                        # Quando chega um novo usuário
                        if payload[-5:] == ": SYN":
                            # Se o nome não tiver disponível retorna 24 e é tratado em user.py para escolher outro nome
                            if payload[0:-5] in self.users.keys():
                                return 2000
                            # Adiciona um novo usuário
                            self.add_user(payload[0:-5],self.addr)

                        elif payload[-6:] == ": list":
                            self.flag = 1
                            self.payload = str([str(k) for k in self.users.keys()])

                        elif reservar:
                            parts = payload.split()

                            self.user_name = parts[0][:-1]
                        
                            # Verifique se tem a quantidade correta de partes para o comando 'reservar'
                            if len(parts) >= 5:  # Deve ser algo como ": reservar sala dia hora"
                                _, sala, dia_abrev, hora = parts[1:5]

                                # Dicionário para mapear abreviações para nomes completos dos dias da semana
                                dias_da_semana_completo = {
                                    "SEG": "Segunda",
                                    "TER": "Terça",
                                    "QUA": "Quarta",
                                    "QUI": "Quinta",
                                    "SEX": "Sexta"
                                }

                                # print("self.reservas 1: " + str(self.reservas[sala][dia_abrev][int(hora)]))

                                # Agora quero verificar se há disponibilidade de sala
                                disponivel = self.verificar_disponibilidade(sala, dia_abrev, int(hora))

                                # Verifica o formato da mensagem - Retorna True - Já muda o status de self.reservas[...][...][...]
                                sucesso = self.realizar_reserva(self.user_name, sala, dia_abrev, int(hora))

                                if disponivel:
                                    if sucesso:
                                        # Aqui utilizamos self.addr para obter o IP e a porta do remetente da reserva
                                        ip, porta = self.addr

                                        # Flag para enviar mensagens diferentes
                                        self.flag_reservar = True
                                        
                                        msg_para_solicitante = f"Você [{ip}:{porta}] reservou a sala {sala}."
                                        msg = f"{self.user_name} [{ip}:{porta}] reservou a sala {sala} na {dias_da_semana_completo[dia_abrev]} às {hora}h. "
                                        
                                        msg = msg + msg_para_solicitante
                                        self.flag = 0

                                    else:
                                        msg = "Comando inválido, porfavor, verificar comandos disponíveis com --help"
                                        self.flag = 1
                                else:
                                    msg = f"A sala {sala} está indisponível para reservas na {dias_da_semana_completo[dia_abrev]} às {hora}h. {self.reservas[sala][dia_abrev][int(hora)]} tem posse dessa reserva."
                                    self.flag = 1

                                self.payload = msg

                        elif cancelar:
                            # Checar se o usuário que mandou a solicitação foi o mesmo que consta no dicionário de reservas
                            parts = payload.split()

                            self.user_name = parts[0][:-1]

                            if len(parts) >= 5: 
                                _, sala, dia_abrev, hora = parts[1:5]

                                dias_da_semana_completo = {
                                    "SEG": "Segunda-Feira",
                                    "TER": "Terça-Feira",
                                    "QUA": "Quarta-Feira",
                                    "QUI": "Quinta-Feira",
                                    "SEX": "Sexta-Feira"
                                }

                                # Preciso criar uma grande verificação para saber se quem solicitou cancelar foi o mesmo que possui a reserva
                                pode_cancelar = self.verificar_condicoes_de_cancelamento(sala, dia_abrev, int(hora), self.user_name)

                                # Se for posso cancelar a reserva e atribuir 2 flags:
                                if pode_cancelar:
                                    # Esta função só irá atualizar o self.reservas - Dicionário de reservas

                                    self.cancelar_reserva(sala, dia_abrev, hora)

                                    # 1° - Usuário que solicitou cancelar: Sua reserva foi cancelada
                                    # Aqui utilizamos self.addr para obter o IP e a porta do remetente da reserva
                                    ip, porta = self.addr

                                    # Flag para enviar mensagens diferentes
                                    self.flag_cancelar = True
                                    
                                    msg_para_solicitante = f"Você [{ip}:{porta}] cancelou a sua reserva com exito."
                                    msg = f"{self.user_name} [{ip}:{porta}] cancelou a sua reserva. Portanto, a sala {sala}  disponível para reserva novamente na {dias_da_semana_completo[dia_abrev]} às {hora}h."
                                    
                                    msg = msg + msg_para_solicitante
                                    self.flag = 0

                                else:
                                    self.flag = 1
                                    msg = "Você não possui esta reserva, portando não está apto a cancelar."

                                self.payload = msg

                        # Fim Antonio
                                
                        # Inicio Heitor

                        elif check:
                            # check <numero_da_sala> <dia>
                            # Checar se o usuário que mandou a solicitação foi o mesmo que consta no dicionário de reservas
                            parts = payload.split()
                            pass
                        
                        elif payload[-5:] == ": bye":
                            aux = payload[0:-5]
                            del self.users[payload[0:-5]]
                            self.flag = 0
                            self.payload = f"{aux} saiu do sistema de reservas!"
                                                  
                        elif payload[-8:] == ": --help":
                            self.flag = 1
                            self.payload = self.mensagem_help

                        else:
                            if self.type == "s": 
                                date_str = str(datetime.now())
                                payload = f"{self.addr[0]}:{self.addr[1]}/~{payload}" + " " + date_str
                            if "~" in payload and self.type == 'u': 
                                nome1 = payload.split("~")
                                nome2 = nome1[1].split(":")

                            print(payload)
                            self.payload = payload

                        action = "sendAck0"   # Ao receber pacote, se o número de sequência for zero manda ack correspondente
                    
                    else: 
                        action = "sendAck1" # Se o pacote não é o correto, manda o ack de sequência 1, ao invés disso
                        self.endFlag=1
                    
                    # Fim Heitor
                
            # Comentar sobre o estado de espra que é uma repetição do  isReceptor seq=0
            # Duda
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
                        self.endFlag=1
                        payload = payload.decode()
                        if payload[-5:] == ": SYN":
                            if payload[0:-5] in self.users.keys():
                                return 2000
                            self.add_user(payload[0:-5],self.addr)

                        elif payload[-6:] == ": list":
                            self.flag = 1
                            self.payload = str([str(k) for k in self.users.keys()])

                        elif reservar:
                            parts = payload.split()

                            self.user_name = parts[0][:-1]
                        
                            # Verifique se tem a quantidade correta de partes para o comando 'reservar'
                            if len(parts) >= 5:  # Deve ser algo como ": reservar sala dia hora"
                                _, sala, dia_abrev, hora = parts[1:5]

                                # Dicionário para mapear abreviações para nomes completos dos dias da semana
                                dias_da_semana_completo = {
                                    "SEG": "Segunda",
                                    "TER": "Terça",
                                    "QUA": "Quarta",
                                    "QUI": "Quinta",
                                    "SEX": "Sexta"
                                }

                                # print("self.reservas 1: " + str(self.reservas[sala][dia_abrev][int(hora)]))

                                # Agora quero verificar se há disponibilidade de sala
                                disponivel = self.verificar_disponibilidade(sala, dia_abrev, int(hora))

                                # Verifica o formato da mensagem - Retorna True - Já muda o status de self.reservas[...][...][...]
                                sucesso = self.realizar_reserva(self.user_name, sala, dia_abrev, int(hora))

                                if disponivel:
                                    if sucesso:
                                        # Aqui utilizamos self.addr para obter o IP e a porta do remetente da reserva
                                        ip, porta = self.addr

                                        # Flag para enviar mensagens diferentes
                                        self.flag_reservar = True
                                        
                                        msg_para_solicitante = f"Você [{ip}:{porta}] reservou a sala {sala}."
                                        msg = f"{self.user_name} [{ip}:{porta}] reservou a sala {sala} na {dias_da_semana_completo[dia_abrev]} às {hora}h. "
                                        
                                        msg = msg + msg_para_solicitante
                                        self.flag = 0

                                    else:
                                        msg = "Comando inválido, porfavor, verificar comandos disponíveis com --help"
                                        self.flag = 1
                                else:
                                    msg = f"A sala {sala} está indisponível para reservas na {dias_da_semana_completo[dia_abrev]} às {hora}h. {self.reservas[sala][dia_abrev][int(hora)]} tem posse dessa reserva."
                                    self.flag = 1

                                self.payload = msg

                        elif cancelar:
                            # Checar se o usuário que mandou a solicitação foi o mesmo que consta no dicionário de reservas
                            parts = payload.split()

                            self.user_name = parts[0][:-1]

                            if len(parts) >= 5: 
                                _, sala, dia_abrev, hora = parts[1:5]

                                dias_da_semana_completo = {
                                    "SEG": "Segunda-Feira",
                                    "TER": "Terça-Feira",
                                    "QUA": "Quarta-Feira",
                                    "QUI": "Quinta-Feira",
                                    "SEX": "Sexta-Feira"
                                }

                                # Preciso criar uma grande verificação para saber se quem solicitou cancelar foi o mesmo que possui a reserva
                                pode_cancelar = self.verificar_condicoes_de_cancelamento(sala, dia_abrev, int(hora), self.user_name)

                                # Se for posso cancelar a reserva e atribuir 2 flags:
                                if pode_cancelar:
                                    # Esta função só irá atualizar o self.reservas - Dicionário de reservas

                                    self.cancelar_reserva(sala, dia_abrev, hora)

                                    # 1° - Usuário que solicitou cancelar: Sua reserva foi cancelada
                                    # Aqui utilizamos self.addr para obter o IP e a porta do remetente da reserva
                                    ip, porta = self.addr

                                    # Flag para enviar mensagens diferentes
                                    self.flag_cancelar = True
                                    
                                    msg_para_solicitante = f"Você [{ip}:{porta}] cancelou a sua reserva com exito."
                                    msg = f"{self.user_name} [{ip}:{porta}] cancelou a sua reserva. Portanto, a sala {sala}  disponível para reserva novamente na {dias_da_semana_completo[dia_abrev]} às {hora}h."
                                    
                                    msg = msg + msg_para_solicitante
                                    self.flag = 0

                                else:
                                    self.flag = 1
                                    msg = "Você não possui esta reserva, portando não está apto a cancelar."

                                self.payload = msg

                        elif payload[-5:] == ": bye":
                            aux = payload[0:-5]
                            del self.users[payload[0:-5]]
                            self.flag = 0
                            self.payload = f"{aux} saiu do sistema de reservas!"
                        
                        elif payload[-8:] == ": --help":
                            self.flag = 1
                            self.payload =   self.mensagem_help

                        else:
                            if self.type == "s": 
                                date_str = str(datetime.now())
                                payload = f"{self.addr[0]}:{self.addr[1]}/~{payload}" + " " + date_str
                            if "~" in payload and self.type == 'u': 
                                nome1 = payload.split("~")
                                nome2 = nome1[1].split(":")

                            print(payload)
                            print("Entrou no wait_seq_1")
                            self.payload = payload

                        action = "sendAck1"   # Ao receber pacote, se o número de sequência for zero manda ack correspondente
                    else: 
                        action = "sendAck0" # Se seq pacote nao for o esperado, manda o ack de sequencia 0, e deve continuar no mesmo estado 
                        self.endFlag=1

            # Inicio Gabriel
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
            # Fim Gabriel

    # Inicio Karol

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
                self.stateS = "waitAck_0"

            elif action == "stopTimer_0":
                self.rdt_socket.settimeout(self.time) #reseta timer
                self.stateS = "waitCall_1"

            elif action == "sendPktSeq_1":
                data = mensagem.encode()    # Lê 1024 bytes do arquivo
                self.fimPck = 1
                self.sendPkt(data, 1)
                self.stateS = "waitAck_1"

            elif action == "stopTimer_1":
                self.rdt_socket.settimeout(self.time) #reseta timer
                self.stateS = "waitCall_0"

            elif action == "ReSendPktSeq_0":
                self.fimPck = 1
                self.sendPkt(data, 0)
                self.stateS = "waitAck_0"
            
            elif action == "ReSendPktSeq_1":
                self.fimPck = 1
                self.sendPkt(data, 1)
                self.stateS = "waitAck_1"     

    # Fim Karol

    # Inicio Miriam
                        
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
                        if self.flag == 0 and self.flag_reservar:
                            # Spam de reserva ou de frases que precisam ser diferentes para os usuários.

                            self.isSender(self.payload[-44:]) # Esse formato sempre será o mesmo por isso posso fazer dessa forma
                            self.broadcast_dif(self.payload[:-44], self.addr)

                            self.flag_reservar = False

                        elif self.flag == 0 and self.flag_cancelar:
                            self.isSender(self.payload[-56:])
                            self.broadcast_dif(self.payload[:-56], self.addr)

                            self.flag_cancelar = False

                        elif self.flag == 0 and self.flag_reservar == False:
                            self.broadcast(self.payload)
                        elif self.flag == 1:
                            self.isSender(self.payload)
                            self.flag = 0
                        elif self.flag == 2:
                            self.flag = 0
                        else:
                            self.flag = 0
                    elif self.flag == 666:
                            return
                        
                           
                elif sock == sys.stdin:
                    # Se o usuário digitou algo no terminal, encerre o servidor
                    input_text = sys.stdin.readline()
                    input_text = input_text.strip()
                    self.isSender(input_text)

                    if input_text == "bye": return
    
    # Fim Miriam