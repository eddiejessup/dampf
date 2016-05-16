import ply.yacc as yacc

from layla_lexer import tokens
import layout


function_name_map = {
    'vskip': layout.VSkip,
    'hskip': layout.HSkip,
}


mode_name_map = {
    'raggedRight': layout.RaggedRightMode,
    'center': layout.CenterMode,
}


def p_document_append_node(p):
    '''document : document NEW_COMPONENT node
    '''
    p[1].append(p[3])
    p[0] = p[1]


def p_document_node(p):
    '''document : node
    '''
    document = layout.LayoutDocument()
    document.append(p[1])
    p[0] = document


def p_moded_node(p):
    '''started_mode_node : BEGIN_MODE NEW_COMPONENT node'''
    ModeFactory = mode_name_map[p[1]]
    mode = ModeFactory()
    p[0] = layout.ModedNode(mode=mode)
    p[0].append(p[3])


def p_moded_node_append(p):
    '''started_mode_node : started_mode_node NEW_COMPONENT node'''
    p[1].append(p[3])
    p[0] = p[1]


def p_node_moded_node(p):
    '''node : started_mode_node NEW_COMPONENT END_MODE'''
    p[0] = p[1]

# def p_moded_node(p):
#     '''moded_node : node END_MODE'''
#     p[0] = (p[1], p[2])
# def p_node_moded_node(p):
#     '''node : BEGIN_MODE moded_node'''
#     begin_mode, node, end_mode = p[1], p[2][0], p[2][1]
#     if not begin_mode == end_mode:
#         import pdb; pdb.set_trace()
#         raise Exception
#     ModeFactory = mode_name_map[begin_mode]
#     mode = ModeFactory()
#     p[0] = layout.ModedNode(mode=mode)
#     p[0].append(node)


# def p_moded_node(p):
#     '''moded_node : node END_MODE'''
#     p[0] = (p[1], p[2])


def p_node_function(p):
    '''node : function'''
    p[0] = p[1]


def p_node_paragraph(p):
    '''node : paragraph'''
    p[0] = p[1]


def p_paragraph_mover_append(p):
    '''paragraph : paragraph mover'''
    p[1].append(p[2])
    p[0] = p[1]


def p_paragraph_mover(p):
    '''paragraph : mover'''
    paragraph = layout.Paragraph()
    paragraph.append(p[1])
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
    p[0] = FunctionFactory(func_args=p[2])


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
