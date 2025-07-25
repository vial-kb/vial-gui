class keycodes_v5:
    kc = {
        "QK_LAYER_TAP": 0x4000,
        "MOD_LCTL": 0x01,
        "MOD_LSFT": 0x02,
        "MOD_LALT": 0x04,
        "MOD_LGUI": 0x08,
        "MOD_RCTL": 0x11,
        "MOD_RSFT": 0x12,
        "MOD_RALT": 0x14,
        "MOD_RGUI": 0x18,
        "MOD_HYPR": 0xF,
        "MOD_MEH": 0x7,
        "QK_TO": 0x5000,
        "QK_MOMENTARY": 0x5100,
        "QK_DEF_LAYER": 0x5200,
        "QK_TOGGLE_LAYER": 0x5300,
        "QK_ONE_SHOT_LAYER": 0x5400,
        "QK_ONE_SHOT_MOD": 0x5500,
        "QK_TAP_DANCE": 0x5700,
        "QK_LAYER_TAP_TOGGLE": 0x5800,
        "QK_LAYER_MOD": 0x5900,
        "QK_MOD_TAP": 0x6000,
        "ON_PRESS": 1,
        "QK_LCTL": 0x0100,
        "QK_LSFT": 0x0200,
        "QK_LALT": 0x0400,
        "QK_LGUI": 0x0800,
        "QK_RCTL": 0x1100,
        "QK_RSFT": 0x1200,
        "QK_RALT": 0x1400,
        "QK_RGUI": 0x1800,

        "ALL_T(kc)": 0x6f00,
        "C_S_T(kc)": 0x6300,
        "C_S(kc)": 0x300,
        "HYPR(kc)": 0xf00,
        "LALT_T(kc)": 0x6400,
        "LALT(kc)": 0x400,
        "LCA_T(kc)": 0x6500,
        "LCA(kc)": 0x500,
        "LCAG_T(kc)": 0x6d00,
        "LCAG(kc)": 0xd00,
        "LCG_T(kc)": 0x6900,
        "LCG(kc)": 0x900,
        "LCTL_T(kc)": 0x6100,
        "LCTL(kc)": 0x100,
        "LGUI_T(kc)": 0x6800,
        "LGUI(kc)": 0x800,
        "LSA_T(kc)": 0x6600,
        "LSA(kc)": 0x600,
        "LSFT_T(kc)": 0x6200,
        "LSFT(kc)": 0x200,
        "MEH_T(kc)": 0x6700,
        "MEH(kc)": 0x700,
        "RALT_T(kc)": 0x7400,
        "RALT(kc)": 0x1400,
        "RCAG_T(kc)": 0x7d00,
        "RCG_T(kc)": 0x7900,
        "RCG(kc)": 0x1900,
        "RCTL_T(kc)": 0x7100,
        "RCTL(kc)": 0x1100,
        "RGUI_T(kc)": 0x7800,
        "RGUI(kc)": 0x1800,
        "RSFT_T(kc)": 0x7200,
        "RSFT(kc)": 0x1200,
        "SGUI_T(kc)": 0x6a00,
        "SGUI(kc)": 0xa00,

        "OSM(MOD_LSFT)": 0x5502,
        "OSM(MOD_LCTL)": 0x5501,
        "OSM(MOD_LALT)": 0x5504,
        "OSM(MOD_LGUI)": 0x5508,
        "OSM(MOD_RSFT)": 0x5512,
        "OSM(MOD_RCTL)": 0x5511,
        "OSM(MOD_RALT)": 0x5514,
        "OSM(MOD_RGUI)": 0x5518,
        "OSM(MOD_LCTL|MOD_LSFT)": 0x5503,
        "OSM(MOD_LCTL|MOD_LALT)": 0x5505,
        "OSM(MOD_LCTL|MOD_LGUI)": 0x5509,
        "OSM(MOD_LSFT|MOD_LALT)": 0x5506,
        "OSM(MOD_LSFT|MOD_LGUI)": 0x550A,
        "OSM(MOD_LALT|MOD_LGUI)": 0x550C,
        "OSM(MOD_LCTL|MOD_LSFT|MOD_LGUI)": 0x550B,
        "OSM(MOD_LCTL|MOD_LALT|MOD_LGUI)": 0x550D,
        "OSM(MOD_LSFT|MOD_LALT|MOD_LGUI)": 0x550E,
        "OSM(MOD_RCTL|MOD_RSFT)": 0x5513,
        "OSM(MOD_RCTL|MOD_RALT)": 0x5515,
        "OSM(MOD_RCTL|MOD_RGUI)": 0x5519,
        "OSM(MOD_RSFT|MOD_RALT)": 0x5516,
        "OSM(MOD_RSFT|MOD_RGUI)": 0x551A,
        "OSM(MOD_RALT|MOD_RGUI)": 0x551C,
        "OSM(MOD_RCTL|MOD_RSFT|MOD_RGUI)": 0x551B,
        "OSM(MOD_RCTL|MOD_RALT|MOD_RGUI)": 0x551D,
        "OSM(MOD_RSFT|MOD_RALT|MOD_RGUI)": 0x551E,
        "OSM(MOD_MEH)": 0x5507,
        "OSM(MOD_HYPR)": 0x550F,
        "OSM(MOD_RCTL|MOD_RSFT|MOD_RALT)": 0x5517,
        "OSM(MOD_RCTL|MOD_RSFT|MOD_RALT|MOD_RGUI)": 0x551F,

        "KC_NO": 0x00,
        "KC_TRNS": 0x01,
        "KC_NUMLOCK": 0x53,
        "KC_KP_SLASH": 0x54,
        "KC_KP_ASTERISK": 0x55,
        "KC_KP_MINUS": 0x56,
        "KC_KP_PLUS": 0x57,
        "KC_KP_ENTER": 0x58,
        "KC_KP_1": 0x59,
        "KC_KP_2": 0x5A,
        "KC_KP_3": 0x5B,
        "KC_KP_4": 0x5C,
        "KC_KP_5": 0x5D,
        "KC_KP_6": 0x5E,
        "KC_KP_7": 0x5F,
        "KC_KP_8": 0x60,
        "KC_KP_9": 0x61,
        "KC_KP_0": 0x62,
        "KC_KP_DOT": 0x63,
        "KC_KP_EQUAL": 0x67,
        "KC_KP_COMMA": 0x85,
        "KC_PSCREEN": 0x46,
        "KC_SCROLLLOCK": 0x47,
        "KC_PAUSE": 0x48,
        "KC_INSERT": 0x49,
        "KC_HOME": 0x4A,
        "KC_PGUP": 0x4B,
        "KC_DELETE": 0x4C,
        "KC_END": 0x4D,
        "KC_PGDOWN": 0x4E,
        "KC_RIGHT": 0x4F,
        "KC_LEFT": 0x50,
        "KC_DOWN": 0x51,
        "KC_UP": 0x52,
        "KC_A": 0x04,
        "KC_B": 0x05,
        "KC_C": 0x06,
        "KC_D": 0x07,
        "KC_E": 0x08,
        "KC_F": 0x09,
        "KC_G": 0x0A,
        "KC_H": 0x0B,
        "KC_I": 0x0C,
        "KC_J": 0x0D,
        "KC_K": 0x0E,
        "KC_L": 0x0F,
        "KC_M": 0x10,
        "KC_N": 0x11,
        "KC_O": 0x12,
        "KC_P": 0x13,
        "KC_Q": 0x14,
        "KC_R": 0x15,
        "KC_S": 0x16,
        "KC_T": 0x17,
        "KC_U": 0x18,
        "KC_V": 0x19,
        "KC_W": 0x1A,
        "KC_X": 0x1B,
        "KC_Y": 0x1C,
        "KC_Z": 0x1D,
        "KC_1": 0x1E,
        "KC_2": 0x1F,
        "KC_3": 0x20,
        "KC_4": 0x21,
        "KC_5": 0x22,
        "KC_6": 0x23,
        "KC_7": 0x24,
        "KC_8": 0x25,
        "KC_9": 0x26,
        "KC_0": 0x27,
        "KC_ENTER": 0x28,
        "KC_ESCAPE": 0x29,
        "KC_BSPACE": 0x2A,
        "KC_TAB": 0x2B,
        "KC_SPACE": 0x2C,
        "KC_MINUS": 0x2D,
        "KC_EQUAL": 0x2E,
        "KC_LBRACKET": 0x2F,
        "KC_RBRACKET": 0x30,
        "KC_BSLASH": 0x31,
        "KC_SCOLON": 0x33,
        "KC_QUOTE": 0x34,
        "KC_GRAVE": 0x35,
        "KC_COMMA": 0x36,
        "KC_DOT": 0x37,
        "KC_SLASH": 0x38,
        "KC_CAPSLOCK": 0x39,
        "KC_F1": 0x3A,
        "KC_F2": 0x3B,
        "KC_F3": 0x3C,
        "KC_F4": 0x3D,
        "KC_F5": 0x3E,
        "KC_F6": 0x3F,
        "KC_F7": 0x40,
        "KC_F8": 0x41,
        "KC_F9": 0x42,
        "KC_F10": 0x43,
        "KC_F11": 0x44,
        "KC_F12": 0x45,
        "KC_APPLICATION": 0x65,
        "KC_LCTRL": 0xE0,
        "KC_LSHIFT": 0xE1,
        "KC_LALT": 0xE2,
        "KC_LGUI": 0xE3,
        "KC_RCTRL": 0xE4,
        "KC_RSHIFT": 0xE5,
        "KC_RALT": 0xE6,
        "KC_RGUI": 0xE7,
        "KC_TILD": 0x235,
        "KC_EXLM": 0x21E,
        "KC_AT": 0x21F,
        "KC_HASH": 0x220,
        "KC_DLR": 0x221,
        "KC_PERC": 0x222,
        "KC_CIRC": 0x223,
        "KC_AMPR": 0x224,
        "KC_ASTR": 0x225,
        "KC_LPRN": 0x226,
        "KC_RPRN": 0x227,
        "KC_UNDS": 0x22D,
        "KC_PLUS": 0x22E,
        "KC_LCBR": 0x22F,
        "KC_RCBR": 0x230,
        "KC_LT": 0x236,
        "KC_GT": 0x237,
        "KC_COLN": 0x233,
        "KC_PIPE": 0x231,
        "KC_QUES": 0x238,
        "KC_DQUO": 0x234,
        "KC_NONUS_HASH": 0x32,
        "KC_NONUS_BSLASH": 0x64,
        "KC_RO": 0x87,
        "KC_KANA": 0x88,
        "KC_JYEN": 0x89,
        "KC_HENK": 0x8A,
        "KC_MHEN": 0x8B,
        "KC_LANG1": 0x90,
        "KC_LANG2": 0x91,
        "KC_GESC": 0x5C16,
        "KC_LSPO": 0x5CD7,
        "KC_RSPC": 0x5CD8,
        "KC_LCPO": 0x5CF3,
        "KC_RCPC": 0x5CF4,
        "KC_LAPO": 0x5CF5,
        "KC_RAPC": 0x5CF6,
        "KC_SFTENT": 0x5CD9,
        "MAGIC_SWAP_CONTROL_CAPSLOCK": 23554,
        "MAGIC_UNSWAP_CONTROL_CAPSLOCK": 23563,
        "MAGIC_CAPSLOCK_TO_CONTROL": 23555,
        "MAGIC_UNCAPSLOCK_TO_CONTROL": 23564,
        "MAGIC_SWAP_LCTL_LGUI": 23802,
        "MAGIC_UNSWAP_LCTL_LGUI": 23804,
        "MAGIC_SWAP_RCTL_RGUI": 23803,
        "MAGIC_UNSWAP_RCTL_RGUI": 23805,
        "MAGIC_SWAP_CTL_GUI": 23806,
        "MAGIC_UNSWAP_CTL_GUI": 23807,
        "MAGIC_TOGGLE_CTL_GUI": 23808,
        "MAGIC_SWAP_LALT_LGUI": 23556,
        "MAGIC_UNSWAP_LALT_LGUI": 23565,
        "MAGIC_SWAP_RALT_RGUI": 23557,
        "MAGIC_UNSWAP_RALT_RGUI": 23566,
        "MAGIC_SWAP_ALT_GUI": 23562,
        "MAGIC_UNSWAP_ALT_GUI": 23571,
        "MAGIC_TOGGLE_ALT_GUI": 23573,
        "MAGIC_NO_GUI": 23558,
        "MAGIC_UNNO_GUI": 23567,
        "MAGIC_SWAP_GRAVE_ESC": 23559,
        "MAGIC_UNSWAP_GRAVE_ESC": 23568,
        "MAGIC_SWAP_BACKSLASH_BACKSPACE": 23560,
        "MAGIC_UNSWAP_BACKSLASH_BACKSPACE": 23569,
        "MAGIC_HOST_NKRO": 23561,
        "MAGIC_UNHOST_NKRO": 23570,
        "MAGIC_TOGGLE_NKRO": 23572,
        "MAGIC_EE_HANDS_LEFT": 23809,
        "MAGIC_EE_HANDS_RIGHT": 23810,
        "AU_ON": 0x5C1D,
        "AU_OFF": 0x5C1E,
        "AU_TOG": 0x5C1F,
        "CLICKY_TOGGLE": 0x5C20,
        "CLICKY_UP": 0x5C23,
        "CLICKY_DOWN": 0x5C24,
        "CLICKY_RESET": 0x5C25,
        "MU_ON": 0x5C26,
        "MU_OFF": 0x5C27,
        "MU_TOG": 0x5C28,
        "MU_MOD": 0x5C29,
        "HPT_ON": 0x5CE6,
        "HPT_OFF": 0x5CE7,
        "HPT_TOG": 0x5CE8,
        "HPT_RST": 0x5CE9,
        "HPT_FBK": 0x5CEA,
        "HPT_BUZ": 0x5CEB,
        "HPT_MODI": 0x5CEC,
        "HPT_MODD": 0x5CED,
        "HPT_CONT": 0x5CEE,
        "HPT_CONI": 0x5CEF,
        "HPT_COND": 0x5CF0,
        "HPT_DWLI": 0x5CF1,
        "HPT_DWLD": 0x5CF2,
        "KC_ASDN": 0x5C18,
        "KC_ASUP": 0x5C17,
        "KC_ASRP": 0x5C19,
        "KC_ASON": 0x5C1B,
        "KC_ASOFF": 0x5C1C,
        "KC_ASTG": 0x5C1A,
        "CMB_ON": 0x5CF7,
        "CMB_OFF": 0x5CF8,
        "CMB_TOG": 0x5CF9,
        "BL_TOGG": 23743,
        "BL_STEP": 23744,
        "BL_BRTG": 23745,
        "BL_ON": 23739,
        "BL_OFF": 23740,
        "BL_INC": 23742,
        "BL_DEC": 23741,
        "RGB_TOG": 23746,
        "RGB_MOD": 23747,
        "RGB_RMOD": 23748,
        "RGB_HUI": 23749,
        "RGB_HUD": 23750,
        "RGB_SAI": 23751,
        "RGB_SAD": 23752,
        "RGB_VAI": 23753,
        "RGB_VAD": 23754,
        "RGB_SPI": 23755,
        "RGB_SPD": 23756,
        "RGB_M_P": 23757,
        "RGB_M_B": 23758,
        "RGB_M_R": 23759,
        "RGB_M_SW": 23760,
        "RGB_M_SN": 23761,
        "RGB_M_K": 23762,
        "RGB_M_X": 23763,
        "RGB_M_G": 23764,
        "RGB_M_T": 23765,
        "KC_F13": 104,
        "KC_F14": 105,
        "KC_F15": 106,
        "KC_F16": 107,
        "KC_F17": 108,
        "KC_F18": 109,
        "KC_F19": 110,
        "KC_F20": 111,
        "KC_F21": 112,
        "KC_F22": 113,
        "KC_F23": 114,
        "KC_F24": 115,
        "KC_PWR": 165,
        "KC_SLEP": 166,
        "KC_WAKE": 167,
        "KC_EXEC": 116,
        "KC_HELP": 117,
        "KC_SLCT": 119,
        "KC_STOP": 120,
        "KC_AGIN": 121,
        "KC_UNDO": 122,
        "KC_CUT": 123,
        "KC_COPY": 124,
        "KC_PSTE": 125,
        "KC_FIND": 126,
        "KC_CALC": 178,
        "KC_MAIL": 177,
        "KC_MSEL": 175,
        "KC_MYCM": 179,
        "KC_WSCH": 180,
        "KC_WHOM": 181,
        "KC_WBAK": 182,
        "KC_WFWD": 183,
        "KC_WSTP": 184,
        "KC_WREF": 185,
        "KC_WFAV": 186,
        "KC_BRIU": 189,
        "KC_BRID": 190,
        "KC_MPRV": 172,
        "KC_MNXT": 171,
        "KC_MUTE": 168,
        "KC_VOLD": 170,
        "KC_VOLU": 169,
        "KC__VOLDOWN": 129,
        "KC__VOLUP": 128,
        "KC_MSTP": 173,
        "KC_MPLY": 174,
        "KC_MRWD": 188,
        "KC_MFFD": 187,
        "KC_EJCT": 176,
        "KC_MS_U": 240,
        "KC_MS_D": 241,
        "KC_MS_L": 242,
        "KC_MS_R": 243,
        "KC_BTN1": 244,
        "KC_BTN2": 245,
        "KC_BTN3": 246,
        "KC_BTN4": 247,
        "KC_BTN5": 248,
        "KC_WH_U": 249,
        "KC_WH_D": 250,
        "KC_WH_L": 251,
        "KC_WH_R": 252,
        "KC_ACL0": 253,
        "KC_ACL1": 254,
        "KC_ACL2": 255,
        "KC_LCAP": 130,
        "KC_LNUM": 131,
        "KC_LSCR": 132,
        "DYN_REC_START1": 0x5D03,
        "DYN_REC_START2": 0x5D04,
        "DYN_REC_STOP": 0x5D05,
        "DYN_MACRO_PLAY1": 0x5D06,
        "DYN_MACRO_PLAY2": 0x5D07,
        "MI_C": 0x5C2F,
        "MI_Cs": 0x5C30,
        "MI_D": 0x5C31,
        "MI_Ds": 0x5C32,
        "MI_E": 0x5C33,
        "MI_F": 0x5C34,
        "MI_Fs": 0x5C35,
        "MI_G": 0x5C36,
        "MI_Gs": 0x5C37,
        "MI_A": 0x5C38,
        "MI_As": 0x5C39,
        "MI_B": 0x5C3A,
        "MI_C_1": 0x5C3B,
        "MI_Cs_1": 0x5C3C,
        "MI_D_1": 0x5C3D,
        "MI_Ds_1": 0x5C3E,
        "MI_E_1": 0x5C3F,
        "MI_F_1": 0x5C40,
        "MI_Fs_1": 0x5C41,
        "MI_G_1": 0x5C42,
        "MI_Gs_1": 0x5C43,
        "MI_A_1": 0x5C44,
        "MI_As_1": 0x5C45,
        "MI_B_1": 0x5C46,
        "MI_C_2": 0x5C47,
        "MI_Cs_2": 0x5C48,
        "MI_D_2": 0x5C49,
        "MI_Ds_2": 0x5C4A,
        "MI_E_2": 0x5C4B,
        "MI_F_2": 0x5C4C,
        "MI_Fs_2": 0x5C4D,
        "MI_G_2": 0x5C4E,
        "MI_Gs_2": 0x5C4F,
        "MI_A_2": 0x5C50,
        "MI_As_2": 0x5C51,
        "MI_B_2": 0x5C52,
        "MI_C_3": 0x5C53,
        "MI_Cs_3": 0x5C54,
        "MI_D_3": 0x5C55,
        "MI_Ds_3": 0x5C56,
        "MI_E_3": 0x5C57,
        "MI_F_3": 0x5C58,
        "MI_Fs_3": 0x5C59,
        "MI_G_3": 0x5C5A,
        "MI_Gs_3": 0x5C5B,
        "MI_A_3": 0x5C5C,
        "MI_As_3": 0x5C5D,
        "MI_B_3": 0x5C5E,
        "MI_C_4": 0x5C5F,
        "MI_Cs_4": 0x5C60,
        "MI_D_4": 0x5C61,
        "MI_Ds_4": 0x5C62,
        "MI_E_4": 0x5C63,
        "MI_F_4": 0x5C64,
        "MI_Fs_4": 0x5C65,
        "MI_G_4": 0x5C66,
        "MI_Gs_4": 0x5C67,
        "MI_A_4": 0x5C68,
        "MI_As_4": 0x5C69,
        "MI_B_4": 0x5C6A,
        "MI_C_5": 0x5C6B,
        "MI_Cs_5": 0x5C6C,
        "MI_D_5": 0x5C6D,
        "MI_Ds_5": 0x5C6E,
        "MI_E_5": 0x5C6F,
        "MI_F_5": 0x5C70,
        "MI_Fs_5": 0x5C71,
        "MI_G_5": 0x5C72,
        "MI_Gs_5": 0x5C73,
        "MI_A_5": 0x5C74,
        "MI_As_5": 0x5C75,
        "MI_B_5": 0x5C76,
        "MI_ALLOFF": 0x5CB0,
        "MI_OCT_N2": 0x5C77,
        "MI_OCT_N1": 0x5C78,
        "MI_OCT_0": 0x5C79,
        "MI_OCT_1": 0x5C7A,
        "MI_OCT_2": 0x5C7B,
        "MI_OCT_3": 0x5C7C,
        "MI_OCT_4": 0x5C7D,
        "MI_OCT_5": 0x5C7E,
        "MI_OCT_6": 0x5C7F,
        "MI_OCT_7": 0x5C80,
        "MI_OCTD": 0x5C81,
        "MI_OCTU": 0x5C82,
        "MI_TRNS_N6": 0x5C83,
        "MI_TRNS_N5": 0x5C84,
        "MI_TRNS_N4": 0x5C85,
        "MI_TRNS_N3": 0x5C86,
        "MI_TRNS_N2": 0x5C87,
        "MI_TRNS_N1": 0x5C88,
        "MI_TRNS_0": 0x5C89,
        "MI_TRNS_1": 0x5C8A,
        "MI_TRNS_2": 0x5C8B,
        "MI_TRNS_3": 0x5C8C,
        "MI_TRNS_4": 0x5C8D,
        "MI_TRNS_5": 0x5C8E,
        "MI_TRNS_6": 0x5C8F,
        "MI_TRNSD": 0x5C90,
        "MI_TRNSU": 0x5C91,
        "MI_VEL_1": 0x5C92,
        "MI_VEL_2": 0x5C93,
        "MI_VEL_3": 0x5C94,
        "MI_VEL_4": 0x5C95,
        "MI_VEL_5": 0x5C96,
        "MI_VEL_6": 0x5C97,
        "MI_VEL_7": 0x5C98,
        "MI_VEL_8": 0x5C99,
        "MI_VEL_9": 0x5C9A,
        "MI_VEL_10": 0x5C9B,
        "MI_VELD": 0x5C9C,
        "MI_VELU": 0x5C9D,
        "MI_CH1": 0x5C9E,
        "MI_CH2": 0x5C9F,
        "MI_CH3": 0x5CA0,
        "MI_CH4": 0x5CA1,
        "MI_CH5": 0x5CA2,
        "MI_CH6": 0x5CA3,
        "MI_CH7": 0x5CA4,
        "MI_CH8": 0x5CA5,
        "MI_CH9": 0x5CA6,
        "MI_CH10": 0x5CA7,
        "MI_CH11": 0x5CA8,
        "MI_CH12": 0x5CA9,
        "MI_CH13": 0x5CAA,
        "MI_CH14": 0x5CAB,
        "MI_CH15": 0x5CAC,
        "MI_CH16": 0x5CAD,
        "MI_CHD": 0x5CAE,
        "MI_CHU": 0x5CAF,
        "MI_SUS": 0x5CB1,
        "MI_PORT": 0x5CB2,
        "MI_SOST": 0x5CB3,
        "MI_SOFT": 0x5CB4,
        "MI_LEG": 0x5CB5,
        "MI_MOD": 0x5CB6,
        "MI_MODSD": 0x5CB7,
        "MI_MODSU": 0x5CB8,
        "MI_BENDD": 0x5CB9,
        "MI_BENDU": 0x5CBA,

        "QK_BOOT": 0x5C00,
        "QK_CLEAR_EEPROM": 0x5CDF,

        "FN_MO13": 0x5F10,
        "FN_MO23": 0x5F11,

        "QK_KB": 0x5F80,
        "QK_MACRO": 0x5F12,

        "QMK_LM_SHIFT": 4,
        "QMK_LM_MASK": 0xF,

        # TODO: these keycodes don't actually exist in v5; we need fake ones here to unbreak the build
        # TODO: these should be removed after we can move keycodes to be owned by the Keyboard object and support optional/not implemented keycodes
        "RM_ON": 0x9990,
        "RM_OFF": 0x9991,
        "RM_TOGG": 0x9992,
        "RM_NEXT": 0x9993,
        "RM_PREV": 0x9994,
        "RM_HUEU": 0x9995,
        "RM_HUED": 0x9996,
        "RM_SATU": 0x9997,
        "RM_SATD": 0x9998,
        "RM_VALU": 0x9999,
        "RM_VALD": 0x999a,
        "RM_SPDU": 0x999b,
        "RM_SPDD": 0x999c,
        "QK_REBOOT": 0x999d,

        "QK_CAPS_WORD_TOGGLE": 0x999e,
        "QK_LAYER_LOCK": 0x999f,
        "QK_PERSISTENT_DEF_LAYER": 0x999a0,  # Reserve 0x999a0 - 0x999bf.
        "QK_REPEAT_KEY": 0x999c0,
        "QK_ALT_REPEAT_KEY": 0x999c1,
    }

    masked = set()


for x in range(256):
    keycodes_v5.kc["M{}".format(x)] = keycodes_v5.kc["QK_MACRO"] + x
    keycodes_v5.kc["TD({})".format(x)] = keycodes_v5.kc["QK_TAP_DANCE"] + x

for x in range(32):
    keycodes_v5.kc["MO({})".format(x)] = keycodes_v5.kc["QK_MOMENTARY"] | x
    keycodes_v5.kc["DF({})".format(x)] = keycodes_v5.kc["QK_DEF_LAYER"] | x
    keycodes_v5.kc["TG({})".format(x)] = keycodes_v5.kc["QK_TOGGLE_LAYER"] | x
    keycodes_v5.kc["TT({})".format(x)] = keycodes_v5.kc["QK_LAYER_TAP_TOGGLE"] | x
    keycodes_v5.kc["OSL({})".format(x)] = keycodes_v5.kc["QK_ONE_SHOT_LAYER"] | x
    keycodes_v5.kc["TO({})".format(x)] = keycodes_v5.kc["QK_TO"] | (1 << 4) | x
    keycodes_v5.kc["PDF({})".format(x)] = keycodes_v5.kc["QK_PERSISTENT_DEF_LAYER"] + x

for x in range(16):
    keycodes_v5.kc["LT{}(kc)".format(x)] = keycodes_v5.kc["QK_LAYER_TAP"] | (((x) & 0xF) << 8)

#TODO(userkeycodes): temp workaround, keycodes handling is messy, rework this later
for x in range(64):
    keycodes_v5.kc["USER{:02}".format(x)] = keycodes_v5.kc["QK_KB"] + x

for name, val in keycodes_v5.kc.items():
    if name.endswith("(kc)"):
        keycodes_v5.masked.add(val)
