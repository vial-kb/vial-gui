import sys

import keyboard


def key_cb(key):
    print(key)


def linux_keystroke_recorder():
    keyboard.hook(key_cb)
    print("Recording")
    while True:
        ch = sys.stdin.read(1)
        if ch == "q":
            keyboard.unhook_all()
            break
