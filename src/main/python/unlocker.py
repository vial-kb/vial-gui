# SPDX-License-Identifier: GPL-2.0-or-later
import time

from PyQt5.QtCore import QCoreApplication, Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QProgressBar

from keyboard_widget import KeyboardWidget
from util import tr


class Unlocker(QWidget):

    def __init__(self, layout_editor):
        super().__init__()
        self.keyboard = None

        layout = QVBoxLayout()

        self.progress = QProgressBar()

        layout.addWidget(QLabel(tr("Unlocker", "In order to proceed, the keyboard must be set into unlocked mode.\n"
                                               "You should only perform this operation on computers that you trust.")))
        layout.addWidget(QLabel(tr("Unlocker", "To exit this mode, you will need to replug the keyboard\n"
                                               "or select Security->Lock from the menu.")))
        layout.addWidget(QLabel(tr("Unlocker", "Press and hold the following keys until the progress bar "
                                               "below fills up:")))

        self.keyboard_reference = KeyboardWidget(layout_editor)
        self.keyboard_reference.set_enabled(False)
        self.keyboard_reference.set_scale(0.5)
        layout.addWidget(self.keyboard_reference)
        layout.setAlignment(self.keyboard_reference, Qt.AlignHCenter)

        layout.addWidget(self.progress)

        self.setLayout(layout)
        self.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint | Qt.CustomizeWindowHint)

        Unlocker.obj = self

    @classmethod
    def get(cls):
        return cls.obj

    def update_reference(self, keyboard):
        """ Updates keycap reference image """

        self.keyboard_reference.set_keys(keyboard.keys, keyboard.encoders)

        # use "active" background to indicate keys to hold
        lock_keys = keyboard.get_unlock_keys()
        for w in self.keyboard_reference.widgets:
            if (w.desc.row, w.desc.col) in lock_keys:
                w.setActive(True)

        self.keyboard_reference.update_layout()
        self.keyboard_reference.update()
        self.keyboard_reference.updateGeometry()

    def perform_unlock(self, keyboard):
        # if it's already unlocked, don't need to do anything
        unlock = keyboard.get_unlock_status()
        if unlock == 1:
            return

        self.update_reference(keyboard)

        self.progress.setMaximum(1)
        self.progress.setValue(0)

        self.show()
        self.keyboard = keyboard
        self.keyboard.unlock_start()

        while True:
            data = self.keyboard.unlock_poll()
            unlocked = data[0]
            unlock_counter = data[2]

            self.progress.setMaximum(max(self.progress.maximum(), unlock_counter))
            self.progress.setValue(self.progress.maximum() - unlock_counter)

            if unlocked == 1:
                break

            QCoreApplication.processEvents()
            time.sleep(0.2)

        # ok all done, the keyboard is now set to insecure state
        self.hide()

    def closeEvent(self, ev):
        ev.ignore()
