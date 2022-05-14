# SPDX-License-Identifier: GPL-2.0-or-later
import struct
import sys

from protocol.constants import CMD_VIA_VIAL_PREFIX, CMD_VIAL_GET_KEYBOARD_ID

if sys.platform == "emscripten":

    import vialglue
    import json

    class hiddevice:

        def open_path(self, path):
            print("opening {}...".format(path))

        def write(self, data):
            print("WRITE {}".format(data.hex()))
            return vialglue.write_device(data)

        def read(self, length, timeout_ms=0):
            data = vialglue.read_device()
            print("READ {}".format(data.hex()))
            return data


    class hid:

        @staticmethod
        def enumerate():
            from util import hid_send

            desc = json.loads(vialglue.get_device_desc())
            # hack: we don't know if it's vial or VIA device because webhid doesn't expose serial number
            # so let's probe it with a vial command, and if the response looks good, inject fake vial serial number
            # in the device descriptor
            dev = hid.device()
            data = hid_send(dev, struct.pack("BB", CMD_VIA_VIAL_PREFIX, CMD_VIAL_GET_KEYBOARD_ID), retries=20)
            uid = data[4:12]
            # here, a VIA keyboard will echo back all zeroes, while vial will return a valid UID
            # so if this looks like vial, inject the serial numebr
            if uid != b"\x00" * 8:
                desc["serial_number"] = "vial:f64c2b3c"
            return [desc]

        @staticmethod
        def device():
            return hiddevice()

elif sys.platform.startswith("linux"):
    import hidraw as hid
else:
    import hid
