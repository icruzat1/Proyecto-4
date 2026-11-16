# Decisiones de preparación

## 16 de noviembre de 2026

Se elige la copia portable del Proyecto 2 conservada en la entrega del Proyecto 3. La comparación con `nic0villegasc/pochoco_soc`, commit `33e8b5ae78faad7a9a36431d5ee8cf145e8573ec`, confirmó la igualdad de Espino, RAM, SPI, SoC y asignación de pines. Los cambios del grupo agregan el contador de ciclos y un wrapper con ruta relativa. La adaptación ASIC del Proyecto 3 usa reset y memoria externos, por lo que la copia FPGA conserva directamente las interfaces requeridas por el enunciado.

El wrapper se denomina `trade_top` y carga `sw/trade.hex`. El valor predeterminado de `MemFile` en `pochoco_soc.v` se ajusta a esa misma ruta para que Yosys pueda elaborar también el módulo sin parámetros. Se retiran del PCF las restricciones UART sin puertos asociados. Se mantiene el reloj de 25 MHz.

Se introduce un firmware mantener para verificar que Espino recibe precios y escribe DECISION. Su resultado esperado es conservar la caja inicial de 10.000 y cero acciones. La estrategia y las alternativas de hardware se elegirán en etapas posteriores con mediciones.

Se utiliza el ensamblador propio del grupo. El testbench del curso menciona `tools/pochoasm.py`, que no aparece en el árbol público revisado. El runner invoca directamente el ensamblador heredado y añade comprobaciones de rango y sintaxis para evitar truncamientos silenciosos.

El flujo común se implementa en Python para admitir argumentos con espacios y rutas relativas en macOS y Windows. La compilación del bitstream y la programación de la placa tienen comandos explícitos. Cada ejecución de simulación y compilación regenera el HEX.

La descarga directa de los adjuntos falló por conectividad. El CSV y el testbench se recuperaron mediante la lectura completa del contenido de los adjuntos, conservando el salto de línea final. Sus tamaños UTF-8 son 185.405 y 5.546 bytes, respectivamente, y coinciden con los tamaños informados por los adjuntos. Se verificaron la estructura del CSV, sus 20.000 ticks consecutivos y los precios entre 72 y 190. La copia recibida del testbench se conserva sin modificaciones en `tb/original/tb_proyecto_4.sv`. La verificación de tamaño y estructura queda registrada, mientras que una comparación byte a byte con una descarga independiente queda pendiente. El PDF permanece accesible mediante el enlace del README.

El banco adaptado permite seleccionar período y cantidad de ticks desde Icarus, usa 20.000 ticks por defecto, escribe en `build/decisiones.csv` y comprueba las filas de entrada. Se utiliza un registro empaquetado para leer el encabezado CSV y facilitar compatibilidad con `$fgets`. Se exige una respuesta por precio y que la última respuesta haya terminado. Un chequeo fallido finaliza con `$fatal` para devolver un código de error al runner. La transacción SPI y la contabilidad del original se conservan.

## Evidencia previa de selección de base

La prueba del juego anterior regeneró las mismas 94 instrucciones y pasó el arranque de 2.000 ciclos. La síntesis y el ruteo a 25 MHz generaron un bitstream de 32.220 bytes. Yosys contó 986 LUT4 y 12 bloques RAM. nextpnr utilizó 1.164 de 1.280 celdas lógicas y 12 de 16 bloques RAM, con frecuencia máxima estimada de 45,86 MHz. Estas cifras corresponden al juego anterior y sirven como referencia de recursos. La evidencia del firmware mantener se registra por separado.
