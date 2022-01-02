import atheris
import sys

sys.path.append("src/main/python")

with atheris.instrument_imports():
    from protocol.macro import macro_deserialize_v1


def TestOneInput(data):
    macro_deserialize_v1(data)


atheris.Setup(sys.argv, TestOneInput)
atheris.Fuzz()
