# Lateral control experiments in Assetto Corsa

Simulation and analysis code for the article "Evaluation of geometric and predictive lateral controllers in high-fidelity simulation", submitted to TecnoLógicas.

Juan Camilo Díaz López, Jesús Alberto Lastra Robles and Francisco Javier Burgos Flórez
Programa de Ingeniería Mecatrónica, Universidad Nacional de Colombia, Sede La Paz

The code runs three lateral controllers, Pure Pursuit, Stanley and a Model Predictive Controller (MPC) with a kinematic bicycle model, against Assetto Corsa as the vehicle plant. The three share the reference path, the speed profile, the longitudinal PI controller and the actuation limits, so that only the lateral controller changes between runs. The repository contains the code and the configuration that executed the runs of the study and the analysis that computes the metrics and the statistical contrasts from the run records. It does not contain the run records, the reference path, nor any code that draws figures or writes tables.

## Software to install

1. **Windows 10 or 11.** The platform reads the shared memory of the game and writes to a virtual joystick, both Windows only.
2. **Assetto Corsa 1.16.4**, from Steam, with the Monza circuit and the Alfa Romeo Giulietta QV. The game publishes the vehicle state in shared memory, including the extended physics page from which the platform measures the axles through the wheel contact points.
3. **vJoy**, the virtual joystick driver, with device 1 enabled. The lateral and longitudinal commands reach the game through its axes, steering on X, throttle on Y and brake on the sixth axis.
4. **Python 3.14** with the packages of `requirements.txt`, installed with `pip install -r requirements.txt`. These are numpy, scipy, osqp and pyvjoy.
5. **TrialSteer 1.0.1**, optional, https://github.com/JCamiloD06/TrialSteer. It packages this same platform as a Windows program with a graphical launcher that opens the game, prepares each session and starts the runs of a plan. The runs of the study were launched with it. It is not needed to run the scripts of this repository, which do the same from the command line.

Assetto Corsa, Steam and vJoy are external programs and are not included. See `P00_control_lateral/TERCEROS.md` for the third party components.

## Setup

1. **Game settings.** Copy the four files of `P00_control_lateral/configs/sesion_ac`, `race.ini`, `assists.ini`, `controls.ini` and `video.ini`, to `Documents\Assetto Corsa\cfg`, after making a backup of that folder. They fix the session conditions of the study and assign the vJoy device as the steering, throttle and brake input. `correr_plan_retardo.py` copies them automatically before every lap and keeps a backup.
2. **Game folder.** If Assetto Corsa is not installed in `C:\Program Files (x86)\Steam\steamapps\common\assettocorsa`, change `ruta_ac` in `P00_control_lateral/configs/juego_ac.json`.
3. **Reference path.** The reference path is not included, since the track geometry belongs to Assetto Corsa. It was obtained by processing the file `fast_lane.ai` of the Monza track supplied with the game. Place the converted file at `Model Predictive Control/Python/monza_fast_lane.csv`, with the columns `index`, `x`, `y_elevation`, `z` and `cumulative_length_m`, in meters and in the coordinates of the simulator. Every run records the SHA256 hash of this file in its manifest and compares it with the hash of the file used in the study, `90c6e5a1955e320c0d00f49b490f1adc3abb0af3ac70144f7e7478f750670915`.

## Contents

| Path | Content |
|---|---|
| `P00_control_lateral/ejecutar_corrida.py` | Runs one lap with a lateral controller and a speed profile, and writes its record |
| `P00_control_lateral/ejecutar_corrida_retardo.py`, `correr_plan_retardo.py` | Runs of the post hoc delay compensation with the MPC of `controladores/mpc_retardo.py` |
| `P00_control_lateral/controladores` | Pure Pursuit, Stanley, the kinematic MPC and the MPC with delay compensation |
| `P00_control_lateral/plataforma` | Shared memory reader, reference path and projection, speed profile, longitudinal PI, common steering interface, vJoy output, lap tracking, game preparation and run recorder |
| `P00_control_lateral/analisis` | Metrics per lap and region, tuning selection, repeatability and thresholds, and campaign contrasts |
| `P00_control_lateral/configs/base.json` | Configuration frozen before the campaign, with the parameters of the three controllers, the PI, the planner, the actuation limits and the decision rule |
| `P00_control_lateral/configs/sintonia`, `piloto` | One configuration per tuning run and per pilot run |
| `P00_control_lateral/configs/plan_*.json`, `plan_retardo*.csv`, `rangos_sintonia.json`, `parametros_piloto.json` | Run plans of the study as they were executed, with the ranges and parameters they were built from |
| `P00_control_lateral/configs/sesion_ac`, `juego_ac.json` | Game settings used in every session |

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
| Post hoc delay compensation | 24, 10 with d = 4, 10 with d = 1 and 4 control laps of the original MPC | `configs/plan_retardo.csv` and `configs/plan_retardo_1ciclo.csv` with `base.json` |

The campaign order was drawn once with seed 20260915 before the campaign and stored in `configs/plan_campana.json`. Each session runs its nine combinations in the stored order, and each entry gives the controller, the profile, the session and the plan identifier for the command above.

The delay compensation runs use `controladores/mpc_retardo.py`, the same MPC with its error state projected d control cycles ahead before each optimization. `ejecutar_corrida_retardo.py` runs one lap with it and accepts `--retardo-ciclos`, and `correr_plan_retardo.py` prepares the game and runs the laps of a plan in order, for example

```
python P00_control_lateral/correr_plan_retardo.py --plan P00_control_lateral/configs/plan_retardo_1ciclo.csv
```

## Analysis

The analysis reads the run folders in `data/raw/p00/corridas` and writes its results as JSON and CSV data files. The run records of the study are available from the corresponding author on reasonable request. Run the scripts from the root of this repository in this order.

1. Coverage of the curvature regions over the racing line, written to `results/p00/auditoria`.

   ```
   python P00_control_lateral/analisis/regiones_curvatura.py
   ```

2. Tuning selection, with the discard criteria and the tie rule of `configs/rangos_sintonia.json`, written to `P00_control_lateral/sintonia_fase4/seleccion_sintonia.json`.

   ```
   python P00_control_lateral/analisis/seleccion_sintonia.py
   ```

3. Repeatability of the pilot laps, its confidence interval and the practical improvement threshold of each comparison, written to `P00_control_lateral/piloto_fase5/repetibilidad_piloto.json`.

   ```
   python P00_control_lateral/analisis/repetibilidad_piloto.py
   ```

4. Campaign map, with the lateral error and the steering activity per cell, the Friedman test, the paired Wilcoxon tests with the Holm correction, the bootstrap intervals over sessions and the verdict of each comparison, written to `P00_control_lateral/resultados_campana/mapa_campana.json`.

   ```
   python P00_control_lateral/analisis/mapa_campana.py
   ```

The metrics of each lap, lateral error by curvature region at the vehicle position and at the rear axle, heading and speed errors, steering rate, saturations and computation time, are computed by `analisis/metricas_vuelta.py`. The campaign map calls it for every run and stores the result as `metricas.json` inside the run folder. It can also be run on a single run.

```
python P00_control_lateral/analisis/metricas_vuelta.py data/raw/p00/corridas/<run folder>
```

## Notes

* Most identifiers and comments are in Spanish, the working language of the authors.
* The output folders of the analysis are listed in `.gitignore`, so that results are never mixed with the code.
