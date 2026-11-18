# servidor-mcp-pocketbase Specification

## Purpose
Permite que Claude Code consulte y modifique la base local de PocketBase del proyecto mediante herramientas MCP acotadas, sin exponer credenciales en archivos versionados.

## Requirements

### Requirement: Registro y arranque del servidor
El proyecto SHALL incluir un servidor MCP por stdio, registrado en `.mcp.json` en la raíz, que Claude Code pueda iniciar sin pasos manuales además de aprobarlo. El servidor SHALL escribir por la salida estándar únicamente mensajes del protocolo MCP.

#### Scenario: Servidor disponible en Claude Code
- **WHEN** se abre el proyecto en Claude Code y se aprueba el servidor
- **THEN** el servidor se inicia y expone sus herramientas

#### Scenario: Sin credenciales en archivos versionados
- **WHEN** se revisa `.mcp.json` y el código del servidor
- **THEN** no contienen la dirección de PocketBase ni contraseñas

### Requirement: Configuración desde el .env
El servidor SHALL leer `POCKETBASE_URL`, `PB_SUPERUSER_EMAIL` y `PB_SUPERUSER_PASSWORD` del archivo `.env` o del entorno, y SHALL autenticarse como superusuario de PocketBase al primer uso, renovando la sesión si el servidor la rechaza por vencida.

#### Scenario: Configuración completa
- **WHEN** las tres variables están definidas y PocketBase está en ejecución
- **THEN** las herramientas funcionan contra esa base

#### Scenario: Variable faltante
- **WHEN** falta alguna de las variables
- **THEN** las herramientas devuelven un error que indica cuál falta y el servidor no se cae

#### Scenario: PocketBase apagado o credenciales incorrectas
- **WHEN** PocketBase no responde o rechaza las credenciales
- **THEN** la herramienta devuelve un error claro, sin mostrar la contraseña

### Requirement: Consulta del estado y del esquema
El servidor SHALL ofrecer herramientas para comprobar el estado de PocketBase, listar las colecciones no de sistema y ver el esquema (campos y tipos) y las reglas de acceso de una colección.

#### Scenario: Listar colecciones
- **WHEN** se invoca la herramienta de colecciones
- **THEN** devuelve los nombres y tipos de las colecciones no de sistema

#### Scenario: Ver una colección
- **WHEN** se invoca la herramienta con el nombre de una colección existente
- **THEN** devuelve sus campos y sus reglas de acceso

### Requirement: Lectura de registros
El servidor SHALL ofrecer herramientas para listar registros de una colección, con filtro, orden y paginación, y para ver un registro por id. La cantidad por página SHALL tener un máximo de 100, y las respuestas SHALL ser JSON legible.

#### Scenario: Listado filtrado
- **WHEN** se lista una colección con un filtro y un orden
- **THEN** devuelve la página de registros que cumple el filtro, en ese orden, con el total

#### Scenario: Página demasiado grande
- **WHEN** se pide una cantidad por página mayor que 100
- **THEN** se limita a 100 e informa el límite aplicado

#### Scenario: Registro inexistente
- **WHEN** se pide un id que no existe
- **THEN** devuelve un error claro de registro no encontrado

### Requirement: Escritura de registros
El servidor SHALL ofrecer herramientas para crear, modificar y borrar registros de una colección, aplicando las validaciones de PocketBase y devolviendo su mensaje de error si las rechaza.

#### Scenario: Crear un registro
- **WHEN** se crea un registro con datos válidos
- **THEN** se guarda y se devuelve el registro creado

#### Scenario: Datos inválidos
- **WHEN** los datos incumplen una validación de la colección
- **THEN** no se guarda nada y se devuelve el detalle del error por campo

#### Scenario: Modificar y borrar
- **WHEN** se modifica o se borra un registro existente
- **THEN** el cambio se aplica y se informa el resultado

### Requirement: Creación y modificación de colecciones
El servidor SHALL ofrecer herramientas para crear una colección y para modificar los campos y las reglas de una existente. El servidor SHALL NOT ofrecer ninguna herramienta que borre colecciones.

#### Scenario: Crear una colección
- **WHEN** se crea una colección con nombre y campos válidos
- **THEN** la colección queda disponible en PocketBase

#### Scenario: Borrado de colecciones
- **WHEN** se revisan las herramientas del servidor
- **THEN** ninguna permite borrar una colección

### Requirement: Protección de colecciones del sistema
El servidor SHALL rechazar toda operación, de lectura o de escritura, sobre colecciones del sistema, es decir, aquellas cuyo nombre empieza con `_` (por ejemplo `_superusers`), indicando el motivo.

#### Scenario: Acceso a una colección de sistema
- **WHEN** se invoca cualquier herramienta sobre `_superusers`
- **THEN** devuelve un error que explica que las colecciones del sistema están protegidas y no accede a ellas

### Requirement: Documentación de uso y riesgos
El proyecto SHALL documentar en el `README` cómo activar el servidor, las variables necesarias, las herramientas disponibles y los riesgos: el acceso es de superusuario, ignora las reglas de la aplicación y permite escribir y borrar datos.

#### Scenario: Instrucciones de activación
- **WHEN** una persona lee el README
- **THEN** encuentra los pasos para instalar la dependencia, configurar el `.env` y aprobar el servidor en Claude Code
