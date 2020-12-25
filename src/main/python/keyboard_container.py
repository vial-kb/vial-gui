# SPDX-License-Identifier: GPL-2.0-or-later

from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QVBoxLayout

from clickable_label import ClickableLabel
from keyboard_widget import KeyboardWidget, EncoderWidget
from keycodes import keycode_label, keycode_tooltip, keycode_is_mask
from constants import LAYER_BTN_STYLE, ACTIVE_LAYER_BTN_STYLE
from util import tr


class KeyboardContainer(QWidget):

    def __init__(self, layout_editor):
        super().__init__()

        self.layout_editor = layout_editor

        self.layout_layers = QHBoxLayout()
        layer_label = QLabel(tr("KeyboardContainer", "Layer"))

        layout_labels_container = QHBoxLayout()
        layout_labels_container.addWidget(layer_label)
        layout_labels_container.addLayout(self.layout_layers)
        layout_labels_container.addStretch()

        # contains the actual keyboard
        self.container = KeyboardWidget(layout_editor)
        self.container.clicked.connect(self.on_key_clicked)

        layout = QVBoxLayout()
        layout.addLayout(layout_labels_container)
        layout.addWidget(self.container)
        layout.setAlignment(self.container, Qt.AlignHCenter)
        self.setLayout(layout)

        self.layer_labels = []
        self.keyboard = None
        self.current_layer = 0

        layout_editor.changed.connect(self.on_layout_changed)

    def rebuild_layers(self):
        # delete old layer labels
        for label in self.layer_labels:
            label.hide()
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

        # get number of layers
        self.rebuild_layers()

        self.container.set_keys(keyboard.keys, keyboard.encoders)

        self.current_layer = 0
        self.on_layout_changed()

    def refresh_layer_display(self):
        """ Refresh text on key widgets to display data corresponding to current layer """

        self.container.update_layout()

        for label in self.layer_labels:
            label.setStyleSheet(LAYER_BTN_STYLE)
        self.layer_labels[self.current_layer].setStyleSheet(ACTIVE_LAYER_BTN_STYLE)

        for widget in self.container.widgets:
            if widget.desc.row is not None:
                code = self.keyboard.layout[(self.current_layer, widget.desc.row, widget.desc.col)]
            else:
                code = self.keyboard.encoder_layout[(self.current_layer, widget.desc.encoder_idx,
                                                     widget.desc.encoder_dir)]
            text = keycode_label(code)
            tooltip = keycode_tooltip(code)
            mask = keycode_is_mask(code)
            mask_text = keycode_label(code & 0xFF)
            if mask:
                text = text.split("\n")[0]
            widget.masked = mask
            widget.setText(text)
            widget.setMaskText(mask_text)
            widget.setToolTip(tooltip)
        self.container.update()
        self.container.updateGeometry()

    def switch_layer(self, idx):
        self.container.deselect()
        self.current_layer = idx
        self.refresh_layer_display()

    def set_key(self, keycode):
        """ Change currently selected key to provided keycode """

        if isinstance(self.container.active_key, EncoderWidget):
            self.set_key_encoder(keycode)
        else:
            self.set_key_matrix(keycode)

        self.container.select_next()

    def set_key_encoder(self, keycode):
        l, i, d = self.current_layer, self.container.active_key.desc.encoder_idx,\
                            self.container.active_key.desc.encoder_dir

        # if masked, ensure that this is a byte-sized keycode
        if self.container.active_mask:
            if keycode > 0xFF:
                return
            keycode = (self.keyboard.encoder_layout[(l, i, d)] & 0xFF00) | keycode

        self.keyboard.set_encoder(l, i, d, keycode)
        self.refresh_layer_display()

    def set_key_matrix(self, keycode):
        l, r, c = self.current_layer, self.container.active_key.desc.row, self.container.active_key.desc.col

        if r >= 0 and c >= 0:
            # if masked, ensure that this is a byte-sized keycode
            if self.container.active_mask:
                if keycode > 0xFF:
                    return
                keycode = (self.keyboard.layout[(l, r, c)] & 0xFF00) | keycode

            self.keyboard.set_key(l, r, c, keycode)
            self.refresh_layer_display()

    def on_key_clicked(self):
        """ Called when a key on the keyboard widget is clicked """
        self.refresh_layer_display()

    def save_layout(self):
        return self.keyboard.save_layout()

    def restore_layout(self, data):
        self.keyboard.restore_layout(data)
        self.refresh_layer_display()

    def on_layout_changed(self):
        if self.keyboard is None:
            return

        self.refresh_layer_display()
        self.keyboard.set_layout_options(self.layout_editor.pack())
