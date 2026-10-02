"""
Corre la campaña corta de compensación de retardo siguiendo configs/plan_retardo.csv.

Repite para cada vuelta el procedimiento del lanzador en la campaña. Cierra y
reabre Assetto Corsa con la plantilla de configs/sesion_ac, deja el carro en la
salida con vJoy en control, guarda la preparación en data/raw/p00/preparaciones_ac
y lanza ejecutar_corrida_retardo.py con esa preparación. Después comprueba en
el manifiesto que la vuelta se completó.

Se puede detener con Ctrl+C y volver a lanzar. Salta las vueltas del plan que ya
tienen una corrida completada con la misma id_plan y la etiqueta retardo, y una
vuelta incompleta se vuelve a correr la próxima vez.

Uso desde la raíz del repositorio, con vJoy instalado y el juego cerrado o abierto.
    py -3.14 P00_control_lateral/correr_plan_retardo.py              corre lo pendiente
    py -3.14 P00_control_lateral/correr_plan_retardo.py --solo-ver   lista lo pendiente sin tocar el juego
"""
import argparse
import csv
import json
import os
import subprocess
import sys
import time
from pathlib import Path

RAIZ_P00 = Path(__file__).resolve().parent
sys.path.insert(0, str(RAIZ_P00))

from plataforma import procedencia  # noqa: E402

PLAN = RAIZ_P00 / "configs" / "plan_retardo.csv"
EJECUTOR = RAIZ_P00 / "ejecutar_corrida_retardo.py"
CORRIDAS = procedencia.RAIZ_REPO / "data" / "raw" / "p00" / "corridas"
ETIQUETA = "retardo"
# Con --plan se usa otro CSV. Si el CSV trae las columnas etiqueta y
# retardo_ciclos, cada vuelta usa esos valores, como en plan_retardo_1ciclo.csv.


def leer_plan(ruta=None):
    with open(ruta or PLAN, encoding="utf-8-sig", newline="") as f:
        return sorted(csv.DictReader(f), key=lambda r: int(r["orden"]))


def completadas(etiqueta=ETIQUETA):
    hechas = set()
    for carpeta in CORRIDAS.glob("prueba_*"):
        ruta = carpeta / "manifiesto.json"
        if not ruta.exists():
            continue
        man = json.load(open(ruta, encoding="utf-8"))
        meta = man.get("meta", {})
        if meta.get("etiqueta") == etiqueta and man.get("resumen", {}).get("vuelta_completada"):
            hechas.add(meta.get("id_plan"))
    return hechas


def preparar_juego():
    from plataforma import juego_ac
    registro = []

    def log(t):
        linea = f"{time.strftime('%H:%M:%S')} {t}"
        registro.append(linea)
        print("   [juego]", t, flush=True)

    cfg = juego_ac.cargar_config()
    carpeta = procedencia.RAIZ_REPO / cfg["directorio_preparaciones"]
    carpeta.mkdir(parents=True, exist_ok=True)
    ruta = carpeta / f"preparacion_{time.strftime('%Y%m%d_%H%M%S')}.json"
    error = None
    try:
        info = juego_ac.preparar(cfg, reiniciar=True, log=log)
    except Exception as e:  # se guarda igual, como hace el lanzador
        info = getattr(e, "info", {})
        info["error"] = error = f"{type(e).__name__}: {e}"
    info["destino"] = "plan_retardo"
    info["registro"] = registro
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(info, f, ensure_ascii=False, indent=1, default=str)
    return ruta, error


def correr(fila, ruta_preparacion):
    args = [sys.executable, str(EJECUTOR), "--controlador", fila["controlador"], "--perfil", fila["perfil"],
            "--sesion", str(int(fila["sesion"])), "--fase", "prueba", "--etiqueta", fila.get("etiqueta") or ETIQUETA,
            "--id-plan", fila["id_plan"], "--info-sesion-ac", str(ruta_preparacion)]
    if fila.get("retardo_ciclos"):
        args += ["--retardo-ciclos", str(int(fila["retardo_ciclos"]))]
    print("   $", " ".join(args[1:]), flush=True)
    entorno = dict(os.environ, PYTHONIOENCODING="utf-8")
    return subprocess.run(args, cwd=str(procedencia.RAIZ_REPO), env=entorno).returncode


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--solo-ver", action="store_true", help="lista las vueltas pendientes sin tocar el juego")
    ap.add_argument("--plan", default=str(PLAN), help="CSV del plan, por defecto configs/plan_retardo.csv")
    args = ap.parse_args()
    plan = leer_plan(args.plan)
    etiqueta = plan[0].get("etiqueta") or ETIQUETA
    hechas = completadas(etiqueta)
    pendientes = [f for f in plan if f["id_plan"] not in hechas]
    print(f"Plan de {len(plan)} vueltas, completadas {len(plan) - len(pendientes)}, pendientes {len(pendientes)}")
    for f in pendientes:
        print(f"   {f['orden']:>2} {f['id_plan']} sesión {f['sesion']} {f['controlador']:14s} {f['perfil']}")
    if args.solo_ver or not pendientes:
        return 0
    for f in pendientes:
        print("\n" + "=" * 70)
        print(f"Vuelta {f['orden']} de {len(plan)}, {f['id_plan']}, {f['controlador']} {f['perfil']}, sesión {f['sesion']}")
        print("=" * 70, flush=True)
        ruta, error = preparar_juego()
        if error:
            print(f"La preparación del juego falló, {error}. Revisa el juego y vuelve a lanzar el script.")
            return 1
        codigo = correr(f, ruta)
        if f["id_plan"] not in completadas(etiqueta):
            print(f"La vuelta {f['id_plan']} no quedó completada (código {codigo}). "
                  "Revisa la salida y vuelve a lanzar el script, la repetirá.")
            return 1
        print(f"Vuelta {f['id_plan']} completada.", flush=True)
    print("\nPlan terminado.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
