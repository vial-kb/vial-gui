# SPDX-License-Identifier: GPL-2.0-or-later

import struct
import json
import lzma
from collections import OrderedDict

from kle_serial import Serial as KleSerial
from util import MSG_LEN, hid_send


CMD_VIA_GET_KEYCODE = 0x04
CMD_VIA_SET_KEYCODE = 0x05
CMD_VIA_GET_LAYER_COUNT = 0x11
CMD_VIA_VIAL_PREFIX = 0xFE

CMD_VIAL_GET_SIZE = 0x01
CMD_VIAL_GET_DEFINITION = 0x02


class Keyboard:
    """ Low-level communication with a vial-enabled keyboard """

    def __init__(self, dev, usb_send=hid_send):
        self.dev = dev
        self.usb_send = usb_send

        # n.b. using OrderedDict here to make order of layout requests consistent for tests
        self.rowcol = OrderedDict()
        self.layout = dict()
        self.layers = 0
        self.keys = []

    def reload(self):
        """ Load information about the keyboard: number of layers, physical key layout """

        self.rowcol = OrderedDict()
        self.layout = dict()

        self.reload_layout()
        self.reload_layers()
        self.reload_keymap()

    def reload_layers(self):
        """ Get how many layers the keyboard has """

        self.layers = self.usb_send(self.dev, struct.pack("B", CMD_VIA_GET_LAYER_COUNT))[1]

    def reload_layout(self):
        """ Requests layout data from the current device """

        # get the size
        data = self.usb_send(self.dev, struct.pack("BB", CMD_VIA_VIAL_PREFIX, CMD_VIAL_GET_SIZE))
        sz = struct.unpack("<I", data[0:4])[0]

        # get the payload
        payload = b""
        block = 0
        while sz > 0:
            data = self.usb_send(self.dev, struct.pack("<BBI", CMD_VIA_VIAL_PREFIX, CMD_VIAL_GET_DEFINITION, block))
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
                self.rowcol[(row, col)] = True

    def reload_keymap(self):
        """ Load current key mapping from the keyboard """

        for layer in range(self.layers):
            for row, col in self.rowcol.keys():
                data = self.usb_send(self.dev, struct.pack("BBBB", CMD_VIA_GET_KEYCODE, layer, row, col))
                keycode = struct.unpack(">H", data[4:6])[0]
                self.layout[(layer, row, col)] = keycode

    def set_key(self, layer, row, col, code):
        self.usb_send(self.dev, struct.pack(">BBBBH", CMD_VIA_SET_KEYCODE, layer, row, col, code))
        self.layout[(layer, row, col)] = code
