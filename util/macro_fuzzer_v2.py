import atheris
import sys

sys.path.append("src/main/python")

with atheris.instrument_imports():
    from keyboard_comm import macro_deserialize_v2


def TestOneInput(data):
    macro_deserialize_v2(data)


atheris.Setup(sys.argv, TestOneInput)
atheris.Fuzz()
