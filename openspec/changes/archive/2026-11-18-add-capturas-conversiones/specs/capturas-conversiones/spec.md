## Purpose

Verifica de punta a punta la interfaz de Mi Cotizador: abre la aplicación real, inicia sesión con un usuario de prueba, hace diez conversiones, guarda una captura de cada resultado y comprueba que quedaron registradas correctamente en el historial.

## ADDED Requirements

### Requirement: Apertura de la aplicación
El programa SHALL abrir Mi Cotizador y esperar a que su ventana de inicio de sesión esté disponible antes de operarla. Por defecto SHALL abrir la aplicación desde el código fuente; con la opción `--exe` SHALL abrir `dist/Mi Cotizador.exe`. Al terminar, con éxito o con error, SHALL cerrar la aplicación que abrió.

#### Scenario: Apertura desde el código fuente
- **WHEN** se ejecuta el programa sin opciones
- **THEN** se abre la ventana de Mi Cotizador y el programa la usa

#### Scenario: Apertura del ejecutable
- **WHEN** se ejecuta con `--exe` y existe `dist/Mi Cotizador.exe`
- **THEN** se abre el ejecutable en lugar del código fuente

#### Scenario: La ventana no aparece
- **WHEN** la ventana no se abre dentro de un tiempo razonable
- **THEN** el programa termina con un error claro y sin dejar procesos abiertos

### Requirement: Inicio de sesión con el usuario de prueba
El programa SHALL iniciar sesión en la ventana con el email y la contraseña de `PB_TEST_EMAIL` y `PB_TEST_PASSWORD`, leídos del `.env` o del entorno, y SHALL comprobar que se abre el conversor. El programa SHALL NOT mostrar ni registrar la contraseña.

#### Scenario: Sesión iniciada
- **WHEN** las credenciales son válidas
- **THEN** el conversor queda abierto mostrando el email del usuario de prueba

#### Scenario: Variables faltantes
- **WHEN** falta `PB_TEST_EMAIL` o `PB_TEST_PASSWORD`
- **THEN** el programa termina antes de abrir la aplicación indicando qué variable falta

#### Scenario: Credenciales rechazadas
- **WHEN** el inicio de sesión falla
- **THEN** el programa termina con un error claro, sin mostrar la contraseña

### Requirement: Diez conversiones con montos distintos
El programa SHALL realizar diez conversiones escribiendo en la ventana diez montos distintos, definidos de forma fija y reproducible, usando la cotización que el conversor haya cargado automáticamente.

#### Scenario: Diez conversiones
- **WHEN** la sesión está iniciada
- **THEN** el programa convierte diez montos distintos, uno por vez, y espera a que cada resultado aparezca antes de pasar al siguiente

#### Scenario: Sin cotización cargada
- **WHEN** el campo de cotización sigue vacío tras esperar
- **THEN** el programa termina con un error claro indicando que no se cargó la cotización

### Requirement: Captura de cada resultado
El programa SHALL guardar, después de cada conversión, una captura de la ventana de Mi Cotizador que muestre el resultado, como imagen PNG en la carpeta `capturas/`, con un nombre que incluya el número de orden y el monto. Las capturas de ejecuciones anteriores SHALL conservarse, y la carpeta SHALL quedar fuera del control de versiones.

#### Scenario: Una captura por conversión
- **WHEN** termina una conversión
- **THEN** se guarda un PNG de la ventana con el resultado visible, con nombre único por ejecución, orden y monto

#### Scenario: Diez capturas
- **WHEN** el programa termina con éxito
- **THEN** hay diez capturas nuevas en `capturas/`

### Requirement: Verificación contra el historial guardado
Al terminar las conversiones, el programa SHALL consultar a PocketBase como el usuario de prueba y comprobar que las diez conversiones quedaron guardadas con el monto ingresado y que cada resultado coincide con monto ÷ cotización registrada, con un margen de redondeo. SHALL informar cuántas coinciden y SHALL terminar con código de salida distinto de cero si alguna no coincide o falta.

#### Scenario: Todo coincide
- **WHEN** las diez consultas guardadas coinciden con lo esperado
- **THEN** el programa informa 10 de 10 y termina con código 0

#### Scenario: Una conversión no se guardó o no coincide
- **WHEN** falta una consulta o su resultado difiere de monto ÷ cotización
- **THEN** el programa informa cuáles fallaron y termina con código distinto de cero

### Requirement: Usuario de prueba persistente
El usuario de prueba SHALL conservarse entre ejecuciones: el programa SHALL NOT borrar el usuario ni sus consultas. Sus credenciales SHALL residir en el `.env`, y `.env.example` SHALL incluir las claves sin valores.

#### Scenario: Ejecuciones repetidas
- **WHEN** el programa se ejecuta varias veces
- **THEN** usa siempre el mismo usuario y el historial acumula las conversiones de todas las ejecuciones

### Requirement: Aviso sobre el uso del teclado
El programa SHALL avisar antes de empezar que va a tomar el teclado y la ventana activa, SHALL ofrecer una cuenta regresiva breve para cancelar, y SHALL permitir interrumpirlo moviendo el mouse a una esquina de la pantalla.

#### Scenario: Cancelar a tiempo
- **WHEN** la persona cancela durante la cuenta regresiva
- **THEN** el programa termina sin abrir la aplicación ni escribir nada

#### Scenario: Interrupción durante la ejecución
- **WHEN** la persona mueve el mouse a una esquina de la pantalla mientras corre
- **THEN** el programa se detiene y cierra la aplicación que abrió
