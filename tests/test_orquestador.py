"""Pruebas del reconocimiento de intencion del orquestador."""

from nutria_ai.orquestador.enrutador import detectar_intencion


def test_intencion_certificado():
    """Un mensaje sobre certificado debe rutear a RRHH."""
    assert detectar_intencion("Necesito un certificado laboral").intencion == "certificado"


def test_intencion_tickets():
    """Un mensaje sobre tickets debe rutear a Soporte TI."""
    assert detectar_intencion("cuantos tickets criticos tengo pendientes").intencion == "tickets"


def test_intencion_desconocida():
    """Un mensaje sin senales debe devolver 'desconocido' para el fallback."""
    resultado = detectar_intencion("hola buenos dias")
    assert resultado.intencion == "desconocido"
    assert resultado.confianza == 0.0
