#!/bin/bash

set -e

VER=$1
DST=$2

pushd $DST

unzip vial-linux.zip
rm vial-linux.zip
mv Vial-x86_64.AppImage Vial-v$VER-x86_64.AppImage

unzip vial-mac.zip
rm vial-mac.zip
mv vial-mac.dmg Vial-v$VER.dmg

unzip vial-win-installer.zip
rm vial-win-installer.zip
mv VialSetup.exe Vial-v$VER-setup.exe

mv vial-win.zip vial-win2.zip
unzip vial-win2.zip
rm vial-win2.zip
mv vial-win.zip Vial-v$VER-portable.zip

popd

echo "All OK"
