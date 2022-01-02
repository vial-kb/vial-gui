# SPDX-License-Identifier: GPL-2.0-or-later
import struct

from keycodes import Keycode
from protocol.base_protocol import BaseProtocol
from protocol.constants import DYNAMIC_VIAL_KEY_OVERRIDE_GET, CMD_VIA_VIAL_PREFIX, CMD_VIAL_DYNAMIC_ENTRY_OP, \
    DYNAMIC_VIAL_KEY_OVERRIDE_SET


class KeyOverrideOptions:

    def __init__(self, data=0):
        self.activation_trigger_down = bool(data & (1 << 0))
        self.activation_required_mod_down = bool(data & (1 << 1))
        self.activation_negative_mod_up = bool(data & (1 << 2))
        self.one_mod = bool(data & (1 << 3))
        self.no_reregister_trigger = bool(data & (1 << 4))
        self.no_unregister_on_other_key_down = bool(data & (1 << 5))
        self.enabled = bool(data & (1 << 7))

    def serialize(self):
        return (int(self.activation_trigger_down) << 0) \
            | (int(self.activation_required_mod_down) << 1) \
            | (int(self.activation_negative_mod_up) << 2) \
            | (int(self.one_mod) << 3) \
            | (int(self.no_reregister_trigger) << 4) \
            | (int(self.no_unregister_on_other_key_down) << 5) \
            | (int(self.enabled) << 7)

    def __repr__(self):
        return "KeyOverrideOptions<{}>".format(self.serialize())


class KeyOverrideEntry:

    def __init__(self, args=None):
        if args is None:
            args = [0] * 7
        self.trigger, self.replacement, self.layers, self.trigger_mods, self.negative_mod_mask, \
            self.suppressed_mods, opt = args
        self.options = KeyOverrideOptions(opt)

    def serialize(self):
        """ Serializes into a vial_key_override_entry_t object """
        return struct.pack("<HHHBBBB", self.trigger, self.replacement, self.layers, self.trigger_mods,
                           self.negative_mod_mask, self.suppressed_mods, self.options.serialize())

    def __repr__(self):
        return "KeyOverride<trigger={} replacement={} layers={} trigger_mods={} negative_mod_mask={} " \
               "suppresed_mods={} options={}>".format(self.trigger, self.replacement, self.layers, self.trigger_mods,
                                                      self.negative_mod_mask, self.suppressed_mods, self.options)

    def __eq__(self, other):
        return isinstance(other, KeyOverrideEntry) and self.serialize() == other.serialize()

    def save(self):
        """ Serializes into Vial layout file """

        return {
            "trigger": Keycode.serialize(self.trigger),
            "replacement": Keycode.serialize(self.replacement),
            "layers": self.layers,
            "trigger_mods": self.trigger_mods,
            "negative_mod_mask": self.negative_mod_mask,
            "suppressed_mods": self.suppressed_mods,
            "options": self.options.serialize()
        }

    def restore(self, data):
        """ Restores from a Vial layout file """

        self.trigger = Keycode.deserialize(data["trigger"])
        self.replacement = Keycode.deserialize(data["replacement"])
        self.layers = data["layers"]
        self.trigger_mods = data["trigger_mods"]
        self.negative_mod_mask = data["negative_mod_mask"]
        self.suppressed_mods = data["suppressed_mods"]
        self.options = KeyOverrideOptions(data["options"])


class ProtocolKeyOverride(BaseProtocol):

    def reload_key_override(self):
        entries = self._retrieve_dynamic_entries(DYNAMIC_VIAL_KEY_OVERRIDE_GET,
                                                 self.key_override_count, "<HHHBBBB")
        self.key_override_entries = [KeyOverrideEntry(e) for e in entries]

    def key_override_get(self, idx):
        return self.key_override_entries[idx]

    def key_override_set(self, idx, entry):
        if entry != self.key_override_entries[idx]:
            self.key_override_entries[idx] = entry
            self.usb_send(self.dev, struct.pack("BBBB", CMD_VIA_VIAL_PREFIX, CMD_VIAL_DYNAMIC_ENTRY_OP,
                                                DYNAMIC_VIAL_KEY_OVERRIDE_SET, idx) + entry.serialize())

    def save_key_override(self):
        return [e.save() for e in self.key_override_entries]

    def restore_key_override(self, data):
        for x, e in enumerate(data):
            if x < self.key_override_count:
                ko = KeyOverrideEntry()
                ko.restore(e)
                self.key_override_set(x, ko)
