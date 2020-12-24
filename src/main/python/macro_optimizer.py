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


PRINTABLE = {
    "KC_1": "1", "KC_2": "2", "KC_3": "3", "KC_4": "4", "KC_5": "5", "KC_6": "6", "KC_7": "7",
    "KC_8": "8", "KC_9": "9", "KC_0": "0",
    "KC_MINUS": "-",
    "KC_EQUAL": "=",
    "KC_Q": "q",
    "KC_W": "w",
    "KC_E": "e",
    "KC_R": "r",
    "KC_T": "t",
    "KC_Y": "y",
    "KC_U": "u",
    "KC_I": "i",
    "KC_O": "o",
    "KC_P": "p",
    "KC_LBRACKET": "[",
    "KC_RBRACKET": "]",
    "KC_A": "a",
    "KC_S": "s",
    "KC_D": "d",
    "KC_F": "f",
    "KC_G": "g",
    "KC_H": "h",
    "KC_J": "j",
    "KC_K": "k",
    "KC_L": "l",
    "KC_SCOLON": ";",
    "KC_QUOTE": "'",
    "KC_GRAVE": "`",
    "KC_BSLASH": "\\",
    "KC_Z": "z",
    "KC_X": "x",
    "KC_C": "c",
    "KC_V": "v",
    "KC_B": "b",
    "KC_N": "n",
    "KC_M": "m",
    "KC_COMMA": ",",
    "KC_DOT": ".",
    "KC_SLASH": "/",
}


def is_printable_tap(k):
    return isinstance(k, KeyTap) and k.keycode.qmk_id in PRINTABLE


def get_printable_char(k):
    return PRINTABLE[k.keycode.qmk_id]


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
