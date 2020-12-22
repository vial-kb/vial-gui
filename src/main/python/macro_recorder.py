import sys

from PyQt5 import QtCore
from PyQt5.QtCore import QProcess
from PyQt5.QtWidgets import QPushButton, QWidget, QApplication, QVBoxLayout
from fbs_runtime.application_context import is_frozen

from basic_editor import BasicEditor
from util import tr
from vial_device import VialKeyboard


class LinuxRecorder(QWidget):

    def __init__(self):
        super().__init__()

        self.process = None

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

        self.process = QProcess()
        args = [sys.executable]
        if is_frozen():
            args += sys.argv[1:]
        else:
            args += sys.argv
        args += ["--linux-recorder"]

        self.process.start("pkexec", args, QProcess.Unbuffered | QProcess.ReadWrite)

    def on_stop(self):
        self.process.write(b"q")
        self.hide()


class MacroRecorder(BasicEditor):

    def __init__(self):
        super().__init__()

        self.recorder = LinuxRecorder()
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
        self.recorder.start()
