# SPDX-License-Identifier: GPL-2.0-or-later
from PyQt5.QtWidgets import QVBoxLayout, QPushButton
from PyQt5.QtCore import Qt, QTimer

import math

from basic_editor import BasicEditor
from keyboard_widget import KeyboardWidget
from vial_device import VialKeyboard
from unlocker import Unlocker


class MatrixTest(BasicEditor):
    def __init__(self, layout_editor):
        super().__init__()

        self.layout_editor = layout_editor

        self.keyboardWidget = KeyboardWidget(layout_editor)
        self.keyboardWidget.set_enabled(False)

        self.startButtonWidget = QPushButton("Start testing")
        self.resetButtonWidget = QPushButton("Reset")

        layout = QVBoxLayout()
        layout.addWidget(self.keyboardWidget)
        layout.setAlignment(self.keyboardWidget, Qt.AlignCenter)

        self.addLayout(layout)
        self.addWidget(self.resetButtonWidget)
        self.addWidget(self.startButtonWidget)

        self.keyboard = None
        self.device = None
        self.polling = False

        self.timer = QTimer()
        self.timer.timeout.connect(self.matrix_poller)

        self.startButtonWidget.clicked.connect(self.toggle)
        self.resetButtonWidget.clicked.connect(self.reset_keyboard_widget)

    def rebuild(self, device):
        super().rebuild(device)
        if self.valid():
            self.keyboard = device.keyboard

            self.keyboardWidget.set_keys(self.keyboard.keys, self.keyboard.encoders)

    def valid(self):
        # Check if vial protocol is v3 or later
        return isinstance(self.device, VialKeyboard) and (self.device.keyboard and self.device.keyboard.vial_protocol >= 3)

    def reset_keyboard_widget(self):
        # reset keyboard widget
        for w in self.keyboardWidget.widgets:
            w.setPressed(False)
            w.setActive(False)

        self.keyboardWidget.update_layout()
        self.keyboardWidget.update()
        self.keyboardWidget.updateGeometry()

    def matrix_poller(self):
        if not self.valid():
            self.stop()
            return

        # Get size for matrix
        rows = self.keyboard.rows
        cols = self.keyboard.cols
        # Generate 2d array of matrix
        matrix = [[None] * cols for x in range(rows)]

        # Get matrix data from keyboard
        try:
            data = self.keyboard.matrix_poll()
        except (RuntimeError, ValueError):
            self.stop()
            return

        # Calculate the amount of bytes belong to 1 row, each bit is 1 key, so per 8 keys in a row,
        # a byte is needed for the row.
        row_size = math.ceil(cols / 8)

        for row in range(rows):
            # Make slice of bytes for the row (skip first 2 bytes, they're for VIAL)
            row_data_start = 2 + (row * row_size)
            row_data_end = row_data_start + row_size
            row_data = data[row_data_start:row_data_end]

            # Get each bit representing pressed state for col
            for col in range(cols):
                # row_data is array of bytes, calculate in which byte the col is located
                col_byte = len(row_data) - 1 - math.floor(col / 8)
                # since we select a single byte as slice of byte, mod 8 to get nth pos of byte
                col_mod = (col % 8)
                # write to matrix array
                matrix[row][col] = (row_data[col_byte] >> col_mod) & 1

        # write matrix state to keyboard widget
        for w in self.keyboardWidget.widgets:
            if w.desc.row is not None and w.desc.col is not None:
                row = w.desc.row
                col = w.desc.col

                if row < len(matrix) and col < len(matrix[row]):
                    w.setPressed(matrix[row][col])
                    if matrix[row][col]:
                        w.setActive(True)

        self.keyboardWidget.update_layout()
        self.keyboardWidget.update()
        self.keyboardWidget.updateGeometry()

    def start(self):
        Unlocker.unlock(self.keyboard)
        self.startButtonWidget.setText("Stop testing")
        self.timer.start(20)
        self.polling = True

    def stop(self):
        self.timer.stop()
        try:
            self.keyboard.lock()
        except (RuntimeError, ValueError):
            # if keyboard disappeared, we can't relock it
            pass
        self.startButtonWidget.setText("Start testing")
        self.polling = False

    def toggle(self):
        if not self.polling:
            self.start()
        else:
            self.stop()
