# Componentes de terceros usados por Trial Steer v1.0.1

Trial Steer no incluye ni reivindica la autoría de los componentes de esta lista. Cada uno conserva su licencia y sus derechos.

## Programas externos, no incluidos

* Assetto Corsa, de Kunos Simulazioni. Es el entorno de simulación externo. Trial Steer no incluye ni reivindica propiedad sobre Assetto Corsa, sus vehículos, circuitos, recursos gráficos ni contenidos asociados. Solo lee la memoria compartida que el juego publica y le envía mandos a través de vJoy.
* Steam, de Valve. Plataforma de distribución del juego.
* vJoy. Controlador de Windows que crea el dispositivo de juego virtual.

## Datos derivados de Assetto Corsa

* `Model Predictive Control/Python/monza_fast_lane.csv`. Trazada de referencia de Monza. Se obtuvo del archivo `fast_lane.ai` de la pista Monza incluido en Assetto Corsa, convertido a CSV con una herramienta propia de los autores. La geometría de la pista proviene del juego y Trial Steer no reivindica su autoría. Solo se usa como referencia de trayectoria.

## Librerías de Python

Se instalan desde `requirements.txt`, y en el ejecutable van dentro de la carpeta `_internal`. Licencias verificadas en los metadatos de los paquetes instalados el 24 de septiembre de 2026.

* numpy, licencia BSD de 3 cláusulas, con componentes bajo licencias 0BSD, MIT, Zlib y CC0.
* scipy, licencia BSD.
* osqp, licencia Apache 2.0.
* pyvjoy, licencia MIT.
* matplotlib, licencia propia de matplotlib basada en la de la Python Software Foundation, solo para las gráficas.
* PyInstaller, licencia GPL 2 o posterior con una excepción que permite distribuir el ejecutable generado, solo para construir el ejecutable.
* Python y tkinter, licencia de la Python Software Foundation.

## Estructura de la memoria compartida de Assetto Corsa

`plataforma/memoria_ac.py` declara con ctypes los campos de la memoria compartida que publica Assetto Corsa. Los campos posteriores a `abs` de la página de física se declararon siguiendo el archivo `Physics.cs` de la librería mdjarv/assettocorsasharedmemory, https://github.com/mdjarv/assettocorsasharedmemory. No se copió código de esa librería, que está escrita en C#. Se tomaron el orden, los nombres y los tipos de los campos, que describen el formato de datos del juego. Esa librería se distribuye con la licencia MIT, cuyo aviso se reproduce a continuación como atribución.

```
MIT License

Copyright (c) 2016 Mathias Djärv

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
