# SPDX-License-Identifier: GPL-2.0-or-later
import sys
import os

from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal, QProcess
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QApplication
from fbs_runtime.application_context import is_frozen

from keycodes import Keycode
from macro_key import KeyUp, KeyDown
from util import tr


class LinuxRecorder(QWidget):

    keystroke = pyqtSignal(object)
    stopped = pyqtSignal()

    def __init__(self):
        super().__init__()

        self.process = QProcess()
        self.process.readyReadStandardOutput.connect(self.on_output)

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
        if os.getenv("APPIMAGE"):
            args = [os.getenv("APPIMAGE")]
        elif is_frozen():
            args += sys.argv[1:]
        else:
            args += sys.argv
        args += ["--linux-recorder"]

        self.process.start("pkexec", args, QProcess.Unbuffered | QProcess.ReadWrite)

    def on_stop(self):
        self.stop()

    def stop(self):
        self.process.write(b"q")
        self.process.waitForFinished()
        self.process.close()
        self.hide()
        self.stopped.emit()

    def on_output(self):
        if self.process.canReadLine():
            line = bytes(self.process.readLine()).decode("utf-8")
            action, key = line.strip().split(":")
            code = Keycode.find_by_recorder_alias(key)
            if code is not None:
                action2cls = {"down": KeyDown, "up": KeyUp}
                self.keystroke.emit(action2cls[action](code))
