from PyQt5.QtWidgets import QVBoxLayout, QPushButton
from PyQt5.QtCore import Qt, QTimer
import struct
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

        layout = QVBoxLayout()
        layout.addWidget(self.keyboardWidget)
        layout.setAlignment(self.keyboardWidget, Qt.AlignCenter)

        self.addLayout(layout)
        self.addWidget(self.startButtonWidget)

        self.keyboard = None
        self.device = None
        self.polling = False

        self.timer = QTimer()
        self.timer.timeout.connect(self.matrix_poller)
        self.startButtonWidget.clicked.connect(self.start_poller)

    def rebuild(self, device):
        super().rebuild(device)
        if self.valid():
            self.keyboard = device.keyboard

            self.keyboardWidget.set_keys(self.keyboard.keys, self.keyboard.encoders)

    def valid(self):
        return isinstance(self.device, VialKeyboard)

    def matrix_poller(self):
        rows = self.keyboard.rows
        cols = self.keyboard.cols
        matrix = [ [None for y in range(cols)] for x in range(rows) ]

        data = self.keyboard.matrix_poll()

        row_size = math.ceil(cols / 8)

        for row in range(rows):
            row_data_start = 2 + (row * row_size)
            row_data_end = row_data_start + row_size
            row_data = data[row_data_start:row_data_end]

            for col in range(cols):
                col_byte = math.floor(col / 8)
                state = (row_data[col_byte] >> col) & 1
                matrix[row][col] = state

        for w in self.keyboardWidget.widgets:
            row = w.desc.row
            col = w.desc.col

            if row < len(matrix) and col < len(matrix[row]):
                w.setActive(matrix[row][col])
        
        self.keyboardWidget.update_layout()
        self.keyboardWidget.update()
        self.keyboardWidget.updateGeometry()

    def start_poller(self):
        if not self.polling:
            Unlocker.unlock(self.keyboard)
            self.startButtonWidget.setText("Stop testing")
            self.timer.start(100)
            self.polling = True
        else:
            self.timer.stop()
            self.keyboard.lock()
            self.startButtonWidget.setText("Start testing")
            self.polling = False
        
