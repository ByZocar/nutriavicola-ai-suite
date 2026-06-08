"""Pruebas del clasificador de tickets nuevos."""

import pandas as pd
import pytest

from nutria_ai.clasificador.modelo import ClasificadorTickets


def _tickets_entrenamiento() -> pd.DataFrame:
    """Datos minimos con senales claras de texto por categoria."""
    return pd.DataFrame({
        "Título": [
            "No tengo acceso a SAP", "Solicitud de acceso a SIESA",
            "Cambio de teclado y mouse", "Reposicion de impresora",
            "Problema de red wifi", "Sin internet en la bodega",
        ],
        "Tipo_Incidencia": ["Accesos", "Accesos", "Hardware", "Hardware", "Redes", "Redes"],
        "Nivel_Soporte": ["Nivel 2", "Nivel 2", "Nivel 1", "Nivel 1", "Nivel 3", "Nivel 3"],
    })


def test_sugerencia_devuelve_campos_esperados():
    """La sugerencia debe traer tipo, nivel y sus confianzas."""
    clasificador = ClasificadorTickets()
    clasificador.entrenar(_tickets_entrenamiento())
    sugerencia = clasificador.sugerir("Necesito acceso a SAP urgente")

    assert "tipo_incidencia_sugerido" in sugerencia
    assert "nivel_soporte_sugerido" in sugerencia
    assert 0.0 <= sugerencia["confianza_tipo"] <= 1.0


def test_clasificador_sin_entrenar_falla():
    """Pedir una sugerencia sin entrenar debe lanzar un error claro."""
    clasificador = ClasificadorTickets()
    with pytest.raises(RuntimeError):
        clasificador.sugerir("cualquier cosa")
