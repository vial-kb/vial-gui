# SPDX-License-Identifier: GPL-2.0-or-later

from fbs_runtime.application_context.PyQt5 import ApplicationContext

import sys

from main_window import MainWindow
from constants import WINDOW_WIDTH, WINDOW_HEIGHT

if __name__ == '__main__':
    appctxt = ApplicationContext()       # 1. Instantiate ApplicationContext
    window = MainWindow()
    window.resize(WINDOW_WIDTH, WINDOW_HEIGHT)
    window.show()
    exit_code = appctxt.app.exec_()      # 2. Invoke appctxt.app.exec_()
    sys.exit(exit_code)
