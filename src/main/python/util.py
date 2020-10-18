# SPDX-License-Identifier: GPL-2.0-or-later

from PyQt5.QtCore import QCoreApplication

import sys

if sys.platform.startswith("linux"):
    import hidraw as hid
else:
    import hid


tr = QCoreApplication.translate

VIAL_SERIAL_NUMBER_MAGIC = "vial:f64c2b3c"

MSG_LEN = 32


def hid_send(dev, msg):
    if len(msg) > MSG_LEN:
        raise RuntimeError("message must be less than 32 bytes")
    msg += b"\x00" * (MSG_LEN - len(msg))

    # add 00 at start for hidapi report id
    dev.write(b"\x00" + msg)

    return bytes(dev.read(MSG_LEN))


def is_rawhid(dev):
    # TODO: this is only broken on linux, other platforms should be able to check usage_page
    return dev["interface_number"] == 1


def find_vial_keyboards(sideload_vid, sideload_pid):
    filtered = []
    for dev in hid.enumerate():
        if VIAL_SERIAL_NUMBER_MAGIC in dev["serial_number"] and is_rawhid(dev):
            filtered.append(dev)
        elif dev["vendor_id"] == sideload_vid and dev["product_id"] == sideload_pid and is_rawhid(dev):
            filtered.append(dev)
    return filtered


def open_device(desc):
    # TODO: error handling here
    dev = hid.device()
    dev.open_path(desc["path"])
    return dev
