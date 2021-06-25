# SPDX-License-Identifier: GPL-2.0-or-later
import json

from PyQt5.QtGui import QPalette
from PyQt5.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QMessageBox, QApplication
from PyQt5.QtCore import Qt

from any_keycode_dialog import AnyKeycodeDialog
from basic_editor import BasicEditor
from keyboard_widget import KeyboardWidget, EncoderWidget
from keycodes import recreate_keyboard_keycodes, Keycode
from keymaps import KEYMAPS
from square_button import SquareButton
from tabbed_keycodes import TabbedKeycodes
from util import tr
from vial_device import VialKeyboard


class KeymapEditor(BasicEditor):

    def __init__(self, layout_editor):
        super().__init__()

        self.layout_editor = layout_editor

        self.layout_layers = QHBoxLayout()
        self.layout_size = QVBoxLayout()
        layer_label = QLabel(tr("KeymapEditor", "Layer"))

        layout_labels_container = QHBoxLayout()
        layout_labels_container.addWidget(layer_label)
        layout_labels_container.addLayout(self.layout_layers)
        layout_labels_container.addStretch()
        layout_labels_container.addLayout(self.layout_size)

        # contains the actual keyboard
        self.container = KeyboardWidget(layout_editor)
        self.container.clicked.connect(self.on_key_clicked)

        layout = QVBoxLayout()
        layout.addLayout(layout_labels_container)
        layout.addWidget(self.container)
        layout.setAlignment(self.container, Qt.AlignHCenter)

        self.layer_buttons = []
        self.keyboard = None
        self.current_layer = 0

        layout_editor.changed.connect(self.on_layout_changed)

        self.keymap_override = KEYMAPS[0][1]

        self.container.anykey.connect(self.on_any_keycode)

        self.tabbed_keycodes = TabbedKeycodes()
        self.tabbed_keycodes.keycode_changed.connect(self.on_keycode_changed)
        self.tabbed_keycodes.anykey.connect(self.on_any_keycode)

        self.addLayout(layout)
        self.addWidget(self.tabbed_keycodes)

        self.device = None

    def on_container_clicked(self):
        """ Called when a mouse click event is bubbled up to the editor's container """
        self.container.deselect()
        self.container.update()

    def on_keycode_changed(self, code):
        self.set_key(code)

    def rebuild_layers(self):
        # delete old layer labels
        for label in self.layer_buttons:
            label.hide()
            label.deleteLater()
        self.layer_buttons = []

        # create new layer labels
        for x in range(self.keyboard.layers):
            btn = SquareButton(str(x))
            btn.setFocusPolicy(Qt.NoFocus)
            btn.setRelSize(1.667)
            btn.setCheckable(True)
            btn.clicked.connect(lambda state, idx=x: self.switch_layer(idx))
            self.layout_layers.addWidget(btn)
            self.layer_buttons.append(btn)
        for x in range(0,2):
            btn = SquareButton("-") if x else SquareButton("+")
            btn.setFocusPolicy(Qt.NoFocus)
            btn.setCheckable(False)
            btn.clicked.connect(lambda state, idx=x: self.adjust_size(idx))
            self.layout_size.addWidget(btn)
            self.layer_buttons.append(btn)

    def adjust_size(self, minus):
        if minus:
            self.container.set_scale(self.container.get_scale() - 0.1)
        else:
            self.container.set_scale(self.container.get_scale() + 0.1)
        self.refresh_layer_display()

    def rebuild(self, device):
        super().rebuild(device)
        if self.valid():
            self.keyboard = device.keyboard

            # get number of layers
            self.rebuild_layers()

            self.container.set_keys(self.keyboard.keys, self.keyboard.encoders)

            self.current_layer = 0
            self.on_layout_changed()

            recreate_keyboard_keycodes(self.keyboard)
            self.tabbed_keycodes.recreate_keycode_buttons()
            self.refresh_layer_display()
        self.container.setEnabled(self.valid())

    def valid(self):
        return isinstance(self.device, VialKeyboard)

    def save_layout(self):
        return self.keyboard.save_layout()

    def restore_layout(self, data):
        if json.loads(data.decode("utf-8")).get("uid") != self.keyboard.keyboard_id:
            ret = QMessageBox.question(self.widget(), "",
                                       tr("KeymapEditor", "Saved keymap belongs to a different keyboard,"
                                                          " are you sure you want to continue?"),
                                       QMessageBox.Yes | QMessageBox.No)
            if ret != QMessageBox.Yes:
                return
        self.keyboard.restore_layout(data)
        self.refresh_layer_display()

    def set_keymap_override(self, override):
        self.keymap_override = override
        self.refresh_layer_display()
        self.tabbed_keycodes.set_keymap_override(override)

    def on_any_keycode(self):
        if self.container.active_key is None:
            return
        current_code = self.code_for_widget(self.container.active_key)
        dlg = AnyKeycodeDialog(current_code)
        if dlg.exec_() and dlg.value >= 0:
            self.on_keycode_changed(dlg.value)

    def code_is_overriden(self, code):
        """ Check whether a country-specific keymap overrides a code """
        key = Keycode.find_outer_keycode(code)
        return key is not None and key.qmk_id in self.keymap_override

    def get_label(self, code):
        """ Get label for a specific keycode """
        if self.code_is_overriden(code):
            return self.keymap_override[Keycode.find_outer_keycode(code).qmk_id]
        return Keycode.label(code)

    def code_for_widget(self, widget):
        if widget.desc.row is not None:
            return self.keyboard.layout[(self.current_layer, widget.desc.row, widget.desc.col)]
        else:
            return self.keyboard.encoder_layout[(self.current_layer, widget.desc.encoder_idx,
                                                 widget.desc.encoder_dir)]

    def refresh_layer_display(self):
        """ Refresh text on key widgets to display data corresponding to current layer """

        self.container.update_layout()

        for idx, btn in enumerate(self.layer_buttons):
            btn.setEnabled(idx != self.current_layer)
            btn.setChecked(idx == self.current_layer)

        for widget in self.container.widgets:
            code = self.code_for_widget(widget)
            text = self.get_label(code)
            tooltip = Keycode.tooltip(code)
            mask = Keycode.is_mask(code)
            mask_text = self.get_label(code & 0xFF)
            if mask:
                text = text.split("\n")[0]
            widget.masked = mask
            widget.setText(text)
            widget.setMaskText(mask_text)
            widget.setToolTip(tooltip)
            if self.code_is_overriden(code):
                widget.setColor(QApplication.palette().color(QPalette.Link))
            else:
                widget.setColor(None)
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

    def on_layout_changed(self):
        if self.keyboard is None:
            return

        self.refresh_layer_display()
        self.keyboard.set_layout_options(self.layout_editor.pack())
