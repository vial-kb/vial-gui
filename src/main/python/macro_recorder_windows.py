# SPDX-License-Identifier: GPL-2.0-or-later
import keyboard

from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QApplication

from keycodes import Keycode
from macro_key import KeyUp, KeyDown
from util import tr


class WindowsRecorder(QWidget):

    keystroke = pyqtSignal(object)
    stopped = pyqtSignal()

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
        code = Keycode.find_by_recorder_alias(ev.name)
        if code is not None:
            action2cls = {"down": KeyDown, "up": KeyUp}
            self.keystroke.emit(action2cls[ev.event_type](code))
