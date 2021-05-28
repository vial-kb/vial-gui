# SPDX-License-Identifier: GPL-2.0-or-later
import sys

from PyQt5.QtWidgets import QPushButton, QHBoxLayout, QTabWidget, QWidget, QLabel

from basic_editor import BasicEditor
from macro_action import ActionText, ActionTap, ActionDown, ActionUp, ActionDelay
from macro_action_ui import ActionTextUI, ActionUpUI, ActionDownUI, ActionTapUI, ActionDelayUI
from macro_key import KeyString, KeyDown, KeyUp, KeyTap
from macro_optimizer import macro_optimize
from macro_tab import MacroTab
from unlocker import Unlocker
from util import tr
from vial_device import VialKeyboard


ui_action = {
    ActionText: ActionTextUI,
    ActionUp: ActionUpUI,
    ActionDown: ActionDownUI,
    ActionTap: ActionTapUI,
    ActionDelay: ActionDelayUI,
}


class MacroRecorder(BasicEditor):

    def __init__(self):
        super().__init__()

        self.keyboard = None
        self.suppress_change = False

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
            tab = MacroTab(self, self.recorder is not None)
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
        while self.tabs.count() > 0:
            self.tabs.removeTab(0)
        for x, w in enumerate(self.macro_tab_w[:self.keyboard.macro_count]):
            self.tabs.addTab(w, "")

        # deserialize macros that came from keyboard
        self.deserialize(self.keyboard.macro)

        self.on_change()

    def update_tab_titles(self):
        macros = self.keyboard.macro.split(b"\x00")
        for x, w in enumerate(self.macro_tab_w[:self.keyboard.macro_count]):
            title = "M{}".format(x)
            if macros[x] != self.keyboard.macro_serialize(self.macro_tabs[x].actions()):
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
        actions = []
        for k in self.keystrokes:
            if isinstance(k, KeyString):
                actions.append(ActionText(k.string))
            else:
                cls = {KeyDown: ActionDown, KeyUp: ActionUp, KeyTap: ActionTap}[type(k)]
                actions.append(cls([k.keycode]))

        # merge: i.e. replace multiple instances of KeyDown with a single multi-key ActionDown, etc
        actions = self.keyboard.macro_deserialize(self.keyboard.macro_serialize(actions))
        self.recording_tab.clear()
        for act in actions:
            self.recording_tab.add_action(ui_action[type(act)](self.recording_tab.container, act))

    def on_keystroke(self, keystroke):
        self.keystrokes.append(keystroke)

    def on_change(self):
        if self.suppress_change:
            return

        data = self.serialize()
        memory = len(data)
        self.lbl_memory.setText("Memory used by macros: {}/{}".format(memory, self.keyboard.macro_memory))
        self.btn_save.setEnabled(data != self.keyboard.macro and memory <= self.keyboard.macro_memory)
        self.lbl_memory.setStyleSheet("QLabel { color: red; }" if memory > self.keyboard.macro_memory else "")
        self.update_tab_titles()

    def serialize(self):
        macros = []
        for x, t in enumerate(self.macro_tabs[:self.keyboard.macro_count]):
            macros.append(t.actions())
        return self.keyboard.macros_serialize(macros)

    def deserialize(self, data):
        self.suppress_change = True
        macros = self.keyboard.macros_deserialize(data)
        for macro, tab in zip(macros, self.macro_tabs[:self.keyboard.macro_count]):
            tab.clear()
            for act in macro:
                tab.add_action(ui_action[type(act)](tab.container, act))
        self.suppress_change = False

    def on_revert(self):
        self.keyboard.reload_macros()
        self.deserialize(self.keyboard.macro)

    def on_save(self):
        Unlocker.unlock(self.device.keyboard)
        self.keyboard.set_macro(self.serialize())
        self.on_change()
