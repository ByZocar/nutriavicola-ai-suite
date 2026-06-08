"""
Exportacion de tickets criticos a JSON.

Construye una estructura pensada para que un agente o sistema externo la consuma:
incluye un conteo explicito (para el mensaje "tienes N tickets criticos") y la lista
de tickets con sus campos relevantes.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import pandas as pd


def construir_payload(df_criticos: pd.DataFrame) -> dict:
    """
    Arma el diccionario que se serializara a JSON.

    El campo 'total_criticos' es el dato que el Agente de Soporte TI usara para
    responder al usuario sin tener que contar los registros por su cuenta.
    """
    registros = json.loads(df_criticos.to_json(orient="records", date_format="iso"))
    return {
        "generado_en": datetime.now().isoformat(timespec="seconds"),
        "criterio": {"estado": "Pendiente", "prioridad": "Alta"},
        "total_criticos": int(len(df_criticos)),
        "tickets": registros,
    }


def exportar_json(df_criticos: pd.DataFrame, ruta_salida: Path | str) -> dict:
    """
    Guarda los tickets criticos en un archivo JSON y devuelve el payload.

    Crea la carpeta de salida si no existe. El JSON queda en UTF-8 y con
    indentacion para que sea legible por humanos y por maquinas.
    """
    ruta_salida = Path(ruta_salida)
    ruta_salida.parent.mkdir(parents=True, exist_ok=True)

    payload = construir_payload(df_criticos)
    with open(ruta_salida, "w", encoding="utf-8") as archivo:
        json.dump(payload, archivo, ensure_ascii=False, indent=2)

    return payload
