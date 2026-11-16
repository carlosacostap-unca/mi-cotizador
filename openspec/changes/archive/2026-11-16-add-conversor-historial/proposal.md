## Why

Se necesita una aplicación de escritorio simple para convertir un monto en pesos a dólares con una cotización ingresada a mano, y dejar registro de cada conversión. (Cambio documentado a posteriori: ya está implementado.)

## What Changes

- Aplicación de escritorio "Mi Cotizador" en Python (Tkinter) con campos de monto en pesos y cotización del dólar, y un botón **Convertir** que muestra el resultado en dólares.
- Cada conversión exitosa se agrega, con fecha y hora, a `historial.txt`.
- Ejecutable de Windows generado con PyInstaller.

## Capabilities

### New Capabilities
- `conversor`: conversión de pesos a dólares con validación de datos y registro de cada conversión en un historial de texto.

### Modified Capabilities

## Impact

- Código: `mi_cotizador.py`.
- Artefactos: `dist/Mi Cotizador.exe` (no versionado) y `historial.txt` (generado, no versionado).
- Dependencias: solo biblioteca estándar de Python; PyInstaller para empaquetar.
