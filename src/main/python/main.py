from fbs_runtime.application_context.PyQt5 import ApplicationContext
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QTabWidget, QVBoxLayout, QPushButton, QLabel

import sys

from flowlayout import FlowLayout

class TabbedKeycodes(QTabWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.tab_basic = QWidget()
        layout = FlowLayout()

        for lbl in ["", "TODO", "Esc", "A", "B", "C", "D", "E", "F"]:
            btn = QPushButton(lbl)
            btn.setFixedSize(50, 50)
            layout.addWidget(btn)
        self.tab_basic.setLayout(layout)

        self.tab_media = QWidget()
        self.tab_macro = QWidget()

        self.addTab(self.tab_basic, "Basic")
        self.addTab(self.tab_media, "Media")
        self.addTab(self.tab_macro, "Macro")


KEY_WIDTH = 40
KEY_HEIGHT = KEY_WIDTH
KEY_SPACING = 10


class KeyboardContainer(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setFixedSize(300, 300)

        for x, btn in enumerate(["Q", "W", "E", "R"]):
            widget = QLabel(btn)
            widget.setParent(self)
            widget.setStyleSheet('background-color:red;')
            widget.setAlignment(Qt.AlignCenter)
            widget.setFixedSize(KEY_WIDTH, KEY_HEIGHT)
            widget.move((KEY_WIDTH + KEY_SPACING) * x, 0)
    
        for x, btn in enumerate(["A", "S", "D", "F"]):
            widget = QLabel(btn)
            widget.setParent(self)
            widget.setStyleSheet('background-color:red;')
            widget.setAlignment(Qt.AlignCenter)
            widget.setFixedSize(KEY_WIDTH, KEY_HEIGHT)
            widget.move((KEY_WIDTH + KEY_SPACING) * (x + 0.25), KEY_HEIGHT + KEY_SPACING)


class MainWindow(QWidget):

    def __init__(self):
        super().__init__()

        self.keyboard_container = KeyboardContainer()

        self.tabbed_keycodes = TabbedKeycodes()

        layout = QVBoxLayout()
        layout.addWidget(self.keyboard_container)
        layout.addWidget(self.tabbed_keycodes)
        self.setLayout(layout)


if __name__ == '__main__':
    appctxt = ApplicationContext()       # 1. Instantiate ApplicationContext
    window = MainWindow()
    window.resize(1024, 768)
    window.show()
    exit_code = appctxt.app.exec_()      # 2. Invoke appctxt.app.exec_()
    sys.exit(exit_code)
