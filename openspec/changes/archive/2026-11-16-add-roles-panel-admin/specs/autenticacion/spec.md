## MODIFIED Requirements

### Requirement: Acceso al conversor tras iniciar sesión
El sistema SHALL abrir en la pantalla de inicio de sesión y SHALL mostrar el conversor únicamente después de un inicio de sesión exitoso. Cuando quien inicia sesión tiene rol admin, el sistema SHALL abrir el panel de administración en lugar del conversor.

#### Scenario: Pantalla inicial
- **WHEN** se abre la aplicación
- **THEN** se muestra la pantalla de inicio de sesión y no el conversor

#### Scenario: Inicio de sesión exitoso
- **WHEN** la persona ingresa un email y una contraseña válidos y confirma
- **THEN** se abre el conversor mostrando el email de la sesión

#### Scenario: Inicio de sesión de un admin
- **WHEN** inicia sesión una persona con rol admin
- **THEN** se abre el panel de administración, desde el cual puede abrir el conversor

#### Scenario: Acceso sin sesión
- **WHEN** no hay sesión iniciada
- **THEN** no hay forma de abrir el conversor desde la interfaz
