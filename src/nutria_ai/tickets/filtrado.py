"""
Reto 2: filtrado de tickets criticos.

Lee el archivo de tickets, filtra los que estan 'Pendiente' con prioridad 'Alta'
y deja el resultado listo para serializar a JSON. La logica de negocio (que es un
ticket critico) vive aqui, separada de la lectura y de la escritura del archivo.
"""

from __future__ import annotations

import pandas as pd

from nutria_ai import config

# Columnas obligatorias para poder aplicar el criterio de filtrado
COLUMNAS_REQUERIDAS = {"Estado", "Prioridad"}


class FormatoTicketsInvalido(Exception):
    """Se lanza cuando el archivo de tickets no tiene la estructura esperada."""


def validar_columnas(df: pd.DataFrame) -> None:
    """
    Verifica que existan las columnas necesarias para filtrar.

    Lanza FormatoTicketsInvalido con un mensaje claro si falta alguna, en vez de
    dejar que el filtrado falle con un error tecnico dificil de entender.
    """
    faltantes = COLUMNAS_REQUERIDAS - set(df.columns)
    if faltantes:
        raise FormatoTicketsInvalido(
            f"El archivo de tickets no tiene las columnas requeridas: {sorted(faltantes)}. "
            "Revisa que el separador sea ';' y que la cabecera este completa."
        )


def filtrar_criticos(df: pd.DataFrame) -> pd.DataFrame:
    """
    Devuelve solo los tickets con Estado 'Pendiente' y Prioridad 'Alta'.

    La comparacion ignora mayusculas/minusculas y espacios para ser tolerante con
    pequenas variaciones de captura en el sistema de origen.
    """
    validar_columnas(df)

    estado = df["Estado"].astype(str).str.strip().str.casefold()
    prioridad = df["Prioridad"].astype(str).str.strip().str.casefold()

    criterio = (estado == config.ESTADO_CRITICO.casefold()) & (
        prioridad == config.PRIORIDAD_CRITICA.casefold()
    )
    return df[criterio].copy()
