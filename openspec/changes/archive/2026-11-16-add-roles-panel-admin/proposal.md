## Why

Hace falta que alguien con rol de administración pueda ver las cuentas registradas, desactivarlas y resetear su contraseña, y que esa capacidad esté protegida en PocketBase y no solo en la interfaz. (Cambio documentado a posteriori: ya está implementado.)

## What Changes

- Campos nuevos en `users`: `rol` (`usuario` o `admin`; vacío equivale a `usuario`) y `desactivado`.
- Reglas de la colección `users` para que solo un admin activo pueda listar todas las cuentas, desactivarlas, cambiar su rol y resetear su contraseña (sin conocer la anterior).
- Las cuentas desactivadas no pueden iniciar sesión.
- Panel de administración en la aplicación, al que llega directamente un admin al iniciar sesión.
- `configurar_pocketbase.py`: script repetible que aplica campos y reglas y puede crear el primer admin.

## Capabilities

### New Capabilities
- `administracion-cuentas`: roles, listado de cuentas, activación/desactivación y reseteo de contraseña, con las reglas de PocketBase que los restringen a admins.

### Modified Capabilities
- `autenticacion`: un admin que inicia sesión llega al panel de administración en lugar de al conversor.

## Impact

- Código: `mi_cotizador.py` (panel, diálogo de contraseña, rol en la sesión) y `configurar_pocketbase.py` (nuevo).
- Sistema externo: esquema y reglas de la colección `users` en PocketBase; hay que ejecutar el script de configuración en cada base nueva.
- Sin dependencias nuevas.
