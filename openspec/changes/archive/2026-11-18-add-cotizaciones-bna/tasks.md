## 1. Configuración

- [x] 1.1 Agregar `BNA_URL` a `.env.example` (sin valor) y al `.env` local, y `cotizaciones_bna.csv` al `.gitignore`; verificar que `git status` no lo muestra y que el programa avisa si la variable falta sin hacer ninguna consulta

## 2. Lectura de la página

- [x] 2.1 Implementar el analizador de la tabla de divisas (contenedor `divisas`, fecha del encabezado, fila "Dolar U.S.A", números con punto o coma); verificar con un HTML de ejemplo propio que devuelve compra, venta y fecha, y que ignora la tabla de billetes aunque tenga otros valores
- [x] 2.2 Implementar la lectura estricta y los errores (sin tabla, sin fila, valores no numéricos, cero o negativos, sin fecha); verificar con HTML alterado que cada caso lanza un error claro y nunca devuelve valores parciales
- [x] 2.3 Implementar la consulta HTTP (una sola solicitud, 20 s, User-Agent genérico, sin reintentos); verificar con un servidor local de prueba el caso correcto, un error HTTP, una respuesta lenta y un servidor inalcanzable

## 3. Registro en el CSV

- [x] 3.1 Implementar la escritura acumulativa (encabezado solo al crear, `;` como separador, coma decimal, UTF-8 con BOM, fecha y hora local de la consulta); verificar creando el archivo, ejecutando dos veces y leyendo con el módulo `csv` que hay dos filas y un solo encabezado
- [x] 3.2 Garantizar que ante cualquier falla no se crea ni se modifica el archivo, y que un error de escritura se informa con claridad; verificar con el archivo inexistente y con uno ya existente, comparando su contenido antes y después de una falla

## 4. Cierre

- [x] 4.1 Probar contra la página real del BNA y comprobar a mano que la compra y la venta guardadas coinciden con la tabla "Cotización Divisas" de la página
- [x] 4.2 Agregar la sección de uso al `README.md` (incluida la programación con el Programador de tareas y la nota sobre Excel), verificar con una búsqueda que no hay direcciones ni credenciales en los archivos versionados, correr `openspec validate --all --strict` y archivar el cambio
