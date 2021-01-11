from keycodes import Keycode
from keymap import french, german, hungarian, norwegian, russian

KEYMAPS = [
    ("QWERTY", dict()),
    ("French (AZERTY)", french.keymap),
    ("German (QWERTZ)", german.keymap),
    ("Hungarian (QWERTZ)", hungarian.keymap),
    ("Norwegian (QWERTY)", norwegian.keymap),
    ("Russian (ЙЦУКЕН)", russian.keymap)
]

# make sure that qmk IDs we used are all correct
for name, keymap in KEYMAPS:
    for qmk_id in keymap.keys():
        if Keycode.find_by_qmk_id(qmk_id) is None:
            raise RuntimeError("Misconfigured - cannot find QMK keycode {}".format(qmk_id))
