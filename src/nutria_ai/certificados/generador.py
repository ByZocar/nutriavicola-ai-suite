"""
Generacion del certificado laboral en PDF.

Es la "accion externa" que el Reto 1 solo pide mencionar; aqui la implementamos de
verdad. Valida que el empleado exista (documento + area) y produce un PDF formal.
Trabaja sobre el dataset sintetico, asi que no expone datos reales.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

from nutria_ai import config


class EmpleadoNoEncontrado(Exception):
    """Se lanza cuando no hay un empleado que coincida con documento + area."""


def _formatear_salario(valor: float) -> str:
    """Convierte 3500000.0 en '$ 3.500.000' para mostrarlo en el certificado."""
    return f"$ {int(valor):,}".replace(",", ".")


def cargar_empleados() -> pd.DataFrame:
    """Lee el dataset sintetico de empleados ya procesado."""
    if not config.RUTA_EMPLEADOS_SINTETICO.exists():
        raise FileNotFoundError(
            "Falta el dataset de empleados. Ejecuta primero: "
            "python -m nutria_ai.datos.pipeline"
        )
    df = pd.read_csv(config.RUTA_EMPLEADOS_SINTETICO, dtype={"Numero_Documento": str})
    return df


def buscar_empleado(numero_documento: str, area: str, df: pd.DataFrame | None = None) -> dict:
    """
    Valida los dos datos clave (documento + area) y devuelve el empleado.

    La comparacion del area ignora mayusculas/minusculas y espacios. Si no hay
    coincidencia se lanza EmpleadoNoEncontrado, que el agente traduce a un mensaje
    amable o a una transferencia a un humano.
    """
    df = df if df is not None else cargar_empleados()

    documento = str(numero_documento).strip()
    area_norm = str(area).strip().casefold()

    coincidencias = df[
        (df["Numero_Documento"] == documento)
        & (df["Area"].str.strip().str.casefold() == area_norm)
    ]
    if coincidencias.empty:
        raise EmpleadoNoEncontrado(
            f"No se encontro un empleado con documento {documento} en el area '{area}'."
        )
    return coincidencias.iloc[0].to_dict()


def buscar_por_documento(numero_documento: str, df: pd.DataFrame | None = None) -> dict:
    """
    Busca un empleado solo por documento (el documento es identificador unico).

    Se usa para la descarga del PDF: la validacion de documento + area ya ocurrio
    en la conversacion, asi que aqui basta el documento para recuperar el archivo.
    """
    df = df if df is not None else cargar_empleados()
    documento = str(numero_documento).strip()
    coincidencias = df[df["Numero_Documento"] == documento]
    if coincidencias.empty:
        raise EmpleadoNoEncontrado(
            f"No se encontro un empleado con documento {documento}."
        )
    return coincidencias.iloc[0].to_dict()


def generar_certificado_pdf_por_documento(
    numero_documento: str, ruta_salida: Path | str | None = None
) -> Path:
    """Genera el certificado validando solo por documento (para la descarga)."""
    empleado = buscar_por_documento(numero_documento)
    return generar_certificado_pdf(empleado["Numero_Documento"], empleado["Area"], ruta_salida)


def generar_certificado_pdf(
    numero_documento: str, area: str, ruta_salida: Path | str | None = None
) -> Path:
    """
    Genera el certificado laboral en PDF para el empleado indicado.

    Devuelve la ruta del PDF generado. El texto es formal, como lo esperaria un
    area de Gestion Humana de Nutriavicola.
    """
    empleado = buscar_empleado(numero_documento, area)

    ruta_salida = Path(ruta_salida) if ruta_salida else (
        config.DIR_PROCESADOS / f"certificado_{empleado['Numero_Documento']}.pdf"
    )
    ruta_salida.parent.mkdir(parents=True, exist_ok=True)

    estilos = getSampleStyleSheet()
    documento_pdf = SimpleDocTemplate(str(ruta_salida), pagesize=letter)

    hoy = datetime.now().strftime("%d de %B de %Y")
    estado = empleado["Estado"]
    verbo = "labora actualmente" if estado == "Activo" else "laboró"

    cuerpo = (
        f"NUTRIAVICOLA S.A.S. certifica que el(la) senor(a) "
        f"<b>{empleado['Nombre_Completo']}</b>, identificado(a) con documento "
        f"No. <b>{empleado['Numero_Documento']}</b>, {verbo} en nuestra compania "
        f"desempenando el cargo de <b>{empleado['Cargo']}</b> en el area de "
        f"<b>{empleado['Area']}</b>, bajo un contrato a termino "
        f"<b>{empleado['Tipo_Contrato']}</b>, con una asignacion salarial mensual de "
        f"<b>{_formatear_salario(empleado['Salario'])}</b>."
    )

    elementos = [
        Paragraph("CERTIFICADO LABORAL", estilos["Title"]),
        Spacer(1, cm),
        Paragraph(f"Bogota, {hoy}", estilos["Normal"]),
        Spacer(1, cm),
        Paragraph(cuerpo, estilos["BodyText"]),
        Spacer(1, cm),
        Paragraph(
            "El presente certificado se expide a solicitud del interesado.",
            estilos["BodyText"],
        ),
        Spacer(1, 2 * cm),
        Paragraph("____________________________", estilos["Normal"]),
        Paragraph("Coordinacion de Gestion Humana", estilos["Normal"]),
        Paragraph("NUTRIAVICOLA S.A.S.", estilos["Normal"]),
    ]

    documento_pdf.build(elementos)
    return ruta_salida
