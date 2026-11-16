## 1. Configuración

- [x] 1.1 Agregar `DOLARAPI_URL` a `.env` y a `.env.example` (sin valor) y leerla en la aplicación; verificar que sin la variable la aplicación avisa y no consulta, y con ella lee el valor

## 2. Consulta de la cotización

- [x] 2.1 Implementar la consulta y validación de la respuesta (`venta` numérico mayor que cero, `fechaActualizacion`); verificar con pruebas de respuesta válida, sin `venta`, `venta` cero o negativa, error HTTP y servidor inalcanzable
- [x] 2.2 Ejecutar la consulta en un hilo con tiempo de espera de 5 s y devolver el resultado a la interfaz con `after()`; verificar con un servicio simulado lento que la ventana responde mientras espera y que una respuesta tardía de otra sesión se descarta

## 3. Interfaz

- [x] 3.1 Cargar la cotización al abrir el conversor solo si el campo está vacío y mostrar origen y fecha; verificar que un campo con valor no se pisa al volver desde el panel
- [x] 3.2 Agregar el botón **Actualizar cotización** que reemplaza el valor del campo; verificar que reemplaza aunque el campo tenga un valor editado a mano
- [x] 3.3 Mostrar un aviso junto al campo cuando la consulta falla, dejando el campo intacto y la conversión manual disponible; verificar con la dirección apuntando a un servicio caído que se puede convertir igualmente

## 4. Cierre

- [x] 4.1 Probar el flujo completo contra dolarapi.com real: abrir, ver el valor de venta cargado, actualizar y convertir; verificar que el historial guarda la cotización usada
- [x] 4.2 Recompilar `dist/Mi Cotizador.exe`, verificar que abre, correr `openspec validate --all --strict` y archivar el cambio
