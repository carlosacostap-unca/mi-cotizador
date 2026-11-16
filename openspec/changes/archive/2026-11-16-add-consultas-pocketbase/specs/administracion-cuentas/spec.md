## MODIFIED Requirements

### Requirement: Configuración repetible de PocketBase
El proyecto SHALL incluir un script idempotente que cree los campos `rol` y `desactivado`, aplique las reglas de la colección `users`, cree la colección `consultas` con sus reglas y permita crear el primer admin con una contraseña aleatoria.

#### Scenario: Ejecución repetida
- **WHEN** el script se ejecuta más de una vez
- **THEN** no duplica campos ni colecciones ni falla, y deja las reglas vigentes

#### Scenario: Colección de consultas
- **WHEN** el script se ejecuta sobre una base sin colección `consultas`
- **THEN** la crea con sus campos y reglas de aislamiento por usuario
