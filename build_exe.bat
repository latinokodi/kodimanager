@echo off
echo [Kodi Manager] Building Standalone EXE...

:: Ensure venv is active
if exist venv\Scripts\activate.bat (
    echo [Kodi Manager] Activating virtual environment...
    call venv\Scripts\activate.bat
) else (
    echo [ERROR] Virtual environment not found. Please run run_app.bat first.
    exit /b 1
)

:: Ensure pyinstaller is installed in venv
pip install pyinstaller
:: Remove potential conflicting packages
pip uninstall -y PyQt6 PyQt6-Qt6 PyQt6-sip

:: Clean previous build
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"

:: Run PyInstaller
:: --add-data separator is ; on Windows
:: mapping: source;dest
:: src/kodimanager/gui/web -> web
:: src/kodimanager/gui/icon.png -> . (root of MEIPASS to match single file logic, or map to match source structure)
:: In main_window.py logic for frozen:
:: script_dir = sys._MEIPASS
:: html = script_dir/web/index.html
:: icon = script_dir/icon.png
:: So we map icon.png to root of bundle (.)

:: PyInstaller for Flet
:: Flet requires including the 'flet' module and assets
:: --add-data "src/kodimanager/gui/assets;assets" maps internal assets to root assets for flet

pyinstaller --noconfirm --clean --onefile --windowed ^
    --name "KodiManager" ^
    --paths "src" ^
    --hidden-import="flet" ^
    --hidden-import="bs4" ^
    --hidden-import="requests" ^
    --icon "src/kodimanager/gui/icon.png" ^
    --add-data "src/kodimanager/gui/assets;src/kodimanager/gui/assets" ^
    launcher.py

echo.
if exist "dist\KodiManager.exe" (
    echo [SUCCESS] Build complete! Executable is in 'dist' folder.
) else (
    echo [ERROR] Build failed.
)

