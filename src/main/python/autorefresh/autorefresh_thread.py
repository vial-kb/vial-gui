import json
import time
import sys

if sys.platform == "emscripten":
    class RLock:
        def __enter__(self):
            pass
        def __exit__(self, *args):
            pass
else:
    from multiprocessing import RLock

from PyQt5.QtCore import pyqtSignal, QThread

from util import find_vial_devices


class AutorefreshThread(QThread):

    devices_updated = pyqtSignal(object, bool)

    def __init__(self):
        super().__init__()

        self.current_device = None
        self.devices = []
        self.locked = False
        self.mutex = RLock()

        self.sideload_json = None
        self.sideload_vid = self.sideload_pid = -1
        # create empty VIA definitions. Easier than setting it to none and handling a bunch of exceptions
        self.via_stack_json = {"definitions": {}}

    def run(self):
        while True:
            self.update()
            time.sleep(1)

    def lock(self):
        with self.mutex:
            self.locked = True

    def unlock(self):
        with self.mutex:
            self.locked = False

    # note that this method is called from both inside and outside of this thread
    def update(self, quiet=True, hard=False):
        # if lock()ed then just do nothing
        with self.mutex:
            if self.locked:
                return
            # can be modified out of mutex so create local copies here
            via_stack_json = self.via_stack_json
            sideload_vid = self.sideload_vid
            sideload_pid = self.sideload_pid

        # this can take a long (~seconds) time on Windows, so run outside of mutex
        # to make sure calling lock() and unlock() is instant
        new_devices = find_vial_devices(via_stack_json, sideload_vid, sideload_pid, quiet=quiet)

        # this is fast again but discard results if we got lock()ed in between
        with self.mutex:
            if self.locked:
                return

            # if the set of the devices didn't change at all, don't need to update the combobox
            old_paths = set(d.desc["path"] for d in self.devices)
            new_paths = set(d.desc["path"] for d in new_devices)
            if old_paths == new_paths and not hard:
                return

            # trigger update and report whether a hard-reload is needed (if current device went away)
            self.devices = new_devices
            old_path = "blank"
            if self.current_device is not None:
                old_path = self.current_device.desc["path"]

            self.devices_updated.emit(new_devices, (old_path not in new_paths) or hard)

    def load_dummy(self, data):
        with self.mutex:
            self.sideload_json = json.loads(data)
            self.sideload_vid = self.sideload_pid = 0
        self.update()

    def sideload_via_json(self, data):
        with self.mutex:
            self.sideload_json = json.loads(data)
            self.sideload_vid = int(self.sideload_json["vendorId"], 16)
            self.sideload_pid = int(self.sideload_json["productId"], 16)
        self.update()

    def load_via_stack(self, data):
        with self.mutex:
            self.via_stack_json = json.loads(data)

    def set_device(self, current_device):
        with self.mutex:
            self.current_device = current_device
