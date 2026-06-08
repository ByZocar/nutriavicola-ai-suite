"""
Clasificador de tickets nuevos.

Los tickets que llegan 'Nuevo' suelen entrar sin tecnico ni categoria. Este modulo
entrena un clasificador de texto (TF-IDF + Naive Bayes) que sugiere el Tipo de
Incidencia y el Nivel de Soporte a partir del titulo del ticket.

Nota honesta: el dataset es pequeno (demostrativo), asi que el modelo es liviano y
su valor esta en mostrar el flujo completo de un asistente que pre-clasifica trabajo.
"""

from __future__ import annotations

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline

from nutria_ai import config


def _construir_pipeline() -> Pipeline:
    """Crea el pipeline TF-IDF + Naive Bayes para texto en espanol."""
    return Pipeline([
        ("tfidf", TfidfVectorizer(lowercase=True, ngram_range=(1, 2))),
        ("nb", MultinomialNB()),
    ])


class ClasificadorTickets:
    """Encapsula dos modelos: uno para Tipo_Incidencia y otro para Nivel_Soporte."""

    def __init__(self) -> None:
        self.modelo_tipo = _construir_pipeline()
        self.modelo_nivel = _construir_pipeline()
        self.entrenado = False

    def entrenar(self, df: pd.DataFrame) -> None:
        """
        Entrena ambos modelos usando el titulo como entrada.

        Usa solo las filas que tienen etiqueta valida en cada objetivo, para no
        ensuciar el entrenamiento con vacios.
        """
        titulos = df["Título"].astype(str)

        mascara_tipo = df["Tipo_Incidencia"].notna() & (df["Tipo_Incidencia"] != "")
        self.modelo_tipo.fit(titulos[mascara_tipo], df.loc[mascara_tipo, "Tipo_Incidencia"])

        mascara_nivel = df["Nivel_Soporte"].notna() & (df["Nivel_Soporte"] != "")
        self.modelo_nivel.fit(titulos[mascara_nivel], df.loc[mascara_nivel, "Nivel_Soporte"])

        self.entrenado = True

    def sugerir(self, titulo: str) -> dict:
        """
        Devuelve la sugerencia de tipo y nivel para un titulo de ticket.

        Incluye la confianza (probabilidad) de cada prediccion, util para decidir
        si se auto-asigna o si se deja en revision humana.
        """
        if not self.entrenado:
            raise RuntimeError("El clasificador no ha sido entrenado todavia.")

        tipo = self.modelo_tipo.predict([titulo])[0]
        nivel = self.modelo_nivel.predict([titulo])[0]
        conf_tipo = float(self.modelo_tipo.predict_proba([titulo]).max())
        conf_nivel = float(self.modelo_nivel.predict_proba([titulo]).max())

        return {
            "titulo": titulo,
            "tipo_incidencia_sugerido": str(tipo),
            "confianza_tipo": round(conf_tipo, 3),
            "nivel_soporte_sugerido": str(nivel),
            "confianza_nivel": round(conf_nivel, 3),
        }


def entrenar_desde_procesados() -> ClasificadorTickets:
    """Carga los tickets limpios y devuelve un clasificador entrenado."""
    if not config.RUTA_TICKETS_LIMPIOS.exists():
        raise FileNotFoundError(
            "Faltan los tickets limpios. Ejecuta primero: "
            "python -m nutria_ai.datos.pipeline"
        )
    df = pd.read_csv(config.RUTA_TICKETS_LIMPIOS)
    clasificador = ClasificadorTickets()
    clasificador.entrenar(df)
    return clasificador
