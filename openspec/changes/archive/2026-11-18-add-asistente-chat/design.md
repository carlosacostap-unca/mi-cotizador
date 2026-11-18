## Context

`mi_cotizador.py` concentra la aplicación Tkinter con pantallas intercambiables (login, registro, conversor, panel de admin) y funciones ya reutilizables: `convertir`, `parsear_numero`, `obtener_cotizacion` (hilo + `after()` para no bloquear), `guardar_consulta` y `listar_consultas` con el token de sesión. La configuración sale de `.env` mediante `entorno.py`, sin direcciones ni valores por defecto en el código. Los servicios externos se consultan con `urllib`, sin SDK. Ver proposal.md para la motivación.

## Goals / Non-Goals

**Goals:**
- Un chat acotado a funciones de usuario ya existentes, con ejecución local y validación estricta.
- Mantener el patrón del proyecto: `urllib`, configuración por `.env`, hilos con `after()`.

**Non-Goals:**
- Funciones de administración por chat (decisión del usuario).
- Streaming de respuestas, voz, imágenes o archivos.
- Guardar las conversaciones, o enviarlas a PocketBase.
- Otros proveedores de IA.

## Decisions

- **Llamadas a funciones (tool calling) sobre la API de chat de OpenAI**, con `urllib` y autenticación `Authorization: Bearer`. Alternativas descartadas: el SDK oficial (una dependencia más para dos llamadas HTTP) y pedir al modelo respuestas en texto libre para interpretarlas (frágil). Se envían solo parámetros básicos (`model`, `messages`, `tools`) para no depender de opciones que varían entre modelos.
- **Configuración sin valores por defecto**: `OPENAI_API_KEY`, `OPENAI_MODEL` y `OPENAI_URL` en el `.env`, por coherencia con las demás direcciones y porque los nombres de modelo cambian con el tiempo. Si falta alguna, el chat lo dice y deshabilita el envío; no afecta al resto de la app.
- **Funciones expuestas** (nombres y descripciones en español, esquemas JSON estrictos): `convertir_pesos_a_dolares(monto_pesos, cotizacion?)`, `obtener_cotizacion_oficial()`, `actualizar_cotizacion()` (carga la venta vigente en el campo del conversor) y `ver_historial(cantidad?)`. Sin cotización indicada, la conversión usa la venta del dólar oficial consultada en el momento. Alternativa descartada: usar el valor que esté en el campo del conversor, que puede estar vacío o desactualizado.
- **La conversión por chat guarda en el historial** igual que el botón, reutilizando la misma lógica, para no tener dos caminos con reglas distintas.
- **Ejecución local con la sesión del usuario**: las funciones usan el token de la sesión, de modo que las reglas de PocketBase siguen siendo la barrera real (cada usuario solo ve y crea lo suyo). El modelo nunca recibe el token, la contraseña ni el email.
- **Validación local de argumentos**: el modelo puede proponer cualquier cosa; se verifica tipo, rango (montos y cotizaciones mayores que cero, historial de 1 a 50) y se devuelve el error como resultado de la función para que el modelo se corrija. Los resultados de las funciones se tratan como datos, no como instrucciones.
- **Máximo de 5 rondas** de funciones por mensaje y de **20 mensajes** de contexto, para acotar costo y bucles.
- **Hilo de trabajo + cola + `after()`**, como la cotización automática: la ventana sigue respondiendo, se muestra "El asistente está respondiendo…", se bloquea el envío mientras tanto y se descarta la respuesta si cambió la sesión. Las funciones que tocan widgets (actualizar el campo de cotización) se ejecutan en el hilo principal, no en el de red.
- **Pantalla propia** (decisión del usuario): `PantallaChat` con historial de mensajes (texto de solo lectura con scroll), campo de entrada, botones Enviar y Volver al conversor, y el aviso de privacidad. El botón del conversor la abre; al volver, el conversor recarga el historial por su `al_mostrar`.
- **Mensaje de sistema** breve en español: asistente de Mi Cotizador, usa solo las funciones, no inventa cifras, responde con los números exactos que devuelven las funciones y rechaza pedidos de administración.
- **Errores de la API traducidos** (401 → clave inválida, 429 → límite de uso, otros → código y mensaje del servicio sin la clave, red → sin conexión, 60 s de espera), conservando la conversación.

## Risks / Trade-offs

- [Cada mensaje consume crédito de la cuenta de OpenAI] → Tope de rondas y de contexto, y aviso en el README.
- [Se envían datos a un tercero] → Aviso visible en el chat; no se envían token, contraseña ni email; el historial solo viaja si el usuario lo pide.
- [El modelo puede interpretar mal un pedido, por ejemplo un monto ("150 mil")] → La respuesta final muestra los números exactos que devolvió la función; la conversión guardada queda visible en el historial.
- [Inyección de instrucciones en los datos devueltos (por ejemplo por la API de cotización)] → Solo hay funciones de usuario, sin acciones destructivas ni de administración, con argumentos validados.
- [No se puede probar contra la API real sin una clave] → Se prueba con un servidor local que imita la API y se deja la prueba real para cuando la clave esté en el `.env`.
- [`mi_cotizador.py` sigue creciendo] → El cliente de OpenAI y las funciones quedan en funciones separadas de la interfaz, fáciles de mover a un módulo propio si hace falta.
