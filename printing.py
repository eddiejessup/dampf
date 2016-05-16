import dvi

from PyDvi.TeXUnit import pt2sp


class Node(object):

    @property
    def width_sp(self):
        return pt2sp(self.width_pt)

    @property
    def height_sp(self):
        return pt2sp(self.height_pt)

    def __repr__(self):
        return self.__class__.__name__


class ContainerListNode(Node):

    def __init__(self, nodes=None):
        if nodes is None:
            nodes = []
        self.nodes = nodes

    @property
    def latest(self):
        return self.nodes[-1]

    def append(self, node):
        self.nodes.append(node)

    def extend(self, nodes):
        self.nodes.extend(nodes)

    def __repr__(self):
        return self.nodes.__repr__()


class PrintDocumentNode(ContainerListNode):

    def __init__(self, fonts=None, **kwargs):
        super(PrintDocumentNode, self).__init__(**kwargs)
        if fonts is None:
            self.fonts = []

    def add_font(self, font):
        self.fonts.append(font)

    @property
    def height_pt(self):
        return self.nodes.height_pt

    @property
    def width_pt(self):
        return self.nodes.width_pt


class SpacedVListNode(ContainerListNode):

    def __init__(self, v_spacing_pt, **kwargs):
        super(SpacedVListNode, self).__init__(**kwargs)
        self.v_spacing_pt = v_spacing_pt

    @property
    def v_spacing_sp(self):
        return pt2sp(self.v_spacing_pt)

    def write_to_dvi_document(self, dvi_document):
        for i, node in enumerate(self.nodes):
            node.write_to_dvi_document(dvi_document)
            if not i == len(self.nodes) - 1:
                dvi_document.down(self.v_spacing_sp)

    @property
    def height_pt(self):
        h = 0
        for i, node in enumerate(self.nodes):
            h += node.height_pt
            h += self.v_spacing_pt
            if not i == len(self.nodes) - 1:
                h += self.v_spacing_pt
        return h

    @property
    def width_pt(self):
        return max(node.width_pt for node in self.nodes)


class RegularVListNode(SpacedVListNode):

    def write_to_dvi_document(self, dvi_document):
        for i, node in enumerate(self.nodes):
            dvi_document.push()
            node.write_to_dvi_document(dvi_document)
            dvi_document.pop()
            dvi_document.down(self.v_spacing_sp)


class HListNode(ContainerListNode):

    def write_to_dvi_document(self, dvi_document):
        for node in self.nodes:
            node.write_to_dvi_document(dvi_document)

    @property
    def height_pt(self):
        return max(node.height_pt for node in self.nodes)

    @property
    def width_pt(self):
        return sum(node.width_pt for node in self.nodes)

    @property
    def white_space_nodes(self):
        return [node for node in self.nodes
                if isinstance(node, HWhiteSpaceNode)]

    def pop_word(self):
        word = []
        while True:
            if isinstance(self.nodes[-1], CharacterNode):
                word.append(self.nodes.pop())
            else:
                # Remove trailing white space before popped word.
                self.nodes.pop()
                break
        return reversed(word)


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
    def width_pt(self):
        return self.font.design_font_size * self.font_info.width

    def write_to_dvi_document(self, dvi_document):
        # TODO: font_number
        dvi_document.set_font(font_number=0)
        dvi_document.put_character(self.character)
        dvi_document.right(self.width_sp)


class HWhiteSpaceNode(Node):

    def __init__(self, width_pt):
        self.width_pt = width_pt
        self.width_pt_base = self.width_pt

    @property
    def height_pt(self):
        return 0

    def scale(self, scale_factor):
        self.width_pt *= scale_factor

    def write_to_dvi_document(self, dvi_document):
        dvi_document.right(self.width_sp)


class VWhiteSpaceNode(Node):

    def __init__(self, height_pt):
        self.height_pt = height_pt
        self.height_pt_base = self.height_pt

    @property
    def width_pt(self):
        return 0

    def scale(self, scale_factor):
        self.height_pt *= scale_factor

    def write_to_dvi_document(self, dvi_document):
        dvi_document.down(self.height_sp)


def print_to_dvi(print_document):
    dvi_document = dvi.DVIDocument()
    dvi_document.write_preamble()
    dvi_document.begin_page()
    for i, font in enumerate(print_document.fonts):
        dvi_document.define_font(font_number=i,
                                 font_check_sum=font.checksum,
                                 scale_factor=pt2sp(font.design_font_size),
                                 design_size=pt2sp(font.design_font_size),
                                 file_path=font.filename)
    dvi_document.set_font(font_number=0)
    for node in print_document.nodes:
        node.write_to_dvi_document(dvi_document)
    dvi_document.end_page()
    dvi_document.write_postamble()
    return dvi_document


def space_words_to_width(line, line_width_pt):
    width_to_make = line_width_pt - line.width_pt
    white_space_width_pt = sum(node.width_pt
                               for node in line.white_space_nodes)
    scale_factor = 1.0 + width_to_make / white_space_width_pt
    for node in line.white_space_nodes:
        node.scale(scale_factor)
