from collections import namedtuple
import os
import math

DVIBytes = namedtuple('Bytes', ['length', 'content', 'signed'])


def twos_complement(n):
    return (~abs(n)) + 1 if n < 0 else n


def to_bytes(n, length, byteorder='big', signed=True):
    # n = twos_complement(n)
    ints = [n >> (8 * i) & 0xff for i in range(length - 1, -1, -1)]
    s = bytes(bytearray(ints))
    return s if byteorder == 'big' else s[::-1]


class DVIDocument(object):
    dvi_version = 2
    byte_endianness = 'big'

    set_character_op_codes = {
        1: 128,
        2: 129,
        3: 130,
        4: 131,
    }
    put_character_op_codes = {
        1: 133,
        2: 134,
        3: 135,
        4: 136,
    }
    begin_page_op_code = 139
    end_page_op_code = 140
    push_op_code = 141
    pop_op_code = 142
    right_op_codes = {
        1: 143,
        2: 144,
        3: 145,
        4: 146,
    }
    down_op_codes = {
        1: 157,
        2: 158,
        3: 159,
        4: 160,
    }
    base_set_font_op_code = 171
    define_font_op_codes = {
        1: 243,
        2: 244,
        3: 245,
        4: 246,
    }
    preamble_op_code = 247
    postamble_op_code = 248
    post_postamble_op_code = 249

    signature_integer = 223

    def __init__(self):
        self.last_begin_page_byte_index = -1
        self.bytes_set = []
        self.font_definitions_bytes_set = []
        self.number_of_pages = 0
        self.maximum_stack_depth = 0
        self.current_stack_depth = 0
        self.current_page_height_plus_depth = 0
        self.maximum_page_height_plus_depth = 0

    def _dvi_bytes_to_bytes(self, dvi_bytes):
        kwargs = {
            'length': dvi_bytes.length,
             'byteorder': self.byte_endianness,
             'signed': dvi_bytes.signed
        }
        return to_bytes(int(dvi_bytes.content), **kwargs)

    def write_preamble(self, unit_numerator=int(254e5),
                       unit_denominator=int(7227 * 2 ** 16),
                       magnification=1000,
                       comment=' TeX output 2016.05.10:1417'):
        """Write the preamble.

        unit_numerator, unit_denominator: positive integers < 2 ** (8 * 4).
            These define the units of measurement; they are the numerator and
            denominator of a fraction by which all dimensions in the file could
            be multiplied in order to get lengths in units of 10^(-7) meters.

            For example, there are exactly 7227 TeX points in 254 centimeters,
            and TeX82 works with scaled points where there are 2^16 sp in a
            point, so TeX82 sets:
            unit_numerator = 25400000
            unit_denominator = (7227 * 2^16) == 473628672.

        magnification: positive integer < 2 ** (8 * 4)
            What TeX82 calls \mag: 1000 times the desired magnification.
            The actual fraction by which dimensions are multiplied is
            therefore
            `magnification * unit_numerator / (1000 * unit_denominator)`.
        """
        # Save for postamble
        self.unit_numerator = unit_numerator
        self.unit_denominator = unit_denominator
        self.magnification = magnification

        self.bytes_set.extend([
            DVIBytes(length=1, content=self.preamble_op_code, signed=False),
            DVIBytes(length=1, content=self.dvi_version, signed=False),
            DVIBytes(length=4, content=unit_numerator, signed=False),
            DVIBytes(length=4, content=unit_denominator, signed=False),
            DVIBytes(length=4, content=magnification, signed=False),
            DVIBytes(length=1, content=len(comment), signed=False),
        ])
        for character in comment:
            self.bytes_set.append(DVIBytes(length=1, content=ord(character),
                                           signed=False))

    def begin_page(self, page_numbers=None):
        self.bytes_set.append(DVIBytes(length=1, content=self.begin_page_op_code, signed=False))
        new_begin_page_byte_index = self.number_of_bytes - 1
        if page_numbers is None:
            page_numbers = [0 for _ in range(10)]
        if len(page_numbers) != 10:
            raise Exception
        for page_number in page_numbers:
            self.bytes_set.append(DVIBytes(length=4, content=page_number, signed=False))
        self.bytes_set.append(DVIBytes(length=4, content=self.last_begin_page_byte_index, signed=True))
        self.last_begin_page_byte_index = new_begin_page_byte_index
        self.number_of_pages += 1

    def _add_op_code(self, op_code):
        self.bytes_set.append(DVIBytes(length=1, content=op_code, signed=False))

    def end_page(self):
        self.current_page_height_plus_depth = 0
        self._add_op_code(self.end_page_op_code)

    def push(self):
        self.current_stack_depth += 1
        self.maximum_stack_depth = max(self.maximum_stack_depth, self.current_stack_depth)
        self._add_op_code(self.push_op_code)

    def pop(self):
        self.current_stack_depth -= 1
        self._add_op_code(self.pop_op_code)

    def down(self, number_of_units):
        if self.current_stack_depth == 0:
            self.current_page_height_plus_depth += number_of_units
            self.maximum_page_height_plus_depth = max(self.maximum_page_height_plus_depth,
                                                      self.current_page_height_plus_depth)

        number_of_bytes = required_bytes(number_of_units)
        op_code = self.down_op_codes[number_of_bytes]
        self._add_op_code(op_code)
        self.bytes_set.append(DVIBytes(length=number_of_bytes,
                                       content=number_of_units,
                                       signed=number_of_units < 0))

    def right(self, number_of_units):
        number_of_bytes = required_bytes(number_of_units)
        op_code = self.right_op_codes[number_of_bytes]
        self._add_op_code(op_code)
        self.bytes_set.append(DVIBytes(length=number_of_bytes,
                                       content=number_of_units,
                                       signed=number_of_units < 0))

    def set_character(self, character):
        character_code = ord(character)
        if character_code < 128:
            number_of_bytes = 0
            op_code = character_code
        else:
            number_of_bytes = required_bytes(character_code)
            op_code = self.set_character_op_codes[number_of_bytes]
        self._add_op_code(op_code)
        if number_of_bytes > 0:
            self.bytes_set.append(DVIBytes(length=number_of_bytes, content=character_code, signed=False))

    def put_character(self, character):
        character_code = ord(character)
        number_of_bytes = required_bytes(character_code)
        op_code = self.put_character_op_codes[number_of_bytes]
        self._add_op_code(op_code)
        if number_of_bytes > 0:
            self.bytes_set.append(DVIBytes(length=number_of_bytes, content=character_code, signed=False))

    def define_font(self, font_number, font_check_sum,
                    scale_factor, design_size, file_path):
        directory_path, file_name = os.path.split(file_path)
        # TODO:
        directory_path = ''
        font_name = os.path.splitext(file_name)[0]
        number_of_bytes = required_bytes(font_number)
        op_code = self.define_font_op_codes[number_of_bytes]
        font_definition_bytes_set = [
            DVIBytes(length=1, content=op_code, signed=False),
            DVIBytes(length=number_of_bytes, content=font_number, signed=False),
            DVIBytes(length=4, content=font_check_sum, signed=False),
            DVIBytes(length=4, content=scale_factor, signed=False),
            DVIBytes(length=4, content=design_size, signed=False),
            DVIBytes(length=1, content=len(directory_path), signed=False),
            DVIBytes(length=1, content=len(font_name), signed=False),
        ]
        if file_path:
            for character in directory_path + font_name:
                font_definition_bytes_set.append(DVIBytes(length=1,
                                                          content=ord(character),
                                                          signed=False))
        self.bytes_set.extend(font_definition_bytes_set)
        self.font_definitions_bytes_set.extend(font_definition_bytes_set)

    def set_font(self, font_number):
        op_code = self.base_set_font_op_code + font_number
        self._add_op_code(op_code)

    @property
    def maximum_page_width(self):
        return 0x01d5c147
        # raise NotImplementedError

    def write_postamble(self):
        self.bytes_set.append(DVIBytes(length=1, content=self.postamble_op_code, signed=False))
        postamble_byte_index = self.number_of_bytes - 1
        self.bytes_set.extend([
            DVIBytes(length=4, content=self.last_begin_page_byte_index, signed=False),
            DVIBytes(length=4, content=self.unit_numerator, signed=False),
            DVIBytes(length=4, content=self.unit_denominator, signed=False),
            DVIBytes(length=4, content=self.magnification, signed=False),
            # In the same units as other dimensions of the file. Often ignored.
            DVIBytes(length=4, content=self.maximum_page_height_plus_depth, signed=False),
            DVIBytes(length=4, content=self.maximum_page_width, signed=False),
            # Maximum stack depth, (the largest excess of push commands over
            # pop commands) needed to process the file.
            DVIBytes(length=2, content=self.maximum_stack_depth, signed=False),
            DVIBytes(length=2, content=self.number_of_pages, signed=False),
        ])
        self.bytes_set.extend(self.font_definitions_bytes_set)
        self._write_post_postamble(postamble_byte_index)

    def _write_post_postamble(self, postamble_byte_index):
        self.bytes_set.extend([
            DVIBytes(length=1, content=self.post_postamble_op_code, signed=False),
            DVIBytes(length=4, content=postamble_byte_index, signed=False),
            DVIBytes(length=1, content=self.dvi_version, signed=False),
        ])
        number_of_signature_integers = self.number_of_bytes % 4
        for _ in range(number_of_signature_integers):
            self.bytes_set.append(DVIBytes(length=1, content=self.signature_integer, signed=False))

    @property
    def number_of_bytes(self):
        total_length = 0
        for byte_set in self.bytes_set:
            total_length += byte_set.length
        return total_length

    def _to_bytes(self):
        return b''.join(self._dvi_bytes_to_bytes(b) for b in self.bytes_set)

    def to_file(self, file_name):
        with open(file_name, 'wb') as file:
            file.write(self._to_bytes())


def required_bytes(integer):
    if integer == 0:
        return 1
    n = int(math.log(abs(integer), 256)) + 1
    if integer < 0:
        n += 1
    return n
