# SPDX-License-Identifier: GPL-2.0-or-later
import ssl
import certifi
import os

if ssl.get_default_verify_paths().cafile is None:
    os.environ['SSL_CERT_FILE'] = certifi.where()

import traceback

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import pyqtSignal
from fbs_runtime.application_context.PyQt5 import ApplicationContext

import sys

from main_window import MainWindow
from constants import WINDOW_WIDTH, WINDOW_HEIGHT


# http://timlehr.com/python-exception-hooks-with-qt-message-box/
from util import init_logger

#Single instance app
from single_application import QtSingleApplication


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


if __name__ == '__main__':
    if len(sys.argv) == 2 and sys.argv[1] == "--linux-recorder":
        app = QtSingleApplication('3A07-4923-A4C0-45CD-FAE9-F3D5-0177-52B9', sys.argv) #VIAL-LINUX-RECORDER
        if app.isRunning(): sys.exit(0)

        from linux_keystroke_recorder import linux_keystroke_recorder

        linux_keystroke_recorder()
    else:
        app = QtSingleApplication('EA48-A684-BD42-588B-2EA1-2E08-12BD-2418', sys.argv) #VIAL-APP
        if app.isRunning(): sys.exit(0)

        appctxt = ApplicationContext()       # 1. Instantiate ApplicationContext
        init_logger()
        qt_exception_hook = UncaughtHook()
        window = MainWindow()
        window.resize(WINDOW_WIDTH, WINDOW_HEIGHT)
        window.show()
        exit_code = appctxt.app.exec_()      # 2. Invoke appctxt.app.exec_()
        sys.exit(exit_code)
