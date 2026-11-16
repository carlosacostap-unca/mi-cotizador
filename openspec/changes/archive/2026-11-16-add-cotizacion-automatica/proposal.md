## Why

Hoy la persona tiene que buscar e ingresar a mano la cotización del dólar antes de cada conversión. Traer automáticamente la cotización oficial evita el paso manual y los errores de tipeo.

## What Changes

- Al abrirse el conversor, la aplicación consulta la cotización del dólar oficial en dolarapi.com y carga el valor de **venta** en el campo de cotización.
- Un botón **Actualizar cotización** vuelve a consultarla y reemplaza el valor del campo.
- Se muestra de dónde viene el valor y su fecha de actualización.
- El campo sigue siendo editable: la persona puede usar otra cotización.
- Si la consulta falla, se avisa y la aplicación sigue funcionando con ingreso manual.
- La dirección de la API se lee de `DOLARAPI_URL` (`.env`), sin valor en el código ni en `.env.example`.

## Capabilities

### New Capabilities
- `cotizacion-automatica`: obtención de la cotización del dólar oficial desde una API pública para precargar y actualizar el campo de cotización.

### Modified Capabilities

## Impact

- Código: `mi_cotizador.py` (consulta HTTP, botón y etiqueta en el conversor).
- Configuración: nueva variable `DOLARAPI_URL` en `.env` y `.env.example`.
- Sistema externo: servicio público dolarapi.com; se hace una consulta GET sin enviar datos de la persona.
- Sin dependencias nuevas.
