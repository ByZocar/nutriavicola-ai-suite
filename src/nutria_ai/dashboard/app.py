"""
Dashboard analitico de tickets TI.

Demuestra la capa de inteligencia de negocio: carga de trabajo por tecnico, areas
mas criticas, prioridades y niveles de soporte. Se construye con Streamlit + Plotly
y se empaqueta en Docker para desplegarlo online (Render).

Ejecucion local:
    PYTHONPATH=src streamlit run src/nutria_ai/dashboard/app.py
"""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from nutria_ai.datos import ingesta, limpieza


@st.cache_data
def cargar_tickets() -> pd.DataFrame:
    """Lee y limpia los tickets una sola vez (cache de Streamlit)."""
    return limpieza.limpiar_tickets(ingesta.cargar_tickets())


def main() -> None:
    """Arma el tablero con los indicadores clave de soporte TI."""
    st.set_page_config(page_title="Nutriavicola - Soporte TI", layout="wide")
    st.title("Tablero de Soporte TI - Nutriavicola")
    st.caption("Analitica de tickets para priorizar y distribuir la carga de trabajo.")

    df = cargar_tickets()
    criticos = df[(df["Estado"] == "Pendiente") & (df["Prioridad"] == "Alta")]

    # Indicadores principales
    col1, col2, col3 = st.columns(3)
    col1.metric("Tickets totales", len(df))
    col2.metric("Criticos (Pendiente + Alta)", len(criticos))
    col3.metric("Sin tecnico asignado", int((df["Técnico_Asignado"] == "Sin asignar").sum()))

    # Distribucion por estado y prioridad
    col_a, col_b = st.columns(2)
    with col_a:
        fig_estado = px.bar(
            df["Estado"].value_counts().reset_index(),
            x="Estado", y="count", title="Tickets por estado",
        )
        st.plotly_chart(fig_estado, use_container_width=True)
    with col_b:
        fig_prioridad = px.pie(
            df, names="Prioridad", title="Distribucion por prioridad",
        )
        st.plotly_chart(fig_prioridad, use_container_width=True)

    # Carga por tecnico y areas mas demandantes
    col_c, col_d = st.columns(2)
    with col_c:
        carga = df[df["Técnico_Asignado"] != "Sin asignar"]["Técnico_Asignado"].value_counts()
        fig_tecnico = px.bar(
            carga.reset_index(), x="Técnico_Asignado", y="count",
            title="Carga de trabajo por tecnico",
        )
        st.plotly_chart(fig_tecnico, use_container_width=True)
    with col_d:
        fig_area = px.bar(
            df["Área_Solicitante"].value_counts().reset_index(),
            x="Área_Solicitante", y="count", title="Tickets por area solicitante",
        )
        st.plotly_chart(fig_area, use_container_width=True)

    st.subheader("Tickets criticos pendientes")
    st.dataframe(
        criticos[["ID", "Título", "Área_Solicitante", "Tipo_Incidencia", "Nivel_Soporte"]],
        use_container_width=True,
    )


if __name__ == "__main__":
    main()
