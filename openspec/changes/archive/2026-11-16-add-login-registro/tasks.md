## 1. Cliente de PocketBase

- [x] 1.1 Implementar inicio de sesión y registro contra la API; verificado contra el PocketBase local (registro, login correcto y login con clave mala)
- [x] 1.2 Traducir errores (duplicado, clave corta, credenciales, servidor caído); verificado con un script contra el servidor real y con un puerto sin servicio

## 2. Pantallas

- [x] 2.1 Crear las pantallas de login y registro; verificado que la aplicación abre en el login
- [x] 2.2 Bloquear el conversor sin sesión y agregar Cerrar sesión; verificado instanciando la aplicación (sin sesión → login, con sesión → conversor, cerrar → login)

## 3. Entrega

- [x] 3.1 Hacer configurable la URL con `POCKETBASE_URL`; verificado en el código y probado con el valor por defecto
- [x] 3.2 Recompilar `dist/Mi Cotizador.exe`; verificado que abre sin errores
