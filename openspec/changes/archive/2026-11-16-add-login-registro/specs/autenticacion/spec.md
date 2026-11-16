## Purpose

Controla quién puede usar Mi Cotizador: permite iniciar sesión y registrarse con los usuarios de PocketBase, y reserva el conversor a quien haya iniciado sesión.

## ADDED Requirements

### Requirement: Acceso al conversor tras iniciar sesión
El sistema SHALL abrir en la pantalla de inicio de sesión y SHALL mostrar el conversor únicamente después de un inicio de sesión exitoso.

#### Scenario: Pantalla inicial
- **WHEN** se abre la aplicación
- **THEN** se muestra la pantalla de inicio de sesión y no el conversor

#### Scenario: Inicio de sesión exitoso
- **WHEN** la persona ingresa un email y una contraseña válidos y confirma
- **THEN** se abre el conversor mostrando el email de la sesión

#### Scenario: Acceso sin sesión
- **WHEN** no hay sesión iniciada
- **THEN** no hay forma de abrir el conversor desde la interfaz

### Requirement: Registro de cuentas
El sistema SHALL permitir crear una cuenta con email, contraseña de al menos 8 caracteres y confirmación de contraseña, e iniciar sesión automáticamente al registrarse.

#### Scenario: Registro exitoso
- **WHEN** la persona completa email, contraseña y confirmación válidos
- **THEN** se crea la cuenta, se inicia sesión y se abre el conversor

#### Scenario: Contraseñas distintas
- **WHEN** la contraseña y su confirmación no coinciden
- **THEN** se muestra un error y no se crea la cuenta

#### Scenario: Email repetido o contraseña corta
- **WHEN** el email ya existe o la contraseña tiene menos de 8 caracteres
- **THEN** se muestra el motivo informado por el servidor y no se crea la cuenta

### Requirement: Cierre de sesión
El sistema SHALL ofrecer un botón **Cerrar sesión** que descarte la sesión, vacíe los campos del conversor y vuelva a la pantalla de inicio de sesión.

#### Scenario: Cerrar sesión
- **WHEN** la persona pulsa Cerrar sesión
- **THEN** se muestra la pantalla de inicio de sesión y el conversor deja de ser accesible

### Requirement: Errores de autenticación comprensibles
El sistema SHALL informar con un mensaje claro cuando falten datos, las credenciales sean incorrectas o el servidor PocketBase no responda, sin cerrar la aplicación.

#### Scenario: Credenciales incorrectas
- **WHEN** el email o la contraseña no corresponden a una cuenta
- **THEN** se muestra un mensaje de error y se permanece en la pantalla de inicio de sesión

#### Scenario: Servidor no disponible
- **WHEN** no se puede conectar con PocketBase
- **THEN** se muestra un mensaje indicando la dirección del servidor que no responde
