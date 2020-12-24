# SPDX-License-Identifier: GPL-2.0-or-later
from keycodes import keycode_label


class KeyDown:

    def __init__(self, keycode):
        self.keycode = keycode

    def __repr__(self):
        return "Down({})".format(keycode_label(self.keycode.code))


class KeyUp:

    def __init__(self, keycode):
        self.keycode = keycode

    def __repr__(self):
        return "Up({})".format(keycode_label(self.keycode.code))


class KeyTap:

    def __init__(self, keycode):
        self.keycode = keycode

    def __repr__(self):
        return "Tap({})".format(keycode_label(self.keycode.code))


class KeyString:

    def __init__(self, string):
        self.string = string

    def __repr__(self):
        return "SendString({})".format(self.string)
