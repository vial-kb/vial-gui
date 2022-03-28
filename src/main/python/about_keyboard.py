from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QVBoxLayout, QLabel, QPlainTextEdit


class AboutKeyboard(QDialog):

    def __init__(self, device):
        super().__init__()

        keyboard = device.keyboard
        self.setWindowTitle("About {}".format(device.title()))

        text = ""
        desc = device.desc
        text += "Manufacturer: {}\n".format(desc["manufacturer_string"])
        text += "Product: {}\n".format(desc["product_string"])
        text += "VID: {:04X}\n".format(desc["vendor_id"])
        text += "PID: {:04X}\n".format(desc["product_id"])
        text += "Device: {}\n".format(desc["path"])
        text += "\n"

        if keyboard.sideload:
            text += "Sideloaded JSON, Vial functionality is disabled\n\n"
        elif keyboard.vial_protocol < 0:
            text += "VIA keyboard, Vial functionality is disabled\n\n"

        text += "VIA protocol: {}\n".format(keyboard.via_protocol)
        text += "Vial protocol: {}\n".format(keyboard.vial_protocol)
        text += "Vial keyboard ID: 0x{:X}\n".format(keyboard.keyboard_id)
        text += "\n"

        font = QFont("monospace")
        font.setStyleHint(QFont.TypeWriter)
        textarea = QPlainTextEdit()
        textarea.setReadOnly(True)
        textarea.setFont(font)

        textarea.setPlainText(text)

        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.layout = QVBoxLayout()
        self.layout.addWidget(textarea)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)
