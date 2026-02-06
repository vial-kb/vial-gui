# SPDX-License-Identifier: GPL-2.0-or-later
import json
import os
import sys
import tempfile
import types
import unittest
from unittest.mock import patch, MagicMock


# cli.py must be importable without Qt — do this before importing cli
# so the headless unlocker doesn't fight with test-time imports
sys.modules.setdefault("unlocker", types.ModuleType("unlocker"))

# Inject a minimal vial_device module so discover_device's isinstance check
# works without pulling in the real import chain (hidraw, simpleeval, etc.)
# Stub native modules that aren't available in a bare test environment
# hidraw: C extension from vial-kb hidapi fork, needed by util_base → hidproxy
if "hidraw" not in sys.modules:
    _hidraw = types.ModuleType("hidraw")
    _hidraw.device = MagicMock
    _hidraw.enumerate = lambda: []
    sys.modules["hidraw"] = _hidraw

if "vial_device" not in sys.modules:
    _vd = types.ModuleType("vial_device")

    class _VialKeyboard:
        pass

    class _VialBootloader:
        pass

    class _VialDummyKeyboard(_VialKeyboard):
        pass

    _vd.VialKeyboard = _VialKeyboard
    _vd.VialBootloader = _VialBootloader
    _vd.VialDummyKeyboard = _VialDummyKeyboard
    sys.modules["vial_device"] = _vd

from vial_device import VialKeyboard as _BaseVialKeyboard

from cli import install_headless_unlocker, discover_device


class FakeKeyboard:
    def __init__(self, name="Test KB", keyboard_id=0):
        self.keyboard_id = keyboard_id
        self._name = name
        self.restored_data = None

    def title(self):
        return self._name

    def save_layout(self):
        return json.dumps({"version": 1, "uid": self.keyboard_id}).encode("utf-8")

    def restore_layout(self, data):
        self.restored_data = data


class FakeDevice(_BaseVialKeyboard):
    """Minimal stand-in for VialKeyboard. Inherits from the injected
    VialKeyboard stub so isinstance checks in discover_device pass."""

    def __init__(self, name="Test KB", keyboard_id=0):
        self.keyboard = FakeKeyboard(name, keyboard_id)
        self._name = name
        self._opened = False
        self._closed = False

    def title(self):
        return self._name

    def open(self, override_json=None):
        self._opened = True

    def close(self):
        self._closed = True


class TestHeadlessUnlocker(unittest.TestCase):

    def test_installs_into_sys_modules(self):
        """install_headless_unlocker should inject an unlocker module with an Unlocker class."""
        old = sys.modules.pop("unlocker", None)
        try:
            install_headless_unlocker()
            mod = sys.modules["unlocker"]
            self.assertTrue(hasattr(mod, "Unlocker"))
            self.assertTrue(hasattr(mod.Unlocker, "unlock"))
        finally:
            if old is not None:
                sys.modules["unlocker"] = old

    def test_already_unlocked(self):
        """If keyboard reports unlocked, HeadlessUnlocker.unlock returns True immediately."""
        install_headless_unlocker()
        Unlocker = sys.modules["unlocker"].Unlocker

        kb = MagicMock()
        kb.get_unlock_status.return_value = 1
        self.assertTrue(Unlocker.unlock(kb))
        kb.unlock_start.assert_not_called()

    def test_no_unlock_keys(self):
        """If keyboard needs unlock but reports no keys, returns False."""
        install_headless_unlocker()
        Unlocker = sys.modules["unlocker"].Unlocker

        kb = MagicMock()
        kb.get_unlock_status.return_value = 0
        kb.get_unlock_keys.return_value = []
        self.assertFalse(Unlocker.unlock(kb))

    def test_unlock_polls_until_done(self):
        """HeadlessUnlocker should poll until the keyboard reports unlocked."""
        install_headless_unlocker()
        Unlocker = sys.modules["unlocker"].Unlocker

        kb = MagicMock()
        kb.get_unlock_status.return_value = 0
        kb.get_unlock_keys.return_value = [(0, 0), (1, 1)]
        # First two polls: still locked. Third: unlocked.
        kb.unlock_poll.side_effect = [
            bytes([0, 0, 2]),
            bytes([0, 0, 1]),
            bytes([1, 0, 0]),
        ]

        with patch("time.sleep"):
            result = Unlocker.unlock(kb)

        self.assertTrue(result)
        self.assertEqual(kb.unlock_poll.call_count, 3)
        kb.unlock_start.assert_called_once()


class TestUidComparison(unittest.TestCase):
    """Test the float64 precision workaround for UID comparison."""

    def test_exact_match(self):
        self.assertEqual(float(12345), float(12345))

    def test_float64_precision_loss_matches(self):
        """UIDs that differ only due to JSON float64 rounding should be equal."""
        # These are the actual values from the bug report
        vil_uid = 8834422349245467000   # after JSON round-trip through JS
        kb_uid = 8834422349245466982    # raw from USB
        self.assertEqual(float(vil_uid), float(kb_uid))

    def test_genuinely_different_uids(self):
        """UIDs from different keyboards should not match."""
        self.assertNotEqual(float(1234567890), float(9876543210))


class TestDiscoverDevice(unittest.TestCase):

    def _make_devices(self, count):
        return [FakeDevice(f"Keyboard {i}", keyboard_id=i) for i in range(count)]

    @patch("util_base.find_vial_devices")
    def test_no_devices_exits(self, mock_find):
        """Should exit with code 1 when no keyboards are found."""
        mock_find.return_value = []
        with self.assertRaises(SystemExit) as ctx:
            discover_device()
        self.assertEqual(ctx.exception.code, 1)

    @patch("util_base.find_vial_devices")
    def test_single_device_returned(self, mock_find):
        """Should return the device when exactly one is found."""
        devices = self._make_devices(1)
        mock_find.return_value = devices
        result = discover_device()
        self.assertIs(result, devices[0])

    @patch("util_base.find_vial_devices")
    def test_single_device_wrong_index(self, mock_find):
        """Should exit if --device index is out of range with one keyboard."""
        mock_find.return_value = self._make_devices(1)
        with self.assertRaises(SystemExit):
            discover_device(device_index=1)

    @patch("util_base.find_vial_devices")
    def test_multiple_devices_no_index_exits(self, mock_find):
        """Should exit and list devices when multiple found without --device."""
        mock_find.return_value = self._make_devices(3)
        with self.assertRaises(SystemExit) as ctx:
            discover_device()
        self.assertEqual(ctx.exception.code, 1)

    @patch("util_base.find_vial_devices")
    def test_multiple_devices_valid_index(self, mock_find):
        """Should return the selected device when --device is valid."""
        devices = self._make_devices(3)
        mock_find.return_value = devices
        result = discover_device(device_index=1)
        self.assertIs(result, devices[1])

    @patch("util_base.find_vial_devices")
    def test_multiple_devices_bad_index_exits(self, mock_find):
        """Should exit if --device index exceeds available keyboards."""
        mock_find.return_value = self._make_devices(2)
        with self.assertRaises(SystemExit):
            discover_device(device_index=5)


class TestCmdUpload(unittest.TestCase):

    def _make_args(self, filepath, device=None, force=False):
        args = MagicMock()
        args.file = filepath
        args.device = device
        args.force = force
        return args

    def test_missing_file_exits(self):
        from cli import cmd_upload
        args = self._make_args("/nonexistent/file.vil")
        with self.assertRaises(SystemExit):
            cmd_upload(args)

    def test_invalid_json_exits(self):
        from cli import cmd_upload
        with tempfile.NamedTemporaryFile(suffix=".vil", delete=False) as f:
            f.write(b"this is not json")
            f.flush()
            args = self._make_args(f.name)
            try:
                with self.assertRaises(SystemExit):
                    cmd_upload(args)
            finally:
                os.unlink(f.name)

    @patch("cli.discover_device")
    def test_uid_mismatch_without_force_exits(self, mock_discover):
        from cli import cmd_upload

        device = FakeDevice("Test KB", keyboard_id=999)
        device.open()
        mock_discover.return_value = device

        vil = json.dumps({"version": 1, "uid": 12345}).encode("utf-8")
        with tempfile.NamedTemporaryFile(suffix=".vil", delete=False) as f:
            f.write(vil)
            f.flush()
            args = self._make_args(f.name, force=False)
            try:
                with self.assertRaises(SystemExit):
                    cmd_upload(args)
            finally:
                os.unlink(f.name)

    @patch("cli.discover_device")
    def test_uid_mismatch_with_force_succeeds(self, mock_discover):
        from cli import cmd_upload

        device = FakeDevice("Test KB", keyboard_id=999)
        mock_discover.return_value = device

        vil = json.dumps({"version": 1, "uid": 12345, "layout": [],
                          "encoder_layout": [], "layout_options": -1,
                          "vial_protocol": 6, "via_protocol": 9}).encode("utf-8")
        with tempfile.NamedTemporaryFile(suffix=".vil", delete=False) as f:
            f.write(vil)
            f.flush()
            args = self._make_args(f.name, force=True)
            try:
                cmd_upload(args)
                self.assertTrue(device._opened)
                self.assertTrue(device._closed)
                self.assertEqual(device.keyboard.restored_data, vil)
            finally:
                os.unlink(f.name)

    @patch("cli.discover_device")
    def test_uid_float64_match_succeeds(self, mock_discover):
        """UIDs that match after float64 rounding should not require --force."""
        from cli import cmd_upload

        # These differ as int64 but are equal as float64
        kb_uid = 8834422349245466982
        vil_uid = 8834422349245467000

        device = FakeDevice("Test KB", keyboard_id=kb_uid)
        mock_discover.return_value = device

        vil = json.dumps({"version": 1, "uid": vil_uid, "layout": [],
                          "encoder_layout": [], "layout_options": -1,
                          "vial_protocol": 6, "via_protocol": 9}).encode("utf-8")
        with tempfile.NamedTemporaryFile(suffix=".vil", delete=False) as f:
            f.write(vil)
            f.flush()
            args = self._make_args(f.name, force=False)
            try:
                cmd_upload(args)
                self.assertEqual(device.keyboard.restored_data, vil)
            finally:
                os.unlink(f.name)


class TestCmdDownload(unittest.TestCase):

    @patch("cli.discover_device")
    def test_download_writes_file(self, mock_discover):
        from cli import cmd_download

        device = FakeDevice("Test KB", keyboard_id=42)
        mock_discover.return_value = device

        with tempfile.NamedTemporaryFile(suffix=".vil", delete=False) as f:
            args = MagicMock()
            args.file = f.name
            args.device = None
            try:
                cmd_download(args)
                with open(f.name, "rb") as out:
                    data = json.loads(out.read())
                self.assertEqual(data["uid"], 42)
                self.assertTrue(device._opened)
                self.assertTrue(device._closed)
            finally:
                os.unlink(f.name)


class TestCliQtFree(unittest.TestCase):
    """cli.py must be importable without PyQt5."""

    def test_no_toplevel_qt_imports(self):
        import ast
        cli_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "cli.py")
        with open(cli_path) as f:
            tree = ast.parse(f.read(), filename="cli.py")
        violations = []
        for node in ast.walk(tree):
            if not isinstance(node, (ast.Import, ast.ImportFrom)):
                continue
            if node.col_offset != 0:
                continue
            module = getattr(node, "module", "") or ""
            names = [a.name for a in node.names]
            combined = module + " " + " ".join(names)
            if "PyQt5" in combined or "Qt" in combined:
                violations.append(f"cli.py:{node.lineno} - {combined.strip()}")
        self.assertEqual(violations, [],
                         "Top-level Qt imports found in cli.py:\n" + "\n".join(violations))
