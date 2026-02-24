# ==============================================================================
# AI-Powered Traffic Signal Simulation — Streamlit Dashboard
# ==============================================================================

import os
import streamlit as st
import pandas as pd
import plotly.express as px

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Traffic Signal Dashboard",
    page_icon="🚦",
    layout="wide",
)


# ── Data loaders ─────────────────────────────────────────────────────────────

def load_excel(sheet_name):
    """Load a sheet from simulation_results.xlsx (if it exists)."""
    path = "simulation_results.xlsx"
    if not os.path.exists(path):
        st.warning(f"'{path}' not found — run the simulation first to generate results.")
        return None
    try:
        return pd.read_excel(path, sheet_name=sheet_name)
    except Exception as exc:
        st.error(f"Error reading '{path}': {exc}")
        return None


def load_signal_results():
    """Load signal_results.csv with error handling."""
    path = "signal_results.csv"
    if not os.path.exists(path):
        st.warning(f"'{path}' not found — run the simulation first.")
        return None
    try:
        return pd.read_csv(path)
    except Exception as exc:
        st.error(f"Error reading '{path}': {exc}")
        return None


# ── Sidebar ──────────────────────────────────────────────────────────────────

st.sidebar.header("Navigation")
page = st.sidebar.radio("Select Page", ["Problem Statement", "Graphical Representation"])


# ==============================================================================
# PAGE 1 — Problem Statement
# ==============================================================================

if page == "Problem Statement":
    st.title("🚦 AI-Powered Traffic Signal Simulation")

    st.header("Problem Definition")
    st.write(
        "In urban environments, inefficient traffic signal timings contribute to "
        "congestion, increased fuel consumption, and environmental pollution. "
        "The goal of this project is to develop an AI-driven approach to optimize "
        "traffic light durations based on real-time vehicle detection."
    )

    st.header("Approach to Solve the Problem")
    st.write(
        "The system utilizes YOLOv8 for vehicle detection, combined with "
        "LSTM-based predictive analysis. The model dynamically adjusts traffic "
        "signal timings based on real-time traffic density and predicted "
        "congestion patterns. Additionally, an LSTM model is implemented to "
        "predict future traffic flow based on historical data. This predictive "
        "capability allows the system to anticipate congestion and adjust signal "
        "timings proactively, improving overall traffic management."
    )

    st.header("How It Works")
    st.write("The AI-powered traffic signal system works through the following steps:")

    st.subheader("1. Vehicle Detection Using YOLOv8")
    st.write(
        "The system processes real-time video feeds from traffic cameras using "
        "the YOLOv8 deep learning model. YOLO (You Only Look Once) is an object "
        "detection algorithm capable of identifying and classifying multiple "
        "vehicles — cars, trucks, buses, and motorcycles — in a single frame. "
        "Detected vehicles are assigned bounding boxes providing precise locations."
    )

    st.subheader("2. Traffic Data Collection and Analysis")
    st.write(
        "Detected vehicles are counted per lane and categorized by type. This "
        "data is stored in a structured format for real-time monitoring of "
        "vehicle density. Traffic data is then analyzed to determine congestion "
        "levels and traffic flow patterns."
    )

    st.subheader("3. Dynamic Traffic Signal Adjustment")
    st.write(
        "Using the collected vehicle data, an AI-based algorithm calculates the "
        "optimal green-light duration. More congested lanes receive longer green "
        "phases, preventing unnecessary delays and reducing idle time."
    )

    st.subheader("4. Continuous Learning and Optimization")
    st.write(
        "The AI model continuously learns from historical traffic patterns using "
        "an LSTM (Long Short-Term Memory) network. This allows the system to "
        "predict future congestion and adjust signal timings accordingly."
    )

    # Demo videos
    st.header("Demo")
    st.write(
        "Below are demonstration videos showcasing the AI-powered traffic signal "
        "simulation in action."
    )

    vid1 = "vids/10.02.2025_21.34.08_REC.mp4"
    vid2 = "vids/10.02.2025_21.30.20_REC.mp4"

    col1, col2 = st.columns(2)
    with col1:
        if os.path.exists(vid1):
            st.video(vid1)
        else:
            st.info(f"Video not found: {vid1}")
    with col2:
        if os.path.exists(vid2):
            st.video(vid2)
        else:
            st.info(f"Video not found: {vid2}")


# ==============================================================================
# PAGE 2 — Graphical Representation
# ==============================================================================

elif page == "Graphical Representation":
    st.title("📊 Traffic Control — Comparison & Results")

    st.header("Comparison of Traffic Control Approaches")
    st.write(
        "This section compares total vehicle counts for YOLO-based and manual "
        "traffic control approaches across multiple experiments."
    )

    signal_df = load_signal_results()

    if signal_df is not None:
        col1, col2 = st.columns(2)

        with col1:
            fig_bar = px.bar(
                signal_df,
                x="Exp No",
                y=["Total", "Manual"],
                barmode="group",
                title="Total Vehicle Counts: YOLO vs Manual",
                labels={"value": "Vehicle Count", "Exp No": "Experiment"},
                color_discrete_map={"Total": "#4A8CFF", "Manual": "#FF6B6B"},
            )
            fig_bar.update_layout(legend_title_text="Approach")
            st.plotly_chart(fig_bar, use_container_width=True)

        with col2:
            fig_line = px.line(
                signal_df,
                x="Exp No",
                y=["Total", "Manual"],
                title="Trend: YOLO vs Manual",
                labels={"value": "Vehicle Count", "Exp No": "Experiment"},
                color_discrete_map={"Total": "#4A8CFF", "Manual": "#FF6B6B"},
                markers=True,
            )
            fig_line.update_layout(legend_title_text="Approach")
            st.plotly_chart(fig_line, use_container_width=True)

        # Per-lane breakdown
        lane_cols = [c for c in signal_df.columns if c.startswith("Lane")]
        if lane_cols:
            st.subheader("Per-Lane Vehicle Distribution")
            fig_lanes = px.bar(
                signal_df,
                x="Exp No",
                y=lane_cols,
                barmode="stack",
                title="Per-Lane Vehicle Counts",
                labels={"value": "Vehicles", "Exp No": "Experiment"},
            )
            st.plotly_chart(fig_lanes, use_container_width=True)

        # Summary statistics
        st.subheader("Summary Statistics")
        summary = signal_df[["Total", "Manual"]].describe().round(1)
        st.dataframe(summary, use_container_width=True)

    st.header("Results and Conclusion")
    st.write(
        "The comparison demonstrates the effectiveness of the AI-driven system:"
    )
    st.markdown(
        """
        - **Higher throughput**: The YOLO-based approach consistently shows higher
          total vehicle counts, indicating improved traffic flow.
        - **Adaptive timing**: Dynamic AI adjustments reduce congestion and optimize
          signal timings compared to the static manual approach.
        - **Scalability**: The system can be extended to multi-junction coordination
          and emergency vehicle prioritization.
        """
    )


# ── Footer ───────────────────────────────────────────────────────────────────
st.success("Dashboard loaded successfully!")
