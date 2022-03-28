from PyQt5.QtCore import QObject, pyqtSignal, Qt
from PyQt5.QtWidgets import QLineEdit, QToolButton, QWidget, QSizePolicy, QSpinBox

from constants import KEY_SIZE_RATIO
from tabbed_keycodes import TabbedKeycodes
from widgets.flowlayout import FlowLayout
from keycodes import KEYCODES_SPECIAL
from macro.macro_action import ActionText, ActionSequence, ActionDown, ActionUp, ActionTap, ActionDelay
from widgets.key_widget import KeyWidget

KC_TRNS = KEYCODES_SPECIAL[1]


class DeletableKeyWidget(KeyWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setFocusPolicy(Qt.ClickFocus)

    def keyReleaseEvent(self, ev):
        # remove this keycode from the sequence when delete is pressed
        if ev.key() == Qt.Key_Delete:
            self.set_keycode(0)


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

    def set_keycode_filter(self, keycode_filter):
        pass


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
        self.btn_plus.setFixedWidth(self.btn_plus.fontMetrics().height() * KEY_SIZE_RATIO)
        self.btn_plus.setFixedHeight(self.btn_plus.fontMetrics().height() * KEY_SIZE_RATIO)
        self.btn_plus.setToolButtonStyle(Qt.ToolButtonTextOnly)
        self.btn_plus.clicked.connect(self.on_add)

        self.layout = FlowLayout()
        self.layout_container = QWidget()
        self.layout_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)
        self.layout_container.setLayout(self.layout)
        self.widgets = []
        self.keycode_filter = None
        self.recreate_sequence()

    def set_keycode_filter(self, keycode_filter):
        if keycode_filter != self.keycode_filter:
            self.keycode_filter = keycode_filter
            for w in self.widgets:
                w.set_keycode_filter(self.keycode_filter)

    def recreate_sequence(self):
        TabbedKeycodes.close_tray()

        self.layout.removeWidget(self.btn_plus)
        for w in self.widgets:
            self.layout.removeWidget(w)
            w.deleteLater()
        self.widgets.clear()

        for kc in self.act.sequence:
            w = DeletableKeyWidget(self.keycode_filter)
            w.set_keycode(kc)
            w.changed.connect(self.on_change)
            self.layout.addWidget(w)
            self.widgets.append(w)
        self.layout.addWidget(self.btn_plus)

    def insert(self, row):
        self.container.addWidget(self.layout_container, row, 2)

    def remove(self):
        self.container.removeWidget(self.layout_container)

    def delete(self):
        TabbedKeycodes.close_tray()
        for w in self.widgets:
            w.deleteLater()
        self.btn_plus.deleteLater()
        self.layout_container.deleteLater()

    def on_add(self):
        self.act.sequence.append(KC_TRNS.code)
        self.recreate_sequence()
        self.changed.emit()

    def on_change(self):
        for x in range(len(self.act.sequence)):
            kc = self.widgets[x].keycode
            if kc == 0:
                # asked to remove this item
                del self.act.sequence[x]
                self.recreate_sequence()
                break
            else:
                self.act.sequence[x] = kc
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


tag_to_action = {
    "down": ActionDown,
    "up": ActionUp,
    "tap": ActionTap,
    "text": ActionText,
    "delay": ActionDelay,
}

ui_action = {
    ActionText: ActionTextUI,
    ActionUp: ActionUpUI,
    ActionDown: ActionDownUI,
    ActionTap: ActionTapUI,
    ActionDelay: ActionDelayUI,
}
