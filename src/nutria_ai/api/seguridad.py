"""
Seguridad de la API: autenticacion por API key y enlaces de descarga firmados.

Dos mecanismos:
1. API key: los endpoints que invoca Power Automate exigen el header 'X-API-Key'.
   Asi nadie de internet puede llamar la API sin la clave.
2. URLs firmadas: el certificado no se descarga por documento (adivinable), sino
   con un token firmado (HMAC) que caduca. El documento viaja DENTRO del token,
   no en la URL.
"""

from __future__ import annotations

from fastapi import Header, HTTPException
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

from nutria_ai import config

# "Sal" del serializador: separa este uso de cualquier otra firma futura
_SAL_DESCARGA = "descarga-certificado"


def _serializador() -> URLSafeTimedSerializer:
    """Crea el serializador con el secreto vigente."""
    return URLSafeTimedSerializer(config.SECRETO_FIRMA, salt=_SAL_DESCARGA)


def verificar_api_key(x_api_key: str | None = Header(default=None)) -> None:
    """
    Dependencia de FastAPI: valida el header 'X-API-Key'.

    Si config.API_KEY esta vacia, la API corre en modo desarrollo y no exige
    clave (para tests y local). En produccion se define API_KEY y se vuelve
    obligatoria. Responde 401 si la clave falta o no coincide.
    """
    if not config.API_KEY:
        return  # modo desarrollo: sin exigencia

    if not x_api_key or x_api_key != config.API_KEY:
        raise HTTPException(status_code=401, detail="API key invalida o ausente.")


def firmar_descarga(numero_documento: str) -> str:
    """Genera un token firmado y con caducidad para descargar un certificado."""
    return _serializador().dumps({"documento": str(numero_documento)})


def validar_descarga(token: str) -> str:
    """
    Valida el token de descarga y devuelve el documento si es valido.

    Lanza 401 si el token esta vencido o adulterado, sin filtrar detalles.
    """
    segundos = config.MINUTOS_VALIDEZ_DESCARGA * 60
    try:
        datos = _serializador().loads(token, max_age=segundos)
    except SignatureExpired as error:
        raise HTTPException(status_code=401, detail="El enlace de descarga expiro.") from error
    except BadSignature as error:
        raise HTTPException(status_code=401, detail="Enlace de descarga invalido.") from error

    return str(datos["documento"])
