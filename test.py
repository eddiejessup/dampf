from __future__ import (print_function, division, absolute_import,
                        unicode_literals)

import dvi

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
dvi_file.set_character(ord('a'))
dvi_file.set_character(ord('b'))
dvi_file.pop()
dvi_file.pop()
dvi_file.down(0x180000)
dvi_file.push()
# dvi_file.right(0x00e860a3)
dvi_file.right(0x01e860a3)
dvi_file.set_character(ord('1'))
dvi_file.pop()
dvi_file.end_page()
dvi_file.write_postamble()
dvi_file.output_to_file('test.dvi')
