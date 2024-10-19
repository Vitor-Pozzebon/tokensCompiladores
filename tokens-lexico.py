import os
import re
from collections import defaultdict

# Limpar a tela (funciona no Windows; para outros sistemas, ajuste conforme necessário)
os.system("cls" if os.name == "nt" else "clear")

# -----------------------------------------------
# DECLARAÇÕES E CONFIGURAÇÕES INICIAIS
# -----------------------------------------------

PALAVRAS_CHAVE = [
    "auto", "break", "case", "char", "const", "continue", "default", "do", "double", "else",
    "enum", "extern", "float", "for", "goto", "if", "inline", "int", "long", "register", "restrict",
    "return", "short", "signed", "sizeof", "static", "struct", "switch", "typedef", "union", "unsigned", 
    "void", "volatile", "while", "return", "main", "printf", "scanf", "include", "define", "else",
    "NULL", "true", "false", "bool", "string", "class", "delete"
]

OPERADORES = [
    '==', '!=', '<=', '>=', '&&', '||', '++', '--', '+=', '-=', '*=', '/=', '%=', '<<', '>>', 
    '+', '-', '*', '/', '=', '<', '>', '!', '&', '|', '^', '~', '%'
]

DELIMITADORES = ['(', ')', '{', '}', '[', ']', ';', ',', '.', ':', '?']

CÓDIGO_TOKENS = {
    "PALAVRACHAVE": 1,
    "IDENTIFICADOR": 2,
    "OPERADOR": 3,
    "DELIMITADOR": 4,
    "NUMERO": 5,
    "STRING": 6,
    "CHAR": 7
}

REGEX_PATTERNS = {
    "NUMERO": r"^\d+(\.\d+)?([eE][-+]?\d+)?$",  
    "STRING": r"^\"(\\.|[^\"\\])*\"$",         
    "CHAR": r"^\'(\\.|[^\'\\])\'$"            
}

# -----------------------------------------------
# FUNÇÃO PARA IDENTIFICAR OS TOKENS DO CÓDIGO EM C
# -----------------------------------------------

def identificar_token(token):
    """
    Identifica o tipo de um token específico.
    """
    if token in PALAVRAS_CHAVE:
        return "PALAVRACHAVE", CÓDIGO_TOKENS["PALAVRACHAVE"]
    elif token in OPERADORES:
        return "OPERADOR", CÓDIGO_TOKENS["OPERADOR"]
    elif token in DELIMITADORES:
        return "DELIMITADOR", CÓDIGO_TOKENS["DELIMITADOR"]
    elif re.match(REGEX_PATTERNS["NUMERO"], token):
        return "NUMERO", CÓDIGO_TOKENS["NUMERO"]
    elif re.match(REGEX_PATTERNS["STRING"], token):
        return "STRING", CÓDIGO_TOKENS["STRING"]
    elif re.match(REGEX_PATTERNS["CHAR"], token):
        return "CHAR", CÓDIGO_TOKENS["CHAR"]
    else:
        if re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", token):
            return "IDENTIFICADOR", CÓDIGO_TOKENS["IDENTIFICADOR"]
        else:
            return "INVALIDO", None 

# -----------------------------------------------
# FUNÇÕES PARA VERIFICAR IDENTIFICADORES REPETIDOS
# -----------------------------------------------

def identificar_token_repetido(token):
    """
    Identifica o tipo de um token específico.
    """
    if token in PALAVRAS_CHAVE:
        return "PALAVRACHAVE"
    elif re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", token):  # Identificadores válidos (variáveis, funções, etc.)
        return "IDENTIFICADOR"
    else:
        return "OUTRO"

def verificar_identificadores_repetidos(linhas):
    """
    Verifica se há identificadores repetidos no código fornecido.
    """
    identificadores = defaultdict(int)  # Dicionário para contar ocorrências de cada identificador
    repetidos = {}  # Dicionário para armazenar identificadores repetidos
    mensagens = []  # Lista para armazenar mensagens

    for numero_linha, linha in enumerate(linhas, start=1):
        tokens = re.findall(r"[A-Za-z_][A-Za-z0-9_]*", linha)  # Identificadores válidos

        for token in tokens:
            if identificar_token_repetido(token) == "IDENTIFICADOR":
                identificadores[token] += 1
                if identificadores[token] > 1:
                    repetidos[token] = numero_linha  # Armazenar a linha onde foi encontrado o repetido

    # Mostrar identificadores repetidos, se houver
    if repetidos:
        for identificador, linha in repetidos.items():
            print(f"Identificador '{identificador}' repetido. Ultima ocorrencia na linha {linha}.")
            mensagens.append(f"Identificador '{identificador}' repetido. Ultima ocorrencia na linha {linha}.")
    else:
        print("Nenhum identificador repetido encontrado.")
        mensagens.append("Nenhum identificador repetido encontrado.")
    return mensagens

# -----------------------------------------------
# FUNÇÃO PARA REMOVER LINHAS VAZIAS DO CÓDIGO
# -----------------------------------------------

def remove_empty_lines(text):
    # Usa splitlines para dividir a string em linhas, e filtra as que não estão vazias
    lines = text.splitlines()
    non_empty_lines = [line for line in lines if line.strip()]
    # Junta as linhas não vazias de volta em uma única string
    return "\n".join(non_empty_lines) 

# -----------------------------------------------
# FUNÇÃO PARA REMOVER OS COMENTÁRIOS DO CÓDIGO
# -----------------------------------------------

def remover_comentarios(codigo):
    """
    Remove comentários de linha única e múltiplas linhas do código-fonte.
    """
    codigo_sem_comentarios = re.sub(r"/\*.*?\*/", "", codigo, flags=re.DOTALL)
    codigo_sem_comentarios = re.sub(r"//.*", "", codigo_sem_comentarios)
    codigo_sem_comentarios = remove_empty_lines(codigo_sem_comentarios)
    return codigo_sem_comentarios

# -----------------------------------------------
# FUNÇÃO PARA VERIFICAR O ";" NO FINAL DA LINHA
# -----------------------------------------------

def verificar_fim_linha(linha, numero_linha):
    """
    Verifica se uma linha de código termina com ';' e emite um aviso se não terminar.
    """
    linha_sem_espacos = linha.rstrip()  # Remove espaços em branco no final da linha
    if linha_sem_espacos and not (linha_sem_espacos.endswith(';') or linha_sem_espacos.endswith('{') or linha_sem_espacos.endswith('}')):
        # Ignorar blocos de controle (como if, else, while, etc.) que não precisam de ';'
        if not any(linha_sem_espacos.startswith(palavra) for palavra in ['if', 'else', 'while', 'for', 'switch', 'do']):
            print("\n" + "*"*60 + "\n")  
            print(f"Aviso: A linha {numero_linha} pode estar faltando um ponto e virgula.")
            print("\n" + "*"*60 + "\n")
            print("-"*60 + "\n") 
            return f"Aviso: A linha {numero_linha} pode estar faltando um ponto e virgula.\n"
    return ""

# -----------------------------------------------
# FUNÇÃO PARA VERIFICAR ABERTURA E FECHAMENTO DOS DELIMITADORES
# -----------------------------------------------

def verificar_delimitadores(linhas):
    """
    Verifica se todos os delimitadores ('()', '[]', '{}') estão presentes e balanceados.
    """
    pilha = []  # Pilha para armazenar os delimitadores de abertura
    pares_delimitadores = {
        '(': ')',
        '[': ']',
        '{': '}'
    }
    delimitadores_abertura = pares_delimitadores.keys()
    delimitadores_fechamento = pares_delimitadores.values()

    erros = []  # Lista para armazenar mensagens de erro

    for numero_linha, linha in enumerate(linhas, start=1):
        for char in linha:
            if char in delimitadores_abertura:
                pilha.append((char, numero_linha))  # Adiciona o delimitador de abertura e sua linha correspondente à pilha
            elif char in delimitadores_fechamento:
                if not pilha:
                    # Se a pilha está vazia, mas encontramos um delimitador de fechamento, temos um erro
                    erros.append(f"Erro: Delimitador de fechamento '{char}' na linha {numero_linha} nao tem um correspondente de abertura.")
                else:
                    delimitador_abertura, linha_abertura = pilha.pop()
                    if pares_delimitadores[delimitador_abertura] != char:
                        # Se o delimitador não corresponde ao esperado, é um erro
                        erros.append(f"Erro: Delimitador '{delimitador_abertura}' aberto na linha {linha_abertura} nao corresponde ao fechamento '{char}' na linha {numero_linha}.")

    # Se ainda houver delimitadores de abertura na pilha, significa que eles não foram fechados
    while pilha:
        delimitador_abertura, linha_abertura = pilha.pop()
        erros.append(f"Erro: Delimitador de abertura '{delimitador_abertura}' na linha {linha_abertura} nao foi fechado.")

    return erros

# -----------------------------------------------
# FUNÇÃO GERAL PARA ANALISAR O CÓDIGO FORNECIDO
# -----------------------------------------------

def analisar_codigo_c(arquivo_entrada, arquivo_saida):
    """
    Analisa o código C fornecido, identifica os tokens e verifica se cada linha termina com ';'.
    """
    try:
        with open(arquivo_entrada, 'r') as entrada:
            codigo = entrada.read()
    except FileNotFoundError:
        print(f"Erro: Arquivo '{arquivo_entrada}' nao encontrado.")
        return

    codigo = remover_comentarios(codigo)
    print("Codigo Analisado:\n")
    print(codigo)
    print("*"*60)
    linhas = codigo.split('\n')

    with open(arquivo_saida, 'w') as saida:
        # Impressão do código analisado no arquivo de saída
        saida.write("Codigo analisado:\n")
        saida.write(codigo)
        saida.write("\n" + "*"*60 + "\n")
        for numero_linha, linha in enumerate(linhas, start=1):
            if not linha.strip():
                continue

            padrao = r"""
                ("(?:\\.|[^"\\])*") |         
                ('(?:\\.|[^'\\])') |          
                (==|!=|<=|>=|&&|\|\||\+\+|--|\+=|-=|\*=|/=|%=|<<|>>) |  
                ([A-Za-z_][A-Za-z0-9_]*) |    
                (\d+\.\d+([eE][-+]?\d+)?) |   
                (\d+) |                        
                ([+\-*/%=<>&|^~!;:,?.()\[\]{}])   
            """
            
            tokens = re.finditer(padrao, linha, re.VERBOSE)

            for match in tokens:
                token = match.group().strip()
                tipo_token, codigo_token = identificar_token(token)

                if tipo_token == "INVALIDO":
                    print(f"Erro: Token invalido '{token}' na linha {numero_linha}")
                    saida.write(f"LINHA: {numero_linha}, TOKEN INVALIDO: {token}\n")
                else:
                    saida.write(f"LINHA: {numero_linha}, TOKEN: '{token}', TIPO: {tipo_token}, CODIGO: {codigo_token}\n")
                    print(f"LINHA: {numero_linha}, TOKEN: '{token}', TIPO: {tipo_token}, CODIGO: {codigo_token}")
            
            saida.write("-"*60 + "\n")
            print("-"*60)
            # Verificar se a linha termina com ";"
            aviso = verificar_fim_linha(linha, numero_linha)
            if aviso:
                saida.write("\n" + "*"*60 + "\n")    
                saida.write(aviso)
                saida.write("*"*60 + "\n")  
                saida.write("\n" + "-"*60 + "\n")

        # Verificar a ausência de delimitadores balanceados
        erros_delimitadores = verificar_delimitadores(linhas)
        for erro in erros_delimitadores:
            saida.write("\n" + "*"*60 + "\n")
            saida.write(erro + "\n")
            saida.write("*"*60 + "\n")
            print("\n" + "*"*60 + "\n")
            print(erro)
            print("\n" + "*"*60 + "\n")

        # Verificar identificadores repetidos
        mensagens_repetidos = verificar_identificadores_repetidos(linhas)
        for mensagem in mensagens_repetidos:
            saida.write("\n" + "*"*60 + "\n")
            saida.write(mensagem + "\n")
            saida.write("*"*60 + "\n")
            print("\n" + "*"*60 + "\n")
            print(mensagem)
            print("\n" + "*"*60 + "\n")

# -----------------------------------------------
# FUNÇÃO PRINCIPAL
# -----------------------------------------------

def main():
    arquivo_entrada = 'codigo-c.c'     
    arquivo_saida = 'tokens_saida3.txt' 

    analisar_codigo_c(arquivo_entrada, arquivo_saida)
    print(f"\nAnálise concluída. Tokens e avisos salvos em '{arquivo_saida}'.")

if __name__ == "__main__":
    main()