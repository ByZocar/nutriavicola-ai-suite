"""
Convierte los diagramas HTML de esta carpeta a PDF.

Cumple la regla del proyecto: los diagramas se construyen en HTML y se exportan a
PDF reproducible, en vez de dibujarlos en markdown. Usa WeasyPrint.

Ejecucion:
    python diagramas/convertir_a_pdf.py
"""

from __future__ import annotations

from pathlib import Path

from weasyprint import HTML

DIR_DIAGRAMAS = Path(__file__).resolve().parent


def convertir_todos() -> None:
    """
    Convierte cada .html en .pdf, incluyendo subcarpetas (ej: canales/).

    Asi entran tanto los diagramas de arquitectura como los mockups de canales.
    """
    htmls = sorted(DIR_DIAGRAMAS.rglob("*.html"))
    if not htmls:
        print("No se encontraron diagramas HTML para convertir.")
        return

    for html in htmls:
        salida = html.with_suffix(".pdf")
        HTML(filename=str(html)).write_pdf(str(salida))
        print(f"PDF generado: {salida.relative_to(DIR_DIAGRAMAS)}")


if __name__ == "__main__":
    convertir_todos()
