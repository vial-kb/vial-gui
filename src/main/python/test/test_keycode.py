import unittest

from keycodes.keycodes import Keycode, recreate_keyboard_keycodes


class FakeKeyboard:

    layers = 4
    macro_count = 16
    custom_keycodes = None
    tap_dance_count = 0
    midi = None

    def __init__(self, protocol):
        self.vial_protocol = protocol
        if protocol >= 6:
            self.supported_features = set([
                "persistent_default_layer", "caps_word", "layer_lock", "repeat_key",
            ])
        else:
            self.supported_features = set()


class TestKeycode(unittest.TestCase):

    def _test_serialize_protocol(self, protocol):
        recreate_keyboard_keycodes(FakeKeyboard(protocol))
        covered = 0

        # at a minimum, we should be able to deserialize/serialize everything
        for x in range(2 ** 16):
            s = Keycode.serialize(x)
            d = Keycode.deserialize(s)
            self.assertEqual(d, x, "{} serialized into {} deserialized into {}".format(x, s, d))
            if s != hex(x):
                covered += 1
        print("[protocol={}] {}/{} covered keycodes, which is {:.4f}%".format(protocol, covered, 2 ** 16, 100 * covered / 2 ** 16))

    def test_serialize_v5(self):
        self._test_serialize_protocol(5)

    def test_serialize_v6(self):
        self._test_serialize_protocol(6)
