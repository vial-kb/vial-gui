# SPDX-License-Identifier: GPL-2.0-or-later
import time

from PyQt5.QtCore import QCoreApplication, Qt
from PyQt5.QtWidgets import QVBoxLayout, QLabel, QProgressBar, QDialog, QDialogButtonBox, QPlainTextEdit

from util import tr


class MacroTextWindow(QDialog):

    def __init__(self, macro):
        super().__init__()
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        layout = QVBoxLayout()

        macrotext = QPlainTextEdit()
        macrotext.setPlainText(macro)
        macrotext.selectAll()

        layout.addWidget(macrotext)

        self.setLayout(layout)
        self.setWindowFlags(self.windowFlags())

    @classmethod
    def show(cls, macro):

        dlg = cls(macro)
        return bool(dlg.exec_())
