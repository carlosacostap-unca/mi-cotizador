## Why

El historial en `historial.txt` es un archivo local, compartido por todos los usuarios de la computadora y sin relación con las cuentas. Guardar cada conversión en PocketBase la asocia a quien la hizo y permite que cada usuario vea solo la suya.

## What Changes

- Nueva colección `consultas` en PocketBase con usuario, monto, cotización, resultado y fecha y hora.
- Cada conversión exitosa se guarda en `consultas` a nombre del usuario con sesión iniciada. **BREAKING**: deja de escribirse `historial.txt`.
- Reglas de PocketBase: cada usuario solo puede crear y leer sus propias consultas; nadie puede modificarlas ni borrarlas desde la aplicación.
- El conversor muestra el historial del usuario (más recientes primero) y lo actualiza tras cada conversión.
- Si no se puede guardar en PocketBase, se muestra el resultado igualmente y se avisa; no se escribe ningún archivo local.
- `configurar_pocketbase.py` crea la colección y sus reglas.

## Capabilities

### New Capabilities
- `historial-consultas`: colección de consultas en PocketBase, aislamiento por usuario y lista del historial propio dentro del conversor.

### Modified Capabilities
- `conversor`: el historial de conversiones pasa del archivo `historial.txt` a PocketBase.
- `administracion-cuentas`: el script de configuración también crea la colección `consultas`.

## Impact

- Código: `mi_cotizador.py` (guardado y listado vía API, lista en el conversor, se elimina el TXT) y `configurar_pocketbase.py`.
- Sistema externo: nueva colección `consultas` con relación a `users`; hay que volver a ejecutar el script de configuración.
- Datos: las conversiones guardadas antes en `historial.txt` no se migran.
- `.gitignore`: `historial.txt` deja de ser relevante.
