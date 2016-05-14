import ply.lex as lex


tokens = (
    'CHARACTER',
    'SPACE',
    'NEW_PARAGRAPH'
)

t_CHARACTER = r'.'
t_SPACE = r'[ ]{1}'
t_NEW_PARAGRAPH = r'\n\n'


def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)


lexer = lex.lex()
