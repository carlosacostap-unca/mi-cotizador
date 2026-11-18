# Mi Cotizador

Aplicación de escritorio (Python y Tkinter) que convierte pesos a dólares. Inicia sesión con los usuarios de PocketBase, trae la cotización del dólar oficial y guarda el historial de cada usuario en PocketBase. Los requisitos del proyecto están en `openspec/specs/`.

## Configuración

Copiá `.env.example` como `.env` y completá los valores (el `.env` no se sube a Git). Para dejar PocketBase listo (campos, reglas y colecciones) ejecutá `python configurar_pocketbase.py`.

## Servidor MCP de PocketBase

`mcp_pocketbase.py` es un servidor MCP (stdio) que le da a Claude Code herramientas sobre la base local de PocketBase. Está registrado en `.mcp.json`.

### Activarlo

1. Instalá la dependencia: `pip install -r requirements.txt`.
2. Completá en el `.env`: `POCKETBASE_URL`, `PB_SUPERUSER_EMAIL` y `PB_SUPERUSER_PASSWORD`.
3. Con PocketBase en ejecución, abrí el proyecto en Claude Code y aprobá el servidor `pocketbase` cuando lo pida.

### Herramientas

| Herramienta | Qué hace |
|---|---|
| `pb_salud` | Comprueba si PocketBase responde |
| `pb_listar_colecciones` | Lista las colecciones (sin las de sistema) |
| `pb_ver_coleccion` | Muestra campos, tipos y reglas de una colección |
| `pb_listar_registros` | Lista registros con filtro, orden y paginación (máximo 100 por página) |
| `pb_ver_registro` | Muestra un registro por id |
| `pb_crear_registro`, `pb_actualizar_registro`, `pb_borrar_registro` | Escriben registros (el borrado es de a uno) |
| `pb_crear_coleccion`, `pb_actualizar_coleccion` | Crean colecciones y agregan o modifican campos y reglas |

### Límites y riesgos

- El servidor entra como **superusuario**, que **ignora las reglas de acceso** de las colecciones: puede ver las consultas de todos los usuarios y modificar o borrar registros que la aplicación trata como inmutables.
- Puede **escribir y borrar datos**. Claude Code pide aprobación para cada herramienta; revisá cada llamada antes de aceptarla.
- No accede a colecciones del sistema (nombre que empieza con `_`, como `_superusers`) y no tiene ninguna herramienta para borrar colecciones.
- `pb_actualizar_coleccion` no elimina campos.
- Ni `.mcp.json` ni el código contienen direcciones o contraseñas: todo sale del `.env`.
