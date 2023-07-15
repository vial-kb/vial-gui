from protocol.keyboard_comm import Keyboard


class DummyKeyboard(Keyboard):

    def reload_layers(self):
        self.layers = 4

    def reload_keymap(self):
        for layer in range(self.layers):
            for row, col in self.rowcol.keys():
                self.layout[(layer, row, col)] = "KC_NO"

        for layer in range(self.layers):
            for idx in self.encoderpos:
                self.encoder_layout[(layer, idx, 0)] = "KC_NO"
                self.encoder_layout[(layer, idx, 1)] = "KC_NO"

        if self.layout_labels:
            self.layout_options = 0

    def reload_macros(self):
        self.macro_count = 16
        self.macro_memory = 900

        self.macro = b"\x00" * self.macro_count

    def set_key(self, layer, row, col, code):
        self.layout[(layer, row, col)] = code

    def set_encoder(self, layer, index, direction, code):
        self.encoder_layout[(layer, index, direction)] = code

    def set_layout_options(self, options):
        if self.layout_options != -1 and self.layout_options != options:
            self.layout_options = options

    def set_macro(self, data):
        if len(data) > self.macro_memory:
            raise RuntimeError("the macro is too big: got {} max {}".format(len(data), self.macro_memory))
        self.macro = data

    def reset(self):
        pass

    def get_uid(self):
        return b"\x00" * 8

    def get_unlock_status(self):
        return 1

    def get_unlock_in_progress(self):
        return 0

    def get_unlock_keys(self):
        return []

    def unlock_start(self):
        return

    def unlock_poll(self):
        return b""

    def lock(self):
        return

    def reload_via_protocol(self):
        pass

    def reload_persistent_rgb(self):
        """
            Reload RGB properties which are slow, and do not change while keyboard is plugged in
            e.g. VialRGB supported effects list
        """

        if "lighting" in self.definition:
            self.lighting_qmk_rgblight = self.definition["lighting"] in ["qmk_rgblight", "qmk_backlight_rgblight"]
            self.lighting_qmk_backlight = self.definition["lighting"] in ["qmk_backlight", "qmk_backlight_rgblight"]
            self.lighting_vialrgb = self.definition["lighting"] == "vialrgb"

        if self.lighting_vialrgb:
            self.rgb_version = 1
            self.rgb_maximum_brightness = 128

            self.rgb_supported_effects = {0, 1, 2, 3}

    def reload_rgb(self):
        if self.lighting_qmk_rgblight:
            self.underglow_brightness = 128
            self.underglow_effect = 1
            self.underglow_effect_speed = 5
            # hue, sat
            self.underglow_color = (32, 64)

        if self.lighting_qmk_backlight:
            self.backlight_brightness = 42
            self.backlight_effect = 0

        if self.lighting_vialrgb:
            self.rgb_mode = 2
            self.rgb_speed = 90
            self.rgb_hsv = (16, 32, 64)
