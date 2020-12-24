# SPDX-License-Identifier: GPL-2.0-or-later
from PyQt5.QtWidgets import QPushButton

from basic_editor import BasicEditor
from macro_optimizer import macro_optimize
from macro_recorder_linux import LinuxRecorder
from vial_device import VialKeyboard


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
        self.keystrokes = macro_optimize(self.keystrokes)
        print(self.keystrokes)

    def on_keystroke(self, keystroke):
        self.keystrokes.append(keystroke)
