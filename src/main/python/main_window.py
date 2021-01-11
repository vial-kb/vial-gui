# SPDX-License-Identifier: GPL-2.0-or-later

from PyQt5.QtCore import Qt, QSettings
from PyQt5.QtWidgets import QWidget, QComboBox, QToolButton, QHBoxLayout, QVBoxLayout, QMainWindow, QAction, qApp, \
    QFileDialog, QDialog, QTabWidget, QActionGroup

import json

from firmware_flasher import FirmwareFlasher
from keymap_editor import KeymapEditor
from keymaps import KEYMAPS
from layout_editor import LayoutEditor
from macro_recorder import MacroRecorder
from unlocker import Unlocker
from util import tr, find_vial_devices
from vial_device import VialKeyboard

import themes


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.settings = QSettings("Vial", "Vial")
        themes.set_theme(self.settings.value("theme"))

        self.current_device = None
        self.devices = []
        self.sideload_json = None
        self.sideload_vid = self.sideload_pid = -1

        self.combobox_devices = QComboBox()
        self.combobox_devices.currentIndexChanged.connect(self.on_device_selected)

        self.btn_refresh_devices = QToolButton()
        self.btn_refresh_devices.setToolButtonStyle(Qt.ToolButtonTextOnly)
        self.btn_refresh_devices.setText(tr("MainWindow", "Refresh"))
        self.btn_refresh_devices.clicked.connect(self.on_click_refresh)

        layout_combobox = QHBoxLayout()
        layout_combobox.addWidget(self.combobox_devices)
        layout_combobox.addWidget(self.btn_refresh_devices)

        self.layout_editor = LayoutEditor()
        self.keymap_editor = KeymapEditor(self.layout_editor)
        self.firmware_flasher = FirmwareFlasher(self)
        self.macro_recorder = MacroRecorder()

        self.editors = [(self.keymap_editor, "Keymap"), (self.layout_editor, "Layout"), (self.macro_recorder, "Macros"),
                        (self.firmware_flasher, "Firmware updater")]
        self.unlocker = Unlocker(self.layout_editor)

        self.tabs = QTabWidget()
        self.refresh_tabs()

        layout = QVBoxLayout()
        layout.addLayout(layout_combobox)
        layout.addWidget(self.tabs)
        w = QWidget()
        w.setLayout(layout)
        self.setCentralWidget(w)

        self.init_menu()

        # make sure initial state is valid
        self.on_click_refresh()

    def init_menu(self):
        layout_load_act = QAction(tr("MenuFile", "Load saved layout..."), self)
        layout_load_act.setShortcut("Ctrl+O")
        layout_load_act.triggered.connect(self.on_layout_load)

        layout_save_act = QAction(tr("MenuFile", "Save current layout..."), self)
        layout_save_act.setShortcut("Ctrl+S")
        layout_save_act.triggered.connect(self.on_layout_save)

        sideload_json_act = QAction(tr("MenuFile", "Sideload VIA JSON..."), self)
        sideload_json_act.triggered.connect(self.on_sideload_json)

        exit_act = QAction(tr("MenuFile", "Exit"), self)
        exit_act.setShortcut("Ctrl+Q")
        exit_act.triggered.connect(qApp.exit)

        file_menu = self.menuBar().addMenu(tr("Menu", "File"))
        file_menu.addAction(layout_load_act)
        file_menu.addAction(layout_save_act)
        file_menu.addSeparator()
        file_menu.addAction(sideload_json_act)
        file_menu.addSeparator()
        file_menu.addAction(exit_act)

        keyboard_unlock_act = QAction(tr("MenuSecurity", "Unlock"), self)
        keyboard_unlock_act.triggered.connect(self.unlock_keyboard)

        keyboard_lock_act = QAction(tr("MenuSecurity", "Lock"), self)
        keyboard_lock_act.triggered.connect(self.lock_keyboard)

        keyboard_reset_act = QAction(tr("MenuSecurity", "Reboot to bootloader"), self)
        keyboard_reset_act.triggered.connect(self.reboot_to_bootloader)

        keyboard_layout_menu = self.menuBar().addMenu(tr("Menu", "Keyboard layout"))
        keymap_group = QActionGroup(self)
        for idx, keymap in enumerate(KEYMAPS):
            act = QAction(tr("KeyboardLayout", keymap[0]), self)
            act.triggered.connect(lambda checked, x=idx: self.change_keyboard_layout(x))
            act.setCheckable(True)
            if idx == 0:
                act.setChecked(True)
            keymap_group.addAction(act)
            keyboard_layout_menu.addAction(act)

        self.security_menu = self.menuBar().addMenu(tr("Menu", "Security"))
        self.security_menu.addAction(keyboard_unlock_act)
        self.security_menu.addAction(keyboard_lock_act)
        self.security_menu.addSeparator()
        self.security_menu.addAction(keyboard_reset_act)

        theme_set_default = QAction(tr("MenuTheme", "System"), self)
        theme_set_default.triggered.connect(lambda: self.set_theme("default"))

        theme_set_light = QAction(tr("MenuTheme", "Light"), self)
        theme_set_light.triggered.connect(lambda: self.set_theme("light"))

        theme_set_dark = QAction(tr("MenuTheme", "Dark"), self)
        theme_set_dark.triggered.connect(lambda: self.set_theme("dark"))

        theme_set_arc = QAction(tr("MenuTheme", "Arc"), self)
        theme_set_arc.triggered.connect(lambda: self.set_theme("arc"))

        self.theme_menu = self.menuBar().addMenu(tr("Menu", "Theme"))
        self.theme_menu.addAction(theme_set_default)
        self.theme_menu.addAction(theme_set_light)
        self.theme_menu.addAction(theme_set_dark)
        self.theme_menu.addAction(theme_set_arc)

    def on_layout_load(self):
        dialog = QFileDialog()
        dialog.setDefaultSuffix("vil")
        dialog.setAcceptMode(QFileDialog.AcceptOpen)
        dialog.setNameFilters(["Vial layout (*.vil)"])
        if dialog.exec_() == QDialog.Accepted:
            with open(dialog.selectedFiles()[0], "rb") as inf:
                data = inf.read()
            self.keymap_editor.restore_layout(data)
            self.rebuild()

    def on_layout_save(self):
        dialog = QFileDialog()
        dialog.setDefaultSuffix("vil")
        dialog.setAcceptMode(QFileDialog.AcceptSave)
        dialog.setNameFilters(["Vial layout (*.vil)"])
        if dialog.exec_() == QDialog.Accepted:
            with open(dialog.selectedFiles()[0], "wb") as outf:
                outf.write(self.keymap_editor.save_layout())

    def on_click_refresh(self):
        self.devices = find_vial_devices(self.sideload_vid, self.sideload_pid)
        self.combobox_devices.clear()

        for dev in self.devices:
            self.combobox_devices.addItem(dev.title())

    def on_device_selected(self):
        if self.current_device is not None:
            self.current_device.close()
        self.current_device = None
        idx = self.combobox_devices.currentIndex()
        if idx >= 0:
            self.current_device = self.devices[idx]

        if self.current_device is not None:
            self.current_device.open(self.sideload_json if self.current_device.sideload else None)

        self.rebuild()

        self.refresh_tabs()

    def rebuild(self):
        # don't show "Security" menu for bootloader mode, as the bootloader is inherently insecure
        self.security_menu.menuAction().setVisible(isinstance(self.current_device, VialKeyboard))

        # if unlock process was interrupted, we must finish it first
        if isinstance(self.current_device, VialKeyboard) and self.current_device.keyboard.get_unlock_in_progress():
            Unlocker.get().perform_unlock(self.current_device.keyboard)
            self.current_device.keyboard.reload()

        for e in [self.layout_editor, self.keymap_editor, self.firmware_flasher, self.macro_recorder]:
            e.rebuild(self.current_device)

    def refresh_tabs(self):
        self.tabs.clear()
        for container, lbl in self.editors:
            if not container.valid():
                continue

            w = QWidget()
            w.setLayout(container)
            self.tabs.addTab(w, tr("MainWindow", lbl))

    def on_sideload_json(self):
        dialog = QFileDialog()
        dialog.setDefaultSuffix("json")
        dialog.setAcceptMode(QFileDialog.AcceptOpen)
        dialog.setNameFilters(["VIA layout JSON (*.json)"])
        if dialog.exec_() == QDialog.Accepted:
            with open(dialog.selectedFiles()[0], "rb") as inf:
                data = inf.read()
            self.sideload_json = json.loads(data)
            self.sideload_vid = int(self.sideload_json["vendorId"], 16)
            self.sideload_pid = int(self.sideload_json["productId"], 16)
            self.on_click_refresh()

    def lock_ui(self):
        self.tabs.setEnabled(False)
        self.combobox_devices.setEnabled(False)
        self.btn_refresh_devices.setEnabled(False)

    def unlock_ui(self):
        self.tabs.setEnabled(True)
        self.combobox_devices.setEnabled(True)
        self.btn_refresh_devices.setEnabled(True)

    def unlock_keyboard(self):
        if isinstance(self.current_device, VialKeyboard):
            self.unlocker.perform_unlock(self.current_device.keyboard)

    def lock_keyboard(self):
        if isinstance(self.current_device, VialKeyboard):
            self.current_device.keyboard.lock()

    def reboot_to_bootloader(self):
        if isinstance(self.current_device, VialKeyboard):
            self.unlocker.perform_unlock(self.current_device.keyboard)
            self.current_device.keyboard.reset()

    def change_keyboard_layout(self, index):
        self.keymap_editor.set_keymap_override(KEYMAPS[index][1])

    def set_theme(self, theme):
        themes.set_theme(theme)
        self.settings.setValue("theme", theme)
