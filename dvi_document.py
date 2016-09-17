from pydvi.Font.TfmParser import TfmParser
from pydvi.TeXUnit import pt2sp


from dvi_spec import (get_set_char_instruction,
                      get_set_rule_instruction,
                      get_put_char_instruction,
                      get_put_rule_instruction,

                      get_no_op_instruction,

                      get_begin_page_instruction,
                      get_end_page_instruction,

                      get_push_instruction,
                      get_pop_instruction,

                      get_right_instruction,
                      get_right_w_instruction,
                      get_set_w_then_right_w_instruction,
                      get_right_x_instruction,
                      get_set_x_then_right_x_instruction,

                      get_down_instruction,
                      get_down_y_instruction,
                      get_set_y_then_down_y_instruction,
                      get_down_z_instruction,
                      get_set_z_then_down_z_instruction,

                      get_define_font_nr_instruction,
                      get_select_font_nr_instruction,

                      get_do_special_instruction,

                      get_preamble_instruction,
                      get_postamble_instruction,
                      get_post_postamble_instruction,
                      )
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
        self.stack_depth = 0
        self.max_stack_depth = self.stack_depth

    @property
    def instructions(self):
        return [self.preamble] + self.mundane_instructions

    @property
    def flat_instruction_parts(self):
        return [p for inst in self.instructions for p in inst.op_and_args]

    @property
    def begin_page_pointers(self):
        byte_pointer = 0
        begin_page_pointers = []
        for part in self.flat_instruction_parts:
            byte_pointer += part.nr_bytes()
            if (isinstance(part, EncodedOperation)
                    and part.op_code == OpCode.begin_page):
                begin_page_pointers.append(byte_pointer)
        return begin_page_pointers

    @property
    def last_begin_page_pointer(self):
        pointers = self.begin_page_pointers
        return pointers[-1] if pointers else -1

    @property
    def nr_begin_page_pointers(self):
        return len(self.begin_page_pointers)

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
        self._define_font(font_nr, font_info)
        self.defined_fonts_info[font_nr] = font_info

    def _define_font(self, font_nr, font_info):
        scale_factor = design_size = int(pt2sp(font_info.design_font_size))
        font_path = font_info.font_name
        define_font_nr_instr = get_define_font_nr_instruction(font_nr,
                                                              font_info.checksum,
                                                              scale_factor,
                                                              design_size,
                                                              font_path)
        self.mundane_instructions.append(define_font_nr_instr)

    def select_font(self, font_nr):
        inst = get_select_font_nr_instruction(font_nr)
        self.mundane_instructions.append(inst)
        # TODO: Could actually get this from instructions dynamically.
        self.current_font_nr = font_nr

    @property
    def current_font_info(self):
        return self.defined_fonts_info[self.current_font_nr]

    def end_document(self):
        self._do_postamble()
        # Define all defined fonts again, as required.
        for font_nr, font_info in self.defined_fonts_info.items():
            self._define_font(font_nr, font_info)
        self._do_post_postamble()

    def _do_postamble(self):
        # I am told these are often ignored, so leave them un-implemented for
        # now.
        max_page_height_plus_depth = 1
        max_page_width = 1

        self.postamble_pointer = len(self.encode()) + 1
        post = get_postamble_instruction(self.last_begin_page_pointer,
                                         numerator,
                                         denominator,
                                         self.magnification,
                                         max_page_height_plus_depth,
                                         max_page_width,
                                         self.max_stack_depth,
                                         self.nr_begin_page_pointers
                                         )
        self.mundane_instructions.append(post)

    def _do_post_postamble(self):
        post_post = get_post_postamble_instruction(self.postamble_pointer,
                                                   dvi_format)
        self.mundane_instructions.append(post_post)

    def push(self):
        # House-keeping to track maximum stack depth for postamble.
        self.stack_depth += 1
        self.max_push_level = max(self.stack_depth, self.max_stack_depth)
        self.mundane_instructions.append(get_push_instruction())

    def pop(self):
        self.stack_depth -= 1
        self.mundane_instructions.append(get_pop_instruction())

    def down(self, a):
        self.mundane_instructions.append(get_down_instruction(a))

    def encode(self):
        return b''.join(inst.encode() for inst in self.instructions)

    def set_char(self, char):
        self.mundane_instructions.append(get_set_char_instruction(char))

    def write(self, file_name):
        open(file_name, 'wb').write(self.encode())

    def put_rule(self, height, width):
        inst = get_put_rule_instruction(height, width)
        self.mundane_instructions.append(inst)

    def set_rule(self, height, width):
        inst = get_set_rule_instruction(height, width)
        self.mundane_instructions.append(inst)

d = DVIDocument(magnification=1000)

d.begin_page()

d.define_font(font_nr=0, font_name='cmr10', font_path='cmr10.tfm')
d.select_font(font_nr=0)
font_info = d.current_font_info
d.push()
for char in range(font_info.smallest_character_code,
                  font_info.largest_character_code):
    d.set_char(char)
d.pop()

d.down(1000000)

d.define_font(font_nr=1, font_name='cmb10', font_path='cmb10.tfm')
d.select_font(font_nr=1)
d.push()
for char in range(font_info.smallest_character_code,
                  font_info.largest_character_code):
    d.set_char(char)
d.pop()

d.down(1000000)
d.put_rule(1000000, 10000000)

d.end_page()
d.end_document()
d.write('test.dvi')
