import sys

from PyQt5.QtCore import QProcess
from PyQt5.QtWidgets import QPushButton, QWidget
from fbs_runtime.application_context import is_frozen

from basic_editor import BasicEditor
from vial_device import VialKeyboard


class LinuxRecorder:

    def __init__(self):
        self.process = None

    def start(self):
        self.process = QProcess()
        args = [sys.executable]
        if is_frozen():
            args += sys.argv[1:]
        else:
            args += sys.argv
        args += ["--linux-recorder"]

        self.process.start("pkexec", args)
        self.process.waitForFinished()
        print(self.process.readAll())


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
