REM Only useful to regenerate or add options to Vial.spec
pyi-makespec ^
    --specpath=misc ^
    --name=Vial ^
    --add-data="../src/main/resources/base/qmk_settings.json:resources/base" ^
    --add-data="../src/build/settings/base.json:resources/settings" ^
    --add-data="../src/build/settings/linux.json:resources/settings" ^
    --add-data="../src/build/settings/mac.json:resources/settings" ^
    --console ^
    --noupx ^
    --icon="../src/main/icons/Icon.ico" ^
    --argv-emulation ^
    ./src/main/python/main.py