"""
Pipeline de la capa de datos.

Orquesta ingesta, limpieza, perfilado y generacion del dataset sintetico, y deja
los artefactos listos en data/processed. Es el punto de entrada de la Fase 2.

Ejecucion:
    python -m nutria_ai.datos.pipeline
"""

from __future__ import annotations

import json
import logging

from nutria_ai import config
from nutria_ai.datos import ingesta, limpieza, perfilado, sintetico

logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
log = logging.getLogger("pipeline_datos")


def _guardar_json(ruta, contenido: dict) -> None:
    """Guarda un diccionario como JSON legible (UTF-8, con indentacion)."""
    ruta.parent.mkdir(parents=True, exist_ok=True)
    with open(ruta, "w", encoding="utf-8") as archivo:
        json.dump(contenido, archivo, ensure_ascii=False, indent=2, default=str)


def procesar_tickets() -> None:
    """Lee, limpia y perfila los tickets; guarda el CSV limpio y su perfil."""
    log.info("Procesando tickets desde %s", config.RUTA_TICKETS_RAW)
    crudo = ingesta.cargar_tickets()
    limpio = limpieza.limpiar_tickets(crudo)

    config.DIR_PROCESADOS.mkdir(parents=True, exist_ok=True)
    limpio.to_csv(config.RUTA_TICKETS_LIMPIOS, index=False, encoding="utf-8")

    perfil = perfilado.perfilar(
        limpio,
        columnas_categoricas=["Estado", "Prioridad", "Tipo_Incidencia", "Nivel_Soporte"],
    )
    _guardar_json(config.RUTA_PERFIL_TICKETS, perfil)
    log.info("Tickets limpios: %s filas -> %s", len(limpio), config.RUTA_TICKETS_LIMPIOS)


def procesar_empleados() -> None:
    """Genera el dataset sintetico de empleados y su perfil de calidad."""
    log.info("Generando dataset sintetico de empleados (sin PII real)")
    empleados = sintetico.generar_empleados_sinteticos()

    config.DIR_PROCESADOS.mkdir(parents=True, exist_ok=True)
    empleados.to_csv(config.RUTA_EMPLEADOS_SINTETICO, index=False, encoding="utf-8")

    perfil = perfilado.perfilar(
        empleados,
        columnas_categoricas=["Area", "Estado", "Tipo_Contrato"],
    )
    _guardar_json(config.RUTA_PERFIL_EMPLEADOS, perfil)
    log.info("Empleados sinteticos: %s filas -> %s", len(empleados), config.RUTA_EMPLEADOS_SINTETICO)


def main() -> None:
    """Ejecuta el pipeline completo de la capa de datos."""
    procesar_tickets()
    procesar_empleados()
    log.info("Pipeline de datos completado.")


if __name__ == "__main__":
    main()
