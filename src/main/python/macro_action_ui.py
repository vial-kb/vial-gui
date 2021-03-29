import struct

from PyQt5.QtCore import QObject, pyqtSignal, Qt
from PyQt5.QtWidgets import QLineEdit, QToolButton, QComboBox, QWidget, QSizePolicy, QSpinBox, QHBoxLayout

from flowlayout import FlowLayout
from keycodes import KEYCODES_BASIC, KEYCODES_ISO, KEYCODES_MEDIA
from macro_action import ActionText, ActionSequence, ActionDown, ActionUp, ActionTap, ActionDelay
from util import tr


MACRO_SEQUENCE_KEYCODES = KEYCODES_BASIC + KEYCODES_ISO + KEYCODES_MEDIA
KC_A = MACRO_SEQUENCE_KEYCODES[0]


class BasicActionUI(QObject):

    changed = pyqtSignal()
    actcls = None

    def __init__(self, container, act=None):
        super().__init__()
        self.container = container
        if act is None:
            act = self.actcls()
        if not isinstance(act, self.actcls):
            raise RuntimeError("{} was initialized with {}, expecting {}".format(self, act, self.actcls))
        self.act = act


class ActionTextUI(BasicActionUI):

    actcls = ActionText

    def __init__(self, container, act=None):
        super().__init__(container, act)
        self.text = QLineEdit()
        self.text.setText(self.act.text)
        self.text.textChanged.connect(self.on_change)

    def insert(self, row):
        self.container.addWidget(self.text, row, 2)

    def remove(self):
        self.container.removeWidget(self.text)

    def delete(self):
        self.text.deleteLater()

    def on_change(self):
        self.act.text = self.text.text()
        self.changed.emit()


class ActionSequenceUI(BasicActionUI):

    actcls = ActionSequence

    def __init__(self, container, act=None):
        super().__init__(container, act)

        self.btn_plus = QToolButton()
        self.btn_plus.setText("+")
        self.btn_plus.setToolButtonStyle(Qt.ToolButtonTextOnly)
        self.btn_plus.clicked.connect(self.on_add)

        self.layout = FlowLayout()
        self.layout_container = QWidget()
        self.layout_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)
        self.layout_container.setLayout(self.layout)
        self.widgets = []
        self.recreate_sequence()

    def recreate_sequence(self):
        self.layout.removeWidget(self.btn_plus)
        for w in self.widgets:
            self.layout.removeWidget(w)
            w.deleteLater()
        self.widgets.clear()

        for item in self.act.sequence:
            w = QComboBox()
            w.view().setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
            w.setStyleSheet("QComboBox { combobox-popup: 0; }")
            w.addItem(tr("MacroEditor", "Remove"))
            w.insertSeparator(1)
            for k in MACRO_SEQUENCE_KEYCODES:
                w.addItem(k.label.replace("\n", ""))
            w.setCurrentIndex(2 + MACRO_SEQUENCE_KEYCODES.index(item))
            w.currentIndexChanged.connect(self.on_change)
            self.layout.addWidget(w)
            self.widgets.append(w)
        self.layout.addWidget(self.btn_plus)

    def insert(self, row):
        self.container.addWidget(self.layout_container, row, 2)

    def remove(self):
        self.container.removeWidget(self.layout_container)

    def delete(self):
        for w in self.widgets:
            w.deleteLater()
        self.btn_plus.deleteLater()
        self.layout_container.deleteLater()

    def on_add(self):
        self.act.sequence.append(KC_A)
        self.recreate_sequence()
        self.changed.emit()

    def on_change(self):
        for x in range(len(self.act.sequence)):
            index = self.widgets[x].currentIndex()
            if index == 0:
                # asked to remove this item
                del self.act.sequence[x]
                self.recreate_sequence()
                break
            else:
                self.act.sequence[x] = MACRO_SEQUENCE_KEYCODES[self.widgets[x].currentIndex() - 2]
        self.changed.emit()


class ActionDownUI(ActionSequenceUI):
    actcls = ActionDown


class ActionUpUI(ActionSequenceUI):
    actcls = ActionUp


class ActionTapUI(ActionSequenceUI):
    actcls = ActionTap


class ActionDelayUI(BasicActionUI):

    actcls = ActionDelay

    def __init__(self, container, act=None):
        super().__init__(container, act)
        self.value = QSpinBox()
        self.value.setMinimum(0)
        self.value.setMaximum(64000)  # up to 64s
        self.value.setValue(self.act.delay)
        self.value.valueChanged.connect(self.on_change)

        self.layout = FlowLayout()
        self.layout_container = QWidget()
        self.layout_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)
        self.layout_container.setLayout(self.layout)

        self.layout.addWidget(self.value)

    def insert(self, row):
        self.container.addWidget(self.layout_container, row, 2)

    def remove(self):
        self.container.removeWidget(self.layout_container)

    def delete(self):
        self.value.deleteLater()
        self.layout_container.deleteLater()

    def on_change(self):
        self.act.delay = self.value.value()
        self.changed.emit()
