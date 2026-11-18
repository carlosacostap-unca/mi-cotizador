## 1. Preparación

- [x] 1.1 Crear `requirements.txt` con la versión fijada de `mcp`, instalarla y verificar con `pip show mcp` y una importación del servidor de ejemplo del SDK que la API elegida existe
- [x] 1.2 Crear el esqueleto de `mcp_pocketbase.py` (arranque por stdio, carga del `.env`, salida estándar reservada al protocolo); verificar con un cliente MCP de prueba que lista las herramientas sin escribir nada extra por la salida estándar

## 2. Cliente de PocketBase

- [x] 2.1 Implementar autenticación de superusuario con renovación ante un 401 y mensajes de error sin credenciales; verificar con PocketBase encendido, con credenciales incorrectas y con PocketBase apagado
- [x] 2.2 Implementar el control de colecciones de sistema (nombre con `_` inicial) en un único punto; verificar que cada herramienta rechaza `_superusers`

## 3. Herramientas

- [x] 3.1 Herramientas de estado y esquema (`pb_salud`, `pb_listar_colecciones`, `pb_ver_coleccion`); verificar contra la base local que devuelven `users` y `consultas` con sus campos y reglas, y no las colecciones de sistema
- [x] 3.2 Herramientas de lectura (`pb_listar_registros`, `pb_ver_registro`) con filtro, orden, paginación y tope de 100; verificar con un filtro sobre `consultas`, con 500 por página (se limita) y con un id inexistente
- [x] 3.3 Herramientas de escritura de registros (`pb_crear_registro`, `pb_actualizar_registro`, `pb_borrar_registro`); verificar con una colección temporal: crear válido, crear inválido (error por campo), modificar y borrar
- [x] 3.4 Herramientas de colecciones (`pb_crear_coleccion`, `pb_actualizar_coleccion`) y comprobar que no hay herramienta de borrado de colecciones; verificar creando y modificando una colección temporal y revisando la lista de herramientas

## 4. Integración y cierre

- [x] 4.1 Crear `.mcp.json` sin direcciones ni credenciales; verificar con una búsqueda que no hay literales de URL ni contraseñas en `.mcp.json` ni en el código, y que el servidor arranca iniciado desde la raíz del proyecto
- [x] 4.2 Probar el servidor de punta a punta con un cliente MCP por stdio sobre la base local, incluido el caso de variable faltante; limpiar los datos de prueba y confirmar que `users` y `consultas` quedan intactas
- [x] 4.3 Escribir el README con instalación, activación, variables, herramientas y riesgos; verificar que `.env.example` y el README coinciden en las variables
- [x] 4.4 Correr `openspec validate --all --strict` y archivar el cambio
