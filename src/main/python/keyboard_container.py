# SPDX-License-Identifier: GPL-2.0-or-later

from collections import defaultdict

from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QVBoxLayout

from clickable_label import ClickableLabel
from keycodes import keycode_label, keycode_tooltip
from constants import KEY_WIDTH, KEY_SPACING, KEY_HEIGHT, LAYER_BTN_STYLE, ACTIVE_LAYER_BTN_STYLE, KEY_NORMAL_STYLE, \
    KEY_ACTIVE_STYLE
from util import tr


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
        self.keyboard = None
        self.current_layer = 0

    def rebuild_layers(self):
        self.number_layers_changed.emit()

        # delete old layer labels
        for label in self.layer_labels:
            label.deleteLater()
        self.layer_labels = []

        # create new layer labels
        for x in range(self.keyboard.layers):
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
            widget.clicked.connect(lambda w=widget: self.on_key_clicked(w))

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
            label.setStyleSheet(LAYER_BTN_STYLE)
        self.layer_labels[self.current_layer].setStyleSheet(ACTIVE_LAYER_BTN_STYLE)

        for (row, col), widgets in self.rowcol.items():
            code = self.keyboard.layout[(self.current_layer, row, col)]
            text = keycode_label(code)
            tooltip = keycode_tooltip(code)
            for widget in widgets:
                widget.setStyleSheet(KEY_NORMAL_STYLE)
                if widget == self.selected_key:
                    widget.setStyleSheet(KEY_ACTIVE_STYLE)
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

    def on_key_clicked(self, widget):
        """ Change which key is currently selected """

        if self.selected_key == widget:
            self.selected_key = None
        else:
            self.selected_key = widget

        for (row, col), widgets in self.rowcol.items():
            if widget in widgets:
                self.selected_row = row
                self.selected_col = col
                break
        self.refresh_layer_display()

    def save_layout(self):
        return self.keyboard.save_layout()

    def restore_layout(self, data):
        self.keyboard.restore_layout(data)
        self.refresh_layer_display()
