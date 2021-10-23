from PyQt5.QtCore import QTimer

from util import find_vial_devices


class Autorefresh:

    def __init__(self, mainwindow):
        self.mainwindow = mainwindow

        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(1000)

    def update(self, check_protocol=False):
        devices = find_vial_devices(self.mainwindow.via_stack_json, self.mainwindow.sideload_vid,
                                    self.mainwindow.sideload_pid, quiet=True, check_protocol=check_protocol)

        old_found = False
        old_path = False
        if self.mainwindow.current_device is not None:
            old_path = self.mainwindow.current_device.desc["path"]

        self.mainwindow.combobox_devices.blockSignals(True)

        self.mainwindow.combobox_devices.clear()
        self.mainwindow.devices = devices
        for dev in devices:
            self.mainwindow.combobox_devices.addItem(dev.title())
            if dev.desc["path"] == old_path:
                old_found = True
                self.mainwindow.combobox_devices.setCurrentIndex(self.mainwindow.combobox_devices.count() - 1)

        self.mainwindow.combobox_devices.blockSignals(False)

        if devices:
            self.mainwindow.lbl_no_devices.hide()
            self.mainwindow.tabs.show()
        else:
            self.mainwindow.lbl_no_devices.show()
            self.mainwindow.tabs.hide()

        if not old_found:
            self.mainwindow.on_device_selected()
