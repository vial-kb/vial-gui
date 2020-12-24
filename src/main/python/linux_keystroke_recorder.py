# SPDX-License-Identifier: GPL-2.0-or-later
import sys

import keyboard


def key_cb(key):
    names = keyboard._nixkeyboard.to_name[(key.scan_code, ())] or ["unknown"]
    name = names[0]
    name = keyboard.normalize_name(name)

    sys.stdout.write("{}:{}\n".format(key.event_type, name))
    sys.stdout.flush()


def linux_keystroke_recorder():
    keyboard.hook(key_cb)
    while True:
        ch = sys.stdin.read(1)
        if ch == "q":
            keyboard.unhook_all()
            break
