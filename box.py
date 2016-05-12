import dvi

from PyDvi.TeXUnit import pt2sp


class Node(object):
    pass


class PageNode(Node):

    def __init__(self, paragraph_list, font):
        self.paragraph_list = paragraph_list
        self.font = font
        self.font_number = 0

    def write_to_file(self):
        dvi_document = dvi.DVIDocument()
        dvi_document.write_preamble()
        dvi_document.begin_page()
        dvi_document.define_font(font_number=0,
                                 font_check_sum=self.font.checksum,
                                 scale_factor=pt2sp(self.font.design_font_size),
                                 design_size=pt2sp(self.font.design_font_size),
                                 file_path='cmr10')
        dvi_document.set_font(font_number=self.font_number)
        self.paragraph_list.write_to_file(dvi_document)
        dvi_document.end_page()
        dvi_document.write_postamble()
        return dvi_document


class ContainerListNode(Node):

    def __init__(self, nodes=None):
        if nodes is None:
            nodes = []
        self.nodes = nodes

    def append(self, node):
        self.nodes.append(node)


class RegularVListNode(ContainerListNode):

    def __init__(self, v_spacing_pt, **kwargs):
        super(RegularVListNode, self).__init__(**kwargs)
        self.v_spacing_pt = v_spacing_pt

    @property
    def v_spacing_sp(self):
        return pt2sp(self.v_spacing_pt)

    def write_to_file(self, dvi_document):
        for i, node in enumerate(self.nodes):
            dvi_document.push()
            node.write_to_file(dvi_document)
            dvi_document.pop()
            if not i == len(self.nodes) - 1:
                dvi_document.down(self.v_spacing_sp)


class HListNode(ContainerListNode):

    def write_to_file(self, dvi_document):
        for node in self.nodes:
            node.write_to_file(dvi_document)

    @property
    def height(self):
        return max(node.height for node in self.nodes)


class CharacterNode(Node):

    def __init__(self, character, font):
        self.character = character
        self.font = font

    @property
    def font_info(self):
        return self.font[ord(self.character)]

    @property
    def height_pt(self):
        return self.font.design_font_size * self.font_info.height

    @property
    def height(self):
        return pt2sp(self.height_pt)

    def write_to_file(self, dvi_document):
        dvi_document.set_character(self.character)


class HWhiteSpaceNode(Node):

    def __init__(self, width_pt):
        self.width_pt = width_pt

    @property
    def width_sp(self):
        return pt2sp(self.width_pt)

    @property
    def height(self):
        return 0

    def write_to_file(self, dvi_document):
        dvi_document.right(self.width_sp)


class WordSpaceNode(HWhiteSpaceNode):

    def __init__(self, font, equiv_character='o'):
        self.font = font
        self.equiv_character = equiv_character

    @property
    def width_pt(self):
        return self.font.design_font_size * self.font[ord(self.equiv_character)].width
