# SPDX-License-Identifier: GPL-2.0-or-later

from PyQt5.QtCore import Qt, QSettings, QStandardPaths
from PyQt5.QtWidgets import QWidget, QComboBox, QToolButton, QHBoxLayout, QVBoxLayout, QMainWindow, QAction, qApp, \
    QFileDialog, QDialog, QTabWidget, QActionGroup, QMessageBox, QLabel

import json
import os
import sys
from urllib.request import urlopen

from editor_container import EditorContainer
from firmware_flasher import FirmwareFlasher
from keyboard_comm import ProtocolError
from keymap_editor import KeymapEditor
from keymaps import KEYMAPS
from layout_editor import LayoutEditor
from macro_recorder import MacroRecorder
from rgb_configurator import RGBConfigurator
from unlocker import Unlocker
from util import tr, find_vial_devices, EXAMPLE_KEYBOARDS
from vial_device import VialKeyboard
from matrix_test import MatrixTest

import themes


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.settings = QSettings("Vial", "Vial")
        themes.set_theme(self.get_theme())

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
        self.matrix_tester = MatrixTest(self.layout_editor)
        self.rgb_configurator = RGBConfigurator()

        self.editors = [(self.keymap_editor, "Keymap"), (self.layout_editor, "Layout"), (self.macro_recorder, "Macros"),
                        (self.rgb_configurator, "Lighting"), (self.matrix_tester, "Matrix tester"),
                        (self.firmware_flasher, "Firmware updater")]

        Unlocker.global_layout_editor = self.layout_editor

        self.current_tab = None
        self.tabs = QTabWidget()
        self.tabs.currentChanged.connect(self.on_tab_changed)
        self.refresh_tabs()

        no_devices = 'No devices detected. Connect a Vial-compatible device and press "Refresh"<br>' \
                     'or select "File" → "Download VIA definitions" in order to enable support for VIA keyboards.'
        if sys.platform.startswith("linux"):
            no_devices += '<br><br>On Linux you need to set up a custom udev rule for keyboards to be detected. ' \
                          'Follow the instructions linked below:<br>' \
                          '<a href="https://get.vial.today/getting-started/linux-udev.html">https://get.vial.today/getting-started/linux-udev.html</a>'
        self.lbl_no_devices = QLabel(tr("MainWindow", no_devices))
        self.lbl_no_devices.setTextFormat(Qt.RichText)
        self.lbl_no_devices.setAlignment(Qt.AlignCenter)

        layout = QVBoxLayout()
        layout.addLayout(layout_combobox)
        layout.addWidget(self.tabs)
        layout.addWidget(self.lbl_no_devices)
        layout.setAlignment(self.lbl_no_devices, Qt.AlignHCenter)
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
        selected_keymap = self.settings.value("keymap")
        for idx, keymap in enumerate(KEYMAPS):
            act = QAction(tr("KeyboardLayout", keymap[0]), self)
            act.triggered.connect(lambda checked, x=idx: self.change_keyboard_layout(x))
            act.setCheckable(True)
            if selected_keymap == keymap[0]:
                self.change_keyboard_layout(idx)
                act.setChecked(True)
            keymap_group.addAction(act)
            keyboard_layout_menu.addAction(act)
        # check "QWERTY" if nothing else is selected
        if keymap_group.checkedAction() is None:
            keymap_group.actions()[0].setChecked(True)

        self.security_menu = self.menuBar().addMenu(tr("Menu", "Security"))
        self.security_menu.addAction(keyboard_unlock_act)
        self.security_menu.addAction(keyboard_lock_act)
        self.security_menu.addSeparator()
        self.security_menu.addAction(keyboard_reset_act)

        self.theme_menu = self.menuBar().addMenu(tr("Menu", "Theme"))
        theme_group = QActionGroup(self)
        selected_theme = self.get_theme()
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
        self.combobox_devices.clear()
        self.devices = find_vial_devices(self.via_stack_json, self.sideload_vid, self.sideload_pid)

        for dev in self.devices:
            self.combobox_devices.addItem(dev.title())

        if self.devices:
            self.lbl_no_devices.hide()
            self.tabs.show()
        else:
            self.lbl_no_devices.show()
            self.tabs.hide()

    def on_device_selected(self):
        if self.current_device is not None:
            self.current_device.close()
        self.current_device = None
        idx = self.combobox_devices.currentIndex()
        if idx >= 0:
            self.current_device = self.devices[idx]

        if self.current_device is not None:
            try:
                if self.current_device.sideload:
                    self.current_device.open(self.sideload_json)
                elif self.current_device.via_stack:
                    self.current_device.open(self.via_stack_json["definitions"][self.current_device.via_id])
                else:
                    self.current_device.open(None)
            except ProtocolError:
                QMessageBox.warning(self, "", "Unsupported protocol version!\n"
                                              "Please download latest Vial from https://get.vial.today/")

            if isinstance(self.current_device, VialKeyboard) \
                    and self.current_device.keyboard.keyboard_id in EXAMPLE_KEYBOARDS:
                QMessageBox.warning(self, "", "An example keyboard UID was detected.\n"
                                              "Please change your keyboard UID to be unique before you ship!")

        self.rebuild()

        self.refresh_tabs()

    def rebuild(self):
        # don't show "Security" menu for bootloader mode, as the bootloader is inherently insecure
        self.security_menu.menuAction().setVisible(isinstance(self.current_device, VialKeyboard))

        # if unlock process was interrupted, we must finish it first
        if isinstance(self.current_device, VialKeyboard) and self.current_device.keyboard.get_unlock_in_progress():
            Unlocker.unlock(self.current_device.keyboard)
            self.current_device.keyboard.reload()

        for e in [self.layout_editor, self.keymap_editor, self.firmware_flasher, self.macro_recorder,
                  self.matrix_tester, self.rgb_configurator]:
            e.rebuild(self.current_device)

    def refresh_tabs(self):
        self.tabs.clear()
        for container, lbl in self.editors:
            if not container.valid():
                continue

            c = EditorContainer(container)
            self.tabs.addTab(c, tr("MainWindow", lbl))

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
            Unlocker.unlock(self.current_device.keyboard)

    def lock_keyboard(self):
        if isinstance(self.current_device, VialKeyboard):
            self.current_device.keyboard.lock()

    def reboot_to_bootloader(self):
        if isinstance(self.current_device, VialKeyboard):
            Unlocker.unlock(self.current_device.keyboard)
            self.current_device.keyboard.reset()

    def change_keyboard_layout(self, index):
        self.settings.setValue("keymap", KEYMAPS[index][0])
        self.keymap_editor.set_keymap_override(KEYMAPS[index][1])

    def get_theme(self):
        return self.settings.value("theme", "Dark")

    def set_theme(self, theme):
        themes.set_theme(theme)
        self.settings.setValue("theme", theme)
        msg = QMessageBox()
        msg.setText(tr("MainWindow", "In order to fully apply the theme you should restart the application."))
        msg.exec_()

    def on_tab_changed(self, index):
        old_tab = self.current_tab
        new_tab = None
        if index >= 0:
            new_tab = self.tabs.widget(index)

        if old_tab is not None:
            old_tab.editor.deactivate()
        if new_tab is not None:
            new_tab.editor.activate()

        self.current_tab = new_tab
