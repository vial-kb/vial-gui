# SPDX-License-Identifier: GPL-2.0-or-later
import struct

SS_QMK_PREFIX = 1

SS_TAP_CODE = 1
SS_DOWN_CODE = 2
SS_UP_CODE = 3
SS_DELAY_CODE = 4


class BasicAction:
    pass


class ActionText(BasicAction):

    def __init__(self, text=""):
        super().__init__()
        self.text = text

    def serialize(self, vial_protocol):
        return self.text.encode("utf-8")


class ActionSequence(BasicAction):

    def __init__(self, sequence=None):
        super().__init__()
        if sequence is None:
            sequence = []
        self.sequence = sequence

    def serialize_prefix(self):
        raise NotImplementedError

    def serialize(self, vial_protocol):
        out = b""
        for k in self.sequence:
            if vial_protocol >= 2:
                out += struct.pack("B", SS_QMK_PREFIX)
            out += self.serialize_prefix()
            out += struct.pack("B", k.code)
        return out


class ActionDown(ActionSequence):

    def serialize_prefix(self):
        return b"\x02"


class ActionUp(ActionSequence):

    def serialize_prefix(self):
        return b"\x03"


class ActionTap(ActionSequence):

    def serialize_prefix(self):
        return b"\x01"


class ActionDelay(BasicAction):

    def __init__(self, delay=0):
        super().__init__()
        self.delay = delay

    def serialize(self, vial_protocol):
        if vial_protocol < 2:
            raise RuntimeError("ActionDelay can only be used with vial_protocol>=2")
        delay = self.delay
        return struct.pack("BBBB", SS_QMK_PREFIX, SS_DELAY_CODE, (delay % 255) + 1, (delay // 255) + 1)
