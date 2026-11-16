## Purpose

Evita ingresar a mano la cotización del dólar: la aplicación la obtiene de una API pública y permite actualizarla cuando la persona quiera.

## ADDED Requirements

### Requirement: Cotización automática al abrir el conversor
El sistema SHALL consultar la cotización del dólar oficial al abrirse el conversor y SHALL cargar el valor de venta en el campo de cotización, siempre que el campo esté vacío. El sistema SHALL mostrar junto al campo el origen del valor y la fecha de actualización informada por el servicio.

#### Scenario: Campo vacío al abrir
- **WHEN** se abre el conversor y el campo de cotización está vacío
- **THEN** el campo se completa con el valor de venta del dólar oficial y se muestra la fecha de actualización

#### Scenario: Campo con un valor ingresado
- **WHEN** se vuelve al conversor y el campo ya tiene un valor
- **THEN** el valor existente no se reemplaza

#### Scenario: Interfaz disponible durante la consulta
- **WHEN** la consulta tarda en responder
- **THEN** la ventana sigue respondiendo y se puede convertir con un valor ingresado a mano

### Requirement: Actualización manual de la cotización
El sistema SHALL ofrecer un botón **Actualizar cotización** que consulte de nuevo el servicio y reemplace el valor del campo de cotización por el de venta obtenido, aunque el campo tenga un valor.

#### Scenario: Actualizar
- **WHEN** la persona pulsa Actualizar cotización y el servicio responde
- **THEN** el campo muestra el valor de venta actual y se actualiza la fecha mostrada

#### Scenario: Valor editado a mano
- **WHEN** la persona editó el campo y pulsa Actualizar cotización
- **THEN** el valor editado se reemplaza por el obtenido del servicio

### Requirement: Cotización editable
El sistema SHALL permitir editar el campo de cotización aunque se haya cargado automáticamente, y SHALL usar el valor que figure en el campo al convertir.

#### Scenario: Convertir con cotización propia
- **WHEN** la persona cambia el valor cargado y pulsa Convertir
- **THEN** la conversión y el historial usan el valor del campo

### Requirement: Tolerancia a fallas de la consulta
Si el servicio no responde, devuelve un error o una respuesta sin valor de venta válido, el sistema SHALL avisar con un mensaje comprensible junto al campo, dejar el campo como estaba y SHALL seguir permitiendo la conversión con ingreso manual.

#### Scenario: Sin conexión
- **WHEN** no se puede conectar con el servicio al abrir el conversor
- **THEN** se muestra un aviso, el campo queda vacío y se puede ingresar la cotización a mano

#### Scenario: Falla al actualizar
- **WHEN** la actualización falla con un valor ya cargado
- **THEN** se mantiene el valor del campo y se muestra el aviso

#### Scenario: Respuesta inválida
- **WHEN** el servicio responde sin un valor de venta positivo
- **THEN** se muestra un aviso y el campo no cambia

### Requirement: Dirección del servicio configurable
La dirección del servicio de cotizaciones SHALL leerse de la variable `DOLARAPI_URL` (archivo `.env` o entorno) y no estar escrita en el código. Si falta, el sistema SHALL avisar que hay que configurarla y seguir permitiendo el ingreso manual.

#### Scenario: Variable ausente
- **WHEN** `DOLARAPI_URL` no está definida
- **THEN** se muestra un aviso indicando que falta configurarla y no se intenta ninguna consulta
