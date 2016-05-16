import printing

from PyDvi.Font.TfmParser import TfmParser


class Character(object):

    def __init__(self, character):
        self.character = character


class Space(object):

    def __init__(self):
        pass


class Indentation(object):

    pass


class Paragraph(object):

    def __init__(self):
        self.movers = [Indentation()]

    def add_mover(self, mover):
        self.movers.append(mover)

    def get_new_line_node(self):
        return printing.HListNode()


class Function(object):

    def __init__(self, *args):
        self.args = args


class VSkip(Function):

    def __init__(self, height_pt):
        self.height_pt = height_pt.number


class HSkip(Function):

    def __init__(self, width_pt):
        self.width_pt = width_pt.number


class LengthPoint(object):

    def __init__(self, number):
        self.number = number


class Mode(object):

    pass


class RaggedRightMode(Mode):

    pass


class ModedComponent(object):

    def __init__(self, component, mode):
        self.mode = mode
        self.component = component


class LayoutDocument(object):

    def __init__(self):
        self.components = []


def space_words_to_width(line, line_width_pt):
    width_to_make = line_width_pt - line.width_pt
    white_space_width_pt = sum(node.width_pt
                               for node in line.white_space_nodes)
    scale_factor = 1.0 + width_to_make / white_space_width_pt
    for node in line.white_space_nodes:
        node.scale(scale_factor)


def wrap_line_if_needed(layout_paragraph, print_paragraph, line_width_pt):
    if print_paragraph.latest.width_pt > line_width_pt:
        word = print_paragraph.latest.pop_word()
        new_line = layout_paragraph.get_new_line_node()
        new_line.extend(word)
        print_paragraph.append(new_line)


def layout_to_print(layout_document, line_spacing_frac=1.2,
                    paragraph_spacing_frac=2, line_width_frac=43.75,
                    indentation_width_pt=30, word_space_equiv_character='o',
                    font=None):
    if font is None:
        font = TfmParser.parse('cmr10',
                               '/Users/ejm/projects/pytex/pytex/cmr10.tfm')

    line_spacing_pt = font.design_font_size * line_spacing_frac
    paragraph_spacing_pt = font.design_font_size * paragraph_spacing_frac
    line_width_pt = font.design_font_size * line_width_frac

    space_width_pt = font.design_font_size * font[ord(word_space_equiv_character)].width

    print_document = printing.PrintDocumentNode()
    print_document.add_font(font)
    for i, layout_component in enumerate(layout_document.components):
        if i < len(layout_document.components) - 1:
            next_layout_component = layout_document.components[i + 1]
        else:
            next_layout_component = None

        if isinstance(layout_component, Paragraph):
            print_paragraph = printing.RegularVListNode(v_spacing_pt=line_spacing_pt)
            line = layout_component.get_new_line_node()
            print_paragraph.append(line)
            for mover in layout_component.movers:
                if isinstance(mover, Indentation):
                    h_node = printing.HWhiteSpaceNode(width_pt=indentation_width_pt)
                    print_paragraph.latest.append(h_node)
                elif isinstance(mover, Space):
                    h_node = printing.HWhiteSpaceNode(width_pt=space_width_pt)
                    print_paragraph.latest.append(h_node)
                elif isinstance(mover, Character):
                    h_node = printing.CharacterNode(mover.character.encode(),
                                                    font=font)
                    print_paragraph.latest.append(h_node)
                elif isinstance(mover, HSkip):
                    h_node = printing.HWhiteSpaceNode(width_pt=mover.width_pt)
                    print_paragraph.latest.append(h_node)
                wrap_line_if_needed(layout_component, print_paragraph,
                                    line_width_pt)
            for line in print_paragraph.nodes[:-1]:
                space_words_to_width(line, line_width_pt)
            print_document.append(print_paragraph)
            if isinstance(next_layout_component, Paragraph):
                print_document.append(printing.VWhiteSpaceNode(height_pt=paragraph_spacing_pt))
        elif isinstance(layout_component, VSkip):
            print_document.append(printing.VWhiteSpaceNode(height_pt=layout_component.height_pt))
    return print_document
