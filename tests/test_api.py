"""Pruebas de la API del extra usando el cliente de pruebas de FastAPI."""

from fastapi.testclient import TestClient

from nutria_ai import config
from nutria_ai.api import seguridad
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


def test_certificado_valido_devuelve_url_firmada():
    """Un empleado valido debe responder con un enlace de descarga firmado."""
    respuesta = cliente.post(
        "/certificados",
        json={"numero_documento": "1010000003", "area": "Gestión Humana"},
    )
    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["exito"] is True
    # La URL ya no expone el documento: usa un token firmado
    assert "/certificados/descargar?token=" in cuerpo["url_descarga"]
    assert "1010000003" not in cuerpo["url_descarga"]


def test_descargar_con_token_valido():
    """Con un token firmado valido se debe poder descargar el PDF."""
    token = seguridad.firmar_descarga("1010000003")
    respuesta = cliente.get(f"/certificados/descargar?token={token}")
    assert respuesta.status_code == 200
    assert respuesta.headers["content-type"] == "application/pdf"


def test_descargar_con_token_invalido_rechaza():
    """Un token falsificado debe ser rechazado con 401."""
    respuesta = cliente.get("/certificados/descargar?token=token-falso-123")
    assert respuesta.status_code == 401


def test_api_key_obligatoria_en_produccion(monkeypatch):
    """Si se define API_KEY, los endpoints protegidos exigen el header correcto."""
    monkeypatch.setattr(config, "API_KEY", "clave-secreta")
    # Sin header -> 401
    sin_clave = cliente.get("/tickets/criticos")
    assert sin_clave.status_code == 401
    # Con header correcto -> 200
    con_clave = cliente.get("/tickets/criticos", headers={"X-API-Key": "clave-secreta"})
    assert con_clave.status_code == 200
