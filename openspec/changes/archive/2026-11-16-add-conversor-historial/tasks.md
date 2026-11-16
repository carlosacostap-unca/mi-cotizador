## 1. Conversión

- [x] 1.1 Implementar el parseo de números y la conversión; verificado con `1.500.000,50` → 1500000.5 y 1.000.000 / 1250 → 800.0
- [x] 1.2 Validar datos no numéricos y cotización no positiva con mensajes de error; verificado en la interfaz de la aplicación

## 2. Historial

- [x] 2.1 Agregar cada conversión a `historial.txt` con fecha y hora; verificado leyendo el archivo generado por una conversión de prueba
- [x] 2.2 Avisar si el historial no se puede escribir; implementado con una advertencia (`OSError`)

## 3. Interfaz y empaquetado

- [x] 3.1 Construir la ventana con los dos campos, el botón Convertir y el resultado; verificado al abrir la aplicación
- [x] 3.2 Generar `dist/Mi Cotizador.exe` con PyInstaller; verificado ejecutándolo y comprobando que abre sin errores
