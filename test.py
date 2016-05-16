from __future__ import (print_function, division, absolute_import,
                        unicode_literals)

import dvi
import printing
import layout
import layla_parser
import layla_lexer


def test_dvi():
    dvi_document = dvi.DVIDocument()
    dvi_document.write_preamble()
    dvi_document.begin_page()
    dvi_document.push()
    dvi_document.down(15859712)
    dvi_document.pop()
    dvi_document.down(42152922)
    dvi_document.push()
    dvi_document.down(4253469734)
    dvi_document.push()
    dvi_document.right(1310720)
    dvi_document.define_font(font_number=0, font_check_sum=0x4bf16079,
                             scale_factor=0x000a0000, design_size=0x000a0000,
                             file_path=b'cmr10')
    dvi_document.set_font(font_number=0)
    dvi_document.set_character('a')
    dvi_document.set_character('b')
    dvi_document.pop()
    dvi_document.pop()
    dvi_document.down(0x180000)
    dvi_document.push()
    dvi_document.right(0x00e860a3)
    dvi_document.set_character('1')
    dvi_document.pop()
    dvi_document.end_page()
    dvi_document.write_postamble()
    dvi_document.to_file('test.dvi')


def test_box():
    c_1 = box.CharacterNode(b'a', font_number=0)
    c_2 = box.CharacterNode(b'b', font_number=0)
    c_4 = box.CharacterNode(b'c', font_number=0)
    w_s = box.WhiteSpaceNode(220000)
    h_list_1 = box.HList([c_1, c_2])
    h_list_2 = box.HList([c_1, c_2, w_s, c_4])
    v_list_1 = box.VList([h_list_1, h_list_2])
    v_list_2 = box.VList([h_list_1, h_list_2])
    v_list_all = box.VList([v_list_1, v_list_2])
    dvi_document = dvi.DVIDocument()
    dvi_document.write_preamble()
    dvi_document.begin_page()
    dvi_document.define_font(font_number=0, font_check_sum=0x4bf16079,
                             scale_factor=0x000a0000, design_size=0x000a0000,
                             file_path=b'cmr10')
    v_list_all.write_to_file(dvi_document)
    dvi_document.end_page()
    dvi_document.write_postamble()
    dvi_document.to_file('box_test.dvi')


def test_tex():
    tex_page = tex.TexPage()
    tex_page.start_paragraph()
    tex_page.add_character('T')
    tex_page.add_character('h')
    tex_page.add_character('e')
    tex_page.add_space()
    tex_page.add_character('s')
    tex_page.add_character('t')
    tex_page.add_character('a')
    tex_page.add_character('r')
    tex_page.add_character('t')
    tex_page.add_character('.')

    tex_page.start_paragraph()
    tex_page.add_character('T')
    tex_page.add_character('h')
    tex_page.add_character('e')
    tex_page.add_space()
    tex_page.add_character('e')
    tex_page.add_character('n')
    tex_page.add_character('d')
    tex_page.add_character('.')

    dvi_document = tex_page.to_dvi_document()
    dvi_document.to_file('tex_test.dvi')


def test_parser():
    data = 'ab \n\nima'
    r = layla_parser.parser.parse(data)
    tex_page = r.to_print_document()
    dvi_file = tex_page.to_dvi_document()
    dvi_file.to_file('parser_test.dvi')


def test_lexer_from_file():
    layla_text = open('parser_test_file.tex', 'r').read()[:-1]
    layla_lexer.lexer.input(layla_text)
    tokens = []
    while True:
        token = layla_lexer.lexer.token()
        if token is None:
            break
        if token.type in ['CHARACTER', 'SPACE']:
            continue
        tokens.append(token)
    import pdb; pdb.set_trace()


def test_parser_from_file():
    layla_text = open('parser_test_file.tex', 'r').read()[:-1]
    layout_document = layla_parser.layla_to_layout(layla_text)
    print_document = layout_document.to_print_document()
    dvi_document = printing.print_to_dvi(print_document)
    dvi_document.to_file('parser_test_from_file.dvi')


if __name__ == '__main__':
    # test_lexer_from_file()
    test_parser_from_file()
