from utils import get_bytes_needed, is_signed_nr_expressible_in_n_bits


nrs = (list(range(2 ** (8 * 2))) +
       list([2 ** i for i in range(4 * 8 + 1)]))
nrs += [n + 1 for n in nrs] + [n - 1 for n in nrs]
nrs += [-n for n in nrs]
nrs = set(nrs)
print('off we go')

max_bits_we_can_use = 4 * 8

for signed in (True, False):
    for n in nrs:
        try:
            nr_bytes = get_bytes_needed(n, signed)
        except ValueError:
            # If we try to get the number of bits for a number we can't encode,
            # that's fine.
            if not is_signed_nr_expressible_in_n_bits(n, max_bits_we_can_use):
                continue
            # This also might happen if we try to encode a signed number with
            # signed=False. Also fine.
            elif not signed and n < 0:
                continue
            else:
                import pdb; pdb.set_trace()

        try:
            n.to_bytes(length=nr_bytes, byteorder='big', signed=signed)
        except:
            print('Too stingy')
            import pdb; pdb.set_trace()

        if nr_bytes > 1:
            nr_bytes_one_smaller = nr_bytes - 1
            try:
                n.to_bytes(length=nr_bytes_one_smaller, byteorder='big', signed=signed)
            except OverflowError:
                pass
            else:
                if n != 0:
                    print('Too generous')
                    import pdb; pdb.set_trace()
