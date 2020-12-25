# coding: utf-8
# SPDX-License-Identifier: GPL-2.0-or-later
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QPushButton, QLineEdit, QGridLayout, QHBoxLayout, QComboBox, QToolButton, QVBoxLayout, \
    QTabWidget, QWidget, QLabel

from basic_editor import BasicEditor
from keycodes import KEYCODES_BASIC
from macro_key import KeyString
from macro_optimizer import macro_optimize
from macro_recorder_linux import LinuxRecorder
from util import tr
from vial_device import VialKeyboard


KC_NO = KEYCODES_BASIC[0]


class BasicAction:

    def __init__(self, container):
        self.container = container


class ActionText(BasicAction):

    def __init__(self, container, text=""):
        super().__init__(container)
        self.text = QLineEdit()
        self.text.setText(text)

    def insert(self, row):
        self.container.addWidget(self.text, row, 2)

    def remove(self):
        self.container.removeWidget(self.text)

    def delete(self):
        self.text.setParent(None)
        self.text.deleteLater()


class ActionSequence(BasicAction):

    def __init__(self, container, sequence=None):
        super().__init__(container)
        if sequence is None:
            sequence = []
        self.sequence = sequence

        self.btn_plus = QToolButton()
        self.btn_plus.setText("+")
        self.btn_plus.setToolButtonStyle(Qt.ToolButtonTextOnly)
        self.btn_plus.clicked.connect(self.on_add)

        self.layout = QHBoxLayout()
        self.layout.addStretch()
        self.widgets = []
        self.recreate_sequence()

    def recreate_sequence(self):
        self.layout.removeWidget(self.btn_plus)
        for w in self.widgets:
            self.layout.removeWidget(w)
            w.deleteLater()
        self.widgets.clear()

        for item in self.sequence:
            w = QComboBox()
            w.view().setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
            w.setStyleSheet("QComboBox { combobox-popup: 0; }")
            w.addItem(tr("MacroEditor", "Remove"))
            w.insertSeparator(1)
            for k in KEYCODES_BASIC:
                w.addItem(k.label.replace("\n", ""))
            w.setCurrentIndex(2 + KEYCODES_BASIC.index(item))
            w.currentIndexChanged.connect(self.on_change)
            self.layout.insertWidget(self.layout.count() - 1, w)
            self.widgets.append(w)
        self.layout.insertWidget(self.layout.count() - 1, self.btn_plus)

    def insert(self, row):
        self.container.addLayout(self.layout, row, 2)

    def remove(self):
        self.container.removeItem(self.layout)

    def delete(self):
        for w in self.widgets:
            w.setParent(None)
            w.deleteLater()
        self.btn_plus.setParent(None)
        self.btn_plus.deleteLater()
        self.layout.setParent(None)
        self.layout.deleteLater()

    def on_add(self):
        self.sequence.append(KC_NO)
        self.recreate_sequence()

    def on_change(self):
        for x in range(len(self.sequence)):
            index = self.widgets[x].currentIndex()
            if index == 0:
                # asked to remove this item
                del self.sequence[x]
                self.recreate_sequence()
                return
            else:
                self.sequence[x] = KEYCODES_BASIC[self.widgets[x].currentIndex() - 2]


class MacroLine:

    types = ["Text", "Down", "Up", "Tap"]
    type_to_cls = [ActionText, ActionSequence, ActionSequence, ActionSequence]

    def __init__(self, parent, action):
        self.parent = parent
        self.container = parent.container

        self.arrows = QHBoxLayout()
        self.btn_up = QToolButton()
        self.btn_up.setText("▲")
        self.btn_up.setToolButtonStyle(Qt.ToolButtonTextOnly)
        self.btn_up.clicked.connect(self.on_move_up)
        self.btn_down = QToolButton()
        self.btn_down.setText("▼")
        self.btn_down.clicked.connect(self.on_move_down)
        self.btn_down.setToolButtonStyle(Qt.ToolButtonTextOnly)

        self.arrows.addWidget(self.btn_up)
        self.arrows.addWidget(self.btn_down)

        self.select_type = QComboBox()
        self.select_type.addItems(self.types)
        self.select_type.currentIndexChanged.connect(self.on_change_type)

        self.action = action
        self.row = -1

        self.btn_remove = QToolButton()
        self.btn_remove.setText("×")
        self.btn_remove.setToolButtonStyle(Qt.ToolButtonTextOnly)
        self.btn_remove.clicked.connect(self.on_remove_clicked)

    def insert(self, row):
        self.row = row
        self.container.addLayout(self.arrows, row, 0)
        self.container.addWidget(self.select_type, row, 1)
        self.container.addWidget(self.btn_remove, row, 3)
        self.action.insert(row)

    def remove(self):
        self.container.removeItem(self.arrows)
        self.container.removeWidget(self.select_type)
        self.container.removeWidget(self.btn_remove)
        self.action.remove()

    def delete(self):
        self.action.delete()
        self.btn_remove.setParent(None)
        self.btn_remove.deleteLater()
        self.select_type.setParent(None)
        self.select_type.deleteLater()
        self.arrows.setParent(None)
        self.arrows.deleteLater()
        self.btn_up.setParent(None)
        self.btn_up.deleteLater()
        self.btn_down.setParent(None)
        self.btn_down.deleteLater()

    def on_change_type(self):
        self.action.remove()
        self.action.delete()
        self.action = self.type_to_cls[self.select_type.currentIndex()](self.container)
        self.action.insert(self.row)

    def on_remove_clicked(self):
        self.parent.on_remove(self)

    def on_move_up(self):
        self.parent.on_move(self, -1)

    def on_move_down(self):
        self.parent.on_move(self, 1)


class MacroTab(QVBoxLayout):

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

        layout_buttons = QHBoxLayout()
        layout_buttons.addStretch()
        layout_buttons.addWidget(btn_add)
        layout_buttons.addWidget(btn_record)

        self.addLayout(self.container)
        self.addLayout(layout_buttons)
        self.addWidget(btn_add)
        self.addStretch()

    def on_add(self):
        self.lines.append(MacroLine(self, ActionText(self.container)))
        self.lines[-1].insert(self.container.rowCount())

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
            self.macro_tabs.append(MacroTab())
            w = QWidget()
            w.setLayout(self.macro_tabs[-1])
            self.tabs.addTab(w, "Macro {}".format(x + 1))

        buttons = QHBoxLayout()
        buttons.addWidget(QLabel("Memory used by macros: 123/345"))
        buttons.addStretch()
        buttons.addWidget(QPushButton("Save"))
        buttons.addWidget(QPushButton("Revert"))

        self.addWidget(self.tabs)
        self.addLayout(buttons)

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
