#!/usr/bin/env python3
"""Flujo reproducible desde macOS y Windows con Python y OSS CAD Suite."""
import argparse
import csv
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

from assemble import assemble

ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / "build"


def suite_root():
    configured = os.environ.get("OSS_CAD_SUITE")
    if configured:
        return Path(configured).expanduser().resolve()
    candidate = Path.home() / "oss-cad-suite"
    return candidate if candidate.is_dir() else None


def tool(name):
    suite = suite_root()
    suffix = ".exe" if os.name == "nt" else ""
    if suite and (suite / "bin" / (name + suffix)).is_file():
        return str(suite / "bin" / (name + suffix))
    found = shutil.which(name)
    if not found:
        raise RuntimeError(f"Falta {name}. Configure OSS_CAD_SUITE o PATH.")
    return found


def run(command, log):
    env = os.environ.copy()
    suite = suite_root()
    if suite:
        env["PATH"] = str(suite / "bin") + os.pathsep + env.get("PATH", "")
    result = subprocess.run(command, cwd=ROOT, env=env, text=True,
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    (BUILD / log).write_text(result.stdout, encoding="utf-8")
    print(result.stdout)
    if result.returncode:
        raise RuntimeError(f"Fallo de {command[0]}. Consulte build/{log}.")
    return result.stdout


def assemble_firmware():
    words = assemble((ROOT / "sw/trade.s").read_text(encoding="utf-8"))
    if len(words) > 512:
        raise RuntimeError("El programa excede las 512 palabras de RAM.")
    # Initialize unused RAM so simulation and FPGA start from defined contents.
    (ROOT / "sw/trade.hex").write_text(
        "\n".join(words + ["00000000"] * (512 - len(words))) + "\n",
        encoding="ascii")
    print(f"Ensambladas {len(words)} instrucciones. RAM de 512 palabras inicializada.")


def cells_model():
    suite = suite_root()
    if suite and (suite / "share/yosys/ice40/cells_sim.v").is_file():
        return str(suite / "share/yosys/ice40/cells_sim.v")
    configured = os.environ.get("YOSYS_DATDIR")
    if configured and (Path(configured) / "ice40/cells_sim.v").is_file():
        return str(Path(configured) / "ice40/cells_sim.v")
    raise RuntimeError("Defina OSS_CAD_SUITE o YOSYS_DATDIR para cells_sim.v.")


def simulate(args):
    if not 1 <= args.ticks <= 20000:
        raise RuntimeError("--ticks debe estar entre 1 y 20000.")
    assemble_firmware()
    sources = [str(p.relative_to(ROOT)) for p in sorted((ROOT / "rtl").rglob("*.v"))]
    run([tool("iverilog"), "-g2012", "-s", "tb_proyecto_4",
         f"-Ptb_proyecto_4.NTICKS={args.ticks}",
         f"-Ptb_proyecto_4.PERIODO_NS={args.period_ns}",
         "-o", "build/sim.vvp", cells_model(), *sources, "tb/tb_proyecto_4.sv"],
        "compile.log")
    output = run([tool("vvp"), "build/sim.vvp"], "simulation.log")
    if "FAIL" in output or "Testbenchs aprobados: 5/5" not in output:
        raise RuntimeError("La simulacion no aprobo todos los chequeos.")
    with (BUILD / "decisiones.csv").open(newline="", encoding="utf-8") as source:
        rows = list(csv.DictReader(source))
    if len(rows) != args.ticks:
        raise RuntimeError("Cantidad de decisiones exportadas incorrecta.")
    if args.expect_hold:
        if any(int(row["decision"], 16) != 0 or int(row["patrimonio"]) != 10000 for row in rows):
            raise RuntimeError("La prueba de mantener detecto una orden o patrimonio incorrecto.")
        print(f"PASS firmware mantener en {len(rows)} ticks.")


def build():
    assemble_firmware()
    script = ("read_verilog rtl/*.v rtl/espino_core/*.v; "
              "synth_ice40 -top trade_top -json build/trade.json; stat")
    run([tool("yosys"), "-p", script], "synthesis.log")
    run([tool("nextpnr-ice40"), "--hx1k", "--package", "vq100", "--freq", "25",
         "--json", "build/trade.json", "--pcf", "goboard.pcf", "--asc", "build/trade.asc"],
        "place_route.log")
    run([tool("icepack"), "build/trade.asc", "build/trade.bin"], "icepack.log")


def versions():
    data = {"python": sys.version, "platform": sys.platform}
    for name, flag in [("iverilog", "-V"), ("yosys", "-V"), ("nextpnr-ice40", "--version")]:
        data[name] = run([tool(name), flag], name + "_version.log").strip()
    (BUILD / "versions.json").write_text(json.dumps(data, indent=2), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["assemble", "sim", "build", "program", "versions"])
    parser.add_argument("--ticks", type=int, default=20000)
    parser.add_argument("--period-ns", type=int, choices=[100000, 1000000, 10000000], default=100000)
    parser.add_argument("--expect-hold", action="store_true", help="Valida el firmware inicial mantener")
    args = parser.parse_args()
    BUILD.mkdir(exist_ok=True)
    try:
        if args.action == "assemble":
            assemble_firmware()
        elif args.action == "sim":
            simulate(args)
        elif args.action == "versions":
            versions()
        else:
            build()
            if args.action == "program":
                run([tool("iceprog"), "build/trade.bin"], "program.log")
    except (OSError, RuntimeError) as error:
        parser.exit(1, f"ERROR: {error}\n")


if __name__ == "__main__":
    main()
