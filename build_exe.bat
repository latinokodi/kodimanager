@echo off
echo [Kodi Manager] Building Standalone EXE (PyQt6 Edition)...

:: Ensure venv is active
if exist venv\Scripts\activate.bat (
    echo [Kodi Manager] Activating virtual environment...
    call venv\Scripts\activate.bat
) else (
    echo [ERROR] Virtual environment not found. Please run run_app.bat first.
    exit /b 1
)

:: Install PyInstaller and Pillow (for icon conversion)
echo [Kodi Manager] Installing PyInstaller and Pillow...
pip install pyinstaller Pillow

:: Clean previous build
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"
if exist "KodiManager.spec" del "KodiManager.spec"

:: Run PyInstaller
echo [Kodi Manager] Running PyInstaller...

:: We need to include the Logo and potentially the Icon as data files
:: Format: source;dest_folder
set "ADD_DATA=--add-data src/kodimanager/gui/LKU-LOGO-Small.png;kodimanager/gui --add-data src/kodimanager/gui/icon.png;kodimanager/gui"
set "ICON=--icon src/kodimanager/gui/icon.png"

pyinstaller --noconfirm --clean --onefile --windowed ^
    --name "KodiManager" ^
    --paths "src" ^
    %ADD_DATA% ^
    %ICON% ^
    launcher.py

echo.
if exist "dist\KodiManager.exe" (
    echo [SUCCESS] Build complete! Executable is in 'dist' folder.
    start "" "dist"
) else (
    echo [ERROR] Build failed.
)

pause
