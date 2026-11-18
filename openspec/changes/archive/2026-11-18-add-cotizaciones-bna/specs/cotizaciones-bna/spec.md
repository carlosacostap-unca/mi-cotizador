## Purpose

Registra de forma acumulativa la compra y la venta del dólar (tabla "Cotización Divisas") que publica el Banco Nación en su página de cotizaciones, con la fecha y hora de cada consulta.

## ADDED Requirements

### Requirement: Lectura de la cotización del dólar en divisas
El programa SHALL consultar la página de cotizaciones del Banco Nación y SHALL obtener de la tabla "Cotización Divisas" la compra y la venta de la fila "Dolar U.S.A", junto con la fecha que informa el banco en el encabezado de esa tabla. Los valores SHALL interpretarse como números positivos, aceptando punto o coma como separador decimal.

#### Scenario: Lectura correcta
- **WHEN** la página responde con la tabla de divisas y la fila "Dolar U.S.A" tiene compra 1550.5000 y venta 1559.5000 con fecha 18/11/2026
- **THEN** el programa obtiene compra 1550.5, venta 1559.5 y fecha del banco 2026-11-18

#### Scenario: No se usa la tabla de billetes
- **WHEN** la página muestra también la tabla "Cotización Billetes" con otros valores del dólar
- **THEN** el programa usa únicamente los de "Cotización Divisas"

### Requirement: Registro con fecha y hora en un CSV acumulativo
El programa SHALL agregar al final de `cotizaciones_bna.csv` una fila por ejecución exitosa, con las columnas `fecha_hora_consulta` (fecha y hora local de la consulta), `fecha_banco`, `compra` y `venta`, creando el archivo con su encabezado si no existe y conservando las filas anteriores. El archivo SHALL poder abrirse en Excel en español: codificación UTF-8 con marca de orden de bytes, separador `;` y coma decimal.

#### Scenario: Primera ejecución
- **WHEN** el archivo no existe y la lectura es correcta
- **THEN** se crea con el encabezado y una fila con los datos leídos

#### Scenario: Ejecuciones siguientes
- **WHEN** el archivo ya tiene filas
- **THEN** se agrega una fila nueva al final sin modificar las anteriores ni repetir el encabezado

#### Scenario: Valores sin cambios
- **WHEN** el banco no cambió su cotización desde la ejecución anterior
- **THEN** igualmente se agrega una fila, con la nueva fecha y hora de consulta

### Requirement: Fallas sin escritura parcial
Si la página no responde, devuelve un error, o no contiene la tabla, la fila o valores numéricos positivos para compra y venta, el programa SHALL informar el motivo, SHALL terminar con código de salida distinto de cero y SHALL NOT agregar ninguna fila ni crear el archivo.

#### Scenario: Sin conexión
- **WHEN** no se puede conectar con la página en el tiempo de espera
- **THEN** informa que no pudo conectarse y no modifica el archivo

#### Scenario: Cambió la estructura de la página
- **WHEN** la página responde pero no se encuentra la tabla de divisas o la fila del dólar
- **THEN** informa que no pudo leer la cotización por un posible cambio en la página y no modifica el archivo

#### Scenario: Valores inválidos
- **WHEN** la compra o la venta no son números mayores que cero
- **THEN** informa el problema y no modifica el archivo

### Requirement: Dirección configurable
La dirección de la página SHALL leerse de la variable `BNA_URL` (archivo `.env` o entorno) y no estar escrita en el código ni en `.env.example`. Si falta, el programa SHALL indicarlo y terminar sin consultar.

#### Scenario: Variable ausente
- **WHEN** `BNA_URL` no está definida
- **THEN** el programa avisa que hay que configurarla y no hace ninguna consulta

### Requirement: Consulta respetuosa
El programa SHALL hacer una única consulta HTTP por ejecución, con un tiempo de espera máximo y un identificador de cliente genérico que no incluya datos personales, y SHALL informar por pantalla la cotización leída y la ubicación del archivo.

#### Scenario: Una consulta por ejecución
- **WHEN** se ejecuta el programa
- **THEN** realiza exactamente una solicitud a la página, sin reintentos automáticos

#### Scenario: Resumen en pantalla
- **WHEN** la ejecución es exitosa
- **THEN** muestra la compra, la venta, la fecha del banco y la ruta del archivo
