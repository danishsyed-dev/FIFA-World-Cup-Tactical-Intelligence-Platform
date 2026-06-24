import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from mplsoccer import Pitch
from pathlib import Path

# Configure page
st.set_page_config(
    page_title="Style Analysis — World Cup Tactical Intelligence Platform",
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
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.2), 0 4px 6px -2px rgba(0, 0, 0, 0.1);
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
from src.data_loader import get_matches, get_events, match_label, WORLD_CUP_SEASONS
from src.style_detector import detect_playing_styles

# ── Title ───────────────────────────────────────────────────────────
st.markdown(
    '<p class="hero-title">Style Analysis</p>',
    unsafe_allow_html=True,
)
st.markdown(
    '<p class="hero-sub">Trace possession dominance, defensive line coordinates, pressing intensity, and playing styles across match phases.</p>',
    unsafe_allow_html=True,
)

# ── Sidebar selectors ───────────────────────────────────────────
with st.sidebar:
    st.markdown("## Play Style Options")
    
    year = st.selectbox(
        "World Cup",
        options=sorted(WORLD_CUP_SEASONS.keys(), reverse=True),
        format_func=lambda y: f"FIFA World Cup {y}",
        key="style_year"
    )

    with st.spinner("Loading matches…"):
        matches = get_matches(year)

    match_options = {match_label(m): m for m in sorted(matches, key=lambda m: m.get("match_date", ""))}
    selected_label = st.selectbox("Match", list(match_options.keys()), key="style_match_sel")
    match = match_options[selected_label]

    home = match["home_team"]["home_team_name"]
    away = match["away_team"]["away_team_name"]
    team = st.radio("Team", [home, away], horizontal=True, key="style_team_sel")

# ── Fetch Match Events ──────────────────────────────────────────────
with st.spinner("Loading match events..."):
    events = get_events(match["match_id"])

if not events:
    st.warning("No events found for this match.")
else:
    # Extract defensive actions and pressing coordinates for the team
    defensive_x = []
    defensive_y = []
    pressure_x = []
    pressure_y = []
    
    for ev in events:
        ev_team = ev.get("team", {}).get("name", "")
        if ev_team != team:
            continue
            
        etype = ev.get("type", {}).get("name", "")
        loc = ev.get("location")
        if not loc or len(loc) < 2:
            continue
            
        is_defensive = False
        if etype in ("Pressure", "Interception", "Ball Recovery"):
            is_defensive = True
        elif etype == "Duel":
            dtype = ev.get("duel", {}).get("type", {}).get("name", "")
            if dtype == "Tackle":
                is_defensive = True
                
        if is_defensive:
            defensive_x.append(loc[0])
            defensive_y.append(loc[1])
            
        if etype == "Pressure":
            pressure_x.append(loc[0])
            pressure_y.append(loc[1])

    # ── Match Metrics Row ────────────────────────────────────────────
    # Run full match style detection
    full_match_style = detect_playing_styles(events, team, start_min=0, end_min=95)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(
            f'<div class="metric-card">'
            f'<div class="label">Possession Share</div>'
            f'<div class="value">{full_match_style["scores"]["possession_score"] * 100:.1f}%</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            f'<div class="metric-card">'
            f'<div class="label">Pressing Height</div>'
            f'<div class="value">{full_match_style["scores"]["average_pressure_x"]:.1f}m</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
    with col3:
        st.markdown(
            f'<div class="metric-card">'
            f'<div class="label">Counter Attacks</div>'
            f'<div class="value">{full_match_style["scores"]["counter_attack_count"]}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
    with col4:
        st.markdown(
            f'<div class="metric-card">'
            f'<div class="label">Primary Style</div>'
            f'<div class="value" style="font-size:1.4rem; padding-top:0.4rem;">{", ".join(full_match_style["styles"]) if full_match_style["styles"] else "Balanced"}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    # ── Columns Layout ──────────────────────────────────────────────
    c_left, c_right = st.columns([1, 1])

    with c_left:
        st.markdown('<div class="section-header">Defensive & Pressing Spatial Footprint</div>', unsafe_allow_html=True)
        
        event_type_filter = st.selectbox("Visualise Event Coordinates", ["Defensive Actions", "Pressure Actions"])
        
        # Pitch plotting
        pitch = Pitch(
            pitch_type="statsbomb",
            pitch_color="#18181b",
            line_color="#27272a",
            linewidth=1.2,
            goal_type="box",
        )
        fig, ax = pitch.draw(figsize=(8, 6))
        fig.patch.set_facecolor("#09090b")
        
        # Determine data to plot
        if event_type_filter == "Defensive Actions" and defensive_x:
            # Heatmap / Hexbin or Scatter
            pitch.hexbin(
                defensive_x, defensive_y, ax=ax,
                gridsize=15, cmap="Blues", mincnt=1, alpha=0.8
            )
            pitch.scatter(
                defensive_x, defensive_y, ax=ax,
                color="#38bdf8", edgecolors="#f4f4f5", s=40, alpha=0.8,
                label="Defensive Action"
            )
            ax.set_title(f"Defensive Action Coordinates — {team}", color="#f4f4f5", fontsize=11, fontfamily='sans-serif', pad=10)
        elif event_type_filter == "Pressure Actions" and pressure_x:
            pitch.hexbin(
                pressure_x, pressure_y, ax=ax,
                gridsize=15, cmap="YlOrBr", mincnt=1, alpha=0.8
            )
            pitch.scatter(
                pressure_x, pressure_y, ax=ax,
                color="#f59e0b", edgecolors="#f4f4f5", s=40, alpha=0.8,
                label="Pressure"
            )
            ax.set_title(f"Pressure Locations — {team}", color="#f4f4f5", fontsize=11, fontfamily='sans-serif', pad=10)
        else:
            ax.text(60, 40, "No positional actions recorded", color="#a1a1aa", ha="center", va="center")
            
        st.pyplot(fig)

    with c_right:
        st.markdown('<div class="section-header">Style Evolution Over Match Minutes</div>', unsafe_allow_html=True)
        
        # Calculate styles in 10-minute intervals
        intervals = [(i, i+10) for i in range(0, 80, 10)] + [(80, 95)]
        
        timeline_records = []
        for start, end in intervals:
            interval_style = detect_playing_styles(events, team, start_min=start, end_min=end)
            timeline_records.append({
                "Interval": f"{start}'–{end}'",
                "Possession %": interval_style["scores"]["possession_score"] * 100,
                "Press Height (X)": interval_style["scores"]["average_pressure_x"],
                "Low Block %": interval_style["scores"]["low_block_score"] * 100,
                "Mid Block %": interval_style["scores"]["mid_block_score"] * 100,
                "High Press %": interval_style["scores"]["high_press_score"] * 100,
                "Styles Detected": ", ".join(interval_style["styles"]) if interval_style["styles"] else "Balanced"
            })
            
        timeline_df = pd.DataFrame(timeline_records)
        
        # Let's plot block heights & possession trends over time
        fig_t, ax_t = plt.subplots(figsize=(8, 5.2))
        fig_t.patch.set_facecolor("#09090b")
        ax_t.set_facecolor("#18181b")
        
        x_ticks = timeline_df["Interval"]
        
        # Plot lines
        ax_t.plot(x_ticks, timeline_df["Possession %"], marker="o", color="#10b981", linewidth=2, label="Possession Share (%)")
        ax_t.plot(x_ticks, timeline_df["Press Height (X)"], marker="s", color="#38bdf8", linewidth=2, label="Pressing Line Height (m)")
        
        # Grid/ticks styling
        ax_t.set_xlabel("Match Phase", color="#a1a1aa", fontsize=9, fontfamily='sans-serif')
        ax_t.set_ylabel("Metric Value", color="#a1a1aa", fontsize=9, fontfamily='sans-serif')
        ax_t.tick_params(colors="#a1a1aa", labelsize=8)
        ax_t.spines['bottom'].set_color('#27272a')
        ax_t.spines['left'].set_color('#27272a')
        ax_t.spines['top'].set_visible(False)
        ax_t.spines['right'].set_visible(False)
        ax_t.grid(color='#27272a', linestyle='--', linewidth=0.5)
        
        legend_t = ax_t.legend(facecolor='#18181b', edgecolor='#27272a', labelcolor='#f4f4f5', loc="upper left")
        for text in legend_t.get_texts():
            text.set_fontfamily('sans-serif')
            
        plt.tight_layout()
        st.pyplot(fig_t)
        
        st.markdown("#### **Phase-by-Phase Style Breakdown**")
        st.dataframe(
            timeline_df[["Interval", "Possession %", "Press Height (X)", "Styles Detected"]].rename(
                columns={
                    "Possession %": "Possession (%)",
                    "Press Height (X)": "Pressing Height",
                    "Styles Detected": "Tactical Style Profile"
                }
            ),
            use_container_width=True,
            hide_index=True
        )

    # ── Narrative Analysis ──────────────────────────────────────────
    st.markdown('<div class="section-header">Tactical Style Narrative</div>', unsafe_allow_html=True)
    
    narratives = []
    
    # 1. Block profile
    low_b_avg = full_match_style["scores"]["low_block_score"] * 100
    mid_b_avg = full_match_style["scores"]["mid_block_score"] * 100
    if low_b_avg > 50:
        narratives.append(
            f"<strong>Defensive Organization:</strong> {team} operated in a deep defensive structure, with <strong>{low_b_avg:.0f}%</strong> of their defensive actions "
            f"occurring inside their own defensive third. This indicates a commitment to a <strong>Low Block</strong> block shape."
        )
    elif mid_b_avg > 50:
        narratives.append(
            f"<strong>Defensive Organization:</strong> {team} maintained a medium defensive line, with <strong>{mid_b_avg:.0f}%</strong> of defensive activity concentrated "
            f"in the middle third, indicating a structured <strong>Mid Block</strong> approach."
        )
    else:
        narratives.append(
            f"<strong>Defensive Organization:</strong> {team} defended actively across all zones, refusing to settle into a static low or mid block shape."
        )
        
    # 2. Pressing profile
    avg_x = full_match_style["scores"]["average_pressure_x"]
    high_p_rate = full_match_style["scores"]["high_press_score"] * 100
    if avg_x > 70 or high_p_rate > 40:
        narratives.append(
            f"<strong>Pressing Intensity:</strong> Exhibited a proactive pressing profile. Average pressure coordinates registered at <strong>{avg_x:.1f} meters</strong> "
            f"up the field, with <strong>{high_p_rate:.0f}%</strong> of all press actions initiated in the opponent third (High Press classification)."
        )
    else:
        narratives.append(
            f"<strong>Pressing Intensity:</strong> Opted for a passive defensive stance. Average pressure coordinates registered at <strong>{avg_x:.1f} meters</strong>, "
            f"allowing the opponent comfortable build-up in their own half."
        )
        
    # 3. Transitions
    counters = full_match_style["scores"]["counter_attack_count"]
    if counters >= 2:
        narratives.append(
            f"<strong>Transition Threat:</strong> Highly dangerous on turnovers. Successfully launched <strong>{counters} rapid counter-attacks</strong> "
            f"transitioning from their own half to an attacking shot inside 20 seconds."
        )
        
    # Display narratives
    for text in narratives:
        st.markdown(f'<div class="insight-box">{text}</div>', unsafe_allow_html=True)
