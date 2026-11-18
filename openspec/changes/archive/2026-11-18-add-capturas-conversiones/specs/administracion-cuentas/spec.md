## MODIFIED Requirements

### Requirement: Configuración repetible de PocketBase
El proyecto SHALL incluir un script idempotente que cree los campos `rol` y `desactivado`, aplique las reglas de la colección `users`, cree la colección `consultas` con sus reglas y permita crear el primer admin con una contraseña aleatoria, así como crear el usuario de prueba (rol común) con las credenciales de `PB_TEST_EMAIL` y `PB_TEST_PASSWORD`.

#### Scenario: Ejecución repetida
- **WHEN** el script se ejecuta más de una vez
- **THEN** no duplica campos ni colecciones ni falla, y deja las reglas vigentes

#### Scenario: Colección de consultas
- **WHEN** el script se ejecuta sobre una base sin colección `consultas`
- **THEN** la crea con sus campos y reglas de aislamiento por usuario

#### Scenario: Creación del usuario de prueba
- **WHEN** el script se ejecuta con la opción de crear el usuario de prueba y las credenciales están definidas
- **THEN** el usuario existe con rol común y puede iniciar sesión, y si ya existía no falla ni cambia su contraseña

#### Scenario: Credenciales de prueba ausentes
- **WHEN** se pide crear el usuario de prueba y falta `PB_TEST_EMAIL` o `PB_TEST_PASSWORD`
- **THEN** el script termina indicando qué variable falta, sin crear nada
