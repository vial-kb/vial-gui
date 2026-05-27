#!/bin/bash
set -e

cd /vial-gui

uv sync --extra build --frozen
uv run pyinstaller --noconfirm --clean vial-linux.spec

APPDIR=AppDir
rm -rf "$APPDIR"
mkdir -p "$APPDIR/usr/bin" \
         "$APPDIR/usr/share/applications" \
         "$APPDIR/usr/share/icons/hicolor/256x256/apps"

cp -r dist/Vial/. "$APPDIR/usr/bin/"
cp src/main/icons/linux/256.png "$APPDIR/usr/share/icons/hicolor/256x256/apps/Vial.png"
cp src/main/icons/linux/256.png "$APPDIR/Vial.png"
cp misc/Vial.desktop "$APPDIR/usr/share/applications/Vial.desktop"
cp misc/Vial.desktop "$APPDIR/Vial.desktop"

cat > "$APPDIR/AppRun" <<'EOF'
#!/bin/sh
HERE=$(dirname "$(readlink -f "$0")")
export QT_QPA_PLATFORM=xcb
exec "$HERE/usr/bin/Vial" "$@"
EOF
chmod +x "$APPDIR/AppRun"

ARCH=x86_64 appimagetool --no-appstream "$APPDIR" /output/Vial-x86_64.AppImage
