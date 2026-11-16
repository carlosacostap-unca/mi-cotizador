"""Mi Cotizador: convierte pesos a dólares y guarda el historial."""
import sys
import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import messagebox, ttk


def carpeta_base() -> Path:
    """Carpeta del .exe (si está empaquetado) o del script."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent


ARCHIVO_HISTORIAL = carpeta_base() / "historial.txt"


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


class App(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Mi Cotizador")
        self.resizable(False, False)

        marco = ttk.Frame(self, padding=20)
        marco.grid()

        ttk.Label(marco, text="Monto en pesos:").grid(row=0, column=0, sticky="w", pady=5)
        self.monto = ttk.Entry(marco, width=22)
        self.monto.grid(row=0, column=1, pady=5)

        ttk.Label(marco, text="Cotización del dólar:").grid(row=1, column=0, sticky="w", pady=5)
        self.cotizacion = ttk.Entry(marco, width=22)
        self.cotizacion.grid(row=1, column=1, pady=5)

        ttk.Button(marco, text="Convertir", command=self.on_convertir).grid(
            row=2, column=0, columnspan=2, pady=12
        )

        self.resultado = ttk.Label(marco, text="", font=("Segoe UI", 14, "bold"))
        self.resultado.grid(row=3, column=0, columnspan=2)

        self.monto.focus()
        self.bind("<Return>", lambda _e: self.on_convertir())

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


if __name__ == "__main__":
    App().mainloop()
