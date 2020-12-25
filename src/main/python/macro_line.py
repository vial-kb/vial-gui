# coding: utf-8
# SPDX-License-Identifier: GPL-2.0-or-later
from PyQt5.QtCore import QObject, pyqtSignal, Qt
from PyQt5.QtWidgets import QHBoxLayout, QToolButton, QComboBox

from macro_action import ActionText, ActionDown, ActionUp, ActionTap


class MacroLine(QObject):

    changed = pyqtSignal()

    types = ["Text", "Down", "Up", "Tap"]
    type_to_cls = [ActionText, ActionDown, ActionUp, ActionTap]

    def __init__(self, parent, action):
        super().__init__()

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
        self.action.changed.connect(self.on_change)
        self.action.insert(self.row)

    def on_remove_clicked(self):
        self.parent.on_remove(self)

    def on_move_up(self):
        self.parent.on_move(self, -1)

    def on_move_down(self):
        self.parent.on_move(self, 1)

    def on_change(self):
        self.changed.emit()

    def serialize(self):
        return self.action.serialize()
