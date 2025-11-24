"""
Herramienta sencilla para generar datos sintéticos y obtener un resumen estadístico.

Se puede reutilizar como módulo o ejecutar desde la línea de comandos. Ejemplo:
    python experimento.py --muestras 200 --media 10 --desviacion 2 --semilla 123
"""
from __future__ import annotations

import argparse
import json
import random
import statistics
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable


@dataclass(slots=True)
class Configuracion:
    """Parámetros de ejecución para el experimento."""

    muestras: int = 100
    media: float = 0.0
    desviacion: float = 1.0
    semilla: int | None = None
    archivo_salida: Path | None = Path("resultados.json")

    def validar(self) -> None:
        if self.muestras <= 0:
            raise ValueError("El número de muestras debe ser mayor que cero.")
        if self.desviacion <= 0:
            raise ValueError("La desviación estándar debe ser mayor que cero.")


def generar_muestras(cfg: Configuracion) -> list[float]:
    """Genera valores simulados con distribución normal."""

    cfg.validar()
    rng = random.Random(cfg.semilla)
    return [rng.gauss(cfg.media, cfg.desviacion) for _ in range(cfg.muestras)]


def resumen_estadistico(valores: Iterable[float]) -> dict[str, float | None]:
    """Calcula medidas descriptivas básicas."""

    datos = list(valores)
    if not datos:
        raise ValueError("No hay datos para analizar.")

    estadisticas: dict[str, float | None] = {
        "minimo": min(datos),
        "maximo": max(datos),
        "media": statistics.mean(datos),
        "mediana": statistics.median(datos),
    }

    if len(datos) > 1:
        estadisticas["desviacion"] = statistics.stdev(datos)
        estadisticas["varianza"] = statistics.variance(datos)
    else:
        estadisticas["desviacion"] = None
        estadisticas["varianza"] = None

    return estadisticas


def guardar_resultados(ruta: Path, cfg: Configuracion, resumen: dict[str, float | None], muestras: list[float]) -> None:
    """Guarda los parámetros de entrada y resultados en un archivo JSON."""

    contenido = {
        "creado_en": datetime.now().isoformat(timespec="seconds"),
        "configuracion": asdict(cfg),
        "resumen": resumen,
        "muestras": muestras[:20],  # incluir una muestra representativa
    }
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text(json.dumps(contenido, indent=2, ensure_ascii=False), encoding="utf-8")


def formatear_resumen(resumen: dict[str, float | None]) -> str:
    lineas = ["Resumen estadístico:"]
    for clave, valor in resumen.items():
        if valor is None:
            lineas.append(f"- {clave}: n/d (se requieren más muestras)")
        else:
            lineas.append(f"- {clave}: {valor:.4f}")
    return "\n".join(lineas)


def obtener_argumentos(argv: list[str] | None = None) -> Configuracion:
    parser = argparse.ArgumentParser(description="Genera datos sintéticos y calcula estadísticas básicas.")
    parser.add_argument("--muestras", type=int, default=100, help="Número de valores a generar (por defecto 100)")
    parser.add_argument("--media", type=float, default=0.0, help="Media de la distribución normal")
    parser.add_argument("--desviacion", type=float, default=1.0, help="Desviación estándar de la distribución")
    parser.add_argument("--semilla", type=int, default=None, help="Semilla opcional para reproducibilidad")
    parser.add_argument(
        "--archivo-salida",
        type=Path,
        default=Path("resultados.json"),
        help="Ruta donde se guardarán los resultados (JSON)",
    )
    parser.add_argument(
        "--sin-archivo",
        action="store_true",
        help="Si se establece, no se generará un archivo de salida",
    )

    args = parser.parse_args(argv)
    archivo_salida = None if args.sin_archivo else args.archivo_salida
    return Configuracion(
        muestras=args.muestras,
        media=args.media,
        desviacion=args.desviacion,
        semilla=args.semilla,
        archivo_salida=archivo_salida,
    )


def main(argv: list[str] | None = None) -> None:
    cfg = obtener_argumentos(argv)
    muestras = generar_muestras(cfg)
    resumen = resumen_estadistico(muestras)
    print(formatear_resumen(resumen))

    if cfg.archivo_salida:
        guardar_resultados(cfg.archivo_salida, cfg, resumen, muestras)
        print(f"\nResultados guardados en: {cfg.archivo_salida.resolve()}")


if __name__ == "__main__":
    main()
