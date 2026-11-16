# conversor Specification

## Purpose
Permite convertir un monto en pesos a dólares usando una cotización ingresada por la persona usuaria, y conserva un registro con fecha y hora de cada conversión realizada.

## Requirements

### Requirement: Conversión de pesos a dólares
El sistema SHALL ofrecer un campo para el monto en pesos, un campo para la cotización del dólar y un botón **Convertir** que muestre el resultado en dólares, calculado como monto dividido por cotización, con dos decimales. El sistema SHALL aceptar números con formato argentino (`1.234,56`) o con punto decimal (`1234.56`).

#### Scenario: Conversión correcta
- **WHEN** la persona ingresa 1.000.000 como monto y 1250 como cotización y pulsa Convertir
- **THEN** el sistema muestra `US$ 800.00`

#### Scenario: Número con formato argentino
- **WHEN** la persona ingresa `1.500.000,50` como monto
- **THEN** el sistema lo interpreta como 1500000.50

### Requirement: Validación de datos
El sistema SHALL rechazar valores que no sean números y cotizaciones menores o iguales a cero, mostrando un mensaje de error, sin mostrar resultado ni registrar la conversión.

#### Scenario: Valor no numérico
- **WHEN** la persona ingresa texto que no es un número en cualquiera de los campos y pulsa Convertir
- **THEN** el sistema muestra un mensaje de error y no registra nada en el historial

#### Scenario: Cotización no positiva
- **WHEN** la persona ingresa una cotización igual o menor que cero
- **THEN** el sistema muestra un mensaje de error y no registra nada en el historial

### Requirement: Historial de conversiones
El sistema SHALL agregar una línea a `historial.txt`, ubicado junto a la aplicación, por cada conversión exitosa, con fecha y hora, monto en pesos, cotización y resultado en dólares.

#### Scenario: Conversión registrada
- **WHEN** una conversión se realiza con éxito
- **THEN** se agrega una línea con el formato `AAAA-MM-DD HH:MM:SS | $<pesos> ARS | cotización <valor> | US$<dólares>` al final de `historial.txt`

#### Scenario: Historial no escribible
- **WHEN** no se puede escribir `historial.txt`
- **THEN** el sistema muestra el resultado igualmente y avisa que no se pudo guardar el historial
