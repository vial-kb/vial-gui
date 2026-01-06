# SPDX-License-Identifier: GPL-2.0-or-later
"""
Rule Lighting Protocol

This module implements the protocol for Rule Lighting (vial_rule_lighting),
a feature that allows configuring per-key RGB colors based on keyboard state
(layer, modifiers, caps lock) and keycode ranges.

Rules are matched in order (first-match-wins) and can set idle and pressed
colors for matching keys. This enables visual feedback for layer indicators,
modifier states, and keycode-based highlighting.
"""
import struct

from keycodes.keycodes import Keycode
from protocol.base_protocol import BaseProtocol
from protocol.constants import CMD_VIA_VIAL_PREFIX, CMD_VIAL_DYNAMIC_ENTRY_OP, \
    DYNAMIC_VIAL_RULE_LIGHTING_GET_ENTRY, DYNAMIC_VIAL_RULE_LIGHTING_SET_ENTRY


# Saturation modes (2 bits) - matches firmware enum
SAT_OFF = 0b00      # LED off (RGB 0,0,0)
SAT_WHITE = 0b01    # S=0 (white/grayscale)
SAT_PASTEL = 0b10   # S=128 (soft color)
SAT_PURE = 0b11     # S=255 (vivid color)

SAT_LABELS = {
    SAT_OFF: "Off",
    SAT_WHITE: "White",
    SAT_PASTEL: "Pastel",
    SAT_PURE: "Pure",
}


class RuleLightingEntry:
    """
    RGB Indicator Rule Entry (8 bytes)

    Bit layout:
      Byte 0-1 (condition):
        Bit 0:    layer_enable (0 = any layer, 1 = match layer field)
        Bit 1:    caps_enable (0 = any caps state, 1 = caps must be ON)
        Bits 2-3: reserved
        Bits 4-7: layer (0-15)
        Bits 8-15: mods (modifier mask, 0 = any)

      Byte 2-3: keycode_start (full 16-bit range)
      Byte 4-5: keycode_end (full 16-bit range, inclusive)

      Byte 6 (color_idle):
        Bits 0-1: sat_idle
        Bits 2-7: h_idle (6-bit hue, use << 2 for 8-bit)

      Byte 7 (color_pressed):
        Bits 0-1: sat_pressed
        Bits 2-7: h_pressed (6-bit hue)
    """

    def __init__(self, data=None):
        if data is None:
            # Default: empty entry
            self.layer_enable = False
            self.caps_enable = False
            self.layer = 0
            self.mods = 0
            self.keycode_start = 0
            self.keycode_end = 0
            self.sat_idle = SAT_OFF
            self.h_idle = 0
            self.sat_pressed = SAT_OFF
            self.h_pressed = 0
        else:
            condition, keycode_start, keycode_end, color_idle, color_pressed = data

            # Parse condition (16 bits)
            self.layer_enable = bool(condition & 0x0001)
            self.caps_enable = bool(condition & 0x0002)
            self.layer = (condition >> 4) & 0x0F
            self.mods = (condition >> 8) & 0xFF

            # Keycodes - serialize to GUI format
            self.keycode_start = Keycode.serialize(keycode_start)
            self.keycode_end = Keycode.serialize(keycode_end)

            # Parse idle color (8 bits)
            self.sat_idle = color_idle & 0x03
            self.h_idle = (color_idle >> 2) & 0x3F

            # Parse pressed color (8 bits)
            self.sat_pressed = color_pressed & 0x03
            self.h_pressed = (color_pressed >> 2) & 0x3F

    def serialize(self):
        """Serializes into a vial_rule_lighting_entry_t object for firmware"""
        # Build condition word
        condition = 0
        condition |= int(self.layer_enable) << 0
        condition |= int(self.caps_enable) << 1
        condition |= (self.layer & 0x0F) << 4
        condition |= (self.mods & 0xFF) << 8

        # Build color bytes
        color_idle = (self.sat_idle & 0x03) | ((self.h_idle & 0x3F) << 2)
        color_pressed = (self.sat_pressed & 0x03) | ((self.h_pressed & 0x3F) << 2)

        return struct.pack("<HHHBB",
                           condition,
                           Keycode.deserialize(self.keycode_start),
                           Keycode.deserialize(self.keycode_end),
                           color_idle,
                           color_pressed)

    def is_empty(self):
        """Check if this entry is effectively empty/disabled"""
        return self.sat_idle == SAT_OFF and self.sat_pressed == SAT_OFF

    def __repr__(self):
        return (f"RuleLightingEntry<layer_en={self.layer_enable} caps_en={self.caps_enable} "
                f"layer={self.layer} mods=0x{self.mods:02X} "
                f"kc={self.keycode_start}-{self.keycode_end} "
                f"idle=({SAT_LABELS[self.sat_idle]},h={self.h_idle}) "
                f"pressed=({SAT_LABELS[self.sat_pressed]},h={self.h_pressed})>")

    def __eq__(self, other):
        return isinstance(other, RuleLightingEntry) and self.serialize() == other.serialize()

    def save(self):
        """Serializes into Vial layout file format"""
        return {
            "layer_enable": self.layer_enable,
            "caps_enable": self.caps_enable,
            "layer": self.layer,
            "mods": self.mods,
            "keycode_start": self.keycode_start,
            "keycode_end": self.keycode_end,
            "sat_idle": self.sat_idle,
            "h_idle": self.h_idle,
            "sat_pressed": self.sat_pressed,
            "h_pressed": self.h_pressed,
        }

    def restore(self, data):
        """Restores from a Vial layout file"""
        self.layer_enable = data.get("layer_enable", False)
        self.caps_enable = data.get("caps_enable", False)
        self.layer = data.get("layer", 0)
        self.mods = data.get("mods", 0)
        self.keycode_start = data.get("keycode_start", 0)
        self.keycode_end = data.get("keycode_end", 0)
        self.sat_idle = data.get("sat_idle", SAT_OFF)
        self.h_idle = data.get("h_idle", 0)
        self.sat_pressed = data.get("sat_pressed", SAT_OFF)
        self.h_pressed = data.get("h_pressed", 0)


class ProtocolRuleLighting(BaseProtocol):
    """Protocol mixin for Rule Lighting (RGB Indicator) communication"""

    rule_lighting_entries = None

    def reload_rule_lighting(self):
        """Load Rule Lighting entries from keyboard"""
        # Skip if no RGB indicator support
        if self.rule_lighting_count == 0:
            self.rule_lighting_entries = []
            return

        # Get entries
        entries = self._retrieve_dynamic_entries(
            DYNAMIC_VIAL_RULE_LIGHTING_GET_ENTRY,
            self.rule_lighting_count,
            "<HHHBB"
        )
        self.rule_lighting_entries = [RuleLightingEntry(e) for e in entries]

    def rule_lighting_get_entry(self, idx):
        return self.rule_lighting_entries[idx]

    def rule_lighting_set_entry(self, idx, entry):
        """Set entry at index and save to keyboard"""
        if entry != self.rule_lighting_entries[idx]:
            self.rule_lighting_entries[idx] = entry
            self.usb_send(
                self.dev,
                struct.pack("BBBB", CMD_VIA_VIAL_PREFIX, CMD_VIAL_DYNAMIC_ENTRY_OP,
                            DYNAMIC_VIAL_RULE_LIGHTING_SET_ENTRY, idx) + entry.serialize()
            )

    def save_rule_lighting(self):
        """Save Rule Lighting to Vial layout file"""
        if self.rule_lighting_count == 0:
            return {}

        return {
            "entries": [e.save() for e in self.rule_lighting_entries]
        }

    def restore_rule_lighting(self, data):
        """Restore Rule Lighting from Vial layout file"""
        if self.rule_lighting_count == 0 or not data:
            return

        # Ignore "config" if present (deprecated, from older layout files)
        if "entries" in data:
            for x, e_data in enumerate(data["entries"]):
                if x < self.rule_lighting_count:
                    entry = RuleLightingEntry()
                    entry.restore(e_data)
                    self.rule_lighting_set_entry(x, entry)
