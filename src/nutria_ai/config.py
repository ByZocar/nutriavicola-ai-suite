"""
Configuracion central del proyecto: rutas y constantes.

Centraliza las rutas para no repetir cadenas magicas por todo el codigo y para
poder sobreescribirlas con variables de entorno (.env) sin tocar la logica.
"""

from __future__ import annotations

import os
from pathlib import Path

# Raiz del proyecto (sube dos niveles desde src/nutria_ai/config.py)
RAIZ_PROYECTO = Path(__file__).resolve().parents[2]

# Carpetas de datos
DIR_DATOS = RAIZ_PROYECTO / "data"
DIR_RAW = DIR_DATOS / "raw"
DIR_PROCESADOS = DIR_DATOS / "processed"

# Archivos crudos de entrada (ignorados por git, viven solo en local)
RUTA_TICKETS_RAW = Path(os.getenv("RUTA_TICKETS_RAW", DIR_RAW / "Reto2.txt"))
RUTA_EMPLEADOS_RAW = Path(os.getenv("RUTA_EMPLEADOS_RAW", DIR_RAW / "empleados.xlsx"))

# Artefactos procesados (versionables, sin PII real)
RUTA_EMPLEADOS_SINTETICO = DIR_PROCESADOS / "empleados_sintetico.csv"
RUTA_TICKETS_LIMPIOS = DIR_PROCESADOS / "tickets_limpios.csv"
RUTA_TICKETS_CRITICOS = DIR_PROCESADOS / "tickets_criticos.json"
RUTA_PERFIL_TICKETS = DIR_PROCESADOS / "perfil_tickets.json"
RUTA_PERFIL_EMPLEADOS = DIR_PROCESADOS / "perfil_empleados.json"

# Separador del archivo de tickets (CSV con punto y coma)
SEPARADOR_TICKETS = ";"

# Criterio de ticket critico (Reto 2)
ESTADO_CRITICO = "Pendiente"
PRIORIDAD_CRITICA = "Alta"

# --- Seguridad de la API ---

# Clave que Power Automate (o cualquier cliente) debe enviar en el header
# 'X-API-Key'. Si esta vacia, la API corre en modo desarrollo SIN exigir clave
# (util para tests y local). En produccion SIEMPRE se debe definir.
API_KEY = os.getenv("API_KEY", "")

# Secreto para firmar las URLs de descarga (HMAC). Asi el enlace no es adivinable
# y caduca. Hay un valor por defecto solo para desarrollo/tests.
SECRETO_FIRMA = os.getenv("SECRETO_FIRMA", "desarrollo-no-usar-en-produccion")

# Minutos de validez del enlace de descarga del certificado
MINUTOS_VALIDEZ_DESCARGA = int(os.getenv("MINUTOS_VALIDEZ_DESCARGA", "15"))

# URL publica base de la API, para construir el enlace de descarga
BASE_URL = os.getenv("BASE_URL", "https://nutriavicola-api.onrender.com")
