# SPDX-License-Identifier: GPL-2.0-or-later

import struct
import json
import lzma

from kle_serial import Serial as KleSerial
from util import MSG_LEN, hid_send


class Keyboard:
    """ Low-level communication with a vial-enabled keyboard """

    def __init__(self, dev):
        self.dev = dev

    def reload(self):
        """ Load information about the keyboard: number of layers, physical key layout """

        self.rowcol = set()
        self.layout = dict()

        self.reload_layers()
        self.reload_layout()
        self.reload_keymap()

    def reload_layers(self):
        """ Get how many layers the keyboard has """

        self.layers = hid_send(self.dev, b"\x11")[1]

    def reload_layout(self):
        """ Requests layout data from the current device """

        # get the size
        data = hid_send(self.dev, b"\xFE\x01")
        sz = struct.unpack("<I", data[0:4])[0]

        # get the payload
        payload = b""
        block = 0
        while sz > 0:
            data = hid_send(self.dev, b"\xFE\x02" + struct.pack("<I", block))
            if sz < MSG_LEN:
                data = data[:sz]
            payload += data
            block += 1
            sz -= MSG_LEN

        payload = json.loads(lzma.decompress(payload))
        serial = KleSerial()
        kb = serial.deserialize(payload["layouts"]["keymap"])

        self.keys = kb.keys

        for key in self.keys:
            key.row = key.col = None
            if key.labels[0] and "," in key.labels[0]:
                row, col = key.labels[0].split(",")
                row, col = int(row), int(col)
                key.row = row
                key.col = col
                self.rowcol.add((row, col))

    def reload_keymap(self):
        """ Load current key mapping from the keyboard """

        for layer in range(self.layers):
            for row, col in self.rowcol:
                data = hid_send(self.dev, b"\x04" + struct.pack("<BBB", layer, row, col))
                keycode = struct.unpack(">H", data[4:6])[0]
                self.layout[(layer, row, col)] = keycode

    def set_key(self, layer, row, col, code):
        hid_send(self.dev, struct.pack(">BBBBH", 5, layer, row, col, code))
        self.layout[(layer, row, col)] = code
