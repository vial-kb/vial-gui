# SPDX-License-Identifier: GPL-2.0-or-later
import keyboard

from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QApplication

from keycodes import KEYCODES_BASIC
from macro_key import KeyUp, KeyDown
from util import tr


class WindowsRecorder(QWidget):

    keystroke = pyqtSignal(object)
    stopped = pyqtSignal()

    mapping_qmk_id = {
        "esc": "KC_ESCAPE",
        "1": "KC_1",
        "2": "KC_2",
        "3": "KC_3",
        "4": "KC_4",
        "5": "KC_5",
        "6": "KC_6",
        "7": "KC_7",
        "8": "KC_8",
        "9": "KC_9",
        "0": "KC_0",
        "-": "KC_MINUS",
        "=": "KC_EQUAL",
        "backspace": "KC_BSPACE",
        "tab": "KC_TAB",
        "q": "KC_Q",
        "w": "KC_W",
        "e": "KC_E",
        "r": "KC_R",
        "t": "KC_T",
        "y": "KC_Y",
        "u": "KC_U",
        "i": "KC_I",
        "o": "KC_O",
        "p": "KC_P",
        "[": "KC_LBRACKET",
        "]": "KC_RBRACKET",
        "enter": "KC_ENTER",
        "ctrl": "KC_LCTRL",
        "a": "KC_A",
        "s": "KC_S",
        "d": "KC_D",
        "f": "KC_F",
        "g": "KC_G",
        "h": "KC_H",
        "j": "KC_J",
        "k": "KC_K",
        "l": "KC_L",
        ";": "KC_SCOLON",
        "'": "KC_QUOTE",
        "`": "KC_GRAVE",
        "shift": "KC_LSHIFT",
        "\\": "KC_BSLASH",
        "z": "KC_Z",
        "x": "KC_X",
        "c": "KC_C",
        "v": "KC_V",
        "b": "KC_B",
        "n": "KC_N",
        "m": "KC_M",
        ",": "KC_COMMA",
        ".": "KC_DOT",
        "/": "KC_SLASH",
        "alt": "KC_LALT",
        "space": "KC_SPACE",
        "caps lock": "KC_CAPSLOCK",
        "f1": "KC_F1",
        "f2": "KC_F2",
        "f3": "KC_F3",
        "f4": "KC_F4",
        "f5": "KC_F5",
        "f6": "KC_F6",
        "f7": "KC_F7",
        "f8": "KC_F8",
        "f9": "KC_F9",
        "f10": "KC_F10",
        "f11": "KC_F11",
        "f12": "KC_F12",
        "num lock": "KC_NUMLOCK",
        "scroll lock": "KC_SCROLLLOCK",
        "break": "KC_PAUSE",
        "home": "KC_HOME",
        "up": "KC_UP",
        "page up": "KC_PGUP",
        "left": "KC_LEFT",
        "right": "KC_RIGHT",
        "end": "KC_END",
        "down": "KC_DOWN",
        "page down": "KC_PGDOWN",
        "insert": "KC_INSERT",
        "delete": "KC_DELETE",
        "pause": "KC_PAUSE",
        "windows": "KC_LGUI",
        "menu": "KC_APPLICATION",
        "left windows": "KC_LGUI",
        "right windows": "KC_RGUI",
        "left shift": "KC_LSHIFT",
        "right shift": "KC_RSHIFT",
        "left ctrl": "KC_LCTRL",
        "right ctrl": "KC_RCTRL",
        "left menu": "KC_APPLICATION",
        "right menu": "KC_APPLICATION",
    }

    mapping = dict()

    def __init__(self):
        super().__init__()

        # have to wrap it because apparently there's no other way to get non-shifted key name
        self.old_get_event_names = keyboard._winkeyboard.get_event_names
        keyboard._winkeyboard.get_event_names = self.wrap_get_event_names

        self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.FramelessWindowHint)

        layout = QVBoxLayout()
        btn = QPushButton(tr("MacroRecorder", "Stop recording"))
        btn.clicked.connect(self.on_stop)
        layout.addWidget(btn)

        self.setLayout(layout)

    def wrap_get_event_names(self, scan_code, vk, is_extended, modifiers):
        return self.old_get_event_names(scan_code, vk, is_extended, [])

    def on_stop(self):
        self.stop()

    def start(self):
        self.show()

        center = QApplication.desktop().availableGeometry(self).center()
        self.move(center.x() - self.width() * 0.5, 0)

        keyboard.hook(self.on_key)

    def stop(self):
        keyboard.unhook_all()
        self.hide()
        self.stopped.emit()

    def on_key(self, ev):
        code = self.mapping.get(ev.name)
        if code is not None:
            action2cls = {"down": KeyDown, "up": KeyUp}
            self.keystroke.emit(action2cls[ev.event_type](code))


for windows, qmk in WindowsRecorder.mapping_qmk_id.items():
    for k in KEYCODES_BASIC:
        if k.qmk_id == qmk:
            WindowsRecorder.mapping[windows] = k
            break
    if windows not in WindowsRecorder.mapping:
        raise RuntimeError("Misconfigured - cannot determine QMK keycode value for {}:{} pair".format(windows, qmk))
