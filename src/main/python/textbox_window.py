# SPDX-License-Identifier: GPL-2.0-or-later
import time

from PyQt5.QtCore import QCoreApplication, Qt
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QDialog, QDialogButtonBox, \
    QPlainTextEdit, QToolButton, QFileDialog

from util import tr


class TextboxWindow(QDialog):

    def __init__(self, text="", file_extension="txt", file_type="Text file", encoding="utf-8"):
        super().__init__()

        self.text = text
        self.file_extension = file_extension
        self.file_type = file_type
        self.encoding = encoding

        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        vbox = QVBoxLayout()

        self.macrotext = QPlainTextEdit()
        self.macrotext.setPlainText(text)
        self.macrotext.selectAll()

        self.btn_save_exit = QToolButton()
        self.btn_save_exit.setText(tr("TextboxWindow", "Save"))
        self.btn_save_exit.setToolButtonStyle(Qt.ToolButtonTextOnly)
        self.btn_save_exit.clicked.connect(self.on_save_exit)

        self.btn_cancel = QToolButton()
        self.btn_cancel.setText(tr("TextboxWindow", "Cancel"))
        self.btn_cancel.setToolButtonStyle(Qt.ToolButtonTextOnly)
        self.btn_cancel.clicked.connect(self.on_cancel)

        self.btn_select_all = QToolButton()
        self.btn_select_all.setText(tr("TextboxWindow", "Select All"))
        self.btn_select_all.setToolButtonStyle(Qt.ToolButtonTextOnly)
        self.btn_select_all.clicked.connect(self.on_select_all)

        self.btn_copy = QToolButton()
        self.btn_copy.setText(tr("TextboxWindow", "Copy"))
        self.btn_copy.setToolButtonStyle(Qt.ToolButtonTextOnly)
        self.btn_copy.clicked.connect(self.on_copy)

        self.btn_paste = QToolButton()
        self.btn_paste.setText(tr("TextboxWindow", "Paste"))
        self.btn_paste.setToolButtonStyle(Qt.ToolButtonTextOnly)
        self.btn_paste.clicked.connect(self.on_paste)

        self.btn_export = QToolButton()
        self.btn_export.setText(tr("TextboxWindowr", "Export"))
        self.btn_export.setToolButtonStyle(Qt.ToolButtonTextOnly)
        self.btn_export.clicked.connect(self.on_export)

        self.btn_import = QToolButton()
        self.btn_import.setText(tr("TextboxWindow", "Import"))
        self.btn_import.setToolButtonStyle(Qt.ToolButtonTextOnly)
        self.btn_import.clicked.connect(self.on_import)

        top_buttons = QHBoxLayout()
        top_buttons.addWidget(self.btn_import)
        top_buttons.addWidget(self.btn_export)
        top_buttons.addStretch()
        top_buttons.addWidget(self.btn_select_all)

        bottom_buttons = QHBoxLayout()
        bottom_buttons.addWidget(self.btn_copy)
        bottom_buttons.addWidget(self.btn_paste)
        bottom_buttons.addStretch()
        bottom_buttons.addWidget(self.btn_save_exit)
        bottom_buttons.addWidget(self.btn_cancel)

        vbox.addLayout(top_buttons)
        vbox.addWidget(self.macrotext, stretch=1)
        vbox.addLayout(bottom_buttons)

        self.setLayout(vbox)
        self.setWindowFlags(self.windowFlags())

    def on_save_exit(self):
        self.accept()
        return

    def on_cancel(self):
        self.reject()
        return

    def on_select_all(self):
        self.macrotext.selectAll()
        return

    def on_copy(self):
        self.macrotext.copy()
        return

    def on_paste(self):
        self.macrotext.paste()
        return

    def on_export(self):
        dialog = QFileDialog()
        dialog.setDefaultSuffix(self.file_extension)
        dialog.setAcceptMode(QFileDialog.AcceptSave)
        dialog.setNameFilters(["{} (*.{})".format(self.file_type, self.file_extension)])

        if dialog.exec_() == QDialog.Accepted:
            with open(dialog.selectedFiles()[0], "wb") as outf:
                outf.write(self.macrotext.toPlainText().encode(self.encoding))
        return

    def on_import(self):
        dialog = QFileDialog()
        dialog.setDefaultSuffix(self.file_extension)
        dialog.setAcceptMode(QFileDialog.AcceptOpen)
        dialog.setNameFilters(["{} (*.{})".format(self.file_type, self.file_extension)])

        if dialog.exec_() == QDialog.Accepted:
            with open(dialog.selectedFiles()[0], "rb") as inf:
                self.macrotext.setPlainText(inf.read().decode(self.encoding))
        return

    def getText(self):
        return self.macrotext.toPlainText()