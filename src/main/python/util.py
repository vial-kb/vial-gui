# SPDX-License-Identifier: GPL-2.0-or-later
import os
import pathlib
from logging.handlers import RotatingFileHandler
import logging

from PyQt5.QtCore import QCoreApplication, QStandardPaths
from PyQt5.QtGui import QPalette
from PyQt5.QtWidgets import QApplication, QWidget, QScrollArea, QFrame

from keycodes.keycodes import Keycode
from keymaps import KEYMAPS

# Re-export protocol utilities so existing imports continue to work
from util_base import (  # noqa: F401
    VIAL_SERIAL_NUMBER_MAGIC, VIBL_SERIAL_NUMBER_MAGIC, MSG_LEN,
    EXAMPLE_KEYBOARDS, EXAMPLE_KEYBOARD_PREFIX,
    hid_send, is_rawhid, find_vial_devices, chunks, pad_for_vibl,
)

tr = QCoreApplication.translate


def init_logger():
    logging.basicConfig(level=logging.INFO)
    directory = QStandardPaths.writableLocation(QStandardPaths.AppLocalDataLocation)
    pathlib.Path(directory).mkdir(parents=True, exist_ok=True)
    path = os.path.join(directory, "vial.log")
    handler = RotatingFileHandler(path, maxBytes=5 * 1024 * 1024, backupCount=5)
    handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(module)s:%(lineno)d - %(message)s"))
    logging.getLogger().addHandler(handler)


def make_scrollable(layout):
    w = QWidget()
    w.setLayout(layout)
    w.setObjectName("w")
    scroll = QScrollArea()
    scroll.setFrameShape(QFrame.NoFrame)
    scroll.setStyleSheet("QScrollArea { background-color:transparent; }")
    w.setStyleSheet("#w { background-color:transparent; }")
    scroll.setWidgetResizable(True)
    scroll.setWidget(w)
    return scroll


class KeycodeDisplay:

    keymap_override = KEYMAPS[0][1]
    clients = []

    @classmethod
    def get_label(cls, code):
        """ Get label for a specific keycode """
        if cls.code_is_overriden(code):
            return cls.keymap_override[Keycode.find_outer_keycode(code).qmk_id]
        return Keycode.label(code)

    @classmethod
    def code_is_overriden(cls, code):
        """ Check whether a country-specific keymap overrides a code """
        key = Keycode.find_outer_keycode(code)
        return key is not None and key.qmk_id in cls.keymap_override

    @classmethod
    def display_keycode(cls, widget, code):
        text = cls.get_label(code)
        tooltip = Keycode.tooltip(code)
        mask = Keycode.is_mask(code)
        mask_text = ""
        inner = Keycode.find_inner_keycode(code)
        if inner:
            mask_text = cls.get_label(inner.qmk_id)
        if mask:
            text = text.split("\n")[0]
        widget.masked = mask
        widget.setText(text)
        widget.setMaskText(mask_text)
        widget.setToolTip(tooltip)
        if cls.code_is_overriden(code):
            widget.setColor(QApplication.palette().color(QPalette.Link))
        else:
            widget.setColor(None)
        if inner and mask and cls.code_is_overriden(inner.qmk_id):
            widget.setMaskColor(QApplication.palette().color(QPalette.Link))
        else:
            widget.setMaskColor(None)

    @classmethod
    def set_keymap_override(cls, override):
        cls.keymap_override = override
        for client in cls.clients:
            client.on_keymap_override()

    @classmethod
    def notify_keymap_override(cls, client):
        cls.clients.append(client)
        client.on_keymap_override()

    @classmethod
    def unregister_keymap_override(cls, client):
        cls.clients.remove(client)

    @classmethod
    def relabel_buttons(cls, buttons):
        for widget in buttons:
            qmk_id = widget.keycode.qmk_id
            if qmk_id in KeycodeDisplay.keymap_override:
                label = KeycodeDisplay.keymap_override[qmk_id]
                highlight_color = QApplication.palette().color(QPalette.Link).getRgb()
                widget.setStyleSheet("QPushButton {color: rgb%s;}" % str(highlight_color))
            else:
                label = widget.keycode.label
                widget.setStyleSheet("QPushButton {}")
            widget.setText(label.replace("&", "&&"))
