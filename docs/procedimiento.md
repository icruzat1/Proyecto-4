# Procedimiento e instrumentos

1. Registrar fecha, sistema, commit y versiones con `tools/project.py versions`.
2. Ensamblar `sw/trade.s`. Revisar los errores de sintaxis y la capacidad de RAM.
3. Simular con Icarus Verilog y el modelo `cells_sim.v` de iCE40. Revisar recepción de precios, cantidad de respuestas, valores definidos de MISO y presupuesto de ciclos.
4. Examinar `build/decisiones.csv` y compararlo con la referencia correspondiente. En esta etapa, `--expect-hold` comprueba decisión cero y patrimonio 10.000 en todos los ticks.
5. Sintetizar con Yosys, colocar y rutear con nextpnr-ice40 a 25 MHz y generar el bitstream con icepack. Revisar LUTs, RAM, celdas lógicas y temporización.
6. Al disponer de la placa, programar mediante el comando `program`, comprobar SPI modo 0 y registrar conexiones, instrumentos y resultados de la prueba física.

La evidencia inicial conserva los registros relevantes y un resumen de resultados en `evidence/setup/`. Cada etapa posterior debe registrar sus decisiones, métricas, limitaciones y resultados reproducibles antes de pasar a la siguiente.

La serie de prueba debe contener columnas `tick,price`, ticks consecutivos desde cero y precios enteros entre 1 y 255. El banco adaptado comprueba las filas que utiliza y falla con salida de error si se incumple un chequeo. El período rápido ofrece un presupuesto conservador de 2.262 ciclos tras descontar 9,5 microsegundos de SPI.
