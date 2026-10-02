"""
Corrida de P00 con el MPC con compensación de retardo, campaña corta del 2026-10-01.

Reutiliza ejecutar_corrida.py. Solo añade el controlador
mpc_retardo a la lista de controladores que acepta. El resto del bucle, los
límites comunes, el perfil, el PI longitudinal y el registro son los mismos.

El controlador mpc_retardo usa los pesos del MPC congelados en base.json y
compensa RETARDO_CICLOS ciclos de 0.05 s.

Uso desde la raíz del repositorio, con Assetto Corsa abierto y el vehículo en pista.
    py -3.14 P00_control_lateral/ejecutar_corrida_retardo.py --controlador mpc_retardo --perfil conservador --sesion 1 --fase prueba --etiqueta retardo --id-plan r01
"""
import sys
from pathlib import Path

RAIZ_P00 = Path(__file__).resolve().parent
sys.path.insert(0, str(RAIZ_P00))

import ejecutar_corrida as ec  # noqa: E402
from controladores import crear_controlador as crear_original  # noqa: E402
from controladores.mpc_retardo import MPCRetardo  # noqa: E402

RETARDO_CICLOS = 4  # valor de la primera corrida, 2026-10-01
# --retardo-ciclos N cambia el valor. Se retira de sys.argv antes de ceder el
# control a ejecutar_corrida.py, y queda registrado en parametros_controlador.
if "--retardo-ciclos" in sys.argv:
    i = sys.argv.index("--retardo-ciclos")
    RETARDO_CICLOS = int(sys.argv[i + 1])
    del sys.argv[i:i + 2]


def crear_controlador(nombre, cfg):
    if nombre == MPCRetardo.nombre:
        parametros = dict(cfg["controladores"]["mpc_cinematico"])
        parametros["retardo_ciclos"] = RETARDO_CICLOS
        return MPCRetardo(parametros, ts_s=cfg["ts_s"],
                          delta_max_rad=cfg["direccion"]["delta_max_rad"],
                          tasa_max_rad_s=cfg["direccion"]["tasa_max_rad_s"])
    return crear_original(nombre, cfg)


ec.NOMBRES = tuple(ec.NOMBRES) + (MPCRetardo.nombre,)
ec.crear_controlador = crear_controlador

if __name__ == "__main__":
    ec.main()
