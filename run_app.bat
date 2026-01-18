@echo off
setlocal
cd /d "%~dp0"

echo [Kodi Manager] Verificando entorno...

if not exist venv (
    echo [Kodi Manager] Creando entorno virtual...
    python -m venv venv
)

call venv\Scripts\activate.bat

echo [Kodi Manager] Instalando/Actualizando dependencias...
pip install -r requirements.txt

echo [Kodi Manager] Iniciando aplicacion...
python launcher.py

if %ERRORLEVEL% NEQ 0 (
    echo Error running application.
    pause
)
endlocal
