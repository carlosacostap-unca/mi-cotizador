## Context

La página pública del BNA entrega HTML estático (no hay API): una caja con pestañas, de las cuales `div#divisas` contiene una `table.cotizacion` cuyo encabezado `th.fechaCot` trae la fecha (por ejemplo `18/11/2026`) y cuyas filas tienen `td.tit` con el nombre de la divisa seguido de compra y venta. Al inspeccionarla, la fila "Dolar U.S.A" de divisas tenía valores con punto decimal y cuatro decimales (`1550.5000`), mientras la tabla de billetes usa coma (`1530,00`). La tabla de divisas no muestra hora de actualización, solo la fecha. El `robots.txt` del sitio permite el acceso. Ver proposal.md para la motivación.

## Goals / Non-Goals

**Goals:**
- Un programa chico y sin dependencias que deje un historial acumulativo y fácil de abrir.
- Fallar de forma clara, sin escribir datos dudosos.

**Non-Goals:**
- Ejecución periódica propia, o servicio en segundo plano.
- Leer otras divisas, la tabla de billetes o el histórico del banco.
- Integrar las cotizaciones con la aplicación de escritorio o con PocketBase.

## Decisions

- **Biblioteca estándar**: `urllib` para la consulta y `html.parser` para leer la tabla, igual que el resto del proyecto, sin instalar nada. Alternativa descartada: `requests` y `BeautifulSoup`, que agregarían dependencias para una sola tabla.
- **Tabla de divisas** (decisión del usuario): se ubica por el contenedor con `id="divisas"` y se lee la fila cuya primera celda es `Dolar U.S.A`; así no se confunde con la de billetes, que también tiene esa fila.
- **Lectura estricta**: se exige la tabla, la fecha del encabezado, la fila y dos números positivos; ante cualquier faltante se aborta sin escribir. Alternativa descartada: adivinar valores o saltear campos, que dejaría datos engañosos en el historial.
- **Números**: si el texto tiene coma, se toma como decimal (y los puntos como miles); si no, el punto es decimal. Cubre `1550.5000` y `1530,00`.
- **Formato del archivo** (decisión del usuario: CSV acumulativo): columnas `fecha_hora_consulta;fecha_banco;compra;venta`, separador `;` y coma decimal, con codificación UTF-8 con BOM, para que Excel en español lo abra sin asistentes. La fecha de consulta se escribe `AAAA-MM-DD HH:MM:SS` en hora local y la del banco `AAAA-MM-DD`. Alternativa descartada: coma y punto decimal, más estándar pero que Excel en español no interpreta bien.
- **Siempre una fila por ejecución**, aunque el banco no haya cambiado el valor: el archivo registra cuándo se consultó.
- **Archivo en la carpeta del programa** (`cotizaciones_bna.csv`), con la opción `--archivo` para cambiarlo.
- **Dirección en `BNA_URL`**, leída con `entorno.py`, sin valor por defecto en el código, coherente con el resto del proyecto.
- **Una consulta, 20 s de espera, sin reintentos**, con User-Agent genérico (`MiCotizador/1.0`): evita cargar el sitio y no revela datos personales.
- **Programación**: el programa no se agenda solo; el README explica cómo programarlo con el Programador de tareas de Windows.

## Risks / Trade-offs

- [El banco puede rediseñar la página y romper la lectura] → La lectura estricta falla con un mensaje claro y sin escribir; el ajuste sería local al analizador.
- [La fecha del banco no trae hora] → Se guarda la hora de la consulta, que es la única hora confiable; la fecha del banco permite detectar valores viejos (por ejemplo, fines de semana).
- [Uso del sitio de un tercero] → El `robots.txt` lo permite y se hace una consulta por ejecución; quien programe ejecuciones frecuentes es responsable de la carga y de los términos del sitio.
- [Un archivo abierto en Excel puede bloquear la escritura] → Se informa el error de escritura de forma clara y no se pierde lo ya guardado.
- [El CSV crece sin límite] → Una fila por ejecución es un volumen bajo; sin rotación por ahora.
