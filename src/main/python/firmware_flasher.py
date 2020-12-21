# SPDX-License-Identifier: GPL-2.0-or-later

import datetime
import struct
import time
import threading

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QFontDatabase
from PyQt5.QtWidgets import QHBoxLayout, QLineEdit, QToolButton, QPlainTextEdit, QProgressBar,QFileDialog, QDialog

from basic_editor import BasicEditor
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


def cmd_flash(device, firmware, log_cb, progress_cb, complete_cb, error_cb):
    while len(firmware) % CHUNK != 0:
        firmware += b"\x00"

    # Check bootloader is correct version
    device.send(b"VC\x00")
    data = device.recv(8)
    log_cb("* Bootloader version: {}".format(data[0]))
    if data[0] != 0:
        return error_cb("Error: Unsupported bootloader version")

    # TODO: Check vial ID against firmware package
    device.send(b"VC\x01")
    data = device.recv(8)
    log_cb("* Vial ID: {}".format(data.hex()))

    # Flash
    log_cb("Flashing...")
    device.send(b"VC\x02" + struct.pack("<H", len(firmware) // CHUNK))
    total = 0
    for part in chunks(firmware, CHUNK):
        if len(part) < CHUNK:
            part += b"\x00" * (CHUNK - len(part))
        if not send_retries(device, part):
            return error_cb("Error while sending data, firmware is corrupted")
        total += len(part)
        progress_cb(total / len(firmware))

    # Reboot
    log_cb("Rebooting...")
    device.send(b"VC\x03")

    complete_cb("Done!")


class FirmwareFlasher(BasicEditor):
    log_signal = pyqtSignal(object)
    progress_signal = pyqtSignal(object)
    complete_signal = pyqtSignal(object)
    error_signal = pyqtSignal(object)

    def __init__(self, main, parent=None):
        super().__init__(parent)

        self.main = main

        self.log_signal.connect(self._on_log)
        self.progress_signal.connect(self._on_progress)
        self.complete_signal.connect(self._on_complete)
        self.error_signal.connect(self._on_error)

        self.selected_firmware_path = ""

        file_selector = QHBoxLayout()
        self.txt_file_selector = QLineEdit()
        self.txt_file_selector.setReadOnly(True)
        file_selector.addWidget(self.txt_file_selector)
        self.btn_select_file = QToolButton()
        self.btn_select_file.setText(tr("Flasher", "Select file..."))
        self.btn_select_file.clicked.connect(self.on_click_select_file)
        file_selector.addWidget(self.btn_select_file)
        self.addLayout(file_selector)
        self.txt_logger = QPlainTextEdit()
        self.txt_logger.setReadOnly(True)
        self.txt_logger.setFont(QFontDatabase.systemFont(QFontDatabase.FixedFont))
        self.addWidget(self.txt_logger)
        progress_flash = QHBoxLayout()
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        progress_flash.addWidget(self.progress_bar)
        self.btn_flash = QToolButton()
        self.btn_flash.setText(tr("Flasher", "Flash"))
        self.btn_flash.clicked.connect(self.on_click_flash)
        progress_flash.addWidget(self.btn_flash)
        self.addLayout(progress_flash)

        self.device = None

    def rebuild(self, device):
        super().rebuild(device)
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
        self.lock_ui()
        threading.Thread(target=lambda: cmd_flash(
            self.device, firmware, self.on_log, self.on_progress, self.on_complete, self.on_error)).start()

    def on_log(self, line):
        self.log_signal.emit(line)

    def on_progress(self, progress):
        self.progress_signal.emit(progress)

    def on_complete(self, msg):
        self.complete_signal.emit(msg)

    def on_error(self, msg):
        self.error_signal.emit(msg)

    def _on_log(self, msg):
        self.log(msg)

    def _on_progress(self, progress):
        self.progress_bar.setValue(int(progress * 100))

    def _on_complete(self, msg):
        self.log(msg)
        self.progress_bar.setValue(100)
        self.unlock_ui()

    def _on_error(self, msg):
        self.log(msg)
        self.unlock_ui()

    def log(self, line):
        self.txt_logger.appendPlainText("[{}] {}".format(datetime.datetime.now(), line))

    def lock_ui(self):
        self.btn_select_file.setEnabled(False)
        self.btn_flash.setEnabled(False)
        self.main.lock_ui()

    def unlock_ui(self):
        self.btn_select_file.setEnabled(True)
        self.btn_flash.setEnabled(True)
        self.main.unlock_ui()
