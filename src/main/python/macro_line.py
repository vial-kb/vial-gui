# coding: utf-8
# SPDX-License-Identifier: GPL-2.0-or-later
from PyQt5.QtCore import QObject, pyqtSignal, Qt
from PyQt5.QtWidgets import QHBoxLayout, QToolButton, QComboBox

from macro_action_ui import ActionTextUI, ActionDownUI, ActionUpUI, ActionTapUI, ActionDelayUI


class MacroLine(QObject):

    changed = pyqtSignal()

    types = ["Text", "Down", "Up", "Tap"]
    type_to_cls = [ActionTextUI, ActionDownUI, ActionUpUI, ActionTapUI]

    def __init__(self, parent, action):
        super().__init__()

        self.parent = parent
        self.container = parent.container

        if self.parent.parent.keyboard.vial_protocol >= 2:
            self.types = self.types[:] + ["Delay (ms)"]
            self.type_to_cls = self.type_to_cls[:] + [ActionDelayUI]

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
        self.arrows.setSpacing(0)

        self.select_type = QComboBox()
        self.select_type.addItems(self.types)
        self.select_type.setCurrentIndex(self.type_to_cls.index(type(action)))
        self.select_type.currentIndexChanged.connect(self.on_change_type)

        self.action = action
        self.action.changed.connect(self.on_change)
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
        self.btn_remove.deleteLater()
        self.select_type.deleteLater()
        self.arrows.deleteLater()
        self.btn_up.deleteLater()
        self.btn_down.deleteLater()

    def on_change_type(self):
        self.action.remove()
        self.action.delete()
        self.action = self.type_to_cls[self.select_type.currentIndex()](self.container)
        self.action.changed.connect(self.on_change)
        self.action.insert(self.row)
        self.changed.emit()

    def on_remove_clicked(self):
        self.parent.on_remove(self)

    def on_move_up(self):
        self.parent.on_move(self, -1)

    def on_move_down(self):
        self.parent.on_move(self, 1)

    def on_change(self):
        self.changed.emit()
