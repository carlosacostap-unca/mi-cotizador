"""Mi Cotizador: convierte pesos a dólares y guarda el historial.

Requiere iniciar sesión con un usuario de PocketBase (o registrarse).
"""
import json
import os
import sys
import tkinter as tk
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path
from tkinter import messagebox, ttk

# Dirección del servidor PocketBase (se puede cambiar con la variable de entorno).
POCKETBASE_URL = os.environ.get("POCKETBASE_URL", "http://127.0.0.1:8090").rstrip("/")


def carpeta_base() -> Path:
    """Carpeta del .exe (si está empaquetado) o del script."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent


ARCHIVO_HISTORIAL = carpeta_base() / "historial.txt"


# ---------------------------------------------------------------- conversión
def parsear_numero(texto: str) -> float:
    """Acepta '1.234,56' (formato AR) o '1234.56'."""
    t = texto.strip().replace(" ", "")
    if "," in t:
        t = t.replace(".", "").replace(",", ".")
    return float(t)


def convertir(pesos: float, cotizacion: float) -> float:
    if cotizacion <= 0:
        raise ValueError("La cotización debe ser mayor que cero.")
    return pesos / cotizacion


def guardar_historial(pesos: float, cotizacion: float, dolares: float) -> None:
    ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    linea = f"{ahora} | ${pesos:,.2f} ARS | cotización {cotizacion:,.2f} | US${dolares:,.2f}\n"
    with open(ARCHIVO_HISTORIAL, "a", encoding="utf-8") as f:
        f.write(linea)


# ---------------------------------------------------------------- PocketBase
class ErrorAuth(Exception):
    """Error legible para mostrar al usuario."""


def _pedir(ruta: str, datos: dict | None = None, metodo: str = "POST", token: str | None = None) -> dict:
    cabeceras = {"Content-Type": "application/json"}
    if token:
        cabeceras["Authorization"] = token
    req = urllib.request.Request(
        f"{POCKETBASE_URL}{ruta}",
        data=json.dumps(datos).encode("utf-8") if datos is not None else None,
        headers=cabeceras,
        method=metodo,
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            cuerpo = resp.read().decode("utf-8")
            return json.loads(cuerpo) if cuerpo else {}
    except urllib.error.HTTPError as e:
        try:
            cuerpo = json.loads(e.read().decode("utf-8"))
        except ValueError:
            cuerpo = {}
        raise ErrorAuth(_mensaje_error(cuerpo, e.code)) from None
    except (urllib.error.URLError, TimeoutError, OSError):
        raise ErrorAuth(f"No se pudo conectar con PocketBase en {POCKETBASE_URL}.") from None


def _mensaje_error(cuerpo: dict, codigo: int) -> str:
    detalles = [
        f"{campo}: {info.get('message', '')}"
        for campo, info in (cuerpo.get("data") or {}).items()
        if isinstance(info, dict)
    ]
    if detalles:
        return "\n".join(detalles)
    if codigo == 400:
        return "Email o contraseña incorrectos, o la cuenta está desactivada."
    if codigo in (401, 403):
        return "No tenés permisos para realizar esta acción."
    return cuerpo.get("message") or f"Error del servidor ({codigo})."


def iniciar_sesion(email: str, clave: str) -> dict:
    """Devuelve {'token': ..., 'record': {...}} o lanza ErrorAuth."""
    return _pedir(
        "/api/collections/users/auth-with-password",
        {"identity": email, "password": clave},
    )


def registrar_usuario(email: str, clave: str, clave2: str) -> None:
    _pedir(
        "/api/collections/users/records",
        {"email": email, "password": clave, "passwordConfirm": clave2},
    )


# Administración de cuentas (las reglas de PocketBase exigen rol admin).
def listar_usuarios(token: str) -> list[dict]:
    datos = _pedir("/api/collections/users/records?perPage=200&sort=email", metodo="GET", token=token)
    return datos.get("items", [])


def cambiar_estado(token: str, id_usuario: str, desactivado: bool) -> None:
    _pedir(f"/api/collections/users/records/{id_usuario}", {"desactivado": desactivado}, "PATCH", token)


def resetear_clave(token: str, id_usuario: str, clave: str) -> None:
    _pedir(
        f"/api/collections/users/records/{id_usuario}",
        {"password": clave, "passwordConfirm": clave},
        "PATCH",
        token,
    )


# ---------------------------------------------------------------- pantallas
class PantallaLogin(ttk.Frame):
    def __init__(self, app: "App") -> None:
        super().__init__(app, padding=20)
        self.app = app

        ttk.Label(self, text="Iniciar sesión", font=("Segoe UI", 14, "bold")).grid(
            row=0, column=0, columnspan=2, pady=(0, 10)
        )
        ttk.Label(self, text="Email:").grid(row=1, column=0, sticky="w", pady=5)
        self.email = ttk.Entry(self, width=28)
        self.email.grid(row=1, column=1, pady=5)
        ttk.Label(self, text="Contraseña:").grid(row=2, column=0, sticky="w", pady=5)
        self.clave = ttk.Entry(self, width=28, show="•")
        self.clave.grid(row=2, column=1, pady=5)

        ttk.Button(self, text="Iniciar sesión", command=self.enviar).grid(
            row=3, column=0, columnspan=2, pady=(12, 4)
        )
        ttk.Button(
            self, text="¿No tenés cuenta? Registrate", command=lambda: app.mostrar("registro")
        ).grid(row=4, column=0, columnspan=2)

    def al_mostrar(self) -> None:
        self.clave.delete(0, tk.END)
        self.email.focus()

    def enviar(self) -> None:
        email, clave = self.email.get().strip(), self.clave.get()
        if not email or not clave:
            messagebox.showerror("Datos incompletos", "Ingresá email y contraseña.")
            return
        try:
            datos = iniciar_sesion(email, clave)
        except ErrorAuth as e:
            messagebox.showerror("No se pudo iniciar sesión", str(e))
            return
        self.app.iniciar(datos, email)


class PantallaRegistro(ttk.Frame):
    def __init__(self, app: "App") -> None:
        super().__init__(app, padding=20)
        self.app = app

        ttk.Label(self, text="Crear cuenta", font=("Segoe UI", 14, "bold")).grid(
            row=0, column=0, columnspan=2, pady=(0, 10)
        )
        ttk.Label(self, text="Email:").grid(row=1, column=0, sticky="w", pady=5)
        self.email = ttk.Entry(self, width=28)
        self.email.grid(row=1, column=1, pady=5)
        ttk.Label(self, text="Contraseña:").grid(row=2, column=0, sticky="w", pady=5)
        self.clave = ttk.Entry(self, width=28, show="•")
        self.clave.grid(row=2, column=1, pady=5)
        ttk.Label(self, text="Repetir contraseña:").grid(row=3, column=0, sticky="w", pady=5)
        self.clave2 = ttk.Entry(self, width=28, show="•")
        self.clave2.grid(row=3, column=1, pady=5)
        ttk.Label(self, text="Mínimo 8 caracteres.", foreground="gray").grid(
            row=4, column=0, columnspan=2, sticky="w"
        )

        ttk.Button(self, text="Registrarme", command=self.enviar).grid(
            row=5, column=0, columnspan=2, pady=(12, 4)
        )
        ttk.Button(
            self, text="Ya tengo cuenta. Volver", command=lambda: app.mostrar("login")
        ).grid(row=6, column=0, columnspan=2)

    def al_mostrar(self) -> None:
        for campo in (self.email, self.clave, self.clave2):
            campo.delete(0, tk.END)
        self.email.focus()

    def enviar(self) -> None:
        email, clave, clave2 = self.email.get().strip(), self.clave.get(), self.clave2.get()
        if not email or not clave:
            messagebox.showerror("Datos incompletos", "Ingresá email y contraseña.")
            return
        if clave != clave2:
            messagebox.showerror("Contraseñas distintas", "Las contraseñas no coinciden.")
            return
        try:
            registrar_usuario(email, clave, clave2)
            datos = iniciar_sesion(email, clave)
        except ErrorAuth as e:
            messagebox.showerror("No se pudo registrar", str(e))
            return
        self.app.iniciar(datos, email)


class PantallaConversor(ttk.Frame):
    def __init__(self, app: "App") -> None:
        super().__init__(app, padding=20)
        self.app = app

        self.saludo = ttk.Label(self, text="", foreground="gray")
        self.saludo.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 8))

        ttk.Label(self, text="Monto en pesos:").grid(row=1, column=0, sticky="w", pady=5)
        self.monto = ttk.Entry(self, width=22)
        self.monto.grid(row=1, column=1, pady=5)

        ttk.Label(self, text="Cotización del dólar:").grid(row=2, column=0, sticky="w", pady=5)
        self.cotizacion = ttk.Entry(self, width=22)
        self.cotizacion.grid(row=2, column=1, pady=5)

        ttk.Button(self, text="Convertir", command=self.on_convertir).grid(
            row=3, column=0, columnspan=2, pady=12
        )

        self.resultado = ttk.Label(self, text="", font=("Segoe UI", 14, "bold"))
        self.resultado.grid(row=4, column=0, columnspan=2)

        self.boton_panel = ttk.Button(
            self, text="Panel de administración", command=lambda: app.mostrar("admin")
        )
        self.boton_panel.grid(row=5, column=0, columnspan=2, pady=(14, 0))
        ttk.Button(self, text="Cerrar sesión", command=self.cerrar_sesion).grid(
            row=6, column=0, columnspan=2, pady=(6, 0)
        )

    def al_mostrar(self) -> None:
        self.saludo.config(text=f"Sesión: {self.app.usuario}")
        self.resultado.config(text="")
        if self.app.es_admin:
            self.boton_panel.grid()
        else:
            self.boton_panel.grid_remove()
        self.monto.focus()

    def cerrar_sesion(self) -> None:
        self.app.cerrar_sesion()
        for campo in (self.monto, self.cotizacion):
            campo.delete(0, tk.END)

    def on_convertir(self) -> None:
        try:
            pesos = parsear_numero(self.monto.get())
            cot = parsear_numero(self.cotizacion.get())
        except ValueError:
            messagebox.showerror("Dato inválido", "Ingresá números válidos en ambos campos.")
            return
        try:
            dolares = convertir(pesos, cot)
        except ValueError as e:
            messagebox.showerror("Dato inválido", str(e))
            return

        self.resultado.config(text=f"US$ {dolares:,.2f}")
        try:
            guardar_historial(pesos, cot, dolares)
        except OSError as e:
            messagebox.showwarning("Historial", f"No se pudo guardar el historial:\n{e}")


class PantallaAdmin(ttk.Frame):
    """Panel para listar cuentas, desactivarlas y resetear contraseñas."""

    def __init__(self, app: "App") -> None:
        super().__init__(app, padding=15)
        self.app = app
        self.cuentas: dict[str, dict] = {}

        ttk.Label(self, text="Panel de administración", font=("Segoe UI", 14, "bold")).grid(
            row=0, column=0, sticky="w", pady=(0, 8)
        )
        columnas = ("email", "rol", "estado", "creada")
        self.tabla = ttk.Treeview(self, columns=columnas, show="headings", height=10, selectmode="browse")
        for col, titulo, ancho in (
            ("email", "Email", 240), ("rol", "Rol", 70), ("estado", "Estado", 90), ("creada", "Creada", 100)
        ):
            self.tabla.heading(col, text=titulo)
            self.tabla.column(col, width=ancho, anchor="w")
        self.tabla.grid(row=1, column=0, sticky="nsew")
        barra = ttk.Scrollbar(self, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=barra.set)
        barra.grid(row=1, column=1, sticky="ns")

        botones = ttk.Frame(self)
        botones.grid(row=2, column=0, columnspan=2, pady=(10, 0), sticky="w")
        ttk.Button(botones, text="Actualizar", command=self.cargar).pack(side="left", padx=(0, 6))
        ttk.Button(botones, text="Activar / Desactivar", command=self.alternar_estado).pack(side="left", padx=6)
        ttk.Button(botones, text="Resetear contraseña", command=self.resetear).pack(side="left", padx=6)
        ttk.Button(botones, text="Abrir conversor", command=lambda: app.mostrar("conversor")).pack(
            side="left", padx=6
        )
        ttk.Button(botones, text="Cerrar sesión", command=app.cerrar_sesion).pack(side="left", padx=6)

    def al_mostrar(self) -> None:
        self.cargar()

    def cargar(self) -> None:
        try:
            usuarios = listar_usuarios(self.app.token)
        except ErrorAuth as e:
            messagebox.showerror("No se pudo cargar la lista", str(e))
            return
        self.cuentas = {u["id"]: u for u in usuarios}
        self.tabla.delete(*self.tabla.get_children())
        for u in usuarios:
            self.tabla.insert(
                "", "end", iid=u["id"],
                values=(
                    u.get("email") or "(oculto)",
                    u.get("rol") or "usuario",
                    "Desactivada" if u.get("desactivado") else "Activa",
                    (u.get("created") or "")[:10],
                ),
            )

    def _seleccionada(self) -> dict | None:
        sel = self.tabla.selection()
        if not sel:
            messagebox.showinfo("Seleccioná una cuenta", "Elegí una cuenta de la lista primero.")
            return None
        return self.cuentas[sel[0]]

    def alternar_estado(self) -> None:
        cuenta = self._seleccionada()
        if not cuenta:
            return
        if cuenta["id"] == self.app.id_usuario:
            messagebox.showwarning("Acción no permitida", "No podés desactivar tu propia cuenta.")
            return
        nuevo = not cuenta.get("desactivado")
        accion = "desactivar" if nuevo else "activar"
        if not messagebox.askyesno("Confirmar", f"¿Querés {accion} la cuenta {cuenta.get('email')}?"):
            return
        try:
            cambiar_estado(self.app.token, cuenta["id"], nuevo)
        except ErrorAuth as e:
            messagebox.showerror("No se pudo cambiar el estado", str(e))
            return
        self.cargar()

    def resetear(self) -> None:
        cuenta = self._seleccionada()
        if not cuenta:
            return
        dialogo = DialogoClave(self, cuenta.get("email") or cuenta["id"])
        self.wait_window(dialogo)
        if not dialogo.clave:
            return
        try:
            resetear_clave(self.app.token, cuenta["id"], dialogo.clave)
        except ErrorAuth as e:
            messagebox.showerror("No se pudo resetear la contraseña", str(e))
            return
        messagebox.showinfo("Listo", "La contraseña se actualizó. Comunicásela al usuario.")


class DialogoClave(tk.Toplevel):
    """Pide una contraseña nueva (dos veces). Deja el resultado en `self.clave`."""

    def __init__(self, padre: tk.Misc, email: str) -> None:
        super().__init__(padre)
        self.title("Resetear contraseña")
        self.resizable(False, False)
        self.clave: str | None = None
        marco = ttk.Frame(self, padding=15)
        marco.grid()
        ttk.Label(marco, text=f"Nueva contraseña para {email}").grid(row=0, column=0, columnspan=2, pady=(0, 8))
        ttk.Label(marco, text="Contraseña:").grid(row=1, column=0, sticky="w", pady=4)
        self.c1 = ttk.Entry(marco, width=26, show="•")
        self.c1.grid(row=1, column=1)
        ttk.Label(marco, text="Repetir:").grid(row=2, column=0, sticky="w", pady=4)
        self.c2 = ttk.Entry(marco, width=26, show="•")
        self.c2.grid(row=2, column=1)
        ttk.Label(marco, text="Mínimo 8 caracteres.", foreground="gray").grid(
            row=3, column=0, columnspan=2, sticky="w"
        )
        botones = ttk.Frame(marco)
        botones.grid(row=4, column=0, columnspan=2, pady=(10, 0))
        ttk.Button(botones, text="Guardar", command=self.aceptar).pack(side="left", padx=4)
        ttk.Button(botones, text="Cancelar", command=self.destroy).pack(side="left", padx=4)
        self.bind("<Return>", lambda _e: self.aceptar())
        self.bind("<Escape>", lambda _e: self.destroy())
        self.transient(padre.winfo_toplevel())
        self.grab_set()
        self.c1.focus()

    def aceptar(self) -> None:
        if len(self.c1.get()) < 8:
            messagebox.showerror("Contraseña inválida", "Debe tener al menos 8 caracteres.", parent=self)
            return
        if self.c1.get() != self.c2.get():
            messagebox.showerror("Contraseñas distintas", "Las contraseñas no coinciden.", parent=self)
            return
        self.clave = self.c1.get()
        self.destroy()


class App(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Mi Cotizador")
        self.resizable(False, False)
        self.usuario: str | None = None
        self.id_usuario: str | None = None
        self.token: str | None = None
        self.rol: str = "usuario"

        self.pantallas = {
            "login": PantallaLogin(self),
            "registro": PantallaRegistro(self),
            "conversor": PantallaConversor(self),
            "admin": PantallaAdmin(self),
        }
        self.actual: str | None = None
        self.bind("<Return>", self._on_enter)
        self.mostrar("login")

    @property
    def es_admin(self) -> bool:
        return bool(self.token) and self.rol == "admin"

    def iniciar(self, datos: dict, email: str) -> None:
        """Guarda la sesión y abre la pantalla que corresponde al rol."""
        registro = datos.get("record", {})
        self.usuario = registro.get("email", email)
        self.id_usuario = registro.get("id")
        self.token = datos.get("token")
        self.rol = registro.get("rol") or "usuario"
        self.mostrar("admin" if self.es_admin else "conversor")

    def cerrar_sesion(self) -> None:
        self.usuario = self.id_usuario = self.token = None
        self.rol = "usuario"
        self.mostrar("login")

    def mostrar(self, nombre: str) -> None:
        # El conversor solo se abre con sesión iniciada; el panel, solo para admins.
        if nombre == "conversor" and not self.usuario:
            nombre = "login"
        if nombre == "admin" and not self.es_admin:
            nombre = "conversor" if self.usuario else "login"
        if self.actual:
            self.pantallas[self.actual].grid_remove()
        self.actual = nombre
        pantalla = self.pantallas[nombre]
        pantalla.grid()
        pantalla.al_mostrar()

    def _on_enter(self, _evento) -> None:
        pantalla = self.pantallas[self.actual]
        accion = {"login": "enviar", "registro": "enviar", "conversor": "on_convertir"}.get(self.actual)
        if accion:
            getattr(pantalla, accion)()


if __name__ == "__main__":
    App().mainloop()
