import threading
import time

from PyQt5.QtCore import QThread

import hidproxy
from autorefresh.autorefresh import Autorefresh
from util import find_vial_devices


class EnumerateRecorder:
    """ Stand-in for hid.enumerate that tracks how many threads are inside it at once """

    def __init__(self, delay=0.0):
        self.delay = delay
        self.guard = threading.Lock()
        self.active = 0
        self.max_active = 0
        self.calls = []
        self.qthreads = []

    def __call__(self):
        with self.guard:
            self.active += 1
            self.max_active = max(self.max_active, self.active)
            self.calls.append(threading.get_ident())
            self.qthreads.append(QThread.currentThread())
        time.sleep(self.delay)
        with self.guard:
            self.active -= 1
        return []


def test_find_vial_devices_serializes_enumerate():
    # macOS hidapi keeps one global IOHIDManager; enumerating from two threads at once
    # schedules it on two run loops and aborts the process
    recorder = EnumerateRecorder(delay=0.05)
    hidproxy.hid.enumerate = recorder

    threads = [threading.Thread(target=find_vial_devices, args=({"definitions": {}},)) for _ in range(4)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    # >= because polling threads left over from earlier GUI tests may also call in
    assert len(recorder.calls) >= 4
    assert recorder.max_active == 1


def test_autorefresh_does_not_poll_before_start(qtbot):
    # the polling thread never stops, so the stub is installed permanently rather than via monkeypatch,
    # otherwise teardown would hand the real hid backend to an orphaned thread
    recorder = EnumerateRecorder()
    hidproxy.hid.enumerate = recorder

    autorefresh = Autorefresh()

    # polling threads left running by earlier tests also hit the stub; only count this instance's thread
    def polled_by_this_thread():
        with recorder.guard:
            return autorefresh.thread in recorder.qthreads

    qtbot.wait(300)
    assert not polled_by_this_thread(), "Autorefresh must not enumerate before the main thread's first refresh"

    autorefresh.start()
    qtbot.waitUntil(polled_by_this_thread, timeout=3000)
