# ============================================================
# DATA CENTRE PREDICTIVE MAINTENANCE & AI OPERATIONS
# Streamlit Dashboard - Complete Replacement
# ============================================================

import re
from io import BytesIO
from datetime import datetime

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.lib import colors
from reportlab.lib.units import mm


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Data Centre AI Operations",
    page_icon="🖥️",
    layout="wide",
)


# ============================================================
# FILE PATHS
# ============================================================

DATA_PATH = "data/raw/data_centre_sensor_data.csv"
RISK_PATH = "notebooks/data/model3_risk_predictions.csv"


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def safe_float(value, default=0.0):
    try:
        if pd.isna(value):
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def safe_int(value, default=0):
    try:
        if pd.isna(value):
            return default
        return int(float(value))
    except (TypeError, ValueError):
        return default


def esc(text):
    """Escape text for ReportLab Paragraph."""
    text = "" if text is None else str(text)
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


# ============================================================
# PDF REPORT GENERATOR
# ============================================================

def create_incident_pdf(
    analysis_text,
    server_id,
    risk_score,
    risk_level,
):
    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=18 * mm,
        bottomMargin=18 * mm,
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "IncidentTitle",
        parent=styles["Title"],
        alignment=TA_CENTER,
        fontSize=20,
        leading=24,
        spaceAfter=12,
    )

    subtitle_style = ParagraphStyle(
        "IncidentSubtitle",
        parent=styles["BodyText"],
        alignment=TA_CENTER,
        fontSize=9,
        leading=12,
        spaceAfter=16,
    )

    heading_style = ParagraphStyle(
        "IncidentHeading",
        parent=styles["Heading2"],
        fontSize=12,
        leading=15,
        spaceBefore=10,
        spaceAfter=6,
    )

    body_style = ParagraphStyle(
        "IncidentBody",
        parent=styles["BodyText"],
        fontSize=9.5,
        leading=14,
        spaceAfter=5,
    )

    small_style = ParagraphStyle(
        "IncidentSmall",
        parent=styles["BodyText"],
        fontSize=8,
        leading=11,
    )

    story = []

    story.append(
        Paragraph(
            "DATA CENTRE AI INCIDENT REPORT",
            title_style,
        )
    )

    story.append(
        Paragraph(
            "Predictive Maintenance & AI Operations Intelligence",
            subtitle_style,
        )
    )

    generated_time = datetime.now().strftime(
        "%d-%m-%Y %H:%M:%S"
    )

    incident_data = [
        [
            Paragraph("<b>Server ID</b>", small_style),
            Paragraph(esc(server_id), small_style),
            Paragraph("<b>Risk Level</b>", small_style),
            Paragraph(esc(risk_level), small_style),
        ],
        [
            Paragraph("<b>Predicted Failure Risk</b>", small_style),
            Paragraph(f"{safe_float(risk_score):.1f}%", small_style),
            Paragraph("<b>Generated</b>", small_style),
            Paragraph(esc(generated_time), small_style),
        ],
    ]

    incident_table = Table(
        incident_data,
        colWidths=[
            35 * mm,
            45 * mm,
            35 * mm,
            45 * mm,
        ],
    )

    incident_table.setStyle(
        TableStyle(
            [
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("BACKGROUND", (0, 0), (0, -1), colors.lightgrey),
                ("BACKGROUND", (2, 0), (2, -1), colors.lightgrey),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 7),
                ("RIGHTPADDING", (0, 0), (-1, -1), 7),
                ("TOPPADDING", (0, 0), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
            ]
        )
    )

    story.append(incident_table)
    story.append(Spacer(1, 12))

    story.append(
        Paragraph(
            "Incident Investigation Report",
            heading_style,
        )
    )

    story.append(
        Paragraph(
            "This report was generated by the AI Operations "
            "Intelligence system using predicted failure risk "
            "and infrastructure telemetry associated with "
            "the selected server.",
            body_style,
        )
    )

    heading_words = [
        "INCIDENT SUMMARY",
        "OBSERVED CONDITIONS",
        "RISK ASSESSMENT",
        "POSSIBLE ROOT CAUSE",
        "EVIDENCE",
        "OPERATIONAL IMPACT",
        "IMMEDIATE ACTIONS",
        "MAINTENANCE RECOMMENDATION",
        "PRIORITY",
        "FINAL ASSESSMENT",
    ]

    for raw_line in str(analysis_text).splitlines():
        line = raw_line.strip()

        if not line:
            story.append(Spacer(1, 5))
            continue

        clean_line = re.sub(r"[*#`]", "", line).strip()
        clean_upper = clean_line.upper()

        if any(
            clean_upper.startswith(word)
            for word in heading_words
        ):
            story.append(
                Paragraph(
                    esc(clean_line),
                    heading_style,
                )
            )

        elif re.match(r"^\d+\.", clean_line):
            story.append(
                Paragraph(
                    esc(clean_line),
                    body_style,
                )
            )

        elif clean_line.startswith("-"):
            bullet = "• " + clean_line[1:].strip()
            story.append(
                Paragraph(
                    esc(bullet),
                    body_style,
                )
            )

        else:
            story.append(
                Paragraph(
                    esc(clean_line),
                    body_style,
                )
            )

    story.append(Spacer(1, 15))

    story.append(
        Paragraph(
            "Generated by Data Centre Predictive Maintenance "
            "& AI Operations Intelligence | Llama 3.2",
            subtitle_style,
        )
    )

    doc.build(story)

    buffer.seek(0)
    return buffer.getvalue()


# ============================================================
# LOAD DATA
# ============================================================

@st.cache_data
def load_data():
    df = pd.read_csv(DATA_PATH)
    risk_df = pd.read_csv(RISK_PATH)
    return df, risk_df


try:
    df, risk_df = load_data()
except Exception as e:
    st.error("Unable to load project data.")
    st.code(str(e))
    st.stop()


# ============================================================
# DATA PREPARATION
# ============================================================

if "Timestamp" in df.columns:
    df["Timestamp"] = pd.to_datetime(
        df["Timestamp"],
        errors="coerce",
    )

if "Timestamp" in risk_df.columns:
    risk_df["Timestamp"] = pd.to_datetime(
        risk_df["Timestamp"],
        errors="coerce",
    )


numeric_columns = [
    "CPU_pct",
    "Memory_pct",
    "Disk_pct",
    "Temperature_C",
    "Power_kW",
    "Error_Count",
    "Anomaly_Flag",
    "Failure_Within_24h",
    "Network_Traffic_MBps",
    "Fan_Speed_RPM",
]

for column in numeric_columns:
    if column in df.columns:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce",
        )


risk_numeric_columns = [
    "Risk_Score",
    "CPU_pct",
    "Memory_pct",
    "Disk_pct",
    "Temperature_C",
    "Power_kW",
    "Error_Count",
    "Network_Traffic_MBps",
    "Fan_Speed_RPM",
]

for column in risk_numeric_columns:
    if column in risk_df.columns:
        risk_df[column] = pd.to_numeric(
            risk_df[column],
            errors="coerce",
        )


# ============================================================
# TITLE
# ============================================================

st.title(
    "🖥️ Data Centre Predictive Maintenance & AI Operations"
)

st.caption(
    "Machine Learning + Time-Series Analysis + "
    "Anomaly Detection + Generative AI"
)


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.header("Dashboard Controls")

if "Server_ID" in df.columns:
    servers = sorted(
        df["Server_ID"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )
else:
    servers = []

selected_server = st.sidebar.selectbox(
    "Select Server",
    ["All Servers"] + servers,
)


# ============================================================
# FILTER DATA
# ============================================================

if (
    selected_server != "All Servers"
    and "Server_ID" in df.columns
):
    df_view = df[
        df["Server_ID"].astype(str) == selected_server
    ].copy()
else:
    df_view = df.copy()


if (
    selected_server != "All Servers"
    and "Server_ID" in risk_df.columns
):
    risk_view = risk_df[
        risk_df["Server_ID"].astype(str) == selected_server
    ].copy()
else:
    risk_view = risk_df.copy()


# ============================================================
# TOP KPI CALCULATIONS
# ============================================================

total_records = len(df_view)

total_servers = (
    df_view["Server_ID"].nunique()
    if "Server_ID" in df_view.columns
    else 0
)

total_anomalies = (
    int(df_view["Anomaly_Flag"].fillna(0).sum())
    if "Anomaly_Flag" in df_view.columns
    else 0
)

high_risk_count = (
    int(
        risk_view["Risk_Level"]
        .isin(["High", "Critical"])
        .sum()
    )
    if "Risk_Level" in risk_view.columns
    else 0
)


# ============================================================
# TOP KPI CARDS
# ============================================================

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Sensor Records",
        f"{total_records:,}",
    )

with col2:
    st.metric(
        "Servers Monitored",
        total_servers,
    )

with col3:
    st.metric(
        "Anomalies Detected",
        f"{total_anomalies:,}",
    )

with col4:
    st.metric(
        "High/Critical Risk",
        f"{high_risk_count:,}",
    )


st.divider()


# ============================================================
# SYSTEM OVERVIEW
# ============================================================

st.subheader("System Overview")

col1, col2, col3, col4 = st.columns(4)

with col1:
    if "CPU_pct" in df_view.columns:
        st.metric(
            "Avg CPU",
            f"{df_view['CPU_pct'].mean():.1f}%",
        )

with col2:
    if "Memory_pct" in df_view.columns:
        st.metric(
            "Avg Memory",
            f"{df_view['Memory_pct'].mean():.1f}%",
        )

with col3:
    if "Temperature_C" in df_view.columns:
        st.metric(
            "Avg Temperature",
            f"{df_view['Temperature_C'].mean():.1f} °C",
        )

with col4:
    if "Power_kW" in df_view.columns:
        st.metric(
            "Avg Power",
            f"{df_view['Power_kW'].mean():.2f} kW",
        )


# ============================================================
# SELECTED SERVER HEALTH
# ============================================================

if selected_server != "All Servers" and len(df_view) > 0:

    st.divider()
    st.subheader("Selected Server Health")

    latest = (
        df_view
        .sort_values("Timestamp")
        .iloc[-1]
    )

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        if "CPU_pct" in latest.index:
            st.metric(
                "CPU",
                f"{safe_float(latest['CPU_pct']):.1f}%",
            )

    with col2:
        if "Memory_pct" in latest.index:
            st.metric(
                "Memory",
                f"{safe_float(latest['Memory_pct']):.1f}%",
            )

    with col3:
        if "Disk_pct" in latest.index:
            st.metric(
                "Disk",
                f"{safe_float(latest['Disk_pct']):.1f}%",
            )

    with col4:
        if "Temperature_C" in latest.index:
            st.metric(
                "Temperature",
                f"{safe_float(latest['Temperature_C']):.1f} °C",
            )

    with col5:
        if "Power_kW" in latest.index:
            st.metric(
                "Power",
                f"{safe_float(latest['Power_kW']):.2f} kW",
            )

    st.caption(
        f"Latest reading for {selected_server}"
    )


# ============================================================
# INFRASTRUCTURE SENSOR TRENDS
# ============================================================

st.subheader("Infrastructure Sensor Trends")

if (
    "Timestamp" in df_view.columns
    and len(df_view) > 0
):

    plot_df = (
        df_view
        .dropna(subset=["Timestamp"])
        .sort_values("Timestamp")
        .tail(500)
    )

    if "Temperature_C" in plot_df.columns:
        fig, ax = plt.subplots(figsize=(12, 4))
        ax.plot(
            plot_df["Timestamp"],
            plot_df["Temperature_C"],
        )
        ax.set_title("Temperature Trend")
        ax.set_xlabel("Time")
        ax.set_ylabel("Temperature (°C)")
        plt.xticks(rotation=45)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close(fig)

    col1, col2 = st.columns(2)

    with col1:
        if "CPU_pct" in plot_df.columns:
            fig, ax = plt.subplots(figsize=(7, 4))
            ax.plot(
                plot_df["Timestamp"],
                plot_df["CPU_pct"],
            )
            ax.set_title("CPU Utilization")
            ax.set_ylabel("CPU %")
            plt.xticks(rotation=45)
            plt.tight_layout()
            st.pyplot(fig)
            plt.close(fig)

    with col2:
        if "Memory_pct" in plot_df.columns:
            fig, ax = plt.subplots(figsize=(7, 4))
            ax.plot(
                plot_df["Timestamp"],
                plot_df["Memory_pct"],
            )
            ax.set_title("Memory Utilization")
            ax.set_ylabel("Memory %")
            plt.xticks(rotation=45)
            plt.tight_layout()
            st.pyplot(fig)
            plt.close(fig)

    col1, col2 = st.columns(2)

    with col1:
        if "Disk_pct" in plot_df.columns:
            fig, ax = plt.subplots(figsize=(7, 4))
            ax.plot(
                plot_df["Timestamp"],
                plot_df["Disk_pct"],
            )
            ax.set_title("Disk Utilization")
            ax.set_ylabel("Disk %")
            plt.xticks(rotation=45)
            plt.tight_layout()
            st.pyplot(fig)
            plt.close(fig)

    with col2:
        if "Power_kW" in plot_df.columns:
            fig, ax = plt.subplots(figsize=(7, 4))
            ax.plot(
                plot_df["Timestamp"],
                plot_df["Power_kW"],
            )
            ax.set_title("Power Consumption")
            ax.set_ylabel("Power (kW)")
            plt.xticks(rotation=45)
            plt.tight_layout()
            st.pyplot(fig)
            plt.close(fig)


# ============================================================
# ACTIVE ANOMALY MONITORING
# ============================================================

st.divider()
st.subheader("Active Anomaly Monitoring")

if "Anomaly_Flag" in df_view.columns:

    anomalies = (
        df_view[
            df_view["Anomaly_Flag"] == 1
        ]
        .sort_values(
            "Timestamp",
            ascending=False,
        )
        .head(20)
        .copy()
    )

    if len(anomalies) > 0:

        anomaly_columns = [
            "Timestamp",
            "Server_ID",
            "CPU_pct",
            "Memory_pct",
            "Disk_pct",
            "Temperature_C",
            "Power_kW",
            "Error_Count",
        ]

        available_columns = [
            c for c in anomaly_columns
            if c in anomalies.columns
        ]

        st.dataframe(
            anomalies[available_columns],
            use_container_width=True,
            hide_index=True,
        )

    else:
        st.success(
            "No active anomalies detected in the selected view."
        )

else:
    st.info("Anomaly information is not available.")


# ============================================================
# RISK DISTRIBUTION
# ============================================================

st.divider()
st.subheader("Failure Risk Distribution")

if "Risk_Level" in risk_view.columns:

    risk_counts = (
        risk_view["Risk_Level"]
        .value_counts()
        .reindex(
            ["Low", "Medium", "High", "Critical"],
            fill_value=0,
        )
    )

    fig, ax = plt.subplots(figsize=(8, 4))
    risk_counts.plot(kind="bar", ax=ax)
    ax.set_title("Predicted Failure Risk Levels")
    ax.set_xlabel("Risk Level")
    ax.set_ylabel("Number of Records")
    plt.xticks(rotation=0)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)


# ============================================================
# HIGHEST RISK EVENTS
# ============================================================

st.subheader("Highest Risk Events")

if (
    "Risk_Score" in risk_view.columns
    and len(risk_view) > 0
):

    high_risk = (
        risk_view
        .sort_values(
            "Risk_Score",
            ascending=False,
        )
        .head(20)
        .copy()
    )

    display_columns = [
        "Timestamp",
        "Server_ID",
        "Rack_ID",
        "Risk_Score",
        "Risk_Level",
        "Disk_pct",
        "Temperature_C",
        "Power_kW",
        "CPU_pct",
        "Memory_pct",
        "Error_Count",
        "AI_Explanation",
        "Maintenance_Action",
    ]

    available_columns = [
        c for c in display_columns
        if c in high_risk.columns
    ]

    st.dataframe(
        high_risk[available_columns],
        use_container_width=True,
        hide_index=True,
    )

else:
    high_risk = pd.DataFrame()
    st.info("Risk prediction data is not available.")


# ============================================================
# AI OPERATIONS INSIGHT
# ============================================================

st.subheader("AI Operations Insight")

if len(high_risk) > 0:

    top = high_risk.iloc[0]

    risk_score = safe_float(top.get("Risk_Score", 0))
    risk_level = top.get("Risk_Level", "Unknown")

    explanations = []
    actions = []

    if (
        "Disk_pct" in top.index
        and safe_float(top["Disk_pct"]) >= 80
    ):
        explanations.append(
            f"high disk utilization ({safe_float(top['Disk_pct']):.1f}%)"
        )
        actions.append(
            "Inspect disk health and storage utilization"
        )

    if (
        "Temperature_C" in top.index
        and safe_float(top["Temperature_C"]) >= 32
    ):
        explanations.append(
            f"elevated temperature ({safe_float(top['Temperature_C']):.1f}°C)"
        )
        actions.append(
            "Check cooling and thermal conditions"
        )

    if (
        "CPU_pct" in top.index
        and safe_float(top["CPU_pct"]) >= 80
    ):
        explanations.append(
            f"high CPU utilization ({safe_float(top['CPU_pct']):.1f}%)"
        )
        actions.append(
            "Review CPU workload and running processes"
        )

    if (
        "Memory_pct" in top.index
        and safe_float(top["Memory_pct"]) >= 80
    ):
        explanations.append(
            f"high memory utilization ({safe_float(top['Memory_pct']):.1f}%)"
        )
        actions.append(
            "Check memory consumption and workloads"
        )

    if (
        "Power_kW" in top.index
        and safe_float(top["Power_kW"]) >= 5
    ):
        explanations.append(
            f"elevated power consumption ({safe_float(top['Power_kW']):.2f} kW)"
        )
        actions.append(
            "Review power consumption and server load"
        )

    if (
        "Error_Count" in top.index
        and safe_float(top["Error_Count"]) >= 5
    ):
        explanations.append(
            f"increased error count ({safe_int(top['Error_Count'])})"
        )
        actions.append(
            "Inspect system and application logs"
        )

    if explanations:
        explanation = (
            "Predicted risk is influenced by "
            + ", ".join(explanations)
            + "."
        )
    else:
        explanation = (
            "The model identifies elevated failure risk "
            "from the combined sensor pattern."
        )

    if actions:
        maintenance = " • ".join(actions)
    else:
        maintenance = (
            "Continue preventive monitoring and routine maintenance."
        )

    st.warning(
        f"""
**Risk Level:** {risk_level}

**Failure Risk:** {risk_score:.2f}%

**AI Explanation:**

{explanation}

**Recommended Maintenance:**

{maintenance}
"""
    )


# ============================================================
# SERVER RISK SUMMARY
# ============================================================

st.divider()
st.subheader("Server Risk Summary")

if (
    "Server_ID" in risk_view.columns
    and "Risk_Score" in risk_view.columns
    and "Risk_Level" in risk_view.columns
):

    server_risk = (
        risk_view
        .groupby("Server_ID")
        .agg(
            Total_Records=("Risk_Level", "size"),
            High_Critical=(
                "Risk_Level",
                lambda x: x.isin(
                    ["High", "Critical"]
                ).sum(),
            ),
            Average_Risk=("Risk_Score", "mean"),
            Maximum_Risk=("Risk_Score", "max"),
        )
        .reset_index()
        .sort_values(
            "High_Critical",
            ascending=False,
        )
    )

    server_risk["Average_Risk"] = (
        server_risk["Average_Risk"].round(2)
    )

    server_risk["Maximum_Risk"] = (
        server_risk["Maximum_Risk"].round(2)
    )

    st.dataframe(
        server_risk,
        use_container_width=True,
        hide_index=True,
    )

    chart_data = (
        server_risk
        .head(10)
        .set_index("Server_ID")["High_Critical"]
    )

    fig, ax = plt.subplots(figsize=(10, 4))
    chart_data.plot(kind="bar", ax=ax)
    ax.set_title(
        "Top Servers by High/Critical Risk Events"
    )
    ax.set_xlabel("Server")
    ax.set_ylabel("High/Critical Events")
    plt.xticks(rotation=45)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

else:
    st.info(
        "Server-level risk information is not available."
    )


# ============================================================
# LIVE SERVER HEALTH DETAILS
# ============================================================

st.divider()
st.subheader("🖥️ Live Server Health Details")

if (
    selected_server != "All Servers"
    and len(df_view) > 0
):

    latest_sensor = (
        df_view
        .sort_values("Timestamp")
        .iloc[-1]
    )

    latest_risk = None

    if (
        "Timestamp" in risk_view.columns
        and len(risk_view) > 0
    ):
        latest_risk = (
            risk_view
            .sort_values("Timestamp")
            .iloc[-1]
        )

    st.markdown(f"### 🖥️ {selected_server}")

    if "Timestamp" in latest_sensor.index:
        st.caption(
            f"Latest sensor reading: {latest_sensor['Timestamp']}"
        )

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        if "CPU_pct" in latest_sensor.index:
            st.metric(
                "CPU",
                f"{safe_float(latest_sensor['CPU_pct']):.1f}%",
            )

    with col2:
        if "Memory_pct" in latest_sensor.index:
            st.metric(
                "Memory",
                f"{safe_float(latest_sensor['Memory_pct']):.1f}%",
            )

    with col3:
        if "Disk_pct" in latest_sensor.index:
            st.metric(
                "Disk",
                f"{safe_float(latest_sensor['Disk_pct']):.1f}%",
            )

    with col4:
        if "Temperature_C" in latest_sensor.index:
            st.metric(
                "Temperature",
                f"{safe_float(latest_sensor['Temperature_C']):.1f} °C",
            )

    with col5:
        if "Power_kW" in latest_sensor.index:
            st.metric(
                "Power",
                f"{safe_float(latest_sensor['Power_kW']):.2f} kW",
            )

    if latest_risk is not None:

        st.markdown("#### 🤖 Predictive Risk")

        col1, col2, col3 = st.columns(3)

        with col1:
            if "Risk_Score" in latest_risk.index:
                st.metric(
                    "Failure Risk",
                    f"{safe_float(latest_risk['Risk_Score']):.1f}%",
                )

        with col2:
            if "Risk_Level" in latest_risk.index:
                st.metric(
                    "Risk Level",
                    str(latest_risk["Risk_Level"]),
                )

        with col3:
            if "Error_Count" in latest_sensor.index:
                st.metric(
                    "Error Count",
                    safe_int(latest_sensor["Error_Count"]),
                )

    st.markdown("#### 📡 Additional Telemetry")

    col1, col2, col3 = st.columns(3)

    with col1:
        if "Network_Traffic_MBps" in latest_sensor.index:
            st.metric(
                "Network Traffic",
                f"{safe_float(latest_sensor['Network_Traffic_MBps']):.2f} MB/s",
            )

    with col2:
        if "Fan_Speed_RPM" in latest_sensor.index:
            st.metric(
                "Fan Speed",
                f"{safe_float(latest_sensor['Fan_Speed_RPM']):.0f} RPM",
            )

    with col3:
        if "Anomaly_Flag" in latest_sensor.index:
            anomaly = safe_int(
                latest_sensor["Anomaly_Flag"]
            )

            if anomaly == 1:
                st.error("⚠️ Anomaly Detected")
            else:
                st.success("✅ No Anomaly")

else:
    st.info(
        "Select a specific server from the sidebar "
        "to view live server health details."
    )


# ============================================================
# ACTIVE RISK ALERTS
# ============================================================

st.subheader("🚨 Active Risk Alerts")

if (
    "Risk_Level" in risk_view.columns
    and "Risk_Score" in risk_view.columns
):

    active_alerts = (
        risk_view[
            risk_view["Risk_Level"].isin(
                ["High", "Critical"]
            )
        ]
        .sort_values(
            "Risk_Score",
            ascending=False,
        )
        .head(10)
    )

    if len(active_alerts) == 0:
        st.success(
            "🟢 No high-risk alerts detected."
        )

    else:
        for _, alert in active_alerts.iterrows():

            level = str(alert["Risk_Level"])
            score = safe_float(alert["Risk_Score"])
            server = str(alert.get("Server_ID", "Unknown"))

            if level == "Critical":
                st.error(
                    f"🔴 CRITICAL | Risk {score:.1f}% | Server {server}"
                )
            else:
                st.warning(
                    f"🟠 HIGH RISK | Risk {score:.1f}% | Server {server}"
                )


# ============================================================
# RISK TREND OVER TIME
# ============================================================

st.subheader("📈 Failure Risk Trend")

if (
    "Timestamp" in risk_view.columns
    and "Risk_Score" in risk_view.columns
):

    risk_trend = (
        risk_view.copy()
        .dropna(subset=["Timestamp"])
        .sort_values("Timestamp")
    )

    if len(risk_trend) > 0:

        risk_trend = (
            risk_trend
            .set_index("Timestamp")
            .resample("1h")["Risk_Score"]
            .mean()
            .reset_index()
        )

        fig, ax = plt.subplots(figsize=(12, 4))

        ax.plot(
            risk_trend["Timestamp"],
            risk_trend["Risk_Score"],
            linewidth=2,
        )

        ax.set_title(
            "Average Failure Risk Over Time"
        )
        ax.set_xlabel("Time")
        ax.set_ylabel("Risk Score (%)")

        plt.xticks(rotation=45)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close(fig)

    else:
        st.info(
            "Timestamp data is not available."
        )

else:
    st.info(
        "Timestamp data is not available "
        "for risk trend analysis."
    )


# ============================================================
# SERVER PERFORMANCE MONITORING
# ============================================================

st.subheader("🖥️ Server Performance Monitoring")

performance_df = df_view.copy()

if "Timestamp" in performance_df.columns:

    performance_df = (
        performance_df
        .dropna(subset=["Timestamp"])
        .sort_values("Timestamp")
        .tail(500)
    )

    col1, col2 = st.columns(2)

    with col1:
        if "CPU_pct" in performance_df.columns:
            fig, ax = plt.subplots(figsize=(7, 4))
            ax.plot(
                performance_df["Timestamp"],
                performance_df["CPU_pct"],
            )
            ax.set_title("CPU Utilization")
            ax.set_ylabel("CPU (%)")
            ax.set_xlabel("Time")
            plt.xticks(rotation=45)
            plt.tight_layout()
            st.pyplot(fig)
            plt.close(fig)

    with col2:
        if "Memory_pct" in performance_df.columns:
            fig, ax = plt.subplots(figsize=(7, 4))
            ax.plot(
                performance_df["Timestamp"],
                performance_df["Memory_pct"],
            )
            ax.set_title("Memory Utilization")
            ax.set_ylabel("Memory (%)")
            ax.set_xlabel("Time")
            plt.xticks(rotation=45)
            plt.tight_layout()
            st.pyplot(fig)
            plt.close(fig)

    col1, col2 = st.columns(2)

    with col1:
        if "Temperature_C" in performance_df.columns:
            fig, ax = plt.subplots(figsize=(7, 4))
            ax.plot(
                performance_df["Timestamp"],
                performance_df["Temperature_C"],
            )
            ax.set_title("Temperature")
            ax.set_ylabel("Temperature (°C)")
            ax.set_xlabel("Time")
            plt.xticks(rotation=45)
            plt.tight_layout()
            st.pyplot(fig)
            plt.close(fig)

    with col2:
        if "Power_kW" in performance_df.columns:
            fig, ax = plt.subplots(figsize=(7, 4))
            ax.plot(
                performance_df["Timestamp"],
                performance_df["Power_kW"],
            )
            ax.set_title("Power Consumption")
            ax.set_ylabel("Power (kW)")
            ax.set_xlabel("Time")
            plt.xticks(rotation=45)
            plt.tight_layout()
            st.pyplot(fig)
            plt.close(fig)


# ============================================================
# PREDICTIVE MODEL PERFORMANCE
# ============================================================

st.divider()
st.subheader("Predictive Model Performance")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Accuracy", "82.74%")

with col2:
    st.metric("ROC-AUC", "86.46%")

with col3:
    st.metric("PR-AUC", "44.84%")

with col4:
    st.metric("Failure Recall", "70.00%")

st.caption(
    "Model 3: Class-Balanced Random Forest"
)


# ============================================================
# PROJECT INTELLIGENCE PIPELINE
# ============================================================

st.divider()
st.subheader("Project Intelligence Pipeline")

st.markdown(
    """
**Sensor Data → Data Cleaning → Time-Series Features →
Anomaly Detection → Machine Learning → Failure Risk Prediction →
AI Operations Insight → Maintenance Recommendation**
"""
)


# ============================================================
# GENAI INCIDENT INVESTIGATION
# ============================================================

st.divider()
st.subheader("🤖 AI Incident Investigation")

st.markdown(
    "Use Llama 3.2 to investigate a predicted failure "
    "and generate an operational incident report."
)

if len(risk_view) > 0:

    incident_options = (
        risk_view
        .sort_values(
            "Risk_Score",
            ascending=False,
        )
        .head(50)
        .copy()
    )

    incident_labels = (
        incident_options["Server_ID"].astype(str)
        + " | "
        + incident_options["Risk_Level"].astype(str)
        + " | Risk "
        + incident_options["Risk_Score"].round(1).astype(str)
        + "%"
    )

    selected_incident = st.selectbox(
        "Select an incident for AI investigation",
        range(len(incident_options)),
        format_func=lambda x: incident_labels.iloc[x],
    )

    selected_row = incident_options.iloc[selected_incident]

    st.write(
        f"**Server:** {selected_row.get('Server_ID', 'Unknown')} "
        f"| **Risk:** {selected_row.get('Risk_Level', 'Unknown')} "
        f"| **Score:** {safe_float(selected_row.get('Risk_Score', 0)):.1f}%"
    )

    if st.button(
        "🔍 Investigate Incident with Llama 3.2",
        type="primary",
    ):

        try:

            from ollama_ai import analyze_incident

            with st.spinner(
                "Llama 3.2 is analyzing the incident..."
            ):
                result = analyze_incident(selected_row)

            if result.get("status") == "success":

                st.success(
                    "AI incident investigation completed."
                )

                analysis_text = result.get(
                    "analysis",
                    "No analysis was returned.",
                )

                try:
                    pdf_report = create_incident_pdf(
                        analysis_text=analysis_text,
                        server_id=selected_row.get(
                            "Server_ID",
                            "Unknown",
                        ),
                        risk_score=safe_float(
                            selected_row.get(
                                "Risk_Score",
                                0,
                            )
                        ),
                        risk_level=selected_row.get(
                            "Risk_Level",
                            "Unknown",
                        ),
                    )

                    st.download_button(
                        label="📄 Download Professional Incident Report",
                        data=pdf_report,
                        file_name=(
                            f"Incident_Report_"
                            f"{selected_row.get('Server_ID', 'Unknown')}.pdf"
                        ),
                        mime="application/pdf",
                    )

                except Exception as pdf_error:
                    st.warning(
                        f"PDF generation failed: {pdf_error}"
                    )

                st.markdown(analysis_text)

                st.download_button(
                    label="📥 Download Incident Report (TXT)",
                    data=analysis_text,
                    file_name=(
                        f"Incident_Report_"
                        f"{selected_row.get('Server_ID', 'Unknown')}.txt"
                    ),
                    mime="text/plain",
                )

            else:
                st.error(
                    result.get(
                        "message",
                        "AI investigation failed.",
                    )
                )

        except ImportError:
            st.error(
                "ollama_ai.py was not found. "
                "Make sure ollama_ai.py is in the same project folder as app.py."
            )

        except Exception as e:
            st.error(
                f"AI investigation error: {e}"
            )

else:
    st.info(
        "No risk records are available for AI investigation."
    )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "Data Centre Predictive Maintenance & AI Operations "
    "Intelligence | Machine Learning + Time-Series Analysis "
    "+ AI Operations | Llama 3.2"
)
