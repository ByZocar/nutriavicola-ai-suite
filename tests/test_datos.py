"""Pruebas de la capa de datos: limpieza y generacion sintetica."""

import pandas as pd

from nutria_ai.datos.limpieza import limpiar_tickets, normalizar_salario
from nutria_ai.datos.sintetico import generar_empleados_sinteticos


def test_normalizar_salario_desde_texto():
    """El salario en texto con simbolos debe convertirse a numero limpio."""
    assert normalizar_salario("$ 3.500.000") == 3500000.0
    assert normalizar_salario("$1.800.000") == 1800000.0


def test_normalizar_salario_invalido_devuelve_none():
    """Un valor no interpretable no debe inventar un numero."""
    assert normalizar_salario(None) is None
    assert normalizar_salario("sin dato") is None


def test_limpiar_tickets_marca_vacios():
    """Los campos vacios de tecnico y categoria deben quedar como 'Sin asignar'."""
    crudo = pd.DataFrame({
        "Título": ["  Solicitud  "],
        "Estado": ["Nuevo"],
        "Prioridad": ["Alta"],
        "Técnico_Asignado": [""],
        "Categoría": [""],
    })
    limpio = limpiar_tickets(crudo)
    assert limpio.loc[0, "Título"] == "Solicitud"
    assert limpio.loc[0, "Técnico_Asignado"] == "Sin asignar"
    assert limpio.loc[0, "Categoría"] == "Sin asignar"


def test_generador_sintetico_es_reproducible():
    """Con la misma semilla, el dataset sintetico debe ser identico."""
    df_a = generar_empleados_sinteticos(cantidad=10, semilla=7)
    df_b = generar_empleados_sinteticos(cantidad=10, semilla=7)
    pd.testing.assert_frame_equal(df_a, df_b)
    assert len(df_a) == 10
    # El documento debe ser un identificador en texto, no un numero
    assert df_a["Numero_Documento"].map(type).eq(str).all()
