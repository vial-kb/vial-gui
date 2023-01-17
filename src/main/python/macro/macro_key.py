# SPDX-License-Identifier: GPL-2.0-or-later
from keycodes.keycodes import Keycode


class BasicKey:

    pass


class BasicKeycode(BasicKey):

    def __init__(self, kc):
        if isinstance(kc, int):
            kc = Keycode.find(kc)
        self.keycode = kc


class KeyDown(BasicKeycode):

    def __repr__(self):
        return "Down({})".format(Keycode.label(self.keycode.code))

    def __eq__(self, other):
        return isinstance(other, KeyDown) and other.keycode == self.keycode


class KeyUp(BasicKeycode):

    def __repr__(self):
        return "Up({})".format(Keycode.label(self.keycode.code))

    def __eq__(self, other):
        return isinstance(other, KeyUp) and other.keycode == self.keycode


class KeyTap(BasicKeycode):

    def __repr__(self):
        return "Tap({})".format(Keycode.label(self.keycode.code))

    def __eq__(self, other):
        return isinstance(other, KeyTap) and other.keycode == self.keycode


class KeyString(BasicKey):

    def __init__(self, string):
        self.string = string

    def __repr__(self):
        return "SendString({})".format(self.string)

    def __eq__(self, other):
        return isinstance(other, KeyString) and other.string == self.string
