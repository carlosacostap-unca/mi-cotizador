"""Registra la cotización del dólar (divisas) del Banco Nación.

Entra a la página de cotizaciones del BNA (dirección en BNA_URL, del .env),
lee la compra y la venta de "Dolar U.S.A" de la tabla "Cotización Divisas" y
agrega una fila a cotizaciones_bna.csv con la fecha y hora de la consulta.

Uso:
    python cotizaciones_bna.py [--archivo RUTA]

Cada ejecución hace UNA consulta a la página y guarda UNA fila. Para registrar
cada tanto, programalo con el Programador de tareas de Windows (ver README).
Si no se puede leer la cotización con certeza, no escribe nada.

El CSV usa ";" como separador y coma decimal, UTF-8 con BOM: se abre directo
en Excel en español.

Códigos de salida: 0 bien, 1 no se pudo consultar, leer o guardar, 2 falta configuración.
"""
import argparse
import csv
import math
import os
import sys
import urllib.error
import urllib.request
from datetime import date, datetime
from html.parser import HTMLParser
from pathlib import Path

from entorno import cargar_env

cargar_env()

RAIZ = Path(sys.executable).parent if getattr(sys, "frozen", False) else Path(__file__).resolve().parent
ARCHIVO_POR_DEFECTO = RAIZ / "cotizaciones_bna.csv"
ENCABEZADO = ["fecha_hora_consulta", "fecha_banco", "compra", "venta"]
MONEDA = "dolar u.s.a"  # nombre de la fila, comparado sin mayúsculas
TIMEOUT = 20


class ErrorBNA(Exception):
    """Error legible para mostrar por pantalla."""


# ------------------------------------------------------------------ lectura
class _AnalizadorDivisas(HTMLParser):
    """Junta el encabezado de fecha y las filas de la tabla dentro de <div id="divisas">."""

    def __init__(self) -> None:
        super().__init__()
        self.profundidad = 0  # niveles de <div> abiertos dentro del contenedor de divisas
        self.dentro = False
        self.texto: list[str] | None = None
        self.en_fecha = False
        self.en_celda = False
        self.fila: list[str] | None = None
        self.filas: list[list[str]] = []
        self.fecha: str | None = None
        self.encontrado = False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "div":
            if self.dentro:
                self.profundidad += 1
            elif a.get("id") == "divisas":
                self.dentro, self.encontrado, self.profundidad = True, True, 1
            return
        if not self.dentro:
            return
        if tag == "th" and "fechaCot" in (a.get("class") or "").split():
            self.en_fecha, self.texto = True, []
        elif tag == "tr":
            self.fila = []
        elif tag == "td" and self.fila is not None:
            self.en_celda, self.texto = True, []

    def handle_endtag(self, tag):
        if tag == "div" and self.dentro:
            self.profundidad -= 1
            if self.profundidad == 0:
                self.dentro = False
            return
        if not self.dentro:
            return
        if tag == "th" and self.en_fecha:
            self.fecha, self.en_fecha = "".join(self.texto or []).strip(), False
        elif tag == "td" and self.en_celda and self.fila is not None:
            self.fila.append(" ".join("".join(self.texto or []).split()))
            self.en_celda = False
        elif tag == "tr" and self.fila is not None:
            self.filas.append(self.fila)
            self.fila = None

    def handle_data(self, data):
        if (self.en_fecha or self.en_celda) and self.texto is not None:
            self.texto.append(data)


def parsear_numero(texto: str) -> float:
    """Acepta '1550.5000' o '1530,00' (y '1.530,00'); debe ser un número positivo."""
    t = texto.strip().replace(" ", "")
    if "," in t:
        t = t.replace(".", "").replace(",", ".")
    try:
        valor = float(t)
    except ValueError:
        raise ErrorBNA(f"El valor «{texto}» no es un número.") from None
    if not math.isfinite(valor) or valor <= 0:
        raise ErrorBNA(f"El valor «{texto}» no es un número mayor que cero.")
    return valor


def leer_cotizacion(html: str) -> tuple[date, float, float]:
    """Devuelve (fecha del banco, compra, venta) del dólar en la tabla de divisas."""
    analizador = _AnalizadorDivisas()
    analizador.feed(html)
    cambio = ("No pude leer la cotización: la página puede haber cambiado de estructura. "
              "Revisá la tabla «Cotización Divisas» del sitio.")
    if not analizador.encontrado:
        raise ErrorBNA(f"No encontré la tabla de divisas. {cambio}")
    fila = next((f for f in analizador.filas if len(f) >= 3 and f[0].strip().lower() == MONEDA), None)
    if fila is None:
        raise ErrorBNA(f"No encontré la fila «Dolar U.S.A» en la tabla de divisas. {cambio}")
    if not analizador.fecha:
        raise ErrorBNA(f"No encontré la fecha de la cotización. {cambio}")
    try:
        fecha = datetime.strptime(analizador.fecha, "%d/%m/%Y").date()
    except ValueError:
        raise ErrorBNA(f"La fecha «{analizador.fecha}» no tiene el formato esperado (dd/mm/aaaa). {cambio}") from None
    return fecha, parsear_numero(fila[1]), parsear_numero(fila[2])


def obtener_html(url: str, timeout: float = TIMEOUT) -> str:
    """Una única solicitud, sin reintentos y con un identificador genérico."""
    req = urllib.request.Request(url, headers={"User-Agent": "MiCotizador/1.0", "Accept": "text/html"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read().decode(resp.headers.get_content_charset() or "utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        raise ErrorBNA(f"La página respondió con un error ({e.code}).") from None
    except (urllib.error.URLError, TimeoutError, OSError):
        raise ErrorBNA("No pude conectarme con la página del Banco Nación.") from None


# ---------------------------------------------------------------- escritura
def _decimal(valor: float) -> str:
    return f"{valor:.4f}".replace(".", ",")


def guardar(ruta: Path, consulta: datetime, fecha_banco: date, compra: float, venta: float) -> None:
    """Agrega una fila (con el encabezado si el archivo no existe), todo en una sola escritura."""
    nuevo = not ruta.exists() or ruta.stat().st_size == 0
    fila = [consulta.strftime("%Y-%m-%d %H:%M:%S"), fecha_banco.isoformat(), _decimal(compra), _decimal(venta)]
    try:
        with open(ruta, "w" if nuevo else "a", encoding="utf-8-sig" if nuevo else "utf-8", newline="") as f:
            escritor = csv.writer(f, delimiter=";")
            if nuevo:
                escritor.writerow(ENCABEZADO)
            escritor.writerow(fila)
    except OSError as e:
        pista = " ¿Está abierto en otro programa, como Excel?" if isinstance(e, PermissionError) else ""
        raise ErrorBNA(f"No pude escribir {ruta} ({e.strerror or e}).{pista}") from None


# ----------------------------------------------------------------- programa
def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Guarda la compra y venta del dólar (divisas) del Banco Nación.")
    ap.add_argument("--archivo", type=Path, default=ARCHIVO_POR_DEFECTO,
                    help=f"archivo CSV de destino (por defecto {ARCHIVO_POR_DEFECTO.name})")
    args = ap.parse_args(argv)

    url = os.environ.get("BNA_URL", "").strip()
    if not url:
        print("Falta configurar BNA_URL en el archivo .env (ver .env.example). No hice ninguna consulta.")
        return 2
    try:
        html = obtener_html(url)
        fecha, compra, venta = leer_cotizacion(html)
        guardar(args.archivo, datetime.now(), fecha, compra, venta)
    except ErrorBNA as e:
        print(f"Error: {e}")
        return 1
    print(f"Dólar (divisas) del Banco Nación al {fecha:%d/%m/%Y}: compra {_decimal(compra)} | venta {_decimal(venta)}")
    print(f"Guardado en {args.archivo}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
