# coding: utf-8

# SPDX-License-Identifier: GPL-2.0-or-later

class Keycode:

    masked_keycodes = set()
    recorder_alias_to_keycode = dict()
    qmk_id_to_keycode = dict()

    def __init__(self, code, qmk_id, label, tooltip=None, masked=False, printable=None, recorder_alias=None,
                 alias=None):
        self.code = code
        self.qmk_id = qmk_id
        self.qmk_id_to_keycode[qmk_id] = self
        self.label = label
        self.tooltip = tooltip
        # whether this keycode requires another sub-keycode
        self.masked = masked

        # if this is printable keycode, what character does it normally output (i.e. non-shifted state)
        self.printable = printable

        self.alias = [self.qmk_id]
        if alias:
            self.alias += alias

        if recorder_alias:
            for alias in recorder_alias:
                if alias in self.recorder_alias_to_keycode:
                    raise RuntimeError("Misconfigured: two keycodes claim the same alias {}".format(alias))
                self.recorder_alias_to_keycode[alias] = self

        if masked:
            self.masked_keycodes.add(code)

    @classmethod
    def find(cls, code):
        for keycode in KEYCODES:
            if keycode.code == code:
                return keycode
        return None

    @classmethod
    def find_outer_keycode(cls, code):
        """
        Finds outer keycode, i.e. if it is masked like 0x5Fxx, just return the 0x5F00 portion
        """
        if cls.is_mask(code):
            code = code & 0xFF00
        return cls.find(code)

    @classmethod
    def find_by_recorder_alias(cls, alias):
        return cls.recorder_alias_to_keycode.get(alias)

    @classmethod
    def find_by_qmk_id(cls, qmk_id):
        return cls.qmk_id_to_keycode.get(qmk_id)

    @classmethod
    def is_mask(cls, code):
        return (code & 0xFF00) in cls.masked_keycodes

    @classmethod
    def label(cls, code):
        keycode = cls.find_outer_keycode(code)
        if keycode is None:
            return "0x{:X}".format(code)
        return keycode.label

    @classmethod
    def tooltip(cls, code):
        keycode = cls.find_outer_keycode(code)
        if keycode is None:
            return None
        tooltip = keycode.qmk_id
        if keycode.tooltip:
            tooltip = "{}: {}".format(tooltip, keycode.tooltip)
        return tooltip

    @classmethod
    def serialize(cls, code):
        if not cls.is_mask(code):
            kc = cls.find(code)
            if kc is not None:
                return kc.qmk_id
        elif cls.is_mask(code):
            outer = cls.find_outer_keycode(code)
            inner = cls.find(code & 0xFF)
            if outer is not None and inner is not None:
                return outer.qmk_id.replace("kc", inner.qmk_id)
        return code

    @classmethod
    def deserialize(cls, val, reraise=False):
        from any_keycode import AnyKeycode

        if isinstance(val, int):
            return val
        if "(" not in val and val in cls.qmk_id_to_keycode:
            return cls.qmk_id_to_keycode[val].code
        anykc = AnyKeycode()
        try:
            return anykc.decode(val)
        except Exception:
            if reraise:
                raise
        return 0


K = Keycode

KEYCODES_SPECIAL = [
    K(0x00, "KC_NO", ""),
    K(0x01, "KC_TRNS", "▽", alias=["KC_TRANSPARENT"]),
]

KEYCODES_BASIC = [
    K(0x04, "KC_A", "A", printable="a", recorder_alias=["a"]),
    K(0x05, "KC_B", "B", printable="b", recorder_alias=["b"]),
    K(0x06, "KC_C", "C", printable="c", recorder_alias=["c"]),
    K(0x07, "KC_D", "D", printable="d", recorder_alias=["d"]),
    K(0x08, "KC_E", "E", printable="e", recorder_alias=["e"]),
    K(0x09, "KC_F", "F", printable="f", recorder_alias=["f"]),
    K(0x0A, "KC_G", "G", printable="g", recorder_alias=["g"]),
    K(0x0B, "KC_H", "H", printable="h", recorder_alias=["h"]),
    K(0x0C, "KC_I", "I", printable="i", recorder_alias=["i"]),
    K(0x0D, "KC_J", "J", printable="j", recorder_alias=["j"]),
    K(0x0E, "KC_K", "K", printable="k", recorder_alias=["k"]),
    K(0x0F, "KC_L", "L", printable="l", recorder_alias=["l"]),
    K(0x10, "KC_M", "M", printable="m", recorder_alias=["m"]),
    K(0x11, "KC_N", "N", printable="n", recorder_alias=["n"]),
    K(0x12, "KC_O", "O", printable="o", recorder_alias=["o"]),
    K(0x13, "KC_P", "P", printable="p", recorder_alias=["p"]),
    K(0x14, "KC_Q", "Q", printable="q", recorder_alias=["q"]),
    K(0x15, "KC_R", "R", printable="r", recorder_alias=["r"]),
    K(0x16, "KC_S", "S", printable="s", recorder_alias=["s"]),
    K(0x17, "KC_T", "T", printable="t", recorder_alias=["t"]),
    K(0x18, "KC_U", "U", printable="u", recorder_alias=["u"]),
    K(0x19, "KC_V", "V", printable="v", recorder_alias=["v"]),
    K(0x1A, "KC_W", "W", printable="w", recorder_alias=["w"]),
    K(0x1B, "KC_X", "X", printable="x", recorder_alias=["x"]),
    K(0x1C, "KC_Y", "Y", printable="y", recorder_alias=["y"]),
    K(0x1D, "KC_Z", "Z", printable="z", recorder_alias=["z"]),
    K(0x1E, "KC_1", "!\n1", printable="1", recorder_alias=["1"]),
    K(0x1F, "KC_2", "@\n2", printable="2", recorder_alias=["2"]),
    K(0x20, "KC_3", "#\n3", printable="3", recorder_alias=["3"]),
    K(0x21, "KC_4", "$\n4", printable="4", recorder_alias=["4"]),
    K(0x22, "KC_5", "%\n5", printable="5", recorder_alias=["5"]),
    K(0x23, "KC_6", "^\n6", printable="6", recorder_alias=["6"]),
    K(0x24, "KC_7", "&\n7", printable="7", recorder_alias=["7"]),
    K(0x25, "KC_8", "*\n8", printable="8", recorder_alias=["8"]),
    K(0x26, "KC_9", "(\n9", printable="9", recorder_alias=["9"]),
    K(0x27, "KC_0", ")\n0", printable="0", recorder_alias=["0"]),
    K(0x28, "KC_ENTER", "Enter", recorder_alias=["enter"], alias=["KC_ENT"]),
    K(0x29, "KC_ESCAPE", "Esc", recorder_alias=["esc"], alias=["KC_ESC"]),
    K(0x2A, "KC_BSPACE", "Bksp", recorder_alias=["backspace"], alias=["KC_BSPC"]),
    K(0x2B, "KC_TAB", "Tab", recorder_alias=["tab"]),
    K(0x2C, "KC_SPACE", "Space", recorder_alias=["space"], alias=["KC_SPC"]),
    K(0x2D, "KC_MINUS", "_\n-", printable="-", recorder_alias=["-"], alias=["KC_MINS"]),
    K(0x2E, "KC_EQUAL", "+\n=", printable="=", recorder_alias=["="], alias=["KC_EQL"]),
    K(0x2F, "KC_LBRACKET", "{\n[", printable="[", recorder_alias=["["], alias=["KC_LBRC"]),
    K(0x30, "KC_RBRACKET", "}\n]", printable="]", recorder_alias=["]"], alias=["KC_RBRC"]),
    K(0x31, "KC_BSLASH", "|\n\\", printable="\\", recorder_alias=["\\"], alias=["KC_BSLS"]),
    K(0x33, "KC_SCOLON", ":\n;", printable=";", recorder_alias=[";"], alias=["KC_SCLN"]),
    K(0x34, "KC_QUOTE", "\"\n'", printable="'", recorder_alias=["'"], alias=["KC_QUOT"]),
    K(0x35, "KC_GRAVE", "~\n`", printable="`", recorder_alias=["`"], alias=["KC_GRV", "KC_ZKHK"]),
    K(0x36, "KC_COMMA", "<\n,", printable=",", recorder_alias=[","], alias=["KC_COMM"]),
    K(0x37, "KC_DOT", ">\n.", printable=".", recorder_alias=["."]),
    K(0x38, "KC_SLASH", "?\n/", printable="/", recorder_alias=["/"], alias=["KC_SLSH"]),
    K(0x39, "KC_CAPSLOCK", "Caps\nLock", recorder_alias=["caps lock"], alias=["KC_CLCK", "KC_CAPS"]),
    K(0x3A, "KC_F1", "F1", recorder_alias=["f1"]),
    K(0x3B, "KC_F2", "F2", recorder_alias=["f2"]),
    K(0x3C, "KC_F3", "F3", recorder_alias=["f3"]),
    K(0x3D, "KC_F4", "F4", recorder_alias=["f4"]),
    K(0x3E, "KC_F5", "F5", recorder_alias=["f5"]),
    K(0x3F, "KC_F6", "F6", recorder_alias=["f6"]),
    K(0x40, "KC_F7", "F7", recorder_alias=["f7"]),
    K(0x41, "KC_F8", "F8", recorder_alias=["f8"]),
    K(0x42, "KC_F9", "F9", recorder_alias=["f9"]),
    K(0x43, "KC_F10", "F10", recorder_alias=["f10"]),
    K(0x44, "KC_F11", "F11", recorder_alias=["f11"]),
    K(0x45, "KC_F12", "F12", recorder_alias=["f12"]),
    K(0x46, "KC_PSCREEN", "Print\nScreen", alias=["KC_PSCR"]),
    K(0x47, "KC_SCROLLLOCK", "Scroll\nLock", recorder_alias=["scroll lock"], alias=["KC_SLCK", "KC_BRMD"]),
    K(0x48, "KC_PAUSE", "Pause", recorder_alias=["pause", "break"], alias=["KC_PAUS", "KC_BRK", "KC_BRMU"]),
    K(0x49, "KC_INSERT", "Insert", recorder_alias=["insert"], alias=["KC_INS"]),
    K(0x4A, "KC_HOME", "Home", recorder_alias=["home"]),
    K(0x4B, "KC_PGUP", "Page\nUp", recorder_alias=["page up"]),
    K(0x4C, "KC_DELETE", "Del", recorder_alias=["delete"], alias=["KC_DEL"]),
    K(0x4D, "KC_END", "End", recorder_alias=["end"]),
    K(0x4E, "KC_PGDOWN", "Page\nDown", recorder_alias=["page down"], alias=["KC_PGDN"]),
    K(0x4F, "KC_RIGHT", "Right", recorder_alias=["right"], alias=["KC_RGHT"]),
    K(0x50, "KC_LEFT", "Left", recorder_alias=["left"]),
    K(0x51, "KC_DOWN", "Down", recorder_alias=["down"]),
    K(0x52, "KC_UP", "Up", recorder_alias=["up"]),
    K(0x53, "KC_NUMLOCK", "Num\nLock", recorder_alias=["num lock"], alias=["KC_NLCK"]),
    K(0x54, "KC_KP_SLASH", "/", alias=["KC_PSLS"]),
    K(0x55, "KC_KP_ASTERISK", "*", alias=["KC_PAST"]),
    K(0x56, "KC_KP_MINUS", "-", alias=["KC_PMNS"]),
    K(0x57, "KC_KP_PLUS", "+", alias=["KC_PPLS"]),
    K(0x58, "KC_KP_ENTER", "Num\nEnter", alias=["KC_PENT"]),
    K(0x59, "KC_KP_1", "1", alias=["KC_P1"]),
    K(0x5A, "KC_KP_2", "2", alias=["KC_P2"]),
    K(0x5B, "KC_KP_3", "3", alias=["KC_P3"]),
    K(0x5C, "KC_KP_4", "4", alias=["KC_P4"]),
    K(0x5D, "KC_KP_5", "5", alias=["KC_P5"]),
    K(0x5E, "KC_KP_6", "6", alias=["KC_P6"]),
    K(0x5F, "KC_KP_7", "7", alias=["KC_P7"]),
    K(0x60, "KC_KP_8", "8", alias=["KC_P8"]),
    K(0x61, "KC_KP_9", "9", alias=["KC_P9"]),
    K(0x62, "KC_KP_0", "0", alias=["KC_P0"]),
    K(0x63, "KC_KP_DOT", ".", alias=["KC_PDOT"]),
    K(0x65, "KC_APPLICATION", "Menu", recorder_alias=["menu", "left menu", "right menu"], alias=["KC_APP"]),
    K(0x67, "KC_KP_EQUAL", "=", alias=["KC_PEQL"]),
    K(0x85, "KC_KP_COMMA", ",", alias=["KC_PCMM"]),

    K(0xE0, "KC_LCTRL", "LCtrl", recorder_alias=["left ctrl", "ctrl"], alias=["KC_LCTL"]),
    K(0xE1, "KC_LSHIFT", "LShift", recorder_alias=["left shift", "shift"], alias=["KC_LSFT"]),
    K(0xE2, "KC_LALT", "LAlt", recorder_alias=["alt"], alias=["KC_LOPT"]),
    K(0xE3, "KC_LGUI", "LGui", recorder_alias=["left windows", "windows"], alias=["KC_LCMD", "KC_LWIN"]),
    K(0xE4, "KC_RCTRL", "RCtrl", recorder_alias=["right ctrl"], alias=["KC_RCTL"]),
    K(0xE5, "KC_RSHIFT", "RShift", recorder_alias=["right shift"], alias=["KC_RSFT"]),
    K(0xE6, "KC_RALT", "RAlt", alias=["KC_ALGR", "KC_ROPT"]),
    K(0xE7, "KC_RGUI", "RGui", recorder_alias=["right windows"], alias=["KC_RCMD", "KC_RWIN"]),
]

KEYCODES_SHIFTED = [
    K(0x235, "KC_TILD", "~"),
    K(0x21E, "KC_EXLM", "!"),
    K(0x21F, "KC_AT", "@"),
    K(0x220, "KC_HASH", "#"),
    K(0x221, "KC_DLR", "$"),
    K(0x222, "KC_PERC", "%"),
    K(0x223, "KC_CIRC", "^"),
    K(0x224, "KC_AMPR", "&"),
    K(0x225, "KC_ASTR", "*"),
    K(0x226, "KC_LPRN", "("),
    K(0x227, "KC_RPRN", ")"),
    K(0x22D, "KC_UNDS", "_"),
    K(0x22E, "KC_PLUS", "+"),
    K(0x22F, "KC_LCBR", "{"),
    K(0x230, "KC_RCBR", "}"),
    K(0x236, "KC_LT", "<"),
    K(0x237, "KC_GT", ">"),
    K(0x233, "KC_COLN", ":"),
    K(0x231, "KC_PIPE", "|"),
    K(0x238, "KC_QUES", "?"),
    K(0x234, "KC_DQUO", '"'),
]

KEYCODES_ISO = [
    K(0x32, "KC_NONUS_HASH", "~\n#", "Non-US # and ~", alias=["KC_NUHS"]),
    K(0x64, "KC_NONUS_BSLASH", "|\n\\", "Non-US \\ and |", alias=["KC_NUBS"]),
    K(0x87, "KC_RO", "_\n\\", "JIS \\ and _", alias=["KC_INT1"]),
    K(0x88, "KC_KANA", "カタカナ\nひらがな", "JIS Katakana/Hiragana", alias=["KC_INT2"]),
    K(0x89, "KC_JYEN", "|\n¥", alias=["KC_INT3"]),
    K(0x8A, "KC_HENK", "変換", "JIS Henkan", alias=["KC_INT4"]),
    K(0x8B, "KC_MHEN", "無変換", "JIS Muhenkan", alias=["KC_INT5"]),
    K(0x90, "KC_LANG1", "한영\nかな", "Korean Han/Yeong / JP Mac Kana", alias=["KC_HAEN"]),
    K(0x91, "KC_LANG2", "漢字\n英数", "Korean Hanja / JP Mac Eisu", alias=["KC_HANJ"]),
]

KEYCODES_LAYERS = []

QK_LAYER_TAP = 0x4000
QK_ONE_SHOT_MOD = 0x5500
QK_MOD_TAP = 0x6000

MOD_LCTL = 0x01
MOD_LSFT = 0x02
MOD_LALT = 0x04
MOD_LGUI = 0x08
MOD_RCTL = 0x11
MOD_RSFT = 0x12
MOD_RALT = 0x14
MOD_RGUI = 0x18

MOD_HYPR = 0xF
MOD_MEH = 0x7

QK_LCTL = 0x0100
QK_LSFT = 0x0200
QK_LALT = 0x0400
QK_LGUI = 0x0800
QK_RCTL = 0x1100
QK_RSFT = 0x1200
QK_RALT = 0x1400
QK_RGUI = 0x1800


def MT(mod):
    return QK_MOD_TAP | (mod << 8)


def LT(layer):
    return QK_LAYER_TAP | (((layer) & 0xF) << 8)


RESET_KEYCODE = 0x5C00


KEYCODES_QUANTUM = [
    K(RESET_KEYCODE, "RESET", "Reset", "Reboot to bootloader"),
    K(QK_ONE_SHOT_MOD | MOD_LSFT, "OSM(MOD_LSFT)", "OSM\nLSft", "Enable Left Shift for one keypress"),
    K(QK_ONE_SHOT_MOD | MOD_LCTL, "OSM(MOD_LCTL)", "OSM\nLCtl", "Enable Left Control for one keypress"),
    K(QK_ONE_SHOT_MOD | MOD_LALT, "OSM(MOD_LALT)", "OSM\nLAlt", "Enable Left Alt for one keypress"),
    K(QK_ONE_SHOT_MOD | MOD_LGUI, "OSM(MOD_LGUI)", "OSM\nLGUI", "Enable Left GUI for one keypress"),
    K(QK_ONE_SHOT_MOD | MOD_RSFT, "OSM(MOD_RSFT)", "OSM\nRSft", "Enable Right Shift for one keypress"),
    K(QK_ONE_SHOT_MOD | MOD_RCTL, "OSM(MOD_RCTL)", "OSM\nRCtl", "Enable Right Control for one keypress"),
    K(QK_ONE_SHOT_MOD | MOD_RALT, "OSM(MOD_RALT)", "OSM\nRAlt", "Enable Right Alt for one keypress"),
    K(QK_ONE_SHOT_MOD | MOD_RGUI, "OSM(MOD_RGUI)", "OSM\nRGUI", "Enable Right GUI for one keypress"),
    K(QK_ONE_SHOT_MOD | MOD_LCTL | MOD_LSFT, "OSM(MOD_LCTL|MOD_LSFT)", "OSM\nCS",
      "Enable Control and Shift for one keypress"),
    K(QK_ONE_SHOT_MOD | MOD_LCTL | MOD_LALT, "OSM(MOD_LCTL|MOD_LALT)", "OSM\nCA",
      "Enable Control and Alt for one keypress"),
    K(QK_ONE_SHOT_MOD | MOD_LCTL | MOD_LGUI, "OSM(MOD_LCTL|MOD_LGUI)", "OSM\nCG",
      "Enable Control and GUI for one keypress"),
    K(QK_ONE_SHOT_MOD | MOD_LSFT | MOD_LALT, "OSM(MOD_LSFT|MOD_LALT)", "OSM\nSA",
      "Enable Shift and Alt for one keypress"),
    K(QK_ONE_SHOT_MOD | MOD_LSFT | MOD_LGUI, "OSM(MOD_LSFT|MOD_LGUI)", "OSM\nSG",
      "Enable Shift and GUI for one keypress"),
    K(QK_ONE_SHOT_MOD | MOD_LALT | MOD_LGUI, "OSM(MOD_LALT|MOD_LGUI)", "OSM\nAG",
      "Enable Alt and GUI for one keypress"),
    K(QK_ONE_SHOT_MOD | MOD_LCTL | MOD_LSFT | MOD_LGUI, "OSM(MOD_LCTL|MOD_LSFT|MOD_LGUI)", "OSM\nCSG",
      "Enable Control, Shift, and GUI for one keypress"),
    K(QK_ONE_SHOT_MOD | MOD_LCTL | MOD_LALT | MOD_LGUI, "OSM(MOD_LCTL|MOD_LALT|MOD_LGUI)", "OSM\nCAG",
      "Enable Control, Alt, and GUI for one keypress"),
    K(QK_ONE_SHOT_MOD | MOD_LSFT | MOD_LALT | MOD_LGUI, "OSM(MOD_LSFT|MOD_LALT|MOD_LGUI)", "OSM\nSAG",
      "Enable Shift, Alt, and GUI for one keypress"),
    K(QK_ONE_SHOT_MOD | MOD_MEH, "OSM(MOD_MEH)", "OSM\nMeh", "Enable Control, Shift, and Alt for one keypress"),
    K(QK_ONE_SHOT_MOD | MOD_HYPR, "OSM(MOD_HYPR)", "OSM\nHyper",
      "Enable Control, Shift, Alt, and GUI for one keypress"),

    K(QK_LSFT, "LSFT(kc)", "LSft\n(kc)", masked=True),
    K(QK_LCTL, "LCTL(kc)", "LCtl\n(kc)", masked=True),
    K(QK_LALT, "LALT(kc)", "LAlt\n(kc)", masked=True),
    K(QK_LGUI, "LGUI(kc)", "LGui\n(kc)", masked=True),
    K(QK_RSFT, "RSFT(kc)", "RSft\n(kc)", masked=True),
    K(QK_RCTL, "RCTL(kc)", "RCtl\n(kc)", masked=True),
    K(QK_RALT, "RALT(kc)", "RAlt\n(kc)", masked=True),
    K(QK_RGUI, "RGUI(kc)", "RGui\n(kc)", masked=True),

    K(MT(MOD_LSFT), "LSFT_T(kc)", "LSft_T\n(kc)", "Left Shift when held, kc when tapped", masked=True),
    K(MT(MOD_LCTL), "LCTL_T(kc)", "LCtl_T\n(kc)", "Left Control when held, kc when tapped", masked=True),
    K(MT(MOD_LALT), "LALT_T(kc)", "LAlt_T\n(kc)", "Left Alt when held, kc when tapped", masked=True),
    K(MT(MOD_LGUI), "LGUI_T(kc)", "LGui_T\n(kc)", "Left GUI when held, kc when tapped", masked=True),
    K(MT(MOD_RSFT), "RSFT_T(kc)", "RSft_T\n(kc)", "Right Shift when held, kc when tapped", masked=True),
    K(MT(MOD_RCTL), "RCTL_T(kc)", "RCtl_T\n(kc)", "Right Control when held, kc when tapped", masked=True),
    K(MT(MOD_RALT), "RALT_T(kc)", "RAlt_T\n(kc)", "Right Alt when held, kc when tapped", masked=True),
    K(MT(MOD_RGUI), "RGUI_T(kc)", "RGui_T\n(kc)", "Right GUI when held, kc when tapped", masked=True),
    K(MT(MOD_LCTL|MOD_LSFT), "C_S_T(kc)", "C_S_T\n(kc)", "Left Control + Left Shift when held, kc when tapped",
      masked=True),
    K(MT(MOD_LCTL|MOD_LSFT|MOD_LALT|MOD_LGUI), "ALL_T(kc)",
      "ALL_T\n(kc)", "LCTL + LSFT + LALT + LGUI when held, kc when tapped", masked=True),
    K(MT(MOD_LCTL|MOD_LSFT|MOD_LALT), "MEH_T(kc)", "Meh_T\n(kc)", "LCTL + LSFT + LALT when held, kc when tapped",
      masked=True),
    K(MT(MOD_LCTL|MOD_LALT|MOD_LGUI), "LCAG_T(kc)", "LCAG_T\n(kc)", "LCTL + LALT + LGUI when held, kc when tapped",
      masked=True),
    K(MT(MOD_RCTL|MOD_RALT|MOD_RGUI), "RCAG_T(kc)", "RCAG_T\n(kc)", "RCTL + RALT + RGUI when held, kc when tapped",
      masked=True),
    K(MT(MOD_LGUI|MOD_LSFT), "SGUI_T(kc)", "SGUI_T\n(kc)", "LGUI + LSFT when held, kc when tapped", masked=True),
    K(MT(MOD_LCTL|MOD_LALT), "LCA_T(kc)", "LCA_T\n(kc)", "LCTL + LALT when held, kc when tapped", masked=True),
    K(MT(MOD_LSFT|MOD_LALT), "LSA_T(kc)", "LSA_T\n(kc)", "LSFT + LALT when held, kc when tapped", masked=True),
    K(MT(MOD_LCTL|MOD_LGUI), "LCG_T(kc)", "LCG_T\n(kc)", "LCTL + LGUI when held, kc when tapped", masked=True),
    K(MT(MOD_RCTL|MOD_RGUI), "RCG_T(kc)", "RCG_T\n(kc)", "RCTL + RGUI when held, kc when tapped", masked=True),

    K(QK_LCTL|QK_LSFT|QK_LALT|QK_LGUI, "HYPR(kc)", "Hyper\n(kc)", "LCTL + LSFT + LALT + LGUI", masked=True),
    K(QK_LCTL|QK_LSFT|QK_LALT, "MEH(kc)", "Meh\n(kc)", "LCTL + LSFT + LALT", masked=True),
    K(QK_LCTL|QK_LALT|QK_LGUI, "LCAG(kc)", "LCAG\n(kc)", "LCTL + LALT + LGUI", masked=True),
    K(QK_LGUI|QK_LSFT, "SGUI(kc)", "SGUI\n(kc)", "LGUI + LSFT", masked=True),
    K(QK_LCTL|QK_LALT, "LCA(kc)", "LCA\n(kc)", "LCTL + LALT", masked=True),
    K(QK_LSFT|QK_LALT, "LSA(kc)", "LSA\n(kc)", "LSFT + LALT", masked=True),
    K(QK_LCTL|QK_LSFT, "C_S(kc)", "C_S\n(kc)", "LCTL + LSFT", masked=True),
    K(QK_LCTL|QK_LGUI, "LCG(kc)", "LCG\n(kc)", "LCTL + LGUI", masked=True),
    K(QK_RCTL|QK_RGUI, "RCG(kc)", "RCG\n(kc)", "RCTL + RGUI", masked=True),

    K(0x5C16, "KC_GESC", "~\nEsc", "Esc normally, but ~ when Shift or GUI is pressed"),
    K(0x5CD7, "KC_LSPO", "LS\n(", "Left Shift when held, ( when tapped"),
    K(0x5CD8, "KC_RSPC", "RS\n)", "Right Shift when held, ) when tapped"),
    K(0x5CF3, "KC_LCPO", "LC\n(", "Left Control when held, ( when tapped"),
    K(0x5CF4, "KC_RCPC", "RC\n)", "Right Control when held, ) when tapped"),
    K(0x5CF5, "KC_LAPO", "LA\n(", "Left Alt when held, ( when tapped"),
    K(0x5CF6, "KC_RAPC", "RA\n)", "Right Alt when held, ) when tapped"),
    K(0x5CD9, "KC_SFTENT", "RS\nEnter", "Right Shift when held, Enter when tapped"),

    K(23554, "MAGIC_SWAP_CONTROL_CAPSLOCK", "Swap\nCtrl\nCaps", "Swap Caps Lock and Left Control", alias=["CL_SWAP"]),
    K(23563, "MAGIC_UNSWAP_CONTROL_CAPSLOCK", "Unswap\nCtrl\nCaps", "Unswap Caps Lock and Left Control",
      alias=["CL_NORM"]),
    K(23555, "MAGIC_CAPSLOCK_TO_CONTROL", "Caps\nto\nCtrl", "Treat Caps Lock as Control", alias=["CL_CTRL"]),
    K(23564, "MAGIC_UNCAPSLOCK_TO_CONTROL", "Caps\nnot to\nCtrl", "Stop treating Caps Lock as Control",
      alias=["CL_CAPS"]),
    K(23802, "MAGIC_SWAP_LCTL_LGUI", "Swap\nLCtl\nLGui", "Swap Left Control and GUI", alias=["LCG_SWP"]),
    K(23804, "MAGIC_UNSWAP_LCTL_LGUI", "Unswap\nLCtl\nLGui", "Unswap Left Control and GUI", alias=["LCG_NRM"]),
    K(23803, "MAGIC_SWAP_RCTL_RGUI", "Swap\nRCtl\nRGui", "Swap Right Control and GUI", alias=["RCG_SWP"]),
    K(23805, "MAGIC_UNSWAP_RCTL_RGUI", "Unswap\nRCtl\nRGui", "Unswap Right Control and GUI", alias=["RCG_NRM"]),
    K(23806, "MAGIC_SWAP_CTL_GUI", "Swap\nCtl\nGui", "Swap Control and GUI on both sides", alias=["CG_SWAP"]),
    K(23807, "MAGIC_UNSWAP_CTL_GUI", "Unswap\nCtl\nGui", "Unswap Control and GUI on both sides", alias=["CG_NORM"]),
    K(23808, "MAGIC_TOGGLE_CTL_GUI", "Toggle\nCtl\nGui", "Toggle Control and GUI swap on both sides",
      alias=["CG_TOGG"]),
    K(23556, "MAGIC_SWAP_LALT_LGUI", "Swap\nLAlt\nLGui", "Swap Left Alt and GUI", alias=["LAG_SWP"]),
    K(23565, "MAGIC_UNSWAP_LALT_LGUI", "Unswap\nLAlt\nLGui", "Unswap Left Alt and GUI", alias=["LAG_NRM"]),
    K(23557, "MAGIC_SWAP_RALT_RGUI", "Swap\nRAlt\nRGui", "Swap Right Alt and GUI", alias=["RAG_SWP"]),
    K(23566, "MAGIC_UNSWAP_RALT_RGUI", "Unswap\nRAlt\nRGui", "Unswap Right Alt and GUI", alias=["RAG_NRM"]),
    K(23562, "MAGIC_SWAP_ALT_GUI", "Swap\nAlt\nGui", "Swap Alt and GUI on both sides", alias=["AG_SWAP"]),
    K(23571, "MAGIC_UNSWAP_ALT_GUI", "Unswap\nAlt\nGui", "Unswap Alt and GUI on both sides", alias=["AG_NORM"]),
    K(23573, "MAGIC_TOGGLE_ALT_GUI", "Toggle\nAlt\nGui", "Toggle Alt and GUI swap on both sides", alias=["AG_TOGG"]),
    K(23558, "MAGIC_NO_GUI", "GUI\nOff", "Disable the GUI keys", alias=["GUI_OFF"]),
    K(23567, "MAGIC_UNNO_GUI", "GUI\nOn", "Enable the GUI keys", alias=["GUI_ON"]),
    K(23559, "MAGIC_SWAP_GRAVE_ESC", "Swap\n`\nEsc", "Swap ` and Escape", alias=["GE_SWAP"]),
    K(23568, "MAGIC_UNSWAP_GRAVE_ESC", "Unswap\n`\nEsc", "Unswap ` and Escape", alias=["GE_NORM"]),
    K(23560, "MAGIC_SWAP_BACKSLASH_BACKSPACE", "Swap\n\\\nBS", "Swap \\ and Backspace", alias=["BS_SWAP"]),
    K(23569, "MAGIC_UNSWAP_BACKSLASH_BACKSPACE", "Unswap\n\\\nBS", "Unswap \\ and Backspace",
      alias=["BS_NORM"]),
    K(23561, "MAGIC_HOST_NKRO", "NKRO\nOn", "Enable N-key rollover", alias=["NK_ON"]),
    K(23570, "MAGIC_UNHOST_NKRO", "NKRO\nOff", "Disable N-key rollover", alias=["NK_OFF"]),
    K(23572, "MAGIC_TOGGLE_NKRO", "NKRO\nToggle", "Toggle N-key rollover", alias=["NK_TOGG"]),
    K(23809, "MAGIC_EE_HANDS_LEFT", "EEH\nLeft",
      "Set the master half of a split keyboard as the left hand (for EE_HANDS)", alias=["EH_LEFT"]),
    K(23810, "MAGIC_EE_HANDS_RIGHT", "EEH\nRight",
      "Set the master half of a split keyboard as the right hand (for EE_HANDS)", alias=["EH_RGHT"]),

    K(0x5C1D, "AU_ON", "Audio\nON", "Audio mode on"),
    K(0x5C1E, "AU_OFF", "Audio\nOFF", "Audio mode off"),
    K(0x5C1F, "AU_TOG", "Audio\nToggle", "Toggles Audio mode"),
    K(0x5C20, "CLICKY_TOGGLE", "Clicky\nToggle", "Toggles Audio clicky mode", alias=["CK_TOGG"]),
    K(0x5C23, "CLICKY_UP", "Clicky\nUp", "Increases frequency of the clicks", alias=["CK_UP"]),
    K(0x5C24, "CLICKY_DOWN", "Clicky\nDown", "Decreases frequency of the clicks", alias=["CK_DOWN"]),
    K(0x5C25, "CLICKY_RESET", "Clicky\nReset", "Resets frequency to default", alias=["CK_RST"]),
    K(0x5C26, "MU_ON", "Music\nOn", "Turns on Music Mode"),
    K(0x5C27, "MU_OFF", "Music\nOff", "Turns off Music Mode"),
    K(0x5C28, "MU_TOG", "Music\nToggle", "Toggles Music Mode"),
    K(0x5C29, "MU_MOD", "Music\nCycle", "Cycles through the music modes"),

    K(0x5CE6, "HPT_ON", "Haptic\nOn", "Turn haptic feedback on"),
    K(0x5CE7, "HPT_OFF", "Haptic\nOff", "Turn haptic feedback off"),
    K(0x5CE8, "HPT_TOG", "Haptic\nToggle", "Toggle haptic feedback on/off"),
    K(0x5CE9, "HPT_RST", "Haptic\nReset", "Reset haptic feedback config to default"),
    K(0x5CEA, "HPT_FBK", "Haptic\nFeed\nback", "Toggle feedback to occur on keypress, release or both"),
    K(0x5CEB, "HPT_BUZ", "Haptic\nBuzz", "Toggle solenoid buzz on/off"),
    K(0x5CEC, "HPT_MODI", "Haptic\nNext", "Go to next DRV2605L waveform"),
    K(0x5CED, "HPT_MODD", "Haptic\nPrev", "Go to previous DRV2605L waveform"),
    K(0x5CEE, "HPT_CONT", "Haptic\nCont.", "Toggle continuous haptic mode on/off"),
    K(0x5CEF, "HPT_CONI", "Haptic\n+", "Increase DRV2605L continous haptic strength"),
    K(0x5CF0, "HPT_COND", "Haptic\n-", "Decrease DRV2605L continous haptic strength"),
    K(0x5CF1, "HPT_DWLI", "Haptic\nDwell+", "Increase Solenoid dwell time"),
    K(0x5CF2, "HPT_DWLD", "Haptic\nDwell-", "Decrease Solenoid dwell time"),
]

KEYCODES_BACKLIGHT = [
    K(23743, "BL_TOGG", "BL\nToggle", "Turn the backlight on or off"),
    K(23744, "BL_STEP", "BL\nCycle", "Cycle through backlight levels"),
    K(23745, "BL_BRTG", "BL\nBreath", "Toggle backlight breathing"),
    K(23739, "BL_ON", "BL On", "Set the backlight to max brightness"),
    K(23740, "BL_OFF", "BL Off", "Turn the backlight off"),
    K(23742, "BL_INC", "BL +", "Increase the backlight level"),
    K(23741, "BL_DEC", "BL - ", "Decrease the backlight level"),

    K(23746, "RGB_TOG", "RGB\nToggle", "Toggle RGB lighting on or off"),
    K(23747, "RGB_MOD", "RGB\nMode +", "Next RGB mode"),
    K(23748, "RGB_RMOD", "RGB\nMode -", "Previous RGB mode"),
    K(23749, "RGB_HUI", "Hue +", "Increase hue"),
    K(23750, "RGB_HUD", "Hue -", "Decrease hue"),
    K(23751, "RGB_SAI", "Sat +", "Increase saturation"),
    K(23752, "RGB_SAD", "Sat -", "Decrease saturation"),
    K(23753, "RGB_VAI", "Bright +", "Increase value"),
    K(23754, "RGB_VAD", "Bright -", "Decrease value"),
    K(23755, "RGB_SPI", "Effect +", "Increase RGB effect speed"),
    K(23756, "RGB_SPD", "Effect -", "Decrease RGB effect speed"),
    K(23757, "RGB_M_P", "RGB\nMode P", "RGB Mode: Plain"),
    K(23758, "RGB_M_B", "RGB\nMode B", "RGB Mode: Breathe"),
    K(23759, "RGB_M_R", "RGB\nMode R", "RGB Mode: Rainbow"),
    K(23760, "RGB_M_SW", "RGB\nMode SW", "RGB Mode: Swirl"),
    K(23761, "RGB_M_SN", "RGB\nMode SN", "RGB Mode: Snake"),
    K(23762, "RGB_M_K", "RGB\nMode K", "RGB Mode: Knight Rider"),
    K(23763, "RGB_M_X", "RGB\nMode X", "RGB Mode: Christmas"),
    K(23764, "RGB_M_G", "RGB\nMode G", "RGB Mode: Gradient"),
    K(23765, "RGB_M_T", "RGB\nMode T", "RGB Mode: Test"),
]

KEYCODES_MEDIA = [
    K(104, "KC_F13", "F13"),
    K(105, "KC_F14", "F14"),
    K(106, "KC_F15", "F15"),
    K(107, "KC_F16", "F16"),
    K(108, "KC_F17", "F17"),
    K(109, "KC_F18", "F18"),
    K(110, "KC_F19", "F19"),
    K(111, "KC_F20", "F20"),
    K(112, "KC_F21", "F21"),
    K(113, "KC_F22", "F22"),
    K(114, "KC_F23", "F23"),
    K(115, "KC_F24", "F24"),

    K(165, "KC_PWR", "Power", "System Power Down", alias=["KC_SYSTEM_POWER"]),
    K(166, "KC_SLEP", "Sleep", "System Sleep", alias=["KC_SYSTEM_SLEEP"]),
    K(167, "KC_WAKE", "Wake", "System Wake", alias=["KC_SYSTEM_WAKE"]),
    K(116, "KC_EXEC", "Exec", "Execute", alias=["KC_EXECUTE"]),
    K(117, "KC_HELP", "Help"),
    K(119, "KC_SLCT", "Select", alias=["KC_SELECT"]),
    K(120, "KC_STOP", "Stop"),
    K(121, "KC_AGIN", "Again", alias=["KC_AGAIN"]),
    K(122, "KC_UNDO", "Undo"),
    K(123, "KC_CUT", "Cut"),
    K(124, "KC_COPY", "Copy"),
    K(125, "KC_PSTE", "Paste", alias=["KC_PASTE"]),
    K(126, "KC_FIND", "Find"),

    K(178, "KC_CALC", "Calc", "Launch Calculator (Windows)", alias=["KC_CALCULATOR"]),
    K(177, "KC_MAIL", "Mail", "Launch Mail (Windows)"),
    K(175, "KC_MSEL", "Media\nPlayer", "Launch Media Player (Windows)", alias=["KC_MEDIA_SELECT"]),
    K(179, "KC_MYCM", "My\nPC", "Launch My Computer (Windows)", alias=["KC_MY_COMPUTER"]),
    K(180, "KC_WSCH", "Browser\nSearch", "Browser Search (Windows)", alias=["KC_WWW_SEARCH"]),
    K(181, "KC_WHOM", "Browser\nHome", "Browser Home (Windows)", alias=["KC_WWW_HOME"]),
    K(182, "KC_WBAK", "Browser\nBack", "Browser Back (Windows)", alias=["KC_WWW_BACK"]),
    K(183, "KC_WFWD", "Browser\nForward", "Browser Forward (Windows)", alias=["KC_WWW_FORWARD"]),
    K(184, "KC_WSTP", "Browser\nStop", "Browser Stop (Windows)", alias=["KC_WWW_STOP"]),
    K(185, "KC_WREF", "Browser\nRefresh", "Browser Refresh (Windows)", alias=["KC_WWW_REFRESH"]),
    K(186, "KC_WFAV", "Browser\nFav.", "Browser Favorites (Windows)", alias=["KC_WWW_FAVORITES"]),
    K(189, "KC_BRIU", "Bright.\nUp", "Increase the brightness of screen (Laptop)", alias=["KC_BRIGHTNESS_UP"]),
    K(190, "KC_BRID", "Bright.\nDown", "Decrease the brightness of screen (Laptop)", alias=["KC_BRIGHTNESS_DOWN"]),

    K(172, "KC_MPRV", "Media\nPrev", "Previous Track", alias=["KC_MEDIA_PREV_TRACK"]),
    K(171, "KC_MNXT", "Media\nNext", "Next Track", alias=["KC_MEDIA_NEXT_TRACK"]),
    K(168, "KC_MUTE", "Mute", "Mute Audio", alias=["KC_AUDIO_MUTE"]),
    K(170, "KC_VOLD", "Vol -", "Volume Down", alias=["KC_AUDIO_VOL_DOWN"]),
    K(169, "KC_VOLU", "Vol +", "Volume Up", alias=["KC_AUDIO_VOL_UP"]),
    K(129, "KC__VOLDOWN", "Vol -\nAlt", "Volume Down Alternate"),
    K(128, "KC__VOLUP", "Vol +\nAlt", "Volume Up Alternate"),
    K(173, "KC_MSTP", "Media\nStop", alias=["KC_MEDIA_STOP"]),
    K(174, "KC_MPLY", "Media\nPlay", "Play/Pause", alias=["KC_MEDIA_PLAY_PAUSE"]),
    K(188, "KC_MRWD", "Prev\nTrack\n(macOS)", "Previous Track / Rewind (macOS)", alias=["KC_MEDIA_REWIND"]),
    K(187, "KC_MFFD", "Next\nTrack\n(macOS)", "Next Track / Fast Forward (macOS)", alias=["KC_MEDIA_FAST_FORWARD"]),
    K(176, "KC_EJCT", "Eject", "Eject (macOS)", alias=["KC_MEDIA_EJECT"]),

    K(240, "KC_MS_U", "Mouse\nUp", "Mouse Cursor Up", alias=["KC_MS_UP"]),
    K(241, "KC_MS_D", "Mouse\nDown", "Mouse Cursor Down", alias=["KC_MS_DOWN"]),
    K(242, "KC_MS_L", "Mouse\nLeft", "Mouse Cursor Left", alias=["KC_MS_LEFT"]),
    K(243, "KC_MS_R", "Mouse\nRight", "Mouse Cursor Right", alias=["KC_MS_RIGHT"]),
    K(244, "KC_BTN1", "Mouse\n1", "Mouse Button 1", alias=["KC_MS_BTN1"]),
    K(245, "KC_BTN2", "Mouse\n2", "Mouse Button 2", alias=["KC_MS_BTN2"]),
    K(246, "KC_BTN3", "Mouse\n3", "Mouse Button 3", alias=["KC_MS_BTN3"]),
    K(247, "KC_BTN4", "Mouse\n4", "Mouse Button 4", alias=["KC_MS_BTN4"]),
    K(248, "KC_BTN5", "Mouse\n5", "Mouse Button 5", alias=["KC_MS_BTN5"]),
    K(249, "KC_WH_U", "Mouse\nWheel\nUp", alias=["KC_MS_WH_UP"]),
    K(250, "KC_WH_D", "Mouse\nWheel\nDown", alias=["KC_MS_WH_DOWN"]),
    K(251, "KC_WH_L", "Mouse\nWheel\nLeft", alias=["KC_MS_WH_LEFT"]),
    K(252, "KC_WH_R", "Mouse\nWheel\nRight", alias=["KC_MS_WH_RIGHT"]),
    K(253, "KC_ACL0", "Mouse\nAccel\n0", "Set mouse acceleration to 0", alias=["KC_MS_ACCEL0"]),
    K(254, "KC_ACL1", "Mouse\nAccel\n1", "Set mouse acceleration to 1", alias=["KC_MS_ACCEL1"]),
    K(255, "KC_ACL2", "Mouse\nAccel\n2", "Set mouse acceleration to 2", alias=["KC_MS_ACCEL2"]),

    K(130, "KC_LCAP", "Locking\nCaps", "Locking Caps Lock", alias=["KC_LOCKING_CAPS"]),
    K(131, "KC_LNUM", "Locking\nNum", "Locking Num Lock", alias=["KC_LOCKING_NUM"]),
    K(132, "KC_LSCR", "Locking\nScroll", "Locking Scroll Lock", alias=["KC_LOCKING_SCROLL"]),
]

KEYCODES_TAP_DANCE = []

KEYCODES_USER = []

KEYCODES_MACRO = []

KEYCODES_MACRO_BASE = [
    K(0x5D03, "DYN_REC_START1", "DM1\nRec", "Dynamic Macro 1 Rec Start", alias=["DM_REC1"]),
    K(0x5D04, "DYN_REC_START2", "DM2\nRec", "Dynamic Macro 2 Rec Start", alias=["DM_REC2"]),
    K(0x5D05, "DYN_REC_STOP", "DM Rec\nStop", "Dynamic Macro Rec Stop", alias=["DM_RSTP"]),
    K(0x5D06, "DYN_MACRO_PLAY1", "DM1\nPlay", "Dynamic Macro 1 Play", alias=["DM_PLY1"]),
    K(0x5D07, "DYN_MACRO_PLAY2", "DM2\nPlay", "Dynamic Macro 2 Play", alias=["DM_PLY2"]),
]

KEYCODES_MIDI = []

KEYCODES_MIDI_BASIC = [
    K(0x5C2F, "MI_C", "ᴹᴵᴰᴵ\nC", "Midi send note C"),
    K(0x5C30, "MI_Cs", "ᴹᴵᴰᴵ\nC#/Dᵇ", "Midi send note C#/Dᵇ", alias=["MI_Db"]),
    K(0x5C31, "MI_D", "ᴹᴵᴰᴵ\nD", "Midi send note D"),
    K(0x5C32, "MI_Ds", "ᴹᴵᴰᴵ\nD#/Eᵇ", "Midi send note D#/Eᵇ", alias=["MI_Eb"]),
    K(0x5C33, "MI_E", "ᴹᴵᴰᴵ\nE", "Midi send note E"),
    K(0x5C34, "MI_F", "ᴹᴵᴰᴵ\nF", "Midi send note F"),
    K(0x5C35, "MI_Fs", "ᴹᴵᴰᴵ\nF#/Gᵇ", "Midi send note F#/Gᵇ", alias=["MI_Gb"]),
    K(0x5C36, "MI_G", "ᴹᴵᴰᴵ\nG", "Midi send note G"),
    K(0x5C37, "MI_Gs", "ᴹᴵᴰᴵ\nG#/Aᵇ", "Midi send note G#/Aᵇ", alias=["MI_Ab"]),
    K(0x5C38, "MI_A", "ᴹᴵᴰᴵ\nA", "Midi send note A"),
    K(0x5C39, "MI_As", "ᴹᴵᴰᴵ\nA#/Bᵇ", "Midi send note A#/Bᵇ", alias=["MI_Bb"]),
    K(0x5C3A, "MI_B", "ᴹᴵᴰᴵ\nB", "Midi send note B"),

    K(0x5C3B, "MI_C_1", "ᴹᴵᴰᴵ\nC₁", "Midi send note C₁"),
    K(0x5C3C, "MI_Cs_1", "ᴹᴵᴰᴵ\nC#₁/Dᵇ₁", "Midi send note C#₁/Dᵇ₁", alias=["MI_Db_1"]),
    K(0x5C3D, "MI_D_1", "ᴹᴵᴰᴵ\nD₁", "Midi send note D₁"),
    K(0x5C3E, "MI_Ds_1", "ᴹᴵᴰᴵ\nD#₁/Eᵇ₁", "Midi send note D#₁/Eᵇ₁", alias=["MI_Eb_1"]),
    K(0x5C3F, "MI_E_1", "ᴹᴵᴰᴵ\nE₁", "Midi send note E₁"),
    K(0x5C40, "MI_F_1", "ᴹᴵᴰᴵ\nF₁", "Midi send note F₁"),
    K(0x5C41, "MI_Fs_1", "ᴹᴵᴰᴵ\nF#₁/Gᵇ₁", "Midi send note F#₁/Gᵇ₁", alias=["MI_Gb_1"]),
    K(0x5C42, "MI_G_1", "ᴹᴵᴰᴵ\nG₁", "Midi send note G₁"),
    K(0x5C43, "MI_Gs_1", "ᴹᴵᴰᴵ\nG#₁/Aᵇ₁", "Midi send note G#₁/Aᵇ₁", alias=["MI_Ab_1"]),
    K(0x5C44, "MI_A_1", "ᴹᴵᴰᴵ\nA₁", "Midi send note A₁"),
    K(0x5C45, "MI_As_1", "ᴹᴵᴰᴵ\nA#₁/Bᵇ₁", "Midi send note A#₁/Bᵇ₁", alias=["MI_Bb_1"]),
    K(0x5C46, "MI_B_1", "ᴹᴵᴰᴵ\nB₁", "Midi send note B₁"),

    K(0x5C47, "MI_C_2", "ᴹᴵᴰᴵ\nC₂", "Midi send note C₂"),
    K(0x5C48, "MI_Cs_2", "ᴹᴵᴰᴵ\nC#₂/Dᵇ₂", "Midi send note C#₂/Dᵇ₂", alias=["MI_Db_2"]),
    K(0x5C49, "MI_D_2", "ᴹᴵᴰᴵ\nD₂", "Midi send note D₂"),
    K(0x5C4A, "MI_Ds_2", "ᴹᴵᴰᴵ\nD#₂/Eᵇ₂", "Midi send note D#₂/Eᵇ₂", alias=["MI_Eb_2"]),
    K(0x5C4B, "MI_E_2", "ᴹᴵᴰᴵ\nE₂", "Midi send note E₂"),
    K(0x5C4C, "MI_F_2", "ᴹᴵᴰᴵ\nF₂", "Midi send note F₂"),
    K(0x5C4D, "MI_Fs_2", "ᴹᴵᴰᴵ\nF#₂/Gᵇ₂", "Midi send note F#₂/Gᵇ₂", alias=["MI_Gb_2"]),
    K(0x5C4E, "MI_G_2", "ᴹᴵᴰᴵ\nG₂", "Midi send note G₂"),
    K(0x5C4F, "MI_Gs_2", "ᴹᴵᴰᴵ\nG#₂/Aᵇ₂", "Midi send note G#₂/Aᵇ₂", alias=["MI_Ab_2"]),
    K(0x5C50, "MI_A_2", "ᴹᴵᴰᴵ\nA₂", "Midi send note A₂"),
    K(0x5C51, "MI_As_2", "ᴹᴵᴰᴵ\nA#₂/Bᵇ₂", "Midi send note A#₂/Bᵇ₂", alias=["MI_Bb_2"]),
    K(0x5C52, "MI_B_2", "ᴹᴵᴰᴵ\nB₂", "Midi send note B₂"),

    K(0x5C53, "MI_C_3", "ᴹᴵᴰᴵ\nC₃", "Midi send note C₃"),
    K(0x5C54, "MI_Cs_3", "ᴹᴵᴰᴵ\nC#₃/Dᵇ₃", "Midi send note C#₃/Dᵇ₃", alias=["MI_Db_3"]),
    K(0x5C55, "MI_D_3", "ᴹᴵᴰᴵ\nD₃", "Midi send note D₃"),
    K(0x5C56, "MI_Ds_3", "ᴹᴵᴰᴵ\nD#₃/Eᵇ₃", "Midi send note D#₃/Eᵇ₃", alias=["MI_Eb_3"]),
    K(0x5C57, "MI_E_3", "ᴹᴵᴰᴵ\nE₃", "Midi send note E₃"),
    K(0x5C58, "MI_F_3", "ᴹᴵᴰᴵ\nF₃", "Midi send note F₃"),
    K(0x5C59, "MI_Fs_3", "ᴹᴵᴰᴵ\nF#₃/Gᵇ₃", "Midi send note F#₃/Gᵇ₃", alias=["MI_Gb_3"]),
    K(0x5C5A, "MI_G_3", "ᴹᴵᴰᴵ\nG₃", "Midi send note G₃"),
    K(0x5C5B, "MI_Gs_3", "ᴹᴵᴰᴵ\nG#₃/Aᵇ₃", "Midi send note G#₃/Aᵇ₃", alias=["MI_Ab_3"]),
    K(0x5C5C, "MI_A_3", "ᴹᴵᴰᴵ\nA₃", "Midi send note A₃"),
    K(0x5C5D, "MI_As_3", "ᴹᴵᴰᴵ\nA#₃/Bᵇ₃", "Midi send note A#₃/Bᵇ₃", alias=["MI_Bb_3"]),
    K(0x5C5E, "MI_B_3", "ᴹᴵᴰᴵ\nB₃", "Midi send note B₃"),

    K(0x5C5F, "MI_C_4", "ᴹᴵᴰᴵ\nC₄", "Midi send note C₄"),
    K(0x5C60, "MI_Cs_4", "ᴹᴵᴰᴵ\nC#₄/Dᵇ₄", "Midi send note C#₄/Dᵇ₄", alias=["MI_Db_4"]),
    K(0x5C61, "MI_D_4", "ᴹᴵᴰᴵ\nD₄", "Midi send note D₄"),
    K(0x5C62, "MI_Ds_4", "ᴹᴵᴰᴵ\nD#₄/Eᵇ₄", "Midi send note D#₄/Eᵇ₄", alias=["MI_Eb_4"]),
    K(0x5C63, "MI_E_4", "ᴹᴵᴰᴵ\nE₄", "Midi send note E₄"),
    K(0x5C64, "MI_F_4", "ᴹᴵᴰᴵ\nF₄", "Midi send note F₄"),
    K(0x5C65, "MI_Fs_4", "ᴹᴵᴰᴵ\nF#₄/Gᵇ₄", "Midi send note F#₄/Gᵇ₄", alias=["MI_Gb_4"]),
    K(0x5C66, "MI_G_4", "ᴹᴵᴰᴵ\nG₄", "Midi send note G₄"),
    K(0x5C67, "MI_Gs_4", "ᴹᴵᴰᴵ\nG#₄/Aᵇ₄", "Midi send note G#₄/Aᵇ₄", alias=["MI_Ab_4"]),
    K(0x5C68, "MI_A_4", "ᴹᴵᴰᴵ\nA₄", "Midi send note A₄"),
    K(0x5C69, "MI_As_4", "ᴹᴵᴰᴵ\nA#₄/Bᵇ₄", "Midi send note A#₄/Bᵇ₄", alias=["MI_Bb_4"]),
    K(0x5C6A, "MI_B_4", "ᴹᴵᴰᴵ\nB₄", "Midi send note B₄"),

    K(0x5C6B, "MI_C_5", "ᴹᴵᴰᴵ\nC₅", "Midi send note C₅"),
    K(0x5C6C, "MI_Cs_5", "ᴹᴵᴰᴵ\nC#₅/Dᵇ₅", "Midi send note C#₅/Dᵇ₅", alias=["MI_Db_5"]),
    K(0x5C6D, "MI_D_5", "ᴹᴵᴰᴵ\nD₅", "Midi send note D₅"),
    K(0x5C6E, "MI_Ds_5", "ᴹᴵᴰᴵ\nD#₅/Eᵇ₅", "Midi send note D#₅/Eᵇ₅", alias=["MI_Eb_5"]),
    K(0x5C6F, "MI_E_5", "ᴹᴵᴰᴵ\nE₅", "Midi send note E₅"),
    K(0x5C70, "MI_F_5", "ᴹᴵᴰᴵ\nF₅", "Midi send note F₅"),
    K(0x5C71, "MI_Fs_5", "ᴹᴵᴰᴵ\nF#₅/Gᵇ₅", "Midi send note F#₅/Gᵇ₅", alias=["MI_Gb_5"]),
    K(0x5C72, "MI_G_5", "ᴹᴵᴰᴵ\nG₅", "Midi send note G₅"),
    K(0x5C73, "MI_Gs_5", "ᴹᴵᴰᴵ\nG#₅/Aᵇ₅", "Midi send note G#₅/Aᵇ₅", alias=["MI_Ab_5"]),
    K(0x5C74, "MI_A_5", "ᴹᴵᴰᴵ\nA₅", "Midi send note A₅"),
    K(0x5C75, "MI_As_5", "ᴹᴵᴰᴵ\nA#₅/Bᵇ₅", "Midi send note A#₅/Bᵇ₅", alias=["MI_Bb_5"]),
    K(0x5C76, "MI_B_5", "ᴹᴵᴰᴵ\nB₅", "Midi send note B₅"),

    K(0x5CB0, "MI_ALLOFF", "ᴹᴵᴰᴵ\nNotesᵒᶠᶠ", "Midi send all notes OFF"),
]

KEYCODES_MIDI_ADVANCED = [
    K(0x5C77, "MI_OCT_N2", "ᴹᴵᴰᴵ\nOct₋₂", "Midi set octave to -2"),
    K(0x5C78, "MI_OCT_N1", "ᴹᴵᴰᴵ\nOct₋₁", "Midi set octave to -1"),
    K(0x5C79, "MI_OCT_0", "ᴹᴵᴰᴵ\nOct₀", "Midi set octave to 0"),
    K(0x5C7A, "MI_OCT_1", "ᴹᴵᴰᴵ\nOct₊₁", "Midi set octave to 1"),
    K(0x5C7B, "MI_OCT_2", "ᴹᴵᴰᴵ\nOct₊₂", "Midi set octave to 2"),
    K(0x5C7C, "MI_OCT_3", "ᴹᴵᴰᴵ\nOct₊₃", "Midi set octave to 3"),
    K(0x5C7D, "MI_OCT_4", "ᴹᴵᴰᴵ\nOct₊₄", "Midi set octave to 4"),
    K(0x5C7E, "MI_OCT_5", "ᴹᴵᴰᴵ\nOct₊₅", "Midi set octave to 5"),
    K(0x5C7F, "MI_OCT_6", "ᴹᴵᴰᴵ\nOct₊₆", "Midi set octave to 6"),
    K(0x5C80, "MI_OCT_7", "ᴹᴵᴰᴵ\nOct₊₇", "Midi set octave to 7"),
    K(0x5C81, "MI_OCTD", "ᴹᴵᴰᴵ\nOctᴰᴺ", "Midi move down an octave"),
    K(0x5C82, "MI_OCTU", "ᴹᴵᴰᴵ\nOctᵁᴾ", "Midi move up an octave"),

    K(0x5C83, "MI_TRNS_N6", "ᴹᴵᴰᴵ\nTrans₋₆", "Midi set transposition to -4 semitones"),
    K(0x5C84, "MI_TRNS_N5", "ᴹᴵᴰᴵ\nTrans₋₅", "Midi set transposition to -5 semitones"),
    K(0x5C85, "MI_TRNS_N4", "ᴹᴵᴰᴵ\nTrans₋₄", "Midi set transposition to -4 semitones"),
    K(0x5C86, "MI_TRNS_N3", "ᴹᴵᴰᴵ\nTrans₋₃", "Midi set transposition to -3 semitones"),
    K(0x5C87, "MI_TRNS_N2", "ᴹᴵᴰᴵ\nTrans₋₂", "Midi set transposition to -2 semitones"),
    K(0x5C88, "MI_TRNS_N1", "ᴹᴵᴰᴵ\nTrans₋₁", "Midi set transposition to -1 semitones"),
    K(0x5C89, "MI_TRNS_0", "ᴹᴵᴰᴵ\nTrans₀", "Midi set no transposition"),
    K(0x5C8A, "MI_TRNS_1", "ᴹᴵᴰᴵ\nTrans₊₁", "Midi set transposition to +1 semitones"),
    K(0x5C8B, "MI_TRNS_2", "ᴹᴵᴰᴵ\nTrans₊₂", "Midi set transposition to +2 semitones"),
    K(0x5C8C, "MI_TRNS_3", "ᴹᴵᴰᴵ\nTrans₊₃", "Midi set transposition to +3 semitones"),
    K(0x5C8D, "MI_TRNS_4", "ᴹᴵᴰᴵ\nTrans₊₄", "Midi set transposition to +4 semitones"),
    K(0x5C8E, "MI_TRNS_5", "ᴹᴵᴰᴵ\nTrans₊₅", "Midi set transposition to +5 semitones"),
    K(0x5C8F, "MI_TRNS_6", "ᴹᴵᴰᴵ\nTrans₊₆", "Midi set transposition to +6 semitones"),
    K(0x5C90, "MI_TRNSD", "ᴹᴵᴰᴵ\nTransᴰᴺ", "Midi decrease transposition"),
    K(0x5C91, "MI_TRNSU", "ᴹᴵᴰᴵ\nTransᵁᴾ", "Midi increase transposition"),

    K(0x5C92, "MI_VEL_1", "ᴹᴵᴰᴵ\nVel₁", "Midi set velocity to 0", alias=["MI_VEL_0"]),
    K(0x5C93, "MI_VEL_2", "ᴹᴵᴰᴵ\nVel₂", "Midi set velocity to 25"),
    K(0x5C94, "MI_VEL_3", "ᴹᴵᴰᴵ\nVel₃", "Midi set velocity to 38"),
    K(0x5C95, "MI_VEL_4", "ᴹᴵᴰᴵ\nVel₄", "Midi set velocity to 51"),
    K(0x5C96, "MI_VEL_5", "ᴹᴵᴰᴵ\nVel₅", "Midi set velocity to 64"),
    K(0x5C97, "MI_VEL_6", "ᴹᴵᴰᴵ\nVel₆", "Midi set velocity to 76"),
    K(0x5C98, "MI_VEL_7", "ᴹᴵᴰᴵ\nVel₇", "Midi set velocity to 89"),
    K(0x5C99, "MI_VEL_8", "ᴹᴵᴰᴵ\nVel₈", "Midi set velocity to 102"),
    K(0x5C9A, "MI_VEL_9", "ᴹᴵᴰᴵ\nVel₉", "Midi set velocity to 114"),
    K(0x5C9B, "MI_VEL_10", "ᴹᴵᴰᴵ\nVel₁₀", "Midi set velocity to 127"),
    K(0x5C9C, "MI_VELD", "ᴹᴵᴰᴵ\nVelᴰᴺ", "Midi decrease velocity"),
    K(0x5C9D, "MI_VELU", "ᴹᴵᴰᴵ\nVelᵁᴾ", "Midi increase velocity"),

    K(0x5C9E, "MI_CH1", "ᴹᴵᴰᴵ\nCH₁", "Midi set channel to 1"),
    K(0x5C9F, "MI_CH2", "ᴹᴵᴰᴵ\nCH₂", "Midi set channel to 2"),
    K(0x5CA0, "MI_CH3", "ᴹᴵᴰᴵ\nCH₃", "Midi set channel to 3"),
    K(0x5CA1, "MI_CH4", "ᴹᴵᴰᴵ\nCH₄", "Midi set channel to 4"),
    K(0x5CA2, "MI_CH5", "ᴹᴵᴰᴵ\nCH₅", "Midi set channel to 5"),
    K(0x5CA3, "MI_CH6", "ᴹᴵᴰᴵ\nCH₆", "Midi set channel to 6"),
    K(0x5CA4, "MI_CH7", "ᴹᴵᴰᴵ\nCH₇", "Midi set channel to 7"),
    K(0x5CA5, "MI_CH8", "ᴹᴵᴰᴵ\nCH₈", "Midi set channel to 8"),
    K(0x5CA6, "MI_CH9", "ᴹᴵᴰᴵ\nCH₉", "Midi set channel to 9"),
    K(0x5CA7, "MI_CH10", "ᴹᴵᴰᴵ\nCH₁₀", "Midi set channel to 10"),
    K(0x5CA8, "MI_CH11", "ᴹᴵᴰᴵ\nCH₁₁", "Midi set channel to 11"),
    K(0x5CA9, "MI_CH12", "ᴹᴵᴰᴵ\nCH₁₂", "Midi set channel to 12"),
    K(0x5CAA, "MI_CH13", "ᴹᴵᴰᴵ\nCH₁₃", "Midi set channel to 13"),
    K(0x5CAB, "MI_CH14", "ᴹᴵᴰᴵ\nCH₁₄", "Midi set channel to 14"),
    K(0x5CAC, "MI_CH15", "ᴹᴵᴰᴵ\nCH₁₅", "Midi set channel to 15"),
    K(0x5CAD, "MI_CH16", "ᴹᴵᴰᴵ\nCH₁₆", "Midi set channel to 16"),
    K(0x5CAE, "MI_CHD", "ᴹᴵᴰᴵ\nCHᴰᴺ", "Midi decrease channel"),
    K(0x5CAF, "MI_CHU", "ᴹᴵᴰᴵ\nCHᵁᴾ", "Midi increase channel"),

    K(0x5CB1, "MI_SUS", "ᴹᴵᴰᴵ\nSust", "Midi Sustain"),
    K(0x5CB2, "MI_PORT", "ᴹᴵᴰᴵ\nPort", "Midi Portmento"),
    K(0x5CB3, "MI_SOST", "ᴹᴵᴰᴵ\nSost", "Midi Sostenuto"),
    K(0x5CB4, "MI_SOFT", "ᴹᴵᴰᴵ\nSPedal", "Midi Soft Pedal"),
    K(0x5CB5, "MI_LEG", "ᴹᴵᴰᴵ\nLegat", "Midi Legato"),
    K(0x5CB6, "MI_MOD", "ᴹᴵᴰᴵ\nModul", "Midi Modulation"),
    K(0x5CB7, "MI_MODSD", "ᴹᴵᴰᴵ\nModulᴰᴺ", "Midi decrease modulation speed"),
    K(0x5CB8, "MI_MODSU", "ᴹᴵᴰᴵ\nModulᵁᴾ", "Midi increase modulation speed"),
    K(0x5CB9, "MI_BENDD", "ᴹᴵᴰᴵ\nBendᴰᴺ", "Midi bend pitch down"),
    K(0x5CBA, "MI_BENDU", "ᴹᴵᴰᴵ\nBendᵁᴾ", "Midi bend pitch up"),
]

KEYCODES_HIDDEN = []
for x in range(256):
    from any_keycode import QK_TAP_DANCE

    KEYCODES_HIDDEN.append(K(QK_TAP_DANCE | x, "TD({})".format(x), "TD({})".format(x)))

KEYCODES = []

K = None


def recreate_keycodes():
    """ Regenerates global KEYCODES array """

    KEYCODES.clear()
    KEYCODES.extend(KEYCODES_SPECIAL + KEYCODES_BASIC + KEYCODES_SHIFTED + KEYCODES_ISO + KEYCODES_LAYERS +
                    KEYCODES_QUANTUM + KEYCODES_BACKLIGHT + KEYCODES_MEDIA + KEYCODES_TAP_DANCE + KEYCODES_MACRO +
                    KEYCODES_USER + KEYCODES_HIDDEN + KEYCODES_MIDI)


def create_user_keycodes():
    KEYCODES_USER.clear()
    for x in range(16):
        KEYCODES_USER.append(
            Keycode(
                0x5F80 + x,
                "USER{:02}".format(x),
                "User {}".format(x),
                "User keycode {}".format(x)
            )
        )


def create_custom_user_keycodes(custom_keycodes):
    KEYCODES_USER.clear()
    for x, c_keycode in enumerate(custom_keycodes):
        KEYCODES_USER.append(
            Keycode(
                0x5F80 + x,
                c_keycode.get("shortName", "USER{:02}".format(x)),
                c_keycode.get("name", "USER{:02}".format(x)),
                c_keycode.get("title", "USER{:02}".format(x))
            )
        )

def create_midi_keycodes(midiSettingLevel):
    KEYCODES_MIDI.clear()

    if midiSettingLevel == "basic" or midiSettingLevel == "advanced":
        KEYCODES_MIDI.extend(KEYCODES_MIDI_BASIC)

    if midiSettingLevel == "advanced":
        KEYCODES_MIDI.extend(KEYCODES_MIDI_ADVANCED)

def recreate_keyboard_keycodes(keyboard):
    """ Generates keycodes based on information the keyboard provides (e.g. layer keycodes, macros) """

    layers = keyboard.layers

    def generate_keycodes_for_mask(label, mask):
        keycodes = []
        for layer in range(layers):
            lbl = "{}({})".format(label, layer)
            keycodes.append(Keycode(mask | layer, lbl, lbl))
        return keycodes

    KEYCODES_LAYERS.clear()

    if layers >= 4:
        KEYCODES_LAYERS.append(Keycode(0x5F10, "FN_MO13", "Fn1\n(Fn3)"))
        KEYCODES_LAYERS.append(Keycode(0x5F11, "FN_MO23", "Fn2\n(Fn3)"))

    KEYCODES_LAYERS.extend(generate_keycodes_for_mask("MO", 0x5100))
    KEYCODES_LAYERS.extend(generate_keycodes_for_mask("DF", 0x5200))
    KEYCODES_LAYERS.extend(generate_keycodes_for_mask("TG", 0x5300))
    KEYCODES_LAYERS.extend(generate_keycodes_for_mask("TT", 0x5800))
    KEYCODES_LAYERS.extend(generate_keycodes_for_mask("OSL", 0x5400))
    KEYCODES_LAYERS.extend(generate_keycodes_for_mask("TO", 0x5000 | (1 << 4)))

    for x in range(layers):
        KEYCODES_LAYERS.append(Keycode(LT(x), "LT({}, kc)".format(x), "LT {}\n(kc)".format(x),
                                       "kc on tap, switch to layer {} while held".format(x), masked=True))

    KEYCODES_MACRO.clear()
    for x in range(keyboard.macro_count):
        lbl = "M{}".format(x)
        KEYCODES_MACRO.append(Keycode(0x5F12 + x, lbl, lbl))

    for x, kc in enumerate(KEYCODES_MACRO_BASE):
        KEYCODES_MACRO.append(kc)

    KEYCODES_TAP_DANCE.clear()
    for x in range(keyboard.tap_dance_count):
        lbl = "TD({})".format(x)
        KEYCODES_TAP_DANCE.append(Keycode(QK_TAP_DANCE | x, lbl, lbl))

    # Check if custom keycodes are defined in keyboard, and if so add them to user keycodes
    if keyboard.custom_keycodes is not None and len(keyboard.custom_keycodes) > 0:
        create_custom_user_keycodes(keyboard.custom_keycodes)
    else:
        create_user_keycodes()

    create_midi_keycodes(keyboard.midi)

    recreate_keycodes()


recreate_keycodes()
