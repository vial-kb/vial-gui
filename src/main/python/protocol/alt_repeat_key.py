# SPDX-License-Identifier: GPL-2.0-or-later
import struct

from keycodes.keycodes import Keycode, RESET_KEYCODE
from protocol.base_protocol import BaseProtocol
from protocol.constants import DYNAMIC_VIAL_ALT_REPEAT_KEY_GET, CMD_VIA_VIAL_PREFIX, CMD_VIAL_DYNAMIC_ENTRY_OP, \
    DYNAMIC_VIAL_ALT_REPEAT_KEY_SET
from unlocker import Unlocker


class AltRepeatKeyOptions:

    def __init__(self, data=0):
        self.default_to_this_alt_key = bool(data & (1 << 0))
        self.bidirectional = bool(data & (1 << 1))
        self.ignore_mod_handedness = bool(data & (1 << 2))
        self.enabled = bool(data & (1 << 3))

    def serialize(self):
        return (int(self.default_to_this_alt_key) << 0) \
            | (int(self.bidirectional) << 1) \
            | (int(self.ignore_mod_handedness) << 2) \
            | (int(self.enabled) << 3)

    def __repr__(self):
        return "AltRepeatKeyOptions<{}>".format(self.serialize())


class AltRepeatKeyEntry:

    def __init__(self, args=None):
        if args is None:
            args = [0] * 4

        self.keycode, self.alt_keycode, self.allowed_mods, opt = args
        self.options = AltRepeatKeyOptions(opt)

    def serialize(self):
        """ Serializes into a vial_alt_repeat_key_entry_t object """
        return struct.pack("<HHBB", Keycode.deserialize(self.keycode), Keycode.deserialize(self.alt_keycode),
                           self.allowed_mods, self.options.serialize())

    def __repr__(self):
        return "AltRepeatKey<keycode={} alt_keycode={} allowed_mods={} options={}>".format(
            self.keycode, self.alt_keycode, self.allowed_mods, self.options
        )

    def __eq__(self, other):
        return isinstance(other, AltRepeatKeyEntry) and self.serialize() == other.serialize()

    def save(self):
        """ Serializes into Vial layout file """

        return {
            "keycode": self.keycode,
            "alt_keycode": self.alt_keycode,
            "allowed_mods": self.allowed_mods,
            "options": self.options.serialize()
        }

    def restore(self, data):
        """ Restores from a Vial layout file """

        self.keycode = data["keycode"]
        self.alt_keycode = data["alt_keycode"]
        self.allowed_mods = data["allowed_mods"]
        self.options = AltRepeatKeyOptions(data["options"])


class ProtocolAltRepeatKey(BaseProtocol):

    def reload_alt_repeat_key(self):
        entries = self._retrieve_dynamic_entries(DYNAMIC_VIAL_ALT_REPEAT_KEY_GET,
                                                 self.alt_repeat_key_count, "<HHBB")
        self.alt_repeat_key_entries = []
        for e in entries:
            e = (Keycode.serialize(e[0]), Keycode.serialize(e[1]), e[2], e[3])
            self.alt_repeat_key_entries.append(AltRepeatKeyEntry(e))

    def alt_repeat_key_get(self, idx):
        return self.alt_repeat_key_entries[idx]

    def alt_repeat_key_set(self, idx, entry):
        if entry != self.alt_repeat_key_entries[idx]:
            if entry.keycode == RESET_KEYCODE or entry.alt_keycode == RESET_KEYCODE:
                Unlocker.unlock(self)

            self.alt_repeat_key_entries[idx] = entry
            self.usb_send(self.dev, struct.pack("BBBB", CMD_VIA_VIAL_PREFIX, CMD_VIAL_DYNAMIC_ENTRY_OP,
                                                DYNAMIC_VIAL_ALT_REPEAT_KEY_SET, idx) + entry.serialize())

    def save_alt_repeat_key(self):
        return [e.save() for e in self.alt_repeat_key_entries]

    def restore_alt_repeat_key(self, data):
        for x, e in enumerate(data):
            if x < self.alt_repeat_key_count:
                ko = AltRepeatKeyEntry()
                ko.restore(e)
                self.alt_repeat_key_set(x, ko)
