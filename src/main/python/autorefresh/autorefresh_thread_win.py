import time
import win32gui, win32con, win32api
import win32gui_struct

from autorefresh.autorefresh_thread import AutorefreshThread


GUID_DEVINTERFACE_USB_DEVICE = "{A5DCBF10-6530-11D2-901F-00C04FB951ED}"
GUID_DEVINTERFACE_HID_DEVICE = "{4D1E55B2-F16F-11CF-88CB-001111000030}"
DEVICE_NOTIFY_ALL_INTERFACE_CLASSES = 4

g_device_changes = 0


def device_changed(hwnd, msg, wp, lp):
    global g_device_changes
    if wp in [win32con.DBT_DEVICEARRIVAL, win32con.DBT_DEVICEREMOVECOMPLETE]:
        g_device_changes += 1


class AutorefreshThreadWin(AutorefreshThread):

    def run(self):
        global g_device_changes

        # code based on:
        # - https://github.com/libsdl-org/SDL/blob/7b3449b89f0625e4603f5d8681e2bac1f51a9386/src/hidapi/SDL_hidapi.c
        # - https://github.com/vmware-archive/salt-windows-install/blob/master/deps/salt/python/App/Lib/site-packages/win32/Demos/win32gui_devicenotify.py
        wc = win32gui.WNDCLASS()
        wc.hInstance = win32api.GetModuleHandle(None)
        wc.lpszClassName = "VIAL_DEVICE_DETECTION"
        wc.lpfnWndProc = { win32con.WM_DEVICECHANGE: device_changed }
        class_atom = win32gui.RegisterClass(wc)
        hwnd = win32gui.CreateWindowEx(0, "VIAL_DEVICE_DETECTION", None, 0, 0, 0, 0, 0, win32con.HWND_MESSAGE, None, None, None)

        hdev = win32gui.RegisterDeviceNotification(
            hwnd,
            win32gui_struct.PackDEV_BROADCAST_DEVICEINTERFACE(GUID_DEVINTERFACE_HID_DEVICE),
            win32con.DEVICE_NOTIFY_WINDOW_HANDLE | DEVICE_NOTIFY_ALL_INTERFACE_CLASSES
        )

        while True:
            for x in range(100):
                win32gui.PumpWaitingMessages()
                time.sleep(0.01)

            if g_device_changes > 0:
                g_device_changes = 0
                self.update()