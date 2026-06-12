"""Pruebas de la API del extra usando el cliente de pruebas de FastAPI."""

from fastapi.testclient import TestClient

from nutria_ai import config
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


def test_certificado_empleado_inexistente_devuelve_exito_false():
    """Empleado no encontrado: responde 200 con exito=false para que Power Automate no lo trate como error de flujo."""
    respuesta = cliente.post(
        "/certificados",
        json={"numero_documento": "0000000000", "area": "Inexistente"},
    )
    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["exito"] is False
    assert "mensaje" in cuerpo


def test_clasificador_sugiere():
    """El clasificador debe responder una sugerencia para un titulo."""
    respuesta = cliente.post("/clasificador/sugerir", json={"titulo": "No tengo acceso a SAP"})
    assert respuesta.status_code == 200
    assert "tipo_incidencia_sugerido" in respuesta.json()


def test_certificado_valido_devuelve_url_descarga():
    """Un empleado valido debe responder con exito y un enlace de descarga."""
    respuesta = cliente.post(
        "/certificados",
        json={"numero_documento": "1010000003", "area": "Gestión Humana"},
    )
    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["exito"] is True
    assert "/certificados/1010000003/pdf" in cuerpo["url_descarga"]


def test_descargar_pdf_por_documento():
    """La URL de descarga directa debe devolver el PDF del empleado."""
    respuesta = cliente.get("/certificados/1010000003/pdf")
    assert respuesta.status_code == 200
    assert respuesta.headers["content-type"] == "application/pdf"


def test_descargar_pdf_documento_inexistente():
    """Un documento que no existe debe devolver 404."""
    respuesta = cliente.get("/certificados/0000000000/pdf")
    assert respuesta.status_code == 404


def test_api_key_obligatoria_en_produccion(monkeypatch):
    """Si se define API_KEY, los endpoints protegidos exigen el header correcto."""
    monkeypatch.setattr(config, "API_KEY", "clave-secreta")
    # Sin header -> 401
    sin_clave = cliente.get("/tickets/criticos")
    assert sin_clave.status_code == 401
    # Con header correcto -> 200
    con_clave = cliente.get("/tickets/criticos", headers={"X-API-Key": "clave-secreta"})
    assert con_clave.status_code == 200
