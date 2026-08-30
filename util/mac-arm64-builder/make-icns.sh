#!/bin/bash
set -e

HERE=$(cd "$(dirname "$0")" && pwd)
ROOT=$(cd "$HERE/../.." && pwd)

BASE="$ROOT/src/main/icons/base"
MAC="$ROOT/src/main/icons/mac"
ICONSET="$ROOT/build/Vial.iconset"

rm -rf "$ICONSET"
mkdir -p "$ICONSET" "$ROOT/build"

cp "$BASE/16.png"  "$ICONSET/icon_16x16.png"
cp "$BASE/32.png"  "$ICONSET/icon_16x16@2x.png"
cp "$BASE/32.png"  "$ICONSET/icon_32x32.png"
cp "$BASE/64.png"  "$ICONSET/icon_32x32@2x.png"
cp "$MAC/128.png"  "$ICONSET/icon_128x128.png"
cp "$MAC/256.png"  "$ICONSET/icon_128x128@2x.png"
cp "$MAC/256.png"  "$ICONSET/icon_256x256.png"
cp "$MAC/512.png"  "$ICONSET/icon_256x256@2x.png"
cp "$MAC/512.png"  "$ICONSET/icon_512x512.png"
cp "$MAC/1024.png" "$ICONSET/icon_512x512@2x.png"

iconutil -c icns "$ICONSET" -o "$ROOT/build/icon.icns"
echo "Wrote $ROOT/build/icon.icns"
