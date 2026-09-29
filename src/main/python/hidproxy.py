# SPDX-License-Identifier: GPL-2.0-or-later
import struct
import sys
import threading

from protocol.constants import CMD_VIA_VIAL_PREFIX, CMD_VIAL_GET_KEYBOARD_ID

# hidapi's macOS backend shares one global IOHIDManager that hid_init schedules on the calling
# thread's run loop; initializing it from two threads at once aborts the process on macOS 27.
# Hold this lock around enumerate() and device opening.
hid_lock = threading.RLock()

if sys.platform == "emscripten":

    import vialglue
    import json

    class hiddevice:

        def open_path(self, path):
            print("opening {}...".format(path))

        def write(self, data):
            return vialglue.write_device(data)

        def read(self, length, timeout_ms=0):
            data = vialglue.read_device()
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
