import sys
import types

if "hidraw" not in sys.modules:
    sys.modules["hidraw"] = types.ModuleType("hidraw")
