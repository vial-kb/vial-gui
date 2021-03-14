# SPDX-License-Identifier: GPL-2.0-or-later
import base64
import struct
import json
import lzma
from collections import OrderedDict

from keycodes import RESET_KEYCODE, Keycode
from kle_serial import Serial as KleSerial
from unlocker import Unlocker
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
CMD_VIA_KEYMAP_GET_BUFFER = 0x12
CMD_VIA_VIAL_PREFIX = 0xFE

VIA_LAYOUT_OPTIONS = 0x02

CMD_VIAL_GET_KEYBOARD_ID = 0x00
CMD_VIAL_GET_SIZE = 0x01
CMD_VIAL_GET_DEFINITION = 0x02
CMD_VIAL_GET_ENCODER = 0x03
CMD_VIAL_SET_ENCODER = 0x04
CMD_VIAL_GET_UNLOCK_STATUS = 0x05
CMD_VIAL_UNLOCK_START = 0x06
CMD_VIAL_UNLOCK_POLL = 0x07
CMD_VIAL_LOCK = 0x08

# how much of a macro/keymap buffer we can read/write per packet
BUFFER_FETCH_CHUNK = 28


class Keyboard:
    """ Low-level communication with a vial-enabled keyboard """

    def __init__(self, dev, usb_send=hid_send):
        self.dev = dev
        self.usb_send = usb_send

        # n.b. using OrderedDict here to make order of layout requests consistent for tests
        self.rowcol = OrderedDict()
        self.encoderpos = OrderedDict()
        self.encoder_count = 0
        self.layout = dict()
        self.encoder_layout = dict()
        self.rows = self.cols = self.layers = 0
        self.layout_labels = None
        self.layout_options = -1
        self.keys = []
        self.encoders = []
        self.macro_count = 0
        self.macro_memory = 0
        self.macro = b""
        self.vibl = False

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

        self.layers = self.usb_send(self.dev, struct.pack("B", CMD_VIA_GET_LAYER_COUNT), retries=20)[1]

    def reload_layout(self, sideload_json=None):
        """ Requests layout data from the current device """

        if sideload_json is not None:
            payload = sideload_json
        else:
            # get keyboard identification
            data = self.usb_send(self.dev, struct.pack("BB", CMD_VIA_VIAL_PREFIX, CMD_VIAL_GET_KEYBOARD_ID), retries=20)
            self.vial_protocol, self.keyboard_id = struct.unpack("<IQ", data[0:12])

            # get the size
            data = self.usb_send(self.dev, struct.pack("BB", CMD_VIA_VIAL_PREFIX, CMD_VIAL_GET_SIZE), retries=20)
            sz = struct.unpack("<I", data[0:4])[0]

            # get the payload
            payload = b""
            block = 0
            while sz > 0:
                data = self.usb_send(self.dev, struct.pack("<BBI", CMD_VIA_VIAL_PREFIX, CMD_VIAL_GET_DEFINITION, block),
                                     retries=20)
                if sz < MSG_LEN:
                    data = data[:sz]
                payload += data
                block += 1
                sz -= MSG_LEN

            payload = json.loads(lzma.decompress(payload))

        if "vial" in payload:
            vial = payload["vial"]
            self.vibl = vial.get("vibl", False)

        self.layout_labels = payload["layouts"].get("labels")

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
                self.encoder_count = max(self.encoder_count, idx + 1)
                self.encoders.append(key)
            elif key.labels[0] and "," in key.labels[0]:
                row, col = key.labels[0].split(",")
                row, col = int(row), int(col)
                key.row = row
                key.col = col
                self.rowcol[(row, col)] = True
                self.keys.append(key)

            # bottom right corner determines layout index and option in this layout
            key.layout_index = -1
            key.layout_option = -1
            if key.labels[8]:
                idx, opt = key.labels[8].split(",")
                key.layout_index, key.layout_option = int(idx), int(opt)

    def reload_keymap(self):
        """ Load current key mapping from the keyboard """

        keymap = b""
        # calculate what the size of keymap will be and retrieve the entire binary buffer
        size = self.layers * self.rows * self.cols * 2
        for x in range(0, size, BUFFER_FETCH_CHUNK):
            offset = x
            sz = min(size - offset, BUFFER_FETCH_CHUNK)
            data = self.usb_send(self.dev, struct.pack(">BHB", CMD_VIA_KEYMAP_GET_BUFFER, offset, sz), retries=20)
            keymap += data[4:4+sz]

        for layer in range(self.layers):
            for row, col in self.rowcol.keys():
                if row >= self.rows or col >= self.cols:
                    raise RuntimeError("malformed vial.json, key references {},{} but matrix declares rows={} cols={}"
                                       .format(row, col, self.rows, self.cols))
                # determine where this (layer, row, col) will be located in keymap array
                offset = layer * self.rows * self.cols * 2 + row * self.cols * 2 + col * 2
                keycode = struct.unpack(">H", keymap[offset:offset+2])[0]
                self.layout[(layer, row, col)] = keycode

        for layer in range(self.layers):
            for idx in self.encoderpos:
                data = self.usb_send(self.dev, struct.pack("BBBB", CMD_VIA_VIAL_PREFIX, CMD_VIAL_GET_ENCODER, layer, idx),
                                     retries=20)
                self.encoder_layout[(layer, idx, 0)] = struct.unpack(">H", data[0:2])[0]
                self.encoder_layout[(layer, idx, 1)] = struct.unpack(">H", data[2:4])[0]

        if self.layout_labels:
            data = self.usb_send(self.dev, struct.pack("BB", CMD_VIA_GET_KEYBOARD_VALUE, VIA_LAYOUT_OPTIONS),
                                 retries=20)
            self.layout_options = struct.unpack(">I", data[2:6])[0]

    def reload_macros(self):
        """ Loads macro information from the keyboard """
        data = self.usb_send(self.dev, struct.pack("B", CMD_VIA_MACRO_GET_COUNT), retries=20)
        self.macro_count = data[1]
        data = self.usb_send(self.dev, struct.pack("B", CMD_VIA_MACRO_GET_BUFFER_SIZE), retries=20)
        self.macro_memory = struct.unpack(">H", data[1:3])[0]

        self.macro = b""
        if self.macro_memory:
            # now retrieve the entire buffer, MACRO_CHUNK bytes at a time, as that is what fits into a packet
            for x in range(0, self.macro_memory, BUFFER_FETCH_CHUNK):
                sz = min(BUFFER_FETCH_CHUNK, self.macro_memory - x)
                data = self.usb_send(self.dev, struct.pack(">BHB", CMD_VIA_MACRO_GET_BUFFER, x, sz), retries=20)
                self.macro += data[4:4+sz]
            # macros are stored as NUL-separated strings, so let's clean up the buffer
            # ensuring we only get macro_count strings after we split by NUL
            macros = self.macro.split(b"\x00") + [b""] * self.macro_count
            self.macro = b"\x00".join(macros[:self.macro_count]) + b"\x00"

    def set_key(self, layer, row, col, code):
        if code < 0:
            return

        key = (layer, row, col)
        if self.layout[key] != code:
            if code == RESET_KEYCODE:
                Unlocker.unlock(self)

            self.usb_send(self.dev, struct.pack(">BBBBH", CMD_VIA_SET_KEYCODE, layer, row, col, code), retries=20)
            self.layout[key] = code

    def set_encoder(self, layer, index, direction, code):
        if code < 0:
            return

        key = (layer, index, direction)
        if self.encoder_layout[key] != code:
            if code == RESET_KEYCODE:
                Unlocker.unlock(self)

            self.usb_send(self.dev, struct.pack(">BBBBBH", CMD_VIA_VIAL_PREFIX, CMD_VIAL_SET_ENCODER,
                                                layer, index, direction, code), retries=20)
            self.encoder_layout[key] = code

    def set_layout_options(self, options):
        if self.layout_options != -1 and self.layout_options != options:
            self.layout_options = options
            self.usb_send(self.dev, struct.pack(">BBI", CMD_VIA_SET_KEYBOARD_VALUE, VIA_LAYOUT_OPTIONS, options),
                          retries=20)

    def set_macro(self, data):
        if len(data) > self.macro_memory:
            raise RuntimeError("the macro is too big: got {} max {}".format(len(data), self.macro_memory))

        for x, chunk in enumerate(chunks(data, BUFFER_FETCH_CHUNK)):
            off = x * BUFFER_FETCH_CHUNK
            self.usb_send(self.dev, struct.pack(">BHB", CMD_VIA_MACRO_SET_BUFFER, off, len(chunk)) + chunk,
                          retries=20)
        self.macro = data

    def save_layout(self):
        """ Serializes current layout to a binary """

        data = {"version": 1, "uid": self.keyboard_id}

        layout = []
        for l in range(self.layers):
            layer = []
            layout.append(layer)
            for r in range(self.rows):
                row = []
                layer.append(row)
                for c in range(self.cols):
                    val = self.layout.get((l, r, c), -1)
                    row.append(Keycode.serialize(val))

        encoder_layout = []
        for l in range(self.layers):
            layer = []
            for e in range(self.encoder_count):
                cw = (l, e, 0)
                ccw = (l, e, 1)
                layer.append([Keycode.serialize(self.encoder_layout.get(cw, -1)),
                              Keycode.serialize(self.encoder_layout.get(ccw, -1))])
            encoder_layout.append(layer)

        data["layout"] = layout
        data["encoder_layout"] = encoder_layout
        data["layout_options"] = self.layout_options
        # TODO: macros should be serialized in a portable format instead of base64 string
        # i.e. use a custom structure (as keycodes numbers can change, etc)
        data["macro"] = base64.b64encode(self.macro).decode("utf-8")

        return json.dumps(data).encode("utf-8")

    def restore_layout(self, data):
        """ Restores saved layout """

        data = json.loads(data.decode("utf-8"))

        # restore keymap
        for l, layer in enumerate(data["layout"]):
            for r, row in enumerate(layer):
                for c, code in enumerate(row):
                    if (l, r, c) in self.layout:
                        self.set_key(l, r, c, Keycode.deserialize(code))

        # restore encoders
        for l, layer in enumerate(data["encoder_layout"]):
            for e, encoder in enumerate(layer):
                self.set_encoder(l, e, 0, Keycode.deserialize(encoder[0]))
                self.set_encoder(l, e, 1, Keycode.deserialize(encoder[1]))

        self.set_layout_options(data["layout_options"])

        # we need to unlock the keyboard before we can restore the macros, lock it afterwards
        # only do that if it's different from current macros
        macro = base64.b64decode(data["macro"])
        if macro != self.macro:
            Unlocker.unlock(self)
            self.set_macro(macro)
            self.lock()

    def reset(self):
        self.usb_send(self.dev, struct.pack("B", 0xB))
        self.dev.close()

    def get_uid(self):
        """ Retrieve UID from the keyboard, explicitly sending a query packet """
        data = self.usb_send(self.dev, struct.pack("BB", CMD_VIA_VIAL_PREFIX, CMD_VIAL_GET_KEYBOARD_ID), retries=20)
        keyboard_id = data[4:12]
        return keyboard_id

    def get_unlock_status(self):
        # VIA keyboards are always unlocked
        if self.vial_protocol < 0:
            return 1

        data = self.usb_send(self.dev, struct.pack("BB", CMD_VIA_VIAL_PREFIX, CMD_VIAL_GET_UNLOCK_STATUS), retries=20)
        return data[0]

    def get_unlock_in_progress(self):
        # VIA keyboards are never being unlocked
        if self.vial_protocol < 0:
            return 0

        data = self.usb_send(self.dev, struct.pack("BB", CMD_VIA_VIAL_PREFIX, CMD_VIAL_GET_UNLOCK_STATUS), retries=20)
        return data[1]

    def get_unlock_keys(self):
        """ Return keys users have to hold to unlock the keyboard as a list of rowcols """

        # VIA keyboards don't have unlock keys
        if self.vial_protocol < 0:
            return []

        data = self.usb_send(self.dev, struct.pack("BB", CMD_VIA_VIAL_PREFIX, CMD_VIAL_GET_UNLOCK_STATUS), retries=20)
        rowcol = []
        for x in range(15):
            row = data[2 + x * 2]
            col = data[3 + x * 2]
            if row != 255 and col != 255:
                rowcol.append((row, col))
        return rowcol

    def unlock_start(self):
        if self.vial_protocol < 0:
            return

        self.usb_send(self.dev, struct.pack("BB", CMD_VIA_VIAL_PREFIX, CMD_VIAL_UNLOCK_START), retries=20)

    def unlock_poll(self):
        if self.vial_protocol < 0:
            return b""

        data = self.usb_send(self.dev, struct.pack("BB", CMD_VIA_VIAL_PREFIX, CMD_VIAL_UNLOCK_POLL), retries=20)
        return data

    def lock(self):
        if self.vial_protocol < 0:
            return

        self.usb_send(self.dev, struct.pack("BB", CMD_VIA_VIAL_PREFIX, CMD_VIAL_LOCK), retries=20)


class DummyKeyboard(Keyboard):

    def reload_layers(self):
        self.layers = 4

    def reload_keymap(self):
        for layer in range(self.layers):
            for row, col in self.rowcol.keys():
                self.layout[(layer, row, col)] = 0

        for layer in range(self.layers):
            for idx in self.encoderpos:
                self.encoder_layout[(layer, idx, 0)] = 0
                self.encoder_layout[(layer, idx, 1)] = 0

        if self.layout_labels:
            self.layout_options = 0

    def reload_macros(self):
        self.macro_count = 16
        self.macro_memory = 900

        self.macro = b"\x00" * self.macro_count

    def set_key(self, layer, row, col, code):
        if code < 0:
            return
        self.layout[(layer, row, col)] = code

    def set_encoder(self, layer, index, direction, code):
        if code < 0:
            return
        self.encoder_layout[(layer, index, direction)] = code

    def set_layout_options(self, options):
        if self.layout_options != -1 and self.layout_options != options:
            self.layout_options = options

    def set_macro(self, data):
        if len(data) > self.macro_memory:
            raise RuntimeError("the macro is too big: got {} max {}".format(len(data), self.macro_memory))
        self.macro = data

    def reset(self):
        pass

    def get_uid(self):
        return b"\x00" * 8

    def get_unlock_status(self):
        return 1

    def get_unlock_in_progress(self):
        return 0

    def get_unlock_keys(self):
        return []

    def unlock_start(self):
        return

    def unlock_poll(self):
        return b""

    def lock(self):
        return
