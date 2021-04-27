# SPDX-License-Identifier: GPL-2.0-or-later

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QTabWidget, QWidget, QScrollArea, QApplication, QLabel
from PyQt5.QtGui import QPalette

from constants import KEYCODE_BTN_RATIO
from flowlayout import FlowLayout
from keycodes import KEYCODES_BASIC, KEYCODES_ISO, KEYCODES_MACRO, KEYCODES_LAYERS, KEYCODES_QUANTUM, \
    KEYCODES_BACKLIGHT, KEYCODES_MEDIA, KEYCODES_SPECIAL, KEYCODES_SHIFTED, KEYCODES_USER, Keycode
from keymaps import KEYMAPS
from square_button import SquareButton
from util import tr


class TabbedKeycodes(QTabWidget):

    keycode_changed = pyqtSignal(int)
    anykey = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.keymap_override = None
        self.custom_keycodes = None

        self.tab_basic = QScrollArea()
        self.tab_iso = QScrollArea()
        self.tab_layers = QScrollArea()
        self.tab_quantum = QScrollArea()
        self.tab_backlight = QScrollArea()
        self.tab_media = QScrollArea()
        self.tab_user = QScrollArea()
        self.tab_macro = QScrollArea()

        self.widgets = []

        for (tab, label, keycodes) in [
            (self.tab_basic, "Basic", KEYCODES_SPECIAL + KEYCODES_BASIC + KEYCODES_SHIFTED),
            (self.tab_iso, "ISO/JIS", KEYCODES_ISO),
            (self.tab_layers, "Layers", KEYCODES_LAYERS),
            (self.tab_quantum, "Quantum", KEYCODES_QUANTUM),
            (self.tab_backlight, "Backlight", KEYCODES_BACKLIGHT),
            (self.tab_media, "App, Media and Mouse", KEYCODES_MEDIA),
            (self.tab_user, "User", KEYCODES_USER),
            (self.tab_macro, "Macro", KEYCODES_MACRO),
        ]:
            layout = FlowLayout()
            if tab == self.tab_layers:
                self.layout_layers = layout
            elif tab == self.tab_macro:
                self.layout_macro = layout
            elif tab == self.tab_basic:
                # create the "Any" keycode button
                btn = SquareButton()
                btn.setText("Any")
                btn.setRelSize(KEYCODE_BTN_RATIO)
                btn.clicked.connect(lambda: self.anykey.emit())
                layout.addWidget(btn)

            self.widgets += self.create_buttons(layout, keycodes)

            tab.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
            tab.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            tab.setWidgetResizable(True)

            w = QWidget()
            w.setLayout(layout)
            tab.setWidget(w)
            self.addTab(tab, tr("TabbedKeycodes", label))

        self.layer_keycode_buttons = []
        self.macro_keycode_buttons = []
        self.set_keymap_override(KEYMAPS[0][1])

    def create_buttons(self, layout, keycodes):
        buttons = []

        for keycode in keycodes:
            btn = SquareButton()
            btn.setRelSize(KEYCODE_BTN_RATIO)
            btn.setToolTip(Keycode.tooltip(keycode.code))
            btn.clicked.connect(lambda st, k=keycode: self.keycode_changed.emit(k.code))
            btn.keycode = keycode
            layout.addWidget(btn)
            buttons.append(btn)

        return buttons

    def recreate_keycode_buttons(self):
        for btn in self.layer_keycode_buttons + self.macro_keycode_buttons:
            self.widgets.remove(btn)
            btn.hide()
            btn.deleteLater()
        self.layer_keycode_buttons = self.create_buttons(self.layout_layers, KEYCODES_LAYERS)
        self.macro_keycode_buttons = self.create_buttons(self.layout_macro, KEYCODES_MACRO)
        self.widgets += self.layer_keycode_buttons + self.macro_keycode_buttons
        self.relabel_buttons()

    def set_keymap_override(self, override):
        self.keymap_override = override
        self.relabel_buttons()

    def set_custom_keycodes(self, custom_keycodes):
        self.custom_keycodes = custom_keycodes
        self.relabel_buttons()

    def relabel_buttons(self):
        for widget in self.widgets:
            qmk_id = widget.keycode.qmk_id
            if self.keymap_override is not None and qmk_id in self.keymap_override:
                label = self.keymap_override[qmk_id]
                highlight_color = QApplication.palette().color(QPalette.Link).getRgb()
                widget.setStyleSheet("QPushButton {color: rgb"+str(highlight_color)+";}")
                widget.setWordWrap(False)
            elif self.custom_keycodes is not None and qmk_id in self.custom_keycodes:
                label = self.custom_keycodes[qmk_id].name
                name = self.custom_keycodes[qmk_id].shortName
                title = self.custom_keycodes[qmk_id].title
                tooltip = "{0}: {1}".format(name, title)
                highlight_color = QApplication.palette().color(QPalette.Link).getRgb()
                widget.setStyleSheet("color: rgb"+str(highlight_color)+";")
                widget.setToolTip(tooltip)
                widget.setWordWrap(True)
            else:
                label = widget.keycode.label
                widget.setStyleSheet("QPushButton {}")
                widget.setWordWrap(False)
            widget.setText(label.replace("&", "&&"))
