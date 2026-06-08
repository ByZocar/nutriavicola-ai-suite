"""Pruebas de la generacion del certificado laboral."""

import pandas as pd
import pytest

from nutria_ai.certificados import generador


def _empleados_de_prueba() -> pd.DataFrame:
    """Mini dataset para validar la busqueda sin depender del archivo."""
    return pd.DataFrame({
        "Numero_Documento": ["1010000003"],
        "Nombre_Completo": ["Lizeth Pérez"],
        "Area": ["Gestión Humana"],
        "Cargo": ["Coordinadora de Selección"],
        "Estado": ["Activo"],
        "Tipo_Contrato": ["Fijo"],
        "Salario": [5600000.0],
    })


def test_buscar_empleado_valido():
    """Con documento + area correctos debe devolver el empleado."""
    empleado = generador.buscar_empleado("1010000003", "Gestión Humana", _empleados_de_prueba())
    assert empleado["Nombre_Completo"] == "Lizeth Pérez"


def test_buscar_empleado_area_tolerante():
    """El area debe compararse ignorando mayusculas y espacios."""
    empleado = generador.buscar_empleado("1010000003", "  gestión humana ", _empleados_de_prueba())
    assert empleado["Cargo"] == "Coordinadora de Selección"


def test_buscar_empleado_inexistente_lanza_error():
    """Documento o area que no coinciden deben lanzar EmpleadoNoEncontrado."""
    with pytest.raises(generador.EmpleadoNoEncontrado):
        generador.buscar_empleado("9999999999", "Ventas", _empleados_de_prueba())


def test_formatear_salario():
    """El salario numerico debe mostrarse como moneda colombiana."""
    assert generador._formatear_salario(3500000.0) == "$ 3.500.000"
