from keycodes.keycodes import Keycode
from keymap import brazilian, canadian_csa, colemak, danish, eurkey, french, german, hebrew, hungarian, italian, japanese, latam, norwegian, russian, slovak, spanish, swedish, swedish_swerty, swiss, turkish, ukrainian, croatian

KEYMAPS = [
    ("QWERTY", dict()),
    ("Brazilian (QWERTY)", brazilian.keymap),
    ("Canadian CSA (QWERTY)", canadian_csa.keymap),
    ("Colemak", colemak.keymap),
    ("Croatian (QWERTZ)", croatian.keymap),
    ("Danish (QWERTY)", danish.keymap),
    ("EurKey (QWERTY)", eurkey.keymap),
    ("French (AZERTY)", french.keymap),
    ("French (MAC)", french.keymap_mac),
    ("German (QWERTZ)", german.keymap),
    ("Hebrew (Standard)", hebrew.keymap),
    ("Hungarian (QWERTZ)", hungarian.keymap),
    ("Italian (QWERTY)", italian.keymap),
    ("Japanese (QWERTY)", japanese.keymap),
    ("Latin American (QWERTY)", latam.keymap),
    ("Norwegian (QWERTY)", norwegian.keymap),
    ("Russian (ЙЦУКЕН)", russian.keymap),
    ("Russian (braindefender, ortho)", russian.universal_braindefender_ortho),
    ("Russian (braindefender, standard)", russian.universal_braindefender_standard),
    ("Slovak (QWERTY)", slovak.keymap),
    ("Spanish (QWERTY)", spanish.keymap),
    ("Swedish (QWERTY)", swedish.keymap),
    ("Swedish (SWERTY)", swedish_swerty.keymap),
    ("Swiss (QWERTZ)", swiss.keymap),
    ("Turkish (QWERTY)", turkish.keymap),
    ("Ukrainian (ЙЦУКЕН)", ukrainian.keymap)
]

# make sure that qmk IDs we used are all correct
for name, keymap in KEYMAPS:
    for qmk_id in keymap.keys():
        if Keycode.find_by_qmk_id(qmk_id) is None:
            raise RuntimeError("Misconfigured - cannot find QMK keycode {}".format(qmk_id))
