## Context

La colección `users` de PocketBase ya se usa para iniciar sesión (ver capacidad `autenticacion`). La interfaz no es una barrera de seguridad por sí sola, así que los permisos deben vivir en las reglas del servidor. Ver proposal.md para la motivación.

## Goals / Non-Goals

**Goals:**
- Que solo un admin activo pueda administrar cuentas, garantizado por PocketBase.
- Poder reproducir la configuración en una base nueva.

**Non-Goals:**
- Un tercer rol o permisos más finos.
- Eliminar cuentas desde el panel, o invitar usuarios.
- Auditoría de acciones de los admins.

## Decisions

- **Campos en `users`**: `rol` (select `usuario`/`admin`, opcional) y `desactivado` (bool). Se usa `desactivado` y no `activo` para que el valor por defecto (falso) deje activas a las cuentas nuevas y existentes.
- **Reglas en el servidor** (`ES_ADMIN` = rol admin y no desactivado): `list/view` propio o admin; `create` sin enviar `rol` ni `desactivado`; `update` propio sin tocar esos campos, o admin; `delete` propio o admin; `authRule` = `desactivado = false`.
- **`manageRule` = admin**: es lo que permite al admin ver emails ajenos (que PocketBase oculta por defecto) y cambiar contraseñas sin la anterior. Alternativa descartada: forzar `emailVisibility` en todas las cuentas, que expondría emails a cualquiera.
- **Script `configurar_pocketbase.py`** con credenciales de superusuario por variables de entorno o prompt, y primer admin con clave aleatoria; así las reglas quedan versionadas aunque `pocketbase/` no lo esté.
- **Admin aterriza en el panel**, con botones para ir al conversor y volver.

## Risks / Trade-offs

- [Un admin puede cambiar el rol de otros, incluido ascender a admin] → Aceptado; es el comportamiento esperado del rol.
- [Un token vigente de una cuenta desactivada sigue siendo válido hasta expirar] → Las reglas de admin exigen `desactivado = false`, así que pierde permisos de inmediato; el acceso a datos propios no es sensible aquí.
- [La clave nueva la conoce el admin y debe comunicarla] → Aceptado; no hay envío de emails.
- [Reglas aplicadas por API no quedan en migraciones de PocketBase] → Se compensa con el script repetible.
