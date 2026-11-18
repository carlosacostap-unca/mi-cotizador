## Context

La interfaz es Tkinter, que no expone sus controles a las herramientas de accesibilidad: solo se puede operar con teclado y mouse reales, y leer con capturas de pantalla. Ya se hizo a mano una prueba así con PowerShell (`SendKeys` y capturas de la ventana) y funcionó. El proyecto usa `.env` para la configuración y `entorno.py` para leerlo. Ver proposal.md para la motivación.

## Goals / Non-Goals

**Goals:**
- Un programa en Python, repetible, que ejercite la interfaz real y deje evidencia.
- Verificar el resultado contra lo guardado en PocketBase, no solo "mirar" las capturas.

**Non-Goals:**
- Un marco general de pruebas de interfaz o integración con CI.
- Leer el texto de las capturas (OCR) o compararlas pixel a pixel.
- Funcionar en otros sistemas operativos.

## Decisions

- **`ctypes` de Windows para teclado y ventana, y Pillow para capturar** (decisión tomada al implementar; el borrador proponía `pyautogui` y `pygetwindow`). Con `SendInput` en modo Unicode el texto se escribe igual con cualquier distribución de teclado (el `@` del email, por ejemplo), `FindWindowW` ubica la ventana por su título exacto y no hay bibliotecas nuevas salvo Pillow. Se activa la conciencia de DPI de Windows (`SetProcessDPIAware`) para que las capturas tengan el tamaño real.
- **Solo teclado, sin coordenadas de mouse**: el login arranca con el foco en el email (Tab hasta la contraseña, Enter), y el conversor arranca con el foco en el monto. Es más robusto frente a cambios de tamaño de la ventana. El mouse solo se vigila para la salvaguarda de esquina, implementada con `GetCursorPos` antes de cada tecla.
- **Foco antes de escribir**: tras pasar la ventana al frente se espera casi un segundo; sin esa pausa se perdía el primer carácter (se descubrió en la primera ejecución real). El inicio de sesión se da por bueno cuando la ventana cambia de tamaño al abrirse el conversor.
- **Cierre de la aplicación**: se usa `taskkill /T` porque el `.exe` de PyInstaller lanza un proceso hijo y cerrar solo el padre dejaba la ventana abierta. Las corridas fallidas borran la carpeta de capturas si quedó vacía.
- **Comprobaciones previas**: antes de tomar el teclado se inicia sesión por la API con el usuario de prueba y se consulta la cotización automática; si fallan, el programa termina sin tocar nada.
- **Qué se abre**: por defecto `python mi_cotizador.py` (siempre el código actual, sin depender de un `.exe` desactualizado); `--exe` abre `dist/Mi Cotizador.exe`. El proceso se cierra al final en un bloque `finally`.
- **Espera de cada resultado**: se toma la captura recién cuando la verificación contra PocketBase indica que la consulta ya existe (se sondea el historial del usuario hasta que aparezca la nueva fila), no con una espera fija. Así cada captura muestra el resultado y la fila nueva en la tabla.
- **Montos fijos y distintos**: `1000, 5000, 12500, 25000, 50000, 75000, 100000, 250000, 500000, 1000000`, escritos como dígitos sin separadores para evitar la ambigüedad del punto. Alternativa descartada: montos aleatorios, que dificultan reproducir un fallo.
- **Verificación vía API de PocketBase** con el login del propio usuario de prueba (reglas normales, no superusuario): se leen sus últimas consultas ordenadas por fecha y se comparan con los diez montos enviados (monto exacto, resultado ≈ monto ÷ cotización con tolerancia de 0,01).
- **Usuario de prueba persistente** (decisión del usuario): se crea una vez con `configurar_pocketbase.py --crear-usuario-prueba` a partir de `PB_TEST_EMAIL` y `PB_TEST_PASSWORD` del `.env` (si falta alguna, el script termina sin crear nada), y nunca se borra. Cada ejecución suma diez consultas al historial de ese usuario.
- **Nombre de las capturas**: `capturas/<AAAAMMDD-HHMMSS>/NN_monto.png`, una subcarpeta por ejecución para no pisar las anteriores. `capturas/` se agrega al `.gitignore`.
- **Credenciales por `.env`**, sin valores en el código ni en `.env.example`; la contraseña nunca se imprime ni aparece en los mensajes de error.
- **Cuenta regresiva de 5 s** (configurable con `--cuenta`) antes de tomar el teclado, cancelable con Ctrl+C, y salvaguarda de esquina activa durante toda la ejecución.

## Risks / Trade-offs

- [Simular teclado afecta a lo que la persona esté haciendo] → Aviso previo, cuenta regresiva cancelable y fail-safe de esquina.
- [Si otra ventana toma el foco, las teclas van a otro lado] → Antes de cada paso se verifica que la ventana de Mi Cotizador sea la activa y se la trae al frente; si no se logra, se aborta sin escribir.
- [El historial del usuario de prueba crece con cada ejecución] → Aceptado (decisión del usuario); son solo diez filas por ejecución.
- [La cotización cambia entre conversiones] → La verificación usa la cotización guardada en cada consulta, no un valor fijo.
- [La automatización depende de detalles de Windows (foco, DPI)] → Se verifica el foco antes de cada paso y se usan solo llamadas estándar de la API de Windows.
