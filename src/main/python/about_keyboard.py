from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QVBoxLayout, QLabel, QPlainTextEdit

from protocol.constants import VIAL_PROTOCOL_DYNAMIC, VIAL_PROTOCOL_KEY_OVERRIDE


class AboutKeyboard(QDialog):

    def about_tap_dance(self):
        if self.keyboard.tap_dance_count > 0:
            return str(self.keyboard.tap_dance_count)
        if self.keyboard.sideload:
            return "unsupported - sideloaded keyboard"
        if self.keyboard.vial_protocol < 0:
            return "unsupported - VIA keyboard"
        if self.keyboard.vial_protocol < VIAL_PROTOCOL_DYNAMIC:
            return "unsupported - Vial protocol too old"
        return "unsupported - disabled in firmware"

    def about_combo(self):
        if self.keyboard.combo_count > 0:
            return str(self.keyboard.combo_count)
        if self.keyboard.sideload:
            return "unsupported - sideloaded keyboard"
        if self.keyboard.vial_protocol < 0:
            return "unsupported - VIA keyboard"
        if self.keyboard.vial_protocol < VIAL_PROTOCOL_DYNAMIC:
            return "unsupported - Vial protocol too old"
        return "unsupported - disabled in firmware"

    def about_key_override(self):
        if self.keyboard.key_override_count > 0:
            return str(self.keyboard.key_override_count)
        if self.keyboard.sideload:
            return "unsupported - sideloaded keyboard"
        if self.keyboard.vial_protocol < 0:
            return "unsupported - VIA keyboard"
        if self.keyboard.vial_protocol < VIAL_PROTOCOL_KEY_OVERRIDE:
            return "unsupported - Vial protocol too old"
        return "unsupported - disabled in firmware"

    def __init__(self, device):
        super().__init__()

        self.keyboard = device.keyboard
        self.setWindowTitle("About {}".format(device.title()))

        text = ""
        desc = device.desc
        text += "Manufacturer: {}\n".format(desc["manufacturer_string"])
        text += "Product: {}\n".format(desc["product_string"])
        text += "VID: {:04X}\n".format(desc["vendor_id"])
        text += "PID: {:04X}\n".format(desc["product_id"])
        text += "Device: {}\n".format(desc["path"])
        text += "\n"

        if self.keyboard.sideload:
            text += "Sideloaded JSON, Vial functionality is disabled\n\n"
        elif self.keyboard.vial_protocol < 0:
            text += "VIA keyboard, Vial functionality is disabled\n\n"

        text += "VIA protocol: {}\n".format(self.keyboard.via_protocol)
        text += "Vial protocol: {}\n".format(self.keyboard.vial_protocol)
        text += "Vial keyboard ID: {:08X}\n".format(self.keyboard.keyboard_id)
        text += "\n"

        text += "Tap Dance entries: {}\n".format(self.about_tap_dance())
        text += "Combo entries: {}\n".format(self.about_combo())
        text += "Key Override entries: {}\n".format(self.about_key_override())
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
