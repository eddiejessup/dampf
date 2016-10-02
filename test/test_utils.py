import pytest

from ..utils import get_bytes_needed, is_signed_nr_expressible_in_n_bits


test_ints = (list(range(2 ** (8 * 2))) +
             list([2 ** i for i in range(4 * 8 + 1)]))
test_ints += [n + 1 for n in test_ints] + [n - 1 for n in test_ints]
test_ints += [-n for n in test_ints]
test_ints = set(test_ints)

max_bits_we_can_use = 4 * 8


def _test(signed, n):
    # Can't encode a number.
    if not is_signed_nr_expressible_in_n_bits(n, max_bits_we_can_use):
        with pytest.raises(ValueError):
            get_bytes_needed(n, signed)

    # Meaningless arguments.
    elif not signed and n < 0:
        with pytest.raises(ValueError):
            get_bytes_needed(n, signed)

    else:
        nr_bytes = get_bytes_needed(n, signed)
        n.to_bytes(length=nr_bytes, byteorder='big', signed=signed)

        if nr_bytes > 1:
            nr_bytes_one_smaller = nr_bytes - 1
            with pytest.raises(OverflowError):
                n.to_bytes(length=nr_bytes_one_smaller,
                           byteorder='big', signed=signed)


def test_bytes_needed():
    for signed in (True, False):
        for n in test_ints:
            _test(signed, n)
