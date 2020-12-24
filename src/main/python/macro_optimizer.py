# SPDX-License-Identifier: GPL-2.0-or-later
from macro_key import KeyUp, KeyDown, KeyTap


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


def macro_optimize(sequence):
    sequence = remove_repeats(sequence)
    sequence = replace_with_tap(sequence)
    return sequence
