# SPDX-License-Identifier: GPL-2.0-or-later
import sys
import json

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QPushButton, QGridLayout, QHBoxLayout, QToolButton, QVBoxLayout, \
    QTabWidget, QWidget, QLabel, QMenu, QScrollArea, QFrame, QFileDialog, QDialog

from basic_editor import BasicEditor
from keycodes import Keycode
from macro_action import ActionText, ActionTap, ActionDown, ActionUp, ActionDelay, SS_TAP_CODE, SS_DOWN_CODE, \
    SS_UP_CODE, SS_DELAY_CODE, SS_QMK_PREFIX
from macro_action_ui import ActionTextUI, ActionDownUI, ActionUpUI, ActionTapUI, ActionDelayUI
from macro_key import KeyString, KeyDown, KeyUp, KeyTap
from macro_line import MacroLine
from macro_optimizer import macro_optimize
from unlocker import Unlocker
from util import tr
from vial_device import VialKeyboard
from textbox_window import TextboxWindow


class MacroTab(QVBoxLayout):

    changed = pyqtSignal()
    record = pyqtSignal(object, bool)
    record_stop = pyqtSignal()

    def __init__(self, parent, enable_recorder):
        super().__init__()

        self.parent = parent

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

        self.btn_text_window = QToolButton()
        self.btn_text_window.setText(tr("MacroRecorder", "Open Text Editor..."))
        self.btn_text_window.setToolButtonStyle(Qt.ToolButtonTextOnly)
        self.btn_text_window.clicked.connect(self.on_text_window)

        layout_buttons = QHBoxLayout()
        layout_buttons.addWidget(self.btn_text_window)
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
        self.add_action(ActionTextUI(self.container))

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

    def on_text_window(self):

        # serialize all actions in this tab to a json
        macro_text = []
        macro_text.append([act.save() for act in self.actions()])
        macro_text = json.dumps(macro_text[0])

        textbox = TextboxWindow(macro_text, "vim", "Vial macro")

        if textbox.exec():
            macro_text = textbox.getText()
            macro_load = json.loads(macro_text)
            
            # ensure a list exists
            if not isinstance(macro_load, list):
                return

            # associate action types with tags from the macro json
            tag_to_action = {
                "down": ActionDown,
                "up": ActionUp,
                "tap": ActionTap,
                "text": ActionText,
                "delay": ActionDelay,
            }
            tag_to_actionUI = {
                "down": ActionDownUI,
                "up": ActionUpUI,
                "tap": ActionTapUI,
                "text": ActionTextUI,
                "delay": ActionDelayUI,
            }

            # clear the actions from this tab
            self.clear()

            # add each action from the json to this tab
            for act in macro_load:
                if act[0] in tag_to_action:
                    obj = tag_to_action[act[0]]()
                    actionUI = tag_to_actionUI[act[0]]
                    obj.restore(act)
                    self.add_action(actionUI(self.container, obj))

    def on_change(self):
        self.changed.emit()

    def on_tap_enter(self):
        self.add_action(ActionTapUI(self.container, ActionTap([Keycode.find_by_qmk_id("KC_ENTER")])))

    def pre_record(self):
        self.btn_record.hide()
        self.btn_add.hide()
        self.btn_tap_enter.hide()
        self.btn_text_window.hide()
        self.btn_record_stop.show()

    def post_record(self):
        self.btn_record.show()
        self.btn_add.show()
        self.btn_tap_enter.show()
        self.btn_text_window.show()
        self.btn_record_stop.hide()

    def actions(self):
        return [line.action.act for line in self.lines]
