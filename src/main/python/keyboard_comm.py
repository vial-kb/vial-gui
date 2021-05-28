# SPDX-License-Identifier: GPL-2.0-or-later
import base64
import struct
import json
import lzma
from collections import OrderedDict

from keycodes import RESET_KEYCODE, Keycode
from kle_serial import Serial as KleSerial
from macro_action import SS_TAP_CODE, SS_DOWN_CODE, SS_UP_CODE, ActionText, ActionTap, ActionDown, ActionUp, \
    SS_QMK_PREFIX, SS_DELAY_CODE, ActionDelay
from unlocker import Unlocker
from util import MSG_LEN, hid_send, chunks

SUPPORTED_VIA_PROTOCOL = [-1, 9]
SUPPORTED_VIAL_PROTOCOL = [-1, 0, 1, 2, 3]

CMD_VIA_GET_PROTOCOL_VERSION = 0x01
CMD_VIA_GET_KEYBOARD_VALUE = 0x02
CMD_VIA_SET_KEYBOARD_VALUE = 0x03
CMD_VIA_GET_KEYCODE = 0x04
CMD_VIA_SET_KEYCODE = 0x05
CMD_VIA_LIGHTING_SET_VALUE = 0x07
CMD_VIA_LIGHTING_GET_VALUE = 0x08
CMD_VIA_LIGHTING_SAVE = 0x09
CMD_VIA_MACRO_GET_COUNT = 0x0C
CMD_VIA_MACRO_GET_BUFFER_SIZE = 0x0D
CMD_VIA_MACRO_GET_BUFFER = 0x0E
CMD_VIA_MACRO_SET_BUFFER = 0x0F
CMD_VIA_GET_LAYER_COUNT = 0x11
CMD_VIA_KEYMAP_GET_BUFFER = 0x12
CMD_VIA_VIAL_PREFIX = 0xFE

VIA_LAYOUT_OPTIONS = 0x02
VIA_SWITCH_MATRIX_STATE = 0x03

QMK_BACKLIGHT_BRIGHTNESS = 0x09
QMK_BACKLIGHT_EFFECT = 0x0A

QMK_RGBLIGHT_BRIGHTNESS = 0x80
QMK_RGBLIGHT_EFFECT = 0x81
QMK_RGBLIGHT_EFFECT_SPEED = 0x82
QMK_RGBLIGHT_COLOR = 0x83

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


class ProtocolError(Exception):
    pass


def macro_deserialize_v1(data):
    """
    Deserialize a single macro, protocol version 1
    """

    out = []
    sequence = []
    data = bytearray(data)
    while len(data) > 0:
        if data[0] in [SS_TAP_CODE, SS_DOWN_CODE, SS_UP_CODE]:
            # append to previous *_CODE if it's the same type, otherwise create a new entry
            if len(sequence) > 0 and isinstance(sequence[-1], list) and sequence[-1][0] == data[0]:
                sequence[-1][1].append(data[1])
            else:
                sequence.append([data[0], [data[1]]])

            data.pop(0)
            data.pop(0)
        else:
            # append to previous string if it is a string, otherwise create a new entry
            ch = chr(data[0])
            if len(sequence) > 0 and isinstance(sequence[-1], str):
                sequence[-1] += ch
            else:
                sequence.append(ch)
            data.pop(0)
    for s in sequence:
        if isinstance(s, str):
            out.append(ActionText(s))
        else:
            # map integer values to qmk keycodes
            keycodes = []
            for code in s[1]:
                keycode = Keycode.find_outer_keycode(code)
                if keycode:
                    keycodes.append(keycode)
            cls = {SS_TAP_CODE: ActionTap, SS_DOWN_CODE: ActionDown, SS_UP_CODE: ActionUp}[s[0]]
            out.append(cls(keycodes))
    return out


def macro_deserialize_v2(data):
    """
    Deserialize a single macro, protocol version 2
    """

    out = []
    sequence = []
    data = bytearray(data)
    while len(data) > 0:
        if data[0] == SS_QMK_PREFIX:
            if data[1] in [SS_TAP_CODE, SS_DOWN_CODE, SS_UP_CODE]:
                # append to previous *_CODE if it's the same type, otherwise create a new entry
                if len(sequence) > 0 and isinstance(sequence[-1], list) and sequence[-1][0] == data[1]:
                    sequence[-1][1].append(data[2])
                else:
                    sequence.append([data[1], [data[2]]])

                for x in range(3):
                    data.pop(0)
            elif data[1] == SS_DELAY_CODE:
                # decode the delay
                delay = (data[2] - 1) + (data[3] - 1) * 255
                sequence.append([SS_DELAY_CODE, delay])

                for x in range(4):
                    data.pop(0)
        else:
            # append to previous string if it is a string, otherwise create a new entry
            ch = chr(data[0])
            if len(sequence) > 0 and isinstance(sequence[-1], str):
                sequence[-1] += ch
            else:
                sequence.append(ch)
            data.pop(0)
    for s in sequence:
        if isinstance(s, str):
            out.append(ActionText(s))
        else:
            args = None
            if s[0] in [SS_TAP_CODE, SS_DOWN_CODE, SS_UP_CODE]:
                # map integer values to qmk keycodes
                args = []
                for code in s[1]:
                    keycode = Keycode.find_outer_keycode(code)
                    if keycode:
                        args.append(keycode)
            elif s[0] == SS_DELAY_CODE:
                args = s[1]

            if args is not None:
                cls = {SS_TAP_CODE: ActionTap, SS_DOWN_CODE: ActionDown, SS_UP_CODE: ActionUp,
                       SS_DELAY_CODE: ActionDelay}[s[0]]
                out.append(cls(args))
    return out


class Keyboard:
    """ Low-level communication with a vial-enabled keyboard """

    def __init__(self, dev, usb_send=hid_send):
        self.dev = dev
        self.usb_send = usb_send
        self.definition = None

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
        self.custom_keycodes = None

        self.lighting_qmk_rgblight = self.lighting_qmk_backlight = False
        self.underglow_brightness = self.underglow_effect = self.underglow_effect_speed = -1
        self.backlight_brightness = self.backlight_effect = -1
        self.underglow_color = (0, 0)

        self.via_protocol = self.vial_protocol = self.keyboard_id = -1

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
        self.reload_rgb()

    def reload_layers(self):
        """ Get how many layers the keyboard has """

        self.layers = self.usb_send(self.dev, struct.pack("B", CMD_VIA_GET_LAYER_COUNT), retries=20)[1]

    def reload_via_protocol(self):
        data = self.usb_send(self.dev, struct.pack("B", CMD_VIA_GET_PROTOCOL_VERSION), retries=20)
        self.via_protocol = struct.unpack(">H", data[1:3])[0]

    def check_protocol_version(self):
        if self.via_protocol not in SUPPORTED_VIA_PROTOCOL or self.vial_protocol not in SUPPORTED_VIAL_PROTOCOL:
            raise ProtocolError()

    def reload_layout(self, sideload_json=None):
        """ Requests layout data from the current device """

        self.reload_via_protocol()

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

        self.check_protocol_version()

        self.definition = payload

        if "vial" in payload:
            vial = payload["vial"]
            self.vibl = vial.get("vibl", False)

        self.layout_labels = payload["layouts"].get("labels")

        self.rows = payload["matrix"]["rows"]
        self.cols = payload["matrix"]["cols"]

        self.custom_keycodes = payload.get("customKeycodes", None)

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

    def reload_rgb(self):
        if "lighting" in self.definition:
            self.lighting_qmk_rgblight = self.definition["lighting"] in ["qmk_rgblight", "qmk_backlight_rgblight"]
            self.lighting_qmk_backlight = self.definition["lighting"] in ["qmk_backlight", "qmk_backlight_rgblight"]

        if self.lighting_qmk_rgblight:
            self.underglow_brightness = self.usb_send(
                self.dev, struct.pack(">BB", CMD_VIA_LIGHTING_GET_VALUE, QMK_RGBLIGHT_BRIGHTNESS), retries=20)[2]
            self.underglow_effect = self.usb_send(
                self.dev, struct.pack(">BB", CMD_VIA_LIGHTING_GET_VALUE, QMK_RGBLIGHT_EFFECT), retries=20)[2]
            self.underglow_effect_speed = self.usb_send(
                self.dev, struct.pack(">BB", CMD_VIA_LIGHTING_GET_VALUE, QMK_RGBLIGHT_EFFECT_SPEED), retries=20)[2]
            color = self.usb_send(
                self.dev, struct.pack(">BB", CMD_VIA_LIGHTING_GET_VALUE, QMK_RGBLIGHT_COLOR), retries=20)[2:4]
            # hue, sat
            self.underglow_color = (color[0], color[1])

        if self.lighting_qmk_backlight:
            self.backlight_brightness = self.usb_send(
                self.dev, struct.pack(">BB", CMD_VIA_LIGHTING_GET_VALUE, QMK_BACKLIGHT_BRIGHTNESS), retries=20)[2]
            self.backlight_effect = self.usb_send(
                self.dev, struct.pack(">BB", CMD_VIA_LIGHTING_GET_VALUE, QMK_BACKLIGHT_EFFECT), retries=20)[2]

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

    def set_qmk_rgblight_brightness(self, value):
        self.underglow_brightness = value
        self.usb_send(self.dev, struct.pack(">BBB", CMD_VIA_LIGHTING_SET_VALUE, QMK_RGBLIGHT_BRIGHTNESS, value),
                      retries=20)

    def set_qmk_rgblight_effect(self, index):
        self.underglow_effect = index
        self.usb_send(self.dev, struct.pack(">BBB", CMD_VIA_LIGHTING_SET_VALUE, QMK_RGBLIGHT_EFFECT, index),
                      retries=20)

    def set_qmk_rgblight_effect_speed(self, value):
        self.underglow_effect_speed = value
        self.usb_send(self.dev, struct.pack(">BBB", CMD_VIA_LIGHTING_SET_VALUE, QMK_RGBLIGHT_EFFECT_SPEED, value),
                      retries=20)

    def set_qmk_rgblight_color(self, h, s, v):
        self.set_qmk_rgblight_brightness(v)
        self.usb_send(self.dev, struct.pack(">BBBB", CMD_VIA_LIGHTING_SET_VALUE, QMK_RGBLIGHT_COLOR, h, s))

    def set_qmk_backlight_brightness(self, value):
        self.backlight_brightness = value
        self.usb_send(self.dev, struct.pack(">BBB", CMD_VIA_LIGHTING_SET_VALUE, QMK_BACKLIGHT_BRIGHTNESS, value))

    def set_qmk_backlight_effect(self, value):
        self.backlight_effect = value
        self.usb_send(self.dev, struct.pack(">BBB", CMD_VIA_LIGHTING_SET_VALUE, QMK_BACKLIGHT_EFFECT, value))

    def save_rgb(self):
        self.usb_send(self.dev, struct.pack(">B", CMD_VIA_LIGHTING_SAVE), retries=20)

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
        data["macro"] = self.save_macro()
        data["vial_protocol"] = self.vial_protocol
        data["via_protocol"] = self.via_protocol

        return json.dumps(data).encode("utf-8")

    def save_macro(self):
        macros = self.macros_deserialize(self.macro)
        out = []
        for macro in macros:
            out.append([act.save() for act in macro])
        return out

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
        self.restore_macros(data.get("macro"))

    def restore_macros(self, macros):
        if not isinstance(macros, list):
            return
        tag_to_action = {
            "down": ActionDown,
            "up": ActionUp,
            "tap": ActionTap,
            "text": ActionText,
            "delay": ActionDelay,
        }
        full_macro = []
        for macro in macros:
            actions = []
            for act in macro:
                if act[0] in tag_to_action:
                    obj = tag_to_action[act[0]]()
                    obj.restore(act)
                    actions.append(obj)
            full_macro.append(actions)
        if len(full_macro) < self.macro_count:
            full_macro += [[] for x in range(self.macro_count - len(full_macro))]
        full_macro = full_macro[:self.macro_count]
        # TODO: log a warning if macro is cutoff
        data = self.macros_serialize(full_macro)[0:self.macro_memory]
        if data != self.macro:
            Unlocker.unlock(self)
            self.set_macro(data)
            self.lock()

    def reset(self):
        self.usb_send(self.dev, struct.pack("B", 0xB))
        self.dev.close()

    def get_uid(self):
        """ Retrieve UID from the keyboard, explicitly sending a query packet """
        data = self.usb_send(self.dev, struct.pack("BB", CMD_VIA_VIAL_PREFIX, CMD_VIAL_GET_KEYBOARD_ID), retries=20)
        keyboard_id = data[4:12]
        return keyboard_id

    def get_unlock_status(self, retries=20):
        # VIA keyboards are always unlocked
        if self.vial_protocol < 0:
            return 1

        data = self.usb_send(self.dev, struct.pack("BB", CMD_VIA_VIAL_PREFIX, CMD_VIAL_GET_UNLOCK_STATUS),
                             retries=retries)
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

    def matrix_poll(self):
        if self.via_protocol < 0:
            return

        data = self.usb_send(self.dev, struct.pack("BB", CMD_VIA_GET_KEYBOARD_VALUE, VIA_SWITCH_MATRIX_STATE), retries=20)
        return data

    def macro_serialize(self, macro):
        """
        Serialize a single macro, a macro is made out of macro actions (BasicAction)
        """
        out = b""
        for action in macro:
            out += action.serialize(self.vial_protocol)
        return out

    def macro_deserialize(self, data):
        """
        Deserialize a single macro
        """
        if self.vial_protocol >= 2:
            return macro_deserialize_v2(data)
        return macro_deserialize_v1(data)

    def macros_serialize(self, macros):
        """
        Serialize a list of macros, the list must contain all macros (macro_count)
        """
        if len(macros) != self.macro_count:
            raise RuntimeError("expected array with {} macros, got {} macros".format(self.macro_count, len(macros)))
        out = [self.macro_serialize(macro) for macro in macros]
        return b"\x00".join(out) + b"\x00"

    def macros_deserialize(self, data):
        """
        Deserialize a list of macros
        """
        macros = data.split(b"\x00")
        if len(macros) < self.macro_count:
            macros += [b""] * (self.macro_count - len(macros))
        macros = macros[:self.macro_count]
        return [self.macro_deserialize(x) for x in macros]


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

    def reload_via_protocol(self):
        pass
