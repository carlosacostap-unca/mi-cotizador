## Context

La aplicación ya inicia sesión contra PocketBase y guarda el token en memoria (capacidad `autenticacion`); el historial hoy es `historial.txt` (capacidad `conversor`). `configurar_pocketbase.py` ya aplica el esquema y las reglas de `users`. Ver proposal.md para la motivación.

## Goals / Non-Goals

**Goals:**
- Que el aislamiento por usuario lo garantice PocketBase, no la interfaz.
- Reutilizar el cliente HTTP y el script de configuración existentes.

**Non-Goals:**
- Migrar las líneas viejas de `historial.txt`.
- Edición, borrado, filtros, paginación o exportación del historial.
- Que un admin vea las consultas de otros (ver supuesto abajo).

## Decisions

- **Colección `consultas` (base)**: `usuario` (relación a `users`, obligatoria, se borran con el usuario), `monto`, `cotizacion`, `resultado` (números) y `fecha` (autodate al crear). Se usa `fecha` propio, asignado por el servidor, para que el cliente no pueda falsearlo.
- **Reglas**: `list/view`: `usuario = @request.auth.id`; `create`: `@request.auth.id != "" && @request.body.usuario = @request.auth.id`; `update/delete`: sin regla (solo superusuarios). Mantiene el historial como registro inmutable.
- **Supuesto: los admins ven solo su propio historial**, igual que cualquier usuario. El pedido dice "cada usuario ve solo su historial"; el panel de administración sigue limitado a gestionar cuentas.
- **Lista del historial**: tabla en el conversor con las últimas 50 consultas (`sort=-fecha`, `perPage=50`), recargada al abrir el conversor y tras cada guardado. Sin paginación por ahora.
- **Falla al guardar**: se muestra el resultado y un aviso; no hay respaldo en TXT (decisión del usuario), por lo que esa conversión no queda registrada.
- **Sin cambios de dependencias**: se reutiliza `_pedir` con el token de sesión.
- **Script**: crea `consultas` si no existe y, si existe, actualiza campos y reglas; debe correr después de que `users` exista y usa su id para la relación.

## Risks / Trade-offs

- [Sin PocketBase no se guarda historial] → Aviso claro; antes el TXT funcionaba sin servidor, pero ya la aplicación exige PocketBase para iniciar sesión.
- [Pérdida de las conversiones guardadas en `historial.txt`] → No se migran; el archivo queda en disco sin tocar.
- [Un usuario eliminado borra su historial por cascada] → Aceptado, coherente con la privacidad por cuenta.
- [Un token vencido o de cuenta desactivada hace fallar el guardado] → Se trata igual que cualquier error de guardado (aviso).
