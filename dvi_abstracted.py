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

                      get_select_font_nr_instruction,
                      get_do_special_instruction,
                      get_define_font_nr_instruction,

                      get_preamble_instruction,
                      get_postamble_instruction,
                      get_post_postamble_instruction,
                      )


def commands_to_bytes(commands):
    return (b'').join(ev.encode() for ev in commands)

commands = []

numerator = int(254e5)
denominator = int(7227 * 2 ** 16)
magnification = 1000
dvi_format = 2
pre = get_preamble_instruction(dvi_format=dvi_format,
                               numerator=numerator, denominator=denominator,
                               magnification=magnification, comment='')
commands += pre

bop_args = list(range(10)) + [-1]
bop = get_begin_page_instruction(*bop_args)
commands += bop
final_begin_page_pointer = len(commands_to_bytes(commands))

font_nr = 0
check_sum = 1274110073
scale_factor = design_size = 655360
font_path = 'cmr10'
commands += get_define_font_nr_instruction(font_nr,
                                           check_sum,
                                           scale_factor, design_size,
                                           font_path)
commands += get_select_font_nr_instruction(font_nr)
commands += get_set_char_instruction(90)

eop = get_end_page_instruction()
commands += eop

max_page_height_plus_depth = 15
max_page_width = 7
max_stack_depth = 1
nr_pages = 1
postamble_pointer = len(commands_to_bytes(commands)) + 1
post = get_postamble_instruction(final_begin_page_pointer,
                                 numerator,
                                 denominator,
                                 magnification,
                                 max_page_height_plus_depth,
                                 max_page_width,
                                 max_stack_depth,
                                 nr_pages
                                 )
commands += post

post_post = get_post_postamble_instruction(postamble_pointer, dvi_format)
commands += post_post
point_nr = 1
for c in commands:
    print(c, ' \t\tpoint: {}'.format(point_nr))
    point_nr += len(commands_to_bytes([c]))
encodeds = commands_to_bytes(commands)

open('test.dvi', 'wb').write(encodeds)
