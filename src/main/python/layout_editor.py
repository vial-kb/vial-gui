# SPDX-License-Identifier: GPL-2.0-or-later

from basic_editor import BasicEditor
from vial_device import VialKeyboard


class LayoutEditor(BasicEditor):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.device = None

    def rebuild(self, device):
        super().rebuild(device)

    def valid(self):
        return isinstance(self.device, VialKeyboard)
