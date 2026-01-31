# Registro de Cambios

## v3.0 (2026-01-31) - Production Overhaul
- **Seguridad**: Se reescribió la lógica de eliminación de instancias para no depender de comandos del sistema (`shell=True`), eliminando riesgos de inyección y mejorando la compatibilidad.
- **Rendimiento**: La detección de instancias ahora se ejecuta en segundo plano (Asíncrono), evitando que la interfaz se congele durante el escaneo.
- **UI/UX Premium**: Nuevo tema "Glassmorphism" (Oscuro) con tipografía moderna, tarjetas rediseñadas y mejores indicadores visuales.
- **Estabilidad**: Mejor manejo de errores al eliminar carpetas bloqueadas y refactorización del código base para mayor robustez.

## v2.2 (2026-01-19)
- **Corrección de Error Crítico**: Se solucionó el error "name 'sys' is not defined" que impedía la instalación en algunos sistemas.
- **Actualización de Versión**: Se incrementó la versión a 2.2.

## v2.1 (2026-01-19)
- **Persistencia del Instalador**: Ahora el instalador de Kodi se guarda en una carpeta local llamada `Kodi_Installers` dentro del directorio de la aplicación.
- **Optimización de Descarga**: Si el instalador ya existe en la carpeta local, la aplicación lo reutiliza en lugar de descargarlo nuevamente, acelerando significativamente el proceso para múltiples instalaciones de la misma versión.
- **Limpieza**: Se eliminó la eliminación automática del instalador después de la instalación.
- **Nombre del Ejecutable**: El archivo compilado ahora se nombra `KodiManager_v2.1.exe`.
- **Mejora de UX**: Al reiniciar en modo administrador, se suprime la pantalla de "Acerca de" (Splash Screen).
