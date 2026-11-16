## 1. PocketBase

- [x] 1.1 Extender `configurar_pocketbase.py` para crear/actualizar la colección `consultas` con sus campos y reglas; verificar ejecutándolo dos veces contra el servidor local sin errores y comprobando la colección por API
- [x] 1.2 Probar las reglas contra el servidor: un usuario lista solo lo suyo, no crea a nombre de otro, no modifica ni borra, y sin sesión se rechaza todo

## 2. Aplicación

- [x] 2.1 Agregar funciones de crear y listar consultas con el token de sesión; verificar con un script contra PocketBase que lo creado aparece en el listado del mismo usuario y no en el de otro
- [x] 2.2 Reemplazar el guardado en `historial.txt` por el guardado en PocketBase, con aviso si falla, y eliminar el código del TXT; verificar que una conversión crea la consulta, que no se crea `historial.txt` y que, con el servidor caído, se muestra el resultado y el aviso
- [x] 2.3 Mostrar la lista del historial en el conversor, actualizada al abrirlo y tras cada conversión, más reciente primero; verificar con dos usuarios que cada uno ve solo lo suyo y que un usuario nuevo ve la lista vacía

## 3. Cierre

- [x] 3.1 Actualizar `.gitignore` (quitar `historial.txt`) y recompilar `dist/Mi Cotizador.exe`; verificar que el ejecutable abre (el guardado se verificó con el script de pruebas sobre el mismo código; falta una prueba manual del .exe)
- [x] 3.2 Revisar los specs con `openspec validate --all --strict` y archivar el cambio
