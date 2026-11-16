## Purpose

Permite a las personas con rol admin ver todas las cuentas, desactivarlas y resetear su contraseña, y garantiza desde el servidor que nadie más pueda hacerlo.

## ADDED Requirements

### Requirement: Roles de usuario
Cada cuenta SHALL tener un rol `usuario` o `admin`; una cuenta sin rol asignado SHALL tratarse como `usuario`. Nadie SHALL poder asignarse un rol, ni crear una cuenta con rol, por su cuenta: solo un admin puede cambiar roles.

#### Scenario: Registro sin privilegios
- **WHEN** alguien intenta registrarse indicando rol `admin` o estado desactivado
- **THEN** el servidor rechaza el registro

#### Scenario: Autoascenso
- **WHEN** un usuario común intenta cambiar su propio rol o su estado de desactivación
- **THEN** el servidor rechaza el cambio

### Requirement: Alcance de visibilidad de cuentas
El servidor SHALL permitir que cada usuario vea solo su propia cuenta y que un admin activo vea todas, incluidos los emails.

#### Scenario: Usuario común
- **WHEN** un usuario común solicita el listado de cuentas
- **THEN** recibe únicamente su propia cuenta

#### Scenario: Admin
- **WHEN** un admin solicita el listado de cuentas
- **THEN** recibe todas las cuentas con su email, rol y estado

### Requirement: Panel de administración
La aplicación SHALL ofrecer a los admins un panel que liste las cuentas con email, rol, estado (activa o desactivada) y fecha de alta, con botones para actualizar la lista, activar o desactivar la cuenta seleccionada, resetear su contraseña, abrir el conversor y cerrar sesión. Un usuario sin rol admin SHALL no poder abrir el panel.

#### Scenario: Listado
- **WHEN** un admin abre el panel
- **THEN** se muestran todas las cuentas registradas

#### Scenario: Usuario común no accede
- **WHEN** un usuario común intenta abrir el panel
- **THEN** permanece en el conversor

#### Scenario: Navegación de un admin
- **WHEN** un admin pulsa Abrir conversor y luego Panel de administración
- **THEN** puede alternar entre el conversor y el panel sin volver a iniciar sesión

### Requirement: Desactivación de cuentas
Un admin SHALL poder desactivar y reactivar cuentas, previa confirmación, excepto la suya. Una cuenta desactivada SHALL no poder iniciar sesión, y un admin desactivado SHALL perder sus permisos de administración.

#### Scenario: Desactivar una cuenta
- **WHEN** un admin confirma la desactivación de una cuenta ajena
- **THEN** la cuenta figura como desactivada y no puede iniciar sesión

#### Scenario: Reactivar una cuenta
- **WHEN** un admin reactiva una cuenta desactivada
- **THEN** la persona puede volver a iniciar sesión

#### Scenario: Autodesactivación
- **WHEN** un admin intenta desactivar su propia cuenta desde el panel
- **THEN** se muestra un aviso y no se realiza el cambio

### Requirement: Reseteo de contraseña por un admin
Un admin SHALL poder fijar una contraseña nueva (de al menos 8 caracteres, escrita dos veces) para otra cuenta sin conocer la anterior. Ningún usuario común SHALL poder cambiar la contraseña de otra cuenta.

#### Scenario: Reseteo exitoso
- **WHEN** un admin ingresa y confirma una contraseña nueva para una cuenta
- **THEN** esa cuenta inicia sesión con la contraseña nueva y no con la anterior

#### Scenario: Contraseña inválida
- **WHEN** la contraseña tiene menos de 8 caracteres o las dos entradas no coinciden
- **THEN** se muestra un error y no se cambia nada

#### Scenario: Intento de un usuario común
- **WHEN** un usuario común intenta cambiar o desactivar otra cuenta directamente contra el servidor
- **THEN** el servidor rechaza la operación

### Requirement: Configuración repetible de PocketBase
El proyecto SHALL incluir un script idempotente que cree los campos `rol` y `desactivado`, aplique las reglas de la colección `users` y permita crear el primer admin con una contraseña aleatoria.

#### Scenario: Ejecución repetida
- **WHEN** el script se ejecuta más de una vez
- **THEN** no duplica campos ni falla, y deja las reglas vigentes
