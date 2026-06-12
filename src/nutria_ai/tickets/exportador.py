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


def _icono_nivel(nivel: str) -> str:
    """Icono visual por nivel de soporte para facilitar el escaneo rapido."""
    iconos = {"Nivel 1": "🟢", "Nivel 2": "🟡", "Nivel 3": "🔴"}
    return iconos.get(str(nivel).strip(), "⚪")


def construir_resumen_texto(tickets: list[dict]) -> str:
    """
    Genera un resumen en texto plano con formato legible para el chat.

    Cada ticket ocupa dos lineas: titulo/area y nivel. Sin JSON, sin parseo,
    listo para mostrarse directamente en el mensaje del agente.
    """
    if not tickets:
        return "No hay tickets críticos pendientes en este momento."

    lineas = [f"*{len(tickets)} tickets críticos pendientes:*\n"]
    for t in tickets:
        icono = _icono_nivel(t.get("Nivel_Soporte", ""))
        lineas.append(
            f"{icono} *#{t.get('ID', '?')}* — {t.get('Título', 'Sin título')}\n"
            f"   Área: {t.get('Área_Solicitante', '?')} · {t.get('Nivel_Soporte', '?')}"
        )
    return "\n".join(lineas)


def construir_payload(df_criticos: pd.DataFrame) -> dict:
    """
    Arma el diccionario que se serializara a JSON.

    Incluye `resumen_texto`: texto ya formateado para mostrar en el chat sin
    pasar por el LLM. El agente solo lo muestra, sin gasto de tokens ni latencia.
    """
    registros = json.loads(df_criticos.to_json(orient="records", date_format="iso"))
    return {
        "generado_en": datetime.now().isoformat(timespec="seconds"),
        "criterio": {"estado": "Pendiente", "prioridad": "Alta"},
        "total_criticos": int(len(df_criticos)),
        "resumen_texto": construir_resumen_texto(registros),
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
