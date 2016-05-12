import sys

import ply.yacc as yacc

from tex_lexer import tokens
import tex

from PyDvi.Font.TfmParser import TfmParser
font = TfmParser.parse('cmr10', '/Users/ejm/projects/pytex/pytex/cmr10.tfm')


class Character(object):

    def __init__(self, character):
        self.character = character


class Space(object):

    def __init__(self, space):
        self.space = space


class String(object):

    def __init__(self, movers=None):
        if movers is None:
            movers = []
        self.movers = movers

    def add_mover(self, mover):
        self.movers.append(mover)

    def add_string(self, string):
        self.movers.extend(string.movers)


class Paragraph(object):

    def __init__(self, string):
        self.string = string

    def add_string(self, string):
        self.string.add_string(string)


class Page(object):

    def __init__(self):
        self.paragraphs = []

    def add_paragraph(self, paragraph):
        self.paragraphs.append(paragraph)

    def to_tex_page(self):
        tex_page = tex.TexPage(font=font)
        for paragraph in self.paragraphs:
            tex_page.start_new_paragraph()
            for mover in paragraph.string.movers:
                if isinstance(mover, Space):
                    tex_page.add_space()
                elif isinstance(mover, Character):
                    tex_page.add_character(mover.character)
        return tex_page


def p_page_append(p):
    '''page : page NEW_PARAGRAPH paragraph
    '''
    p[1].add_paragraph(p[3])
    p[0] = p[1]


def p_page(p):
    '''page : paragraph
    '''
    page = Page()
    page.add_paragraph(p[1])
    p[0] = page


def p_paragraph_1(p):
    '''paragraph : paragraph string
    '''
    p[1].add_string(p[1])
    p[0] = p[1]


def p_paragraph(p):
    '''paragraph : string
    '''
    p[0] = Paragraph(p[1])


def p_tex_string(p):
    '''string : string string'''
    p[1].add_string(p[2])
    p[0] = p[1]


def p_tex_string_1(p):
    '''string : mover'''
    string = String([p[1]])
    p[0] = string


def p_mover(p):
    '''mover : tex_character
             | tex_space'''
    p[0] = p[1]


def p_tex_character_character(p):
    '''tex_character : CHARACTER'''
    p[0] = Character(p[1])


def p_tex_space_space(p):
    'tex_space : SPACE'
    p[0] = Space(p[1])


# Error rule for syntax errors
def p_error(p):
    print("Syntax error in input!")

# Build the parser
parser = yacc.yacc(debug=True)
