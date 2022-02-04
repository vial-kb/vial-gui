import json

from PyQt5.QtCore import QTimer, QObject, pyqtSignal

from keyboard_comm import ProtocolError
from util import find_vial_devices


class AutorefreshLocker:

    def __init__(self, autorefresh):
        self.autorefresh = autorefresh

    def __enter__(self):
        self.autorefresh._lock()

    def __exit__(self):
        self.autorefresh._unlock()


class Autorefresh(QObject):

    instance = None
    devices_updated = pyqtSignal(object, bool)

    def __init__(self):
        super().__init__()
        self.devices = []
        self.locked = False
        self.current_device = None

        self.sideload_json = None
        self.sideload_vid = self.sideload_pid = -1
        # create empty VIA definitions. Easier than setting it to none and handling a bunch of exceptions
        self.via_stack_json = {"definitions": {}}

        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(1000)

        Autorefresh.instance = self

    def update(self, check_protocol=False):
        if self.locked:
            return

        new_devices = find_vial_devices(self.via_stack_json, self.sideload_vid, self.sideload_pid,
                                        quiet=True, check_protocol=check_protocol)

        # if the set of the devices didn't change at all, don't need to update the combobox
        old_paths = set(d.desc["path"] for d in self.devices)
        new_paths = set(d.desc["path"] for d in new_devices)
        if old_paths == new_paths:
            return

        # trigger update and report whether a hard-reload is needed (if current device went away)
        self.devices = new_devices
        old_path = "blank"
        if self.current_device is not None:
            old_path = self.current_device.desc["path"]
        self.devices_updated.emit(new_devices, old_path not in new_paths)

    def _lock(self):
        self.locked = True

    def _unlock(self):
        self.locked = False

    @classmethod
    def lock(cls):
        return AutorefreshLocker(cls.instance)

    def load_dummy(self, data):
        self.sideload_json = json.loads(data)
        self.sideload_vid = self.sideload_pid = 0
        self.update()

    def sideload_via_json(self, data):
        self.sideload_json = json.loads(data)
        self.sideload_vid = int(self.sideload_json["vendorId"], 16)
        self.sideload_pid = int(self.sideload_json["productId"], 16)
        self.update()

    def load_via_stack(self, data):
        self.via_stack_json = json.loads(data)

    def select_device(self, idx):
        if self.current_device is not None:
            self.current_device.close()
        self.current_device = None
        if idx >= 0:
            self.current_device = self.devices[idx]

        if self.current_device is not None:
            if self.current_device.sideload:
                self.current_device.open(self.sideload_json)
            elif self.current_device.via_stack:
                self.current_device.open(self.via_stack_json["definitions"][self.current_device.via_id])
            else:
                self.current_device.open(None)
