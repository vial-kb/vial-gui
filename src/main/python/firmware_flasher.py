# SPDX-License-Identifier: GPL-2.0-or-later

import datetime
import struct
import time
import threading

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QFontDatabase
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QLineEdit, QToolButton, QPlainTextEdit, QProgressBar,\
    QFileDialog, QDialog

from util import tr, chunks
from vial_device import VialBootloader


def send_retries(dev, data, retries=20):
    """ Sends usb packet up to 'retries' times, returns True if success, False if failed """

    for x in range(retries):
        ret = dev.send(data)
        if ret == len(data) + 1:
            return True
        elif ret < 0:
            time.sleep(0.1)
        else:
            return False
    return False


CHUNK = 64


def cmd_flash(device, firmware, log):
    # Check bootloader is correct version
    device.send(b"VC\x00")
    data = device.recv(8)
    log("* Bootloader version: {}".format(data[0]))
    if data[0] != 0:
        log("Error: Unsupported bootloader version")
        return

    # TODO: Check vial ID against firmware package
    device.send(b"VC\x01")
    data = device.recv(8)
    log("* Vial ID: {}".format(data.hex()))

    # Flash
    firmware_size = len(firmware)
    if firmware_size % CHUNK != 0:
        firmware_size += CHUNK - firmware_size % CHUNK
    log(device.send(b"VC\x02" + struct.pack("<H", firmware_size // CHUNK)))
    for part in chunks(firmware, CHUNK):
        if len(part) < CHUNK:
            part += b"\x00" * (CHUNK - len(part))
        if not send_retries(device, part):
            log("Error while sending data, firmware is corrupted.")
            return
        log(datetime.datetime.now())

    # Reboot
    log("Rebooting...")
    device.send(b"VC\x03")


class FirmwareFlasher(QVBoxLayout):
    log_signal = pyqtSignal(object)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.log_signal.connect(self._on_log)

        self.selected_firmware_path = ""

        file_selector = QHBoxLayout()
        self.txt_file_selector = QLineEdit()
        self.txt_file_selector.setReadOnly(True)
        file_selector.addWidget(self.txt_file_selector)
        btn_select_file = QToolButton()
        btn_select_file.setText(tr("Flasher", "Select file..."))
        btn_select_file.clicked.connect(self.on_click_select_file)
        file_selector.addWidget(btn_select_file)
        self.addLayout(file_selector)
        self.txt_logger = QPlainTextEdit()
        self.txt_logger.setReadOnly(True)
        self.txt_logger.setFont(QFontDatabase.systemFont(QFontDatabase.FixedFont))
        self.addWidget(self.txt_logger)
        progress_flash = QHBoxLayout()
        progress_flash.addWidget(QProgressBar())
        btn_flash = QToolButton()
        btn_flash.setText(tr("Flasher", "Flash"))
        btn_flash.clicked.connect(self.on_click_flash)
        progress_flash.addWidget(btn_flash)
        self.addLayout(progress_flash)

        self.device = None

    def rebuild(self, device):
        self.device = device
        self.txt_logger.clear()
        if isinstance(self.device, VialBootloader):
            self.log("Valid Vial Bootloader device at {}".format(self.device.desc["path"].decode("utf-8")))

    def valid(self):
        # TODO: it is also valid to flash a VialKeyboard which supports optional "vibl-integration" feature
        return isinstance(self.device, VialBootloader)

    def on_click_select_file(self):
        dialog = QFileDialog()
        # TODO: this should be .vfw for Vial Firmware
        dialog.setDefaultSuffix("bin")
        dialog.setAcceptMode(QFileDialog.AcceptOpen)
        dialog.setNameFilters(["Vial Firmware (*.bin)"])
        if dialog.exec_() == QDialog.Accepted:
            self.selected_firmware_path = dialog.selectedFiles()[0]
            self.txt_file_selector.setText(self.selected_firmware_path)
            self.log("Firmware update package: {}".format(self.selected_firmware_path))

    def on_click_flash(self):
        if not self.selected_firmware_path:
            self.log("Error: Please select a firmware update package")
            return

        with open(self.selected_firmware_path, "rb") as inf:
            firmware = inf.read()

        if len(firmware) > 10 * 1024 * 1024:
            self.log("Error: Firmware is too large. Check you've selected the correct file")
            return

        self.log("Preparing to flash...")
        threading.Thread(target=lambda: cmd_flash(self.device, firmware, self.on_log)).start()

    def on_log(self, line):
        self.log_signal.emit(line)

    def _on_log(self, line):
        self.log(line)

    def log(self, line):
        self.txt_logger.appendPlainText("[{}] {}".format(datetime.datetime.now(), line))
