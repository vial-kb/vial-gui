# SPDX-License-Identifier: GPL-2.0-or-later
from PyQt5.QtWidgets import QCheckBox


class CheckBoxNoPadding(QCheckBox):

    def __init__(self, *args):
        super().__init__(*args)
        self.setStyleSheet("QCheckBox { padding: 0; }")
