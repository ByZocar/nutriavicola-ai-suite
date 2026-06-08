"""
Orquestador real (reconocimiento de intencion y ruteo).

Replica en Python la logica del orquestador que se construye en Copilot Studio:
recibe el mensaje del usuario, detecta si la intencion es de RRHH (certificado) o de
Soporte TI (tickets) y enruta al servicio correspondiente. Es la prueba viva de la
arquitectura "orquestador -> sub-flujos".
"""

from __future__ import annotations

from dataclasses import dataclass

# Palabras clave por intencion. En Copilot Studio esto equivale a las frases
# desencadenantes / Intent Recognition de cada Topic.
PALABRAS_CERTIFICADO = {
    "certificado", "laboral", "constancia", "carta laboral", "certificacion",
    "certificación", "rrhh", "recursos humanos", "gestion humana",
}
PALABRAS_TICKETS = {
    "ticket", "tickets", "soporte", "incidencia", "caso", "pendiente",
    "critico", "crítico", "ti", "mesa de ayuda", "reporte",
}


@dataclass
class ResultadoIntencion:
    """Resultado del reconocimiento de intencion."""

    intencion: str          # 'certificado', 'tickets' o 'desconocido'
    confianza: float        # proporcion de senales encontradas
    coincidencias: list[str]


def detectar_intencion(mensaje: str) -> ResultadoIntencion:
    """
    Detecta la intencion del mensaje contando coincidencias de palabras clave.

    Devuelve la intencion ganadora y una confianza simple. Si no hay senales de
    ninguna, devuelve 'desconocido' para que el orquestador active el fallback.
    """
    texto = mensaje.lower()
    hits_cert = [p for p in PALABRAS_CERTIFICADO if p in texto]
    hits_tick = [p for p in PALABRAS_TICKETS if p in texto]

    if not hits_cert and not hits_tick:
        return ResultadoIntencion("desconocido", 0.0, [])

    if len(hits_cert) >= len(hits_tick):
        total = len(hits_cert) + len(hits_tick)
        return ResultadoIntencion("certificado", len(hits_cert) / total, hits_cert)

    total = len(hits_cert) + len(hits_tick)
    return ResultadoIntencion("tickets", len(hits_tick) / total, hits_tick)
