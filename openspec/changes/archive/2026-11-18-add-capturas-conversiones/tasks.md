## 1. Usuario de prueba

- [x] 1.1 Agregar `PB_TEST_EMAIL` y `PB_TEST_PASSWORD` a `.env.example` (sin valores) y la opción `--crear-usuario-prueba` a `configurar_pocketbase.py`; verificar creándolo, ejecutándolo de nuevo sin error y sin cambiar la contraseña, y con las variables ausentes (error que nombra la faltante)
- [x] 1.2 Crear el usuario de prueba en la base local y guardar sus credenciales en el `.env`; verificar que inicia sesión por la API y que no es admin

## 2. Programa

- [x] 2.1 Agregar Pillow a `requirements.txt` y verificar que captura la ventana con las dimensiones reales (520×431 el login, 814×898 el conversor)
- [x] 2.2 Crear `capturas_conversiones.py` con la lectura del `.env`, la cuenta regresiva y el aviso, la apertura de la aplicación (código fuente o `--exe`) y el cierre en `finally`; verificar que sin las variables aborta antes de abrir nada y que con cancelación no deja procesos
- [x] 2.3 Implementar el inicio de sesión por teclado y la comprobación de que el conversor abrió; verificar con credenciales válidas y con una contraseña incorrecta (error claro, sin mostrar la clave)
- [x] 2.4 Implementar las diez conversiones con espera por sondeo del historial y captura PNG de la ventana tras cada una, en `capturas/<fecha>/NN_monto.png`; verificar que se generan diez imágenes y que cada una muestra el resultado
- [x] 2.5 Implementar la verificación contra PocketBase (diez consultas con el monto y el resultado esperados) y el código de salida; verificar el caso correcto (10 de 10, código 0) y un caso forzado con un valor alterado (código distinto de cero)

## 3. Cierre

- [x] 3.1 Agregar `capturas/` al `.gitignore` y la sección de uso al `README.md`; verificar con `git status` que las capturas no aparecen y que el README coincide con las opciones reales
- [x] 3.2 Ejecutar el programa completo dos veces, con el código fuente y con el `.exe`, revisar visualmente las capturas, confirmar que no hay credenciales en los archivos versionados y que el usuario de prueba sigue existiendo; correr `openspec validate --all --strict` y archivar el cambio
