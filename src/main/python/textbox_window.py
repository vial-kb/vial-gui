# SPDX-License-Identifier: GPL-2.0-or-later
import time

from PyQt5.QtCore import QCoreApplication, Qt
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QDialog, QDialogButtonBox, \
    QPlainTextEdit, QToolButton, QFileDialog, QWidget

from util import tr


class TextboxWindow(QDialog):

    def __init__(self, text="", file_extension="txt", file_type="Text file", encoding="utf-8"):
        super().__init__()

        self.text = text
        self.file_extension = file_extension
        self.file_type = file_type
        self.encoding = encoding

        self.control_held = False

        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        vbox = QVBoxLayout()

        self.macrotext = QPlainTextEdit()
        self.macrotext.setPlainText(text)
        self.macrotext.selectAll()

        self.btn_apply = QToolButton()
        self.btn_apply.setText(tr("TextboxWindow", "Apply"))
        self.btn_apply.setToolButtonStyle(Qt.ToolButtonTextOnly)
        self.btn_apply.clicked.connect(self.on_apply)

        self.btn_cancel = QToolButton()
        self.btn_cancel.setText(tr("TextboxWindow", "Cancel"))
        self.btn_cancel.setToolButtonStyle(Qt.ToolButtonTextOnly)
        self.btn_cancel.clicked.connect(self.on_cancel)

        self.btn_copy = QToolButton()
        self.btn_copy.setText(tr("TextboxWindow", "Copy"))
        self.btn_copy.setToolButtonStyle(Qt.ToolButtonTextOnly)
        self.btn_copy.clicked.connect(self.on_copy)

        self.btn_paste = QToolButton()
        self.btn_paste.setText(tr("TextboxWindow", "Paste"))
        self.btn_paste.setToolButtonStyle(Qt.ToolButtonTextOnly)
        self.btn_paste.clicked.connect(self.on_paste)

        bottom_buttons = QHBoxLayout()
        bottom_buttons.setContentsMargins(0, 0, 0, 0)
        bottom_buttons.addWidget(self.btn_copy)
        bottom_buttons.addWidget(self.btn_paste)
        bottom_buttons.addSpacing(15)
        bottom_buttons.addStretch()
        bottom_buttons.addWidget(self.btn_apply)
        bottom_buttons.addWidget(self.btn_cancel)

        self.bottom_widget = QWidget()
        self.bottom_widget.setLayout(bottom_buttons)

        vbox.addWidget(self.macrotext, stretch=1)
        vbox.addWidget(self.bottom_widget)

        self.setLayout(vbox)
        self.setWindowFlags(self.windowFlags())

    def on_apply(self):
        self.accept()

    def on_cancel(self):
        self.reject()

    def on_select_all(self):
        self.macrotext.selectAll()

    def on_copy(self):
        self.macrotext.copy()

    def on_paste(self):
        self.macrotext.paste()

    def on_export(self):
        dialog = QFileDialog()
        dialog.setDefaultSuffix(self.file_extension)
        dialog.setAcceptMode(QFileDialog.AcceptSave)
        dialog.setNameFilters(["{} (*.{})".format(self.file_type, self.file_extension)])

        if dialog.exec_() == QDialog.Accepted:
            with open(dialog.selectedFiles()[0], "wb") as outf:
                outf.write(self.macrotext.toPlainText().encode(self.encoding))

    def on_import(self):
        dialog = QFileDialog()
        dialog.setDefaultSuffix(self.file_extension)
        dialog.setAcceptMode(QFileDialog.AcceptOpen)
        dialog.setNameFilters(["{} (*.{})".format(self.file_type, self.file_extension)])

        if dialog.exec_() == QDialog.Accepted:
            with open(dialog.selectedFiles()[0], "rb") as inf:
                self.macrotext.setPlainText(inf.read().decode(self.encoding))

    def getText(self):
        return self.macrotext.toPlainText()

    def keyPressEvent(self, ev):
        if ev.key() == Qt.Key_Escape:
            self.reject()

        if ev.key() == Qt.Key_Control:
            self.control_held = True

        if self.control_held:
            if ev.key() == Qt.Key_O:
                self.on_import()

            if ev.key() == Qt.Key_S:
                self.on_export()

    def keyReleaseEvent(self, ev):
        if ev.key() == Qt.Key_Control:
            self.control_held = False