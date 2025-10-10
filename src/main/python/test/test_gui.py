import lzma
import os.path
import struct

from PyQt5.QtCore import QPoint
from PyQt5.QtWidgets import QPushButton
from pytestqt.qt_compat import qt_api

from main_window import MainWindow

from protocol.constants import CMD_VIA_GET_PROTOCOL_VERSION, CMD_VIA_VIAL_PREFIX, CMD_VIAL_GET_KEYBOARD_ID, \
    CMD_VIAL_GET_SIZE, CMD_VIAL_GET_DEFINITION, CMD_VIA_GET_LAYER_COUNT, CMD_VIA_MACRO_GET_COUNT, \
    CMD_VIA_MACRO_GET_BUFFER_SIZE, CMD_VIAL_QMK_SETTINGS_QUERY, CMD_VIAL_DYNAMIC_ENTRY_OP, \
    DYNAMIC_VIAL_GET_NUMBER_OF_ENTRIES, CMD_VIA_KEYMAP_GET_BUFFER, CMD_VIA_MACRO_GET_BUFFER, CMD_VIAL_GET_UNLOCK_STATUS, \
    CMD_VIA_SET_KEYCODE, DYNAMIC_VIAL_COMBO_GET, DYNAMIC_VIAL_COMBO_SET, DYNAMIC_VIAL_TAP_DANCE_GET, \
    DYNAMIC_VIAL_TAP_DANCE_SET
from widgets.square_button import SquareButton

FAKE_KEYBOARD = """
{
  "matrix": {
    "rows": 2,
    "cols": 2
  },
  "layouts": {
    "keymap": [
      [
        "0,0",
        "0,1"
      ],
      [
        "1,0",
        "1,1"
      ]
    ]
  }
}
"""


def mock_enumerate():
    return [{
        "vendor_id": 0xDEAD,
        "product_id": 0xBEEF,
        "serial_number": "vial:f64c2b3c",
        "usage_page": 0xFF60,
        "usage": 0x61,
        "path": "/magic/path/for/tests",
        "manufacturer_string": "Vial Testing Ltd",
        "product_string": "Test Keyboard",
    }]


class VirtualKeyboard:

    def __init__(self, kbjson, combos=None, tap_dance=None):
        if combos is None:
            combos = []
        if tap_dance is None:
            tap_dance = []

        self.keyboard_definition = lzma.compress(kbjson.encode("utf-8"))

        self.rows = 2
        self.cols = 2
        self.layers = 4
        self.keymap = []
        for layer in range(self.layers):
            self.keymap.append([])
            for row in range(self.rows):
                self.keymap[-1].append([0 for x in range(self.cols)])

        self.macro_count = 8
        self.macro_buffer = b"\x00" * 512

        self.combos = combos
        self.tap_dance = tap_dance

        self.key_override_entries = 0
        self.alt_repeat_key_entries = 0

    def get_keymap_buffer(self):
        output = b""
        for layer in range(self.layers):
            for row in range(self.rows):
                for col in range(self.cols):
                    output += struct.pack(">H", self.keymap[layer][row][col])
        return output

    def vial_cmd_dynamic(self, msg):
        if msg[2] == DYNAMIC_VIAL_GET_NUMBER_OF_ENTRIES:
            response = struct.pack("BBBB", len(self.tap_dance), len(self.combos),
                                   self.key_override_entries, self.alt_repeat_key_entries)
            # Zero pad to 31 bytes.
            response += (31 - len(response)) * b'\0'
            # Set last two bits, indicating Caps Word and Layer Lock.
            response += (0b00000011).to_bytes(1, "little")
            return response
        elif msg[2] == DYNAMIC_VIAL_COMBO_GET:
            idx = msg[3]
            assert idx < len(self.combos)
            return struct.pack("<BHHHHH", 0, *self.combos[idx])
        elif msg[2] == DYNAMIC_VIAL_COMBO_SET:
            idx = msg[3]
            keys = struct.unpack_from("<HHHHH", msg[4:])
            assert idx < len(self.combos)
            self.combos[idx] = keys
            return b""
        elif msg[2] == DYNAMIC_VIAL_TAP_DANCE_GET:
            idx = msg[3]
            assert idx < len(self.tap_dance)
            return struct.pack("<BHHHHH", 0, *self.tap_dance[idx])
        elif msg[2] == DYNAMIC_VIAL_TAP_DANCE_SET:
            idx = msg[3]
            values = struct.unpack_from("<HHHHH", msg[4:])
            assert idx < len(self.tap_dance)
            self.tap_dance[idx] = values
            return b""
        raise RuntimeError("unsupported dynamic submsg 0x{:02X}".format(msg[2]))

    def vial_cmd(self, msg):
        if msg[1] == CMD_VIAL_GET_KEYBOARD_ID:
            return struct.pack("<IQ", 6, 0xF00DFACEDEADBEEF)
        elif msg[1] == CMD_VIAL_GET_SIZE:
            return struct.pack("<I", len(self.keyboard_definition))
        elif msg[1] == CMD_VIAL_GET_DEFINITION:
            page = struct.unpack_from("<H", msg[2:])[0]
            return self.keyboard_definition[page*32:(page+1)*32]
        elif msg[1] == CMD_VIAL_GET_UNLOCK_STATUS:
            return struct.pack("<BB", 0, 0)  # TODO we want to test unlocking as well
        elif msg[1] == CMD_VIAL_QMK_SETTINGS_QUERY:
            return b"\xFF" * 32
        elif msg[1] == CMD_VIAL_DYNAMIC_ENTRY_OP:
            return self.vial_cmd_dynamic(msg)
        raise RuntimeError("unknown command for Vial protocol 0x{:02X}".format(msg[1]))

    def process(self, msg):
        if msg[0] == CMD_VIA_VIAL_PREFIX:
            return self.vial_cmd(msg)
        elif msg[0] == CMD_VIA_GET_PROTOCOL_VERSION:
            return struct.pack(">BH", msg[0], 9)
        elif msg[0] == CMD_VIA_SET_KEYCODE:
            layer, row, col, kc = struct.unpack_from(">BBBH", msg[1:])
            self.keymap[layer][row][col] = kc
            return b""
        elif msg[0] == CMD_VIA_MACRO_GET_COUNT:
            return struct.pack(">BB", msg[0], self.macro_count)
        elif msg[0] == CMD_VIA_MACRO_GET_BUFFER_SIZE:
            return struct.pack(">BH", msg[0], len(self.macro_buffer))
        elif msg[0] == CMD_VIA_MACRO_GET_BUFFER:
            offset, size = struct.unpack_from(">HB", msg[1:])
            return msg[0:1] + self.macro_buffer[offset:offset+size]
        elif msg[0] == CMD_VIA_GET_LAYER_COUNT:
            return struct.pack(">BB", msg[0], self.layers)
        elif msg[0] == CMD_VIA_KEYMAP_GET_BUFFER:
            offset, size = struct.unpack_from(">HB", msg[1:])
            return msg[0:1] + self.get_keymap_buffer()[offset:offset+size]
        raise RuntimeError("unknown command for VIA protocol 0x{:02X}".format(msg[0]))


class MockDevice:

    def open_path(self, path):
        assert path == "/magic/path/for/tests"

    def close(self):
        pass

    def write(self, data):
        assert len(data) == 33
        assert data[0] == 0
        self.msg = data[1:]

        return len(data)

    def read(self, sz, timeout_ms=None):
        assert sz == 32
        resp = self.vk.process(self.msg)
        assert len(resp) <= 32
        resp += b"\x00" * (32 - len(resp))
        return resp


class FakeAppctx:

    def get_resource(self, path):
        return os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../resources/base/", path)


all_mw = []


def prepare(qtbot, keyboard_json, combos=None, tap_dance=None):
    import hidraw as hid

    vk = VirtualKeyboard(keyboard_json, combos=combos, tap_dance=tap_dance)
    MockDevice.vk = vk

    hid.enumerate = mock_enumerate
    hid.device = MockDevice

    mw = MainWindow(FakeAppctx())
    qtbot.addWidget(mw)
    mw.show()
    # keep reference to MainWindow for the duration of tests
    # when MainWindow goes out of scope some KeyWidgets are still registered within KeycodeDisplay which causes UaF
    all_mw.append(mw)

    return mw, vk


def test_gui_startup(qtbot):
    mw, vk = prepare(qtbot, FAKE_KEYBOARD)
    assert mw.combobox_devices.currentText() == "Vial Testing Ltd Test Keyboard"
    assert mw.combobox_devices.count() == 1


def test_about_keyboard(qtbot):
    mw, vk = prepare(qtbot, FAKE_KEYBOARD)

    mw.about_menu.actions()[0].trigger()
    assert mw.about_dialog.windowTitle() == "About Vial Testing Ltd Test Keyboard"
    assert mw.about_dialog.textarea.toPlainText() == ('Manufacturer: Vial Testing Ltd\n'
         'Product: Test Keyboard\n'
         'VID: DEAD\n'
         'PID: BEEF\n'
         'Device: /magic/path/for/tests\n'
         '\n'
         'VIA protocol: 9\n'
         'Vial protocol: 6\n'
         'Vial keyboard ID: F00DFACEDEADBEEF\n'
         '\n'
         'Macro entries: 8\n'
         'Macro memory: 512 bytes\n'
         'Macro delays: yes\n'
         'Complex (2-byte) macro keycodes: yes\n'
         '\n'
         'Tap Dance entries: unsupported - disabled in firmware\n'
         'Combo entries: unsupported - disabled in firmware\n'
         'Key Override entries: unsupported - disabled in firmware\n'
         'Alt Repeat Key entries: unsupported - disabled in firmware\n'
         'Caps Word: yes\n'
         'Layer Lock: yes\n'
         '\n'
         'QMK Settings: disabled in firmware\n')
    mw.about_dialog.accept()


def test_key_change(qtbot):
    """ Tests changing keys in a keymap """
    mw, vk = prepare(qtbot, FAKE_KEYBOARD)

    # nothing should be selected yet in the keyboard display
    assert mw.keymap_editor.container.active_key is None

    # initial keycode must be KC_NO
    assert vk.keymap[0][0][0] == 0

    # clicking on first key must activate it
    point = mw.keymap_editor.container.widgets[0].bbox[0]
    qtbot.mouseClick(mw.keymap_editor.container, qt_api.QtCore.Qt.MouseButton.LeftButton,
                     pos=QPoint(int(point.x()), int(point.y())))

    assert mw.keymap_editor.container.active_key == mw.keymap_editor.container.widgets[0]

    ak = mw.keymap_editor.tabbed_keycodes.all_keycodes
    bk = mw.keymap_editor.tabbed_keycodes.basic_keycodes

    # at this point we can select all keycodes so basic should be hidden
    assert ak.isVisible()
    assert not bk.isVisible()

    # change current key to B
    assert ak.currentIndex() == 0
    assert ak.tabText(ak.currentIndex()) == "Basic"
    btn = ak.widget(0).layout.itemAt(3).widget().buttons[3]
    assert btn.text == "B"
    qtbot.mouseClick(btn, qt_api.QtCore.Qt.MouseButton.LeftButton)

    # check the new keycode is KC_B
    assert vk.keymap[0][0][0] == 5

    # check that we moved to the next key after setting the first key
    assert mw.keymap_editor.container.active_key == mw.keymap_editor.container.widgets[1]

    def find_key_btn(start, text):
        for w in start.findChildren(SquareButton):
            if w.isVisible() and w.text == text:
                return w
        raise RuntimeError("cannot find a visible key button with text='{}'".format(text))

    # switch to the Quantum tab
    ak.setCurrentIndex(3)
    assert ak.tabText(ak.currentIndex()) == "Quantum"

    # change current key to a masked LCTL()
    btn = find_key_btn(ak, "LCtl\n(kc)")
    qtbot.mouseClick(btn, qt_api.QtCore.Qt.MouseButton.LeftButton)

    # check the new keycode is LCTL()
    assert vk.keymap[0][0][1] == 0x100

    # check that we moved to the next key after setting the second key
    assert mw.keymap_editor.container.active_key == mw.keymap_editor.container.widgets[2]

    # click back on the second key
    point = mw.keymap_editor.container.widgets[1].bbox[0]
    qtbot.mouseClick(mw.keymap_editor.container, qt_api.QtCore.Qt.MouseButton.LeftButton,
                     pos=QPoint(int(point.x()), int(point.y())))

    # check that we have the second key selected & it's not a mask
    assert mw.keymap_editor.container.active_key == mw.keymap_editor.container.widgets[1]
    assert not mw.keymap_editor.container.active_mask

    # click on the mask now by manually calculating somewhere within last 4/5th Y, midpoint X
    bbox = mw.keymap_editor.container.widgets[1].bbox
    min_x = min(p.x() for p in bbox)
    max_x = max(p.x() for p in bbox)
    min_y = min(p.y() for p in bbox)
    max_y = max(p.y() for p in bbox)
    qtbot.mouseClick(mw.keymap_editor.container, qt_api.QtCore.Qt.MouseButton.LeftButton,
                     pos=QPoint(int((min_x + max_x) / 2), int(min_y + (max_y - min_y) * 4/5)))
    # now we must have the inner selected on the same key
    assert mw.keymap_editor.container.active_key == mw.keymap_editor.container.widgets[1]
    assert mw.keymap_editor.container.active_mask

    # now only basic keys should be settable
    assert not ak.isVisible()
    assert bk.isVisible()

    # let's set key C
    btn = find_key_btn(bk, "C")
    qtbot.mouseClick(btn, qt_api.QtCore.Qt.MouseButton.LeftButton)

    # check the new keycode is LCTL(KC_C)
    assert vk.keymap[0][0][1] == 0x106

    # and we should have moved to the next key, setting the full key and not the inner
    assert mw.keymap_editor.container.active_key == mw.keymap_editor.container.widgets[2]
    assert not mw.keymap_editor.container.active_mask
    assert ak.isVisible()
    assert not bk.isVisible()


def test_keymap_zoom(qtbot):
    """ Tests zooming keymap in/out using +/- keys """
    mw, vk = prepare(qtbot, FAKE_KEYBOARD)

    btn_plus = mw.keymap_editor.layout_size.itemAt(0).widget()
    btn_minus = mw.keymap_editor.layout_size.itemAt(1).widget()
    # TODO: resolve this field collision, +/- are SquareButton which overrides text
    assert QPushButton.text(btn_plus) == "+"
    assert QPushButton.text(btn_minus) == "-"

    # grab area for first widget
    scale_initial = mw.keymap_editor.container.scale

    # click the plus button
    qtbot.mouseClick(btn_plus, qt_api.QtCore.Qt.MouseButton.LeftButton)
    # area got bigger
    assert mw.keymap_editor.container.scale > scale_initial

    # click the minus button
    qtbot.mouseClick(btn_minus, qt_api.QtCore.Qt.MouseButton.LeftButton)
    # area back to the initial
    assert abs(mw.keymap_editor.container.scale - scale_initial) < 0.01

    # click the minus button
    qtbot.mouseClick(btn_minus, qt_api.QtCore.Qt.MouseButton.LeftButton)
    # area got smaller
    assert mw.keymap_editor.container.scale < scale_initial


def find_key_btn(start, text):
    for w in start.findChildren(SquareButton):
        if w.isVisible() and w.text == text:
            return w
    raise RuntimeError("cannot find a visible key button with text='{}'".format(text))


def test_layer_switch(qtbot):
    """ Tests setting keycodes across different layers """
    mw, vk = prepare(qtbot, FAKE_KEYBOARD)

    ak = mw.keymap_editor.tabbed_keycodes.all_keycodes
    bk = mw.keymap_editor.tabbed_keycodes.basic_keycodes
    c = mw.keymap_editor.container

    # initial keycode must be KC_NO
    assert vk.keymap[0][0][0] == 0

    # clicking on first key must activate it
    point = c.widgets[0].bbox[0]
    qtbot.mouseClick(c, qt_api.QtCore.Qt.MouseButton.LeftButton,
                     pos=QPoint(int(point.x()), int(point.y())))
    assert c.active_key == c.widgets[0]

    # change current key to Z
    qtbot.mouseClick(find_key_btn(ak, "Z"), qt_api.QtCore.Qt.MouseButton.LeftButton)
    assert vk.keymap[0][0][0] == 0x1D
    assert vk.keymap[1][0][0] == 0

    # make sure display for the widget now says Z
    assert c.widgets[0].text == "Z"
    # and that the next key is selected
    assert c.active_key == c.widgets[1]
    assert not c.active_mask

    # go to layer 1
    btn_layer_0 = mw.keymap_editor.layer_buttons[0]
    btn_layer_1 = mw.keymap_editor.layer_buttons[1]
    # TODO: resolve this field collision, +/- are SquareButton which overrides text
    assert QPushButton.text(btn_layer_0) == "0"
    assert QPushButton.text(btn_layer_1) == "1"

    qtbot.mouseClick(btn_layer_1, qt_api.QtCore.Qt.MouseButton.LeftButton)
    # check the current key got deselected
    assert c.active_key is None
    assert not c.active_mask

    # check the widget now displays layer 1 data, i.e. empty string as it's not set yet
    assert c.widgets[0].text == ""

    # click the key again
    qtbot.mouseClick(c, qt_api.QtCore.Qt.MouseButton.LeftButton,
                     pos=QPoint(int(point.x()), int(point.y())))
    assert c.active_key == c.widgets[0]

    # change current key to Y
    qtbot.mouseClick(find_key_btn(ak, "Y"), qt_api.QtCore.Qt.MouseButton.LeftButton)
    assert vk.keymap[0][0][0] == 0x1D
    assert vk.keymap[1][0][0] == 0x1C

    # make sure display for the widget now says Y
    assert c.widgets[0].text == "Y"

    # go back to the layer 0 and make sure the button got redrawn to Z
    qtbot.mouseClick(btn_layer_0, qt_api.QtCore.Qt.MouseButton.LeftButton)
    assert c.widgets[0].text == "Z"


def test_combos(qtbot):
    from widgets.key_widget import KeyWidget

    """ Tests setting combo keycodes """
    mw, vk = prepare(qtbot, FAKE_KEYBOARD, combos=[[0, 0, 0, 0, 0], [4, 5, 6, 7, 8], [0, 0x106, 0, 0, 0]])

    combos = None
    for x in range(mw.tabs.count()):
        if mw.tabs.tabText(x) == "Combos":
            combos = mw.tabs.widget(x).editor

    assert combos is not None, "could not find the combos tab"
    ct = combos.tabs

    tabs = []
    for x in range(ct.count()):
        tabs.append(ct.tabText(x))
    assert tabs == ["1", "2", "3"]

    def check_tab(idx, keys):
        ct.setCurrentIndex(idx)
        assert ct.tabText(ct.currentIndex()) == str(idx + 1)
        w = ct.widget(ct.currentIndex()).findChildren(KeyWidget)
        assert len(w) == 5
        for x in range(5):
            assert w[x].keycode == keys[x], "unexpected keycode at tab {} position {}: {} vs {}".format(idx, x, w[x].keycode, keys[x])

    check_tab(0, ["KC_NO", "KC_NO", "KC_NO", "KC_NO", "KC_NO"])
    check_tab(1, ["KC_A", "KC_B", "KC_C", "KC_D", "KC_E"])
    check_tab(2, ["KC_NO", "LCTL(KC_C)", "KC_NO", "KC_NO", "KC_NO"])

    # ok now still on tab index 2, let's switch some combos
    # change "Key 1" to "A"
    assert not mw.tray_keycodes.isVisible()
    w = ct.widget(ct.currentIndex()).findChildren(KeyWidget)
    bbox = w[0].widgets[0].bbox
    min_x = min(p.x() for p in bbox)
    max_x = max(p.x() for p in bbox)
    min_y = min(p.y() for p in bbox)
    max_y = max(p.y() for p in bbox)
    pos_mask = QPoint(int((min_x + max_x) / 2), int(min_y + (max_y - min_y) * 4/5))
    pos = QPoint(bbox[0].x(), bbox[0].y())
    qtbot.mouseClick(w[0], qt_api.QtCore.Qt.MouseButton.LeftButton, pos=pos)
    assert mw.tray_keycodes.isVisible()

    qtbot.mouseClick(find_key_btn(mw.tray_keycodes, "A"), qt_api.QtCore.Qt.MouseButton.LeftButton)
    assert vk.combos[2] == (4, 0x106, 0, 0, 0)

    # change "Output key" to "B"
    qtbot.mouseClick(w[4], qt_api.QtCore.Qt.MouseButton.LeftButton, pos=pos)
    qtbot.mouseClick(find_key_btn(mw.tray_keycodes, "B"), qt_api.QtCore.Qt.MouseButton.LeftButton)
    assert vk.combos[2] == (4, 0x106, 0, 0, 5)

    ak = mw.tray_keycodes.all_keycodes
    bk = mw.tray_keycodes.basic_keycodes

    # change "Key 4" to LSft(D)
    # first set up LSft(kc)
    qtbot.mouseClick(w[3], qt_api.QtCore.Qt.MouseButton.LeftButton, pos=pos)
    assert ak.isVisible()
    assert not bk.isVisible()
    ak.setCurrentIndex(3)
    assert ak.tabText(ak.currentIndex()) == "Quantum"
    qtbot.mouseClick(find_key_btn(mw.tray_keycodes, "LSft\n(kc)"), qt_api.QtCore.Qt.MouseButton.LeftButton)
    assert vk.combos[2] == (4, 0x106, 0, 0x200, 5)
    # now click the mask and set up D inside
    qtbot.mouseClick(w[3], qt_api.QtCore.Qt.MouseButton.LeftButton, pos=pos_mask)
    assert not ak.isVisible()
    assert bk.isVisible()
    qtbot.mouseClick(find_key_btn(mw.tray_keycodes, "D"), qt_api.QtCore.Qt.MouseButton.LeftButton)
    assert vk.combos[2] == (4, 0x106, 0, 0x207, 5)

    # change "Key 2" to E
    qtbot.mouseClick(w[1], qt_api.QtCore.Qt.MouseButton.LeftButton, pos=pos)
    assert ak.isVisible()
    assert not bk.isVisible()
    ak.setCurrentIndex(0)
    qtbot.mouseClick(find_key_btn(mw.tray_keycodes, "E"), qt_api.QtCore.Qt.MouseButton.LeftButton)
    assert vk.combos[2] == (4, 8, 0, 0x207, 5)

    # check the final result in the gui as well
    check_tab(2, ["KC_A", "KC_E", "KC_NO", "LSFT(KC_D)", "KC_B"])

    # TODO: a future unit test should check switching between multiple keyboards with different number of combos


def test_tap_dance(qtbot):
    from widgets.key_widget import KeyWidget
    from PyQt5.QtWidgets import QSpinBox

    mw, vk = prepare(qtbot, FAKE_KEYBOARD, tap_dance=[[0, 0, 0, 0, 200], [4, 5, 6, 7, 200], [0, 0x106, 0, 0, 500]])

    # TODO: a future unit test should check switching between multiple keyboards with different number of tap dances

    tde = None
    for x in range(mw.tabs.count()):
        if mw.tabs.tabText(x) == "Tap Dance":
            tde = mw.tabs.widget(x).editor

    assert tde is not None, "could not find the combos tab"
    td = tde.tabs

    tabs = []
    for x in range(td.count()):
        tabs.append(td.tabText(x))
    assert tabs == ["0", "1", "2"]

    def check_tab(idx, keys, timeout):
        td.setCurrentIndex(idx)
        assert td.tabText(td.currentIndex()) == str(idx)
        w = td.widget(td.currentIndex()).findChildren(KeyWidget)
        assert len(w) == 4
        for x in range(4):
            assert w[x].keycode == keys[x], "unexpected keycode at tab {} position {}: {} vs {}".format(idx, x, w[x].keycode, keys[x])
        timeout_w = td.widget(td.currentIndex()).findChildren(QSpinBox)[0]
        assert timeout_w.value() == timeout

    check_tab(0, ["KC_NO", "KC_NO", "KC_NO", "KC_NO"], 200)
    check_tab(1, ["KC_A", "KC_B", "KC_C", "KC_D"], 200)
    check_tab(2, ["KC_NO", "LCTL(KC_C)", "KC_NO", "KC_NO"], 500)

    # ok now still on tab index 2, let's switch the tap dance
    # change "Key 1" to "A"
    assert not mw.tray_keycodes.isVisible()
    w = td.widget(td.currentIndex()).findChildren(KeyWidget)
    bbox = w[0].widgets[0].bbox
    min_x = min(p.x() for p in bbox)
    max_x = max(p.x() for p in bbox)
    min_y = min(p.y() for p in bbox)
    max_y = max(p.y() for p in bbox)
    pos_mask = QPoint(int((min_x + max_x) / 2), int(min_y + (max_y - min_y) * 4/5))
    pos = QPoint(bbox[0].x(), bbox[0].y())
    qtbot.mouseClick(w[0], qt_api.QtCore.Qt.MouseButton.LeftButton, pos=pos)
    assert mw.tray_keycodes.isVisible()

    # note that for the tap dance the keycode change is immediate but not the timeout change
    qtbot.mouseClick(find_key_btn(mw.tray_keycodes, "A"), qt_api.QtCore.Qt.MouseButton.LeftButton)
    assert vk.tap_dance[2] == (4, 0x106, 0, 0, 500)

    timeout_w = td.widget(td.currentIndex()).findChildren(QSpinBox)[0]
    timeout_w.setValue(123)
    assert vk.tap_dance[2] == (4, 0x106, 0, 0, 500)

    # check that we are adding * to the tab text when there are pending changes
    assert td.tabText(td.currentIndex()) == "2*"
    timeout_w.setValue(500)
    assert td.tabText(td.currentIndex()) == "2"

    # ok commit the change now
    timeout_w.setValue(123)
    assert td.tabText(td.currentIndex()) == "2*"
    qtbot.mouseClick(tde.btn_save, qt_api.QtCore.Qt.MouseButton.LeftButton)
    assert td.tabText(td.currentIndex()) == "2"
    assert vk.tap_dance[2] == (4, 0x106, 0, 0, 123)

    # let's check that reverting works
    assert not tde.btn_save.isEnabled()
    timeout_w.setValue(321)
    assert tde.btn_save.isEnabled()
    assert td.tabText(td.currentIndex()) == "2*"

    qtbot.mouseClick(tde.btn_revert, qt_api.QtCore.Qt.MouseButton.LeftButton)
    assert not tde.btn_save.isEnabled()
    assert td.tabText(td.currentIndex()) == "2"
    assert timeout_w.value() == 123
