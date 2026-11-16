## Context

Aplicación Tkinter de un solo archivo (ver capacidad `conversor`). PocketBase corre aparte y ya trae la colección de autenticación `users`. Ver proposal.md para la motivación.

## Goals / Non-Goals

**Goals:**
- Reutilizar PocketBase para cuentas, sin guardar contraseñas en la aplicación.
- Mantener un único ejecutable sin dependencias nuevas.

**Non-Goals:**
- Recuperar contraseñas por email, verificar emails o iniciar sesión con terceros.
- Asociar el historial a cada usuario.
- Persistir la sesión entre ejecuciones.

## Decisions

- **API REST con `urllib`**: se usan `auth-with-password` y la creación de registros de `users`; evita sumar el SDK de PocketBase u otras bibliotecas.
- **Una ventana con pantallas intercambiables** (login, registro, conversor) en vez de ventanas separadas; la navegación pasa por un único método que bloquea el acceso al conversor sin sesión.
- **Errores traducidos**: los errores de validación del servidor (`data.<campo>.message`) se muestran tal cual; los 400 de login se muestran como credenciales incorrectas.
- **Sesión solo en memoria**: al cerrar la aplicación se pierde, lo que evita guardar el token en disco.
- **URL configurable por `POCKETBASE_URL`**: permite apuntar a otro servidor sin recompilar.

## Risks / Trade-offs

- [Llamadas de red bloqueantes congelan brevemente la ventana] → Tiempo de espera de 10 s y mensaje de error.
- [El control de acceso en la interfaz no protege a PocketBase] → La protección real se define en las reglas del servidor (ver cambio de roles).
- [Servidor local sin HTTPS] → Aceptado para uso local; para otro servidor usar `https://`.
