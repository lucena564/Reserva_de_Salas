reservas = {sala: {dia: {hora: None for hora in range(8, 18)} for dia in ['Seg', 'Ter', 'Qua', 'Qui', 'Sex']} for sala in ['E101', 'E102', 'E103', 'E104', 'E105']}
# print(reservas)

import re

def verifica_formato(string):
    padrao = r'\w+:\sreservas\s(E101|E102|E103|E104|E105)\s(SEG|TER|QUA|QUI|SEX)\s(1[0-8]|[89])$'
    if re.match(padrao, string):
        return True
    else:
        return False

# Exemplo de uso:
string_exemplo = "Antonio: reservas E101 SEX 11"
if verifica_formato(string_exemplo):
    print("Formato correto!")
else:
    print("Formato incorreto!")
