import ply.lex as lex


reserved = {
    # Estrutura do Programa
    'PROGRAM': 'PROGRAM',
    'END': 'END',
    
    # Tipos de Dados
    'INTEGER': 'INTEGER',
    'REAL': 'REAL',
    'LOGICAL': 'LOGICAL',
    'CHARACTER': 'CHARACTER',
    
    # Controlo de Fluxo
    'IF': 'IF',
    'THEN': 'THEN',
    'ELSE': 'ELSE',
    'ENDIF': 'ENDIF',
    'DO': 'DO',
    'GOTO': 'GOTO',
    'CONTINUE': 'CONTINUE',
    
    # Input / Output
    'READ': 'READ',
    'PRINT': 'PRINT',
    
    # Subprogramas 
    'FUNCTION': 'FUNCTION',
    'SUBROUTINE': 'SUBROUTINE',
    'CALL': 'CALL',
    'RETURN': 'RETURN',
    
    # Valores Lógicos Fortran
    '.TRUE.': 'TRUE',
    '.FALSE.': 'FALSE',
    
    # Operadores Relacionais e Lógicos Fortran
    '.EQ.': 'EQ',    # Equal
    '.NE.': 'NE',    # Not Equal
    '.LT.': 'LT',    # Less Than
    '.LE.': 'LE',    # Less or Equal
    '.GT.': 'GT',    # Greater Than
    '.GE.': 'GE',    # Greater or Equal
    '.AND.': 'AND',
    '.OR.': 'OR',
    '.NOT.': 'NOT'
}

# 2. Lista de Tokens
tokens = [
    'ID',           # Identificadores
    'INT_CONST',    # Constantes inteiras
    'REAL_CONST',   # Constantes reais (floats)
    'STRING',       # Strings literais
    'PLUS',         # +
    'MINUS',        # -
    'TIMES',        # *
    'DIVIDE',       # /
    'EQUALS',       # =
    'LPAREN',       # (
    'RPAREN',       # )
    'COMMA',        # ,
] + list(dict.fromkeys(reserved.values()))

t_PLUS    = r'\+'
t_MINUS   = r'-'
t_TIMES   = r'\*'
t_DIVIDE  = r'/'
t_EQUALS  = r'='
t_LPAREN  = r'\('
t_RPAREN  = r'\)'
t_COMMA   = r','

t_ignore  = ' \t'


# Ignorar comentários
def t_COMMENT(t):
    r'!.*'
    pass 

# Strings
def t_STRING(t):
    r'\'[^\']*\'|\"[^\"]*\"'
    t.value = t.value[1:-1] 
    return t

# Números Reais 
def t_REAL_CONST(t):
    r'\d+\.\d+'
    t.value = float(t.value)
    return t

# Números Inteiros 
def t_INT_CONST(t):
    r'\d+'
    t.value = int(t.value)
    return t

# Identificadores, Palavras Reservadas e Operadores Fortran (.EQ., .AND.)
def t_ID(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*|\.[a-zA-Z]+\.'
    upper_val = t.value.upper()
    t.type = reserved.get(upper_val, 'ID') 
    return t

# Contagem de linhas
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# Tratamento de erros léxicos
def t_error(t):
    print(f"Erro Léxico: Caráter ilegal '{t.value[0]}' na linha {t.lexer.lineno}")
    t.lexer.skip(1)

lexer = lex.lex()

