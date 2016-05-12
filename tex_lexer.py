import box
import ply.lex as lex


tokens = (
    'CHARACTER',
    'SPACE',
    'NEW_PARAGRAPH'
)

t_CHARACTER = r'.'
t_SPACE = r'[ ]+'
t_NEW_PARAGRAPH = r'\n\n'


def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)


lexer = lex.lex()
# data = 'abc\n\nhihi my mate'
# lexer.input(data)

# while True:
#     tok = lexer.token()
#     if not tok:
#         break
#     print(tok.type, tok.value, tok.lineno, tok.lexpos)
# class TexLexer(object):

#     def __init__(self, file):
#         self.file = file

#     def get_next_token(self):
