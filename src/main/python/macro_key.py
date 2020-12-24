# SPDX-License-Identifier: GPL-2.0-or-later
from keycodes import keycode_label


class BasicAction:

    pass


class KeyDown(BasicAction):

    def __init__(self, keycode):
        self.keycode = keycode

    def __repr__(self):
        return "Down({})".format(keycode_label(self.keycode.code))

    def __eq__(self, other):
        return isinstance(other, KeyDown) and other.keycode == self.keycode


class KeyUp(BasicAction):

    def __init__(self, keycode):
        self.keycode = keycode

    def __repr__(self):
        return "Up({})".format(keycode_label(self.keycode.code))

    def __eq__(self, other):
        return isinstance(other, KeyUp) and other.keycode == self.keycode


class KeyTap(BasicAction):

    def __init__(self, keycode):
        self.keycode = keycode

    def __repr__(self):
        return "Tap({})".format(keycode_label(self.keycode.code))

    def __eq__(self, other):
        return isinstance(other, KeyTap) and other.keycode == self.keycode


class KeyString(BasicAction):

    def __init__(self, string):
        self.string = string

    def __repr__(self):
        return "SendString({})".format(self.string)

    def __eq__(self, other):
        return isinstance(other, KeyString) and other.string == self.string
