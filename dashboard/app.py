from datetime import datetime
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st
from sqlalchemy import create_engine, text

DB_PATH = Path(__file__).resolve().parent.parent / "telemetry.db"
DATABASE_URL = f"sqlite:///{DB_PATH}"
REFRESH_SECONDS = 5
MAX_CHART_POINTS = 100
MAX_TABLE_ROWS = 20


@st.cache_resource
def get_engine():
    return create_engine(DATABASE_URL, connect_args={"check_same_thread": False})


def load_telemetry(limit: int = MAX_CHART_POINTS) -> pd.DataFrame:
    if not DB_PATH.exists():
        return pd.DataFrame()

    engine = get_engine()
    query = text(
        """
        SELECT id, timestamp, device_id, pecas_produzidas, temperatura_c,
               rpm_motor, status_maquina, tempo_ciclo_s, eficiencia_pct
        FROM telemetry
        ORDER BY timestamp DESC
        LIMIT :limit
        """
    )
    with engine.connect() as conn:
        df = pd.read_sql(query, conn, params={"limit": limit})

    if df.empty:
        return df

    df["timestamp"] = pd.to_datetime(df["timestamp"])
    return df.sort_values("timestamp")


@st.fragment(run_every=f"{REFRESH_SECONDS}s")
def dashboard_content() -> None:
    df = load_telemetry()

    st.caption(f"Última atualização: {datetime.now().strftime('%H:%M:%S')} — refresh a cada {REFRESH_SECONDS}s")

    if df.empty:
        st.warning(
            "Nenhum dado encontrado. Inicie a API e envie telemetria com o ESP32 ou `python scripts/simulate_esp.py`."
        )
        return

    latest = df.iloc[-1]

    if latest["status_maquina"] == "ALARM":
        st.error("ALERTA: máquina em estado ALARM!")

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Temperatura", f"{latest['temperatura_c']:.1f} °C")
    col2.metric("RPM Motor", f"{latest['rpm_motor']}")
    col3.metric("Peças produzidas", f"{latest['pecas_produzidas']}")
    col4.metric("Eficiência", f"{latest['eficiencia_pct']:.1f} %")
    col5.metric(
        "Status",
        latest["status_maquina"],
        delta=None,
        delta_color="off",
    )

    st.markdown(
        f"**Dispositivo:** `{latest['device_id']}` | "
        f"**Tempo de ciclo:** {latest['tempo_ciclo_s']:.1f}s | "
        f"**Último registro:** {latest['timestamp'].strftime('%d/%m/%Y %H:%M:%S')}"
    )

    st.subheader("Tendências")
    chart_col1, chart_col2, chart_col3 = st.columns(3)

    with chart_col1:
        fig_temp = px.line(
            df,
            x="timestamp",
            y="temperatura_c",
            title="Temperatura (°C)",
            markers=True,
        )
        fig_temp.update_layout(margin=dict(l=20, r=20, t=40, b=20), height=300)
        st.plotly_chart(fig_temp, use_container_width=True)

    with chart_col2:
        fig_rpm = px.line(
            df,
            x="timestamp",
            y="rpm_motor",
            title="RPM do Motor",
            markers=True,
        )
        fig_rpm.update_layout(margin=dict(l=20, r=20, t=40, b=20), height=300)
        st.plotly_chart(fig_rpm, use_container_width=True)

    with chart_col3:
        fig_eff = px.line(
            df,
            x="timestamp",
            y="eficiencia_pct",
            title="Eficiência (%)",
            markers=True,
        )
        fig_eff.update_layout(margin=dict(l=20, r=20, t=40, b=20), height=300)
        st.plotly_chart(fig_eff, use_container_width=True)

    st.subheader("Leituras recentes")
    table_df = df.sort_values("timestamp", ascending=False).head(MAX_TABLE_ROWS).copy()
    table_df["timestamp"] = table_df["timestamp"].dt.strftime("%d/%m/%Y %H:%M:%S")
    st.dataframe(table_df, use_container_width=True, hide_index=True)


def main() -> None:
    st.set_page_config(
        page_title="Telemetria de Produção",
        page_icon="📊",
        layout="wide",
    )
    st.title("Dashboard de Telemetria de Produção")
    st.markdown("Monitoramento em tempo quase real da linha de produção simulada.")
    dashboard_content()


if __name__ == "__main__":
    main()
