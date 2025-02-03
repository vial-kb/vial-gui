# SPDX-License-Identifier: GPL-2.0-or-later
import logging
import platform
from json import JSONDecodeError

from PyQt5.QtCore import Qt, QSettings, QStandardPaths, QTimer, QRect, QT_VERSION_STR
from PyQt5.QtWidgets import QWidget, QComboBox, QToolButton, QHBoxLayout, QVBoxLayout, QMainWindow, QAction, qApp, \
    QFileDialog, QDialog, QTabWidget, QActionGroup, QMessageBox, QLabel

import os
import sys

from about_keyboard import AboutKeyboard
from autorefresh.autorefresh import Autorefresh
from editor.combos import Combos
from constants import WINDOW_WIDTH, WINDOW_HEIGHT
from widgets.editor_container import EditorContainer
from editor.firmware_flasher import FirmwareFlasher
from editor.key_override import KeyOverride
from protocol.keyboard_comm import ProtocolError
from editor.keymap_editor import KeymapEditor
from keymaps import KEYMAPS
from editor.layout_editor import LayoutEditor
from editor.macro_recorder import MacroRecorder
from editor.qmk_settings import QmkSettings
from editor.rgb_configurator import RGBConfigurator
from tabbed_keycodes import TabbedKeycodes
from editor.tap_dance import TapDance
from unlocker import Unlocker
from util import tr, EXAMPLE_KEYBOARDS, KeycodeDisplay, EXAMPLE_KEYBOARD_PREFIX
from vial_device import VialKeyboard
from editor.matrix_test import MatrixTest

import themes


class MainWindow(QMainWindow):

    def __init__(self, appctx):
        super().__init__()
        self.appctx = appctx

        self.ui_lock_count = 0

        self.settings = QSettings("Vial", "Vial")
        if self.settings.value("size", None):
            self.resize(self.settings.value("size"))
        else:
            self.resize(WINDOW_WIDTH, WINDOW_HEIGHT)

        _pos = self.settings.value("pos", None)
        # NOTE: QDesktopWidget is obsolete, but QApplication.screenAt only usable in Qt 5.10+
        if _pos and qApp.desktop().geometry().contains(QRect(_pos, self.size())):
        #if _pos and qApp.screenAt(_pos) and qApp.screenAt(_pos + (self.rect().bottomRight())):
            self.move(self.settings.value("pos"))

        if self.settings.value("maximized", False, bool):
            self.showMaximized()

        themes.Theme.set_theme(self.get_theme())

        self.combobox_devices = QComboBox()
        self.combobox_devices.currentIndexChanged.connect(self.on_device_selected)

        self.btn_refresh_devices = QToolButton()
        self.btn_refresh_devices.setToolButtonStyle(Qt.ToolButtonTextOnly)
        self.btn_refresh_devices.setText(tr("MainWindow", "Refresh"))
        self.btn_refresh_devices.clicked.connect(self.on_click_refresh)

        layout_combobox = QHBoxLayout()
        layout_combobox.addWidget(self.combobox_devices)
        if sys.platform != "emscripten":
            layout_combobox.addWidget(self.btn_refresh_devices)

        self.layout_editor = LayoutEditor()
        self.keymap_editor = KeymapEditor(self.layout_editor)
        self.firmware_flasher = FirmwareFlasher(self)
        self.macro_recorder = MacroRecorder()
        self.tap_dance = TapDance()
        self.combos = Combos()
        self.key_override = KeyOverride()
        QmkSettings.initialize(appctx)
        self.qmk_settings = QmkSettings()
        self.matrix_tester = MatrixTest(self.layout_editor)
        self.rgb_configurator = RGBConfigurator()

        self.editors = [(self.keymap_editor, "Keymap"), (self.layout_editor, "Layout"), (self.macro_recorder, "Macros"),
                        (self.rgb_configurator, "Lighting"), (self.tap_dance, "Tap Dance"), (self.combos, "Combos"),
                        (self.key_override, "Key Overrides"), (self.qmk_settings, "QMK Settings"),
                        (self.matrix_tester, "Matrix tester"), (self.firmware_flasher, "Firmware updater")]

        Unlocker.global_layout_editor = self.layout_editor
        Unlocker.global_main_window = self

        self.current_tab = None
        self.tabs = QTabWidget()
        self.tabs.currentChanged.connect(self.on_tab_changed)
        self.refresh_tabs()

        no_devices = 'No devices detected. Connect a Vial-compatible device and press "Refresh"<br>' \
                     'or select "File" → "Download VIA definitions" in order to enable support for VIA keyboards.'
        if sys.platform.startswith("linux"):
            no_devices += '<br><br>On Linux you need to set up a custom udev rule for keyboards to be detected. ' \
                          'Follow the instructions linked below:<br>' \
                          '<a href="https://get.vial.today/manual/linux-udev.html">https://get.vial.today/manual/linux-udev.html</a>'
        self.lbl_no_devices = QLabel(tr("MainWindow", no_devices))
        self.lbl_no_devices.setTextFormat(Qt.RichText)
        self.lbl_no_devices.setAlignment(Qt.AlignCenter)

        layout = QVBoxLayout()
        layout.addLayout(layout_combobox)
        layout.addWidget(self.tabs, 1)
        layout.addWidget(self.lbl_no_devices)
        layout.setAlignment(self.lbl_no_devices, Qt.AlignHCenter)
        self.tray_keycodes = TabbedKeycodes()
        self.tray_keycodes.make_tray()
        layout.addWidget(self.tray_keycodes, 1)
        self.tray_keycodes.hide()
        w = QWidget()
        w.setLayout(layout)
        self.setCentralWidget(w)

        self.init_menu()

        self.autorefresh = Autorefresh()
        self.autorefresh.devices_updated.connect(self.on_devices_updated)

        # cache for via definition files
        self.cache_path = QStandardPaths.writableLocation(QStandardPaths.CacheLocation)
        if not os.path.exists(self.cache_path):
            os.makedirs(self.cache_path)

        # check if the via defitions already exist
        if os.path.isfile(os.path.join(self.cache_path, "via_keyboards.json")):
            with open(os.path.join(self.cache_path, "via_keyboards.json")) as vf:
                data = vf.read()
            try:
                self.autorefresh.load_via_stack(data)
            except JSONDecodeError as e:
                # the saved file is invalid - just ignore this
                logging.warning("Failed to parse stored via_keyboards.json: {}".format(e))

        # make sure initial state is valid
        self.on_click_refresh()

        if sys.platform == "emscripten":
            import vialglue
            QTimer.singleShot(100, vialglue.notify_ready)

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
        exit_act.triggered.connect(self.close)

        if sys.platform != "emscripten":
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
        keyboard_unlock_act.setShortcut("Ctrl+U")
        keyboard_unlock_act.triggered.connect(self.unlock_keyboard)

        keyboard_lock_act = QAction(tr("MenuSecurity", "Lock"), self)
        keyboard_lock_act.setShortcut("Ctrl+L")
        keyboard_lock_act.triggered.connect(self.lock_keyboard)

        keyboard_reset_act = QAction(tr("MenuSecurity", "Reboot to bootloader"), self)
        keyboard_reset_act.setShortcut("Ctrl+B")
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

        if sys.platform != "emscripten":
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

        about_vial_act = QAction(tr("MenuAbout", "About Vial..."), self)
        about_vial_act.triggered.connect(self.about_vial)
        self.about_keyboard_act = QAction("", self)
        self.about_keyboard_act.triggered.connect(self.about_keyboard)
        self.about_menu = self.menuBar().addMenu(tr("Menu", "About"))
        self.about_menu.addAction(self.about_keyboard_act)
        self.about_menu.addAction(about_vial_act)

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
        self.autorefresh.update(quiet=False, hard=True)

    def on_devices_updated(self, devices, hard_refresh):
        self.combobox_devices.blockSignals(True)

        self.combobox_devices.clear()
        for dev in devices:
            self.combobox_devices.addItem(dev.title())
            if self.autorefresh.current_device and dev.desc["path"] == self.autorefresh.current_device.desc["path"]:
                self.combobox_devices.setCurrentIndex(self.combobox_devices.count() - 1)

        self.combobox_devices.blockSignals(False)

        if devices:
            self.lbl_no_devices.hide()
            self.tabs.show()
        else:
            self.lbl_no_devices.show()
            self.tabs.hide()

        if hard_refresh:
            self.on_device_selected()

    def on_device_selected(self):
        try:
            self.autorefresh.select_device(self.combobox_devices.currentIndex())
        except ProtocolError:
            QMessageBox.warning(self, "", "Unsupported protocol version!\n"
                                          "Please download latest Vial from https://get.vial.today/")

        if isinstance(self.autorefresh.current_device, VialKeyboard):
            keyboard_id = self.autorefresh.current_device.keyboard.keyboard_id
            if (keyboard_id in EXAMPLE_KEYBOARDS) or ((keyboard_id & 0xFFFFFFFFFFFFFF) == EXAMPLE_KEYBOARD_PREFIX):
                QMessageBox.warning(self, "", "An example keyboard UID was detected.\n"
                                              "Please change your keyboard UID to be unique before you ship!")

        self.rebuild()
        self.refresh_tabs()

    def rebuild(self):
        # don't show "Security" menu for bootloader mode, as the bootloader is inherently insecure
        self.security_menu.menuAction().setVisible(isinstance(self.autorefresh.current_device, VialKeyboard))

        self.about_keyboard_act.setVisible(False)
        if isinstance(self.autorefresh.current_device, VialKeyboard):
            self.about_keyboard_act.setText("About {}...".format(self.autorefresh.current_device.title()))
            self.about_keyboard_act.setVisible(True)

        # if unlock process was interrupted, we must finish it first
        if isinstance(self.autorefresh.current_device, VialKeyboard) and self.autorefresh.current_device.keyboard.get_unlock_in_progress():
            Unlocker.unlock(self.autorefresh.current_device.keyboard)
            self.autorefresh.current_device.keyboard.reload()

        for e in [self.layout_editor, self.keymap_editor, self.firmware_flasher, self.macro_recorder,
                  self.tap_dance, self.combos, self.key_override, self.qmk_settings, self.matrix_tester,
                  self.rgb_configurator]:
            e.rebuild(self.autorefresh.current_device)

    def refresh_tabs(self):
        self.tabs.clear()
        for container, lbl in self.editors:
            if not container.valid():
                continue

            c = EditorContainer(container)
            self.tabs.addTab(c, tr("MainWindow", lbl))

    def load_via_stack_json(self):
        from urllib.request import urlopen

        with urlopen("https://github.com/vial-kb/via-keymap-precompiled/raw/main/via_keyboard_stack.json") as resp:
            data = resp.read()
        self.autorefresh.load_via_stack(data)
        # write to cache
        with open(os.path.join(self.cache_path, "via_keyboards.json"), "wb") as cf:
            cf.write(data)

    def on_sideload_json(self):
        dialog = QFileDialog()
        dialog.setDefaultSuffix("json")
        dialog.setAcceptMode(QFileDialog.AcceptOpen)
        dialog.setNameFilters(["VIA layout JSON (*.json)"])
        if dialog.exec_() == QDialog.Accepted:
            with open(dialog.selectedFiles()[0], "rb") as inf:
                data = inf.read()
            self.autorefresh.sideload_via_json(data)

    def on_load_dummy(self):
        dialog = QFileDialog()
        dialog.setDefaultSuffix("json")
        dialog.setAcceptMode(QFileDialog.AcceptOpen)
        dialog.setNameFilters(["VIA layout JSON (*.json)"])
        if dialog.exec_() == QDialog.Accepted:
            with open(dialog.selectedFiles()[0], "rb") as inf:
                data = inf.read()
            self.autorefresh.load_dummy(data)

    def lock_ui(self):
        self.ui_lock_count += 1
        if self.ui_lock_count == 1:
            self.autorefresh._lock()
            self.tabs.setEnabled(False)
            self.combobox_devices.setEnabled(False)
            self.btn_refresh_devices.setEnabled(False)

    def unlock_ui(self):
        self.ui_lock_count -= 1
        if self.ui_lock_count == 0:
            self.autorefresh._unlock()
            self.tabs.setEnabled(True)
            self.combobox_devices.setEnabled(True)
            self.btn_refresh_devices.setEnabled(True)

    def unlock_keyboard(self):
        if isinstance(self.autorefresh.current_device, VialKeyboard):
            Unlocker.unlock(self.autorefresh.current_device.keyboard)

    def lock_keyboard(self):
        if isinstance(self.autorefresh.current_device, VialKeyboard):
            self.autorefresh.current_device.keyboard.lock()

    def reboot_to_bootloader(self):
        if isinstance(self.autorefresh.current_device, VialKeyboard):
            Unlocker.unlock(self.autorefresh.current_device.keyboard)
            self.autorefresh.current_device.keyboard.reset()

    def change_keyboard_layout(self, index):
        self.settings.setValue("keymap", KEYMAPS[index][0])
        KeycodeDisplay.set_keymap_override(KEYMAPS[index][1])

    def get_theme(self):
        return self.settings.value("theme", "Dark")

    def set_theme(self, theme):
        themes.Theme.set_theme(theme)
        self.settings.setValue("theme", theme)
        msg = QMessageBox()
        msg.setText(tr("MainWindow", "In order to fully apply the theme you should restart the application."))
        msg.exec_()

    def on_tab_changed(self, index):
        TabbedKeycodes.close_tray()
        old_tab = self.current_tab
        new_tab = None
        if index >= 0:
            new_tab = self.tabs.widget(index)

        if old_tab is not None:
            old_tab.editor.deactivate()
        if new_tab is not None:
            new_tab.editor.activate()

        self.current_tab = new_tab

    def about_vial(self):
        title = "About Vial"
        text = 'Vial {}<br><br>Python {}<br>Qt {}<br><br>' \
               'Licensed under the terms of the<br>GNU General Public License (version 2 or later)<br><br>' \
               '<a href="https://get.vial.today/">https://get.vial.today/</a>' \
               .format(qApp.applicationVersion(),
                       platform.python_version(), QT_VERSION_STR)

        if sys.platform == "emscripten":
            self.msg_about = QMessageBox()
            self.msg_about.setWindowTitle(title)
            self.msg_about.setText(text)
            self.msg_about.setModal(True)
            self.msg_about.show()
        else:
            QMessageBox.about(self, title, text)

    def about_keyboard(self):
        self.about_dialog = AboutKeyboard(self.autorefresh.current_device)
        self.about_dialog.setModal(True)
        self.about_dialog.show()

    def closeEvent(self, e):
        self.settings.setValue("size", self.size())
        self.settings.setValue("pos", self.pos())
        self.settings.setValue("maximized", self.isMaximized())

        e.accept()
