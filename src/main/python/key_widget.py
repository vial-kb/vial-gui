from keyboard_widget import KeyboardWidget
from kle_serial import Key
from tabbed_keycodes import TabbedKeycodes


class KeyWidget(KeyboardWidget):

    def __init__(self):
        super().__init__(None)

        self.padding = 1

        self.keycode = 0

        key = Key()
        key.row = key.col = 0
        key.layout_index = key.layout_option = -1
        self.set_keys([key], [])

    def mousePressEvent(self, ev):
        super().mousePressEvent(ev)
        if self.active_key is not None:
            TabbedKeycodes.open_tray(self)
        else:
            TabbedKeycodes.close_tray()
