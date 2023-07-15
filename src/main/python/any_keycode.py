import ast

import simpleeval
import operator

from keycodes.keycodes import KEYCODES_SPECIAL, KEYCODES_BASIC, KEYCODES_SHIFTED, KEYCODES_ISO, KEYCODES_BACKLIGHT, \
    KEYCODES_MEDIA, KEYCODES_USER, Keycode

r = Keycode.resolve


def LCTL(kc): return (r("QK_LCTL") | (kc))
def LSFT(kc): return (r("QK_LSFT") | (kc))
def LALT(kc): return (r("QK_LALT") | (kc))
def LGUI(kc): return (r("QK_LGUI") | (kc))
def RCTL(kc): return (r("QK_RCTL") | (kc))
def RSFT(kc): return (r("QK_RSFT") | (kc))
def RALT(kc): return (r("QK_RALT") | (kc))
def RGUI(kc): return (r("QK_RGUI") | (kc))
def C_S(kc): return (r("QK_LCTL") | r("QK_LSFT") | (kc))
def HYPR(kc): return (r("QK_LCTL") | r("QK_LSFT") | r("QK_LALT") | r("QK_LGUI") | (kc))
def MEH(kc): return (r("QK_LCTL") | r("QK_LSFT") | r("QK_LALT") | (kc))
def LCAG(kc): return (r("QK_LCTL") | r("QK_LALT") | r("QK_LGUI") | (kc))
def SGUI(kc): return (r("QK_LGUI") | r("QK_LSFT") | (kc))
def LCA(kc): return (r("QK_LCTL") | r("QK_LALT") | (kc))
def LSA(kc): return (r("QK_LSFT") | r("QK_LALT") | (kc))
def RSA(kc): return (r("QK_RSFT") | r("QK_RALT") | (kc))
def RCS(kc): return (r("QK_RCTL") | r("QK_RSFT") | (kc))
def LCG(kc): return (r("QK_LCTL") | r("QK_LGUI") | (kc))
def RCG(kc): return (r("QK_RCTL") | r("QK_RGUI") | (kc))

# TODO: make sure bit packing is the same in new fw
def LT(layer, kc): return (r("QK_LAYER_TAP") | (((layer)&0xF) << 8) | ((kc)&0xFF))
def TO(layer): return (r("QK_TO") | (r("ON_PRESS") << 0x4) | ((layer)&0xFF))
def MO(layer): return (r("QK_MOMENTARY") | ((layer)&0xFF))
def DF(layer): return (r("QK_DEF_LAYER") | ((layer)&0xFF))
def TG(layer): return (r("QK_TOGGLE_LAYER") | ((layer)&0xFF))
def OSL(layer): return (r("QK_ONE_SHOT_LAYER") | ((layer)&0xFF))
def LM(layer, mod): return (r("QK_LAYER_MOD") | (((layer)&0xF) << 4) | ((mod)&0xF))
def OSM(mod): return (r("QK_ONE_SHOT_MOD") | ((mod)&0xFF))
def TT(layer): return (r("QK_LAYER_TAP_TOGGLE") | ((layer)&0xFF))
def MT(mod, kc): return (r("QK_MOD_TAP") | (((mod)&0x1F) << 8) | ((kc)&0xFF))
def TD(n): return (r("QK_TAP_DANCE") | ((n)&0xFF))


def LCTL_T(kc): return MT(r("MOD_LCTL"), kc)
def RCTL_T(kc): return MT(r("MOD_RCTL"), kc)
def LSFT_T(kc): return MT(r("MOD_LSFT"), kc)
def RSFT_T(kc): return MT(r("MOD_RSFT"), kc)
def LALT_T(kc): return MT(r("MOD_LALT"), kc)
def RALT_T(kc): return MT(r("MOD_RALT"), kc)
def LGUI_T(kc): return MT(r("MOD_LGUI"), kc)
def RGUI_T(kc): return MT(r("MOD_RGUI"), kc)
def C_S_T(kc): return MT(r("MOD_LCTL") | r("MOD_LSFT"), kc)
def MEH_T(kc): return MT(r("MOD_LCTL") | r("MOD_LSFT") | r("MOD_LALT"), kc)
def LCAG_T(kc): return MT(r("MOD_LCTL") | r("MOD_LALT") | r("MOD_LGUI"), kc)
def RCAG_T(kc): return MT(r("MOD_RCTL") | r("MOD_RALT") | r("MOD_RGUI"), kc)
def HYPR_T(kc): return MT(r("MOD_LCTL") | r("MOD_LSFT") | r("MOD_LALT") | r("MOD_LGUI"), kc)
def SGUI_T(kc): return MT(r("MOD_LGUI") | r("MOD_LSFT"), kc)
def LCA_T(kc): return MT(r("MOD_LCTL") | r("MOD_LALT"), kc)
def LSA_T(kc): return MT(r("MOD_LSFT") | r("MOD_LALT"), kc)
def RSA_T(kc): return MT(r("MOD_RSFT") | r("MOD_RALT"), kc)
def RCS_T(kc): return MT(r("MOD_RCTL") | r("MOD_RSFT"), kc)
def LCG_T(kc): return MT(r("MOD_LCTL") | r("MOD_LGUI"), kc)
def RCG_T(kc): return MT(r("MOD_RCTL") | r("MOD_RGUI"), kc)


functions = {
    "LCTL": LCTL, "LSFT": LSFT, "LALT": LALT, "LGUI": LGUI, "LOPT": LALT, "LCMD": LGUI, "LWIN": LGUI,
    "RCTL": RCTL, "RSFT": RSFT, "RALT": RALT, "RGUI": RGUI, "ALGR": RALT, "ROPT": RALT, "RCMD": RGUI, "RWIN": RGUI,
    "HYPR": HYPR, "MEH": MEH, "LCAG": LCAG, "SGUI": SGUI, "SCMD": SGUI, "SWIN": SGUI, "LSG": SGUI,
    "C_S": C_S,
    "LCA": LCA, "LSA": LSA, "RSA": RSA, "RCS": RCS, "SAGR": RSA,
    "C": LCTL, "S": LSFT, "A": LALT, "G": LGUI,
    "LT": LT, "TO": TO, "MO": MO, "DF": DF, "TG": TG, "OSL": OSL, "LM": LM, "OSM": OSM, "TT": TT, "MT": MT,
    "LCTL_T": LCTL_T, "RCTL_T": RCTL_T, "CTL_T": LCTL_T,
    "LSFT_T": LSFT_T, "RSFT_T": RSFT_T, "SFT_T": LSFT_T,
    "LALT_T": LALT_T, "RALT_T": RALT_T, "LOPT_T": LALT_T, "ROPT_T": RALT_T, "ALGR_T": RALT_T, "ALT_T": LALT_T, "OPT_T": LALT_T,
    "LGUI_T": LGUI_T, "RGUI_T": RGUI_T, "LCMD_T": LGUI_T, "LWIN_T": LGUI_T, "RCMD_T": RGUI_T, "RWIN_T": RGUI_T,
    "GUI_T": LGUI_T, "CMD_T": LGUI_T, "WIN_T": LGUI_T,
    "C_S_T": C_S_T, "MEH_T": MEH_T,
    "LCAG_T": LCAG_T, "RCAG_T": RCAG_T, "HYPR_T": HYPR_T, "SGUI_T": SGUI_T, "SCMD_T": SGUI_T, "SWIN_T": SGUI_T,
    "LSG_T": SGUI_T,
    "LCA_T": LCA_T, "LSA_T": LSA_T, "RSA_T": RSA_T, "RCS_T": RCS_T, "SAGR_T": RSA_T, "ALL_T": HYPR_T,
    "TD": TD,
    "LCG": LCG, "RCG": RCG, "LCG_T": LCG_T, "RCG_T": RCG_T,
}

for x in range(32):
    functions["LT{}".format(x)] = lambda kc, layer=x: (r("QK_LAYER_TAP") | (((layer)&0xF) << 8) | ((kc)&0xFF))


class AnyKeycode:

    def __init__(self):
        self.ops = simpleeval.DEFAULT_OPERATORS.copy()
        self.ops.update({
            ast.BitOr: operator.or_,
            ast.BitXor: operator.xor,
            ast.BitAnd: operator.and_,
        })
        self.names = dict()
        self.prepare_names()

    def prepare_names(self):
        for kc in KEYCODES_SPECIAL + KEYCODES_BASIC + KEYCODES_SHIFTED + KEYCODES_ISO + KEYCODES_BACKLIGHT + \
                  KEYCODES_MEDIA + KEYCODES_USER:
            for qmk_id in kc.alias:
                self.names[qmk_id] = Keycode.resolve(kc.qmk_id)
        macros = dict()
        for s in ["MOD_LCTL", "MOD_LSFT", "MOD_LALT", "MOD_LGUI", "MOD_RCTL", "MOD_RSFT", "MOD_RALT", "MOD_RGUI",
                  "MOD_MEH", "MOD_HYPR"]:
            macros[s] = Keycode.resolve(s)
        self.names.update(macros)

    def decode(self, s):
        return simpleeval.simple_eval(s, names=self.names, functions=functions, operators=self.ops)
