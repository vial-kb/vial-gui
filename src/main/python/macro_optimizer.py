# SPDX-License-Identifier: GPL-2.0-or-later
from macro_key import KeyUp, KeyDown, KeyTap, KeyString


def remove_repeats(sequence):
    """ Removes exact repetition, i.e. two Down or two Up of the same key """
    out = []
    for k in sequence:
        if out and (isinstance(k, KeyDown) or isinstance(k, KeyUp)) and k == out[-1]:
            continue
        out.append(k)
    return out


def replace_with_tap(sequence):
    """ Replaces a sequence of Down/Up with a Tap """
    out = []
    sequence = sequence[:]
    while len(sequence) > 0:
        if len(sequence) >= 2 and isinstance(sequence[0], KeyDown) and isinstance(sequence[1], KeyUp) and \
                sequence[0].keycode == sequence[1].keycode:
            key = KeyTap(sequence[0].keycode)
            out.append(key)
            sequence.pop(0)
            sequence.pop(0)
        else:
            out.append(sequence[0])
            sequence.pop(0)
    return out


def is_printable_tap(k):
    return isinstance(k, KeyTap) and k.keycode.printable


def get_printable_char(k):
    return k.keycode.printable


def replace_with_string(sequence):
    """ Replaces a sequence of printable taps with a sendstring """
    out = []
    sequence = sequence[:]
    while len(sequence) > 0:
        if len(sequence) >= 2 and is_printable_tap(sequence[0]) and is_printable_tap(sequence[1]):
            cur = get_printable_char(sequence[0]) + get_printable_char(sequence[1])
            sequence.pop(0)
            sequence.pop(0)
            while len(sequence) and is_printable_tap(sequence[0]):
                cur += get_printable_char(sequence[0])
                sequence.pop(0)
            out.append(KeyString(cur))
        else:
            out.append(sequence[0])
            sequence.pop(0)
    return out


def macro_optimize(sequence):
    sequence = remove_repeats(sequence)
    sequence = replace_with_tap(sequence)
    sequence = replace_with_string(sequence)
    return sequence
