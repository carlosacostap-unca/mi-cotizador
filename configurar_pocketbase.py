"""Configura la colección `users` de PocketBase para Mi Cotizador.

- Agrega el campo `rol` (usuario / admin) y `desactivado` (bool).
- Define las reglas para que solo un admin pueda listar cuentas,
  desactivarlas y resetear contraseñas.
- Opcionalmente crea el primer admin.

Es idempotente: se puede ejecutar varias veces.

Uso (credenciales del superusuario por variables de entorno o se piden):
    set PB_SUPERUSER_EMAIL=...
    set PB_SUPERUSER_PASSWORD=...
    python configurar_pocketbase.py [--crear-admin EMAIL]
"""
import argparse
import getpass
import json
import os
import secrets
import string
import urllib.error
import urllib.request

URL = os.environ.get("POCKETBASE_URL", "http://127.0.0.1:8090").rstrip("/")

# Un admin válido: rol admin y cuenta no desactivada.
ES_ADMIN = '@request.auth.rol = "admin" && @request.auth.desactivado = false'
NO_TOCA_PRIVILEGIOS = '@request.body.rol:isset = false && @request.body.desactivado:isset = false'

REGLAS = {
    # Cada usuario ve su propia cuenta; el admin ve todas.
    "listRule": f'id = @request.auth.id || ({ES_ADMIN})',
    "viewRule": f'id = @request.auth.id || ({ES_ADMIN})',
    # El registro es público, pero nadie puede darse rol ni estado al crearse.
    "createRule": NO_TOCA_PRIVILEGIOS,
    # Cada uno edita lo suyo sin tocar rol/desactivado; el admin edita cualquiera
    # (desactivar, cambiar contraseña, cambiar rol).
    "updateRule": f'(id = @request.auth.id && {NO_TOCA_PRIVILEGIOS}) || ({ES_ADMIN})',
    "deleteRule": f'id = @request.auth.id || ({ES_ADMIN})',
    # Una cuenta desactivada no puede iniciar sesión.
    "authRule": "desactivado = false",
    # El admin gestiona cuentas ajenas: ve su email y cambia su contraseña
    # sin necesitar la anterior.
    "manageRule": ES_ADMIN,
}

CAMPOS = [
    {"type": "select", "name": "rol", "values": ["usuario", "admin"], "maxSelect": 1},
    {"type": "bool", "name": "desactivado"},
]


def pedir(metodo, ruta, datos=None, token=None):
    h = {"Content-Type": "application/json"}
    if token:
        h["Authorization"] = token
    req = urllib.request.Request(
        URL + ruta, data=json.dumps(datos).encode() if datos is not None else None,
        headers=h, method=metodo,
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            t = r.read()
            return json.loads(t) if t else {}
    except urllib.error.HTTPError as e:
        raise SystemExit(f"Error {e.code} en {metodo} {ruta}: {e.read().decode()}")


def configurar_consultas(token: str, id_users: str) -> None:
    """Crea (o actualiza) la colección `consultas`: el historial de conversiones."""
    campos = [
        {"type": "relation", "name": "usuario", "collectionId": id_users,
         "required": True, "maxSelect": 1, "cascadeDelete": True},
        {"type": "number", "name": "monto"},
        {"type": "number", "name": "cotizacion", "required": True},
        {"type": "number", "name": "resultado"},
        # Fecha y hora asignadas por el servidor al crear.
        {"type": "autodate", "name": "fecha", "onCreate": True, "onUpdate": False},
    ]
    # Cada usuario crea y lee solo lo suyo. Sin regla de update/delete (null):
    # solo un superusuario puede modificar o borrar, el historial es inmutable.
    reglas = {
        "listRule": "usuario = @request.auth.id",
        "viewRule": "usuario = @request.auth.id",
        "createRule": '@request.auth.id != "" && @request.body.usuario = @request.auth.id',
        "updateRule": None,
        "deleteRule": None,
    }
    try:
        col = pedir("GET", "/api/collections/consultas", token=token)
    except SystemExit:
        col = None
    if col is None:
        pedir("POST", "/api/collections", {"name": "consultas", "type": "base", "fields": campos, **reglas}, token)
        print("Colección consultas creada.")
    else:
        existentes = {c["name"] for c in col["fields"]}
        todos = col["fields"] + [c for c in campos if c["name"] not in existentes]
        pedir("PATCH", "/api/collections/consultas", {"fields": todos, **reglas}, token)
        print("Colección consultas actualizada.")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--crear-admin", metavar="EMAIL", help="crea un usuario admin con clave aleatoria")
    args = ap.parse_args()

    email = os.environ.get("PB_SUPERUSER_EMAIL") or input("Email del superusuario: ")
    clave = os.environ.get("PB_SUPERUSER_PASSWORD") or getpass.getpass("Contraseña del superusuario: ")
    token = pedir("POST", "/api/collections/_superusers/auth-with-password",
                  {"identity": email, "password": clave})["token"]

    col = pedir("GET", "/api/collections/users", token=token)
    existentes = {c["name"] for c in col["fields"]}
    campos = col["fields"] + [c for c in CAMPOS if c["name"] not in existentes]
    pedir("PATCH", "/api/collections/users", {"fields": campos, **REGLAS}, token)
    print("Colección users configurada (campos rol y desactivado + reglas).")

    configurar_consultas(token, col["id"])

    if args.crear_admin:
        alfabeto = string.ascii_letters + string.digits
        clave_admin = "".join(secrets.choice(alfabeto) for _ in range(20))
        pedir("POST", "/api/collections/users/records", {
            "email": args.crear_admin, "password": clave_admin,
            "passwordConfirm": clave_admin, "rol": "admin", "emailVisibility": True,
        }, token)
        print(f"Admin creado: {args.crear_admin}")
        print(f"Contraseña: {clave_admin}")


if __name__ == "__main__":
    main()
