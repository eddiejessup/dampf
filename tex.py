import dvi
import box


class TexFile(object):

    def __init__(self):
        self.v_list = box.VListNode()

    @property
    def current_h_list(self):
        h_list = self.v_list.nodes[-1]
        if not isinstance(h_list, box.HListNode):
            raise TypeError
        return h_list

    def start_paragraph(self):
        h_list = box.HListNode()
        self.v_list.append(h_list)

    def add_character(self, character):
        b = character.encode()
        c = box.CharacterNode(b, font_number=0)
        self.current_h_list.append(c)

    def add_space(self):
        n = box.WhiteSpaceNode(220000)
        self.current_h_list.append(n)

    def output_to_dvi_file(self):
        dvi_file = dvi.DVIFile()
        dvi_file.write_preamble()
        dvi_file.begin_page()
        dvi_file.define_font(font_number=0, font_check_sum=0x4bf16079,
                             scale_factor=0x000a0000, design_size=0x000a0000,
                             file_path=b'cmr10')
        self.v_list.write_to_file(dvi_file)
        dvi_file.end_page()
        dvi_file.write_postamble()
        return dvi_file
