class Node(object):
    pass


class ContainerListNode(Node):

    def __init__(self, nodes=None):
        if nodes is None:
            nodes = []
        self.nodes = nodes

    def append(self, node):
        self.nodes.append(node)


class VListNode(ContainerListNode):

    def write_to_file(self, dvi_file):
        for node in self.nodes:
            dvi_file.push()
            node.write_to_file(dvi_file)
            dvi_file.pop()
            dvi_file.down(node.height)


class HListNode(ContainerListNode):

    @property
    def height(self):
        return max(node.height for node in self.nodes)

    def write_to_file(self, dvi_file):
        for node in self.nodes:
            node.write_to_file(dvi_file)
            # dvi_file.right(node.width)


class CharacterNode(Node):

    def __init__(self, character, font_number):
        self.character = character
        self.font_number = font_number

    @property
    def height(self):
        return 1000000

    def write_to_file(self, dvi_file):
        dvi_file.set_font(font_number=self.font_number)
        dvi_file.set_character(self.character)


class WhiteSpaceNode(Node):

    def __init__(self, number_of_units):
        self.number_of_units = number_of_units

    @property
    def height(self):
        return 0

    def write_to_file(self, dvi_file):
        dvi_file.right(self.number_of_units)
