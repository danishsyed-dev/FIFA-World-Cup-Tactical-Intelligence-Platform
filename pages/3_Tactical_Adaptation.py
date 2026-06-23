import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt

# Configure page
st.set_page_config(
    page_title="Tactical Adaptation — World Cup Tactical Intelligence Platform",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for dark theme matching main app
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Geist:wght@300;400;500;600;700&family=Geist+Mono:wght@300;400;500;600;700&display=swap');

:root {
    --bg-primary: #09090b;
    --bg-card: #18181b;
    --bg-elevated: #27272a;
    --accent-green: #10b981;
    --accent-emerald-muted: rgba(16, 185, 129, 0.1);
    --accent-rose: #f43f5e;
    --text-primary: #f4f4f5;
    --text-muted: #a1a1aa;
    --border-subtle: #27272a;
}

.stApp {
    background: var(--bg-primary) !important;
    font-family: 'Geist', sans-serif;
}

[data-testid="stSidebar"] {
    background: var(--bg-card) !important;
    border-right: 1px solid var(--border-subtle);
}

[data-testid="stSidebar"] .stMarkdown h1,
[data-testid="stSidebar"] .stMarkdown h2,
[data-testid="stSidebar"] .stMarkdown h3,
[data-testid="stSidebar"] .stMarkdown p,
[data-testid="stSidebar"] .stMarkdown label {
    color: var(--text-primary) !important;
}

.hero-title {
    font-family: 'Geist', sans-serif;
    font-weight: 700;
    font-size: 2.5rem;
    letter-spacing: -0.04em;
    color: var(--text-primary);
    margin-bottom: 0;
    line-height: 1.1;
}

.hero-sub {
    font-size: 1rem;
    color: var(--text-muted);
    margin-top: 6px;
    margin-bottom: 2rem;
}

.section-header {
    font-family: 'Geist', sans-serif;
    font-weight: 600;
    font-size: 1.3rem;
    letter-spacing: -0.02em;
    color: var(--text-primary);
    border-bottom: 1px solid var(--border-subtle);
    padding-bottom: 8px;
    margin-top: 2rem;
    margin-bottom: 1.5rem;
    width: 100%;
}

.metric-card {
    background: var(--bg-card);
    border: 1px solid var(--border-subtle);
    border-radius: 16px;
    padding: 1.5rem;
    text-align: left;
    transition: transform 0.2s cubic-bezier(0.25, 1, 0.5, 1), border-color 0.2s ease, box-shadow 0.2s ease;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
}

.metric-card:hover {
    transform: translateY(-2px);
    border-color: var(--accent-green);
}

.metric-card .label {
    font-size: 0.75rem;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: var(--text-muted);
    margin-bottom: 8px;
}

.metric-card .value {
    font-family: 'Geist Mono', monospace;
    font-size: 2rem;
    font-weight: 700;
    color: var(--text-primary);
}

.insight-box {
    background: var(--bg-card);
    border: 1px solid var(--border-subtle);
    border-left: 4px solid var(--accent-green);
    border-radius: 8px;
    padding: 1.2rem;
    margin: 0.8rem 0;
    color: var(--text-primary);
    font-size: 0.95rem;
    line-height: 1.6;
}

.comparison-grid {
    display: grid;
    grid-template-columns: 2fr 1fr 2fr;
    gap: 1rem;
    align-items: center;
    background: var(--bg-card);
    border: 1px solid var(--border-subtle);
    border-radius: 12px;
    padding: 1.2rem;
    margin-bottom: 1rem;
}

.grid-side {
    text-align: center;
}

.grid-metric-name {
    text-align: center;
    font-size: 0.85rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: var(--text-muted);
}

.grid-val {
    font-family: 'Geist Mono', monospace;
    font-size: 1.6rem;
    font-weight: 700;
    color: var(--text-primary);
}

.stSelectbox div[data-baseweb="select"] {
    background-color: var(--bg-card) !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: 8px !important;
}
.stSelectbox div[role="button"] {
    color: var(--text-primary) !important;
}
[data-testid="stWidgetLabel"] p {
    color: var(--text-muted) !important;
    font-size: 0.85rem !important;
    font-weight: 500 !important;
}
</style>
""", unsafe_allow_html=True)

# Helper imports from src
from src.data_loader import get_events
from src.adaptation_analyzer import analyze_tactical_shift

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

@st.cache_data
def load_shifts_data():
    s_file = DATA_DIR / "tactical_shifts.csv"
    if not s_file.exists():
        return None
    return pd.read_csv(s_file)

shifts_df = load_shifts_data()

# ── Title ───────────────────────────────────────────────────────────
st.markdown(
    '<p class="hero-title">Tactical Adaptation Analysis</p>',
    unsafe_allow_html=True,
)
st.markdown(
    '<p class="hero-sub">Evaluate the efficacy of in-game formation changes by contrasting team performance metrics before and after the shift.</p>',
    unsafe_allow_html=True,
)

if shifts_df is None:
    st.error("Database files not found. Please compile the database first by running: python -m src.generate_tactical_db")
else:
    # ── Sidebar selectors ───────────────────────────────────────────
    with st.sidebar:
        st.markdown("## Adaptation Options")
        
        # Select Manager
        available_managers = sorted(shifts_df["manager"].unique())
        selected_manager = st.selectbox(
            "Select Manager",
            options=available_managers,
            index=available_managers.index("Didier Deschamps") if "Didier Deschamps" in available_managers else 0
        )
        
        # Filter shifts to selected manager
        mgr_shifts = shifts_df[shifts_df["manager"] == selected_manager].copy()
        
        # Create descriptive select label for shifts
        mgr_shifts["shift_label"] = (
            mgr_shifts["opponent"] + " (" + mgr_shifts["minute"].astype(str) + "') — " +
            mgr_shifts["formation_before"] + " ➔ " + mgr_shifts["formation_after"]
        )
        
        shift_options = dict(zip(mgr_shifts["shift_label"], mgr_shifts.index))
        
        selected_shift_label = st.selectbox(
            "Choose Tactical Shift",
            options=list(shift_options.keys())
        )

    # ── Summary Metrics for Manager ─────────────────────────────────
    total_mgr_shifts = len(mgr_shifts)
    success_shifts = len(mgr_shifts[mgr_shifts["classification"] == "Successful"])
    success_pct = (success_shifts / total_mgr_shifts * 100) if total_mgr_shifts > 0 else 0.0
    avg_adaptation_score = mgr_shifts["adaptation_score"].mean()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(
            f'<div class="metric-card">'
            f'<div class="label">Total Shifts Executed</div>'
            f'<div class="value">{total_mgr_shifts}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            f'<div class="metric-card">'
            f'<div class="label">Success Rate</div>'
            f'<div class="value">{success_pct:.1f}%</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
    with col3:
        st.markdown(
            f'<div class="metric-card">'
            f'<div class="label">Avg adaptation Score</div>'
            f'<div class="value">{avg_adaptation_score:.1f}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
    with col4:
        st.markdown(
            f'<div class="metric-card">'
            f'<div class="label">Primary Transition</div>'
            f'<div class="value" style="font-size:1.4rem; padding-top:0.4rem;">'
            f'{mgr_shifts["formation_before"].mode().iloc[0] if not mgr_shifts["formation_before"].empty else "—"} ➔ '
            f'{mgr_shifts["formation_after"].mode().iloc[0] if not mgr_shifts["formation_after"].empty else "—"}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    # ── Details of selected shift ───────────────────────────────────
    st.markdown('<div class="section-header">Tactical Shift Details & Performance Comparison</div>', unsafe_allow_html=True)
    
    if selected_shift_label:
        shift_idx = shift_options[selected_shift_label]
        shift_row = mgr_shifts.loc[shift_idx]
        
        # Load events for that specific match to perform live detailed analysis (incl. entries and pressures)
        with st.spinner("Analyzing shift context and loading metrics..."):
            try:
                events = get_events(int(shift_row["match_id"]))
                live_analysis = analyze_tactical_shift(
                    events,
                    team=shift_row["team"],
                    shift_minute=float(shift_row["minute"]),
                    formation_before=shift_row["formation_before"],
                    formation_after=shift_row["formation_after"]
                )
            except Exception as e:
                live_analysis = None
                
        # If live analysis succeeded, show the fully expanded before/after comparison
        if live_analysis:
            before = live_analysis["before"]
            after = live_analysis["after"]
            
            # Helper function for rendering metric comparison rows
            def render_comparison_row(name, val_b, val_a, format_str="{}", higher_is_better=True):
                diff = val_a - val_b
                sign = "+" if diff >= 0 else ""
                
                # Determine text color based on metric success
                is_positive_change = diff > 0 if higher_is_better else diff < 0
                if diff == 0:
                    diff_style = "color: var(--text-muted);"
                elif is_positive_change:
                    diff_style = "color: var(--accent-green);"
                else:
                    diff_style = "color: var(--accent-rose);"
                    
                st.markdown(f"""
                <div class="comparison-grid">
                    <div class="grid-side">
                        <div class="grid-val">{format_str.format(val_b)}</div>
                    </div>
                    <div>
                        <div class="grid-metric-name">{name}</div>
                        <div style="text-align: center; font-size: 0.8rem; font-weight: 600; {diff_style}">
                            {sign}{format_str.format(diff)}
                        </div>
                    </div>
                    <div class="grid-side">
                        <div class="grid-val">{format_str.format(val_a)}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            c_left, c_right = st.columns([1, 1])
            
            with c_left:
                st.markdown("#### **Attacking & Possession Metrics (10m window)**")
                render_comparison_row("Possession Share", before["possession_pct"] * 100, after["possession_pct"] * 100, "{:.1f}%")
                render_comparison_row("Shots Attempted", before["shots"], after["shots"], "{:d}")
                render_comparison_row("Expected Goals (xG)", before["xg"], after["xg"], "{:.2f}")
                render_comparison_row("Final Third Entries", before["final_third_entries"], after["final_third_entries"], "{:d}")
                
            with c_right:
                st.markdown("#### **Defensive & Opponent Metrics (10m window)**")
                render_comparison_row("Shots Conceded", before["shots_conceded"], after["shots_conceded"], "{:d}", higher_is_better=False)
                render_comparison_row("xG Conceded", before["xg_conceded"], after["xg_conceded"], "{:.2f}", higher_is_better=False)
                render_comparison_row("Pressures Executed", before["pressures"], after["pressures"], "{:d}")
                
                # Success Badge
                class_color = "var(--accent-green)" if live_analysis["classification"] == "Successful" else ("var(--accent-rose)" if live_analysis["classification"] == "Unsuccessful" else "var(--text-muted)")
                st.markdown(f"""
                <div style="background: var(--bg-card); border: 1px solid var(--border-subtle); border-radius: 12px; padding: 1.2rem; text-align: center;">
                    <div class="label" style="margin-bottom: 4px;">Shift Classification</div>
                    <div style="font-size: 1.8rem; font-weight: 700; color: {class_color};">{live_analysis["classification"].upper()}</div>
                    <div class="label" style="margin-top: 12px; margin-bottom: 4px;">Adaptation Score</div>
                    <div style="font-family: 'Geist Mono', monospace; font-size: 2.2rem; font-weight: 800; color: var(--text-primary);">{live_analysis["adaptation_score"]}</div>
                </div>
                """, unsafe_allow_html=True)
                
            # Narrative insight box
            st.markdown('<div class="section-header">Tactical Adaptation Insight</div>', unsafe_allow_html=True)
            
            narrative = (
                f"<strong>Manager Decision:</strong> At the <strong>{shift_row['minute']:.0f}th minute</strong>, {selected_manager} shifted the team shape from "
                f"<strong>{shift_row['formation_before']}</strong> to <strong>{shift_row['formation_after']}</strong> against {shift_row['opponent']}.<br><br>"
            )
            
            possession_diff = (after["possession_pct"] - before["possession_pct"]) * 100
            shots_diff = after["shots"] - before["shots"]
            conceded_diff = after["shots_conceded"] - before["shots_conceded"]
            
            narrative += "<strong>Impact Assessment:</strong> "
            if live_analysis["classification"] == "Successful":
                narrative += f"The shift was highly successful. "
                if possession_diff > 5:
                    narrative += f"The team reclaimed control of the tempo, increasing possession share by <strong>{possession_diff:.1f}%</strong>. "
                if shots_diff > 0 or conceded_diff < 0:
                    narrative += f"Attacking output improved by <strong>{shots_diff}</strong> shots while limiting the opponent to <strong>{conceded_diff}</strong> shots."
            elif live_analysis["classification"] == "Unsuccessful":
                narrative += f"The modification backfired. "
                if conceded_diff > 0:
                    narrative += f"Opponent attacking momentum surged, resulting in <strong>{conceded_diff}</strong> more shots conceded after the shape change."
                if possession_diff < -5:
                    narrative += f"Control of the midfield was lost, with possession share dropping by <strong>{-possession_diff:.1f}%</strong>."
            else:
                narrative += "The change resulted in a balanced, neutral impact, stabilizing play without shifting the match momentum significantly."
                
            st.markdown(f'<div class="insight-box">{narrative}</div>', unsafe_allow_html=True)
            
        else:
            st.info("Could not perform live analysis of the shift events. Displaying cached overview metrics:")
            st.write(shift_row)
