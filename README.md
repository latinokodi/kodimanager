# Kodi Manager v3.0

Una aplicación de escritorio profesional para gestionar múltiples instancias portables de Kodi en Windows.

## 🚀 Novedades (v3.0)
- **UI Premium "Glassmorphism"**: Interfaz rediseñada con tema oscuro, efectos de transparencia y tarjetas modernas.
- **Rendimiento Mejorado**: Detección de instancias 100% asíncrona (no congela la interfaz) y tiempo de inicio instantáneo.
- **Seguridad**: Sistema de eliminación de instancias robusto que previene errores y riesgos de seguridad.
- **Soporte Ko-fi**: Botón integrado para apoyar el desarrollo.

## Resumen
Kodi Manager permite a los usuarios:
- Descargar Kodi desde fuentes oficiales.
- Instalar Kodi en "modo portable" con un solo clic.
- Gestionar múltiples instalaciones independientes.
- Detectar instalaciones existentes automáticamente.
- Crear accesos directos personalizados en el escritorio.

## Instalación

### Método Recomendado (Usuario Final)
1. Descargue el último instalador: `KodiManager_Setup_v3.0.exe`.
2. Ejecute el instalador y siga los pasos.
3. Inicie **Kodi Manager** desde el acceso directo en su escritorio.

### Desarrollo (Código Fuente)
1. Instale Python 3.10 o superior.
2. Clone este repositorio.
3. Ejecute `run_app.bat` en Windows.

## Arquitectura Técnica
La aplicación sigue una arquitectura modular y escalable:

- **Core (`src/kodimanager/core`)**: Lógica de negocio pura (Gestor de instancias, Descargador, Instalador). Decoplado de la UI.
- **GUI (`src/kodimanager/gui`)**: Interfaz construida con **PyQt6**.
  - **Worker Threads**: Las tareas pesadas (detección, descarga) se ejecutan en hilos secundarios para mantener la UI fluida.
  - **Design System (`styles.py`)**: Sistema de estilos centralizado para una apariencia consistente.
- **Datos**: Persistencia ligera usando JSON en `%APPDATA%\KodiManager`.

### Construcción (Build)
Para generar el ejecutable y el instalador:
1. Ejecute `build_exe.bat` (Genera el ejecutable optimizado en modo directorio).
2. Compile `setup.iss` usando **Inno Setup** para crear el instalador final.

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
