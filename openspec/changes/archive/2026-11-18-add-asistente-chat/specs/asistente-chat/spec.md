## Purpose

Permite pedirle a Mi Cotizador, en lenguaje natural, que convierta montos, consulte o actualice la cotización del dólar y muestre el historial propio, resolviendo cada pedido con las funciones que la aplicación ya tiene.

## ADDED Requirements

### Requirement: Acceso al chat
La aplicación SHALL ofrecer en el conversor un botón **Asistente** que abra la pantalla de chat, y la pantalla de chat SHALL tener un botón para volver al conversor. El chat SHALL ser accesible únicamente con sesión iniciada.

#### Scenario: Abrir y volver
- **WHEN** una persona con sesión iniciada pulsa Asistente y luego Volver
- **THEN** se muestra el chat y después el conversor, con la cotización y el monto que tenía antes

#### Scenario: Sin sesión
- **WHEN** no hay sesión iniciada
- **THEN** no hay forma de abrir el chat desde la interfaz

### Requirement: Configuración desde el .env
La clave de la API, el modelo y la dirección de la API SHALL leerse de `OPENAI_API_KEY`, `OPENAI_MODEL` y `OPENAI_URL` (archivo `.env` o entorno), sin valores por defecto ni en el código ni en `.env.example`. Si falta alguna, el chat SHALL indicar cuál y no enviar ninguna solicitud. La clave SHALL NOT mostrarse en pantalla, en mensajes de error ni en archivos.

#### Scenario: Variable faltante
- **WHEN** falta `OPENAI_API_KEY`, `OPENAI_MODEL` o `OPENAI_URL`
- **THEN** el chat avisa cuál falta, no permite enviar mensajes y el resto de la aplicación funciona normalmente

#### Scenario: Clave rechazada
- **WHEN** la API responde que la clave es inválida
- **THEN** el chat muestra un mensaje claro sin incluir la clave

### Requirement: Pedidos en lenguaje natural resueltos con funciones de la app
Al recibir un mensaje, el sistema SHALL enviarlo a la API de OpenAI junto con la conversación y la descripción de las funciones disponibles, ejecutar localmente las funciones que el modelo solicite, devolverle los resultados y mostrar su respuesta final. Las funciones disponibles SHALL ser únicamente: convertir pesos a dólares, consultar la cotización del dólar oficial, actualizar la cotización cargada en el conversor y ver el historial propio. El sistema SHALL NOT exponer funciones de administración de cuentas.

#### Scenario: Conversión pedida por chat
- **WHEN** la persona escribe "convertime 150000 pesos"
- **THEN** se convierte con la cotización del dólar oficial, se guarda en su historial igual que con el botón Convertir y la respuesta informa el resultado

#### Scenario: Cotización indicada en el pedido
- **WHEN** la persona pide convertir 150000 pesos a una cotización de 1600
- **THEN** la conversión usa 1600 y no la del dólar oficial

#### Scenario: Consultar la cotización
- **WHEN** la persona pregunta a cuánto está el dólar
- **THEN** la respuesta informa la cotización de venta del dólar oficial y su fecha de actualización

#### Scenario: Actualizar la cotización del conversor
- **WHEN** la persona pide actualizar la cotización
- **THEN** el campo de cotización del conversor queda con el valor vigente, igual que con el botón Actualizar cotización

#### Scenario: Ver el historial
- **WHEN** la persona pide ver sus últimas conversiones
- **THEN** la respuesta muestra únicamente las de su propia cuenta, hasta un máximo de 50

#### Scenario: Pedido de administración
- **WHEN** la persona pide desactivar una cuenta o resetear una contraseña
- **THEN** el asistente explica que no puede hacerlo y no ejecuta ninguna función de administración

### Requirement: Validación de los argumentos de las funciones
El sistema SHALL validar localmente los argumentos que proponga el modelo con las mismas reglas de la aplicación (números mayores que cero, cantidad máxima de historial) y SHALL devolver al modelo un error comprensible si no son válidos, sin ejecutar la función.

#### Scenario: Monto inválido
- **WHEN** el modelo solicita convertir un monto negativo o no numérico
- **THEN** no se convierte ni se guarda nada y el chat informa que el monto no es válido

#### Scenario: Cotización no positiva
- **WHEN** el modelo solicita una conversión con cotización cero
- **THEN** no se convierte ni se guarda nada

### Requirement: Límite de iteraciones y respuesta sin funciones
El sistema SHALL limitar a un máximo de cinco rondas de llamadas a funciones por mensaje y SHALL mostrar como respuesta el texto del modelo cuando no solicite funciones.

#### Scenario: Pregunta general
- **WHEN** el modelo responde con texto sin solicitar funciones
- **THEN** el chat muestra ese texto

#### Scenario: Bucle de funciones
- **WHEN** el modelo sigue solicitando funciones después de la quinta ronda
- **THEN** el sistema corta e informa que no pudo completar el pedido

### Requirement: Interfaz que no se bloquea
Las consultas a la API SHALL ejecutarse sin congelar la ventana, mostrando un indicador de que el asistente está respondiendo y bloqueando el envío de otro mensaje hasta que termine. Si la respuesta llega luego de cerrar la sesión, SHALL descartarse.

#### Scenario: Respuesta lenta
- **WHEN** la API tarda en responder
- **THEN** la ventana sigue respondiendo y se muestra el indicador

#### Scenario: Cerrar sesión durante la espera
- **WHEN** se cierra la sesión y después llega la respuesta
- **THEN** no se muestra ni se ejecuta nada

### Requirement: Manejo de fallas de la API
Si la API no responde, tarda más del tiempo de espera, devuelve un error (clave, límite de uso, servicio) o una respuesta ilegible, el chat SHALL mostrar un mensaje claro, conservar la conversación y permitir reintentar, sin cerrar la aplicación.

#### Scenario: Sin conexión
- **WHEN** no se puede conectar con la API
- **THEN** el chat muestra un aviso de conexión y se puede escribir de nuevo

#### Scenario: Límite de uso
- **WHEN** la API responde que se superó el límite de uso
- **THEN** el chat lo informa con un mensaje claro

### Requirement: Conversación efímera y aviso de privacidad
La conversación SHALL conservarse solo en memoria, acotada a los últimos mensajes, y SHALL borrarse al cerrar sesión. La pantalla de chat SHALL mostrar un aviso de que los mensajes y los resultados de las funciones se envían a OpenAI, y SHALL NOT enviar la contraseña, el token de sesión ni el email de la persona.

#### Scenario: Cerrar sesión
- **WHEN** la persona cierra la sesión y otra inicia sesión
- **THEN** el chat aparece vacío

#### Scenario: Aviso visible
- **WHEN** se abre la pantalla de chat
- **THEN** se ve el aviso de envío de datos a OpenAI
