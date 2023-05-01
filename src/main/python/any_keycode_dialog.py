# SPDX-License-Identifier: GPL-2.0-or-later
from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QVBoxLayout, QLineEdit, QLabel, QHBoxLayout, QCheckBox

from keycodes.keycodes import Keycode
from util import tr


class AnyKeycodeDialog(QDialog):

    def __init__(self, initial):
        super().__init__()

        self.setWindowTitle(tr("AnyKeycodeDialog", "Enter an arbitrary keycode"))

        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)

        self.lbl_computed = QLabel()
        self.txt_entry = QLineEdit()
        self.txt_entry.textChanged.connect(self.on_change)

        self.keycode_computed = QLabel()

        self.toggleModify = QCheckBox("Modifiers")
        self.mod_tap = QCheckBox("Mod-Tap")
        self.one_shot_mod = QCheckBox("One-Shot Mod")
        self.toggleCtl = QCheckBox("LCTL")
        self.toggleSft = QCheckBox("LSFT")
        self.toggleAlt = QCheckBox("LALT")
        self.toggleGui = QCheckBox("LGUI")
        self.right_side_mods = QCheckBox("Right-Side Mods")

        self.toggleModify.stateChanged.connect(self.on_modify_change)
        self.mod_tap.stateChanged.connect(self.on_mod_tap_change)
        self.one_shot_mod.stateChanged.connect(self.on_osm_change)
        self.toggleCtl.stateChanged.connect(self.on_change)
        self.toggleSft.stateChanged.connect(self.on_change)
        self.toggleAlt.stateChanged.connect(self.on_change)
        self.toggleGui.stateChanged.connect(self.on_change)
        self.right_side_mods.stateChanged.connect(self.on_right_mods_change)

        code = Keycode.deserialize(initial, reraise=True)
        self.modifyEnable = self.is_modifiable(code)
        self.toggleModify.setEnabled(self.modifyEnable)     
        
        initial = Keycode.serialize(code)

        self.modifier_bar = QHBoxLayout()
        self.modifier_bar.addWidget(self.toggleModify)
        self.modifier_bar.addWidget(self.right_side_mods)

        self.modifiers = QHBoxLayout()
        self.modifiers.addWidget(self.toggleCtl)
        self.modifiers.addWidget(self.toggleSft)
        self.modifiers.addWidget(self.toggleAlt)
        self.modifiers.addWidget(self.toggleGui)

        self.modifier_options = QHBoxLayout()
        self.modifier_options.addWidget(self.mod_tap)
        self.modifier_options.addWidget(self.one_shot_mod)

        self.layout = QVBoxLayout()
        self.layout.addLayout(self.modifier_bar)
        self.layout.addLayout(self.modifier_options)
        self.layout.addWidget(self.txt_entry)
        self.layout.addLayout(self.modifiers)
        self.layout.addWidget(self.keycode_computed)
        self.layout.addWidget(self.lbl_computed)
        self.layout.addWidget(self.buttons)
        self.setLayout(self.layout)

        self.value = initial
        self.txt_entry.setText(initial)
        self.txt_entry.selectAll()

        self.clear_modifiers()
        self.hide_modifiers()   

    def on_change(self):
        text = self.txt_entry.text()
        value = err = None
        try:
            if self.toggleModify.checkState():                
                prefix = "MOD_" if self.one_shot_mod.checkState() else "QK_"
                if self.one_shot_mod.checkState():
                    value = Keycode.resolve("QK_ONE_SHOT_MOD")
                else:
                    value = Keycode.deserialize(text, reraise=True)
                if self.mod_tap.checkState():
                    value |= Keycode.resolve("QK_MOD_TAP")
                if self.toggleGui.checkState():
                    value |= Keycode.resolve(prefix+self.toggleGui.text())
                if self.toggleAlt.checkState():
                    value |= Keycode.resolve(prefix+self.toggleAlt.text())
                if self.toggleSft.checkState():
                    value |= Keycode.resolve(prefix+self.toggleSft.text())
                if self.toggleCtl.checkState():
                    value |= Keycode.resolve(prefix+self.toggleCtl.text())
            else:
                value = Keycode.deserialize(text, reraise=True)
        except Exception as e:
            err = str(e)

        if not text:
            self.value = ""
            self.lbl_computed.setText(tr("AnyKeycodeDialog", "Enter an expression"))
            if self.toggleModify.checkState():
                self.keycode_computed.setText("Computed keycode: None")
            self.modifyEnable = True
            self.toggleModify.setEnabled(self.modifyEnable)
        elif err:
            self.value = ""
            self.lbl_computed.setText(tr("AnyKeycodeDialog", "Invalid input: {}").format(err))
            if self.toggleModify.checkState():
                self.keycode_computed.setText("Computed keycode: Invalid")
        elif isinstance(value, int):
            self.value = Keycode.serialize(value)
            self.lbl_computed.setText(tr("AnyKeycodeDialog", "Computed value: 0x{:X}").format(value))
            if self.toggleModify.checkState():
                self.keycode_computed.setText("Computed keycode: "+self.value)
            self.modifyEnable = self.is_modifiable(value)
            self.toggleModify.setEnabled(self.modifyEnable)
            if self.modifyEnable == False:
                self.toggleModify.setChecked(False)
        else:
            self.value = ""
            self.lbl_computed.setText(tr("AnyKeycodeDialog", "Invalid input"))
            if self.toggleModify.checkState():
                self.keycode_computed.setText("Computed keycode: Invalid")

        self.buttons.button(QDialogButtonBox.Ok).setEnabled(self.value != "")

    def on_right_mods_change(self):
        side = 'R' if self.right_side_mods.checkState() else 'L'
        self.toggleGui.setText(side+"GUI")
        self.toggleAlt.setText(side+"ALT")
        self.toggleSft.setText(side+"SFT")
        self.toggleCtl.setText(side+"CTL")
        self.on_change()

    def on_mod_tap_change(self):
        if self.mod_tap.checkState():
            self.one_shot_mod.setChecked(False)
        self.on_change()

    def on_osm_change(self):
        if self.one_shot_mod.checkState():
            self.mod_tap.setChecked(False)
            self.txt_entry.setEnabled(False)
        else:
            self.txt_entry.setEnabled(True)
        self.on_change()

    def on_modify_change(self):
        if self.toggleModify.checkState():
            self.show_modifiers()
        else:
            self.hide_modifiers()
        self.on_change()

    def is_modifiable(self, code):
        return self.is_one_shot_mod(code) or self.is_mod_tap(code) or self.is_modified_basic(code)
    
    def is_one_shot_mod(self, code):
        return (code & 0xFF00) == Keycode.resolve("QK_ONE_SHOT_MOD")
    
    def is_mod_tap(self, code):
        return ((code & 0xFF00) >= Keycode.resolve("QK_MOD_TAP")) and \
             ((code & 0xFF00) <= Keycode.resolve("ALL_T(kc)")|Keycode.resolve("QK_RCTL"))
    
    def is_modified_basic(self, code):
        return ((code & 0xFF00) <= Keycode.resolve("HYPR(kc)")|Keycode.resolve("QK_RCTL")) and \
            ((code & 0xFF00) >= 0x00)
    
    def hide_modifiers(self):
        text = self.txt_entry.text()
        value = None
        try:
            value = Keycode.deserialize(text, reraise=True)
            prefix = "MOD_" if self.one_shot_mod.checkState() else "QK_"
            if self.one_shot_mod.checkState():
                value = Keycode.resolve("QK_ONE_SHOT_MOD")
            if self.mod_tap.checkState():
                value |= Keycode.resolve("QK_MOD_TAP")
            if self.toggleGui.checkState():
                value |= Keycode.resolve(prefix+self.toggleGui.text())
            if self.toggleAlt.checkState():
                value |= Keycode.resolve(prefix+self.toggleAlt.text())
            if self.toggleSft.checkState():
                value |= Keycode.resolve(prefix+self.toggleSft.text())
            if self.toggleCtl.checkState():
                value |= Keycode.resolve(prefix+self.toggleCtl.text())
            self.txt_entry.setText(Keycode.serialize(value))
        except:
            pass             

        self.clear_modifiers()

        self.mod_tap.hide()
        self.one_shot_mod.hide()
        self.toggleCtl.hide()
        self.toggleSft.hide()
        self.toggleAlt.hide()
        self.toggleGui.hide()
        self.right_side_mods.hide()
        self.keycode_computed.hide()

    def clear_modifiers(self):
        self.mod_tap.setChecked(False)
        self.one_shot_mod.setChecked(False)
        self.toggleCtl.setChecked(False)
        self.toggleSft.setChecked(False)
        self.toggleAlt.setChecked(False)
        self.toggleGui.setChecked(False)
        self.right_side_mods.setChecked(False)

    def show_modifiers(self):

        try:
            code = Keycode.deserialize(self.txt_entry.text(), reraise=True)

            if self.is_one_shot_mod(code):
                self.one_shot_mod.setChecked(True)
            if self.is_mod_tap(code):
                self.mod_tap.setChecked(True)
            prefix = "MOD_" if self.one_shot_mod.checkState() else "QK_"

            if code & Keycode.resolve(prefix+"LCTL"):
                self.toggleCtl.setChecked(True)
            if code & Keycode.resolve(prefix+"LSFT"):
                self.toggleSft.setChecked(True)
            if code & Keycode.resolve(prefix+"LALT"):
                self.toggleAlt.setChecked(True)
            if code & Keycode.resolve(prefix+"LGUI"):
                self.toggleGui.setChecked(True)
            if code & (Keycode.resolve(prefix+"RGUI")-Keycode.resolve(prefix+"LGUI")):
                self.right_side_mods.setChecked(True)
        
            self.txt_entry.setText(Keycode.serialize(0x00 if self.one_shot_mod.checkState() else code & 0xFF))

        except:
            self.clear_modifiers()

        self.mod_tap.show()
        self.one_shot_mod.show()
        self.toggleCtl.show()
        self.toggleSft.show()
        self.toggleAlt.show()
        self.toggleGui.show()
        self.right_side_mods.show()
        self.keycode_computed.show()