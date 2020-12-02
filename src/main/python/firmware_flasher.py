# SPDX-License-Identifier: GPL-2.0-or-later

import datetime

from PyQt5.QtGui import QFontDatabase
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QLineEdit, QToolButton, QPlainTextEdit, QProgressBar,\
    QFileDialog, QDialog

from util import tr
from vial_device import VialBootloader


class FirmwareFlasher(QVBoxLayout):

    def __init__(self, parent=None):
        super().__init__(parent)

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
        pass

    def log(self, line):
        self.txt_logger.appendPlainText("[{}] {}".format(datetime.datetime.now(), line))
