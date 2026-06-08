"""
CLI del Reto 2: filtra tickets criticos y genera el JSON de salida.

Une las piezas (ingesta -> limpieza -> filtrado -> exportacion) en un comando
ejecutable y maneja los errores con mensajes claros, como pide el reto.

Ejecucion:
    PYTHONPATH=src python -m nutria_ai.tickets.cli
    PYTHONPATH=src python -m nutria_ai.tickets.cli --entrada data/raw/Reto2.txt --salida salida.json
"""

from __future__ import annotations

import argparse
import logging
import sys

import pandas as pd

from nutria_ai import config
from nutria_ai.datos import ingesta, limpieza
from nutria_ai.tickets import exportador, filtrado

logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
log = logging.getLogger("reto2")


def ejecutar(ruta_entrada, ruta_salida) -> int:
    """
    Ejecuta el flujo completo del Reto 2 y devuelve un codigo de salida.

    Devuelve 0 si todo sale bien y 1 si ocurre un error controlado. Captura los
    fallos esperados (archivo no encontrado, vacio o con formato invalido) y los
    traduce a mensajes entendibles para quien corre el script.
    """
    try:
        crudo = ingesta.cargar_tickets(ruta_entrada)
    except FileNotFoundError as error:
        log.error("No se pudo abrir el archivo de tickets: %s", error)
        return 1
    except pd.errors.EmptyDataError:
        log.error("El archivo de tickets esta vacio o corrupto. Revisa su contenido.")
        return 1

    try:
        limpio = limpieza.limpiar_tickets(crudo)
        criticos = filtrado.filtrar_criticos(limpio)
    except filtrado.FormatoTicketsInvalido as error:
        log.error("%s", error)
        return 1

    payload = exportador.exportar_json(criticos, ruta_salida)
    log.info("Tickets leidos: %s", len(limpio))
    log.info("Tickets criticos (Pendiente + Alta): %s", payload["total_criticos"])
    log.info("JSON generado en: %s", ruta_salida)
    return 0


def main() -> None:
    """Punto de entrada: parsea argumentos y ejecuta el flujo."""
    parser = argparse.ArgumentParser(
        description="Filtra tickets criticos (Pendiente + Alta) y genera un JSON."
    )
    parser.add_argument(
        "--entrada", default=str(config.RUTA_TICKETS_RAW),
        help="Ruta del archivo de tickets de entrada (CSV/TXT separado por ';').",
    )
    parser.add_argument(
        "--salida", default=str(config.RUTA_TICKETS_CRITICOS),
        help="Ruta del archivo JSON de salida.",
    )
    args = parser.parse_args()
    sys.exit(ejecutar(args.entrada, args.salida))


if __name__ == "__main__":
    main()
