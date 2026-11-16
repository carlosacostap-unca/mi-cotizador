"""Carga variables de configuración desde un archivo .env (sin dependencias).

Busca `.env` junto al ejecutable (si está empaquetado) o junto al script.
Las variables que ya existen en el entorno tienen prioridad sobre el archivo.
"""
import os
import sys
from pathlib import Path


def carpeta_base() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent


def cargar_env(ruta: Path | None = None) -> None:
    ruta = ruta or carpeta_base() / ".env"
    try:
        lineas = ruta.read_text(encoding="utf-8-sig").splitlines()
    except OSError:
        return  # sin .env: se usan los valores por defecto
    for linea in lineas:
        linea = linea.strip()
        if not linea or linea.startswith("#") or "=" not in linea:
            continue
        clave, valor = linea.split("=", 1)
        clave, valor = clave.strip(), valor.strip()
        if len(valor) >= 2 and valor[0] == valor[-1] and valor[0] in "\"'":
            valor = valor[1:-1]
        if valor:  # un valor vacío no pisa nada
            os.environ.setdefault(clave, valor)
