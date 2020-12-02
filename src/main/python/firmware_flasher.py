# SPDX-License-Identifier: GPL-2.0-or-later

from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QLineEdit, QToolButton, QPlainTextEdit, QProgressBar

from util import tr
from vial_device import VialBootloader


class FirmwareFlasher(QVBoxLayout):

    def __init__(self, parent=None):
        super().__init__(parent)

        file_selector = QHBoxLayout()
        file_selector.addWidget(QLineEdit())
        btn_select_file = QToolButton()
        btn_select_file.setText(tr("Flasher", "Select file..."))
        file_selector.addWidget(btn_select_file)
        self.addLayout(file_selector)
        self.addWidget(QPlainTextEdit())
        progress_flash = QHBoxLayout()
        progress_flash.addWidget(QProgressBar())
        btn_flash = QToolButton()
        btn_flash.setText(tr("Flasher", "Flash"))
        progress_flash.addWidget(btn_flash)
        self.addLayout(progress_flash)

        self.device = None

    def rebuild(self, device):
        self.device = device

    def valid(self):
        return isinstance(self.device, VialBootloader)
