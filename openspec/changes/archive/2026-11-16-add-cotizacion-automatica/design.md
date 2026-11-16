## Context

El conversor (capacidad `conversor`) pide la cotización a mano. La aplicación ya lee su configuración de `.env` mediante `entorno.py` y no lleva direcciones escritas en el código (ver cambio de configuración previo). El servicio dolarapi.com responde un JSON con `compra`, `venta` y `fechaActualizacion` para el dólar oficial. Ver proposal.md para la motivación.

## Goals / Non-Goals

**Goals:**
- Precargar la cotización de venta del dólar oficial sin trabar la interfaz.
- Mantener el ingreso manual siempre disponible.

**Non-Goals:**
- Otros tipos de dólar (blue, MEP, tarjeta) o selección de casa.
- Actualización periódica automática, caché o historial de cotizaciones.
- Guardar la cotización en PocketBase más allá de lo que ya guarda cada consulta.

## Decisions

- **Valor de venta** (decisión del usuario): es el precio de compra de dólares con pesos, el que corresponde a la conversión pesos → dólares.
- **Consulta en un hilo aparte** con `threading` y resultado recogido con `after()`: evita congelar la ventana si el servicio tarda (tiempo de espera de 5 s). Alternativa descartada: llamada sincrónica, que bloquea la interfaz hasta 5 s sin conexión.
- **Al abrir solo se completa si el campo está vacío**; el botón siempre reemplaza. Así volver desde el panel de administración no pisa un valor que la persona escribió.
- **Formato del valor en el campo**: dos decimales con coma (`1575,00`), que el parseo actual interpreta correctamente.
- **Dirección en `DOLARAPI_URL`** (decisión del usuario), leída con el mismo mecanismo que `POCKETBASE_URL`, sin valor por defecto ni en el código ni en `.env.example`.
- **Validación de la respuesta**: se exige un número `venta` mayor que cero; cualquier otra forma de respuesta se trata como error de consulta. Se descarta una respuesta que llegue después de que la persona cerró sesión.
- **User-Agent genérico (`MiCotizador/1.0`)**: descubierto al probar contra el servicio real, que rechaza con 403 el User-Agent por defecto de Python. No incluye datos personales.
- **Sin dependencias nuevas**: `urllib` y `json` de la biblioteca estándar.

## Risks / Trade-offs

- [El servicio externo puede caerse o cambiar su formato] → Aviso claro y entrada manual siempre disponible.
- [La cotización mostrada puede estar desactualizada] → Se muestra la fecha informada por el servicio.
- [La consulta revela a un tercero la dirección IP de quien usa la app] → Aceptado; no se envían datos de la persona ni del historial.
- [Una respuesta tardía puede llegar con otra sesión abierta] → Se descarta si la pantalla ya no es la misma sesión.
