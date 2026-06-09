"""Pruebas de la API del extra usando el cliente de pruebas de FastAPI."""

from fastapi.testclient import TestClient

from nutria_ai.api.app import app

cliente = TestClient(app)


def test_salud():
    """El endpoint de salud debe responder ok."""
    respuesta = cliente.get("/salud")
    assert respuesta.status_code == 200
    assert respuesta.json()["estado"] == "ok"


def test_tickets_criticos():
    """El endpoint de criticos debe traer el conteo y la lista."""
    respuesta = cliente.get("/tickets/criticos")
    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert "total_criticos" in cuerpo
    assert isinstance(cuerpo["tickets"], list)


def test_certificado_empleado_inexistente_devuelve_404():
    """Pedir certificado de un empleado inexistente debe responder 404."""
    respuesta = cliente.post(
        "/certificados",
        json={"numero_documento": "0000000000", "area": "Inexistente"},
    )
    assert respuesta.status_code == 404


def test_clasificador_sugiere():
    """El clasificador debe responder una sugerencia para un titulo."""
    respuesta = cliente.post("/clasificador/sugerir", json={"titulo": "No tengo acceso a SAP"})
    assert respuesta.status_code == 200
    assert "tipo_incidencia_sugerido" in respuesta.json()


def test_certificado_valido_devuelve_url_descarga():
    """Un empleado valido debe responder con el enlace de descarga del PDF."""
    respuesta = cliente.post(
        "/certificados",
        json={"numero_documento": "1010000003", "area": "Gestión Humana"},
    )
    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert "url_descarga" in cuerpo
    assert cuerpo["url_descarga"].endswith("/certificados/1010000003/pdf")


def test_descargar_pdf_por_documento():
    """El endpoint de descarga debe devolver un PDF para un documento valido."""
    respuesta = cliente.get("/certificados/1010000003/pdf")
    assert respuesta.status_code == 200
    assert respuesta.headers["content-type"] == "application/pdf"
