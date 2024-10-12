import os
import re

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

def remover_comentarios(codigo):
    """
    Remove comentários de linha única e múltiplas linhas do código-fonte.
    """
    codigo_sem_comentarios = re.sub(r"/\*.*?\*/", "", codigo, flags=re.DOTALL)
    codigo_sem_comentarios = re.sub(r"//.*", "", codigo_sem_comentarios)
    return codigo_sem_comentarios

def verificar_fim_linha(linha, numero_linha):
    """
    Verifica se uma linha de código termina com ';' e emite um aviso se não terminar.
    """
    linha_sem_espacos = linha.rstrip()  # Remove espaços em branco no final da linha
    if linha_sem_espacos and not (linha_sem_espacos.endswith(';') or linha_sem_espacos.endswith('{') or linha_sem_espacos.endswith('}')):
        # Ignorar blocos de controle (como if, else, while, etc.) que não precisam de ';'
        if not any(linha_sem_espacos.startswith(palavra) for palavra in ['if', 'else', 'while', 'for', 'switch', 'do']):
            print(f"Aviso: A linha {numero_linha} pode estar faltando um ponto e virgula.")
            return f"Aviso: A linha {numero_linha} pode estar faltando um ponto e virgula.\n"
    return ""

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
                    erros.append(f"Erro: Delimitador de fechamento '{char}' na linha {numero_linha} não tem um correspondente de abertura.")
                else:
                    delimitador_abertura, linha_abertura = pilha.pop()
                    if pares_delimitadores[delimitador_abertura] != char:
                        # Se o delimitador não corresponde ao esperado, é um erro
                        erros.append(f"Erro: Delimitador '{delimitador_abertura}' aberto na linha {linha_abertura} não corresponde ao fechamento '{char}' na linha {numero_linha}.")

    # Se ainda houver delimitadores de abertura na pilha, significa que eles não foram fechados
    while pilha:
        delimitador_abertura, linha_abertura = pilha.pop()
        erros.append(f"Erro: Delimitador de abertura '{delimitador_abertura}' na linha {linha_abertura} não foi fechado.")

    return erros

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
    linhas = codigo.split('\n')

    with open(arquivo_saida, 'w') as saida:
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
            
            print("-"*60)
            # Verificar se a linha termina com ";"
            aviso = verificar_fim_linha(linha, numero_linha)
            if aviso:
                saida.write(aviso)

        # Verificar a ausência de delimitadores balanceados
        erros_delimitadores = verificar_delimitadores(linhas)
        for erro in erros_delimitadores:
            saida.write(erro + "\n")
            print(erro)

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