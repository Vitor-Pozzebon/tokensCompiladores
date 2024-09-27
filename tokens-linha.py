import os
import re
os.system("cls")

# -----------------------------------------------
# FUNÇÕES E DECLARAÇÕES
# -----------------------------------------------

# Tokens de palavras-chave, operadores e delimitadores da linguagem C
palavras_chave = [
    "auto", "break", "case", "char", "const", "continue", "default", "do", "double", "else",
    "enum", "extern", "float", "for", "goto", "if", "inline", "int", "long", "register", "restrict",
    "return", "short", "signed", "sizeof", "static", "struct", "switch", "typedef", "union", "unsigned", 
    "void", "volatile", "while"
]
operadores = ['+', '-', '*', '/', '=', '==', '!=', '<', '>', '>=', '<=', '&&', '||', '!', '&', '|', '^', '~', '<<', '>>', "%"]
delimitadores = ['(', ')', '{', '}', '[', ']', ';', ',', '"', "'"]

# Associando um valor para cada token
codigo_tokens = {
    "PALAVRACHAVE": 1,
    "IDENTIFICADOR": 2,
    "OPERADOR": 3,
    "DELIMITADOR": 4,
    "NUMERO": 5,
    "STRING": 6,
    "CHAR": 7
}

# Função para identificar o tipo de token
def identificar_token(token):
    if token in palavras_chave:
        return "PALAVRACHAVE", codigo_tokens["PALAVRACHAVE"]
    elif token in operadores:
        return "OPERADOR", codigo_tokens["OPERADOR"]
    elif token in delimitadores:
        return "DELIMITADOR", codigo_tokens["DELIMITADOR"]
    elif re.match(r"^[0-9]+$", token):  # números
        return "NUMERO", codigo_tokens["NUMERO"]
    elif re.match(r"^\".*\"$", token):  # strings
        return "STRING", codigo_tokens["STRING"]
    elif re.match(r"^'.*'$", token):  # caracteres
        return "CHAR", codigo_tokens["CHAR"]
    else:
        return "IDENTIFICADOR", codigo_tokens["IDENTIFICADOR"]
    
# Função para ler o arquivo C, gerar os tokens e escrever a saída
def analisar_codigo_c(arquivo_entrada, arquivo_saida):
    with open(arquivo_entrada, 'r') as entrada, open(arquivo_saida, 'w') as saida:
        #lendo e separando cada linha do arquivo em C
        linhas = entrada.readlines()
        
        # Usando a biblioteca regex para separar tokens
        # as linhas serão enumeradas e separadas para que sejam identificadas
        for numero_linha, linha in enumerate(linhas, start=1):
            tokens = re.findall(r"\"[^\"]*\"|\w+|==|!=|<=|%|>=|&&|\|\||[+\-*/=<>;,\(\)\{\}\[\]\"']", linha)

            # Processando e identificando cada token
            for token in tokens:
                tipo_token, codigo_token = identificar_token(token)

                # Para cada token, escrever qual linha o mesmo está, bem como seus dados respectivos
                saida.write(f"LINHA: {numero_linha}, TOKEN: {token}, TIPO: {tipo_token}, CODIGO: {codigo_token}\n")
                print(f"LINHA: {numero_linha}, TOKEN: {token}, TIPO: {tipo_token}, CODIGO: {codigo_token}")

# -----------------------------------------------
# INÍCIO DO PROGRAMA (MAIN)
# -----------------------------------------------

# Caminho do arquivo de código C de entrada e o arquivo de saída
arquivo_entrada = 'codigo-c.c'  # Arquivo de código em C
arquivo_saida = 'tokens_saida2.txt'  # Arquivo onde serão salvos os tokens

# Chamada da função para analisar o código em C
analisar_codigo_c(arquivo_entrada, arquivo_saida)