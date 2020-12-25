# SPDX-License-Identifier: GPL-2.0-or-later

import struct
import json
import lzma
from collections import OrderedDict

from kle_serial import Serial as KleSerial
from util import MSG_LEN, hid_send, chunks

CMD_VIA_GET_KEYBOARD_VALUE = 0x02
CMD_VIA_SET_KEYBOARD_VALUE = 0x03
CMD_VIA_GET_KEYCODE = 0x04
CMD_VIA_SET_KEYCODE = 0x05
CMD_VIA_MACRO_GET_COUNT = 0x0C
CMD_VIA_MACRO_GET_BUFFER_SIZE = 0x0D
CMD_VIA_MACRO_GET_BUFFER = 0x0E
CMD_VIA_MACRO_SET_BUFFER = 0x0F
CMD_VIA_GET_LAYER_COUNT = 0x11
CMD_VIA_VIAL_PREFIX = 0xFE

VIA_LAYOUT_OPTIONS = 0x02

CMD_VIAL_GET_KEYBOARD_ID = 0x00
CMD_VIAL_GET_SIZE = 0x01
CMD_VIAL_GET_DEFINITION = 0x02
CMD_VIAL_GET_ENCODER = 0x03
CMD_VIAL_SET_ENCODER = 0x04
CMD_VIAL_GET_KEYMAP_FAST = 0x05

# how much of a macro we can read/write per packet
MACRO_CHUNK = 28


class Keyboard:
    """ Low-level communication with a vial-enabled keyboard """

    def __init__(self, dev, usb_send=hid_send):
        self.dev = dev
        self.usb_send = usb_send

        # n.b. using OrderedDict here to make order of layout requests consistent for tests
        self.rowcol = OrderedDict()
        self.encoderpos = OrderedDict()
        self.layout = dict()
        self.encoder_layout = dict()
        self.rows = self.cols = self.layers = 0
        self.layouts = None
        self.layout_options = -1
        self.keys = []
        self.encoders = []
        self.sideload = False
        self.macro_count = 0
        self.macro_memory = 0
        self.macro = b""

        self.vial_protocol = self.keyboard_id = -1

    def reload(self, sideload_json=None):
        """ Load information about the keyboard: number of layers, physical key layout """

        self.rowcol = OrderedDict()
        self.encoderpos = OrderedDict()
        self.layout = dict()
        self.encoder_layout = dict()

        self.reload_layout(sideload_json)
        self.reload_layers()
        self.reload_keymap()
        self.reload_macros()

    def reload_layers(self):
        """ Get how many layers the keyboard has """

        self.layers = self.usb_send(self.dev, struct.pack("B", CMD_VIA_GET_LAYER_COUNT))[1]

    def reload_layout(self, sideload_json=None):
        """ Requests layout data from the current device """

        if sideload_json is not None:
            payload = sideload_json
            self.sideload = True
        else:
            # get keyboard identification
            data = self.usb_send(self.dev, struct.pack("BB", CMD_VIA_VIAL_PREFIX, CMD_VIAL_GET_KEYBOARD_ID))
            self.vial_protocol, self.keyboard_id = struct.unpack("<IQ", data[0:12])

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

        self.layouts = payload.get("layouts")

        self.rows = payload["matrix"]["rows"]
        self.cols = payload["matrix"]["cols"]

        serial = KleSerial()
        kb = serial.deserialize(payload["layouts"]["keymap"])

        self.keys = []
        self.encoders = []

        for key in kb.keys:
            key.row = key.col = None
            key.encoder_idx = key.encoder_dir = None
            if key.labels[4] == "e":
                idx, direction = key.labels[0].split(",")
                idx, direction = int(idx), int(direction)
                key.encoder_idx = idx
                key.encoder_dir = direction
                self.encoderpos[idx] = True
                self.encoders.append(key)
            elif key.labels[0] and "," in key.labels[0]:
                row, col = key.labels[0].split(",")
                row, col = int(row), int(col)
                key.row = row
                key.col = col
                self.rowcol.setdefault(row, []).append(col)
                self.keys.append(key)

            # bottom right corner determines layout index and option in this layout
            key.layout_index = -1
            key.layout_option = -1
            if key.labels[8]:
                idx, opt = key.labels[8].split(",")
                key.layout_index, key.layout_option = int(idx), int(opt)

    def reload_keymap(self):
        """ Load current key mapping from the keyboard """

        for layer in range(self.layers):
            for row, cols in self.rowcol.items():
                # if this is a sideload, we have to assume it's a VIA keyboard
                # and does not support fast keymap retrieval
                if self.sideload:
                    for col in cols:
                        data = self.usb_send(self.dev, struct.pack("BBBB", CMD_VIA_GET_KEYCODE, layer, row, col))
                        keycode = struct.unpack(">H", data[4:6])[0]
                        self.layout[(layer, row, col)] = keycode
                else:
                    for chunk in chunks(cols, 16):
                        req = struct.pack("BBBB", CMD_VIA_VIAL_PREFIX, CMD_VIAL_GET_KEYMAP_FAST, layer, row)
                        for col in chunk:
                            req += struct.pack("B", col)
                        req += b"\xFF" * (MSG_LEN - len(req))

                        data = self.usb_send(self.dev, req)
                        for x, col in enumerate(chunk):
                            keycode = struct.unpack(">H", data[x*2:x*2+2])[0]
                            self.layout[(layer, row, col)] = keycode

        for layer in range(self.layers):
            for idx in self.encoderpos:
                data = self.usb_send(self.dev, struct.pack("BBBB", CMD_VIA_VIAL_PREFIX, CMD_VIAL_GET_ENCODER, layer, idx))
                self.encoder_layout[(layer, idx, 0)] = struct.unpack(">H", data[0:2])[0]
                self.encoder_layout[(layer, idx, 1)] = struct.unpack(">H", data[2:4])[0]

        if self.layouts:
            data = self.usb_send(self.dev, struct.pack("BB", CMD_VIA_GET_KEYBOARD_VALUE, VIA_LAYOUT_OPTIONS))
            self.layout_options = struct.unpack(">I", data[2:6])[0]

    def reload_macros(self):
        """ Loads macro information from the keyboard """
        data = self.usb_send(self.dev, struct.pack("B", CMD_VIA_MACRO_GET_COUNT))
        self.macro_count = data[1]
        data = self.usb_send(self.dev, struct.pack("B", CMD_VIA_MACRO_GET_BUFFER_SIZE))
        self.macro_memory = struct.unpack(">H", data[1:3])[0]

        self.macro = b""
        # now retrieve the entire buffer, MACRO_CHUNK bytes at a time, as that is what fits into a packet
        for x in range(0, self.macro_memory, MACRO_CHUNK):
            sz = min(MACRO_CHUNK, self.macro_memory - x)
            data = self.usb_send(self.dev, struct.pack(">BHB", CMD_VIA_MACRO_GET_BUFFER, x, sz))
            self.macro += data[4:4+sz]
        # macros are stored as NUL-separated strings, so let's clean up the buffer
        # ensuring we only get macro_count strings after we split by NUL
        macros = self.macro.split(b"\x00") + [b""] * self.macro_count
        self.macro = b"\x00".join(macros[:self.macro_count]) + b"\x00"

    def set_key(self, layer, row, col, code):
        key = (layer, row, col)
        if self.layout[key] != code:
            self.usb_send(self.dev, struct.pack(">BBBBH", CMD_VIA_SET_KEYCODE, layer, row, col, code))
            self.layout[key] = code

    def set_encoder(self, layer, index, direction, code):
        key = (layer, index, direction)
        if self.encoder_layout[key] != code:
            self.usb_send(self.dev, struct.pack(">BBBBBH", CMD_VIA_VIAL_PREFIX, CMD_VIAL_SET_ENCODER,
                                                layer, index, direction, code))
            self.encoder_layout[key] = code

    def set_layout_options(self, options):
        if self.layout_options != -1 and self.layout_options != options:
            self.layout_options = options
            self.usb_send(self.dev, struct.pack(">BBI", CMD_VIA_SET_KEYBOARD_VALUE, VIA_LAYOUT_OPTIONS, options))

    def set_macro(self, data):
        if len(data) > self.macro_memory:
            raise RuntimeError("the macro is too big: got {} max {}".format(len(data), self.macro_memory))

        for x, chunk in enumerate(chunks(data, MACRO_CHUNK)):
            off = x * MACRO_CHUNK
            self.usb_send(self.dev, struct.pack(">BHB", CMD_VIA_MACRO_SET_BUFFER, off, len(chunk)) + chunk)
        self.macro = data

    def save_layout(self):
        """ Serializes current layout to a binary """

        # TODO: increase version before release
        data = {"version": 0}
        layout = []
        for l in range(self.layers):
            layer = []
            layout.append(layer)
            for r in range(self.rows):
                row = []
                layer.append(row)
                for c in range(self.cols):
                    val = self.layout.get((l, r, c), -1)
                    row.append(val)
        data["layout"] = layout
        # TODO: this should also save/restore macros, when implemented
        return json.dumps(data).encode("utf-8")

    def restore_layout(self, data):
        """ Restores saved layout """

        data = json.loads(data.decode("utf-8"))
        for l, layer in enumerate(data["layout"]):
            for r, row in enumerate(layer):
                for c, col in enumerate(row):
                    if (l, r, c) in self.layout:
                        self.set_key(l, r, c, col)
