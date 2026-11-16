## 1. PocketBase

- [x] 1.1 Crear `configurar_pocketbase.py` con campos `rol` y `desactivado` y las reglas de `users`; verificado ejecutándolo contra el servidor local, dos veces, sin errores
- [x] 1.2 Agregar `manageRule` para ver emails y resetear contraseñas como admin; verificado en las pruebas del panel
- [x] 1.3 Crear el primer admin con clave aleatoria; verificado iniciando sesión y comprobando `rol = admin`

## 2. Aplicación

- [x] 2.1 Guardar rol, id y token de la sesión y mostrar el panel a los admins; verificado instanciando la aplicación (admin → panel, usuario común → conversor)
- [x] 2.2 Construir el panel con lista, activar/desactivar y resetear contraseña con confirmación; verificado cargando las cuentas reales
- [x] 2.3 Bloquear el panel a no admins y la autodesactivación; verificado por navegación y por código

## 3. Verificación

- [x] 3.1 Probar las reglas contra PocketBase (registro con rol, autoascenso, listado, desactivar y resetear como usuario común y como admin); 20 comprobaciones correctas
- [x] 3.2 Recompilar `dist/Mi Cotizador.exe`; verificado que abre sin errores
