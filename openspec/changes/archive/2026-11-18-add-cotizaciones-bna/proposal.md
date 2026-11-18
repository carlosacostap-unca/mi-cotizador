## Why

Interesa conservar un registro propio, con fecha y hora, de la cotización de divisas del Banco Nación (BNA), que la página del banco solo muestra del día. Un programa que la lea y la guarde permite acumular ese historial ejecutándolo cuando se quiera.

## What Changes

- Nuevo programa `cotizaciones_bna.py` que entra a la página de cotizaciones del BNA, lee la **compra y la venta del dólar de la tabla "Cotización Divisas"** y agrega una fila a un archivo **CSV acumulativo** (`cotizaciones_bna.csv`) con la fecha y hora de la consulta, la fecha que informa el banco, la compra y la venta.
- La dirección de la página se lee de `BNA_URL` en el `.env` (sin valor en el código ni en `.env.example`).
- Cada ejecución hace **una sola consulta** a la página y guarda una fila; no hay ejecución periódica propia (se puede programar desde el Programador de tareas de Windows).
- Si la página no responde o cambió de forma de manera que no se puede leer con certeza, el programa informa el error y **no escribe nada** en el archivo.
- El CSV queda fuera de Git y `README.md` documenta el uso.
- Sin dependencias nuevas: solo la biblioteca estándar de Python.

## Capabilities

### New Capabilities
- `cotizaciones-bna`: lectura de la compra y la venta del dólar (divisas) de la página del Banco Nación y registro acumulativo con fecha y hora en un archivo CSV.

### Modified Capabilities

## Impact

- Código nuevo: `cotizaciones_bna.py`; reutiliza `entorno.py`.
- Configuración: `BNA_URL` en `.env` y `.env.example`; `cotizaciones_bna.csv` en `.gitignore`.
- Sistema externo: sitio público del BNA. Su `robots.txt` permite el acceso; el programa hace una consulta por ejecución con un identificador genérico. La estructura de la página no es una API estable: si el banco la rediseña, el programa dejará de poder leerla hasta ajustarlo.
- Sin cambios en la aplicación de escritorio ni en PocketBase.
