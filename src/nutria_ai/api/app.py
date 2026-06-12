"""
API REST del extra (FastAPI).

Expone como servicio lo que construimos: el filtrado de tickets criticos, un resumen
analitico, la generacion del certificado laboral y la sugerencia del clasificador.
Es el punto que Copilot Studio invoca como "accion externa".

Ejecucion local:
    PYTHONPATH=src uvicorn nutria_ai.api.app:app --reload
"""

from __future__ import annotations

import pandas as pd
from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from nutria_ai import config
from nutria_ai.api import seguridad
from nutria_ai.certificados import generador
from nutria_ai.clasificador import modelo
from nutria_ai.tickets import exportador, filtrado

app = FastAPI(
    title="Nutriavicola AI Suite - API",
    description="Acciones externas para los agentes de RRHH y Soporte TI.",
    version="0.1.0",
)


def _leer_tickets_procesados() -> pd.DataFrame:
    """
    Lee los tickets desde el CSV procesado, no desde el raw.

    En el contenedor de produccion no existen datos crudos (gitignored),
    asi que siempre leemos el artefacto limpio que si esta en el repo.
    """
    return pd.read_csv(config.RUTA_TICKETS_LIMPIOS)

# El clasificador se entrena una sola vez y se reutiliza (cache en memoria)
_clasificador: modelo.ClasificadorTickets | None = None


def _obtener_clasificador() -> modelo.ClasificadorTickets:
    """Entrena el clasificador la primera vez y lo cachea para las siguientes."""
    global _clasificador
    if _clasificador is None:
        _clasificador = modelo.entrenar_desde_procesados()
    return _clasificador


class SolicitudCertificado(BaseModel):
    """Datos que el agente de RRHH valida antes de generar el certificado."""

    numero_documento: str = Field(..., examples=["1010000003"])
    area: str = Field(..., examples=["Gestión Humana"])
    # Correo del usuario autenticado (Entra ID). Si llega, se valida que el
    # documento le pertenezca. El agente en Teams/web lo envia siempre.
    correo_solicitante: str | None = Field(default=None, examples=["lizeth.perez003@nutriavicola.com"])


class SolicitudClasificacion(BaseModel):
    """Titulo de un ticket nuevo para sugerir su clasificacion."""

    titulo: str = Field(..., examples=["No tengo acceso a SAP"])


@app.get("/salud")
def salud() -> dict:
    """Verificacion simple de que la API esta viva."""
    return {"estado": "ok", "servicio": "nutriavicola-ai-suite"}


@app.get("/tickets/criticos", dependencies=[Depends(seguridad.verificar_api_key)])
def tickets_criticos() -> dict:
    """Devuelve los tickets criticos (Pendiente + Alta) y su conteo."""
    df = _leer_tickets_procesados()
    criticos = filtrado.filtrar_criticos(df)
    return exportador.construir_payload(criticos)


@app.get("/tickets/resumen", dependencies=[Depends(seguridad.verificar_api_key)])
def resumen_tickets() -> dict:
    """Resumen analitico de los tickets para el dashboard y el agente."""
    df = _leer_tickets_procesados()
    return {
        "total": int(len(df)),
        "por_estado": df["Estado"].value_counts().to_dict(),
        "por_prioridad": df["Prioridad"].value_counts().to_dict(),
        "por_tipo": df["Tipo_Incidencia"].value_counts().to_dict(),
        "por_nivel": df["Nivel_Soporte"].value_counts().to_dict(),
    }


@app.post("/certificados", dependencies=[Depends(seguridad.verificar_api_key)])
def crear_certificado(solicitud: SolicitudCertificado) -> dict:
    """
    Valida documento + area y genera el certificado laboral en PDF.

    Si el empleado no existe devuelve exito=false (no 404) para que Copilot
    Studio lo trate como dato de negocio y no como error de flujo. Cuando hay
    exito devuelve un enlace de descarga FIRMADO y con caducidad: el documento
    viaja dentro del token, no en la URL, asi no es adivinable.
    """
    try:
        empleado = generador.buscar_empleado(solicitud.numero_documento, solicitud.area)
        generador.validar_identidad(empleado, solicitud.correo_solicitante)
        generador.generar_certificado_pdf(solicitud.numero_documento, solicitud.area)
    except (generador.EmpleadoNoEncontrado, generador.IdentidadNoCoincide) as error:
        # exito=false: el agente lo maneja conversacionalmente (no es error de flujo)
        return {
            "exito": False,
            "mensaje": str(error),
            "url_descarga": "",
        }

    documento = str(empleado["Numero_Documento"])
    token = seguridad.firmar_descarga(documento)
    url_descarga = f"{config.BASE_URL}/certificados/descargar?token={token}"

    return {
        "exito": True,
        "mensaje": f"Certificado generado para {empleado['Nombre_Completo']}.",
        "url_descarga": url_descarga,
        "empleado": {
            "nombre": empleado["Nombre_Completo"],
            "cargo": empleado["Cargo"],
            "area": empleado["Area"],
            "estado": empleado["Estado"],
        },
    }


@app.get("/certificados/descargar")
def descargar_certificado(token: str) -> FileResponse:
    """
    Devuelve el PDF del certificado a partir de un token firmado y vigente.

    No exige API key porque lo abre el navegador del usuario, pero el token
    caduca y no se puede falsificar. El documento se extrae del token, nunca
    de la URL en claro.
    """
    documento = seguridad.validar_descarga(token)
    try:
        ruta = generador.generar_certificado_pdf_por_documento(documento)
    except generador.EmpleadoNoEncontrado as error:
        raise HTTPException(status_code=404, detail=str(error))
    return FileResponse(ruta, media_type="application/pdf", filename=ruta.name)


@app.post("/clasificador/sugerir", dependencies=[Depends(seguridad.verificar_api_key)])
def sugerir_clasificacion(solicitud: SolicitudClasificacion) -> dict:
    """Sugiere tipo de incidencia y nivel de soporte para un ticket nuevo."""
    clasificador = _obtener_clasificador()
    return clasificador.sugerir(solicitud.titulo)
