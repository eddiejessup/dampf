from __future__ import (print_function, division, absolute_import,
                        unicode_literals)

import dvi
import box


def test_dvi():
    dvi_file = dvi.DVIFile()
    dvi_file.write_preamble()
    dvi_file.begin_page()
    dvi_file.push()
    dvi_file.down(15859712)
    dvi_file.pop()
    dvi_file.down(42152922)
    dvi_file.push()
    dvi_file.down(4253469734)
    dvi_file.push()
    dvi_file.right(1310720)
    dvi_file.define_font(font_number=0, font_check_sum=0x4bf16079,
                         scale_factor=0x000a0000, design_size=0x000a0000,
                         file_path=b'cmr10')
    dvi_file.set_font(font_number=0)
    dvi_file.set_character('a')
    dvi_file.set_character('b')
    dvi_file.pop()
    dvi_file.pop()
    dvi_file.down(0x180000)
    dvi_file.push()
    dvi_file.right(0x00e860a3)
    dvi_file.set_character('1')
    dvi_file.pop()
    dvi_file.end_page()
    dvi_file.write_postamble()
    dvi_file.output_to_file('test.dvi')


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
    dvi_file = dvi.DVIFile()
    dvi_file.write_preamble()
    dvi_file.begin_page()
    dvi_file.define_font(font_number=0, font_check_sum=0x4bf16079,
                         scale_factor=0x000a0000, design_size=0x000a0000,
                         file_path=b'cmr10')
    v_list_all.write_to_file(dvi_file)
    dvi_file.end_page()
    dvi_file.write_postamble()
    dvi_file.output_to_file('box_test.dvi')


if __name__ == '__main__':
    test_box()
