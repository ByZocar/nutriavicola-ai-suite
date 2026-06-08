"""
Generador de dataset sintetico de empleados.

Decision clave del proyecto: los datos reales traen documentos y salarios (PII),
asi que NO se suben al repo. Este modulo genera empleados ficticios con la misma
estructura y dominios realistas, para que todo el proyecto sea ejecutable y
demostrable sin exponer datos personales.
"""

from __future__ import annotations

from datetime import datetime, timedelta

import pandas as pd
from faker import Faker

# Dominios realistas tomados de la estructura del negocio (avicola)
AREAS = [
    "Inteligencia de Negocios", "Producción", "Mantenimiento", "Gestión Humana",
    "Ventas", "Calidad", "Logística",
]
CARGOS_POR_AREA = {
    "Inteligencia de Negocios": ["Analista de Datos", "Desarrolladora BI", "Científica de Datos"],
    "Producción": ["Supervisor de Granja", "Operario de Empaque", "Operario de Mezcla"],
    "Mantenimiento": ["Técnico Eléctrico", "Mecánico Industrial", "Soldador"],
    "Gestión Humana": ["Coordinadora de Selección", "Analista de Nómina", "Psicóloga de Bienestar"],
    "Ventas": ["Asesor Comercial TAT", "Ejecutivo de Cuentas", "Mercaderista"],
    "Calidad": ["Inspectora de Inocuidad", "Microbióloga", "Analista Físico-Químico"],
    "Logística": ["Conductor de Ruta", "Auxiliar de Bodega", "Montacarguista"],
}
TIPOS_CONTRATO = ["Indefinido", "Fijo", "Obra o Labor"]


def generar_empleados_sinteticos(cantidad: int = 50, semilla: int = 42) -> pd.DataFrame:
    """
    Genera un DataFrame de empleados ficticios con la misma estructura del original.

    Usa una semilla fija para que el resultado sea reproducible entre ejecuciones.
    Los documentos son secuenciales y ficticios; los nombres provienen de Faker.
    """
    faker = Faker("es_CO")
    Faker.seed(semilla)

    filas = []
    for indice in range(cantidad):
        area = faker.random_element(AREAS)
        cargo = faker.random_element(CARGOS_POR_AREA[area])
        # Un 80% activos, 20% retirados para tener ambos casos en las pruebas
        estado = "Retirado" if faker.boolean(chance_of_getting_true=20) else "Activo"
        fecha_ingreso = faker.date_between(start_date="-6y", end_date="-3m")
        # Solo los retirados tienen fecha de retiro posterior al ingreso
        fecha_retiro = None
        if estado == "Retirado":
            fecha_retiro = fecha_ingreso + timedelta(days=faker.random_int(180, 1500))

        filas.append({
            "Numero_Documento": str(1010000001 + indice),
            "Nombre_Completo": faker.name(),
            "Area": area,
            "Cargo": cargo,
            "Estado": estado,
            "Tipo_Contrato": faker.random_element(TIPOS_CONTRATO),
            # Salario realista en pesos colombianos, multiplo de 100 mil
            "Salario": float(faker.random_int(13, 85) * 100_000),
            "Fecha_Ingreso": pd.to_datetime(fecha_ingreso),
            "Fecha_Retiro": pd.to_datetime(fecha_retiro) if fecha_retiro else pd.NaT,
        })

    return pd.DataFrame(filas)
