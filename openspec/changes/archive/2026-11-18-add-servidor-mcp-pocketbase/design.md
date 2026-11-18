## Context

El proyecto ya lee su configuración y las credenciales de PocketBase desde `.env` mediante `entorno.py`, y evita escribir direcciones o contraseñas en el código versionado. Claude Code carga servidores MCP de proyecto desde `.mcp.json` y pide aprobación al usuario; ese archivo no lee el `.env` por sí solo. Ver proposal.md para la motivación y specs para los requisitos.

## Goals / Non-Goals

**Goals:**
- Un servidor pequeño, sin paquetes de terceros con acceso a la base, con herramientas acotadas.
- Reutilizar `entorno.py` y el modelo de configuración existente.

**Non-Goals:**
- Exponer todo el SDK de PocketBase (archivos, realtime, backups, logs, ajustes del servidor).
- Operar en nombre de usuarios de la aplicación (solo superusuario).
- Que la aplicación de escritorio use el MCP o lo incluya en el `.exe`.

## Decisions

- **Servidor propio en Python con el SDK oficial de MCP** (decisión del usuario), por stdio. Alternativa descartada: paquetes npm de terceros que correrían con las credenciales de superusuario. Se fija la versión exacta en `requirements.txt`; se prefiere la 1.x estable más reciente con `FastMCP`, y la 2.x solo si ofrece la misma API verificada.
- **Lectura y escritura** (decisión del usuario), con las salvaguardas de abajo.
- **`.mcp.json` sin secretos**: ejecuta `python mcp_pocketbase.py` con la ruta del proyecto; el servidor importa `entorno.py` y carga el `.env` por su cuenta, así que ni la dirección ni las credenciales aparecen en `.mcp.json`.
- **Autenticación como superusuario** vía `/api/collections/_superusers/auth-with-password`, con el token en memoria; ante un 401 se vuelve a autenticar una vez y se reintenta. Sin dependencias HTTP nuevas (`urllib`, como en la app).
- **Herramientas** (nombres con prefijo `pb_`): `pb_salud`, `pb_listar_colecciones`, `pb_ver_coleccion`, `pb_listar_registros`, `pb_ver_registro`, `pb_crear_registro`, `pb_actualizar_registro`, `pb_borrar_registro`, `pb_crear_coleccion`, `pb_actualizar_coleccion`.
- **Supuesto: no hay herramienta para borrar colecciones**, pensando en que es lo más irreversible; se puede agregar con otro cambio si hace falta.
- **Colecciones de sistema bloqueadas** (nombre con `_` inicial): evita que Claude lea o altere los superusuarios, la configuración de autenticación o los registros internos. Se aplica en un único punto de validación que usan todas las herramientas.
- **Límite de 100 registros por página** para no desbordar el contexto de Claude.
- **Errores de PocketBase** se devuelven como texto legible (mensaje y detalle por campo) sin incluir credenciales ni tokens.
- **Salida estándar reservada al protocolo**: cualquier registro o diagnóstico va a la salida de errores.
- **Aprobación por herramienta**: se deja el comportamiento por defecto de Claude Code, que pide permiso al usar herramientas MCP; no se preaprueban en la configuración.
- **Dependencia aislada**: `mcp` se declara en `requirements.txt` solo para el servidor; la aplicación de escritorio y su `.exe` no lo importan.

## Risks / Trade-offs

- [El superusuario ignora las reglas de PocketBase: Claude puede ver las consultas de todos los usuarios y modificar o borrar registros que la app declara inmutables, como `consultas`] → Aprobación por herramienta en Claude Code, documentado en el README.
- [Borrado accidental de registros] → Cada borrado requiere aprobación; el borrado es por id (no masivo).
- [Un cambio de esquema mal formado puede romper la aplicación] → Las colecciones se modifican con PATCH sobre lo existente y PocketBase valida; el script `configurar_pocketbase.py` permite reaplicar lo esperado.
- [Cambios mayores del SDK de MCP] → Versión fijada en `requirements.txt`.
- [El `.env` con la contraseña de superusuario debe existir donde corra el servidor] → Se busca con la misma lógica que la aplicación; si falta, error claro.
