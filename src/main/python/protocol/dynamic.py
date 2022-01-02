# SPDX-License-Identifier: GPL-2.0-or-later
import struct

from protocol.base_protocol import BaseProtocol
from protocol.constants import CMD_VIA_VIAL_PREFIX, CMD_VIAL_DYNAMIC_ENTRY_OP, DYNAMIC_VIAL_GET_NUMBER_OF_ENTRIES


class ProtocolDynamic(BaseProtocol):

    def reload_dynamic(self):
        if self.vial_protocol < 4:
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
