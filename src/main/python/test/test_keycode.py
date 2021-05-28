import unittest

from keycodes import Keycode, recreate_keyboard_keycodes


class FakeKeyboard:

    layers = 4
    macro_count = 16
    custom_keycodes = None


class TestKeycode(unittest.TestCase):

    def test_serialize(self):
        recreate_keyboard_keycodes(FakeKeyboard())

        # at a minimum, we should be able to deserialize/serialize everything
        for x in range(2 ** 16):
            s = Keycode.serialize(x)
            d = Keycode.deserialize(s)
            self.assertEqual(d, x, "{} serialized into {} deserialized into {}".format(x, s, d))
