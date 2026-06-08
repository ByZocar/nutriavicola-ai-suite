"""
Perfilado de calidad de datos.

Genera un reporte simple pero util para entender la salud de un dataset antes de
usarlo: cuantas filas, nulos por columna, duplicados y dominio de las columnas
categoricas. Sirve para sustentar decisiones y detectar problemas temprano.
"""

from __future__ import annotations

from typing import Any

import pandas as pd


def perfilar(df: pd.DataFrame, columnas_categoricas: list[str] | None = None) -> dict[str, Any]:
    """
    Construye un reporte de calidad del DataFrame.

    Devuelve un diccionario serializable a JSON con conteos de filas, nulos,
    duplicados y los valores unicos de las columnas categoricas indicadas.
    """
    reporte: dict[str, Any] = {
        "total_filas": int(len(df)),
        "total_columnas": int(df.shape[1]),
        "columnas": list(df.columns),
        "nulos_por_columna": {
            col: int(df[col].isna().sum()) for col in df.columns
        },
        "filas_duplicadas": int(df.duplicated().sum()),
    }

    # Dominio de las columnas categoricas: ayuda a validar entradas del agente
    if columnas_categoricas:
        dominios: dict[str, list[str]] = {}
        for col in columnas_categoricas:
            if col in df.columns:
                valores = sorted(v for v in df[col].dropna().unique())
                dominios[col] = [str(v) for v in valores]
        reporte["dominios_categoricos"] = dominios

    return reporte
