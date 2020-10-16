from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QTabWidget, QWidget, QPushButton

from constants import KEYCODE_BTN_WIDTH, KEYCODE_BTN_HEIGHT
from flowlayout import FlowLayout
from keycodes import KEYCODES_BASIC, KEYCODES_ISO, KEYCODES_MACRO, KEYCODES_LAYERS, KEYCODES_SPECIAL, keycode_tooltip
from util import tr


class TabbedKeycodes(QTabWidget):

    keycode_changed = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.tab_basic = QWidget()
        self.tab_iso = QWidget()
        self.tab_macro = QWidget()
        self.tab_layers = QWidget()
        self.tab_special = QWidget()

        for (tab, label, keycodes) in [
            (self.tab_basic, "Basic", KEYCODES_BASIC),
            (self.tab_iso, "ISO/JIS", KEYCODES_ISO),
            (self.tab_macro, "Macro", KEYCODES_MACRO),
            (self.tab_layers, "Layers", KEYCODES_LAYERS),
            (self.tab_special, "Special", KEYCODES_SPECIAL),
        ]:
            layout = FlowLayout()
            buttons = self.create_buttons(layout, keycodes)
            tab.setLayout(layout)
            self.addTab(tab, tr("TabbedKeycodes", label))

        self.layer_keycode_buttons = []

    def create_buttons(self, layout, keycodes):
        buttons = []

        for keycode in keycodes:
            btn = QPushButton(keycode.label)
            btn.setFixedSize(KEYCODE_BTN_WIDTH, KEYCODE_BTN_HEIGHT)
            btn.setToolTip(keycode_tooltip(keycode.code))
            btn.clicked.connect(lambda st, k=keycode: self.keycode_changed.emit(k.code))
            layout.addWidget(btn)
            buttons.append(btn)

        return buttons

    def recreate_layer_keycode_buttons(self):
        for btn in self.layer_keycode_buttons:
            btn.deleteLater()
        self.layer_keycode_buttons = self.create_buttons(self.tab_layers.layout(), KEYCODES_LAYERS)
