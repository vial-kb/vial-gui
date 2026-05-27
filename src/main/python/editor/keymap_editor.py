# SPDX-License-Identifier: GPL-2.0-or-later
import json

from PyQt5.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QMessageBox, QWidget, QCheckBox, QApplication
from PyQt5.QtCore import Qt, QSettings, pyqtSignal

from any_keycode_dialog import AnyKeycodeDialog
from editor.basic_editor import BasicEditor
from widgets.keyboard_widget import KeyboardWidget, EncoderWidget
from keycodes.keycodes import Keycode
from widgets.square_button import SquareButton
from tabbed_keycodes import TabbedKeycodes, keycode_filter_masked
from util import tr, KeycodeDisplay
from vial_device import VialKeyboard


class ClickableWidget(QWidget):

    clicked = pyqtSignal()

    def mousePressEvent(self, evt):
        super().mousePressEvent(evt)
        self.clicked.emit()


class KeymapEditor(BasicEditor):

    def __init__(self, layout_editor):
        super().__init__()

        self.layout_editor = layout_editor

        self.layout_layers = QHBoxLayout()
        self.layout_size = QVBoxLayout()
        self.layout_layers_toggles = QHBoxLayout()
        layer_label = QLabel(tr("KeymapEditor", "Layer"))
        self.active_label = QLabel(tr("KeymapEditor", "Active"))

        self.chk_show_inherited = QCheckBox(tr("KeymapEditor", "Show inherited keys"))
        self.chk_show_inherited.setFocusPolicy(Qt.NoFocus)
        self.chk_show_inherited.setToolTip(tr("KeymapEditor",
            "Show what KC_TRNS keys inherit from lower layers"))
        saved = QSettings("Vial", "Vial").value("keymap/show_inherited", False, bool)
        self.chk_show_inherited.setChecked(saved)
        self.chk_show_inherited.stateChanged.connect(self.on_show_inherited_changed)

        layout_top_row = QHBoxLayout()
        layout_top_row.addWidget(layer_label)
        layout_top_row.addLayout(self.layout_layers)
        layout_top_row.addStretch()
        layout_top_row.addWidget(self.chk_show_inherited)
        layout_top_row.addLayout(self.layout_size)

        self.layout_toggle_row = QHBoxLayout()
        self.layout_toggle_row.addWidget(self.active_label)
        self.layout_toggle_row.addLayout(self.layout_layers_toggles)
        self.layout_toggle_row.addStretch()

        layout_labels_container = QVBoxLayout()
        layout_labels_container.addLayout(layout_top_row)
        layout_labels_container.addLayout(self.layout_toggle_row)

        # contains the actual keyboard
        self.container = KeyboardWidget(layout_editor)
        self.container.clicked.connect(self.on_key_clicked)
        self.container.deselected.connect(self.on_key_deselected)

        layout = QVBoxLayout()
        layout.addLayout(layout_labels_container)
        layout.addWidget(self.container)
        layout.setAlignment(self.container, Qt.AlignHCenter)
        w = ClickableWidget()
        w.setLayout(layout)
        w.clicked.connect(self.on_empty_space_clicked)

        self.layer_buttons = []
        self.layer_toggle_buttons = []
        self.layer_toggle_cells = []
        self.active_layers = set()
        self.keyboard = None
        self.current_layer = 0

        layout_editor.changed.connect(self.on_layout_changed)

        self.container.anykey.connect(self.on_any_keycode)

        self.tabbed_keycodes = TabbedKeycodes()
        self.tabbed_keycodes.keycode_changed.connect(self.on_keycode_changed)
        self.tabbed_keycodes.anykey.connect(self.on_any_keycode)

        self.addWidget(w)
        self.addWidget(self.tabbed_keycodes)

        self.device = None
        KeycodeDisplay.notify_keymap_override(self)

    def on_empty_space_clicked(self):
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

        # delete old toggle checkboxes
        for cb in self.layer_toggle_buttons:
            cb.hide()
            cb.deleteLater()
        self.layer_toggle_buttons = []
        for cell in getattr(self, "layer_toggle_cells", []):
            cell.hide()
            cell.deleteLater()
        self.layer_toggle_cells = []

        # create new layer labels and toggles
        self.active_layers = set(range(self.keyboard.layers))
        for x in range(self.keyboard.layers):
            btn = SquareButton(str(x))
            btn.setFocusPolicy(Qt.NoFocus)
            btn.setRelSize(1.667)
            btn.setCheckable(True)
            btn.clicked.connect(lambda state, idx=x: self.switch_layer(idx))
            self.layout_layers.addWidget(btn)
            self.layer_buttons.append(btn)

            cb = QCheckBox()
            cb.setChecked(True)
            cb.setFocusPolicy(Qt.NoFocus)
            cb.setToolTip(tr("KeymapEditor", "Include layer {} when resolving KC_TRNS").format(x))
            if x == 0:
                cb.setEnabled(False)
            else:
                cb.stateChanged.connect(lambda state, idx=x: self.on_toggle_layer(idx, state))
            # wrap in a fixed-width container to align with layer buttons above
            cell = QWidget()
            cell_size = int(round(QApplication.fontMetrics().height() * 1.667))
            cell.setFixedWidth(cell_size)
            cell_layout = QHBoxLayout(cell)
            cell_layout.setContentsMargins(0, 0, 0, 0)
            cell_layout.addWidget(cb, 0, Qt.AlignCenter)
            self.layout_layers_toggles.addWidget(cell)
            self.layer_toggle_buttons.append(cb)
            self.layer_toggle_cells.append(cell)

        self._update_toggle_row_visibility()

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

            self.tabbed_keycodes.recreate_keycode_buttons()
            TabbedKeycodes.tray.recreate_keycode_buttons()
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

    def on_any_keycode(self):
        if self.container.active_key is None:
            return
        current_code = self.code_for_widget(self.container.active_key)
        if self.container.active_mask:
            kc = Keycode.find_inner_keycode(current_code)
            current_code = kc.qmk_id

        self.dlg = AnyKeycodeDialog(current_code)
        self.dlg.finished.connect(self.on_dlg_finished)
        self.dlg.setModal(True)
        self.dlg.show()

    def on_dlg_finished(self, res):
        if res > 0:
            self.on_keycode_changed(self.dlg.value)

    def code_for_widget(self, widget):
        if widget.desc.row is not None:
            return self.keyboard.layout[(self.current_layer, widget.desc.row, widget.desc.col)]
        else:
            return self.keyboard.encoder_layout[(self.current_layer, widget.desc.encoder_idx,
                                                 widget.desc.encoder_dir)]

    def on_show_inherited_changed(self, state):
        QSettings("Vial", "Vial").setValue("keymap/show_inherited", bool(state))
        self._update_toggle_row_visibility()
        self.refresh_layer_display()

    def _update_toggle_row_visibility(self):
        show = self.chk_show_inherited.isChecked() and self.keyboard is not None and self.keyboard.layers > 1
        self.active_label.setVisible(show)
        for cell in self.layer_toggle_cells:
            cell.setVisible(show)

    def on_toggle_layer(self, idx, state):
        if state:
            self.active_layers.add(idx)
        else:
            self.active_layers.discard(idx)
        self.refresh_layer_display()

    def resolve_trns(self, widget, layer):
        """ Walk downward through active layers to find what KC_TRNS inherits from """
        candidates = sorted([l for l in self.active_layers if l < layer], reverse=True)
        for l in candidates:
            if widget.desc.row is not None:
                code = self.keyboard.layout.get((l, widget.desc.row, widget.desc.col))
            else:
                code = self.keyboard.encoder_layout.get(
                    (l, widget.desc.encoder_idx, widget.desc.encoder_dir))
            if code is not None and code != "KC_TRNS":
                return code, l
        return None

    def refresh_layer_display(self):
        """ Refresh text on key widgets to display data corresponding to current layer """

        self.container.update_layout()

        for idx, btn in enumerate(self.layer_buttons):
            btn.setEnabled(idx != self.current_layer)
            btn.setChecked(idx == self.current_layer)

        for widget in self.container.widgets:
            code = self.code_for_widget(widget)
            trns_resolved = None
            if self.chk_show_inherited.isChecked() and code == "KC_TRNS" and self.current_layer > 0:
                trns_resolved = self.resolve_trns(widget, self.current_layer)
            KeycodeDisplay.display_keycode(widget, code, trns_resolved)
        self.container.update()
        self.container.updateGeometry()

    def switch_layer(self, idx):
        self.container.deselect()
        self.current_layer = idx
        self.refresh_layer_display()

    def set_key(self, keycode):
        """ Change currently selected key to provided keycode """

        if self.container.active_key is None:
            return

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
            if not Keycode.is_basic(keycode):
                return
            kc = Keycode.find_outer_keycode(self.keyboard.encoder_layout[(l, i, d)])
            if kc is None:
                return
            keycode = kc.qmk_id.replace("(kc)", "({})".format(keycode))

        self.keyboard.set_encoder(l, i, d, keycode)
        self.refresh_layer_display()

    def set_key_matrix(self, keycode):
        l, r, c = self.current_layer, self.container.active_key.desc.row, self.container.active_key.desc.col

        if r >= 0 and c >= 0:
            # if masked, ensure that this is a byte-sized keycode
            if self.container.active_mask:
                if not Keycode.is_basic(keycode):
                    return
                kc = Keycode.find_outer_keycode(self.keyboard.layout[(l, r, c)])
                if kc is None:
                    return
                keycode = kc.qmk_id.replace("(kc)", "({})".format(keycode))

            self.keyboard.set_key(l, r, c, keycode)
            self.refresh_layer_display()

    def on_key_clicked(self):
        """ Called when a key on the keyboard widget is clicked """
        self.refresh_layer_display()
        if self.container.active_mask:
            self.tabbed_keycodes.set_keycode_filter(keycode_filter_masked)
        else:
            self.tabbed_keycodes.set_keycode_filter(None)

    def on_key_deselected(self):
        self.tabbed_keycodes.set_keycode_filter(None)

    def on_layout_changed(self):
        if self.keyboard is None:
            return

        self.refresh_layer_display()
        self.keyboard.set_layout_options(self.layout_editor.pack())

    def on_keymap_override(self):
        self.refresh_layer_display()
