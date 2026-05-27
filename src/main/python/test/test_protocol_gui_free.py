import ast
import os
import unittest


# Protocol chain: all modules that should be importable without PyQt5
PROTOCOL_CHAIN = [
    "protocol/keyboard_comm.py",
    "protocol/constants.py",
    "protocol/tap_dance.py",
    "protocol/combo.py",
    "protocol/key_override.py",
    "protocol/macro.py",
    "protocol/dynamic.py",
    "protocol/base_protocol.py",
    "protocol/alt_repeat_key.py",
    "keycodes/keycodes.py",
    "keycodes/keycodes_v5.py",
    "keycodes/keycodes_v6.py",
    "any_keycode.py",
    "vial_device.py",
    "kle_serial.py",
    "hidproxy.py",
    "util_base.py",
]

# Modules that pull in Qt and must only be imported lazily (inside functions)
GUI_MODULES = {"unlocker", "util", "macro.macro_action_ui", "editor.qmk_settings"}

SRC_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class TestProtocolGuiFree(unittest.TestCase):
    """Ensure the protocol layer can be imported without PyQt5."""

    def test_no_toplevel_qt_imports(self):
        """No file in the protocol chain should import PyQt5 at module level."""
        violations = []
        for relpath in PROTOCOL_CHAIN:
            filepath = os.path.join(SRC_DIR, relpath)
            if not os.path.exists(filepath):
                continue
            with open(filepath) as f:
                tree = ast.parse(f.read(), filename=relpath)
            for node in ast.walk(tree):
                if not isinstance(node, (ast.Import, ast.ImportFrom)):
                    continue
                if node.col_offset != 0:
                    continue  # inside a function = lazy, that's fine
                module = getattr(node, "module", "") or ""
                names = [a.name for a in node.names]
                combined = module + " " + " ".join(names)
                if "PyQt5" in combined or "Qt" in combined:
                    violations.append("{}:{} - {}".format(relpath, node.lineno, combined.strip()))
        self.assertEqual(violations, [], "Top-level Qt imports found in protocol chain:\n" + "\n".join(violations))

    def test_no_toplevel_gui_module_imports(self):
        """GUI-only modules (unlocker, util, macro_action_ui) must not be imported at top level."""
        violations = []
        for relpath in PROTOCOL_CHAIN:
            filepath = os.path.join(SRC_DIR, relpath)
            if not os.path.exists(filepath):
                continue
            with open(filepath) as f:
                tree = ast.parse(f.read(), filename=relpath)
            for node in ast.walk(tree):
                if not isinstance(node, (ast.Import, ast.ImportFrom)):
                    continue
                if node.col_offset != 0:
                    continue
                module = getattr(node, "module", "") or ""
                if module in GUI_MODULES or any(module.endswith("." + m) for m in GUI_MODULES):
                    violations.append("{}:{} - from {} import ...".format(relpath, node.lineno, module))
        self.assertEqual(violations, [], "Top-level GUI module imports found in protocol chain:\n" + "\n".join(violations))
