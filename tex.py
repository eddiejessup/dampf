import box


class TexPage(object):

    def __init__(self, font, line_spacing_frac=1.2, paragraph_spacing_frac=2):
        self.paragraph_spacing_frac = paragraph_spacing_frac
        self.line_spacing_frac = line_spacing_frac
        self.font = font
        paragraph_list = box.RegularVListNode(v_spacing_pt=self.paragraph_spacing_pt)
        self.page = box.PageNode(paragraph_list=paragraph_list, font=font)

    @property
    def _paragraph_list(self):
        return self.page.paragraph_list

    @property
    def _current_paragraph(self):
        return self._paragraph_list.nodes[-1]

    @property
    def _current_line(self):
        return self._current_paragraph.nodes[-1]

    @property
    def line_spacing_pt(self):
        return self.font.design_font_size * self.line_spacing_frac

    @property
    def paragraph_spacing_pt(self):
        return self.font.design_font_size * self.paragraph_spacing_frac

    def _start_new_line(self):
        line = box.HListNode()
        self._current_paragraph.append(line)

    def start_new_paragraph(self):
        paragraph = box.RegularVListNode(v_spacing_pt=self.line_spacing_pt)
        self._paragraph_list.append(paragraph)
        self._start_new_line()
        indentation = box.HWhiteSpaceNode(width_pt=50)
        self._current_line.append(indentation)

    def add_character(self, character):
        c = box.CharacterNode(character.encode(), font=self.font)
        self._current_line.append(c)

    def add_space(self):
        n = box.WordSpaceNode(font=self.font)
        self._current_line.append(n)

    def output_to_dvi_file(self):
        return self.page.write_to_file()
