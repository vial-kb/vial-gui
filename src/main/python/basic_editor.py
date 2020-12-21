from PyQt5.QtWidgets import QVBoxLayout


class BasicEditor(QVBoxLayout):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.device = None

    def valid(self):
        raise NotImplementedError

    def rebuild(self, device):
        self.device = device
