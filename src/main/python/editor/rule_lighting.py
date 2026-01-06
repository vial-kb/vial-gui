# SPDX-License-Identifier: GPL-2.0-or-later
"""
Rule Lighting UI Components

Provides widgets for configuring Rule Lighting entries.
Integrated into VialRGBHandler as a lighting mode option.
"""
from PyQt5 import QtCore
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (QWidget, QGridLayout, QHBoxLayout, QVBoxLayout,
                             QLabel, QCheckBox, QSlider, QSpinBox, QComboBox,
                             QFrame, QScrollArea, QSizePolicy, QRadioButton,
                             QButtonGroup, QStackedWidget, QGroupBox)

from keycodes.keycodes import Keycode
from protocol.rule_lighting import (RuleLightingEntry,
                                    SAT_OFF, SAT_WHITE, SAT_PASTEL, SAT_PURE)
from util import make_scrollable
from widgets.key_widget import KeyWidget


# Hue presets (6-bit values 0-63, displayed as colors)
HUE_PRESETS = [
    (0, "Red"),
    (5, "Orange"),
    (10, "Yellow"),
    (21, "Green"),
    (32, "Cyan"),
    (43, "Blue"),
    (48, "Purple"),
    (53, "Magenta"),
    (58, "Pink"),
]

# Key categories for Category mode - comprehensive QMK keycode ranges
KEY_CATEGORIES = [
    # Basic Keycodes (0x00-0xFF)
    ("Letters (A-Z)", 0x04, 0x1D),
    ("Numbers (1-0)", 0x1E, 0x27),
    ("Punctuation", 0x28, 0x38),
    ("F-keys (F1-F12)", 0x3A, 0x45),
    ("Navigation", 0x46, 0x52),
    ("Numpad", 0x53, 0x63),
    ("F-keys (F13-F24)", 0x68, 0x73),
    ("International", 0x87, 0x98),
    ("System/Power", 0xA5, 0xA7),
    ("Media/Consumer", 0xA8, 0xBA),
    ("Mouse Keys", 0xCD, 0xDF),
    ("Modifiers", 0xE0, 0xE7),
    # Quantum Keycodes
    ("Mod-Tap", 0x2000, 0x3FFF),
    ("Layer-Tap", 0x4000, 0x4FFF),
    ("Layer-Mod", 0x5000, 0x51FF),
    ("Layer Switch (TO/MO/TG/DF)", 0x5200, 0x527F),
    ("One-Shot Layer", 0x5280, 0x529F),
    ("One-Shot Mod", 0x52A0, 0x52BF),
    ("Tap-Toggle Layer", 0x52C0, 0x52FF),
    ("Swap Hands", 0x5600, 0x56FF),
    ("Tap Dance", 0x5700, 0x57FF),
    ("Magic/Config", 0x7000, 0x70FF),
    ("MIDI", 0x7100, 0x71FF),
    ("Sequencer", 0x7200, 0x73FF),
    ("Joystick", 0x7400, 0x743F),
    ("Programmable Button", 0x7440, 0x747F),
    ("Audio", 0x7480, 0x74BF),
    ("Steno", 0x74C0, 0x74FF),
    ("Macro", 0x7700, 0x777F),
    ("Bluetooth/Wireless", 0x7780, 0x77BF),
    ("Backlight", 0x7800, 0x780F),
    ("LED Matrix", 0x7810, 0x781F),
    ("RGB Underglow", 0x7820, 0x783F),
    ("RGB Matrix", 0x7840, 0x78FF),
    ("Quantum/Firmware", 0x7C00, 0x7C7F),
    ("Keyboard-Specific", 0x7E00, 0x7E3F),
    ("User-Defined", 0x7E40, 0x7FFF),
    ("Unicode", 0x8000, 0xFFFF),
]

# Key names for display in category mode
KEY_NAMES = {
    # Letters
    0x04: "A", 0x05: "B", 0x06: "C", 0x07: "D", 0x08: "E", 0x09: "F",
    0x0A: "G", 0x0B: "H", 0x0C: "I", 0x0D: "J", 0x0E: "K", 0x0F: "L",
    0x10: "M", 0x11: "N", 0x12: "O", 0x13: "P", 0x14: "Q", 0x15: "R",
    0x16: "S", 0x17: "T", 0x18: "U", 0x19: "V", 0x1A: "W", 0x1B: "X",
    0x1C: "Y", 0x1D: "Z",
    # Numbers
    0x1E: "1", 0x1F: "2", 0x20: "3", 0x21: "4", 0x22: "5",
    0x23: "6", 0x24: "7", 0x25: "8", 0x26: "9", 0x27: "0",
    # Punctuation
    0x28: "Enter", 0x29: "Esc", 0x2A: "Bksp", 0x2B: "Tab", 0x2C: "Space",
    0x2D: "-", 0x2E: "=", 0x2F: "[", 0x30: "]", 0x31: "\\",
    0x33: ";", 0x34: "'", 0x35: "`", 0x36: ",", 0x37: ".", 0x38: "/",
    # F-keys
    0x3A: "F1", 0x3B: "F2", 0x3C: "F3", 0x3D: "F4", 0x3E: "F5", 0x3F: "F6",
    0x40: "F7", 0x41: "F8", 0x42: "F9", 0x43: "F10", 0x44: "F11", 0x45: "F12",
    # Navigation
    0x46: "PrtSc", 0x47: "ScrLk", 0x48: "Pause", 0x49: "Ins", 0x4A: "Home",
    0x4B: "PgUp", 0x4C: "Del", 0x4D: "End", 0x4E: "PgDn",
    0x4F: "Right", 0x50: "Left", 0x51: "Down", 0x52: "Up",
    # Modifiers
    0xE0: "LCtrl", 0xE1: "LShift", 0xE2: "LAlt", 0xE3: "LGui",
    0xE4: "RCtrl", 0xE5: "RShift", 0xE6: "RAlt", 0xE7: "RGui",
}


def get_key_name(keycode):
    """Get human-readable key name for a keycode"""
    if keycode in KEY_NAMES:
        return KEY_NAMES[keycode]
    return f"0x{keycode:02X}"


class HexSpinBox(QSpinBox):
    """SpinBox that displays values in hexadecimal"""

    def __init__(self):
        super().__init__()
        self.setRange(0, 0xFFFF)
        self.setPrefix("0x")

    def textFromValue(self, value):
        return f"{value:04X}"

    def valueFromText(self, text):
        text = text.replace("0x", "").replace("0X", "")
        try:
            return int(text, 16)
        except ValueError:
            return 0


class CategoryRangeSlider(QWidget):
    """
    A range slider for selecting category ranges.
    Shows category names and allows selecting from/to categories.
    """
    changed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self._updating = False

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        # From category
        from_layout = QHBoxLayout()
        from_layout.setSpacing(4)
        from_layout.addWidget(QLabel("From:"))
        self.from_combo = QComboBox()
        for i, (name, start, end) in enumerate(KEY_CATEGORIES):
            self.from_combo.addItem(name, i)
        self.from_combo.currentIndexChanged.connect(self._on_from_changed)
        from_layout.addWidget(self.from_combo, 1)
        layout.addLayout(from_layout)

        # To category
        to_layout = QHBoxLayout()
        to_layout.setSpacing(4)
        to_layout.addWidget(QLabel("To:"))
        self.to_combo = QComboBox()
        for i, (name, start, end) in enumerate(KEY_CATEGORIES):
            self.to_combo.addItem(name, i)
        self.to_combo.setCurrentIndex(len(KEY_CATEGORIES) - 1)
        self.to_combo.currentIndexChanged.connect(self._on_to_changed)
        to_layout.addWidget(self.to_combo, 1)
        layout.addLayout(to_layout)

        # Range display
        self.range_label = QLabel()
        self.range_label.setStyleSheet("color: gray; font-size: 10px;")
        layout.addWidget(self.range_label)

        self.setLayout(layout)
        self._update_range_label()

    def _on_from_changed(self):
        if self._updating:
            return
        # Ensure from <= to
        if self.from_combo.currentIndex() > self.to_combo.currentIndex():
            self._updating = True
            self.to_combo.setCurrentIndex(self.from_combo.currentIndex())
            self._updating = False
        self._update_range_label()
        self.changed.emit()

    def _on_to_changed(self):
        if self._updating:
            return
        # Ensure to >= from
        if self.to_combo.currentIndex() < self.from_combo.currentIndex():
            self._updating = True
            self.from_combo.setCurrentIndex(self.to_combo.currentIndex())
            self._updating = False
        self._update_range_label()
        self.changed.emit()

    def _update_range_label(self):
        start, end = self.get_range()
        self.range_label.setText(f"Keycodes: 0x{start:04X} - 0x{end:04X}")

    def get_range(self):
        """Returns (start_keycode, end_keycode) spanning selected categories"""
        from_idx = self.from_combo.currentIndex()
        to_idx = self.to_combo.currentIndex()
        start = KEY_CATEGORIES[from_idx][1]  # start of first category
        end = KEY_CATEGORIES[to_idx][2]      # end of last category
        return (start, end)

    def load(self, start, end):
        """Load a keycode range, finding best matching categories"""
        self._updating = True

        # Find category containing start
        from_idx = 0
        for i, (name, cat_start, cat_end) in enumerate(KEY_CATEGORIES):
            if start >= cat_start and start <= cat_end:
                from_idx = i
                break
            elif start < cat_start:
                from_idx = i
                break

        # Find category containing end
        to_idx = len(KEY_CATEGORIES) - 1
        for i, (name, cat_start, cat_end) in enumerate(KEY_CATEGORIES):
            if end >= cat_start and end <= cat_end:
                to_idx = i
                break

        self.from_combo.setCurrentIndex(from_idx)
        self.to_combo.setCurrentIndex(to_idx)
        self._update_range_label()
        self._updating = False


def hue_to_rgb(hue_6bit):
    """Convert 6-bit hue (0-63) to RGB tuple"""
    # Map 0-63 to 0-360 degrees
    hue_360 = (hue_6bit / 63.0) * 360.0
    # HSV to RGB with full saturation and value
    h = hue_360 / 60.0
    i = int(h) % 6
    f = h - int(h)
    q = 1 - f
    t = f

    if i == 0:
        r, g, b = 1, t, 0
    elif i == 1:
        r, g, b = q, 1, 0
    elif i == 2:
        r, g, b = 0, 1, t
    elif i == 3:
        r, g, b = 0, q, 1
    elif i == 4:
        r, g, b = t, 0, 1
    else:
        r, g, b = 1, 0, q

    return (int(r * 255), int(g * 255), int(b * 255))


class HueSlider(QSlider):
    """Slider with rainbow gradient background"""

    def __init__(self):
        super().__init__(Qt.Horizontal)
        self.setRange(0, 63)
        self.setMinimumWidth(150)
        self._update_style()

    def _update_style(self):
        # Build gradient stops for the rainbow
        stops = []
        for i in range(64):
            r, g, b = hue_to_rgb(i)
            pos = i / 63.0
            stops.append(f"stop:{pos:.3f} rgb({r},{g},{b})")
        gradient = ", ".join(stops)

        self.setStyleSheet(f"""
            QSlider::groove:horizontal {{
                height: 12px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, {gradient});
                border-radius: 4px;
            }}
            QSlider::handle:horizontal {{
                background: white;
                border: 2px solid #333;
                width: 14px;
                margin: -3px 0;
                border-radius: 7px;
            }}
        """)


class ColorPicker(QWidget):
    """Color picker with saturation dropdown, hue slider, and color preview"""

    changed = pyqtSignal()

    def __init__(self, label="Color"):
        super().__init__()

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        self.label = QLabel(label + ":")
        self.label.setFixedWidth(50)

        self.sat_combo = QComboBox()
        self.sat_combo.addItem("Off", SAT_OFF)
        self.sat_combo.addItem("White", SAT_WHITE)
        self.sat_combo.addItem("Pastel", SAT_PASTEL)
        self.sat_combo.addItem("Vivid", SAT_PURE)
        self.sat_combo.setFixedWidth(65)
        self.sat_combo.currentIndexChanged.connect(self._on_change)

        self.hue_slider = HueSlider()
        self.hue_slider.valueChanged.connect(self._on_change)

        self.preview = QLabel()
        self.preview.setFixedSize(24, 24)
        self.preview.setStyleSheet("border: 1px solid #333; border-radius: 4px;")

        layout.addWidget(self.label)
        layout.addWidget(self.sat_combo)
        layout.addWidget(self.hue_slider, 1)
        layout.addWidget(self.preview)

        self.setLayout(layout)
        self._update_preview()

    def _on_change(self):
        self._update_preview()
        self.changed.emit()

    def _update_preview(self):
        sat = self.sat_combo.currentData()
        hue = self.hue_slider.value()

        if sat == SAT_OFF:
            # Off - dark/black
            self.preview.setStyleSheet("background: #222; border: 1px solid #333; border-radius: 4px;")
            self.hue_slider.setEnabled(False)
        elif sat == SAT_WHITE:
            # White
            self.preview.setStyleSheet("background: white; border: 1px solid #333; border-radius: 4px;")
            self.hue_slider.setEnabled(False)
        else:
            r, g, b = hue_to_rgb(hue)
            if sat == SAT_PASTEL:
                # Pastel - blend with white
                r = (r + 255) // 2
                g = (g + 255) // 2
                b = (b + 255) // 2
            self.preview.setStyleSheet(f"background: rgb({r},{g},{b}); border: 1px solid #333; border-radius: 4px;")
            self.hue_slider.setEnabled(True)

    def load(self, sat, hue):
        self.blockSignals(True)
        self.sat_combo.blockSignals(True)
        self.hue_slider.blockSignals(True)

        idx = self.sat_combo.findData(sat)
        if idx >= 0:
            self.sat_combo.setCurrentIndex(idx)

        self.hue_slider.setValue(hue)
        self._update_preview()

        self.sat_combo.blockSignals(False)
        self.hue_slider.blockSignals(False)
        self.blockSignals(False)

    def get_sat(self):
        return self.sat_combo.currentData()

    def get_hue(self):
        return self.hue_slider.value()


class KeyRangeSelector(QWidget):
    """
    Widget for selecting a key range with 3 modes:
    - All Keys: Sets range 0x04-0xFF
    - Custom Range: KeyWidget + hex spinbox + slider for from/to
    - Category: Dropdown + two sliders within category bounds
    """

    changed = pyqtSignal()

    MODE_ALL = 0
    MODE_CUSTOM = 1
    MODE_CATEGORY = 2

    def __init__(self):
        super().__init__()
        self._updating = False

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        # Radio buttons for mode selection
        mode_layout = QHBoxLayout()
        mode_layout.setSpacing(8)

        self.mode_group = QButtonGroup()
        self.radio_all = QRadioButton("All Keys")
        self.radio_custom = QRadioButton("Custom")
        self.radio_category = QRadioButton("Category")

        self.mode_group.addButton(self.radio_all, self.MODE_ALL)
        self.mode_group.addButton(self.radio_custom, self.MODE_CUSTOM)
        self.mode_group.addButton(self.radio_category, self.MODE_CATEGORY)

        mode_layout.addWidget(self.radio_all)
        mode_layout.addWidget(self.radio_custom)
        mode_layout.addWidget(self.radio_category)
        mode_layout.addStretch()
        layout.addLayout(mode_layout)

        # Stacked widget for mode-specific controls
        self.stack = QStackedWidget()

        # Mode 0: All Keys - empty widget
        self.stack.addWidget(QWidget())

        # Mode 1: Custom Range
        custom_widget = QWidget()
        custom_layout = QVBoxLayout()
        custom_layout.setContentsMargins(0, 0, 0, 0)
        custom_layout.setSpacing(2)

        # From row
        from_layout = QHBoxLayout()
        from_layout.setSpacing(4)
        from_layout.addWidget(QLabel("From:"))
        self.custom_from_key = KeyWidget()
        self.custom_from_key.changed.connect(self._on_custom_from_key_changed)
        from_layout.addWidget(self.custom_from_key)
        self.custom_from_hex = HexSpinBox()
        self.custom_from_hex.setFixedWidth(70)
        self.custom_from_hex.valueChanged.connect(self._on_custom_from_hex_changed)
        from_layout.addWidget(self.custom_from_hex)
        self.custom_from_slider = QSlider(Qt.Horizontal)
        self.custom_from_slider.setRange(0, 0xFFFF)
        self.custom_from_slider.valueChanged.connect(self._on_custom_from_slider_changed)
        from_layout.addWidget(self.custom_from_slider, 1)
        custom_layout.addLayout(from_layout)

        # To row
        to_layout = QHBoxLayout()
        to_layout.setSpacing(4)
        to_layout.addWidget(QLabel("To:"))
        self.custom_to_key = KeyWidget()
        self.custom_to_key.changed.connect(self._on_custom_to_key_changed)
        to_layout.addWidget(self.custom_to_key)
        self.custom_to_hex = HexSpinBox()
        self.custom_to_hex.setFixedWidth(70)
        self.custom_to_hex.valueChanged.connect(self._on_custom_to_hex_changed)
        to_layout.addWidget(self.custom_to_hex)
        self.custom_to_slider = QSlider(Qt.Horizontal)
        self.custom_to_slider.setRange(0, 0xFFFF)
        self.custom_to_slider.valueChanged.connect(self._on_custom_to_slider_changed)
        to_layout.addWidget(self.custom_to_slider, 1)
        custom_layout.addLayout(to_layout)

        custom_widget.setLayout(custom_layout)
        self.stack.addWidget(custom_widget)

        # Mode 2: Category - use CategoryRangeSlider
        self.category_range = CategoryRangeSlider()
        self.category_range.changed.connect(self._on_category_changed)
        self.stack.addWidget(self.category_range)

        layout.addWidget(self.stack)
        self.setLayout(layout)

        # Connect mode changes
        self.mode_group.buttonClicked.connect(self._on_mode_changed)

        # Initialize
        self.radio_all.setChecked(True)
        self._on_category_changed()

    def _on_mode_changed(self):
        mode = self.mode_group.checkedId()
        self.stack.setCurrentIndex(mode)
        self.changed.emit()

    def _on_custom_from_key_changed(self):
        if self._updating:
            return
        self._updating = True
        keycode = self.custom_from_key.keycode or 0x04
        self.custom_from_hex.setValue(keycode)
        self.custom_from_slider.setValue(keycode)
        self._updating = False
        self.changed.emit()

    def _on_custom_from_hex_changed(self, value):
        if self._updating:
            return
        self._updating = True
        self.custom_from_slider.setValue(value)
        self.custom_from_key.set_keycode(Keycode.serialize(value))
        self._updating = False
        self.changed.emit()

    def _on_custom_from_slider_changed(self, value):
        if self._updating:
            return
        self._updating = True
        self.custom_from_hex.setValue(value)
        self.custom_from_key.set_keycode(Keycode.serialize(value))
        self._updating = False
        self.changed.emit()

    def _on_custom_to_key_changed(self):
        if self._updating:
            return
        self._updating = True
        keycode = self.custom_to_key.keycode or 0xFFFF
        self.custom_to_hex.setValue(keycode)
        self.custom_to_slider.setValue(keycode)
        self._updating = False
        self.changed.emit()

    def _on_custom_to_hex_changed(self, value):
        if self._updating:
            return
        self._updating = True
        self.custom_to_slider.setValue(value)
        self.custom_to_key.set_keycode(Keycode.serialize(value))
        self._updating = False
        self.changed.emit()

    def _on_custom_to_slider_changed(self, value):
        if self._updating:
            return
        self._updating = True
        self.custom_to_hex.setValue(value)
        self.custom_to_key.set_keycode(Keycode.serialize(value))
        self._updating = False
        self.changed.emit()

    def _on_category_changed(self):
        if self._updating:
            return
        self.changed.emit()

    def get_range(self):
        """Returns (start, end) keycode tuple"""
        mode = self.mode_group.checkedId()
        if mode == self.MODE_ALL:
            return (0x0000, 0xFFFF)
        elif mode == self.MODE_CUSTOM:
            start = self.custom_from_hex.value()
            end = self.custom_to_hex.value()
            return (start, end)
        else:  # MODE_CATEGORY
            return self.category_range.get_range()

    def load(self, start, end):
        """Load a key range, auto-detecting the best mode"""
        self._updating = True

        # Check if it matches All Keys (0x0000-0xFFFF)
        if start == 0x0000 and end == 0xFFFF:
            self.radio_all.setChecked(True)
            self.stack.setCurrentIndex(self.MODE_ALL)
        else:
            # Check if range spans categories (use category mode)
            spans_categories = False
            for i, (name, cat_start, cat_end) in enumerate(KEY_CATEGORIES):
                if start >= cat_start and start <= cat_end:
                    spans_categories = True
                    break

            if spans_categories:
                self.radio_category.setChecked(True)
                self.stack.setCurrentIndex(self.MODE_CATEGORY)
                self.category_range.load(start, end)
            else:
                # Use custom mode
                self.radio_custom.setChecked(True)
                self.stack.setCurrentIndex(self.MODE_CUSTOM)
                self.custom_from_hex.setValue(start)
                self.custom_from_slider.setValue(start)
                self.custom_from_key.set_keycode(Keycode.serialize(start))
                self.custom_to_hex.setValue(end)
                self.custom_to_slider.setValue(end)
                self.custom_to_key.set_keycode(Keycode.serialize(end))

        self._updating = False


class RuleWidget(QWidget):
    """Single rule configuration widget"""

    changed = pyqtSignal()

    def __init__(self, index):
        super().__init__()
        self.index = index

        layout = QVBoxLayout()
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(3)

        # Header
        header = QLabel(f"Rule {index + 1}")
        header.setStyleSheet("font-weight: bold;")
        layout.addWidget(header)

        # Condition row: layer + caps (compact grid)
        cond_layout = QHBoxLayout()
        cond_layout.setSpacing(8)

        self.layer_check = QCheckBox("Layer:")
        self.layer_check.stateChanged.connect(self._on_change)
        self.layer_spin = QSpinBox()
        self.layer_spin.setRange(0, 15)
        self.layer_spin.setFixedWidth(45)
        self.layer_spin.valueChanged.connect(self._on_change)

        self.caps_check = QCheckBox("Caps Lock ON")
        self.caps_check.stateChanged.connect(self._on_change)

        cond_layout.addWidget(self.layer_check)
        cond_layout.addWidget(self.layer_spin)
        cond_layout.addSpacing(10)
        cond_layout.addWidget(self.caps_check)
        cond_layout.addStretch()
        layout.addLayout(cond_layout)

        # Modifiers row (more compact)
        mods_layout = QHBoxLayout()
        mods_layout.setSpacing(2)
        mods_layout.addWidget(QLabel("Mods:"))

        self.mod_checks = {}
        for mod_name, mod_bit in [("LC", 0x01), ("LS", 0x02), ("LA", 0x04), ("LG", 0x08),
                                   ("RC", 0x10), ("RS", 0x20), ("RA", 0x40), ("RG", 0x80)]:
            cb = QCheckBox(mod_name)
            cb.setToolTip({"LC": "Left Ctrl", "LS": "Left Shift", "LA": "Left Alt", "LG": "Left GUI",
                          "RC": "Right Ctrl", "RS": "Right Shift", "RA": "Right Alt", "RG": "Right GUI"}[mod_name])
            cb.stateChanged.connect(self._on_change)
            self.mod_checks[mod_bit] = cb
            mods_layout.addWidget(cb)
        mods_layout.addStretch()
        layout.addLayout(mods_layout)

        # Key range selector
        self.key_range = KeyRangeSelector()
        self.key_range.changed.connect(self._on_change)
        layout.addWidget(self.key_range)

        # Colors row (side by side)
        colors_layout = QHBoxLayout()
        colors_layout.setSpacing(15)
        self.idle_color = ColorPicker("Idle")
        self.idle_color.changed.connect(self._on_change)
        colors_layout.addWidget(self.idle_color)

        self.pressed_color = ColorPicker("Pressed")
        self.pressed_color.changed.connect(self._on_change)
        colors_layout.addWidget(self.pressed_color)
        colors_layout.addStretch()
        layout.addLayout(colors_layout)

        # Separator
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        layout.addWidget(line)

        self.setLayout(layout)

    def _on_change(self):
        self.layer_spin.setEnabled(self.layer_check.isChecked())
        self.changed.emit()

    def load(self, entry):
        self.blockSignals(True)

        self.layer_check.setChecked(entry.layer_enable)
        self.layer_spin.setValue(entry.layer)
        self.layer_spin.setEnabled(entry.layer_enable)
        self.caps_check.setChecked(entry.caps_enable)

        # Load mods
        for mod_bit, cb in self.mod_checks.items():
            cb.setChecked(bool(entry.mods & mod_bit))

        # Load key range - deserialize from GUI format to raw keycodes
        start = Keycode.deserialize(entry.keycode_start)
        end = Keycode.deserialize(entry.keycode_end)
        self.key_range.load(start, end)

        self.idle_color.load(entry.sat_idle, entry.h_idle)
        self.pressed_color.load(entry.sat_pressed, entry.h_pressed)

        self.blockSignals(False)

    def save(self):
        entry = RuleLightingEntry()

        entry.layer_enable = self.layer_check.isChecked()
        entry.layer = self.layer_spin.value()
        entry.caps_enable = self.caps_check.isChecked()

        # Collect mods
        entry.mods = 0
        for mod_bit, cb in self.mod_checks.items():
            if cb.isChecked():
                entry.mods |= mod_bit

        # Key range - serialize to GUI format for consistent storage
        start, end = self.key_range.get_range()
        entry.keycode_start = Keycode.serialize(start)
        entry.keycode_end = Keycode.serialize(end)

        entry.sat_idle = self.idle_color.get_sat()
        entry.h_idle = self.idle_color.get_hue()
        entry.sat_pressed = self.pressed_color.get_sat()
        entry.h_pressed = self.pressed_color.get_hue()

        return entry


class RuleLightingPanel(QWidget):
    """Panel containing all Rule Lighting configuration"""

    changed = pyqtSignal()
    modified_changed = pyqtSignal(bool)  # Emitted when modified state changes

    def __init__(self):
        super().__init__()
        self.keyboard = None
        self.rule_widgets = []
        self.max_entries = 0
        self._modified = False

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        # Scrollable rules area
        self.rules_layout = QVBoxLayout()
        self.rules_layout.setContentsMargins(0, 0, 0, 0)
        self.rules_layout.setSpacing(2)
        scroll = make_scrollable(self.rules_layout)
        scroll.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(scroll, 1)

        self.setLayout(layout)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def set_keyboard(self, keyboard):
        self.keyboard = keyboard
        self.max_entries = keyboard.rule_lighting_count if keyboard else 0
        self._rebuild_rules()

    def _rebuild_rules(self):
        # Clear old
        for w in self.rule_widgets:
            w.deleteLater()
        self.rule_widgets = []

        if not self.keyboard or self.max_entries == 0:
            return

        # Create rule widgets for all possible entries
        for i in range(self.max_entries):
            widget = RuleWidget(i)
            widget.changed.connect(self._on_rule_change)
            self.rules_layout.addWidget(widget)
            self.rule_widgets.append(widget)

        self.rules_layout.addStretch()

    def load_from_keyboard(self):
        if not self.keyboard:
            return

        self.blockSignals(True)

        for i, widget in enumerate(self.rule_widgets):
            entry = self.keyboard.rule_lighting_get_entry(i)
            widget.load(entry)

        self.blockSignals(False)
        self._set_modified(False)

    def _set_modified(self, modified):
        if self._modified != modified:
            self._modified = modified
            self.modified_changed.emit(modified)

    def is_modified(self):
        return self._modified

    def mark_saved(self):
        """Called after Save to clear modified state"""
        self._set_modified(False)

    def _on_rule_change(self):
        self._save_entries()
        self._set_modified(True)

    def _save_entries(self):
        if not self.keyboard:
            return

        for i, widget in enumerate(self.rule_widgets):
            entry = widget.save()
            self.keyboard.rule_lighting_set_entry(i, entry)


# Special effect index for Rule Lighting mode
RULE_LIGHTING_EFFECT_IDX = 0xFE
