"""
Ingesta de datos crudos.

Lee las dos fuentes del proyecto (empleados en Excel y tickets en texto) y las
devuelve como DataFrames sin transformar. La limpieza vive en otro modulo para
separar responsabilidades: aqui solo leemos y validamos que el archivo exista.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from nutria_ai import config


def cargar_empleados(ruta: Path | str | None = None) -> pd.DataFrame:
    """
    Lee el Excel de empleados y devuelve un DataFrame crudo.

    Lanza FileNotFoundError con mensaje claro si el archivo no existe, para que
    el usuario sepa que debe ubicar la fuente en data/raw/.
    """
    ruta = Path(ruta) if ruta else config.RUTA_EMPLEADOS_RAW
    if not ruta.exists():
        raise FileNotFoundError(
            f"No se encontro el archivo de empleados en: {ruta}. "
            "Ubicalo en data/raw/ o ajusta RUTA_EMPLEADOS_RAW en el .env."
        )
    # openpyxl es el motor para .xlsx; pandas convierte las fechas serial de Excel
    return pd.read_excel(ruta, engine="openpyxl")


def cargar_tickets(ruta: Path | str | None = None) -> pd.DataFrame:
    """
    Lee el archivo de tickets (CSV separado por punto y coma) y lo devuelve crudo.

    Maneja el encoding de forma tolerante (utf-8 con respaldo latin-1) porque los
    nombres en espanol traen tildes que pueden venir en distintas codificaciones.
    """
    ruta = Path(ruta) if ruta else config.RUTA_TICKETS_RAW
    if not ruta.exists():
        raise FileNotFoundError(
            f"No se encontro el archivo de tickets en: {ruta}. "
            "Ubicalo en data/raw/ o ajusta RUTA_TICKETS_RAW en el .env."
        )
    try:
        return pd.read_csv(ruta, sep=config.SEPARADOR_TICKETS, encoding="utf-8")
    except UnicodeDecodeError:
        # Respaldo para archivos guardados en latin-1 (comun en exportes de Windows)
        return pd.read_csv(ruta, sep=config.SEPARADOR_TICKETS, encoding="latin-1")
