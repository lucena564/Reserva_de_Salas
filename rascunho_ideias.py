reservas = {sala: {dia: {hora: None for hora in range(8, 18)} for dia in ['SEG', 'TER', 'QUA', 'QUI', 'SEX']} for sala in ['E101', 'E102', 'E103', 'E104', 'E105']}
# print(reservas)

import re

def verifica_formato(string):
    padrao = r'\w+:\sreservas\s(E101|E102|E103|E104|E105)\s(SEG|TER|QUA|QUI|SEX)\s(1[0-8]|[89])$'
    if re.match(padrao, string):
        return True
    else:
        return False
    
def verificar_disponibilidade(sala, dia, hora, reservas = reservas):
    return reservas[sala][dia][int(hora)] is None


print(verificar_disponibilidade("E101", "SEG", 12))
