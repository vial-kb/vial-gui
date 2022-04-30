from PyQt5.QtCore import pyqtSignal

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

        self.keycode = 0
        self.set_keycode_filter(keycode_filter)

        key = Key()
        key.row = key.col = 0
        key.layout_index = key.layout_option = -1
        self.set_keys([key], [])

        self.anykey.connect(self.on_anykey)

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
            if keycode > 0xFF:
                return
            keycode = (self.keycode & 0xFF00) | keycode
        self.set_keycode(keycode)

    def on_anykey(self):
        if self.active_key is None:
            return
        self.dlg = AnyKeycodeDialog((self.keycode & 0xFF) if self.active_mask else self.keycode)
        self.dlg.finished.connect(self.on_dlg_finished)
        self.dlg.setModal(True)
        self.dlg.show()

    def on_dlg_finished(self, res):
        if res > 0:
            self.on_keycode_changed(self.dlg.value)

    def set_keycode(self, kc):
        if kc == self.keycode:
            return
        if self.keycode_filter and not self.keycode_filter(kc):
            return
        self.keycode = kc
        KeycodeDisplay.display_keycode(self.widgets[0], self.keycode)
        self.update()

        self.changed.emit()

    def set_keycode_filter(self, keycode_filter):
        if keycode_filter is None:
            keycode_filter = keycode_filter_any
        self.keycode_filter = keycode_filter
