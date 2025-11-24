# Tesis

Script con los que trabajaré mi experimento.

## `tarea_esfuerzo.py`
Simulador de decisiones costo-beneficio en paradigmas *effort-based decision making*. Genera ensayos con una opción de baja
recompensa/bajo esfuerzo y otra de alta recompensa/alto esfuerzo, calcula la probabilidad de elegir la alternativa exigente y
produce un resumen agregado. Útil para planificar pilotos, validar parámetros o generar conjuntos de prueba.

### Ejecución básica
```bash
python tarea_esfuerzo.py --ensayos 40 --semilla 7
```

### Parámetros principales
- `--ensayos`: número de ensayos a simular.
- `--recompensa-baja` / `--recompensa-alta`: rangos en formato `min,max` para las recompensas de cada opción.
- `--esfuerzo-bajo` / `--esfuerzo-alto`: rangos en formato `min,max` para los esfuerzos de cada opción.
- `--peso-recompensa` y `--peso-esfuerzo`: pesos positivos en la función logística que controla la probabilidad de elegir la opción exigente
  (mayor peso de recompensa aumenta la elección de la opción alta, mayor peso de esfuerzo la reduce).
- `--sesgo`: término independiente para ajustar la propensión general a elegir el esfuerzo alto.
- `--semilla`: semilla opcional para reproducibilidad.
- `--archivo-csv`: ruta del archivo que almacenará los ensayos simulados (se omite con `--sin-archivo`).

### Ejemplo de salida en consola
```
Resumen de la simulación:
- Tasa de elección alta: 0.575
- Recompensa media: 6.592
- Recompensa mediana: 6.318
- Esfuerzo medio: 5.123
- Esfuerzo mediano: 5.110

Ensayos guardados en: /ruta/completa/ensayos_esfuerzo.csv
```

### Ejecución orientada a prototipos
Puedes ajustar la sensibilidad al esfuerzo para ver cómo cambia la tasa de elección alta:
```bash
python tarea_esfuerzo.py --ensayos 80 --peso-esfuerzo 0.8 --peso-recompensa 0.5 --semilla 21
```

## `experimento.py`
Herramienta sencilla para generar datos sintéticos con distribución normal y obtener un resumen estadístico. Puede ejecutarse desde la
línea de comandos o importarse como módulo.

### Ejecución básica
```bash
python experimento.py --muestras 200 --media 10 --desviacion 2 --semilla 123
```

### Opciones disponibles
- `--muestras`: número de valores a generar (por defecto 100).
- `--media`: media de la distribución normal.
- `--desviacion`: desviación estándar de la distribución.
- `--semilla`: semilla opcional para reproducibilidad.
- `--archivo-salida`: ruta donde se guardarán los resultados en formato JSON (por defecto `resultados.json`).
- `--sin-archivo`: evita crear un archivo de salida y solo muestra el resumen en pantalla.

### Ejemplo de salida
```
Resumen estadístico:
- minimo: 1.4135
- maximo: 1.8510
- media: 1.5146
- mediana: 1.4362
- desviacion: 0.1884
- varianza: 0.0355
```

### Uso como módulo
```python
from experimento import Configuracion, generar_muestras, resumen_estadistico

cfg = Configuracion(muestras=50, media=0.0, desviacion=1.0, semilla=42)
datos = generar_muestras(cfg)
print(resumen_estadistico(datos))
```
