## Why

El conversor debe quedar reservado a personas con cuenta. Se usan los usuarios de PocketBase para no construir un sistema de cuentas propio. (Cambio documentado a posteriori: ya está implementado.)

## What Changes

- Pantalla de inicio de sesión (email y contraseña) como pantalla inicial.
- Pantalla de registro (email, contraseña y confirmación), que al completarse inicia sesión.
- El conversor solo se abre después de iniciar sesión; botón **Cerrar sesión** que vuelve al login.
- La dirección de PocketBase se toma de la variable `POCKETBASE_URL` (definida en el `.env`).

## Capabilities

### New Capabilities
- `autenticacion`: inicio de sesión, registro y cierre de sesión contra la colección `users` de PocketBase, y control de acceso al conversor.

### Modified Capabilities

## Impact

- Código: `mi_cotizador.py` (pantallas y cliente HTTP de PocketBase con `urllib`).
- Sistema externo: servidor PocketBase en ejecución con la colección `users`.
- Sin dependencias nuevas.
