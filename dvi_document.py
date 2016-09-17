from pydvi.Font.TfmParser import TfmParser
from pydvi.TeXUnit import pt2sp


from dvi_abstracted import (get_preamble_instruction,
                            get_begin_page_instruction,
                            get_end_page_instruction,
                            get_define_font_nr_instruction,
                            get_select_font_nr_instruction,
                            get_postamble_instruction,
                            get_post_postamble_instruction,
                            get_set_char_instruction)
from dvi_spec import EncodedOperation, OpCode

numerator = int(254e5)
denominator = int(7227 * 2 ** 16)
dvi_format = 2


class DVIDocument(object):
    """docstring for DVIDocument"""
    def __init__(self, magnification):
        self.magnification = magnification

        self.preamble = get_preamble_instruction(dvi_format=dvi_format,
                                                 numerator=numerator,
                                                 denominator=denominator,
                                                 magnification=self.magnification,
                                                 comment='')
        self.mundane_instructions = []
        self.defined_fonts_info = {}

    @property
    def instructions(self):
        return [self.preamble] + self.mundane_instructions


    @property
    def last_begin_page_pointer(self):
        last_begin_page_pointer = -1
        byte_pointer = 0
        for instruction in reversed(self.mundane_instructions):
            for part in instruction.op_and_args:
                byte_pointer += part.nr_bytes()
                if (isinstance(part, EncodedOperation)
                        and part.op_code == OpCode.begin_page):
                    last_begin_page_pointer = byte_pointer
        return last_begin_page_pointer

    def begin_page(self):
        bop_args = list(range(10)) + [self.last_begin_page_pointer]
        bop = get_begin_page_instruction(*bop_args)
        self.mundane_instructions.append(bop)

    def end_page(self):
        eop = get_end_page_instruction()
        self.mundane_instructions.append(eop)

    def define_font(self, font_nr, font_name, font_path):
        font_parser = TfmParser(font_name, font_path)
        font_info = font_parser.tfm
        scale_factor = design_size = int(pt2sp(font_info.design_font_size))
        font_path = font_info.font_name
        define_font_nr_instr = get_define_font_nr_instruction(font_nr,
                                                              font_info.checksum,
                                                              scale_factor,
                                                              design_size,
                                                              font_path)
        self.mundane_instructions.append(define_font_nr_instr)
        self.defined_fonts_info[font_nr] = font_parser

    def select_font(self, font_nr):
        inst = get_select_font_nr_instruction(font_nr)
        self.mundane_instructions.append(inst)
        # TODO: Could actually get this from instructions dynamically.
        self.current_font_nr = font_nr

    @property
    def current_font_info(self):
        return self.defined_fonts_info[self.current_font_nr]

    def end_document(self):
        self.do_postamble()
        # TODO: Re-define fonts.
        self.do_post_postamble()

    def do_postamble(self):
        max_page_height_plus_depth = 15
        max_page_width = 7
        max_stack_depth = 1
        nr_pages = 1
        self.postamble_pointer = len(self.encode()) + 1
        post = get_postamble_instruction(self.last_begin_page_pointer,
                                         numerator,
                                         denominator,
                                         self.magnification,
                                         max_page_height_plus_depth,
                                         max_page_width,
                                         max_stack_depth,
                                         nr_pages
                                         )
        self.mundane_instructions.append(post)

    def do_post_postamble(self):
        post_post = get_post_postamble_instruction(self.postamble_pointer,
                                                   dvi_format)
        self.mundane_instructions.append(post_post)

    def encode(self):
        return b''.join(inst.encode() for inst in self.instructions)

    def set_char(self, char):
        self.mundane_instructions.append(get_set_char_instruction(char))

    def write(self, file_name):
        open(file_name, 'wb').write(self.encode())

d = DVIDocument(magnification=1000)
d.begin_page()
d.define_font(font_nr=0, font_name='cmr10', font_path='cmr10.tfm')
d.select_font(font_nr=0)
font_info = d.current_font_info
for char in range(font_info.smallest_character_code,
                  font_info.largest_character_code):
    d.set_char(char)
d.end_page()
d.end_document()
d.write('test.dvi')
