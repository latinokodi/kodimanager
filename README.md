# Kodi Manager

Una aplicación de escritorio para Windows para gestionar múltiples instancias portables de Kodi 64-bit.

## Resumen
Kodi Manager permite a los usuarios:
- Descargar Kodi desde fuentes oficiales (o espejos/mirrors).
- Instalar Kodi en "modo portable" en carpetas separadas.
- Mantener múltiples instalaciones independientes una al lado de la otra.
- Iniciar instancias con la bandera correcta `-p`.
- Realizar "Limpieza Total" de instancias (resetear datos de usuario) individualmente.

## Arquitectura
La aplicación está construida con una clara separación de responsabilidades:
- **Lógica Central (`src/kodimanager/core`)**: Maneja la descarga, extracción y gestión del registro de instancias. Independiente de la GUI.
- **GUI (`src/kodimanager/gui`)**: Una interfaz responsiva construida con PyQt6.
- **Datos**: Utiliza un simple JSON `instances.json` para rastrear las versiones y rutas instaladas.

### Stack Tecnológico
- **Lenguaje**: Python 3.10+ (Seleccionado por su robusto manejo de archivos, excelente librería estándar y soporte multiplataforma).
- **Framework GUI**: `PyQt6` (Aspecto y sensación profesional y nativa, bucle de eventos robusto).
- **Red**: `requests` + `beautifulsoup4` (Manejo confiable de encabezados y análisis para páginas de descarga).
- **Entorno**: Basado en Entorno Virtual (`venv`) (Estrategia B).

## Uso del Sistema de Archivos
- **Raíz del Proyecto**: Contiene el código fuente y los lanzadores.
- **Datos de Ejecución**: 
    - La configuración y el Registro de Instancias se almacenan en `%APPDATA%\KodiManager` (Windows) o `~/.config/kodimanager` (Linux) para evitar contaminar el espacio de trabajo, aunque las instancias portables se pueden instalar donde el usuario elija (por defecto en una carpeta `KodiInstances`).
    - **Nota**: La aplicación respeta la regla de "Archivos Externos" por defecto pero permite anulaciones del usuario.

## Instalación y Ejecución

### Prerrequisitos
- Windows 10/11 (Objetivo principal) o Linux.
- Python 3.10 o superior instalado.

### Ejecución
Usamos la **Estrategia B: Entorno local del proyecto**.

**Windows:**
Haga doble clic en `run_app.bat`. Esto:
1. Creará un entorno virtual de Python (`venv`) si falta.
2. Instalará las dependencias.
3. Iniciará la aplicación.

**Linux/macOS:**
Ejecute `./run_app.sh`.

## Pruebas
Ejecute las pruebas con:
```bash
# Active venv primero
python -m pytest tests
```

## Seguridad y Rendimiento
- Las descargas se verifican si los hashes están disponibles (mejora futura).
- No se requieren privilegios de administrador para la operación estándar (a menos que se instale en carpetas protegidas, lo cual se desaconseja).
- "Limpieza Total" es una operación destructiva; la interfaz incluye diálogos de confirmación.

## Horario de Transmisiones (Twitch)
🔴 **En Vivo**: Lunes, Miércoles, Viernes y Domingos

| Zona | Hora |
| :--- | :--- |
| 🇲🇽 México (CDMX) | 7:00 PM |
| 🇨🇴 Colombia / 🇵🇪 Perú | 8:00 PM |
| 🇻🇪 Venezuela | 9:00 PM |
| 🇦🇷 Argentina / 🇨🇱 Chile | 10:00 PM |
| 🇪🇸 España | 2:00 AM (Día sgte) |

[Visita el canal aquí](https://www.twitch.tv/Latinokodi)

## Autor
**Latinokodi 2026**

