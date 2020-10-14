from fbs_runtime.application_context.PyQt5 import ApplicationContext
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QTabWidget, QVBoxLayout, QPushButton, QLabel

import sys
import json

from flowlayout import FlowLayout
from util import tr
from kle_serial import Serial as KleSerial

class TabbedKeycodes(QTabWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.tab_basic = QWidget()
        layout = FlowLayout()

        for lbl in ["", "hello", "Esc", "A", "B", "C", "D", "E", "F"]:
            btn = QPushButton(lbl)
            btn.setFixedSize(50, 50)
            layout.addWidget(btn)
        self.tab_basic.setLayout(layout)

        self.tab_media = QWidget()
        self.tab_macro = QWidget()

        self.addTab(self.tab_basic, tr("TabbedKeycodes", "Basic"))
        self.addTab(self.tab_media, tr("TabbedKeycodes", "Media"))
        self.addTab(self.tab_macro, tr("TabbedKeycodes", "Macro"))


KEY_WIDTH = 40
KEY_HEIGHT = KEY_WIDTH
KEY_SPACING = 4


class KeyboardContainer(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        serial = KleSerial()
        data = open("g60.json", "r").read()
        data = json.loads(data)
        kb = serial.deserialize(data["layouts"]["keymap"])

        max_w = max_h = 0

        for key in kb.keys:
            widget = QLabel(str(key.labels[0]))
            widget.setParent(self)
            widget.setStyleSheet('background-color:white; border: 1px solid black')
            widget.setAlignment(Qt.AlignCenter)

            x = (KEY_WIDTH + KEY_SPACING) * key.x
            y = (KEY_HEIGHT + KEY_SPACING) * key.y
            w = (KEY_WIDTH + KEY_SPACING) * key.width - KEY_SPACING
            h = (KEY_HEIGHT + KEY_SPACING) * key.height - KEY_SPACING

            widget.setFixedSize(w, h)
            widget.move(x, y)
            print("{} {}x{}+{}x{}".format(key.labels, key.x, key.y, key.width, key.height))

            max_w = max(max_w, x + w)
            max_h = max(max_h, y + h)
    
        self.setFixedSize(max_w, max_h)


class MainWindow(QWidget):

    def __init__(self):
        super().__init__()

        self.keyboard_container = KeyboardContainer()

        self.tabbed_keycodes = TabbedKeycodes()

        layout = QVBoxLayout()
        layout.addWidget(self.keyboard_container)
        layout.setAlignment(self.keyboard_container, Qt.AlignHCenter)
        layout.addWidget(self.tabbed_keycodes)
        self.setLayout(layout)


if __name__ == '__main__':
    appctxt = ApplicationContext()       # 1. Instantiate ApplicationContext
    window = MainWindow()
    window.resize(1024, 768)
    window.show()
    exit_code = appctxt.app.exec_()      # 2. Invoke appctxt.app.exec_()
    sys.exit(exit_code)
