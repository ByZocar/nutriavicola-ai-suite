"""
Limpieza y normalizacion de datos.

Convierte los datos crudos en datos confiables: normaliza salarios que vienen como
texto, parsea fechas, estandariza espacios y deja explicitos los campos vacios.
Cada funcion devuelve una copia para no mutar el DataFrame original.
"""

from __future__ import annotations

import re

import pandas as pd


def _normalizar_texto(serie: pd.Series) -> pd.Series:
    """Quita espacios sobrantes y unifica vacios a cadena vacia."""
    return serie.fillna("").astype(str).str.strip()


def normalizar_salario(valor: str | float | int) -> float | None:
    """
    Convierte un salario en texto tipo "$ 3.500.000" a numero (3500000.0).

    Devuelve None si el valor no es interpretable, para no inventar datos.
    """
    if pd.isna(valor):
        return None
    if isinstance(valor, (int, float)):
        return float(valor)
    # Deja solo digitos: elimina simbolo de peso, espacios y separadores de miles
    solo_digitos = re.sub(r"[^\d]", "", str(valor))
    return float(solo_digitos) if solo_digitos else None


def limpiar_empleados(df: pd.DataFrame) -> pd.DataFrame:
    """
    Limpia el DataFrame de empleados.

    - Normaliza el salario de texto a numero.
    - Convierte las fechas a datetime (los activos traen 'N/A' en Fecha_Retiro).
    - Estandariza columnas de texto.
    """
    df = df.copy()

    if "Salario" in df.columns:
        df["Salario"] = df["Salario"].apply(normalizar_salario)

    # 'N/A' en retiro significa empleado activo: lo dejamos como nulo real
    if "Fecha_Retiro" in df.columns:
        df["Fecha_Retiro"] = df["Fecha_Retiro"].replace("N/A", pd.NaT)
        df["Fecha_Retiro"] = pd.to_datetime(df["Fecha_Retiro"], errors="coerce")

    if "Fecha_Ingreso" in df.columns:
        df["Fecha_Ingreso"] = pd.to_datetime(df["Fecha_Ingreso"], errors="coerce")

    # Columnas de texto que sirven para validar al empleado en el agente
    for columna in ["Nombre_Completo", "Area", "Cargo", "Estado", "Tipo_Contrato"]:
        if columna in df.columns:
            df[columna] = _normalizar_texto(df[columna])

    # El documento se trata como cadena: es un identificador, no una cantidad
    if "Numero_Documento" in df.columns:
        df["Numero_Documento"] = df["Numero_Documento"].astype(str).str.strip()

    return df


def limpiar_tickets(df: pd.DataFrame) -> pd.DataFrame:
    """
    Limpia el DataFrame de tickets.

    - Estandariza espacios en todas las columnas de texto.
    - Parsea las fechas a datetime.
    - Marca como 'Sin asignar' los campos vacios de Tecnico y Categoria, que es
      justo lo que el clasificador intentara completar despues.
    """
    df = df.copy()

    # Normaliza espacios en todas las columnas de texto (object y string)
    for columna in df.select_dtypes(include=["object", "string"]).columns:
        df[columna] = _normalizar_texto(df[columna])

    for columna in ["Última actualización", "Fecha de Apertura"]:
        if columna in df.columns:
            df[columna] = pd.to_datetime(df[columna], dayfirst=True, errors="coerce")

    # Campos que vienen vacios en tickets nuevos: los dejamos explicitos
    for columna in ["Técnico_Asignado", "Categoría"]:
        if columna in df.columns:
            df[columna] = df[columna].replace("", "Sin asignar")

    return df
