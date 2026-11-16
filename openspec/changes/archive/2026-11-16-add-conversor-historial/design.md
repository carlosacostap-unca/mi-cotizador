## Context

Aplicación de escritorio para Windows de un solo archivo, sin dependencias externas. Ver proposal.md para la motivación.

## Goals / Non-Goals

**Goals:**
- Distribuir un único `.exe` que no requiera Python instalado.
- Mantener la lógica de conversión y de historial separada de la interfaz para poder probarla.

**Non-Goals:**
- Obtener cotizaciones automáticamente desde internet.
- Mostrar o filtrar el historial dentro de la aplicación.

## Decisions

- **Tkinter/ttk**: incluido en Python, sin instalar nada; alternativas (PyQt, web) agregan dependencias innecesarias.
- **PyInstaller `--onefile --windowed`**: un solo ejecutable sin consola.
- **`historial.txt` junto al ejecutable**: se usa la carpeta del `.exe` cuando está empaquetado (`sys.frozen`) y la del script en desarrollo; así el archivo no queda en una carpeta temporal.
- **Texto plano UTF-8, una línea por conversión**: simple de leer y abrir con cualquier editor.
- **Parseo de números tolerante**: si hay coma, se toman los puntos como separador de miles y la coma como decimal.

## Risks / Trade-offs

- [El historial puede crecer sin límite] → Aceptado; es texto plano y de bajo volumen.
- [Carpeta del ejecutable sin permisos de escritura] → Se muestra una advertencia y la conversión igualmente se muestra.
