"""Prueba de punta a punta de Mi Cotizador: abre la aplicación real, inicia sesión
con el usuario de prueba, hace diez conversiones con montos distintos, guarda una
captura de cada resultado y verifica que quedaron bien guardadas en PocketBase.

Uso:
    python capturas_conversiones.py            # abre mi_cotizador.py
    python capturas_conversiones.py --exe      # abre dist/Mi Cotizador.exe

Configuración (en el .env): POCKETBASE_URL, DOLARAPI_URL, PB_TEST_EMAIL y
PB_TEST_PASSWORD. El usuario de prueba se crea con
`python configurar_pocketbase.py --crear-usuario-prueba` y NO se borra.

IMPORTANTE: mientras corre, el programa toma el teclado y la ventana activa.
Para interrumpirlo, mové el mouse a una esquina de la pantalla.
Solo funciona en Windows.

Códigos de salida: 0 todo bien, 1 la verificación no coincide, 2 configuración
o requisitos, 3 error al operar la ventana, 130 cancelado.
"""
import argparse
import ctypes
import os
import subprocess
import sys
import time
from ctypes import wintypes
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urlencode

import mi_cotizador as m  # carga el .env y trae el cliente de PocketBase

EMPAQUETADO = getattr(sys, "frozen", False)  # ejecutándose como .exe de PyInstaller
RAIZ = Path(sys.executable).parent if EMPAQUETADO else Path(__file__).resolve().parent


def ubicar_exe() -> Path:
    """Busca Mi Cotizador.exe: junto a este programa, en dist/ o en ../dist/."""
    candidatos = [RAIZ / "Mi Cotizador.exe", RAIZ / "dist" / "Mi Cotizador.exe",
                  RAIZ.parent / "dist" / "Mi Cotizador.exe"]
    return next((c for c in candidatos if c.exists()), candidatos[1])


EXE = ubicar_exe()
TITULO = "Mi Cotizador"
# Fijos y distintos, para poder reproducir una ejecución. Se escriben sin separadores.
MONTOS = [1000, 5000, 12500, 25000, 50000, 75000, 100000, 250000, 500000, 1000000]
TOLERANCIA = 0.01


class ErrorVentana(Exception):
    """No se pudo operar la ventana de la aplicación."""


class Interrumpido(Exception):
    """La persona movió el mouse a una esquina de la pantalla."""


# ------------------------------------------------------------ entrada y ventana
if sys.platform == "win32":
    user32 = ctypes.windll.user32
    user32.SetProcessDPIAware()  # coordenadas y capturas en píxeles reales

    class _KEYBDINPUT(ctypes.Structure):
        _fields_ = [("wVk", wintypes.WORD), ("wScan", wintypes.WORD), ("dwFlags", wintypes.DWORD),
                    ("time", wintypes.DWORD), ("dwExtraInfo", ctypes.c_size_t)]

    class _MOUSEINPUT(ctypes.Structure):
        _fields_ = [("dx", wintypes.LONG), ("dy", wintypes.LONG), ("mouseData", wintypes.DWORD),
                    ("dwFlags", wintypes.DWORD), ("time", wintypes.DWORD), ("dwExtraInfo", ctypes.c_size_t)]

    class _UNION(ctypes.Union):
        _fields_ = [("ki", _KEYBDINPUT), ("mi", _MOUSEINPUT)]

    class _INPUT(ctypes.Structure):
        _anonymous_ = ("u",)
        _fields_ = [("type", wintypes.DWORD), ("u", _UNION)]

    user32.FindWindowW.restype = wintypes.HWND
    user32.GetForegroundWindow.restype = wintypes.HWND

VK_BACK, VK_TAB, VK_RETURN, VK_END, VK_MENU = 0x08, 0x09, 0x0D, 0x23, 0x12
_KEYUP, _UNICODE, _EXTENDED = 0x0002, 0x0004, 0x0001


def _enviar(*eventos: tuple[int, int, int]) -> None:
    entradas = (_INPUT * len(eventos))()
    for i, (vk, scan, flags) in enumerate(eventos):
        entradas[i].type = 1  # INPUT_KEYBOARD
        entradas[i].ki = _KEYBDINPUT(vk, scan, flags, 0, 0)
    user32.SendInput(len(eventos), entradas, ctypes.sizeof(_INPUT))


def vigilar_esquina() -> None:
    """Interrumpe si el mouse está en una esquina de la pantalla."""
    p = wintypes.POINT()
    user32.GetCursorPos(ctypes.byref(p))
    ancho, alto = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
    if p.x in (0, ancho - 1) and p.y in (0, alto - 1):
        raise Interrumpido()


def tecla(vk: int, extendida: bool = False) -> None:
    vigilar_esquina()
    flag = _EXTENDED if extendida else 0
    _enviar((vk, 0, flag), (vk, 0, flag | _KEYUP))
    time.sleep(0.05)


def escribir(texto: str) -> None:
    """Escribe caracteres Unicode: no depende de la distribución del teclado."""
    for c in texto:
        vigilar_esquina()
        _enviar((0, ord(c), _UNICODE), (0, ord(c), _UNICODE | _KEYUP))
        time.sleep(0.02)


def buscar_ventana() -> int | None:
    return user32.FindWindowW(None, TITULO) or None


def tamano(hwnd: int) -> tuple[int, int]:
    r = wintypes.RECT()
    user32.GetWindowRect(hwnd, ctypes.byref(r))
    return r.right - r.left, r.bottom - r.top


def traer_al_frente(hwnd: int) -> None:
    """Pone la ventana al frente; si no lo logra, falla en vez de escribir en otra."""
    if user32.GetForegroundWindow() == hwnd:
        return
    for intento in range(8):
        user32.ShowWindow(hwnd, 9)  # SW_RESTORE
        if intento:  # desde el segundo intento, el truco de la tecla Alt permite cambiar el foco
            _enviar((VK_MENU, 0, 0), (VK_MENU, 0, _KEYUP))
        user32.SetForegroundWindow(hwnd)
        time.sleep(0.3)
        if user32.GetForegroundWindow() == hwnd:
            time.sleep(0.8)  # deja que la ventana tome el foco antes de escribir (si no, se pierde el primer carácter)
            return
    raise ErrorVentana("No se pudo poner Mi Cotizador al frente; otra ventana tiene el foco.")


def capturar(hwnd: int, ruta: Path) -> None:
    from PIL import ImageGrab
    r = wintypes.RECT()
    user32.GetWindowRect(hwnd, ctypes.byref(r))
    ImageGrab.grab(bbox=(r.left, r.top, r.right, r.bottom), all_screens=True).save(ruta)


# ----------------------------------------------------------------- PocketBase
def total_consultas(token: str) -> int:
    return m._pedir("/api/collections/consultas/records?perPage=1", metodo="GET", token=token)["totalItems"]


def consultas_desde(token: str, desde_utc: str) -> list[dict]:
    q = urlencode({"filter": f'fecha >= "{desde_utc}"', "sort": "-fecha", "perPage": 100})
    return m._pedir(f"/api/collections/consultas/records?{q}", metodo="GET", token=token)["items"]


def verificar(montos: list[int], consultas: list[dict]) -> tuple[int, list[str]]:
    """Compara los montos enviados con las consultas guardadas.

    Devuelve (cantidad que coincide, detalle por monto). Cada consulta debe tener
    el monto ingresado y un resultado igual a monto ÷ cotización registrada.
    """
    pendientes = list(consultas)
    coinciden, detalle = 0, []
    for monto in montos:
        c = next((x for x in pendientes if abs((x.get("monto") or 0) - monto) < 1e-6), None)
        if c is None:
            detalle.append(f"FALTA     {monto:>9,}: no hay una consulta guardada con ese monto")
            continue
        pendientes.remove(c)
        cot = c.get("cotizacion") or 0
        resultado = c.get("resultado") or 0
        if cot <= 0 or abs(resultado - monto / cot) > TOLERANCIA:
            detalle.append(f"DIFIERE   {monto:>9,}: cotización {cot}, resultado guardado {resultado:.2f}, "
                           f"esperado {(monto / cot if cot > 0 else float('nan')):.2f}")
            continue
        coinciden += 1
        detalle.append(f"COINCIDE  {monto:>9,} ÷ {cot:,.2f} = US$ {resultado:,.2f}")
    return coinciden, detalle


# ------------------------------------------------------------------- programa
def abrir_aplicacion(usar_exe: bool) -> subprocess.Popen:
    if usar_exe:
        return subprocess.Popen([str(EXE)], cwd=str(RAIZ))
    return subprocess.Popen([sys.executable, str(RAIZ / "mi_cotizador.py")], cwd=str(RAIZ))


def cerrar_aplicacion(proceso: subprocess.Popen) -> None:
    """Cierra la aplicación y sus procesos hijos (el .exe de PyInstaller lanza uno)."""
    subprocess.run(["taskkill", "/F", "/T", "/PID", str(proceso.pid)], capture_output=True)
    try:
        proceso.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proceso.kill()
    for _ in range(20):  # espera a que la ventana desaparezca
        if not buscar_ventana():
            return
        time.sleep(0.2)


def esperar_ventana(proceso: subprocess.Popen, segundos: float = 20) -> int:
    limite = time.time() + segundos
    while time.time() < limite:
        if proceso.poll() is not None:
            raise ErrorVentana("Mi Cotizador se cerró apenas abrirse.")
        hwnd = buscar_ventana()
        if hwnd:
            return hwnd
        time.sleep(0.3)
    raise ErrorVentana(f"La ventana de Mi Cotizador no apareció en {segundos:.0f} segundos.")


def cerrar_dialogo() -> None:
    tecla(VK_RETURN)  # cierra un mensaje de error si quedó abierto


def iniciar_sesion_en_ventana(hwnd: int, email: str, clave: str) -> None:
    ancho0, alto0 = tamano(hwnd)
    traer_al_frente(hwnd)
    escribir(email)
    tecla(VK_TAB)
    escribir(clave)
    tecla(VK_RETURN)
    limite = time.time() + 15
    while time.time() < limite:  # al abrirse el conversor, la ventana crece
        if tamano(hwnd) != (ancho0, alto0):
            return
        time.sleep(0.3)
    cerrar_dialogo()
    raise ErrorVentana("El conversor no se abrió tras iniciar sesión (¿credenciales rechazadas?).")


def convertir_en_ventana(hwnd: int, monto: int, token: str, previas: int) -> None:
    traer_al_frente(hwnd)
    tecla(VK_END, extendida=True)
    for _ in range(14):  # borra lo que haya quedado del monto anterior
        tecla(VK_BACK)
    escribir(str(monto))
    tecla(VK_RETURN)
    limite = time.time() + 15
    while time.time() < limite:  # espera a que la consulta esté guardada
        if total_consultas(token) > previas:
            time.sleep(1.2)  # deja que la ventana muestre el resultado y refresque el historial
            return
        time.sleep(0.4)
    cerrar_dialogo()
    raise ErrorVentana(f"La conversión de {monto:,} no se guardó: ¿el campo de cotización quedó vacío?")


def main() -> int:
    ap = argparse.ArgumentParser(description="Diez conversiones con captura de cada resultado.")
    ap.add_argument("--exe", action="store_true", help="abrir dist/Mi Cotizador.exe en lugar del código fuente")
    ap.add_argument("--cuenta", type=int, default=5, help="segundos de cuenta regresiva antes de empezar (5)")
    args = ap.parse_args()

    if sys.platform != "win32":
        print("Este programa solo funciona en Windows.")
        return 2
    faltan = [v for v in ("POCKETBASE_URL", "PB_TEST_EMAIL", "PB_TEST_PASSWORD") if not os.environ.get(v)]
    if faltan:
        print("Faltan en el .env o el entorno: " + ", ".join(faltan) + ". No se abrió nada.")
        return 2
    # Empaquetado como .exe no hay código fuente que abrir: se usa siempre Mi Cotizador.exe.
    usar_exe = args.exe or EMPAQUETADO
    if usar_exe and not EXE.exists():
        print(f"No encuentro Mi Cotizador.exe (busqué en {EXE.parent}). Dejalo junto a este programa"
              + ("." if EMPAQUETADO else " o ejecutá sin --exe."))
        return 2
    try:
        import PIL  # noqa: F401
    except ImportError:
        print("Falta Pillow: pip install -r requirements.txt")
        return 2
    if buscar_ventana():
        print("Ya hay una ventana de Mi Cotizador abierta. Cerrala y volvé a ejecutar.")
        return 2

    email, clave = os.environ["PB_TEST_EMAIL"], os.environ["PB_TEST_PASSWORD"]
    try:  # comprobaciones previas: fallar antes de tomar el teclado
        sesion = m.iniciar_sesion(email, clave)
    except m.ErrorAuth as e:
        print(f"No se pudo iniciar sesión con el usuario de prueba: {e}")
        return 2
    token = sesion["token"]
    try:
        if not m.DOLARAPI_URL:
            raise m.ErrorCotizacion("falta DOLARAPI_URL en el .env")
        m.obtener_cotizacion(m.DOLARAPI_URL)
    except m.ErrorCotizacion as e:
        print(f"No se cargaría la cotización automática: {e}")
        return 2

    print(f"Voy a TOMAR EL TECLADO Y LA VENTANA ACTIVA y hacer {len(MONTOS)} conversiones.")
    print("No toques el teclado. Para interrumpir: mové el mouse a una esquina de la pantalla.")
    try:
        for restante in range(args.cuenta, 0, -1):
            print(f"  empiezo en {restante}... (Ctrl+C para cancelar)")
            time.sleep(1)
    except KeyboardInterrupt:
        print("Cancelado. No se abrió nada.")
        return 130

    carpeta = RAIZ / "capturas" / datetime.now().strftime("%Y%m%d-%H%M%S")
    carpeta.mkdir(parents=True, exist_ok=True)
    inicio_utc = (datetime.now(timezone.utc) - timedelta(seconds=2)).strftime("%Y-%m-%d %H:%M:%S")
    proceso = None
    try:
        proceso = abrir_aplicacion(usar_exe)
        hwnd = esperar_ventana(proceso)
        time.sleep(1.0)
        iniciar_sesion_en_ventana(hwnd, email, clave)
        print("Sesión iniciada. Esperando la cotización automática...")
        time.sleep(4)
        for i, monto in enumerate(MONTOS, start=1):
            convertir_en_ventana(hwnd, monto, token, total_consultas(token))
            ruta = carpeta / f"{i:02d}_{monto}.png"
            capturar(hwnd, ruta)
            print(f"  {i:2d}/{len(MONTOS)}  {monto:>9,} pesos -> {ruta.relative_to(RAIZ)}")
    except Interrumpido:
        print("Interrumpido: el mouse llegó a una esquina de la pantalla.")
        return 130
    except ErrorVentana as e:
        print(f"Error al operar la ventana: {e}")
        return 3
    except KeyboardInterrupt:
        print("Interrumpido con Ctrl+C.")
        return 130
    finally:
        if proceso:
            cerrar_aplicacion(proceso)
        if not any(carpeta.iterdir()):
            carpeta.rmdir()  # una corrida fallida no deja carpetas vacías

    capturas = len(list(carpeta.glob("*.png")))
    print(f"\nVerificando contra PocketBase ({email})...")
    coinciden, detalle = verificar(MONTOS, consultas_desde(token, inicio_utc))
    print("\n".join("  " + d for d in detalle))
    print(f"\n{coinciden} de {len(MONTOS)} conversiones coinciden; {capturas} capturas en {carpeta.relative_to(RAIZ)}")
    return 0 if coinciden == len(MONTOS) and capturas == len(MONTOS) else 1


if __name__ == "__main__":
    sys.exit(main())
