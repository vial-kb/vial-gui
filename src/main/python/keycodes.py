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

    K(QK_LCTL|QK_LSFT|QK_LALT|QK_LGUI, "HYPR(kc)", "Hyper\n(kc)", "LCTL + LSFT + LALT + LGUI", masked=True),
    K(QK_LCTL|QK_LSFT|QK_LALT, "MEH(kc)", "Meh\n(kc)", "LCTL + LSFT + LALT", masked=True),
    K(QK_LCTL|QK_LALT|QK_LGUI, "LCAG(kc)", "LCAG\n(kc)", "LCTL + LALT + LGUI", masked=True),
    K(QK_LGUI|QK_LSFT, "SGUI(kc)", "SGUI\n(kc)", "LGUI + LSFT", masked=True),
    K(QK_LCTL|QK_LALT, "LCA(kc)", "LCA\n(kc)", "LCTL + LALT", masked=True),
    K(QK_LSFT|QK_LALT, "LSA(kc)", "LSA\n(kc)", "LSFT + LALT", masked=True),
    K(QK_LCTL|QK_LSFT, "C_S(kc)", "C_S\n(kc)", "LCTL + LSFT", masked=True),

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

KEYCODES_USER = []

KEYCODES_MACRO = []

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
                    KEYCODES_QUANTUM + KEYCODES_BACKLIGHT + KEYCODES_MEDIA + KEYCODES_MACRO + KEYCODES_USER +
                    KEYCODES_HIDDEN)


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

    # Check if custom keycodes are defined in keyboard, and if so add them to user keycodes
    if keyboard.custom_keycodes is not None and len(keyboard.custom_keycodes) > 0:
        create_custom_user_keycodes(keyboard.custom_keycodes)
    else:
        create_user_keycodes()

    recreate_keycodes()


recreate_keycodes()
