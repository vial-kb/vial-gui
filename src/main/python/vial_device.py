# SPDX-License-Identifier: GPL-2.0-or-later
from hidproxy import hid
from keyboard import Keyboard


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

    def recv(self, length):
        return bytes(self.dev.read(length))

    def close(self):
        self.dev.close()


class VialKeyboard(VialDevice):

    def __init__(self, dev, sideload=False):
        super().__init__(dev)
        self.sideload = sideload
        self.keyboard = None

    def open(self, override_json=None):
        super().open(override_json)
        self.keyboard = Keyboard(self.dev)
        self.keyboard.reload(override_json)

    def title(self):
        s = "{} {}".format(self.desc["manufacturer_string"], self.desc["product_string"])
        if self.sideload:
            s += " [sideload]"
        return s


class VialBootloader(VialDevice):

    def title(self):
        return "Vial Bootloader [{:04X}:{:04X}]".format(self.desc["vendor_id"], self.desc["product_id"])
