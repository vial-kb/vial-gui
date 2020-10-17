# SPDX-License-Identifier: GPL-2.0-or-later

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QComboBox, QToolButton, QHBoxLayout, QVBoxLayout, QMainWindow, QAction, qApp, \
    QFileDialog, QDialog

from keyboard import Keyboard
from keyboard_container import KeyboardContainer
from keycodes import recreate_layer_keycodes
from tabbed_keycodes import TabbedKeycodes
from util import tr, find_vial_keyboards, open_device


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.device = None
        self.devices = []

        self.keyboard_container = KeyboardContainer()
        self.keyboard_container.number_layers_changed.connect(self.on_number_layers_changed)

        self.tabbed_keycodes = TabbedKeycodes()
        self.tabbed_keycodes.keycode_changed.connect(self.on_keycode_changed)

        self.combobox_devices = QComboBox()
        self.combobox_devices.currentIndexChanged.connect(self.on_device_selected)

        btn_refresh_devices = QToolButton()
        btn_refresh_devices.setToolButtonStyle(Qt.ToolButtonTextOnly)
        btn_refresh_devices.setText(tr("MainWindow", "Refresh"))
        btn_refresh_devices.clicked.connect(self.on_click_refresh)

        layout_combobox = QHBoxLayout()
        layout_combobox.addWidget(self.combobox_devices)
        layout_combobox.addWidget(btn_refresh_devices)

        layout = QVBoxLayout()
        layout.addLayout(layout_combobox)
        layout.addWidget(self.keyboard_container)
        layout.addWidget(self.tabbed_keycodes)
        w = QWidget()
        w.setLayout(layout)
        self.setCentralWidget(w)

        self.init_menu()

        # make sure initial state is valid
        self.on_click_refresh()

    def init_menu(self):
        layout_load_act = QAction(tr("MenuFile", "Load saved layout"), self)
        layout_load_act.setShortcut("Ctrl+O")
        layout_load_act.triggered.connect(self.on_layout_load)

        layout_save_act = QAction(tr("MenuFile", "Save current layout"), self)
        layout_save_act.setShortcut("Ctrl+S")
        layout_save_act.triggered.connect(self.on_layout_save)

        exit_act = QAction(tr("MenuFile", "Exit"), self)
        exit_act.setShortcut("Ctrl+Q")
        exit_act.triggered.connect(qApp.exit)

        menubar = self.menuBar()
        file_menu = self.menuBar().addMenu(tr("Menu", "File"))
        file_menu.addAction(layout_load_act)
        file_menu.addAction(layout_save_act)
        file_menu.addSeparator()
        file_menu.addAction(exit_act)

    def on_layout_load(self):
        dialog = QFileDialog()
        dialog.setDefaultSuffix("vil")
        dialog.setAcceptMode(QFileDialog.AcceptOpen)
        dialog.setNameFilters(["Vial layout (*.vil)"])
        if dialog.exec_() == QDialog.Accepted:
            with open(dialog.selectedFiles()[0], "rb") as inf:
                data = inf.read()
            self.keyboard_container.restore_layout(data)

    def on_layout_save(self):
        dialog = QFileDialog()
        dialog.setDefaultSuffix("vil")
        dialog.setAcceptMode(QFileDialog.AcceptSave)
        dialog.setNameFilters(["Vial layout (*.vil)"])
        if dialog.exec_() == QDialog.Accepted:
            with open(dialog.selectedFiles()[0], "wb") as outf:
                outf.write(self.keyboard_container.save_layout())

    def on_click_refresh(self):
        self.devices = find_vial_keyboards()
        self.combobox_devices.clear()

        for dev in self.devices:
            self.combobox_devices.addItem("{} {}".format(dev["manufacturer_string"], dev["product_string"]))

    def on_device_selected(self):
        self.device = None
        idx = self.combobox_devices.currentIndex()
        if idx >= 0:
            keyboard = Keyboard(open_device(self.devices[idx]))
            keyboard.reload()
            self.keyboard_container.rebuild(keyboard)

    def on_number_layers_changed(self):
        recreate_layer_keycodes(self.keyboard_container.keyboard.layers)
        self.tabbed_keycodes.recreate_layer_keycode_buttons()

    def on_keycode_changed(self, code):
        self.keyboard_container.set_key(code)
