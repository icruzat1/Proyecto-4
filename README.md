# Proyecto 4 · Pochoco Trader

Universidad de los Andes, Arquitectura de Computadores, semestre 2026-2.

La entrega en GitHub está prevista para el 27 de noviembre de 2026 a las 10:00 y la competencia y defensa para las 10:30, según la confirmación de Ignacio. La prueba con la FPGA maestra figura para el 19 de noviembre en el enunciado.

El enunciado original está disponible en [Proyecto_4_arq.pdf](https://chatgpt.com/library?file_id=libfile_fde3_f-e6b073fafb108191b7d327e055e6041c_da192ca8c21881918569c8dedc38c031&account_id=personal). Su calendario impreso corresponde a la fecha previa del 24 de noviembre. La copia PDF local queda pendiente de descarga.

## Estado

Esta preparación establece el flujo de herramientas y un firmware de integración que lee cada precio SPI y escribe mantener. La estrategia de inversión, sus mediciones y las dos alternativas de aceleración por hardware corresponden a las siguientes etapas.

La verificación inicial en macOS completó los 20.000 ticks de práctica, con cinco chequeos aprobados y una latencia máxima de 18 ciclos. La síntesis, el ruteo a 25 MHz y la generación del bitstream fueron correctos. Los resultados y sus límites se detallan en [evidence/setup/README.md](evidence/setup/README.md).

El RTL procede de `Proyecto 3/entrega/baseline/proyecto2/pochoco_soc-main`. Los ocho archivos del núcleo Espino, el SPI, la RAM y `pochoco_soc.v` coinciden byte a byte con el repositorio del curso en el commit `33e8b5ae78faad7a9a36431d5ee8cf145e8573ec`. Se conserva el contador de ciclos añadido por el grupo en el Proyecto 2.

## Requisitos y comandos

Se necesita Python 3.9 o posterior y OSS CAD Suite con Icarus Verilog, Yosys, nextpnr-ice40, icepack e iceprog. Establecer `OSS_CAD_SUITE` con la carpeta de instalación permite localizar ejecutables y modelos de simulación. En macOS también se detecta `~/oss-cad-suite`. Alternativamente, los ejecutables pueden estar en `PATH` y el modelo en `YOSYS_DATDIR/ice40/cells_sim.v`.

Desde la raíz del repositorio, en macOS

```sh
export OSS_CAD_SUITE="$HOME/oss-cad-suite"
python3 tools/project.py versions
python3 tools/project.py assemble
python3 tools/project.py sim --expect-hold
python3 tools/project.py build
```

En Windows PowerShell, ajustar la ruta a la instalación propia

```powershell
$env:OSS_CAD_SUITE = 'C:\oss-cad-suite'
py -3 tools/project.py versions
py -3 tools/project.py assemble
py -3 tools/project.py sim --expect-hold
py -3 tools/project.py build
```

`build` genera `build/trade.bin`. Con la Go Board conectada, `python3 tools/project.py program` o `py -3 tools/project.py program` reconstruye el bitstream y ejecuta iceprog. La instalación del controlador USB depende del sistema y debe verificarse al disponer de la placa.

La simulación usa 20.000 ticks y un período de 100.000 ns por defecto. Para una prueba breve se puede usar `sim --ticks 100 --expect-hold`. `--period-ns` admite 100.000, 1.000.000 y 10.000.000. Retirar `--expect-hold` cuando se implemente una estrategia que opere.

El runner siempre resuelve las rutas respecto al repositorio y vuelve a ensamblar antes de simular o sintetizar. Los resultados y registros quedan en `build/`. El comando `versions` registra las versiones efectivamente ejecutadas en `build/versions.json`.

## Contenido

| Ruta | Función |
|---|---|
| `rtl/` | Espino, RAM, SPI, periféricos y wrapper `trade_top` |
| `sw/trade.s` | Firmware de integración con decisión mantener |
| `tools/assemble.py` | Ensamblador propio heredado del Proyecto 2 |
| `tools/project.py` | Ensamblado, simulación, síntesis y programación |
| `tb/original/` | Banco de pruebas suministrado por el curso |
| `tb/tb_proyecto_4.sv` | Adaptación reproducible con parámetros y controles adicionales |
| `tb/practica.csv` | Serie oficial de práctica |
| `docs/` | Enunciado, decisiones y procedimientos |
| `evidence/setup/` | Evidencia de la preparación inicial |

## Firmware y memoria

Espino opera a 25 MHz y tiene 16 registros de 32 bits. La RAM del SoC contiene 512 palabras compartidas entre programa y datos. El runner inicializa la parte libre con ceros y rechaza programas mayores que esa capacidad. La asignación entre código y datos deberá definirse al implementar la estrategia.

| Dirección | Registro | Acceso |
|---|---|---|
| `0x8000000C` | Contador de ciclos | Lectura |
| `0x80010000` | STATUS, bit 0 indica precio nuevo | Lectura |
| `0x80010004` | PRICE, su lectura limpia el indicador | Lectura |
| `0x80010008` | DECISION, acción y cantidad | Escritura |

El programa mantiene la base SPI en `x1`, consulta STATUS en `x2`, carga PRICE en `x3` y escribe cero en DECISION. La lectura y escritura las ejecuta Espino. El SPI devuelve durante el tick actual la decisión preparada tras el precio anterior.

El ensamblador admite `lui`, `addi`, `andi`, `add`, `sub`, `lw`, `sw`, `beq`, `bne`, `blt` y `jal`, registros `x0` a `x15` y etiquetas. Acepta las declaraciones `.text`, `.section .text`, `.global` y `.globl`. Rechaza directivas desconocidas, etiquetas duplicadas, operandos sobrantes, registros fuera de RV32E, inmediatos fuera de rango y saltos desalineados a instrucciones de 4 bytes. La ampliación de instrucciones se realizará según el algoritmo elegido.

## Verificación pendiente

Las pruebas físicas necesitan la Go Board y la FPGA maestra. Los comandos Windows están preparados mediante Python y rutas relativas, pero deben ejecutarse en Windows para confirmar esa plataforma. La comparación completa con una referencia de inversión se implementará junto con la estrategia.
