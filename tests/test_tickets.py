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


def test_payload_incluye_resumen_texto():
    """El payload debe incluir un resumen en texto listo para el chat."""
    df = pd.DataFrame({
        "ID": [6565],
        "Título": ["Cambio contraseña de SIESa"],
        "Estado": ["Pendiente"],
        "Prioridad": ["Alta"],
        "Área_Solicitante": ["Calidad"],
        "Nivel_Soporte": ["Nivel 3"],
    })
    payload = exportador.construir_payload(df)
    assert "resumen_texto" in payload
    resumen = payload["resumen_texto"]
    # Debe mostrar ID, titulo, area y nivel (legible, no JSON crudo)
    assert "6565" in resumen
    assert "Calidad" in resumen
    assert "Nivel 3" in resumen
    assert "{" not in resumen  # no puede ser JSON crudo


def test_resumen_texto_vacio():
    """Con cero tickets el resumen debe decirlo, no mostrar una lista vacia."""
    payload = exportador.construir_payload(pd.DataFrame(columns=["ID", "Título", "Área_Solicitante", "Nivel_Soporte"]))
    assert "No hay" in payload["resumen_texto"]


def test_cli_archivo_inexistente_devuelve_codigo_error(tmp_path):
    """La CLI debe devolver 1 (no romper) si el archivo de entrada no existe."""
    codigo = cli.ejecutar(tmp_path / "no_existe.txt", tmp_path / "salida.json")
    assert codigo == 1
