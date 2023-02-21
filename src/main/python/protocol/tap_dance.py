# SPDX-License-Identifier: GPL-2.0-or-later
import struct

from keycodes.keycodes import Keycode, RESET_KEYCODE
from protocol.base_protocol import BaseProtocol
from protocol.constants import DYNAMIC_VIAL_TAP_DANCE_GET, CMD_VIA_VIAL_PREFIX, DYNAMIC_VIAL_TAP_DANCE_SET, \
    CMD_VIAL_DYNAMIC_ENTRY_OP
from unlocker import Unlocker


class ProtocolTapDance(BaseProtocol):

    def reload_tap_dance(self):
        self.tap_dance_entries = self._retrieve_dynamic_entries(DYNAMIC_VIAL_TAP_DANCE_GET,
                                                                self.tap_dance_count, "<HHHHH")
        for x, entry in enumerate(self.tap_dance_entries):
            self.tap_dance_entries[x] = (Keycode.serialize(entry[0]), Keycode.serialize(entry[1]),
                                         Keycode.serialize(entry[2]), Keycode.serialize(entry[3]),
                                         entry[4])

    def tap_dance_get(self, idx):
        return self.tap_dance_entries[idx]

    def tap_dance_set(self, idx, entry):
        if self.tap_dance_entries[idx] == entry:
            return
        for x in range(4):
            if entry[x] == RESET_KEYCODE:
                Unlocker.unlock(self)
        self.tap_dance_entries[idx] = entry
        entry = [Keycode.deserialize(entry[0]), Keycode.deserialize(entry[1]), Keycode.deserialize(entry[2]),
                 Keycode.deserialize(entry[3]), entry[4]]
        serialized = struct.pack("<HHHHH", *entry)
        self.usb_send(self.dev, struct.pack("BBBB", CMD_VIA_VIAL_PREFIX, CMD_VIAL_DYNAMIC_ENTRY_OP,
                                            DYNAMIC_VIAL_TAP_DANCE_SET, idx) + serialized, retries=20)

    def save_tap_dance(self):
        tap_dance = []
        for entry in self.tap_dance_entries:
            tap_dance.append((entry[0], entry[1], entry[2], entry[3], entry[4]))
        return tap_dance

    def restore_tap_dance(self, data):
        for x, e in enumerate(data):
            if x < self.tap_dance_count:
                self.tap_dance_set(x, e)
