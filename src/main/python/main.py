# SPDX-License-Identifier: GPL-2.0-or-later
from functools import cached_property
from glob import glob
import json
import os
from os import path
import ssl
import sys
import traceback

import certifi
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QApplication

from main_window import MainWindow
# http://timlehr.com/python-exception-hooks-with-qt-message-box/
from util import init_logger

if ssl.get_default_verify_paths().cafile is None:
    os.environ['SSL_CERT_FILE'] = certifi.where()

def show_exception_box(log_msg):
    if QtWidgets.QApplication.instance() is not None:
        errorbox = QtWidgets.QMessageBox()
        errorbox.setText(log_msg)
        errorbox.exec_()


class UncaughtHook(QtCore.QObject):
    _exception_caught = pyqtSignal(object)

    def __init__(self, *args, **kwargs):
        super(UncaughtHook, self).__init__(*args, **kwargs)

        # this registers the exception_hook() function as hook with the Python interpreter
        sys._excepthook = sys.excepthook
        sys.excepthook = self.exception_hook

        # connect signal to execute the message box function always on main thread
        self._exception_caught.connect(show_exception_box)

    def exception_hook(self, exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            # ignore keyboard interrupt to support console applications
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
        else:
            log_msg = '\n'.join([''.join(traceback.format_tb(exc_traceback)),
                                 '{0}: {1}'.format(exc_type.__name__, exc_value)])

            # trigger message box show
            self._exception_caught.emit(log_msg)
        sys._excepthook(exc_type, exc_value, exc_traceback)

class VialApplicationContext():

    def __init__(self):
        self.bundle_dir = self.get_bundle_dir()
        self.vial_settings = self.load_vial_settings()

    @cached_property
    def app(self):
        # Override the app definition in order to set WM_CLASS.
        result = QtWidgets.QApplication(sys.argv)
        result.setApplicationName(self.vial_settings["app_name"])
        result.setOrganizationName(self.vial_settings["organization_name"])
        # Only used on mac in place of organization Name
        result.setOrganizationDomain(self.vial_settings["organization_domain"])

        # TODO: Qt sets applicationVersion on non-Linux platforms if the exe/pkg
        # metadata is correctly configured.
        # https://doc.qt.io/qt-5/qcoreapplication.html#applicationVersion-prop
        # Verify it is, and only set manually on Linux.
        #if sys.platform.startswith("linux"):
        result.setApplicationVersion(self.vial_settings["version"])
        return result

    def load_vial_settings(self):
        """Load and merge settings/*.json files"""
        settings_file_names = self.get_settings_file_names()
        vial_settings = {}
        for file_name in settings_file_names:
            with open(file_name, "r") as base:
                settings = json.load(base)
            vial_settings |= settings
        return vial_settings

    def get_bundle_dir(self):
        """Calculate the absolute base path of the bundled app"""
        return path.abspath(path.dirname(__file__))

    def get_settings_file_names(self):
        """Read all settings files from the bundled resources/settings dir"""
        # resources/settings/ is the bundled path set in Vial.spec for source path
        settings_files_pattern = self.real_path("resources", "settings", "*.json")
        return glob(settings_files_pattern)

    def real_path(self, *args):
        """Calculate the absolute path of a bundled file"""
        return path.join(self.bundle_dir, *args)

    def get_resource(self, file_name):
        """Implement fsb context's get_resource."""
        # TODO: FSB Assumed all resources are in the following directory. Maybe
        #  files should be moved?
        return self.real_path(os.path.join("resources", "base", file_name))


if __name__ == '__main__':
    if len(sys.argv) == 2 and sys.argv[1] == "--linux-recorder":
        from linux_keystroke_recorder import linux_keystroke_recorder

        linux_keystroke_recorder()
    else:
        init_logger()
        appctxt = VialApplicationContext()
        app = appctxt.app
        qt_exception_hook = UncaughtHook()
        window = MainWindow(appctxt)
        window.show()
        sys.exit(app.exec_())
