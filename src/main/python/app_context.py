# SPDX-License-Identifier: GPL-2.0-or-later
"""Replacement for fbs_runtime.application_context.

Resource resolution:
  - frozen build (PyInstaller): files bundled at sys._MEIPASS root
  - source checkout: src/main/resources/base/<name>
"""
import os
import sys
from functools import cached_property
from pathlib import Path

from PyQt5 import QtWidgets


def is_frozen():
    return getattr(sys, "frozen", False)


def _resource_root():
    if is_frozen():
        return Path(getattr(sys, "_MEIPASS", os.path.dirname(sys.executable)))
    # this file: src/main/python/app_context.py -> src/main/resources/base
    return Path(__file__).resolve().parent.parent / "resources" / "base"


class VialContext:
    build_settings = {
        "app_name": "Vial",
        "version": "0.7.5",
    }

    @cached_property
    def app(self):
        a = QtWidgets.QApplication(sys.argv)
        a.setApplicationName(self.build_settings["app_name"])
        a.setOrganizationDomain("vial.today")
        a.setApplicationVersion(self.build_settings["version"])
        return a

    def get_resource(self, name):
        return str(_resource_root() / name)
