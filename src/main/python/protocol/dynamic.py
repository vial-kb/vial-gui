# SPDX-License-Identifier: GPL-2.0-or-later
import struct

from protocol.base_protocol import BaseProtocol
from protocol.constants import CMD_VIA_VIAL_PREFIX, CMD_VIAL_DYNAMIC_ENTRY_OP, DYNAMIC_VIAL_GET_NUMBER_OF_ENTRIES, \
    VIAL_PROTOCOL_DYNAMIC, VIAL_PROTOCOL_OPTIONAL_FEATURES


class ProtocolDynamic(BaseProtocol):

    def reload_dynamic(self):
        self.supported_features = set()

        if self.vial_protocol < VIAL_PROTOCOL_DYNAMIC:
            self.tap_dance_count = 0
            self.tap_dance_entries = []
            self.combo_count = 0
            self.combo_entries = []
            self.key_override_count = 0
            self.key_override_entries = []
            return
        data = self.usb_send(self.dev, struct.pack("BBB", CMD_VIA_VIAL_PREFIX, CMD_VIAL_DYNAMIC_ENTRY_OP,
                                                   DYNAMIC_VIAL_GET_NUMBER_OF_ENTRIES), retries=20)
        self.tap_dance_count = data[0]
        self.combo_count = data[1]
        self.key_override_count = data[2]

        if self.vial_protocol >= VIAL_PROTOCOL_OPTIONAL_FEATURES:
          # Bits of data[-1] indicate optionally supported features.
          for bit_index, feature in [
              (0, "caps_word"),
              (1, "layer_lock"),
              # Add more feature bits as needed...
          ]:
            if data[-1] & (1 << bit_index):
              self.supported_features.add(feature)

          # Persistent Default Layers isn't present in older QMK builds, but is
          # unconditionally enabled in recent QMK builds.
          self.supported_features.add("persistent_default_layer")
