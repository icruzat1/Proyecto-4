# Verificación inicial · 16 de noviembre de 2026

La preparación se verificó en macOS con el firmware mantener de siete instrucciones. La estrategia de inversión y sus aceleradores se implementarán en las siguientes etapas.

| Comprobación | Resultado |
|---|---|
| Regresión del ensamblador sobre el juego anterior | Las 94 palabras HEX coinciden con la referencia del Proyecto 2 |
| Validaciones del ensamblador | Tres pruebas aprobadas, incluyendo 13 entradas inválidas |
| Serie de práctica | 20.000 ticks consecutivos, precios entre 72 y 190 |
| Simulación rápida, período 100.000 ns | 20.000 ticks, cinco chequeos aprobados |
| Decisiones y contabilidad exportadas | 20.000 decisiones mantener, caja y patrimonio 10.000, cero acciones |
| Peor latencia precio a escritura de DECISION | 18 ciclos, equivalentes a 0,72 microsegundos a 25 MHz |
| Presupuesto conservador de ronda rápida | 2.262 ciclos |
| Prueba breve con período 1.000.000 ns | Cinco ticks, cinco chequeos aprobados, peor latencia de 18 ciclos |
| Prueba breve con período 10.000.000 ns | Cinco ticks, cinco chequeos aprobados, peor latencia de 18 ciclos |
| Síntesis | 986 LUT4, 12 bloques RAM |
| Colocación y ruteo | 1.164 de 1.280 celdas lógicas, 12 de 16 bloques RAM |
| Temporización final | Aprobada a 25 MHz, frecuencia máxima estimada de 44,94 MHz |
| Bitstream generado | `build/trade.bin`, 32.220 bytes |

El testbench calculó 6.497 para su referencia comprar al inicio y mantener sobre la serie completa. El firmware inicial conserva 10.000 porque no realiza órdenes. Esta comprobación valida la integración y la respuesta SPI.

Las versiones efectivas están en `versions.json`. Se usaron Python 3.9.6, Icarus Verilog 14.0 devel, Yosys 0.68+130 y nextpnr-ice40 0.11.1-13 de OSS CAD Suite.

## Reproducción

```sh
python3 tools/test_assemble.py
python3 tools/project.py versions
python3 tools/project.py sim --expect-hold
python3 tools/project.py build
```

En Windows, sustituir `python3` por `py -3` y configurar la ruta `OSS_CAD_SUITE` según el README principal. La ejecución en Windows queda pendiente. Las pruebas físicas y programación quedan pendientes de disponibilidad de la Go Board.

Los registros `simulation.log`, `synthesis.log`, `place_route.log` y `smoke_*.log` conservan la salida de las herramientas. `decisiones.csv` permite inspeccionar todos los ticks. `serie.json` registra la validación del archivo de entrada y su SHA-256. `source_sha256.json` identifica los archivos fuente usados en esta preparación.
