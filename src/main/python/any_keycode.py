import ast

import simpleeval
import operator

from keycodes import KEYCODES_SPECIAL, KEYCODES_BASIC, KEYCODES_SHIFTED, KEYCODES_ISO, KEYCODES_BACKLIGHT, \
    KEYCODES_MEDIA, KEYCODES_USER, QK_LCTL, QK_LSFT, QK_LALT, QK_LGUI, QK_RCTL, QK_RSFT, QK_RALT, QK_RGUI, QK_LAYER_TAP, \
    MOD_MEH, MOD_HYPR


QK_TO = 0x5000
QK_MOMENTARY = 0x5100
QK_DEF_LAYER = 0x5200
QK_TOGGLE_LAYER = 0x5300
QK_ONE_SHOT_LAYER = 0x5400
QK_ONE_SHOT_MOD = 0x5500
QK_TAP_DANCE = 0x5700
QK_LAYER_TAP_TOGGLE = 0x5800
QK_LAYER_MOD = 0x5900
QK_MOD_TAP = 0x6000
ON_PRESS = 1

MOD_LCTL = 0x01
MOD_LSFT = 0x02
MOD_LALT = 0x04
MOD_LGUI = 0x08
MOD_RCTL = 0x11
MOD_RSFT = 0x12
MOD_RALT = 0x14
MOD_RGUI = 0x18


def LCTL(kc): return (QK_LCTL | (kc))
def LSFT(kc): return (QK_LSFT | (kc))
def LALT(kc): return (QK_LALT | (kc))
def LGUI(kc): return (QK_LGUI | (kc))
def RCTL(kc): return (QK_RCTL | (kc))
def RSFT(kc): return (QK_RSFT | (kc))
def RALT(kc): return (QK_RALT | (kc))
def RGUI(kc): return (QK_RGUI | (kc))
def C_S(kc): return (QK_LCTL | QK_LSFT | (kc))
def HYPR(kc): return (QK_LCTL | QK_LSFT | QK_LALT | QK_LGUI | (kc))
def MEH(kc): return (QK_LCTL | QK_LSFT | QK_LALT | (kc))
def LCAG(kc): return (QK_LCTL | QK_LALT | QK_LGUI | (kc))
def SGUI(kc): return (QK_LGUI | QK_LSFT | (kc))
def LCA(kc): return (QK_LCTL | QK_LALT | (kc))
def LSA(kc): return (QK_LSFT | QK_LALT | (kc))
def RSA(kc): return (QK_RSFT | QK_RALT | (kc))
def RCS(kc): return (QK_RCTL | QK_RSFT | (kc))


def LT(layer, kc): return (QK_LAYER_TAP | (((layer)&0xF) << 8) | ((kc)&0xFF))
def TO(layer): return (QK_TO | (ON_PRESS << 0x4) | ((layer)&0xFF))
def MO(layer): return (QK_MOMENTARY | ((layer)&0xFF))
def DF(layer): return (QK_DEF_LAYER | ((layer)&0xFF))
def TG(layer): return (QK_TOGGLE_LAYER | ((layer)&0xFF))
def OSL(layer): return (QK_ONE_SHOT_LAYER | ((layer)&0xFF))
def LM(layer, mod): return (QK_LAYER_MOD | (((layer)&0xF) << 4) | ((mod)&0xF))
def OSM(mod): return (QK_ONE_SHOT_MOD | ((mod)&0xFF))
def TT(layer): return (QK_LAYER_TAP_TOGGLE | ((layer)&0xFF))
def MT(mod, kc): return (QK_MOD_TAP | (((mod)&0x1F) << 8) | ((kc)&0xFF))
def TD(n): return (QK_TAP_DANCE | ((n)&0xFF))


def LCTL_T(kc): return MT(MOD_LCTL, kc)
def RCTL_T(kc): return MT(MOD_RCTL, kc)
def LSFT_T(kc): return MT(MOD_LSFT, kc)
def RSFT_T(kc): return MT(MOD_RSFT, kc)
def LALT_T(kc): return MT(MOD_LALT, kc)
def RALT_T(kc): return MT(MOD_RALT, kc)
def LGUI_T(kc): return MT(MOD_LGUI, kc)
def RGUI_T(kc): return MT(MOD_RGUI, kc)
def C_S_T(kc): return MT(MOD_LCTL | MOD_LSFT, kc)
def MEH_T(kc): return MT(MOD_LCTL | MOD_LSFT | MOD_LALT, kc)
def LCAG_T(kc): return MT(MOD_LCTL | MOD_LALT | MOD_LGUI, kc)
def RCAG_T(kc): return MT(MOD_RCTL | MOD_RALT | MOD_RGUI, kc)
def HYPR_T(kc): return MT(MOD_LCTL | MOD_LSFT | MOD_LALT | MOD_LGUI, kc)
def SGUI_T(kc): return MT(MOD_LGUI | MOD_LSFT, kc)
def LCA_T(kc): return MT(MOD_LCTL | MOD_LALT, kc)
def LSA_T(kc): return MT(MOD_LSFT | MOD_LALT, kc)
def RSA_T(kc): return MT(MOD_RSFT | MOD_RALT, kc)
def RCS_T(kc): return MT(MOD_RCTL | MOD_RSFT, kc)


functions = {
    "LCTL": LCTL, "LSFT": LSFT, "LALT": LALT, "LGUI": LGUI, "LOPT": LALT, "LCMD": LGUI, "LWIN": LGUI,
    "RCTL": RCTL, "RSFT": RSFT, "RALT": RALT, "RGUI": RGUI, "ALGR": RALT, "ROPT": RALT, "RCMD": RGUI, "RWIN": RGUI,
    "HYPR": HYPR, "MEH": MEH, "LCAG": LCAG, "SGUI": SGUI, "SCMD": SGUI, "SWIN": SGUI,
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
    "LCA_T": LCA_T, "LSA_T": LSA_T, "RSA_T": RSA_T, "RCS_T": RCS_T, "SAGR_T": RSA_T, "ALL_T": HYPR_T,
    "TD": TD,
}


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
                self.names[qmk_id] = kc.code
        self.names.update({
            "MOD_LCTL": MOD_LCTL,
            "MOD_LSFT": MOD_LSFT,
            "MOD_LALT": MOD_LALT,
            "MOD_LGUI": MOD_LGUI,
            "MOD_RCTL": MOD_RCTL,
            "MOD_RSFT": MOD_RSFT,
            "MOD_RALT": MOD_RALT,
            "MOD_RGUI": MOD_RGUI,
            "MOD_MEH": MOD_MEH,
            "MOD_HYPR": MOD_HYPR,
        })

    def decode(self, s):
        return simpleeval.simple_eval(s, names=self.names, functions=functions, operators=self.ops)
