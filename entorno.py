"""Carga variables de configuración desde un archivo .env (sin dependencias).

Busca `.env` en este orden y usa el primero que exista:
1. junto al ejecutable (si está empaquetado) o junto al script;
2. en la carpeta desde la que se ejecuta;
3. en la carpeta superior (cubre `dist/` dentro del proyecto).
Las variables que ya existen en el entorno tienen prioridad sobre el archivo.
"""
import os
import sys
from pathlib import Path


def carpeta_base() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent


def carpetas_de_busqueda() -> list[Path]:
    base = carpeta_base()
    carpetas: list[Path] = []
    for c in (base, Path.cwd(), base.parent):
        if c not in carpetas:
            carpetas.append(c)
    return carpetas


def cargar_env(ruta: Path | None = None) -> None:
    candidatos = [ruta] if ruta else [c / ".env" for c in carpetas_de_busqueda()]
    for candidato in candidatos:
        try:
            lineas = candidato.read_text(encoding="utf-8-sig").splitlines()
        except OSError:
            continue
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
        return  # se usó el primer .env encontrado


def donde_se_busco() -> str:
    """Texto con las carpetas donde se busca el .env (para los mensajes de error)."""
    return ", ".join(str(c) for c in carpetas_de_busqueda())
