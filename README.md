# Mi Cotizador

Aplicación de escritorio (Python y Tkinter) que convierte pesos a dólares. Inicia sesión con los usuarios de PocketBase, trae la cotización del dólar oficial y guarda el historial de cada usuario en PocketBase. Los requisitos del proyecto están en `openspec/specs/`.

## Configuración

Copiá `.env.example` como `.env` y completá los valores (el `.env` no se sube a Git). Para dejar PocketBase listo (campos, reglas y colecciones) ejecutá `python configurar_pocketbase.py`.

## Asistente (chat con OpenAI)

El botón **Asistente** del conversor abre un chat donde se piden cosas en lenguaje natural ("convertime 150 mil pesos", "¿a cuánto está el dólar?", "actualizá la cotización", "mostrame mis últimas conversiones"). El modelo de OpenAI interpreta el pedido y la app lo resuelve con sus propias funciones, usando tu sesión:

- convertir pesos a dólares (se guarda en tu historial igual que con el botón; sin cotización indicada usa la venta del dólar oficial),
- consultar la cotización del dólar oficial,
- actualizar la cotización cargada en el conversor,
- ver tu historial (hasta 50 conversiones).

**No** puede administrar cuentas ni contraseñas, ni siquiera si sos admin.

**Configuración** (en el `.env`, ver `.env.example`; las tres son obligatorias y no tienen valor por defecto): `OPENAI_URL` (la dirección del endpoint de chat completions), `OPENAI_MODEL` (el nombre del modelo, tal como figura en tu cuenta de OpenAI) y `OPENAI_API_KEY` (tu clave). Hay una cuarta, **opcional**: `OPENAI_REASONING_EFFORT`. Algunos modelos razonan por defecto y la API de chat no admite funciones en ese modo; si el chat muestra un error 400 que menciona `reasoning_effort`, definila como `none`. Si falta alguna de las tres obligatorias, el chat avisa cuál y el resto de la app funciona igual. La clave nunca se muestra, no se guarda en ningún archivo y no viaja dentro del `.exe`: se lee del `.env`.

**Costo y privacidad**
- Es un servicio de pago: cada mensaje consume crédito de la cuenta de la clave. Por mensaje, el asistente hace como máximo 5 rondas de funciones y se envían los últimos 20 mensajes de la conversación.
- Lo que escribís y los resultados de las funciones (por ejemplo tu historial, si lo pedís) **se envían a OpenAI**. No se envían tu contraseña, tu email ni el token de sesión. La pantalla lo recuerda con un aviso.
- La conversación vive solo en memoria y se borra al cerrar sesión.

La lógica del chat está en `asistente.py`. Se probó con un servidor local que imita la API; la primera vez que agregues tu clave, probá un pedido de cada tipo.

## Cotizaciones del Banco Nación

`cotizaciones_bna.py` entra a la página de cotizaciones del Banco Nación, lee la **compra y la venta del dólar de la tabla "Cotización Divisas"** y agrega una fila a `cotizaciones_bna.csv` (fuera de Git) con la fecha y hora de la consulta, la fecha que informa el banco, la compra y la venta. Solo usa la biblioteca estándar de Python.

1. Definí `BNA_URL` en el `.env` (la dirección de la página de cotizaciones).
2. Ejecutá `python cotizaciones_bna.py` (con `--archivo RUTA` para otro destino).

Cada ejecución hace **una** consulta y guarda **una** fila, aunque el banco no haya cambiado el valor. Si la página no responde o cambió de forma que no se puede leer con certeza, no escribe nada y termina con código 1 (2 si falta `BNA_URL`). La tabla de divisas trae solo la fecha, sin hora, por eso se guarda la hora de tu consulta.

El CSV usa `;` como separador y coma decimal, en UTF-8 con BOM: se abre directo en Excel en español. Cerralo en Excel antes de la siguiente ejecución, porque Excel bloquea el archivo.

Para registrar la cotización todos los días, programalo con el Programador de tareas de Windows (ajustá la hora y la ruta):

```
schtasks /Create /SC DAILY /ST 17:30 /TN "Cotizaciones BNA" /TR "python C:\ruta\al\proyecto\cotizaciones_bna.py"
```

El `.env` se busca junto al programa. Ejecutalo con moderación: es el sitio de un tercero y el programa no limita la frecuencia por sí mismo. Si el banco rediseña la página, la lectura va a fallar con un aviso hasta que se ajuste el programa.

## Prueba de punta a punta con capturas

`capturas_conversiones.py` abre Mi Cotizador, inicia sesión con el usuario de prueba, hace diez conversiones con montos distintos (1.000 a 1.000.000), guarda una captura de cada resultado en `capturas/<fecha>/` (carpeta fuera de Git) y comprueba contra PocketBase que las diez quedaron guardadas con el resultado correcto (monto ÷ cotización). Solo funciona en Windows.

1. `pip install -r requirements.txt`.
2. Completá en el `.env`: `PB_TEST_EMAIL` y `PB_TEST_PASSWORD`, además de `POCKETBASE_URL` y `DOLARAPI_URL`.
3. Creá el usuario de prueba una sola vez: `python configurar_pocketbase.py --crear-usuario-prueba`. Es un usuario común y no se borra: el historial acumula las conversiones de cada ejecución.
4. Con PocketBase en ejecución: `python capturas_conversiones.py` (abre el código fuente) o `python capturas_conversiones.py --exe` (abre `dist/Mi Cotizador.exe`). `--cuenta N` cambia la cuenta regresiva de 5 segundos.

Mientras corre, **el programa toma el teclado y la ventana activa**: no toques nada. Para interrumpirlo, mové el mouse a una esquina de la pantalla (o Ctrl+C durante la cuenta regresiva). Termina con código 0 si las diez coinciden, 1 si alguna no coincide, 2 si falta configuración y 3 si falla al operar la ventana.

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
