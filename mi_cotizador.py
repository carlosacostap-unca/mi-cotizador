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


def _pedir(ruta: str, datos: dict) -> dict:
    req = urllib.request.Request(
        f"{POCKETBASE_URL}{ruta}",
        data=json.dumps(datos).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode("utf-8"))
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
        return "Email o contraseña incorrectos."
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
        self.app.usuario = datos.get("record", {}).get("email", email)
        self.app.mostrar("conversor")


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
        self.app.usuario = datos.get("record", {}).get("email", email)
        self.app.mostrar("conversor")


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

        ttk.Button(self, text="Cerrar sesión", command=self.cerrar_sesion).grid(
            row=5, column=0, columnspan=2, pady=(14, 0)
        )

    def al_mostrar(self) -> None:
        self.saludo.config(text=f"Sesión: {self.app.usuario}")
        self.resultado.config(text="")
        self.monto.focus()

    def cerrar_sesion(self) -> None:
        self.app.usuario = None
        for campo in (self.monto, self.cotizacion):
            campo.delete(0, tk.END)
        self.app.mostrar("login")

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


class App(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Mi Cotizador")
        self.resizable(False, False)
        self.usuario: str | None = None

        self.pantallas = {
            "login": PantallaLogin(self),
            "registro": PantallaRegistro(self),
            "conversor": PantallaConversor(self),
        }
        self.actual: str | None = None
        self.bind("<Return>", self._on_enter)
        self.mostrar("login")

    def mostrar(self, nombre: str) -> None:
        # El conversor solo se abre con sesión iniciada.
        if nombre == "conversor" and not self.usuario:
            nombre = "login"
        if self.actual:
            self.pantallas[self.actual].grid_remove()
        self.actual = nombre
        pantalla = self.pantallas[nombre]
        pantalla.grid()
        pantalla.al_mostrar()

    def _on_enter(self, _evento) -> None:
        pantalla = self.pantallas[self.actual]
        accion = {"login": "enviar", "registro": "enviar", "conversor": "on_convertir"}[self.actual]
        getattr(pantalla, accion)()


if __name__ == "__main__":
    App().mainloop()
