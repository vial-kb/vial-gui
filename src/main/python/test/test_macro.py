# SPDX-License-Identifier: GPL-2.0-or-later
import unittest

from keycodes import find_keycode
from macro_key import KeyDown, KeyTap
from macro_optimizer import remove_repeats


KC_A = find_keycode(0x04)
KC_B = find_keycode(0x05)
KC_C = find_keycode(0x06)


class TestMacro(unittest.TestCase):

    def test_remove_repeats(self):
        self.assertEqual(remove_repeats([KeyDown(KC_A), KeyDown(KC_A)]), [KeyDown(KC_A)])
        self.assertEqual(remove_repeats([KeyDown(KC_A), KeyDown(KC_B), KeyDown(KC_B), KeyDown(KC_C), KeyDown(KC_C)]),
                         [KeyDown(KC_A), KeyDown(KC_B), KeyDown(KC_C)])

        # don't remove repeated taps
        self.assertEqual(remove_repeats([KeyTap(KC_A), KeyTap(KC_A)]), [KeyTap(KC_A), KeyTap(KC_A)])
