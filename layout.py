import printing

from PyDvi.Font.TfmParser import TfmParser


class LayoutNode(object):

    def __init__(self, *args, **kwargs):
        self.parent = None

    def setting(self, key):
        return self.parent.setting(key)

    @property
    def first_concrete_node(self):
        if self.is_concrete:
            return self
        return self.nodes[0].first_concrete_node


class LayoutBranchNode(LayoutNode):

    def __init__(self, *args, **kwargs):
        super(LayoutBranchNode, self).__init__(*args, **kwargs)
        self.nodes = []

    def append(self, node):
        if node.parent is not None:
            raise ValueError
        self.nodes.append(node)
        node.parent = self

    def extend(self, nodes):
        for node in nodes:
            self.append(node)


class LayoutDocument(LayoutBranchNode):

    is_concrete = True

    def __init__(self):
        self.nodes = []

        line_spacing_frac = 1.2
        paragraph_spacing_frac = 2
        line_width_frac = 43.75
        indentation_width_pt = 30
        word_space_equiv_character = 'o'

        font = TfmParser.parse('cmr10',
                               '/Users/ejm/projects/pytex/pytex/cmr10.tfm')
        line_spacing_pt = font.design_font_size * line_spacing_frac
        paragraph_spacing_pt = font.design_font_size * paragraph_spacing_frac
        line_width_pt = font.design_font_size * line_width_frac

        space_width_pt = font.design_font_size * font[ord(word_space_equiv_character)].width

        self.settings = {
            'font': font,
            'line_spacing_pt': line_spacing_pt,
            'indentation_width_pt': indentation_width_pt,
            'line_width_pt': line_width_pt,
            'space_width_pt': space_width_pt,
            'paragraph_spacing_pt': paragraph_spacing_pt,
        }

    def setting(self, key):
        if key in self.settings:
            setting = self.settings[key]
            return setting
        raise NotImplementedError

    def to_print_document(self):
        print_document = printing.PrintDocumentNode()
        print_document.add_font(self.setting('font'))
        for i, layout_node in enumerate(self.nodes):
            next_layout_node = None
            for i_next in range(i + 1, len(self.nodes)):
                next_layout_node = self.nodes[i_next].first_concrete_node
                if next_layout_node is not None:
                    break

            if isinstance(layout_node, (VSkip, Paragraph, ModedNode)):
                v_nodes = layout_node.to_print_nodes(next_layout_node)
                print_document.extend(v_nodes)
        return print_document


class Character(LayoutNode):

    is_concrete = True

    def __init__(self, character, *args, **kwargs):
        super(Character, self).__init__(*args, **kwargs)
        self.character = character


class Space(LayoutNode):

    is_concrete = True

    def to_print_nodes(self):
        return [printing.HWhiteSpaceNode(width_pt=self.setting('space_width_pt'))]


class Indentation(LayoutNode):

    is_concrete = True

    def to_print_nodes(self):
        return [printing.HWhiteSpaceNode(width_pt=self.setting('indentation_width_pt'))]


class Paragraph(LayoutBranchNode):

    is_concrete = True

    def __init__(self, *args, **kwargs):
        super(Paragraph, self).__init__(*args, **kwargs)
        self.append(Indentation())

    def get_new_line_node(self):
        return printing.HListNode()

    def get_trailing_v_white_space_node(self):
        return printing.VWhiteSpaceNode(height_pt=self.setting('paragraph_spacing_pt'))

    def wrap_line_if_needed(self, print_paragraph, line_width_pt):
        if print_paragraph.latest.width_pt > line_width_pt:
            word = print_paragraph.latest.pop_word()
            new_line = self.get_new_line_node()
            new_line.extend(word)
            print_paragraph.append(new_line)

    def to_print_nodes(self, next_layout_node):
        print_paragraph = printing.RegularVListNode(v_spacing_pt=self.setting('line_spacing_pt'))
        line = self.get_new_line_node()
        print_paragraph.append(line)
        for node in self.nodes:
            if isinstance(node, Indentation):
                h_nodes = node.to_print_nodes()
                print_paragraph.latest.extend(h_nodes)
            elif isinstance(node, Space):
                h_nodes = node.to_print_nodes()
                print_paragraph.latest.extend(h_nodes)
            elif isinstance(node, Character):
                h_node = printing.CharacterNode(node.character.encode(),
                                                font=self.setting('font'))
                print_paragraph.latest.append(h_node)
            elif isinstance(node, HSkip):
                h_node = printing.HWhiteSpaceNode(width_pt=node.width_pt)
                print_paragraph.latest.append(h_node)
            self.wrap_line_if_needed(print_paragraph,
                                     self.setting('line_width_pt'))
        for line in print_paragraph.nodes[:-1]:
            printing.space_words_to_width(line, self.setting('line_width_pt'))
        v_nodes = []
        v_nodes.append(print_paragraph)
        if isinstance(next_layout_node, Paragraph):
            v_nodes.append(self.get_trailing_v_white_space_node())
        return v_nodes


class Function(LayoutNode):

    def __init__(self, func_args, *args, **kwargs):
        super(Function, self).__init__(*args, **kwargs)
        self.args = func_args


class VSkip(Function):

    is_concrete = True

    @property
    def height_pt(self):
        return self.args[0].number

    def to_print_nodes(self, next_layout_node):
        return [printing.VWhiteSpaceNode(height_pt=self.height_pt)]


class HSkip(Function):

    is_concrete = True

    @property
    def width_pt(self):
        return self.args[0].number


class ModedNode(LayoutBranchNode):

    is_concrete = False

    def __init__(self, mode, *args, **kwargs):
        super(ModedNode, self).__init__(*args, **kwargs)
        self.mode = mode

    def setting(self, key):
        if key in self.mode.settings:
            return self.mode.settings[key]
        return super(ModedNode, self).setting(key)

    def to_print_nodes(self, *args, **kwargs):
        print_nodes = []
        for node in self.nodes:
            print_nodes.extend(node.to_print_nodes(*args, **kwargs))
        return print_nodes


class LengthPoint(object):

    def __init__(self, number):
        self.number = number


class Mode(object):

    pass


class RaggedRightMode(Mode):

    def __init__(self):
        self.settings = {
            'line_width_pt': 300.0,
        }
