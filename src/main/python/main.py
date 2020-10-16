# SPDX-License-Identifier: GPL-2.0-or-later

from fbs_runtime.application_context.PyQt5 import ApplicationContext
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QTabWidget, QVBoxLayout, QPushButton, QLabel, QComboBox, QToolButton, QHBoxLayout, QSizePolicy

import sys
import json
import struct
import lzma
from collections import defaultdict

from flowlayout import FlowLayout
from util import tr, find_vial_keyboards, open_device, hid_send, MSG_LEN
from kle_serial import Serial as KleSerial
from clickable_label import ClickableLabel
from keycodes import keycode_label, keycode_tooltip, KEYCODES_BASIC, KEYCODES_ISO, KEYCODES_MACRO, KEYCODES_LAYERS, KEYCODES_SPECIAL


class TabbedKeycodes(QTabWidget):

    def __init__(self, kb, parent=None):
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
            self.create_buttons(tab, keycodes)
            self.addTab(tab, tr("TabbedKeycodes", label))

    def create_buttons(self, tab, keycodes):
        layout = FlowLayout()

        for keycode in keycodes:
            btn = QPushButton(keycode.label)
            btn.setFixedSize(50, 50)
            btn.setToolTip(keycode_tooltip(keycode.code))
            btn.clicked.connect(lambda st, k=keycode: kb.set_key(k.code))
            layout.addWidget(btn)

        tab.setLayout(layout)


KEY_WIDTH = 40
KEY_HEIGHT = KEY_WIDTH
KEY_SPACING = 4


class KeyboardContainer(QWidget):

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
        self.layout = dict()
        self.selected_key = None
        self.selected_row = -1
        self.selected_col = -1

    def rebuild_layers(self, dev):
        self.layers = hid_send(dev, b"\x11")[1]

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

    def rebuild_layout(self, dev):
        """ Load current key mapping from the keyboard """

        for layer in range(self.layers):
            for row, col in self.rowcol.keys():
                data = hid_send(dev, b"\x04" + struct.pack("<BBB", layer, row, col))
                keycode = struct.unpack(">H", data[4:6])[0]
                self.layout[(layer, row, col)] = keycode

    def rebuild(self, dev, data):
        # delete current layout
        for key in self.keys:
            key.deleteLater()
        self.keys = []

        # get number of layers
        self.rebuild_layers(dev)

        # prepare for fetching keymap
        self.rowcol = defaultdict(list)

        serial = KleSerial()
        kb = serial.deserialize(data["layouts"]["keymap"])

        max_w = max_h = 0

        for key in kb.keys:
            widget = ClickableLabel()
            widget.clicked.connect(lambda w=widget: self.select_key(w))

            if key.labels[0] and "," in key.labels[0]:
                row, col = key.labels[0].split(",")
                row, col = int(row), int(col)
                self.rowcol[(row, col)].append(widget)

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
        self.rebuild_layout(dev)
        self.current_layer = 0
        self.refresh_layer_display()

    def refresh_layer_display(self):
        """ Refresh text on key widgets to display data corresponding to current layer """

        for label in self.layer_labels:
            label.setStyleSheet("border: 1px solid black; padding: 5px")
        self.layer_labels[self.current_layer].setStyleSheet("border: 1px solid black; padding: 5px; background-color: black; color: white")

        for (row, col), widgets in self.rowcol.items():
            code = self.layout[(self.current_layer, row, col)]
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
            hid_send(self.dev, struct.pack(">BBBBH", 5, self.current_layer, self.selected_row, self.selected_col, keycode))
            self.layout[(self.current_layer, self.selected_row, self.selected_col)] = keycode

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

        self.tabbed_keycodes = TabbedKeycodes(self.keyboard_container)

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
        self.keyboard_container.dev = None
        idx = self.combobox_devices.currentIndex()
        if idx >= 0:
            self.device = open_device(self.devices[idx])
            self.keyboard_container.dev = self.device
            self.reload_layout()

    def reload_layout(self):
        """ Requests layout data from the current device """

        # get the size
        data = hid_send(self.device, b"\xFE\x01")
        sz = struct.unpack("<I", data[0:4])[0]

        # get the payload
        payload = b""
        block = 0
        while sz > 0:
            data = hid_send(self.device, b"\xFE\x02" + struct.pack("<I", block))
            if sz < MSG_LEN:
                data = data[:sz]
            payload += data
            block += 1
            sz -= MSG_LEN

        payload = json.loads(lzma.decompress(payload))
        self.keyboard_container.rebuild(self.device, payload)


if __name__ == '__main__':
    appctxt = ApplicationContext()       # 1. Instantiate ApplicationContext
    window = MainWindow()
    window.resize(1024, 768)
    window.show()
    exit_code = appctxt.app.exec_()      # 2. Invoke appctxt.app.exec_()
    sys.exit(exit_code)
