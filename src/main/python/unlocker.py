# SPDX-License-Identifier: GPL-2.0-or-later
import time

from PyQt5.QtCore import QCoreApplication, Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QProgressBar

from util import tr


class Unlocker(QWidget):

    def __init__(self):
        super().__init__()
        self.keyboard = None

        layout = QVBoxLayout()

        self.progress = QProgressBar()

        layout.addWidget(QLabel(tr("Unlocker", "In order to proceed, the keyboard must be set into unlocked mode.\n"
                                               "You should only perform this operation on computers that you trust.")))
        layout.addWidget(QLabel(tr("Unlocker", "To exit this mode, you will need to replug the keyboard.")))
        layout.addWidget(QLabel(tr("Unlocker", "Press and hold the following keys until the progress bar "
                                               "below fills up:")))

        # TODO: add image/text reference of keys user needs to hold

        layout.addWidget(self.progress)

        self.setLayout(layout)
        self.setWindowFlag(Qt.Dialog)

    def perform_unlock(self, keyboard):
        # if it's already unlocked, don't need to do anything
        if keyboard.get_lock() == 0:
            return

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
