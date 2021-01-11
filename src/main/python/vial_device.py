# SPDX-License-Identifier: GPL-2.0-or-later
from hidproxy import hid
from keyboard_comm import Keyboard
from util import MSG_LEN, pad_for_vibl


class VialDevice:

    def __init__(self, dev):
        self.desc = dev
        self.dev = None
        self.sideload = False

    def open(self, override_json=None):
        # TODO: error handling here
        self.dev = hid.device()
        self.dev.open_path(self.desc["path"])

    def send(self, data):
        # add 00 at start for hidapi report id
        return self.dev.write(b"\x00" + data)

    def recv(self, length, timeout_ms=0):
        return bytes(self.dev.read(length, timeout_ms=timeout_ms))

    def close(self):
        self.dev.close()


class VialKeyboard(VialDevice):

    def __init__(self, dev, sideload=False, via_stack=False):
        super().__init__(dev)
        self.via_id = str(dev["vendor_id"] * 65536 + dev["product_id"])
        self.sideload = sideload
        self.via_stack = via_stack
        self.keyboard = None

    def open(self, override_json=None):
        super().open(override_json)
        self.keyboard = Keyboard(self.dev)
        self.keyboard.reload(override_json)

    def title(self):
        s = "{} {}".format(self.desc["manufacturer_string"], self.desc["product_string"])
        if self.sideload:
            s += " [sideload]"
        elif self.via_stack:
            s += " [VIA]"
        return s

    def get_uid(self):
        try:
            super().open()
        except OSError:
            return b""
        self.send(b"\xFE\x00" + b"\x00" * 30)
        data = self.recv(MSG_LEN, timeout_ms=500)
        super().close()
        return data[4:12]


class VialBootloader(VialDevice):

    def title(self):
        return "Vial Bootloader [{:04X}:{:04X}]".format(self.desc["vendor_id"], self.desc["product_id"])

    def get_uid(self):
        try:
            super().open()
        except OSError:
            return b""
        self.send(pad_for_vibl(b"VC\x01"))
        data = self.recv(8, timeout_ms=500)
        super().close()
        return data
