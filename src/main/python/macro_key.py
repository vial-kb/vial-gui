# SPDX-License-Identifier: GPL-2.0-or-later
from keycodes import Keycode


class BasicKey:

    pass


class KeyDown(BasicKey):

    def __init__(self, keycode):
        self.keycode = keycode

    def __repr__(self):
        return "Down({})".format(Keycode.label(self.keycode.code))

    def __eq__(self, other):
        return isinstance(other, KeyDown) and other.keycode == self.keycode


class KeyUp(BasicKey):

    def __init__(self, keycode):
        self.keycode = keycode

    def __repr__(self):
        return "Up({})".format(Keycode.label(self.keycode.code))

    def __eq__(self, other):
        return isinstance(other, KeyUp) and other.keycode == self.keycode


class KeyTap(BasicKey):

    def __init__(self, keycode):
        self.keycode = keycode

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
