# SPDX-License-Identifier: GPL-2.0-or-later
from protocol.base_protocol import BaseProtocol
from protocol.constants import DYNAMIC_VIAL_KEY_OVERRIDE_GET


class KeyOverride:
    pass


class ProtocolKeyOverride(BaseProtocol):

    def reload_key_override(self):
        self.key_override_entries = self._retrieve_dynamic_entries(DYNAMIC_VIAL_KEY_OVERRIDE_GET,
                                                                   self.key_override_count, "<HHHBBBB")
