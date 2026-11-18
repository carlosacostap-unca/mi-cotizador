## Why

Hasta ahora las pruebas de la interfaz de Mi Cotizador se hicieron a mano o con scripts descartables. Un programa reutilizable que maneje la aplicación real, haga varias conversiones y guarde una captura de cada resultado permite repetir la verificación después de cada cambio y dejar evidencia visual.

## What Changes

- Nuevo programa `capturas_conversiones.py` que abre Mi Cotizador, inicia sesión con un usuario de prueba, realiza **diez conversiones con montos distintos** escribiendo en la ventana real y guarda una captura de la ventana tras cada resultado en `capturas/`.
- Al terminar, el programa comprueba contra PocketBase que las diez conversiones quedaron guardadas en el historial del usuario de prueba y que cada resultado coincide con monto ÷ cotización; informa el resultado y devuelve un código de salida distinto de cero si algo no coincide.
- El **usuario de prueba es persistente**: se crea una vez y no se borra. Sus credenciales viven en el `.env` (`PB_TEST_EMAIL`, `PB_TEST_PASSWORD`); `.env.example` incluye las claves sin valores.
- `configurar_pocketbase.py` gana la opción `--crear-usuario-prueba`, que crea ese usuario (rol común) con las credenciales del `.env`, igual que ya hace con el admin.
- La carpeta `capturas/` queda fuera de Git.
- Una dependencia nueva para este programa: Pillow (para las capturas). El teclado y la ventana se manejan con `ctypes` de Windows, sin otras bibliotecas.

## Capabilities

### New Capabilities
- `capturas-conversiones`: automatización de la interfaz de Mi Cotizador para ejecutar diez conversiones, capturar cada resultado y verificarlas contra el historial guardado.

### Modified Capabilities
- `administracion-cuentas`: el script de configuración también crea el usuario de prueba.

## Impact

- Código nuevo: `capturas_conversiones.py`; cambio menor en `configurar_pocketbase.py`.
- Configuración: `PB_TEST_EMAIL` y `PB_TEST_PASSWORD` en `.env` y `.env.example`; `capturas/` en `.gitignore`; `README.md` con el modo de uso.
- Dependencias: Pillow en `requirements.txt` (solo para este programa; la aplicación y su `.exe` no la usan).
- Datos: cada ejecución agrega diez consultas al historial del usuario de prueba, que se conservan.
- Plataforma: Windows. Mientras corre, el programa toma el teclado y la ventana activa.
