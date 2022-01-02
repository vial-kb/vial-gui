# SPDX-License-Identifier: GPL-2.0-or-later
import struct

from protocol.constants import CMD_VIA_VIAL_PREFIX, CMD_VIAL_DYNAMIC_ENTRY_OP


class BaseProtocol:
    vial_protocol = None
    usb_send = NotImplemented
    dev = None

    def _retrieve_dynamic_entries(self, cmd, count, fmt):
        out = []
        for x in range(count):
            data = self.usb_send(
                self.dev,
                struct.pack("BBBB", CMD_VIA_VIAL_PREFIX, CMD_VIAL_DYNAMIC_ENTRY_OP, cmd, x),
                retries=20
            )
            if data[0] != 0:
                raise RuntimeError("failed retrieving dynamic={} entry {} from the device".format(cmd, x))
            out.append(struct.unpack(fmt, data[1:1 + struct.calcsize(fmt)]))
        return out
