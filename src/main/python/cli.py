#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-or-later
"""
Headless CLI for uploading/downloading Vial keyboard configurations.

Usage:
    python cli.py upload <file.vil>     Upload a .vil layout to the keyboard
    python cli.py download <file.vil>   Download current layout from keyboard
"""

import argparse
import json
import logging
import os
import sys
import time
import types


def install_headless_unlocker():
    """Inject a headless Unlocker before any protocol code lazily imports it."""

    class HeadlessUnlocker:
        @classmethod
        def unlock(cls, keyboard):
            if keyboard.get_unlock_status() == 1:
                return True

            keys = keyboard.get_unlock_keys()
            if not keys:
                print("Keyboard requires unlock but reports no unlock keys.",
                      file=sys.stderr)
                return False

            print("Keyboard requires unlock. Hold these key positions simultaneously:")
            for row, col in keys:
                print(f"  Row {row}, Col {col}")
            print()

            keyboard.unlock_start()
            print("Waiting for unlock...", end="", flush=True)

            while True:
                data = keyboard.unlock_poll()
                unlocked = data[0]
                if unlocked == 1:
                    print(" done!")
                    return True
                print(".", end="", flush=True)
                time.sleep(0.2)

    mod = types.ModuleType("unlocker")
    mod.Unlocker = HeadlessUnlocker
    sys.modules["unlocker"] = mod


def init_qmk_settings():
    """Initialize QmkSettings with the resource path so settings (de)serialization works."""

    resource_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resources")
    settings_json = os.path.join(resource_dir, "qmk_settings.json")

    if not os.path.exists(settings_json):
        logging.debug("qmk_settings.json not found at %s, settings support disabled", settings_json)
        return

    from editor.qmk_settings import QmkSettings
    from collections import defaultdict

    QmkSettings.qsid_fields = defaultdict(list)
    with open(settings_json, "r") as f:
        QmkSettings.settings_defs = json.load(f)
    for tab in QmkSettings.settings_defs["tabs"]:
        for field in tab["fields"]:
            QmkSettings.qsid_fields[field["qsid"]].append(field)


def discover_device(device_index=None):
    """Find and return a single VialKeyboard, with helpful output for edge cases."""

    from util_base import find_vial_devices
    from vial_device import VialKeyboard

    devices = find_vial_devices({"definitions": {}}, quiet=True)
    keyboards = [d for d in devices if isinstance(d, VialKeyboard)]

    if len(keyboards) == 0:
        print("No Vial keyboards found.\n", file=sys.stderr)
        print("Troubleshooting:", file=sys.stderr)
        print("  - Is the keyboard plugged in?", file=sys.stderr)
        print("  - Does your user have HID access? (check udev rules)", file=sys.stderr)
        print("  - Is the firmware Vial-enabled?", file=sys.stderr)
        sys.exit(1)

    if len(keyboards) == 1:
        if device_index is not None and device_index != 0:
            print(f"Error: --device {device_index} out of range, only 1 keyboard found.",
                  file=sys.stderr)
            sys.exit(1)
        return keyboards[0]

    # Multiple keyboards
    if device_index is not None:
        if device_index < 0 or device_index >= len(keyboards):
            print(f"Error: --device {device_index} out of range (0-{len(keyboards) - 1})\n",
                  file=sys.stderr)
            for i, kb in enumerate(keyboards):
                print(f"  {i}: {kb.title()}", file=sys.stderr)
            sys.exit(1)
        return keyboards[device_index]

    print(f"Found {len(keyboards)} Vial keyboards. Use --device N to select one:\n",
          file=sys.stderr)
    for i, kb in enumerate(keyboards):
        print(f"  {i}: {kb.title()}", file=sys.stderr)
    print(file=sys.stderr)
    sys.exit(1)


def cmd_upload(args):
    """Upload a .vil file to the keyboard."""

    try:
        with open(args.file, "rb") as f:
            data = f.read()
    except FileNotFoundError:
        print(f"Error: File not found: {args.file}", file=sys.stderr)
        sys.exit(1)
    except IOError as e:
        print(f"Error reading {args.file}: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        vil_data = json.loads(data.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        print(f"Error: {args.file} is not a valid .vil file: {e}", file=sys.stderr)
        sys.exit(1)

    device = discover_device(args.device)
    print(f"Opening {device.title()}...")
    device.open()
    keyboard = device.keyboard

    # UID mismatch check (JSON int64 loses precision through float64 in JS/web UI)
    vil_uid = vil_data.get("uid")
    if float(vil_uid) != float(keyboard.keyboard_id):
        if not args.force:
            print(f"Error: Layout UID does not match keyboard.\n", file=sys.stderr)
            print(f"  Layout:   {vil_data.get('uid')}", file=sys.stderr)
            print(f"  Keyboard: {keyboard.keyboard_id}", file=sys.stderr)
            print(f"\nUse --force to upload anyway.", file=sys.stderr)
            device.close()
            sys.exit(1)
        print("Warning: Layout UID does not match keyboard, continuing with --force.")

    print(f"Uploading {args.file}...")
    keyboard.restore_layout(data)
    device.close()
    print("Done.")


def cmd_download(args):
    """Download current layout from the keyboard to a .vil file."""

    device = discover_device(args.device)
    print(f"Opening {device.title()}...")
    device.open()

    print("Reading layout...")
    data = device.keyboard.save_layout()
    device.close()

    with open(args.file, "wb") as f:
        f.write(data)

    print(f"Saved to {args.file}")


def main():
    parser = argparse.ArgumentParser(
        prog="vial-cli",
        description="Headless CLI for Vial keyboard configuration",
    )
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Enable debug logging")
    parser.add_argument("--device", type=int, default=None, metavar="N",
                        help="Select keyboard by index when multiple are connected")

    sub = parser.add_subparsers(dest="command")
    sub.required = True

    up = sub.add_parser("upload", help="Upload a .vil layout to the keyboard")
    up.add_argument("file", help="Path to .vil file to upload")
    up.add_argument("--force", action="store_true",
                    help="Upload even if layout UID doesn't match keyboard")

    dl = sub.add_parser("download", help="Download layout from keyboard to a file")
    dl.add_argument("file", help="Output path for .vil file")

    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.WARNING,
        format="%(levelname)s: %(message)s",
    )

    # Must happen before any protocol code imports unlocker
    install_headless_unlocker()
    init_qmk_settings()

    if args.command == "upload":
        cmd_upload(args)
    elif args.command == "download":
        cmd_download(args)


if __name__ == "__main__":
    main()
