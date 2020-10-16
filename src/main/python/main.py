# SPDX-License-Identifier: GPL-2.0-or-later

from fbs_runtime.application_context.PyQt5 import ApplicationContext
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QWidget, QTabWidget, QVBoxLayout, QPushButton, QLabel, QComboBox, QToolButton, QHBoxLayout, QSizePolicy

import sys
import json
import struct
import lzma
from collections import defaultdict

from flowlayout import FlowLayout
from util import tr, find_vial_keyboards, open_device
from clickable_label import ClickableLabel
from keycodes import keycode_label, keycode_tooltip, recreate_layer_keycodes, KEYCODES_BASIC, KEYCODES_ISO, KEYCODES_MACRO, KEYCODES_LAYERS, KEYCODES_SPECIAL
from keyboard import Keyboard


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
            btn.setFixedSize(50, 50)
            btn.setToolTip(keycode_tooltip(keycode.code))
            btn.clicked.connect(lambda st, k=keycode: self.keycode_changed.emit(k.code))
            layout.addWidget(btn)
            buttons.append(btn)

        return buttons

    def recreate_layer_keycode_buttons(self):
        for btn in self.layer_keycode_buttons:
            btn.deleteLater()
        self.layer_keycode_buttons = self.create_buttons(self.tab_layers.layout(), KEYCODES_LAYERS)


KEY_WIDTH = 40
KEY_HEIGHT = KEY_WIDTH
KEY_SPACING = 4


class KeyboardContainer(QWidget):

    number_layers_changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.layout_layers = QHBoxLayout()
        layer_label = QLabel(tr("KeyboardContainer", "Layer"))

        layout_labels_container = QHBoxLayout()
        layout_labels_container.addWidget(layer_label)
        layout_labels_container.addLayout(self.layout_layers)
        layout_labels_container.addStretch()

        # contains the actual keyboard
        self.container = QWidget()

        layout = QVBoxLayout()
        layout.addLayout(layout_labels_container)
        layout.addWidget(self.container)
        layout.setAlignment(self.container, Qt.AlignHCenter)
        self.setLayout(layout)

        self.keys = []
        self.layer_labels = []
        self.rowcol = defaultdict(list)
        self.selected_key = None
        self.selected_row = -1
        self.selected_col = -1

    def rebuild_layers(self):
        self.layers = self.keyboard.layers
        self.number_layers_changed.emit()

        # delete old layer labels
        for label in self.layer_labels:
            label.deleteLater()
        self.layer_labels = []

        # create new layer labels
        for x in range(self.layers):
            label = ClickableLabel(str(x))
            label.setAlignment(Qt.AlignCenter)
            label.clicked.connect(lambda idx=x: self.switch_layer(idx))
            self.layout_layers.addWidget(label)
            self.layer_labels.append(label)

    def rebuild(self, keyboard):
        self.keyboard = keyboard

        # delete current layout
        for key in self.keys:
            key.deleteLater()
        self.keys = []

        # get number of layers
        self.rebuild_layers()

        # prepare for fetching keymap
        self.rowcol = defaultdict(list)

        max_w = max_h = 0

        for key in keyboard.keys:
            widget = ClickableLabel()
            widget.clicked.connect(lambda w=widget: self.select_key(w))

            if key.row is not None:
                self.rowcol[(key.row, key.col)].append(widget)

            widget.setParent(self.container)
            widget.setAlignment(Qt.AlignCenter)

            x = (KEY_WIDTH + KEY_SPACING) * key.x
            y = (KEY_HEIGHT + KEY_SPACING) * key.y
            w = (KEY_WIDTH + KEY_SPACING) * key.width - KEY_SPACING
            h = (KEY_HEIGHT + KEY_SPACING) * key.height - KEY_SPACING

            widget.setFixedSize(w, h)
            widget.move(x, y)
            widget.show()

            max_w = max(max_w, x + w)
            max_h = max(max_h, y + h)

            self.keys.append(widget)

        self.container.setFixedSize(max_w, max_h)
        self.current_layer = 0
        self.refresh_layer_display()

    def refresh_layer_display(self):
        """ Refresh text on key widgets to display data corresponding to current layer """

        for label in self.layer_labels:
            label.setStyleSheet("border: 1px solid black; padding: 5px")
        self.layer_labels[self.current_layer].setStyleSheet("border: 1px solid black; padding: 5px; background-color: black; color: white")

        for (row, col), widgets in self.rowcol.items():
            code = self.keyboard.layout[(self.current_layer, row, col)]
            text = keycode_label(code)
            tooltip = keycode_tooltip(code)
            for widget in widgets:
                widget.setStyleSheet('background-color:white; border: 1px solid black')
                if widget == self.selected_key:
                    widget.setStyleSheet('background-color:black; color: white; border: 1px solid black')
                widget.setText(text)
                widget.setToolTip(tooltip)

    def switch_layer(self, idx):
        self.current_layer = idx
        self.selected_key = None
        self.selected_row = -1
        self.selected_col = -1
        self.refresh_layer_display()

    def set_key(self, keycode):
        """ Change currently selected key to provided keycode """

        if self.selected_row >= 0 and self.selected_col >= 0:
            self.keyboard.set_key(self.current_layer, self.selected_row, self.selected_col, keycode)
            self.refresh_layer_display()

    def select_key(self, widget):
        """ Change which key is currently selected """

        self.selected_key = widget
        for (row, col), widgets in self.rowcol.items():
            if widget in widgets:
                self.selected_row = row
                self.selected_col = col
                break
        self.refresh_layer_display()


class MainWindow(QWidget):

    def __init__(self):
        super().__init__()
        self.device = None
        self.devices = []

        self.keyboard_container = KeyboardContainer()
        self.keyboard_container.number_layers_changed.connect(self.on_number_layers_changed)

        self.tabbed_keycodes = TabbedKeycodes()
        self.tabbed_keycodes.keycode_changed.connect(self.on_keycode_changed)

        self.combobox_devices = QComboBox()
        self.combobox_devices.currentIndexChanged.connect(self.on_device_selected)

        btn_refresh_devices = QToolButton()
        btn_refresh_devices.setToolButtonStyle(Qt.ToolButtonTextOnly)
        btn_refresh_devices.setText(tr("MainWindow", "Refresh"))
        btn_refresh_devices.clicked.connect(self.on_click_refresh)

        layout_combobox = QHBoxLayout()
        layout_combobox.addWidget(self.combobox_devices)
        layout_combobox.addWidget(btn_refresh_devices)

        layout = QVBoxLayout()
        layout.addLayout(layout_combobox)
        layout.addWidget(self.keyboard_container)
        layout.addWidget(self.tabbed_keycodes)
        self.setLayout(layout)

        # make sure initial state is valid
        self.on_click_refresh()

    def on_click_refresh(self):
        self.devices = find_vial_keyboards()
        self.combobox_devices.clear()

        for dev in self.devices:
            self.combobox_devices.addItem("{} {}".format(dev["manufacturer_string"], dev["product_string"]))

    def on_device_selected(self):
        self.device = None
        idx = self.combobox_devices.currentIndex()
        if idx >= 0:
            keyboard = Keyboard(open_device(self.devices[idx]))
            keyboard.reload()
            self.keyboard_container.rebuild(keyboard)

    def on_number_layers_changed(self):
        recreate_layer_keycodes(self.keyboard_container.layers)
        self.tabbed_keycodes.recreate_layer_keycode_buttons()

    def on_keycode_changed(self, code):
        self.keyboard_container.set_key(code)


if __name__ == '__main__':
    appctxt = ApplicationContext()       # 1. Instantiate ApplicationContext
    window = MainWindow()
    window.resize(1024, 768)
    window.show()
    exit_code = appctxt.app.exec_()      # 2. Invoke appctxt.app.exec_()
    sys.exit(exit_code)
