import hid

VIAL_SERIAL_NUMBER_MAGIC = "vial:f64c2b3c"

def find_vial_keyboards():
    for dev in hid.enumerate():
        print(dev)
