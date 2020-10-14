REPORT_LEN = 32

def hid_send(dev, msg):
    if len(report) > REPORT_LEN:
        raise RuntimeError("report must be less than 64 bytes")
    msg += b"\x00" * (REPORT_LEN - len(msg))

    # add 00 at start for hidapi report id
    dev.write(b"\x00" + report)

    return dev.read(REPORT_LEN)
