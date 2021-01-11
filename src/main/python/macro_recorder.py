# SPDX-License-Identifier: GPL-2.0-or-later
import sys

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QPushButton, QGridLayout, QHBoxLayout, QToolButton, QVBoxLayout, \
    QTabWidget, QWidget, QLabel, QMenu, QScrollArea, QFrame

from basic_editor import BasicEditor
from keycodes import find_keycode
from macro_action import ActionText, ActionTap, ActionDown, ActionUp, SS_TAP_CODE, SS_DOWN_CODE, SS_UP_CODE
from macro_key import KeyString, KeyDown, KeyUp, KeyTap
from macro_line import MacroLine
from macro_optimizer import macro_optimize
from unlocker import Unlocker
from util import tr
from vial_device import VialKeyboard


class MacroTab(QVBoxLayout):

    changed = pyqtSignal()
    record = pyqtSignal(object, bool)
    record_stop = pyqtSignal()

    def __init__(self, enable_recorder):
        super().__init__()

        self.lines = []

        self.container = QGridLayout()

        menu_record = QMenu()
        menu_record.addAction(tr("MacroRecorder", "Append to current"))\
            .triggered.connect(lambda: self.record.emit(self, True))
        menu_record.addAction(tr("MacroRecorder", "Replace everything"))\
            .triggered.connect(lambda: self.record.emit(self, False))

        self.btn_record = QPushButton(tr("MacroRecorder", "Record macro"))
        self.btn_record.setMenu(menu_record)
        if not enable_recorder:
            self.btn_record.hide()

        self.btn_record_stop = QPushButton(tr("MacroRecorder", "Stop recording"))
        self.btn_record_stop.clicked.connect(lambda: self.record_stop.emit())
        self.btn_record_stop.hide()

        self.btn_add = QToolButton()
        self.btn_add.setText(tr("MacroRecorder", "Add action"))
        self.btn_add.setToolButtonStyle(Qt.ToolButtonTextOnly)
        self.btn_add.clicked.connect(self.on_add)

        self.btn_tap_enter = QToolButton()
        self.btn_tap_enter.setText(tr("MacroRecorder", "Tap Enter"))
        self.btn_tap_enter.setToolButtonStyle(Qt.ToolButtonTextOnly)
        self.btn_tap_enter.clicked.connect(self.on_tap_enter)

        layout_buttons = QHBoxLayout()
        layout_buttons.addStretch()
        layout_buttons.addWidget(self.btn_add)
        layout_buttons.addWidget(self.btn_tap_enter)
        layout_buttons.addWidget(self.btn_record)
        layout_buttons.addWidget(self.btn_record_stop)

        vbox = QVBoxLayout()
        vbox.addLayout(self.container)
        vbox.addStretch()

        w = QWidget()
        w.setLayout(vbox)
        w.setObjectName("w")
        scroll = QScrollArea()
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("QScrollArea { background-color:transparent; }")
        w.setStyleSheet("#w { background-color:transparent; }")
        scroll.setWidgetResizable(True)
        scroll.setWidget(w)

        self.addWidget(scroll)
        self.addLayout(layout_buttons)

    def add_action(self, act):
        line = MacroLine(self, act)
        line.changed.connect(self.on_change)
        self.lines.append(line)
        line.insert(len(self.lines) - 1)
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

    def clear(self):
        for line in self.lines[:]:
            self.on_remove(line)

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

    def deserialize(self, data):
        self.clear()

        sequence = []
        data = bytearray(data)
        while len(data) > 0:
            if data[0] in [SS_TAP_CODE, SS_DOWN_CODE, SS_UP_CODE]:
                # append to previous *_CODE if it's the same type, otherwise create a new entry
                if len(sequence) > 0 and isinstance(sequence[-1], list) and sequence[-1][0] == data[0]:
                    sequence[-1][1].append(data[1])
                else:
                    sequence.append([data[0], [data[1]]])

                data.pop(0)
                data.pop(0)
            else:
                # append to previous string if it is a string, otherwise create a new entry
                ch = chr(data[0])
                if len(sequence) > 0 and isinstance(sequence[-1], str):
                    sequence[-1] += ch
                else:
                    sequence.append(ch)
                data.pop(0)
        for s in sequence:
            if isinstance(s, str):
                self.add_action(ActionText(self.container, s))
            else:
                # map integer values to qmk keycodes
                keycodes = []
                for code in s[1]:
                    keycode = find_keycode(code)
                    if keycode:
                        keycodes.append(keycode)
                cls = {SS_TAP_CODE: ActionTap, SS_DOWN_CODE: ActionDown, SS_UP_CODE: ActionUp}[s[0]]
                self.add_action(cls(self.container, keycodes))

    def on_change(self):
        self.changed.emit()

    def on_tap_enter(self):
        self.add_action(ActionTap(self.container, [find_keycode(0x28)]))

    def pre_record(self):
        self.btn_record.hide()
        self.btn_add.hide()
        self.btn_tap_enter.hide()
        self.btn_record_stop.show()

    def post_record(self):
        self.btn_record.show()
        self.btn_add.show()
        self.btn_tap_enter.show()
        self.btn_record_stop.hide()


class MacroRecorder(BasicEditor):

    def __init__(self):
        super().__init__()

        self.keyboard = None

        self.keystrokes = []
        self.macro_tabs = []
        self.macro_tab_w = []

        self.recorder = None

        if sys.platform.startswith("linux"):
            from macro_recorder_linux import LinuxRecorder

            self.recorder = LinuxRecorder()
        elif sys.platform.startswith("win"):
            from macro_recorder_windows import WindowsRecorder

            self.recorder = WindowsRecorder()

        if self.recorder:
            self.recorder.keystroke.connect(self.on_keystroke)
            self.recorder.stopped.connect(self.on_stop)
        self.recording = False

        self.recording_tab = None
        self.recording_append = False

        self.tabs = QTabWidget()
        for x in range(32):
            tab = MacroTab(self.recorder is not None)
            tab.changed.connect(self.on_change)
            tab.record.connect(self.on_record)
            tab.record_stop.connect(self.on_tab_stop)
            self.macro_tabs.append(tab)
            w = QWidget()
            w.setLayout(tab)
            self.macro_tab_w.append(w)

        self.lbl_memory = QLabel()

        buttons = QHBoxLayout()
        buttons.addWidget(self.lbl_memory)
        buttons.addStretch()
        self.btn_save = QPushButton(tr("MacroRecorder", "Save"))
        self.btn_save.clicked.connect(self.on_save)
        btn_revert = QPushButton(tr("MacroRecorder", "Revert"))
        btn_revert.clicked.connect(self.on_revert)
        buttons.addWidget(self.btn_save)
        buttons.addWidget(btn_revert)

        self.addWidget(self.tabs)
        self.addLayout(buttons)

    def valid(self):
        return isinstance(self.device, VialKeyboard)

    def rebuild(self, device):
        super().rebuild(device)
        if not self.valid():
            return
        self.keyboard = self.device.keyboard

        # only show the number of macro editors that keyboard supports
        for x in range(self.tabs.count()):
            self.tabs.removeTab(x)
        for x, w in enumerate(self.macro_tab_w[:self.keyboard.macro_count]):
            self.tabs.addTab(w, "")
        self.update_tab_titles()

        # deserialize macros that came from keyboard
        self.deserialize(self.keyboard.macro)

        self.on_change()

    def update_tab_titles(self):
        macros = self.keyboard.macro.split(b"\x00")
        for x, w in enumerate(self.macro_tab_w[:self.keyboard.macro_count]):
            title = "M{}".format(x)
            if macros[x] != self.macro_tabs[x].serialize():
                title += "*"
            self.tabs.setTabText(x, title)

    def on_record(self, tab, append):
        self.recording_tab = tab
        self.recording_append = append

        self.recording_tab.pre_record()

        for x, w in enumerate(self.macro_tabs[:self.keyboard.macro_count]):
            if tab != w:
                self.tabs.tabBar().setTabEnabled(x, False)

        self.recording = True
        self.keystrokes = []
        self.recorder.start()

    def on_tab_stop(self):
        self.recorder.stop()

    def on_stop(self):
        for x in range(self.keyboard.macro_count):
            self.tabs.tabBar().setTabEnabled(x, True)

        if not self.recording_append:
            self.recording_tab.clear()

        self.recording_tab.post_record()

        self.keystrokes = macro_optimize(self.keystrokes)
        for k in self.keystrokes:
            if isinstance(k, KeyString):
                self.recording_tab.add_action(ActionText(self.recording_tab.container, k.string))
            else:
                cls = {KeyDown: ActionDown, KeyUp: ActionUp, KeyTap: ActionTap}[type(k)]
                self.recording_tab.add_action(cls(self.recording_tab.container, [k.keycode]))
        # merge: i.e. replace multiple instances of KeyDown with a single multi-key ActionDown, etc
        self.recording_tab.deserialize(self.recording_tab.serialize())

    def on_keystroke(self, keystroke):
        self.keystrokes.append(keystroke)

    def on_change(self):
        data = self.serialize()
        memory = len(data)
        self.lbl_memory.setText("Memory used by macros: {}/{}".format(memory, self.keyboard.macro_memory))
        self.btn_save.setEnabled(data != self.keyboard.macro and memory <= self.keyboard.macro_memory)
        self.lbl_memory.setStyleSheet("QLabel { color: red; }" if memory > self.keyboard.macro_memory else "")
        self.update_tab_titles()

    def deserialize(self, data):
        macros = data.split(b"\x00")
        for x, tab in enumerate(self.macro_tabs[:self.keyboard.macro_count]):
            macro = b"\x00"
            if len(macros) > x:
                macro = macros[x]
            tab.deserialize(macro)

    def serialize(self):
        data = b""
        for tab in self.macro_tabs[:self.keyboard.macro_count]:
            data += tab.serialize() + b"\x00"
        return data

    def on_revert(self):
        self.keyboard.reload_macros()
        self.deserialize(self.keyboard.macro)

    def on_save(self):
        Unlocker.get().perform_unlock(self.device.keyboard)
        self.keyboard.set_macro(self.serialize())
        self.on_change()
