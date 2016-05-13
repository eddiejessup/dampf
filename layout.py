import printer

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


class LayoutDocument(object):

    def __init__(self):
        self.paragraphs = []


def layout_to_print(layout_document, line_spacing_frac=1.2,
                    paragraph_spacing_frac=2, line_length_frac=40,
                    font=None):
    if font is None:
        font = TfmParser.parse('cmr10',
                               '/Users/ejm/projects/pytex/pytex/cmr10.tfm')

    line_spacing_pt = font.design_font_size * line_spacing_frac
    paragraph_spacing_pt = font.design_font_size * paragraph_spacing_frac
    line_length_pt = font.design_font_size * line_length_frac

    print_document = printer.PrintDocumentNode(font=font,
                                               paragraph_spacing_pt=paragraph_spacing_pt)
    for layout_paragraph in layout_document.paragraphs:
        print_paragraph = printer.RegularVListNode(v_spacing_pt=line_spacing_pt)
        line = printer.HListNode()
        print_paragraph.append(line)
        for mover in layout_paragraph.movers:
            if isinstance(mover, Indentation):
                h_node = printer.HWhiteSpaceNode(width_pt=50)
            elif isinstance(mover, Space):
                h_node = printer.WordSpaceNode(font=font)
            elif isinstance(mover, Character):
                h_node = printer.CharacterNode(mover.character.encode(), font=font)
            print_paragraph.latest.append(h_node)
        print_document.add_paragraph(print_paragraph)
    return print_document
