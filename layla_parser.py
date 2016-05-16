import ply.yacc as yacc

from layla_lexer import tokens
import layout


function_name_map = {
    'vskip': layout.VSkip,
    'hskip': layout.HSkip,
}


mode_name_map = {
    'raggedRight': layout.RaggedRightMode
}


def p_document_append_component(p):
    '''document : document component
    '''
    p[1].components.append(p[2])
    p[0] = p[1]


def p_document_component(p):
    '''document : component
    '''
    document = layout.LayoutDocument()
    document.components.append(p[1])
    p[0] = document


def p_wrapped_component(p):
    '''component : BEGIN_MODE ended_component'''
    begin_mode, component, end_mode = p[1], p[2][0], p[2][1]
    if not begin_mode == end_mode:
        import pdb; pdb.set_trace()
        raise Exception
    p[0] = layout.ModedComponent(component=component, mode=begin_mode)


def p_component_with_end(p):
    '''ended_component : component END_MODE'''
    p[0] = (p[1], p[2])


def p_component_function(p):
    '''component : function'''
    p[0] = p[1]


def p_component_paragraph(p):
    '''component : paragraph'''
    p[0] = p[1]


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
             | layout_space
             | function
    '''
    p[0] = p[1]


def p_layout_character_character(p):
    '''layout_character : CHARACTER'''
    p[0] = layout.Character(p[1])


def p_layout_space_space(p):
    '''layout_space : SPACE'''
    p[0] = layout.Space()


def p_function_constituents(p):
    '''function : FUNCTION_NAME argument_list'''
    FunctionFactory = function_name_map[p[1]]
    p[0] = FunctionFactory(*p[2])


def p_argument_list_append(p):
    '''argument_list : argument_list argument'''
    p[0] = p[1] + [p[2]]


def p_argument_list(p):
    '''argument_list : argument'''
    p[0] = [p[1]]


def p_argument_length(p):
    '''argument : LENGTH_PT'''
    p[0] = layout.LengthPoint(p[1])


# Error rule for syntax errors
def p_error(p):
    print("Syntax error in input!")

# Build the parser
parser = yacc.yacc(debug=True)


def layla_to_layout(text):
    return parser.parse(text)
