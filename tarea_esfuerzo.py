"""Simulador sencillo para tareas de *effort-based decision making*.

Genera pares de opciones con recompensas y esfuerzos diferentes, calcula la
probabilidad de elegir la alternativa de mayor recompensa/mayor esfuerzo y
simula la respuesta de un participante virtual. Pensado como punto de partida
para pilotos o análisis exploratorios de costo-beneficio.
"""
from __future__ import annotations

import argparse
import csv
import math
import random
import statistics
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


@dataclass(slots=True)
class Opcion:
    """Representa una alternativa en el ensayo."""

    recompensa: float
    esfuerzo: float


@dataclass(slots=True)
class Ensayo:
    """Resultado de un ensayo simulado."""

    opcion_baja: Opcion
    opcion_alta: Opcion
    elige_alta: bool
    probabilidad_alta: float
    recompensa_obtenida: float
    esfuerzo_asumido: float


@dataclass(slots=True)
class ConfiguracionSimulacion:
    ensayos: int = 60
    rango_recompensa_baja: tuple[float, float] = (1.0, 3.0)
    rango_recompensa_alta: tuple[float, float] = (5.0, 10.0)
    rango_esfuerzo_bajo: tuple[float, float] = (1.0, 3.0)
    rango_esfuerzo_alto: tuple[float, float] = (6.0, 10.0)
    peso_recompensa: float = 0.6
    peso_esfuerzo: float = 0.4
    sesgo: float = 0.0
    semilla: int | None = None
    archivo_csv: Path | None = Path("ensayos_esfuerzo.csv")

    def validar(self) -> None:
        if self.ensayos <= 0:
            raise ValueError("El número de ensayos debe ser positivo.")

        for etiqueta, rango in (
            ("recompensa baja", self.rango_recompensa_baja),
            ("recompensa alta", self.rango_recompensa_alta),
            ("esfuerzo bajo", self.rango_esfuerzo_bajo),
            ("esfuerzo alto", self.rango_esfuerzo_alto),
        ):
            if rango[0] <= 0 or rango[1] <= 0:
                raise ValueError(f"Los límites de {etiqueta} deben ser positivos.")
            if rango[0] >= rango[1]:
                raise ValueError(
                    f"El mínimo debe ser menor que el máximo en el rango de {etiqueta}."
                )

        if self.peso_recompensa < 0 or self.peso_esfuerzo < 0:
            raise ValueError("Los pesos deben ser no negativos.")


def _valor_uniforme(rng: random.Random, rango: tuple[float, float]) -> float:
    return rng.uniform(*rango)


def probabilidad_elegir_alta(opcion_baja: Opcion, opcion_alta: Opcion, cfg: ConfiguracionSimulacion) -> float:
    """Calcula la probabilidad de elegir la alternativa de mayor recompensa."""

    delta_recompensa = opcion_alta.recompensa - opcion_baja.recompensa
    delta_esfuerzo = opcion_alta.esfuerzo - opcion_baja.esfuerzo
    valor = cfg.peso_recompensa * delta_recompensa - cfg.peso_esfuerzo * delta_esfuerzo + cfg.sesgo

    # Función logística para mapear a probabilidad (0,1)
    try:
        return 1 / (1 + math.exp(-valor))
    except OverflowError:
        return 1.0 if valor > 0 else 0.0


def generar_ensayo(rng: random.Random, cfg: ConfiguracionSimulacion) -> Ensayo:
    opcion_baja = Opcion(
        recompensa=_valor_uniforme(rng, cfg.rango_recompensa_baja),
        esfuerzo=_valor_uniforme(rng, cfg.rango_esfuerzo_bajo),
    )
    opcion_alta = Opcion(
        recompensa=_valor_uniforme(rng, cfg.rango_recompensa_alta),
        esfuerzo=_valor_uniforme(rng, cfg.rango_esfuerzo_alto),
    )

    prob_alta = probabilidad_elegir_alta(opcion_baja, opcion_alta, cfg)
    elige_alta = rng.random() < prob_alta
    elegida = opcion_alta if elige_alta else opcion_baja

    return Ensayo(
        opcion_baja=opcion_baja,
        opcion_alta=opcion_alta,
        elige_alta=elige_alta,
        probabilidad_alta=prob_alta,
        recompensa_obtenida=elegida.recompensa,
        esfuerzo_asumido=elegida.esfuerzo,
    )


def simular(cfg: ConfiguracionSimulacion) -> list[Ensayo]:
    cfg.validar()
    rng = random.Random(cfg.semilla)
    return [generar_ensayo(rng, cfg) for _ in range(cfg.ensayos)]


def resumen(ensayos: Iterable[Ensayo]) -> dict[str, float]:
    lista = list(ensayos)
    if not lista:
        raise ValueError("No hay ensayos para resumir.")

    tasa_alta = sum(1 for e in lista if e.elige_alta) / len(lista)
    recompensas = [e.recompensa_obtenida for e in lista]
    esfuerzos = [e.esfuerzo_asumido for e in lista]

    return {
        "tasa_eleccion_alta": tasa_alta,
        "recompensa_media": statistics.mean(recompensas),
        "esfuerzo_medio": statistics.mean(esfuerzos),
        "mediana_esfuerzo": statistics.median(esfuerzos),
        "mediana_recompensa": statistics.median(recompensas),
    }


def _guardar_csv(ruta: Path, ensayos: Iterable[Ensayo]) -> None:
    ruta.parent.mkdir(parents=True, exist_ok=True)
    with ruta.open("w", newline="", encoding="utf-8") as archivo:
        writer = csv.writer(archivo)
        writer.writerow(
            [
                "recompensa_baja",
                "esfuerzo_bajo",
                "recompensa_alta",
                "esfuerzo_alto",
                "elige_alta",
                "probabilidad_alta",
                "recompensa_obtenida",
                "esfuerzo_asumido",
            ]
        )
        for e in ensayos:
            writer.writerow(
                [
                    f"{e.opcion_baja.recompensa:.3f}",
                    f"{e.opcion_baja.esfuerzo:.3f}",
                    f"{e.opcion_alta.recompensa:.3f}",
                    f"{e.opcion_alta.esfuerzo:.3f}",
                    int(e.elige_alta),
                    f"{e.probabilidad_alta:.3f}",
                    f"{e.recompensa_obtenida:.3f}",
                    f"{e.esfuerzo_asumido:.3f}",
                ]
            )


def _mostrar_resumen(resumen_calculado: dict[str, float]) -> str:
    return "\n".join(
        [
            "Resumen de la simulación:",
            f"- Tasa de elección alta: {resumen_calculado['tasa_eleccion_alta']:.3f}",
            f"- Recompensa media: {resumen_calculado['recompensa_media']:.3f}",
            f"- Recompensa mediana: {resumen_calculado['mediana_recompensa']:.3f}",
            f"- Esfuerzo medio: {resumen_calculado['esfuerzo_medio']:.3f}",
            f"- Esfuerzo mediano: {resumen_calculado['mediana_esfuerzo']:.3f}",
        ]
    )


def _parsear_rango(texto: str) -> tuple[float, float]:
    try:
        minimo, maximo = (float(valor) for valor in texto.split(","))
        return (minimo, maximo)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(
            "Formato de rango inválido. Usa minimo,maximo (p.ej., 1,5)."
        ) from exc


def _obtener_argumentos(argv: list[str] | None = None) -> ConfiguracionSimulacion:
    parser = argparse.ArgumentParser(
        description="Simula decisiones en una tarea effort-based con dos opciones por ensayo.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument("--ensayos", type=int, default=60, help="Número de ensayos a generar")
    parser.add_argument(
        "--recompensa-baja",
        type=_parsear_rango,
        default=_parsear_rango("1,3"),
        help="Rango (min,max) para la recompensa de la opción de bajo esfuerzo",
    )
    parser.add_argument(
        "--recompensa-alta",
        type=_parsear_rango,
        default=_parsear_rango("5,10"),
        help="Rango (min,max) para la recompensa de la opción de alto esfuerzo",
    )
    parser.add_argument(
        "--esfuerzo-bajo",
        type=_parsear_rango,
        default=_parsear_rango("1,3"),
        help="Rango (min,max) para el esfuerzo de la opción de bajo esfuerzo",
    )
    parser.add_argument(
        "--esfuerzo-alto",
        type=_parsear_rango,
        default=_parsear_rango("6,10"),
        help="Rango (min,max) para el esfuerzo de la opción de alto esfuerzo",
    )
    parser.add_argument(
        "--peso-recompensa",
        type=float,
        default=0.6,
        help="Sensibilidad a la diferencia de recompensa (coeficiente positivo)",
    )
    parser.add_argument(
        "--peso-esfuerzo",
        type=float,
        default=0.4,
        help="Sensibilidad al costo de esfuerzo (coeficiente positivo)",
    )
    parser.add_argument("--sesgo", type=float, default=0.0, help="Término independiente en la función logística")
    parser.add_argument("--semilla", type=int, default=None, help="Semilla para reproducibilidad")
    parser.add_argument(
        "--archivo-csv",
        type=Path,
        default=Path("ensayos_esfuerzo.csv"),
        help="Ruta del archivo CSV con los ensayos generados",
    )
    parser.add_argument(
        "--sin-archivo",
        action="store_true",
        help="No guardar resultados en disco, solo mostrar el resumen en pantalla",
    )

    args = parser.parse_args(argv)
    archivo_csv = None if args.sin_archivo else args.archivo_csv

    return ConfiguracionSimulacion(
        ensayos=args.ensayos,
        rango_recompensa_baja=args.recompensa_baja,
        rango_recompensa_alta=args.recompensa_alta,
        rango_esfuerzo_bajo=args.esfuerzo_bajo,
        rango_esfuerzo_alto=args.esfuerzo_alto,
        peso_recompensa=args.peso_recompensa,
        peso_esfuerzo=args.peso_esfuerzo,
        sesgo=args.sesgo,
        semilla=args.semilla,
        archivo_csv=archivo_csv,
    )


def main(argv: list[str] | None = None) -> None:
    cfg = _obtener_argumentos(argv)
    ensayos = simular(cfg)
    resumen_calculado = resumen(ensayos)
    print(_mostrar_resumen(resumen_calculado))

    if cfg.archivo_csv:
        _guardar_csv(cfg.archivo_csv, ensayos)
        print(f"\nEnsayos guardados en: {cfg.archivo_csv.resolve()}")


if __name__ == "__main__":
    main()
