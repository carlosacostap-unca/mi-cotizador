## MODIFIED Requirements

### Requirement: Historial de conversiones
El sistema SHALL guardar cada conversión exitosa en el historial del usuario en PocketBase y SHALL NOT escribir `historial.txt` ni ningún otro archivo local. Si no se puede guardar, SHALL mostrar igualmente el resultado y avisar que no se pudo guardar.

#### Scenario: Conversión registrada
- **WHEN** una conversión se realiza con éxito
- **THEN** se guarda una consulta en PocketBase a nombre del usuario con sesión iniciada y no se escribe ningún archivo de texto

#### Scenario: Historial no escribible
- **WHEN** PocketBase no responde o rechaza el guardado de la consulta
- **THEN** el sistema muestra el resultado igualmente y avisa que no se pudo guardar el historial
