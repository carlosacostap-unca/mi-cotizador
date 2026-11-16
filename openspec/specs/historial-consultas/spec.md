# historial-consultas Specification

## Purpose
Guarda cada conversión en PocketBase asociada a quien la hizo y garantiza, desde el servidor, que cada usuario vea únicamente su propio historial.

## Requirements

### Requirement: Registro de consultas en PocketBase
El sistema SHALL guardar cada conversión exitosa como una consulta con el usuario que la realizó, el monto en pesos, la cotización, el resultado en dólares y la fecha y hora de creación, asignada por el servidor.

#### Scenario: Conversión guardada
- **WHEN** un usuario con sesión iniciada realiza una conversión exitosa
- **THEN** se crea una consulta con su usuario, el monto, la cotización, el resultado y la fecha y hora

#### Scenario: Conversión inválida
- **WHEN** la conversión se rechaza por datos inválidos
- **THEN** no se crea ninguna consulta

### Requirement: Aislamiento del historial por usuario
El servidor SHALL permitir leer una consulta únicamente a su propietario, incluidos los admins respecto de las ajenas, y SHALL permitir crear consultas solo a nombre del usuario autenticado. Las consultas SHALL ser inmutables: ningún usuario puede modificarlas ni borrarlas.

#### Scenario: Listado propio
- **WHEN** un usuario solicita el listado de consultas
- **THEN** recibe únicamente las suyas

#### Scenario: Acceso a consultas ajenas
- **WHEN** un usuario, incluso admin, intenta leer una consulta de otra persona
- **THEN** el servidor no la devuelve

#### Scenario: Creación a nombre de otro
- **WHEN** un usuario intenta crear una consulta asignada a otro usuario
- **THEN** el servidor rechaza la operación

#### Scenario: Sin sesión
- **WHEN** una solicitud sin autenticar intenta leer o crear consultas
- **THEN** el servidor rechaza la operación

#### Scenario: Modificación o borrado
- **WHEN** un usuario intenta modificar o borrar una consulta
- **THEN** el servidor rechaza la operación

### Requirement: Historial visible en el conversor
El conversor SHALL mostrar al usuario su historial de consultas con fecha y hora, monto, cotización y resultado, ordenado de la más reciente a la más antigua, y SHALL actualizarlo al abrirse y después de cada conversión guardada.

#### Scenario: Historial al abrir
- **WHEN** un usuario abre el conversor
- **THEN** ve sus consultas anteriores, de la más reciente a la más antigua

#### Scenario: Nueva conversión
- **WHEN** el usuario realiza una conversión exitosa
- **THEN** la nueva consulta aparece al principio de la lista

#### Scenario: Usuario sin consultas
- **WHEN** un usuario nuevo abre el conversor
- **THEN** la lista aparece vacía sin errores

#### Scenario: Error al cargar
- **WHEN** no se puede obtener el historial desde el servidor
- **THEN** se muestra un aviso y el conversor sigue siendo utilizable
