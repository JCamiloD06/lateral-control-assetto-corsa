# Lateral control experiments in Assetto Corsa

Simulation and experiment code for the article "Evaluation of geometric and predictive lateral controllers in high-fidelity simulation", submitted to TecnoLógicas.

Juan Camilo Díaz López, Jesús Alberto Lastra Robles and Francisco Javier Burgos Flórez
Programa de Ingeniería Mecatrónica, Universidad Nacional de Colombia, Sede La Paz

The code runs three lateral controllers, Pure Pursuit, Stanley and a Model Predictive Controller (MPC) with a kinematic bicycle model, against Assetto Corsa as the vehicle plant. The three share the reference path, the speed profile, the longitudinal PI controller and the actuation limits, so that only the lateral controller changes between runs. This repository contains the code and the configuration that executed the runs of the study. It does not contain the run records nor the analysis that produced the results of the article.

The same platform is distributed as the software TrialSteer, https://github.com/JCamiloD06/TrialSteer.

## Requirements

* Windows with Assetto Corsa 1.16.4, the Monza circuit and the Alfa Romeo Giulietta QV.
* vJoy, the virtual joystick driver, with one device configured as the steering, throttle and brake input of the game.
* Python 3.14 with the packages of `requirements.txt`.

## Contents

| Path | Content |
|---|---|
| `P00_control_lateral/ejecutar_corrida.py` | Runs one lap with a lateral controller and a speed profile, and writes its record |
| `P00_control_lateral/controladores` | Pure Pursuit, Stanley and the kinematic MPC |
| `P00_control_lateral/plataforma` | Shared memory reader, reference path and projection, speed profile, longitudinal PI, common steering interface, vJoy output, lap tracking and run recorder |
| `P00_control_lateral/lanzador` | Generators of the tuning, pilot and campaign plans, with fixed seeds |
| `P00_control_lateral/configs/base.json` | Configuration frozen before the campaign, with the parameters of the three controllers, the PI, the planner and the actuation limits |
| `P00_control_lateral/configs/sintonia`, `piloto` | One configuration per tuning run and per pilot run |
| `P00_control_lateral/configs/plan_*.json`, `rangos_sintonia.json`, `parametros_piloto.json` | Run plans of the study as they were executed, and the rules used to generate them |
| `P00_control_lateral/configs/sesion_ac`, `juego_ac.json` | Game settings used in every session |

## Reference path

The reference path is not included, since the track geometry belongs to Assetto Corsa. It was obtained by processing the file `fast_lane.ai` of the Monza track supplied with the game. Place the converted file at

`Model Predictive Control/Python/monza_fast_lane.csv`

with the columns `index`, `x`, `y_elevation`, `z` and `cumulative_length_m`, in meters and in the coordinates of the simulator. Every run records the SHA256 hash of this file in its manifest and compares it with the hash of the file used in the study, `90c6e5a1955e320c0d00f49b490f1adc3abb0af3ac70144f7e7478f750670915`.

## Running a lap

Open Assetto Corsa with the vehicle on track and run from the root of this repository

```
python P00_control_lateral/ejecutar_corrida.py --controlador stanley --perfil conservador --sesion 0 --fase prueba
```

* `--controlador` is `pure_pursuit`, `stanley` or `mpc_cinematico`.
* `--perfil` is `conservador`, `nominal` or `rapido`, the speed profile factors 0.8, 0.9 and 1.0 of the article.
* `--fase` labels the run as `verificacion`, `sintonia`, `piloto`, `campana` or `prueba`.
* `--config` selects a configuration other than `base.json`, as in the tuning and pilot runs.
* `--id-plan` links the run to its entry in a plan, and is required in the campaign.
* `--tiempo-max-s` stops a run that exceeds an optional time limit. The limit of 420 s per run used in the study is already set in `base.json`.

The run ends when the measured lap is completed and writes a folder in `data/raw/p00/corridas` with the telemetry of every 0.05 s cycle, a manifest with the configuration and its hashes, and the target speed profile.

## Experimental runs of the study

| Stage | Runs | Plan or configuration |
|---|---|---|
| Platform verification | 9 | `base.json`, phase `verificacion` |
| Tuning | 60, 20 per controller on the nominal profile | `configs/plan_sintonia.json` and `configs/sintonia` |
| Pilot | 36 | `configs/plan_piloto.json` and `configs/piloto` |
| Campaign | 90, 3 controllers by 3 profiles by 10 sessions | `configs/plan_campana.json` with `base.json` |

The campaign order was generated once with seed 20260915 by `lanzador/plan.py` and stored in `configs/plan_campana.json`. Each session runs its nine combinations in the stored order, and each entry gives the controller, the profile, the session and the plan identifier for the command above.

## Notes

* Most identifiers and comments are in Spanish, the working language of the authors.
* Assetto Corsa, Steam and vJoy are external programs and are not included. See `P00_control_lateral/TERCEROS.md` for third party components.
