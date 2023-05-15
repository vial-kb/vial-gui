from PyQt5.QtCore import pyqtSignal

from keycodes.keycodes import Keycode
from any_keycode_dialog import AnyKeycodeDialog
from widgets.keyboard_widget import KeyboardWidget
from kle_serial import Key
from tabbed_keycodes import TabbedKeycodes, keycode_filter_masked, keycode_filter_any
from util import KeycodeDisplay


class KeyWidget(KeyboardWidget):

    changed = pyqtSignal()

    def __init__(self, keycode_filter=None):
        super().__init__(None)

        self.padding = 1

        self.keycode = "KC_NO"
        self.set_keycode_filter(keycode_filter)

        key = Key()
        key.row = key.col = 0
        key.layout_index = key.layout_option = -1
        self.set_keys([key], [])

        self.anykey.connect(self.on_anykey)
        KeycodeDisplay.notify_keymap_override(self)

    def delete(self):
        KeycodeDisplay.unregister_keymap_override(self)
        super().delete()

    def deleteLater(self):
        KeycodeDisplay.unregister_keymap_override(self)
        super().deleteLater()

    def mousePressEvent(self, ev):
        super().mousePressEvent(ev)
        if self.active_key is not None:
            keycode_filter = self.keycode_filter
            if self.active_mask:
                keycode_filter = keycode_filter_masked
            TabbedKeycodes.open_tray(self, keycode_filter)
        else:
            TabbedKeycodes.close_tray()

    def mouseReleaseEvent(self, ev):
        ev.accept()

    def on_keycode_changed(self, keycode):
        """ Unlike set_keycode, this handles setting masked keycode inside the mask """

        if self.active_mask:
            if not Keycode.is_basic(keycode):
                return
            kc = Keycode.find_outer_keycode(self.keycode)
            if kc is None:
                return
            keycode = kc.qmk_id.replace("(kc)", "({})".format(keycode))
        self.set_keycode(keycode)

    def on_anykey(self):
        if self.active_key is None:
            return
        if self.active_mask:
            kc = Keycode.find_inner_keycode(self.keycode).qmk_id
        else:
            kc = self.keycode
        self.dlg = AnyKeycodeDialog(kc)
        self.dlg.finished.connect(self.on_dlg_finished)
        self.dlg.setModal(True)
        self.dlg.show()

    def on_dlg_finished(self, res):
        if res > 0:
            self.on_keycode_changed(self.dlg.value)

    def update_display(self):
        KeycodeDisplay.display_keycode(self.widgets[0], self.keycode)
        self.update()

    def set_keycode(self, kc):
        if kc == self.keycode:
            return
        if self.keycode_filter and not self.keycode_filter(kc):
            return
        self.keycode = kc
        self.update_display()

        self.changed.emit()

    def set_keycode_filter(self, keycode_filter):
        if keycode_filter is None:
            keycode_filter = keycode_filter_any
        self.keycode_filter = keycode_filter

    def on_keymap_override(self):
        self.update_display()
