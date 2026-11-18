## Why

Para trabajar con Claude Code sobre este proyecto hoy hay que consultar y cambiar la base de PocketBase por fuera (scripts sueltos, el panel web). Un servidor MCP propio le da a Claude herramientas directas y acotadas sobre la base local, sin confiar credenciales de superusuario a paquetes de terceros.

## What Changes

- Nuevo servidor MCP en Python (`mcp_pocketbase.py`, transporte stdio) conectado a la base local de PocketBase, con herramientas de **lectura y escritura**: estado del servidor, colecciones y su esquema/reglas, y alta, consulta, modificación y borrado de registros; creación y modificación de colecciones.
- Registro del servidor en `.mcp.json` en la raíz del proyecto, para que Claude Code lo ofrezca al abrir el proyecto. El archivo no contiene direcciones ni credenciales.
- La dirección y las credenciales del superusuario se leen del `.env` (`POCKETBASE_URL`, `PB_SUPERUSER_EMAIL`, `PB_SUPERUSER_PASSWORD`), igual que en el resto del proyecto.
- El servidor no permite operar sobre colecciones del sistema (nombre que empieza con `_`, como `_superusers`) y no puede borrar colecciones.
- Nueva dependencia de desarrollo: el SDK oficial de MCP para Python, declarada en `requirements.txt`.
- Documentación breve de uso y riesgos en el `README`.

## Capabilities

### New Capabilities
- `servidor-mcp-pocketbase`: servidor MCP para que Claude Code consulte y modifique la base local de PocketBase, con límites de seguridad definidos.

### Modified Capabilities

## Impact

- Código nuevo: `mcp_pocketbase.py`; reutiliza `entorno.py`.
- Archivos nuevos: `.mcp.json`, `requirements.txt` y `README.md` (si no existe).
- Dependencias: paquete `mcp` (solo para el servidor; la aplicación de escritorio y su `.exe` no lo usan).
- Seguridad: Claude podrá, previa aprobación de cada llamada en Claude Code, leer y modificar cualquier colección no de sistema, y como el superusuario ignora las reglas de acceso, también las consultas de todos los usuarios.
- Sin cambios en la aplicación de escritorio ni en las reglas de PocketBase.
