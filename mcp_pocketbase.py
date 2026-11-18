"""Servidor MCP (stdio) para consultar y modificar la base local de PocketBase.

Lee POCKETBASE_URL, PB_SUPERUSER_EMAIL y PB_SUPERUSER_PASSWORD del archivo .env
(o del entorno) y entra como superusuario. IMPORTANTE: el superusuario ignora
las reglas de acceso de las colecciones.

Límites de seguridad:
- No opera sobre colecciones del sistema (nombre con "_" inicial, p. ej. _superusers).
- No ofrece ninguna herramienta para borrar colecciones.
- Máximo 100 registros por página.

La salida estándar es del protocolo MCP: aquí nunca se usa print().
"""
import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

from mcp.server.fastmcp import FastMCP

from entorno import cargar_env

cargar_env()

MAX_POR_PAGINA = 100
CLAVES_REGLAS = ("listRule", "viewRule", "createRule", "updateRule", "deleteRule", "manageRule", "authRule")
NOMBRE_VALIDO = re.compile(r"[A-Za-z][A-Za-z0-9_]*")

mcp = FastMCP("pocketbase")


class ErrorPB(Exception):
    """Error legible para devolver a Claude (nunca incluye credenciales)."""

    def __init__(self, mensaje: str, codigo: int | None = None) -> None:
        super().__init__(mensaje)
        self.codigo = codigo


# ------------------------------------------------------------------ cliente
_token: str | None = None


def _config() -> tuple[str, str, str]:
    url = os.environ.get("POCKETBASE_URL", "").rstrip("/")
    email = os.environ.get("PB_SUPERUSER_EMAIL", "")
    clave = os.environ.get("PB_SUPERUSER_PASSWORD", "")
    faltan = [n for n, v in (("POCKETBASE_URL", url), ("PB_SUPERUSER_EMAIL", email),
                             ("PB_SUPERUSER_PASSWORD", clave)) if not v]
    if faltan:
        raise ErrorPB("Faltan variables en el .env o el entorno: " + ", ".join(faltan) + ".")
    return url, email, clave


def _mensaje(cuerpo: dict, codigo: int) -> str:
    detalles = [
        f"{campo}: {info.get('message', '')}"
        for campo, info in (cuerpo.get("data") or {}).items()
        if isinstance(info, dict)
    ]
    base = cuerpo.get("message") or f"Error {codigo} de PocketBase."
    return f"{base} " + "; ".join(detalles) if detalles else base


def _http(metodo: str, ruta: str, datos: Any = None, token: str | None = None) -> Any:
    url, _, _ = _config()
    cabeceras = {"Content-Type": "application/json"}
    if token:
        cabeceras["Authorization"] = token
    req = urllib.request.Request(
        url + ruta,
        data=json.dumps(datos).encode("utf-8") if datos is not None else None,
        headers=cabeceras,
        method=metodo,
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            cuerpo = resp.read().decode("utf-8")
            return json.loads(cuerpo) if cuerpo else {}
    except urllib.error.HTTPError as e:
        try:
            detalle = json.loads(e.read().decode("utf-8"))
        except ValueError:
            detalle = {}
        raise ErrorPB(_mensaje(detalle, e.code), e.code) from None
    except (urllib.error.URLError, TimeoutError, OSError):
        raise ErrorPB(f"No se pudo conectar con PocketBase en {url}. ¿Está en ejecución?") from None


def _autenticar() -> str:
    global _token
    _, email, clave = _config()
    try:
        datos = _http("POST", "/api/collections/_superusers/auth-with-password",
                      {"identity": email, "password": clave})
    except ErrorPB as e:
        if e.codigo == 400:
            raise ErrorPB("PocketBase rechazó las credenciales del superusuario "
                          "(revisá PB_SUPERUSER_EMAIL y PB_SUPERUSER_PASSWORD).", 400) from None
        raise
    _token = datos["token"]
    return _token


def _api(metodo: str, ruta: str, datos: Any = None) -> Any:
    """Llamada autenticada; si el token venció, se renueva una vez."""
    token = _token or _autenticar()
    try:
        return _http(metodo, ruta, datos, token)
    except ErrorPB as e:
        if e.codigo not in (401, 403):
            raise
    return _http(metodo, ruta, datos, _autenticar())


def _json(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False, indent=2)


# ------------------------------------------------------- colecciones protegidas
def _es_de_sistema(col: dict) -> bool:
    return col.get("name", "").startswith("_") or bool(col.get("system"))


def _coleccion(referencia: str) -> dict:
    """Devuelve los datos de una colección (por nombre o id), rechazando las de sistema.

    Se resuelve contra PocketBase para que tampoco se pueda saltear la protección
    usando el id interno de una colección de sistema.
    """
    referencia = (referencia or "").strip()
    if not referencia:
        raise ErrorPB("Indicá el nombre de la colección.")
    if referencia.startswith("_"):
        raise ErrorPB(_MENSAJE_SISTEMA)
    if not re.fullmatch(r"[A-Za-z0-9_]+", referencia):
        raise ErrorPB("Nombre de colección inválido: solo letras, números y guion bajo.")
    col = _api("GET", f"/api/collections/{referencia}")
    if _es_de_sistema(col):
        raise ErrorPB(_MENSAJE_SISTEMA)
    return col


_MENSAJE_SISTEMA = (
    "Las colecciones del sistema (nombre que empieza con '_', como _superusers) "
    "están protegidas: este servidor no accede a ellas."
)


def _id(valor: str) -> str:
    if not re.fullmatch(r"[A-Za-z0-9]+", (valor or "").strip()):
        raise ErrorPB("Id de registro inválido.")
    return valor.strip()


# ------------------------------------------------------------------ herramientas
@mcp.tool()
def pb_salud() -> str:
    """Comprueba si PocketBase responde (no requiere credenciales)."""
    return _json(_http("GET", "/api/health"))


@mcp.tool()
def pb_listar_colecciones() -> str:
    """Lista las colecciones no de sistema con su tipo y cantidad de campos."""
    datos = _api("GET", "/api/collections?perPage=200&sort=name")
    return _json([
        {"nombre": c["name"], "tipo": c["type"], "id": c["id"], "campos": len(c.get("fields", []))}
        for c in datos.get("items", []) if not _es_de_sistema(c)
    ])


@mcp.tool()
def pb_ver_coleccion(coleccion: str) -> str:
    """Muestra el esquema (campos y tipos) y las reglas de acceso de una colección."""
    col = _coleccion(coleccion)
    return _json({
        "nombre": col["name"], "tipo": col["type"], "id": col["id"],
        "campos": col.get("fields", []),
        "reglas": {k: col.get(k) for k in CLAVES_REGLAS if k in col},
        "indices": col.get("indexes", []),
    })


@mcp.tool()
def pb_listar_registros(coleccion: str, filtro: str = "", orden: str = "", pagina: int = 1,
                        por_pagina: int = 30, expandir: str = "") -> str:
    """Lista registros de una colección.

    filtro: sintaxis de filtros de PocketBase, p. ej. `usuario = "abc123" && monto > 1000`.
    orden: p. ej. `-fecha` (descendente) o `monto,-fecha`.
    por_pagina: máximo 100.
    expandir: relaciones a expandir, p. ej. `usuario`.
    """
    _coleccion(coleccion)
    limitado = por_pagina > MAX_POR_PAGINA
    por_pagina = max(1, min(por_pagina, MAX_POR_PAGINA))
    parametros = {"page": max(1, pagina), "perPage": por_pagina}
    for clave, valor in (("filter", filtro), ("sort", orden), ("expand", expandir)):
        if valor:
            parametros[clave] = valor
    datos = _api("GET", f"/api/collections/{coleccion}/records?" + urllib.parse.urlencode(parametros))
    if limitado:
        datos["limite_aplicado"] = f"por_pagina se limitó a {MAX_POR_PAGINA}"
    return _json(datos)


@mcp.tool()
def pb_ver_registro(coleccion: str, id: str, expandir: str = "") -> str:
    """Muestra un registro por su id."""
    _coleccion(coleccion)
    ruta = f"/api/collections/{coleccion}/records/{_id(id)}"
    if expandir:
        ruta += "?" + urllib.parse.urlencode({"expand": expandir})
    try:
        return _json(_api("GET", ruta))
    except ErrorPB as e:
        if e.codigo == 404:
            raise ErrorPB(f"Registro no encontrado: {id} en {coleccion}.", 404) from None
        raise


@mcp.tool()
def pb_crear_registro(coleccion: str, datos: dict[str, Any]) -> str:
    """Crea un registro. `datos` es un objeto campo → valor. PocketBase valida los datos."""
    _coleccion(coleccion)
    return _json(_api("POST", f"/api/collections/{coleccion}/records", datos))


@mcp.tool()
def pb_actualizar_registro(coleccion: str, id: str, datos: dict[str, Any]) -> str:
    """Modifica solo los campos indicados en `datos` de un registro existente."""
    _coleccion(coleccion)
    return _json(_api("PATCH", f"/api/collections/{coleccion}/records/{_id(id)}", datos))


@mcp.tool()
def pb_borrar_registro(coleccion: str, id: str) -> str:
    """Borra un registro por su id (de a uno; no hay borrado masivo). Es irreversible."""
    _coleccion(coleccion)
    _api("DELETE", f"/api/collections/{coleccion}/records/{_id(id)}")
    return _json({"borrado": True, "coleccion": coleccion, "id": id})


def _reglas_validas(reglas: dict[str, Any] | None) -> dict[str, Any]:
    reglas = reglas or {}
    invalidas = [k for k in reglas if k not in CLAVES_REGLAS]
    if invalidas:
        raise ErrorPB("Reglas desconocidas: " + ", ".join(invalidas) + ". Válidas: " + ", ".join(CLAVES_REGLAS))
    return reglas


@mcp.tool()
def pb_crear_coleccion(nombre: str, campos: list[dict[str, Any]], tipo: str = "base",
                       reglas: dict[str, Any] | None = None) -> str:
    """Crea una colección (tipo `base`, `auth` o `view`).

    campos: lista de definiciones de campo de PocketBase, p. ej.
    `[{"type": "text", "name": "titulo", "required": true}]`.
    reglas: claves listRule, viewRule, createRule, updateRule, deleteRule (null = solo superusuario).
    """
    if not NOMBRE_VALIDO.fullmatch(nombre or ""):
        raise ErrorPB("Nombre inválido: debe empezar con una letra (no con '_') y usar letras, números o guion bajo.")
    if tipo not in ("base", "auth", "view"):
        raise ErrorPB("tipo debe ser base, auth o view.")
    col = _api("POST", "/api/collections", {"name": nombre, "type": tipo, "fields": campos,
                                            **_reglas_validas(reglas)})
    return _json({"creada": col["name"], "id": col["id"], "tipo": col["type"]})


@mcp.tool()
def pb_actualizar_coleccion(coleccion: str, campos: list[dict[str, Any]] | None = None,
                            reglas: dict[str, Any] | None = None) -> str:
    """Agrega o modifica campos y/o cambia reglas de una colección existente.

    campos: los que tengan el nombre de un campo existente lo modifican (conservan su id,
    así no se pierden datos); los demás se agregan. Esta herramienta no elimina campos.
    reglas: claves listRule, viewRule, createRule, updateRule, deleteRule, manageRule, authRule.
    """
    col = _coleccion(coleccion)
    cambios: dict[str, Any] = dict(_reglas_validas(reglas))
    if campos:
        actuales = {c["name"]: c for c in col.get("fields", [])}
        fusion = dict(actuales)
        for nuevo in campos:
            nombre = nuevo.get("name")
            if not nombre:
                raise ErrorPB("Cada campo necesita `name`.")
            fusion[nombre] = {**actuales[nombre], **nuevo} if nombre in actuales else nuevo
        cambios["fields"] = list(fusion.values())
    if not cambios:
        raise ErrorPB("Indicá campos o reglas para modificar.")
    res = _api("PATCH", f"/api/collections/{col['id']}", cambios)
    return _json({"actualizada": res["name"], "campos": [c["name"] for c in res.get("fields", [])]})


if __name__ == "__main__":
    mcp.run()
