# SPDX-License-Identifier: GPL-2.0-or-later
import sys

from PyQt5 import QtCore
from PyQt5.QtCore import QProcess, pyqtSignal
from PyQt5.QtWidgets import QPushButton, QWidget, QApplication, QVBoxLayout
from fbs_runtime.application_context import is_frozen

from basic_editor import BasicEditor
from keycodes import KEYCODES_BASIC
from macro_key import KeyDown, KeyUp
from util import tr
from vial_device import VialKeyboard


class LinuxRecorder(QWidget):

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
    }

    mapping = dict()

    def __init__(self):
        super().__init__()

        self.process = QProcess()

        self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.X11BypassWindowManagerHint)

        layout = QVBoxLayout()
        btn = QPushButton(tr("MacroRecorder", "Stop recording"))
        btn.clicked.connect(self.on_stop)
        layout.addWidget(btn)

        self.setLayout(layout)

    def start(self):
        self.show()

        center = QApplication.desktop().availableGeometry(self).center()
        self.move(center.x() - self.width() * 0.5, 0)

        args = [sys.executable]
        if is_frozen():
            args += sys.argv[1:]
        else:
            args += sys.argv
        args += ["--linux-recorder"]

        self.process.readyReadStandardOutput.connect(self.on_output)
        self.process.start("pkexec", args, QProcess.Unbuffered | QProcess.ReadWrite)

    def on_stop(self):
        self.process.write(b"q")
        self.process.waitForFinished()
        self.process.close()
        self.hide()
        self.stopped.emit()

    def action2cls(self, action):
        if action == "up":
            return KeyUp
        elif action == "down":
            return KeyDown
        else:
            raise RuntimeError("unexpected action={}".format(action))

    def key2code(self, key):
        return self.mapping.get(key, None)

    def on_output(self):
        if self.process.canReadLine():
            line = bytes(self.process.readLine()).decode("utf-8")
            action, key = line.strip().split(":")
            code = self.key2code(key)
            if code is not None:
                self.keystroke.emit(self.action2cls(action)(code))


for linux, qmk in LinuxRecorder.mapping_qmk_id.items():
    for k in KEYCODES_BASIC:
        if k.qmk_id == qmk:
            LinuxRecorder.mapping[linux] = k
            break
    if linux not in LinuxRecorder.mapping:
        raise RuntimeError("Misconfigured - cannot determine QMK keycode value for {}:{} pair".format(linux, qmk))


class MacroRecorder(BasicEditor):

    def __init__(self):
        super().__init__()

        self.keystrokes = []

        self.recorder = LinuxRecorder()
        self.recorder.keystroke.connect(self.on_keystroke)
        self.recorder.stopped.connect(self.on_stop)
        self.recording = False

        btn = QPushButton("Record")
        btn.clicked.connect(self.on_record_clicked)
        self.addWidget(btn)

    def valid(self):
        return isinstance(self.device, VialKeyboard)

    def rebuild(self, device):
        super().rebuild(device)
        if not self.valid():
            return

    def on_record_clicked(self):
        self.keystrokes = []
        self.recorder.start()

    def on_stop(self):
        print(self.keystrokes)

    def on_keystroke(self, keystroke):
        self.keystrokes.append(keystroke)
