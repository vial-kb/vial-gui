from PyQt5.QtCore import pyqtSignal

from any_keycode_dialog import AnyKeycodeDialog
from keyboard_widget import KeyboardWidget
from kle_serial import Key
from tabbed_keycodes import TabbedKeycodes
from util import KeycodeDisplay


class KeyWidget(KeyboardWidget):

    changed = pyqtSignal()

    def __init__(self):
        super().__init__(None)

        self.padding = 1

        self.keycode = 0

        key = Key()
        key.row = key.col = 0
        key.layout_index = key.layout_option = -1
        self.set_keys([key], [])

        self.anykey.connect(self.on_anykey)

    def mousePressEvent(self, ev):
        super().mousePressEvent(ev)
        if self.active_key is not None:
            TabbedKeycodes.open_tray(self)
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
        dlg = AnyKeycodeDialog(self.keycode)
        if dlg.exec_() and dlg.value >= 0:
            self.set_keycode(dlg.value)

    def set_keycode(self, kc):
        if kc == self.keycode:
            return
        self.keycode = kc
        KeycodeDisplay.display_keycode(self.widgets[0], self.keycode)
        self.update()

        self.changed.emit()
