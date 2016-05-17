import ply.lex as lex
from ply.lex import TOKEN


states = (
    ('function', 'exclusive'),
    ('mode', 'exclusive'),
)

tokens = (
    'FUNCTION_NAME',
    'CHARACTER',
    'SPACE',
    'LENGTH_PT',
    'BEGIN_MODE',
    'END_BEGIN_MODE',
    'END_MODE',
    'NEW_COMPONENT',
)


t_CHARACTER = r'.'
t_SPACE = r'[ ]{1}'

QUANTITY_PT = r'-?\d+pt'
# MODE = r'\<.+(' + QUANTITY_PT + r')*\>'
NAME_START = r'[_a-zA-Z]'
NAME_BODY = r'\w*'
NAME = NAME_START + NAME_BODY


def t_NEW_COMPONENT(t):
    r'\n\n'
    return t


def t_END_MODE(t):
    r'\<\/.+\>'
    t.value = t.value[2:-1]
    return t


@TOKEN(r'\<' + NAME + r'[ ]{1}')
def t_BEGIN_MODE(t):
    t.lexer.begin('mode')
    t.value = t.value[1:-1]
    return t


def t_mode_END_BEGIN_MODE(t):
    r'\>'
    t.lexer.begin('INITIAL')
    return t


def t_begin_function(t):
    r'\\.+\{'
    t.lexer.begin('function')
    t.type = 'FUNCTION_NAME'
    t.value = t.value[1:-1]
    return t


@TOKEN(QUANTITY_PT)
def t_function_mode_LENGTH_PT(t):
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
