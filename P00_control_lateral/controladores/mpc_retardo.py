"""
MPC cinemático con compensación del retardo de actuación.

Mismo controlador que MPCCinematico, con los mismos pesos, horizonte y límites.
La única diferencia es el estado desde el que optimiza. El retardo efectivo
medido entre el comando y la respuesta del vehículo es de unos 0.20 s, es decir
4 ciclos de 0.05 s. Durante ese tiempo actúan comandos que ya se enviaron y que
el controlador conoce. Antes de optimizar, el estado de errores del eje trasero
se proyecta hacia adelante esos ciclos con el mismo modelo lineal del MPC,

    e_y   <- e_y + Ts v e_psi
    e_psi <- e_psi + Ts v (delta / L - kappa)

aplicando en orden los últimos comandos ya aplicados, y la posición sobre la
trazada se adelanta la distancia v Ts por ciclo. El QP se resuelve desde ese
estado proyectado, de modo que el primer ángulo de la secuencia es el que
actuará cuando el comando llegue al vehículo. La velocidad se mantiene
constante en la proyección, igual que en el horizonte del MPC.
"""
from collections import deque
from dataclasses import replace

from controladores.mpc_cinematico import MPCCinematico


class MPCRetardo(MPCCinematico):
    nombre = "mpc_retardo"

    def __init__(self, parametros, ts_s, delta_max_rad, tasa_max_rad_s):
        super().__init__(parametros, ts_s, delta_max_rad, tasa_max_rad_s)
        self.retardo_ciclos = int(self.parametros.get("retardo_ciclos", 4))
        if self.retardo_ciclos < 0:
            raise ValueError("retardo_ciclos no puede ser negativo")
        self.aplicados = deque(maxlen=max(self.retardo_ciclos, 1))
        self.ultimo_estado_proyectado = None

    def reiniciar(self):
        super().reiniciar()
        self.aplicados.clear()
        self.ultimo_estado_proyectado = None

    def proyectar(self, e):
        """Entrada con los errores del eje trasero adelantados retardo_ciclos ciclos."""
        d = self.retardo_ciclos
        # delta_prev es el último ángulo aplicado por la interfaz común.
        self.aplicados.append(float(e.delta_prev))
        if d == 0:
            return e
        historia = list(self.aplicados)
        if len(historia) < d:
            historia = [historia[0]] * (d - len(historia)) + historia
        v = max(e.v_ms, 0.0)
        ts, L = self.ts, e.L
        e_y, e_psi, avance = e.e_y_tras, e.e_psi_tras, 0.0
        for delta in historia[-d:]:
            kappa = e.trazada.curvatura_adelante(e.idx_tras, avance)
            e_y = e_y + ts * v * e_psi
            e_psi = e_psi + ts * v * (delta / L - kappa)
            avance += v * ts
        idx = e.trazada.indice_adelante(e.idx_tras, avance)
        self.ultimo_estado_proyectado = (e_y, e_psi, avance)
        return replace(e, e_y_tras=e_y, e_psi_tras=e_psi, idx_tras=idx)

    def calcular(self, e):
        return super().calcular(self.proyectar(e))
