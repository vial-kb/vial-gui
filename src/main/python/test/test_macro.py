# SPDX-License-Identifier: GPL-2.0-or-later
import unittest

from keyboard_comm import DummyKeyboard
from keycodes import Keycode
from macro_action import ActionTap, ActionDown, ActionText, ActionDelay
from macro_key import KeyDown, KeyTap, KeyUp, KeyString
from macro_optimizer import remove_repeats, replace_with_tap, replace_with_string

KC_A = Keycode.find_by_qmk_id("KC_A")
KC_B = Keycode.find_by_qmk_id("KC_B")
KC_C = Keycode.find_by_qmk_id("KC_C")


class TestMacro(unittest.TestCase):

    def test_remove_repeats(self):
        self.assertEqual(remove_repeats([KeyDown(KC_A), KeyDown(KC_A)]), [KeyDown(KC_A)])
        self.assertEqual(remove_repeats([KeyDown(KC_A), KeyDown(KC_B), KeyDown(KC_B), KeyDown(KC_C), KeyDown(KC_C)]),
                         [KeyDown(KC_A), KeyDown(KC_B), KeyDown(KC_C)])

        # don't remove repeated taps
        self.assertEqual(remove_repeats([KeyTap(KC_A), KeyTap(KC_A)]), [KeyTap(KC_A), KeyTap(KC_A)])

    def test_replace_tap(self):
        self.assertEqual(replace_with_tap([KeyDown(KC_A)]), [KeyDown(KC_A)])
        self.assertEqual(replace_with_tap([KeyDown(KC_A), KeyUp(KC_A)]), [KeyTap(KC_A)])
        self.assertEqual(replace_with_tap([KeyUp(KC_A), KeyDown(KC_A)]), [KeyUp(KC_A), KeyDown(KC_A)])

    def test_replace_string(self):
        self.assertEqual(replace_with_string([KeyTap(KC_A), KeyTap(KC_B)]), [KeyString("ab")])

    def test_serialize_v1(self):
        kb = DummyKeyboard(None)
        kb.vial_protocol = 1
        data = kb.macro_serialize([ActionText("Hello"), ActionTap([KC_A, KC_B, KC_C]), ActionText("World"),
                                   ActionDown([KC_C, KC_B, KC_A])])
        self.assertEqual(data, b"Hello\x01\x04\x01\x05\x01\x06World\x02\x06\x02\x05\x02\x04")

    def test_deserialize_v1(self):
        kb = DummyKeyboard(None)
        kb.vial_protocol = 1
        macro = kb.macro_deserialize(b"Hello\x01\x04\x01\x05\x01\x06World\x02\x06\x02\x05\x02\x04")
        self.assertEqual(macro, [ActionText("Hello"), ActionTap([KC_A, KC_B, KC_C]), ActionText("World"),
                                 ActionDown([KC_C, KC_B, KC_A])])

    def test_serialize_v2(self):
        kb = DummyKeyboard(None)
        kb.vial_protocol = 2
        data = kb.macro_serialize([ActionText("Hello"), ActionTap([KC_A, KC_B, KC_C]), ActionText("World"),
                                   ActionDown([KC_C, KC_B, KC_A]), ActionDelay(1000)])
        self.assertEqual(data, b"Hello\x01\x01\x04\x01\x01\x05\x01\x01\x06World\x01\x02\x06\x01\x02\x05\x01\x02\x04"
                               b"\x01\x04\xEC\x04")
        data = kb.macro_serialize([ActionText("Hello"), ActionTap([KC_A, KC_B, KC_C]), ActionText("World"),
                                   ActionDown([KC_C, KC_B, KC_A]), ActionDelay(0)])
        self.assertEqual(data, b"Hello\x01\x01\x04\x01\x01\x05\x01\x01\x06World\x01\x02\x06\x01\x02\x05\x01\x02\x04"
                               b"\x01\x04\x01\x01")
        data = kb.macro_serialize([ActionText("Hello"), ActionTap([KC_A, KC_B, KC_C]), ActionText("World"),
                                   ActionDown([KC_C, KC_B, KC_A]), ActionDelay(1)])
        self.assertEqual(data, b"Hello\x01\x01\x04\x01\x01\x05\x01\x01\x06World\x01\x02\x06\x01\x02\x05\x01\x02\x04"
                               b"\x01\x04\x02\x01")
        data = kb.macro_serialize([ActionText("Hello"), ActionTap([KC_A, KC_B, KC_C]), ActionText("World"),
                                   ActionDown([KC_C, KC_B, KC_A]), ActionDelay(256)])
        self.assertEqual(data, b"Hello\x01\x01\x04\x01\x01\x05\x01\x01\x06World\x01\x02\x06\x01\x02\x05\x01\x02\x04"
                               b"\x01\x04\x02\x02")

    def test_deserialize_v2(self):
        kb = DummyKeyboard(None)
        kb.vial_protocol = 2
        macro = kb.macro_deserialize(b"Hello\x01\x01\x04\x01\x01\x05\x01\x01\x06World\x01\x02\x06\x01\x02\x05"
                                     b"\x01\x02\x04\x01\x04\xEC\x04")
        self.assertEqual(macro, [ActionText("Hello"), ActionTap([KC_A, KC_B, KC_C]), ActionText("World"),
                                 ActionDown([KC_C, KC_B, KC_A]), ActionDelay(1000)])
        macro = kb.macro_deserialize(b"Hello\x01\x01\x04\x01\x01\x05\x01\x01\x06World\x01\x02\x06\x01\x02\x05"
                                     b"\x01\x02\x04\x01\x04\x01\x01")
        self.assertEqual(macro, [ActionText("Hello"), ActionTap([KC_A, KC_B, KC_C]), ActionText("World"),
                                 ActionDown([KC_C, KC_B, KC_A]), ActionDelay(0)])
        macro = kb.macro_deserialize(b"Hello\x01\x01\x04\x01\x01\x05\x01\x01\x06World\x01\x02\x06\x01\x02\x05"
                                     b"\x01\x02\x04\x01\x04\x02\x01")
        self.assertEqual(macro, [ActionText("Hello"), ActionTap([KC_A, KC_B, KC_C]), ActionText("World"),
                                 ActionDown([KC_C, KC_B, KC_A]), ActionDelay(1)])
        macro = kb.macro_deserialize(b"Hello\x01\x01\x04\x01\x01\x05\x01\x01\x06World\x01\x02\x06\x01\x02\x05"
                                     b"\x01\x02\x04\x01\x04\x02\x02")
        self.assertEqual(macro, [ActionText("Hello"), ActionTap([KC_A, KC_B, KC_C]), ActionText("World"),
                                 ActionDown([KC_C, KC_B, KC_A]), ActionDelay(256)])

    def test_save(self):
        down = ActionDown([KC_A, KC_B])
        self.assertEqual(down.save(), ["down", "KC_A", "KC_B"])
        tap = ActionTap([KC_B, KC_A])
        self.assertEqual(tap.save(), ["tap", "KC_B", "KC_A"])
        text = ActionText("Hello world")
        self.assertEqual(text.save(), ["text", "Hello world"])
        delay = ActionDelay(123)
        self.assertEqual(delay.save(), ["delay", 123])

    def test_restore(self):
        down = ActionDown()
        down.restore(["down", "KC_A", "KC_B"])
        self.assertEqual(down, ActionDown([KC_A, KC_B]))
        tap = ActionTap()
        tap.restore(["tap", "KC_B", "KC_A"])
        self.assertEqual(tap, ActionTap([KC_B, KC_A]))
        text = ActionText()
        text.restore(["text", "Hello world"])
        self.assertEqual(text, ActionText("Hello world"))
        delay = ActionDelay()
        delay.restore(["delay", 123])
        self.assertEqual(delay, ActionDelay(123))
