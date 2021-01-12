# SPDX-License-Identifier: GPL-2.0-or-later

from PyQt5.QtCore import Qt, QSettings, QStandardPaths
from PyQt5.QtWidgets import QWidget, QComboBox, QToolButton, QHBoxLayout, QVBoxLayout, QMainWindow, QAction, qApp, \
    QFileDialog, QDialog, QTabWidget, QActionGroup, QMessageBox

import json
import os
from urllib.request import urlopen

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
        # create empty VIA definitions. Easier than setting it to none and handling a bunch of exceptions
        self.via_stack_json = {"definitions": {}}
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

        # cache for via definition files
        self.cache_path = QStandardPaths.writableLocation(QStandardPaths.CacheLocation)
        if not os.path.exists(self.cache_path):
            os.makedirs(self.cache_path)
        # check if the via defitions already exist
        if os.path.isfile(os.path.join(self.cache_path, "via_keyboards.json")):
            with open(os.path.join(self.cache_path, "via_keyboards.json")) as vf:
                self.via_stack_json = json.load(vf)
                vf.close()

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

        download_via_stack_act = QAction(tr("MenuFile", "Download VIA definitions"), self)
        download_via_stack_act.triggered.connect(self.load_via_stack_json)

        load_dummy_act = QAction(tr("MenuFile", "Load dummy JSON..."), self)
        load_dummy_act.triggered.connect(self.on_load_dummy)

        exit_act = QAction(tr("MenuFile", "Exit"), self)
        exit_act.setShortcut("Ctrl+Q")
        exit_act.triggered.connect(qApp.exit)

        file_menu = self.menuBar().addMenu(tr("Menu", "File"))
        file_menu.addAction(layout_load_act)
        file_menu.addAction(layout_save_act)
        file_menu.addSeparator()
        file_menu.addAction(sideload_json_act)
        file_menu.addAction(download_via_stack_act)
        file_menu.addAction(load_dummy_act)
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

        self.theme_menu = self.menuBar().addMenu(tr("Menu", "Theme"))
        theme_group = QActionGroup(self)
        selected_theme = self.settings.value("theme")
        for name, _ in [("System", None)] + themes.themes:
            act = QAction(tr("MenuTheme", name), self)
            act.triggered.connect(lambda x,name=name: self.set_theme(name))
            act.setCheckable(True)
            act.setChecked(selected_theme == name)
            theme_group.addAction(act)
            self.theme_menu.addAction(act)
        # check "System" if nothing else is selected
        if theme_group.checkedAction() is None:
            theme_group.actions()[0].setChecked(True)

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
        self.devices = find_vial_devices(self.via_stack_json, self.sideload_vid, self.sideload_pid)
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
            if self.current_device.sideload:
                self.current_device.open(self.sideload_json)
            elif self.current_device.via_stack:
                self.current_device.open(self.via_stack_json["definitions"][self.current_device.via_id])
            else:
                self.current_device.open(None)

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

    def load_via_stack_json(self):
        data = urlopen("https://github.com/vial-kb/via-keymap-precompiled/raw/main/via_keyboard_stack.json")
        self.via_stack_json = json.load(data)
        # write to cache
        with open(os.path.join(self.cache_path, "via_keyboards.json"), "w") as cf:
            cf.write(json.dumps(self.via_stack_json, indent=2))
            cf.close()

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

    def on_load_dummy(self):
        dialog = QFileDialog()
        dialog.setDefaultSuffix("json")
        dialog.setAcceptMode(QFileDialog.AcceptOpen)
        dialog.setNameFilters(["VIA layout JSON (*.json)"])
        if dialog.exec_() == QDialog.Accepted:
            with open(dialog.selectedFiles()[0], "rb") as inf:
                data = inf.read()
            self.sideload_json = json.loads(data)
            self.sideload_vid = self.sideload_pid = 0
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
        msg = QMessageBox()
        msg.setText(tr("MainWindow", "In order to fully apply the theme you should restart the application."))
        msg.exec_()
