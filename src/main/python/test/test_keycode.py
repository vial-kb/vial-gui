import unittest

from keycodes import Keycode


class TestKeycode(unittest.TestCase):

    def test_serialize(self):
        print(Keycode.serialize(0x100))
        print(Keycode.deserialize("KC_A"))
