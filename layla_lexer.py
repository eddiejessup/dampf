import ply.lex as lex


states = (
    ('function', 'exclusive'),
)

tokens = (
    'FUNCTION_NAME',
    'CHARACTER',
    'SPACE',
    'LENGTH_PT',
    'BEGIN_MODE',
    'END_MODE',
    'NEW_COMPONENT',
)

BEGIN_FUNCTION_ARGS = r'\{'
END_FUNCTION_ARGS = r'\}'
FUNCTION_ARGS = r'.*'
FUNCTION_NAME = r'\\.+'


t_CHARACTER = r'.'
t_SPACE = r'[ ]{1}'


def t_NEW_COMPONENT(t):
    r'\n\n'
    return t


def t_END_MODE(t):
    r'\<\/.+\>'
    t.value = t.value[2:-1]
    return t


def t_BEGIN_MODE(t):
    r'\<.+\>'
    t.value = t.value[1:-1]
    return t


def t_begin_function(t):
    r'\\.+\{'
    t.lexer.begin('function')
    t.type = 'FUNCTION_NAME'
    t.value = t.value[1:-1]
    return t


def t_function_LENGTH_PT(t):
    r'-?[0-9]+pt'
    t.value = float(t.value[:-2])
    return t


def t_function_argument_delimiter(t):
    r','


def t_function_end_function(t):
    r'\}'
    t.lexer.begin('INITIAL')


def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)


def t_function_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)


lexer = lex.lex()
