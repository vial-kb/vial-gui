# Command Line to generate a spec

These are the command-line options used to generate the .spec file for pyinstaller:

```
pyi-makespec \
    --specpath=misc \
    --name=Vial \
    --add-data="../src/main/resources/base/qmk_settings.json:resources/base" \
    --add-data="../src/build/settings/base.json:resources/settings" \
    --add-data="../src/build/settings/linux.json:resources/settings" \
    --add-data="../src/build/settings/mac.json:resources/settings" \
    --windowed \
    --noupx \
    --icon="../src/main/icons/Icon.ico" \
    --argv-emulation \
    ./src/main/python/main.py
```


If you are upgrading pyinstaller and want to use new default options, you must
either delete the old spec or rename it to force pyi-makespec to use updated
default options.

## Building from the spec

```
pyinstaller misc/Vial.spec
```