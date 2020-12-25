# SPDX-License-Identifier: GPL-2.0-or-later

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QPushButton, QGridLayout, QHBoxLayout, QToolButton, QVBoxLayout, \
    QTabWidget, QWidget, QLabel

from basic_editor import BasicEditor
from keycodes import find_keycode
from macro_action import ActionText, ActionSequence, ActionTap
from macro_key import KeyString
from macro_line import MacroLine
from macro_optimizer import macro_optimize
from macro_recorder_linux import LinuxRecorder
from util import tr
from vial_device import VialKeyboard


class MacroTab(QVBoxLayout):

    changed = pyqtSignal()

    def __init__(self):
        super().__init__()

        self.lines = []

        self.container = QGridLayout()

        btn_record = QToolButton()
        btn_record.setText(tr("MacroRecorder", "Record macro"))
        btn_record.setToolButtonStyle(Qt.ToolButtonTextOnly)
        # btn_record.clicked.connect(self.on_record)

        btn_add = QToolButton()
        btn_add.setText(tr("MacroRecorder", "Add action"))
        btn_add.setToolButtonStyle(Qt.ToolButtonTextOnly)
        btn_add.clicked.connect(self.on_add)

        btn_tap_enter = QToolButton()
        btn_tap_enter.setText(tr("MacroRecorder", "Tap Enter"))
        btn_tap_enter.setToolButtonStyle(Qt.ToolButtonTextOnly)
        btn_tap_enter.clicked.connect(self.on_tap_enter)

        layout_buttons = QHBoxLayout()
        layout_buttons.addStretch()
        layout_buttons.addWidget(btn_add)
        layout_buttons.addWidget(btn_tap_enter)
        layout_buttons.addWidget(btn_record)

        self.addLayout(self.container)
        self.addLayout(layout_buttons)
        self.addWidget(btn_add)
        self.addStretch()

    def add_action(self, act):
        line = MacroLine(self, act)
        line.changed.connect(self.on_change)
        self.lines.append(line)
        line.insert(self.container.rowCount())
        self.changed.emit()

    def on_add(self):
        self.add_action(ActionText(self.container))

    def on_remove(self, obj):
        for line in self.lines:
            if line == obj:
                line.remove()
                line.delete()
        self.lines.remove(obj)
        for line in self.lines:
            line.remove()
        for x, line in enumerate(self.lines):
            line.insert(x)
        self.changed.emit()

    def on_move(self, obj, offset):
        if offset == 0:
            return
        index = self.lines.index(obj)
        if index + offset < 0 or index + offset >= len(self.lines):
            return
        other = self.lines.index(self.lines[index + offset])
        self.lines[index].remove()
        self.lines[other].remove()
        self.lines[index], self.lines[other] = self.lines[other], self.lines[index]
        self.lines[index].insert(index)
        self.lines[other].insert(other)
        self.changed.emit()

    def serialize(self):
        out = b""
        for line in self.lines:
            out += line.serialize()
        return out

    def on_change(self):
        self.changed.emit()

    def on_tap_enter(self):
        self.add_action(ActionTap(self.container, [find_keycode(0x28)]))


class MacroRecorder(BasicEditor):

    def __init__(self):
        super().__init__()

        self.keystrokes = []
        self.macro_tabs = []

        self.recorder = LinuxRecorder()
        self.recorder.keystroke.connect(self.on_keystroke)
        self.recorder.stopped.connect(self.on_stop)
        self.recording = False

        self.tabs = QTabWidget()
        for x in range(32):
            tab = MacroTab()
            tab.changed.connect(self.on_change)
            self.macro_tabs.append(tab)
            w = QWidget()
            w.setLayout(tab)
            self.tabs.addTab(w, "Macro {}".format(x + 1))

        self.lbl_memory = QLabel()

        buttons = QHBoxLayout()
        buttons.addWidget(self.lbl_memory)
        buttons.addStretch()
        buttons.addWidget(QPushButton("Save"))
        buttons.addWidget(QPushButton("Revert"))

        self.addWidget(self.tabs)
        self.addLayout(buttons)

        self.on_change()

    def valid(self):
        return isinstance(self.device, VialKeyboard)

    def rebuild(self, device):
        super().rebuild(device)
        if not self.valid():
            return

    def on_record(self):
        if not self.recording:
            self.recording = True
            self.keystrokes = []
            self.recorder.start()
        else:
            self.recording = False
            self.recorder.stop()

    def on_stop(self):
        self.keystrokes = macro_optimize(self.keystrokes)
        for k in self.keystrokes:
            if isinstance(k, KeyString):
                self.lines.append(MacroLine(self, ActionText(self.container, k.string)))
            else:
                self.lines.append(MacroLine(self, ActionSequence(self.container, [k])))

        for x, line in enumerate(self.lines):
            line.insert(x)
        print(self.keystrokes)

    def on_keystroke(self, keystroke):
        self.keystrokes.append(keystroke)

    def on_change(self):
        memory = 0
        for x, macro in enumerate(self.macro_tabs):
            memory += len(macro.serialize())
        self.lbl_memory.setText("Memory used by macros: {}/345".format(memory))
