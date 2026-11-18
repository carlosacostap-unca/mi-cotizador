## 1. Configuración

- [x] 1.1 Agregar `OPENAI_API_KEY`, `OPENAI_MODEL` y `OPENAI_URL` a `.env.example` (sin valores) y leerlas en la aplicación; verificar que sin cada una el chat avisa cuál falta, no envía nada y el resto de la app funciona, y que ninguna aparece con valor en archivos versionados

## 2. Cliente de la API

- [x] 2.1 Implementar la solicitud de chat con `tools` por `urllib` (Bearer, 60 s de espera, solo `model`, `messages` y `tools`) y el análisis de la respuesta; verificar con un servidor local que imita la API una respuesta de texto y una con llamadas a funciones, y que la clave solo viaja en la cabecera
- [x] 2.2 Implementar la traducción de errores (401, 429, otros códigos, red, tiempo de espera, JSON ilegible) sin mostrar la clave; verificar cada caso con el servidor local y buscando la clave en todos los mensajes
- [x] 2.3 Implementar el ciclo de funciones (máximo 5 rondas, contexto de 20 mensajes); verificar con respuestas simuladas: sin funciones, una función, varias seguidas y un bucle infinito que se corta en la quinta ronda

## 3. Funciones de la app

- [x] 3.1 Implementar `convertir_pesos_a_dolares` con la misma conversión y guardado en el historial que el botón, usando la venta oficial si no se indica cotización; verificar contra PocketBase real que se guarda la consulta del usuario y con un servicio simulado de cotización
- [x] 3.2 Implementar `obtener_cotizacion_oficial`, `actualizar_cotizacion` y `ver_historial` (1 a 50, solo las del usuario); verificar con dos usuarios que cada uno ve solo lo suyo y que la actualización llena el campo del conversor
- [x] 3.3 Validar localmente los argumentos del modelo (tipos, montos y cotizaciones mayores que cero, cantidad) devolviendo errores comprensibles; verificar con argumentos negativos, cero, texto, ausentes y excesivos que no se ejecuta ni guarda nada, y que no existe ninguna función de administración expuesta

## 4. Pantalla de chat

- [x] 4.1 Crear `PantallaChat` (mensajes con desplazamiento, campo de entrada con Enter, Enviar, Volver, aviso de privacidad) y el botón Asistente en el conversor; verificar la navegación de ida y vuelta conservando el monto y la cotización, y que sin sesión no se accede
- [x] 4.2 Ejecutar las consultas en un hilo con indicador y envío bloqueado, descartando respuestas de otra sesión y ejecutando en el hilo principal lo que toca widgets; verificar con un servidor lento que la ventana responde, que no se puede enviar dos veces y que cerrar sesión durante la espera no muestra nada
- [x] 4.3 Borrar la conversación al cerrar sesión; verificar con dos usuarios que el segundo ve el chat vacío
- [x] 4.4 Probar el chat en la ventana real contra el servidor simulado con una captura de pantalla que muestre un pedido de conversión, la respuesta y la fila nueva en el historial al volver al conversor

## 5. Cierre

- [x] 5.1 Probar contra la API real de OpenAI con la clave del `.env`: pedir una conversión, consultar la cotización, ver el historial y pedir algo de administración (debe negarse); si todavía no hay clave configurada, dejar anotado que esta prueba queda a cargo de quien agregue la clave. **Nota al archivar: no había clave en el `.env`, esta prueba con la API real NO se hizo y queda pendiente (ver README).**
- [x] 5.2 Documentar en el `README.md` la configuración, el costo, el envío de datos a OpenAI y las funciones disponibles; recompilar `dist/Mi Cotizador.exe`, correr `openspec validate --all --strict` y archivar el cambio
