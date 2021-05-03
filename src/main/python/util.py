# SPDX-License-Identifier: GPL-2.0-or-later
import logging
import os
import time
from logging.handlers import RotatingFileHandler

from PyQt5.QtCore import QCoreApplication, QStandardPaths

from hidproxy import hid


tr = QCoreApplication.translate

# For Vial keyboard
VIAL_SERIAL_NUMBER_MAGIC = "vial:f64c2b3c"

# For bootloader
VIBL_SERIAL_NUMBER_MAGIC = "vibl:d4f8159c"

MSG_LEN = 32

# these should match what we have in vial-qmk/keyboards/vial_example
# so that people don't accidentally reuse a sample keyboard UID
EXAMPLE_KEYBOARDS = [
    0xD4A36200603E3007,  # vial_stm32f103_vibl
    0x32F62BC2EEF2237B,  # vial_atmega32u4
    0x38CEA320F23046A5,  # vial_stm32f072
]


def hid_send(dev, msg, retries=1):
    if len(msg) > MSG_LEN:
        raise RuntimeError("message must be less than 32 bytes")
    msg += b"\x00" * (MSG_LEN - len(msg))

    data = b""
    first = True

    while retries > 0:
        retries -= 1
        if not first:
            time.sleep(0.5)
        first = False
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


def is_rawhid(desc):
    if desc["usage_page"] != 0xFF60 or desc["usage"] != 0x61:
        logging.warning("is_rawhid: {} does not match - usage_page={:04X} usage={:02X}".format(
            desc["path"], desc["usage_page"], desc["usage"]))
        return False

    dev = hid.device()

    try:
        dev.open_path(desc["path"])
    except OSError as e:
        logging.warning("is_rawhid: {} does not match - open_path error {}".format(desc["path"], e))
        return False

    # probe VIA version and ensure it is supported
    data = b""
    try:
        data = hid_send(dev, b"\x01", retries=3)
    except RuntimeError as e:
        logging.warning("is_rawhid: {} does not match - hid_send error {}".format(desc["path"], e))
        pass
    dev.close()

    # must have VIA protocol version = 9
    if data[0:3] != b"\x01\x00\x09":
        logging.warning("is_rawhid: {} does not match - unexpected data in response {}".format(
            desc["path"], data.hex()))
        return False

    logging.info("is_rawhid: {} matched OK".format(desc["path"]))
    return True


def find_vial_devices(via_stack_json, sideload_vid=None, sideload_pid=None):
    from vial_device import VialBootloader, VialKeyboard, VialDummyKeyboard

    filtered = []
    for dev in hid.enumerate():
        if dev["vendor_id"] == sideload_vid and dev["product_id"] == sideload_pid:
            logging.info("Trying VID={:04X}, PID={:04X}, serial={}, path={} - sideload".format(
                dev["vendor_id"], dev["product_id"], dev["serial_number"], dev["path"]
            ))
            if is_rawhid(dev):
                filtered.append(VialKeyboard(dev, sideload=True))
        elif VIAL_SERIAL_NUMBER_MAGIC in dev["serial_number"]:
            logging.info("Matching VID={:04X}, PID={:04X}, serial={}, path={} - vial serial magic".format(
                dev["vendor_id"], dev["product_id"], dev["serial_number"], dev["path"]
            ))
            if is_rawhid(dev):
                filtered.append(VialKeyboard(dev))
        elif VIBL_SERIAL_NUMBER_MAGIC in dev["serial_number"]:
            logging.info("Matching VID={:04X}, PID={:04X}, serial={}, path={} - vibl serial magic".format(
                dev["vendor_id"], dev["product_id"], dev["serial_number"], dev["path"]
            ))
            filtered.append(VialBootloader(dev))
        elif str(dev["vendor_id"] * 65536 + dev["product_id"]) in via_stack_json["definitions"]:
            logging.info("Matching VID={:04X}, PID={:04X}, serial={}, path={} - VIA stack".format(
                dev["vendor_id"], dev["product_id"], dev["serial_number"], dev["path"]
            ))
            if is_rawhid(dev):
                filtered.append(VialKeyboard(dev, via_stack=True))

    if sideload_vid == sideload_pid == 0:
        filtered.append(VialDummyKeyboard())

    return filtered


def chunks(data, sz):
    for i in range(0, len(data), sz):
        yield data[i:i+sz]


def pad_for_vibl(msg):
    """ Pads message to vibl fixed 64-byte length """
    if len(msg) > 64:
        raise RuntimeError("vibl message too long")
    return msg + b"\x00" * (64 - len(msg))


def init_logger():
    logging.basicConfig(level=logging.INFO)
    directory = QStandardPaths.writableLocation(QStandardPaths.AppLocalDataLocation)
    if not os.path.exists(directory):
        os.mkdir(directory)
    path = os.path.join(directory, "vial.log")
    handler = RotatingFileHandler(path, maxBytes=5 * 1024 * 1024, backupCount=5)
    handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(module)s:%(lineno)d - %(message)s"))
    logging.getLogger().addHandler(handler)
