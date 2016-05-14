import ply.yacc as yacc

from layla_lexer import tokens
import layout


def p_document_append_paragraph(p):
    '''document : document NEW_PARAGRAPH paragraph
    '''
    p[1].paragraphs.append(p[3])
    p[0] = p[1]


def p_document_paragraph(p):
    '''document : paragraph
    '''
    document = layout.LayoutDocument()
    document.paragraphs.append(p[1])
    p[0] = document


def p_paragraph_mover_append(p):
    '''paragraph : paragraph mover'''
    p[1].add_mover(p[2])
    p[0] = p[1]


def p_paragraph_mover(p):
    '''paragraph : mover'''
    paragraph = layout.Paragraph()
    paragraph.add_mover(p[1])
    p[0] = paragraph


def p_mover(p):
    '''mover : layout_character
             | layout_space'''
    p[0] = p[1]


def p_layout_character_character(p):
    '''layout_character : CHARACTER'''
    p[0] = layout.Character(p[1])


def p_layout_space_space(p):
    'layout_space : SPACE'
    p[0] = layout.Space()


# Error rule for syntax errors
def p_error(p):
    print("Syntax error in input!")

# Build the parser
parser = yacc.yacc(debug=True)


def layla_to_layout(text):
    return parser.parse(text)
