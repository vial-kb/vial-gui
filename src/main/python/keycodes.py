# coding: utf-8

# SPDX-License-Identifier: GPL-2.0-or-later

class Keycode:

    def __init__(self, code, qmk_id, label, tooltip=None):
        self.code = code
        self.qmk_id = qmk_id
        self.label = label
        self.tooltip = tooltip


K = Keycode

KEYCODES_BASIC = [
    K(0x00, "KC_NO", ""),
    K(0x01, "KC_TRNS", "▽"),
    K(0x04, "KC_A", "A"),
    K(0x05, "KC_B", "B"),
    K(0x06, "KC_C", "C"),
    K(0x07, "KC_D", "D"),
    K(0x08, "KC_E", "E"),
    K(0x09, "KC_F", "F"),
    K(0x0A, "KC_G", "G"),
    K(0x0B, "KC_H", "H"),
    K(0x0C, "KC_I", "I"),
    K(0x0D, "KC_J", "J"),
    K(0x0E, "KC_K", "K"),
    K(0x0F, "KC_L", "L"),
    K(0x10, "KC_M", "M"),
    K(0x11, "KC_N", "N"),
    K(0x12, "KC_O", "O"),
    K(0x13, "KC_P", "P"),
    K(0x14, "KC_Q", "Q"),
    K(0x15, "KC_R", "R"),
    K(0x16, "KC_S", "S"),
    K(0x17, "KC_T", "T"),
    K(0x18, "KC_U", "U"),
    K(0x19, "KC_V", "V"),
    K(0x1A, "KC_W", "W"),
    K(0x1B, "KC_X", "X"),
    K(0x1C, "KC_Y", "Y"),
    K(0x1D, "KC_Z", "Z"),
    K(0x1E, "KC_1", "!\n1"),
    K(0x1F, "KC_2", "@\n2"),
    K(0x20, "KC_3", "#\n3"),
    K(0x21, "KC_4", "$\n4"),
    K(0x22, "KC_5", "%\n5"),
    K(0x23, "KC_6", "^\n6"),
    K(0x24, "KC_7", "&\n7"),
    K(0x25, "KC_8", "*\n8"),
    K(0x26, "KC_9", "(\n9"),
    K(0x27, "KC_0", ")\n0"),
    K(0x28, "KC_ENTER", "Enter"),
    K(0x29, "KC_ESCAPE", "Esc"),
    K(0x2A, "KC_BSPACE", "Bksp"),
    K(0x2B, "KC_TAB", "Tab"),
    K(0x2C, "KC_SPACE", "Space"),
    K(0x2D, "KC_MINUS", "_\n-"),
    K(0x2E, "KC_EQUAL", "+\n="),
    K(0x2F, "KC_LBRACKET", "{\n["),
    K(0x30, "KC_RBRACKET", "}\n]"),
    K(0x31, "KC_BSLASH", "|\n\\"),
    K(0x33, "KC_SCOLON", ":\n;"),
    K(0x34, "KC_QUOTE", "\"\n'"),
    K(0x35, "KC_GRAVE", "~\n`"),
    K(0x36, "KC_COMMA", "<\n,"),
    K(0x37, "KC_DOT", ">\n."),
    K(0x38, "KC_SLASH", "?\n/"),
    K(0x39, "KC_CAPSLOCK", "Caps\nLock"),
    K(0x3A, "KC_F1", "F1"),
    K(0x3B, "KC_F2", "F2"),
    K(0x3C, "KC_F3", "F3"),
    K(0x3D, "KC_F4", "F4"),
    K(0x3E, "KC_F5", "F5"),
    K(0x3F, "KC_F6", "F6"),
    K(0x40, "KC_F7", "F7"),
    K(0x41, "KC_F8", "F8"),
    K(0x42, "KC_F9", "F9"),
    K(0x43, "KC_F10", "F10"),
    K(0x44, "KC_F11", "F11"),
    K(0x45, "KC_F12", "F12"),
    K(0x46, "KC_PSCREEN", "Print\nScreen"),
    K(0x47, "KC_SCROLLLOCK", "Scroll\nLock"),
    K(0x48, "KC_PAUSE", "Pause"),
    K(0x49, "KC_INSERT", "Insert"),
    K(0x4A, "KC_HOME", "Home"),
    K(0x4B, "KC_PGUP", "Page\nUp"),
    K(0x4C, "KC_DELETE", "Del"),
    K(0x4D, "KC_END", "End"),
    K(0x4E, "KC_PGDOWN", "Page\nDown"),
    K(0x4F, "KC_RIGHT", "Right"),
    K(0x50, "KC_LEFT", "Left"),
    K(0x51, "KC_DOWN", "Down"),
    K(0x52, "KC_UP", "Up"),
    K(0x53, "KC_NUMLOCK", "Num\nLock"),
    K(0x54, "KC_KP_SLASH", "/"),
    K(0x55, "KC_KP_ASTERISK", "*"),
    K(0x56, "KC_KP_MINUS", "-"),
    K(0x57, "KC_KP_PLUS", "+"),
    K(0x58, "KC_KP_ENTER", "Num\nEnter"),
    K(0x59, "KC_KP_1", "1"),
    K(0x5A, "KC_KP_2", "2"),
    K(0x5B, "KC_KP_3", "3"),
    K(0x5C, "KC_KP_4", "4"),
    K(0x5D, "KC_KP_5", "5"),
    K(0x5E, "KC_KP_6", "6"),
    K(0x5F, "KC_KP_7", "7"),
    K(0x60, "KC_KP_8", "8"),
    K(0x61, "KC_KP_9", "9"),
    K(0x62, "KC_KP_0", "0"),
    K(0x63, "KC_KP_DOT", "."),
    K(0x65, "KC_APPLICATION", "Menu"),
    # KC_POWER,
    K(0x67, "KC_KP_EQUAL", "="),
    # KC_F13,
    # KC_F14,
    # KC_F15,
    # KC_F16,
    # KC_F17,
    # KC_F18,
    # KC_F19,
    # KC_F20,
    # KC_F21,  // 0x70
    # KC_F22,
    # KC_F23,
    # KC_F24,
    # KC_EXECUTE,
    # KC_HELP,
    # KC_MENU,
    # KC_SELECT,
    # KC_STOP,
    # KC_AGAIN,
    # KC_UNDO,
    # KC_CUT,
    # KC_COPY,
    # KC_PASTE,
    # KC_FIND,
    # KC__MUTE,
    # KC__VOLUP,  // 0x80
    # KC__VOLDOWN,
    # KC_LOCKING_CAPS,
    # KC_LOCKING_NUM,
    # KC_LOCKING_SCROLL,
    K(0x85, "KC_KP_COMMA", ","),
    # KC_KP_EQUAL_AS400,
    # KC_INT1,
    # KC_INT2,
    # KC_INT3,
    # KC_INT4,
    # KC_INT5,
    # KC_INT6,
    # KC_INT7,
    # KC_INT8,
    # KC_INT9,
    # KC_LANG1,  // 0x90
    # KC_LANG2,
    # KC_LANG3,
    # KC_LANG4,
    # KC_LANG5,
    # KC_LANG6,
    # KC_LANG7,
    # KC_LANG8,
    # KC_LANG9,
    # KC_ALT_ERASE,
    # KC_SYSREQ,
    # KC_CANCEL,
    # KC_CLEAR,
    # KC_PRIOR,
    # KC_RETURN,
    # KC_SEPARATOR,
    # KC_OUT,  // 0xA0
    # KC_OPER,
    # KC_CLEAR_AGAIN,
    # KC_CRSEL,
    # KC_EXSEL,

    K(0xE0, "KC_LCTRL", "LCtrl"),
    K(0xE1, "KC_LSHIFT", "LShift"),
    K(0xE2, "KC_LALT", "LAlt"),
    K(0xE3, "KC_LGUI", "LGui"),
    K(0xE4, "KC_RCTRL", "RCtrl"),
    K(0xE5, "KC_RSHIFT", "RShift"),
    K(0xE6, "KC_RALT", "RAlt"),
    K(0xE7, "KC_RGUI", "RGui"),

    K(0x235, "KC_TILD", "~"),
    K(0x21E, "KC_EXLM", "!"),
    K(0x21F, "KC_AT", "@"),
    K(0x220, "KC_HASH", "#"),
    K(0x221, "KC_DLR", "$"),
    K(0x222, "KC_PERC", "%"),
    K(0x223, "KC_CIRC", "^"),
    K(0x224, "KC_AMPR", "&&"),
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
    K(0x32, "KC_NONUS_HASH", "~\n#", "Non-US # and ~"),
    K(0x64, "KC_NONUS_BSLASH", "|\n\\", "Non-US \\ and |"),
    K(0x87, "KC_RO", "_\n\\", "JIS \\ and _"),
    K(0x88, "KC_KANA", "カタカナ\nひらがな", "JIS Katakana/Hiragana"),
    K(0x89, "KC_JYEN", "|\n¥"),
    K(0x8A, "KC_HENK", "変換", "JIS Henkan"),
    K(0x8B, "KC_MHEN", "無変換", "JIS Muhenkan"),
    K(0x90, "KC_LANG1", "한영\nかな", "Korean Han/Yeong / JP Mac Kana"),
    K(0x91, "KC_LANG2", "漢字\n英数", "Korean Hanja / JP Mac Eisu"),
]

KEYCODES_LAYERS = []

QK_ONE_SHOT_MOD = 0x5500
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

KEYCODES_QUANTUM = [
    K(0x5C00, "RESET", "Reset", "Reboot to bootloader"),
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

    K(0x5C16, "KC_GESC", "Esc\n~", "Esc normally, but ~ when Shift or GUI is pressed"),
    K(0x5CD7, "KC_LSPO", "LS\n(", "Left Shift when held, ( when tapped"),
    K(0x5CD8, "KC_RSPC", "RS\n)", "Right Shift when held, ) when tapped"),
    K(0x5CF3, "KC_LCPO", "LC\n(", "Left Control when held, ( when tapped"),
    K(0x5CF4, "KC_RCPC", "RC\n)", "Right Control when held, ) when tapped"),
    K(0x5CF5, "KC_LAPO", "LA\n(", "Left Alt when held, ( when tapped"),
    K(0x5CF6, "KC_RAPC", "RA\n)", "Right Alt when held, ) when tapped"),
    K(0x5CD9, "KC_SFTENT", "RS\nEnter", "Right Shift when held, Enter when tapped"),
]

KEYCODES_BACKLIGHT = [

]

KEYCODES_MEDIA = [

]

KEYCODES_MACRO = []

KEYCODES = []

K = None


def find_keycode(code):
    for keycode in KEYCODES:
        if keycode.code == code:
            return keycode
    return None


def keycode_label(code):
    keycode = find_keycode(code)
    if keycode is None:
        return "0x{:X}".format(code)
    return keycode.label


def keycode_tooltip(code):
    keycode = find_keycode(code)
    if keycode is None:
        return None
    tooltip = keycode.qmk_id
    if keycode.tooltip:
        tooltip = "{}: {}".format(tooltip, keycode.tooltip)
    return tooltip


def recreate_keycodes():
    """ Regenerates global KEYCODES array """

    KEYCODES.clear()
    KEYCODES.extend(KEYCODES_BASIC + KEYCODES_ISO + KEYCODES_LAYERS + KEYCODES_QUANTUM + KEYCODES_BACKLIGHT +
                    KEYCODES_MEDIA + KEYCODES_MACRO)


def recreate_layer_keycodes(layers):
    """ Generates layer keycodes based on number of layers a keyboard provides """

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
    KEYCODES_LAYERS.extend(generate_keycodes_for_mask("TG", 0x5300))
    KEYCODES_LAYERS.extend(generate_keycodes_for_mask("TT", 0x5800))
    KEYCODES_LAYERS.extend(generate_keycodes_for_mask("OSL", 0x5400))
    KEYCODES_LAYERS.extend(generate_keycodes_for_mask("TO", 0x5000 | (1 << 4)))

    recreate_keycodes()

recreate_keycodes()
