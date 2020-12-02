# SPDX-License-Identifier: GPL-2.0-or-later

import sys


if sys.platform.startswith("linux"):
    import hidraw as hid
else:
    import hid
