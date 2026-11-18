## Why

Hoy hay que completar campos y apretar botones para cada acción. Un chat que entienda pedidos en lenguaje natural ("convertime 150 mil pesos", "¿a cuánto está el dólar?", "mostrame mis últimas conversiones") y los resuelva con las funciones que la app ya tiene hace más rápido el uso cotidiano.

## What Changes

- Nueva pantalla **Asistente** (chat), a la que se llega con un botón desde el conversor, con botón para volver. Solo para usuarios con sesión iniciada.
- El chat usa la API de OpenAI con **llamadas a funciones**: el modelo interpreta el pedido y la app ejecuta localmente, con la sesión del usuario, solo estas funciones ya existentes:
  - convertir pesos a dólares (con la misma validación y guardado en el historial que el botón Convertir; sin cotización indicada usa la del dólar oficial),
  - consultar la cotización del dólar oficial,
  - actualizar la cotización cargada en el conversor,
  - ver el historial propio.
- **No** expone las funciones de administración de cuentas (listar, desactivar, resetear contraseñas): ni siquiera para admins.
- La clave de OpenAI va en el `.env` (`OPENAI_API_KEY`), junto con el modelo (`OPENAI_MODEL`) y la dirección de la API (`OPENAI_URL`), todos sin valor por defecto en el código ni en `.env.example`.
- Las llamadas a la API no bloquean la ventana; la conversación vive solo en memoria y se borra al cerrar sesión.
- Aviso visible en el chat de que lo que se escribe, y los resultados de las funciones (como el historial), se envían a OpenAI.
- Sin dependencias nuevas: la API se consulta con `urllib`, igual que PocketBase y la cotización.

## Capabilities

### New Capabilities
- `asistente-chat`: chat en lenguaje natural que resuelve pedidos con funciones de usuario de la app mediante la API de OpenAI.

### Modified Capabilities

## Impact

- Código: `mi_cotizador.py` (pantalla de chat, cliente de OpenAI, funciones expuestas al modelo); la lógica reutiliza `convertir`, `obtener_cotizacion`, `guardar_consulta` y `listar_consultas`.
- Configuración: `OPENAI_API_KEY`, `OPENAI_MODEL` y `OPENAI_URL` en `.env` y `.env.example`; `README.md` con el uso y los avisos.
- Sistema externo: API de OpenAI (servicio de pago: cada mensaje consume crédito de la cuenta de la clave). Se envían a OpenAI los mensajes del usuario y los resultados de las funciones; no se envían la clave de PocketBase, el token de sesión ni la contraseña.
- El `.exe` no incluye la clave: la lee del `.env` que quede junto al ejecutable.
- Sin cambios en PocketBase ni en las reglas de acceso.
