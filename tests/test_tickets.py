"""Pruebas del Reto 2: filtrado de tickets criticos y manejo de errores."""

import pandas as pd
import pytest

from nutria_ai.tickets import cli, exportador, filtrado


def _tickets_de_prueba() -> pd.DataFrame:
    """DataFrame minimo con casos mezclados para validar el filtro."""
    return pd.DataFrame({
        "ID": [1, 2, 3, 4],
        "Estado": ["Pendiente", "Pendiente", "Nuevo", "En curso"],
        "Prioridad": ["Alta", "Mediana", "Alta", "Alta"],
    })


def test_filtrar_criticos_solo_pendiente_y_alta():
    """Solo debe quedar el ticket Pendiente + Alta (ID 1)."""
    resultado = filtrado.filtrar_criticos(_tickets_de_prueba())
    assert list(resultado["ID"]) == [1]


def test_filtrar_es_tolerante_a_mayusculas_y_espacios():
    """ 'pendiente ' y 'ALTA' deben contar como criticos."""
    df = pd.DataFrame({"ID": [9], "Estado": [" pendiente "], "Prioridad": ["ALTA"]})
    assert list(filtrado.filtrar_criticos(df)["ID"]) == [9]


def test_columnas_faltantes_lanza_error_claro():
    """Si falta una columna requerida debe lanzarse FormatoTicketsInvalido."""
    df = pd.DataFrame({"Estado": ["Pendiente"]})
    with pytest.raises(filtrado.FormatoTicketsInvalido):
        filtrado.filtrar_criticos(df)


def test_payload_incluye_conteo(tmp_path):
    """El JSON debe traer el total y la lista de tickets."""
    salida = tmp_path / "criticos.json"
    payload = exportador.exportar_json(_tickets_de_prueba().head(1), salida)
    assert payload["total_criticos"] == 1
    assert salida.exists()


def test_cli_archivo_inexistente_devuelve_codigo_error(tmp_path):
    """La CLI debe devolver 1 (no romper) si el archivo de entrada no existe."""
    codigo = cli.ejecutar(tmp_path / "no_existe.txt", tmp_path / "salida.json")
    assert codigo == 1
