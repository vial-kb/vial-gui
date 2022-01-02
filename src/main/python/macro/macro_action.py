# SPDX-License-Identifier: GPL-2.0-or-later
import struct

from keycodes import Keycode

SS_QMK_PREFIX = 1

SS_TAP_CODE = 1
SS_DOWN_CODE = 2
SS_UP_CODE = 3
SS_DELAY_CODE = 4


class BasicAction:

    tag = "unknown"

    def save(self):
        return [self.tag]

    def restore(self, act):
        if self.tag != act[0]:
            raise RuntimeError("cannot restore {}: expected tag={} got tag={}".format(
                self, self.tag, act[0]
            ))

    def __eq__(self, other):
        return self.tag == other.tag


class ActionText(BasicAction):

    tag = "text"

    def __init__(self, text=""):
        super().__init__()
        self.text = text

    def serialize(self, vial_protocol):
        return self.text.encode("utf-8")

    def save(self):
        return super().save() + [self.text]

    def restore(self, act):
        super().restore(act)
        self.text = act[1]

    def __eq__(self, other):
        return super().__eq__(other) and self.text == other.text


class ActionSequence(BasicAction):

    tag = "unknown-sequence"

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

    def save(self):
        out = super().save()
        for k in self.sequence:
            out.append(k.qmk_id)
        return out

    def restore(self, act):
        super().restore(act)
        for qmk_id in act[1:]:
            self.sequence.append(Keycode.find_by_qmk_id(qmk_id))

    def __eq__(self, other):
        return super().__eq__(other) and self.sequence == other.sequence


class ActionDown(ActionSequence):

    tag = "down"

    def serialize_prefix(self):
        return b"\x02"


class ActionUp(ActionSequence):

    tag = "up"

    def serialize_prefix(self):
        return b"\x03"


class ActionTap(ActionSequence):

    tag = "tap"

    def serialize_prefix(self):
        return b"\x01"


class ActionDelay(BasicAction):

    tag = "delay"

    def __init__(self, delay=0):
        super().__init__()
        self.delay = delay

    def serialize(self, vial_protocol):
        if vial_protocol < 2:
            raise RuntimeError("ActionDelay can only be used with vial_protocol>=2")
        delay = self.delay
        return struct.pack("BBBB", SS_QMK_PREFIX, SS_DELAY_CODE, (delay % 255) + 1, (delay // 255) + 1)

    def save(self):
        return super().save() + [self.delay]

    def restore(self, act):
        super().restore(act)
        self.delay = act[1]

    def __eq__(self, other):
        return super().__eq__(other) and self.delay == other.delay
