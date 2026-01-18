#!/usr/bin/env bash

# Resolve script directory logic
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "[Kodi Manager] Verificando entorno..."

if [ ! -d "venv" ]; then
    echo "[Kodi Manager] Creando entorno virtual..."
    python3 -m venv venv
fi

source venv/bin/activate

echo "[Kodi Manager] Instalando/Actualizando dependencias..."
pip install -r requirements.txt > /dev/null 2>&1

echo "[Kodi Manager] Iniciando aplicacion..."
python3 -m src.kodimanager.gui.main_window
