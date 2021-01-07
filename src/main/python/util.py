# SPDX-License-Identifier: GPL-2.0-or-later

from PyQt5.QtCore import QCoreApplication

from hidproxy import hid


tr = QCoreApplication.translate

# For Vial keyboard
VIAL_SERIAL_NUMBER_MAGIC = "vial:f64c2b3c"

# For bootloader
VIBL_SERIAL_NUMBER_MAGIC = "vibl:d4f8159c"

MSG_LEN = 32


def hid_send(dev, msg, retries=1):
    if len(msg) > MSG_LEN:
        raise RuntimeError("message must be less than 32 bytes")
    msg += b"\x00" * (MSG_LEN - len(msg))

    data = b""

    while retries > 0:
        retries -= 1
        try:
            # add 00 at start for hidapi report id
            if dev.write(b"\x00" + msg) != MSG_LEN + 1:
                continue

            data = bytes(dev.read(MSG_LEN, timeout_ms=500))
            if not data:
                continue
        except OSError:
            continue
        break

    if not data:
        raise RuntimeError("failed to communicate with the device")
    return data


def is_rawhid(dev):
    # TODO: this is only broken on linux, other platforms should be able to check usage_page
    return dev["interface_number"] == 1


def find_vial_devices(sideload_vid=None, sideload_pid=None):
    from vial_device import VialBootloader, VialKeyboard

    filtered = []
    for dev in hid.enumerate():
        if dev["vendor_id"] == sideload_vid and dev["product_id"] == sideload_pid and is_rawhid(dev):
            filtered.append(VialKeyboard(dev, sideload=True))
        elif VIAL_SERIAL_NUMBER_MAGIC in dev["serial_number"] and is_rawhid(dev):
            filtered.append(VialKeyboard(dev))
        elif VIBL_SERIAL_NUMBER_MAGIC in dev["serial_number"]:
            filtered.append(VialBootloader(dev))

    return filtered


def chunks(data, sz):
    for i in range(0, len(data), sz):
        yield data[i:i+sz]


def pad_for_vibl(msg):
    """ Pads message to vibl fixed 64-byte length """
    if len(msg) > 64:
        raise RuntimeError("vibl message too long")
    return msg + b"\x00" * (64 - len(msg))
