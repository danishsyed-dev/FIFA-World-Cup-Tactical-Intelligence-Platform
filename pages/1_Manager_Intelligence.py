import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# Configure page
st.set_page_config(
    page_title="Manager Intelligence — World Cup Tactical Intelligence Platform",
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

/* Base resets */
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
    transition: transform 0.2s ease;
}

.insight-box:hover {
    transform: translateX(4px);
}

.percentile-label {
    font-size: 0.85rem;
    color: var(--text-primary);
    font-weight: 500;
    margin-bottom: 4px;
}

.percentile-num {
    font-family: 'Geist Mono', monospace;
    font-weight: 700;
    color: var(--accent-green);
}

/* Custom styled forms */
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

# Helper to load data
DATA_DIR = Path(__file__).resolve().parent.parent / "data"

@st.cache_data
def load_cached_data():
    p_file = DATA_DIR / "manager_profiles.csv"
    d_file = DATA_DIR / "tactical_dna.csv"
    s_file = DATA_DIR / "style_analysis.csv"
    
    if not (p_file.exists() and d_file.exists() and s_file.exists()):
        return None, None, None
        
    profiles = pd.read_csv(p_file)
    dna = pd.read_csv(d_file)
    style = pd.read_csv(s_file)
    return profiles, dna, style

profiles_df, dna_df, style_df = load_cached_data()

# ── Title ───────────────────────────────────────────────────────────
st.markdown(
    '<p class="hero-title">Manager Intelligence</p>',
    unsafe_allow_html=True,
)
st.markdown(
    '<p class="hero-sub">Explore and compare tactical signatures, playing style DNA, and adaptability indexes of World Cup managers.</p>',
    unsafe_allow_html=True,
)

if profiles_df is None:
    st.error("Database files not found. Please compile the database first by running: python -m src.generate_tactical_db")
else:
    # ── Sidebar selectors ───────────────────────────────────────────
    with st.sidebar:
        st.markdown("## Manager Profile Options")
        
        # Filter by World Cup
        wc_year = st.selectbox(
            "Filter Managers by Tournament",
            options=["All", "2018 & 2022", "2022 Only", "2018 Only"]
        )
        
        # Filter the profiles_df accordingly
        if wc_year == "2018 & 2022":
            avail_mgrs = profiles_df[profiles_df["category"] == "Category A"]["manager"].unique()
        elif wc_year == "2022 Only":
            avail_mgrs = profiles_df[(profiles_df["category"] == "Category B") & (profiles_df["world_cups"].astype(str).str.contains("2022"))]["manager"].unique()
        elif wc_year == "2018 Only":
            avail_mgrs = profiles_df[(profiles_df["category"] == "Category B") & (profiles_df["world_cups"].astype(str).str.contains("2018"))]["manager"].unique()
        else:
            avail_mgrs = profiles_df["manager"].unique()
            
        avail_mgrs = sorted(avail_mgrs)
        
        primary_mgr = st.selectbox(
            "Primary Manager",
            options=avail_mgrs,
            index=avail_mgrs.index("Didier Deschamps") if "Didier Deschamps" in avail_mgrs else 0
        )
        
        compare_mode = st.toggle("Compare Managers", value=False)
        
        compare_mgr = None
        if compare_mode:
            remaining_mgrs = [m for m in avail_mgrs if m != primary_mgr]
            compare_mgr = st.selectbox(
                "Compare With",
                options=remaining_mgrs,
                index=0 if remaining_mgrs else None
            )
            
        p_data = profiles_df[profiles_df["manager"] == primary_mgr].iloc[0]
        
        evolution_mode = False
        if p_data["category"] == "Category A" and not compare_mode:
            evolution_mode = st.toggle("Compare 2018 vs 2022 Evolution", value=False)

    # ── Load data for selected managers ─────────────────────────────
    style_mgr = style_df[style_df["manager"] == primary_mgr]
    
    dna_row = None
    dna_row_18 = None
    dna_row_22 = None
    
    if evolution_mode:
        row_18_query = dna_df[(dna_df["manager"] == primary_mgr) & (dna_df["year"] == "2018")]
        row_22_query = dna_df[(dna_df["manager"] == primary_mgr) & (dna_df["year"] == "2022")]
        dna_row_18 = row_18_query.iloc[0] if not row_18_query.empty else None
        dna_row_22 = row_22_query.iloc[0] if not row_22_query.empty else None
    else:
        row_query = dna_df[(dna_df["manager"] == primary_mgr) & (dna_df["year"] == "Overall")]
        dna_row = row_query.iloc[0] if not row_query.empty else dna_df[dna_df["manager"] == primary_mgr].iloc[0]
        
    c_data = None
    c_dna_row = None
    c_style_mgr = None
    if compare_mgr:
        c_data = profiles_df[profiles_df["manager"] == compare_mgr].iloc[0]
        c_row_query = dna_df[(dna_df["manager"] == compare_mgr) & (dna_df["year"] == "Overall")]
        c_dna_row = c_row_query.iloc[0] if not c_row_query.empty else dna_df[dna_df["manager"] == compare_mgr].iloc[0]
        c_style_mgr = style_df[style_df["manager"] == compare_mgr]

    # ── Metric Cards Row ────────────────────────────────────────────
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(
            f'<div class="metric-card">'
            f'<div class="label">Matches / Record</div>'
            f'<div class="value">{p_data["matches"]} <span style="font-size:1rem; color:var(--text-muted);">({p_data["wins"]}W-{p_data["draws"]}D-{p_data["losses"]}L)</span></div>'
            f'</div>',
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            f'<div class="metric-card">'
            f'<div class="label">Primary Formation</div>'
            f'<div class="value">{p_data["most_used_formation"]}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
    with col3:
        st.markdown(
            f'<div class="metric-card">'
            f'<div class="label">Tactical Shifts</div>'
            f'<div class="value">{p_data["tactical_shifts"]}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
    with col4:
        st.markdown(
            f'<div class="metric-card">'
            f'<div class="label">Stability index</div>'
            f'<div class="value">{p_data["formation_stability"] * 100:.0f}%</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    # ── Radar Chart and Profile Layout ──────────────────────────────
    c_left, c_right = st.columns([1, 1])
    
    with c_left:
        st.markdown('<div class="section-header">Tactical DNA Signature (Heuristic Score)</div>', unsafe_allow_html=True)
        
        # Radar Chart Plotting
        labels = [
            "Defensive\nAdaptability",
            "Attacking\nFlexibility",
            "Formation\nStability",
            "Press\nResistance",
            "Counter Attack\nUsage",
            "Tactical\nFlexibility"
        ]
        cols = [
            "defensive_adaptability",
            "attacking_flexibility",
            "formation_stability",
            "press_resistance",
            "counter_attack_usage",
            "tactical_flexibility"
        ]
        
        num_vars = len(labels)
        angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
        angles += angles[:1]
        
        fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
        fig.patch.set_facecolor("#09090b")
        ax.set_facecolor("#18181b")
        
        # Set category names
        plt.xticks(angles[:-1], labels, color="#a1a1aa", size=9, fontfamily='sans-serif')
        
        # Radar boundaries
        ax.set_rlabel_position(0)
        plt.yticks([20, 40, 60, 80, 100], ["20", "40", "60", "80", "100"], color="#64748b", size=7, fontfamily='sans-serif')
        plt.ylim(0, 100)
        
        # Custom grid lines
        ax.spines['polar'].set_color('#27272a')
        ax.grid(color='#27272a', linestyle='-', linewidth=0.8)
        
        # Plot manager shapes
        if evolution_mode and dna_row_18 is not None and dna_row_22 is not None:
            # 2018 DNA
            values1 = dna_row_18[cols].values.tolist()
            values1 += values1[:1]
            ax.plot(angles, values1, color="#10b981", linewidth=2, label="2018 DNA")
            ax.fill(angles, values1, color="#10b981", alpha=0.15)
            
            # 2022 DNA
            values2 = dna_row_22[cols].values.tolist()
            values2 += values2[:1]
            ax.plot(angles, values2, color="#f43f5e", linewidth=2, label="2022 DNA")
            ax.fill(angles, values2, color="#f43f5e", alpha=0.15)
        else:
            # Plot Manager 1 Overall
            values1 = dna_row[cols].values.tolist()
            values1 += values1[:1]
            ax.plot(angles, values1, color="#10b981", linewidth=2, label=primary_mgr)
            ax.fill(angles, values1, color="#10b981", alpha=0.15)
            
            # Plot Manager 2 if present
            if compare_mode and c_dna_row is not None:
                values2 = c_dna_row[cols].values.tolist()
                values2 += values2[:1]
                ax.plot(angles, values2, color="#f43f5e", linewidth=2, label=compare_mgr)
                ax.fill(angles, values2, color="#f43f5e", alpha=0.15)
            
        legend = ax.legend(loc="upper right", bbox_to_anchor=(1.25, 1.1), frameon=True)
        legend.get_frame().set_facecolor('#18181b')
        legend.get_frame().set_edgecolor('#27272a')
        for text in legend.get_texts():
            text.set_color('#f4f4f5')
            text.set_fontfamily('sans-serif')
            
        st.pyplot(fig)

    with c_right:
        st.markdown('<div class="section-header">Tactical Profile Details</div>', unsafe_allow_html=True)
        
        # Category A direct comparison (2018 vs 2022)
        if p_data["category"] == "Category A" and not compare_mode:
            if evolution_mode and dna_row_18 is not None and dna_row_22 is not None:
                st.markdown(f"### **{primary_mgr} — Tactical DNA Evolution (2018 vs 2022)**")
                st.markdown("Analysis of changes in tactical signature over the 4-year World Cup cycle:")
                
                evolution_records = []
                for label, col in zip(labels, cols):
                    v_18 = int(dna_row_18[col])
                    v_22 = int(dna_row_22[col])
                    diff = v_22 - v_18
                    sign = "+" if diff >= 0 else ""
                    evolution_records.append({
                        "Tactical Dimension": label.replace("\n", " "),
                        "2018 Score": v_18,
                        "2022 Score": v_22,
                        "Evolution Delta": f"{sign}{diff}"
                    })
                st.table(pd.DataFrame(evolution_records).set_index("Tactical Dimension"))
            else:
                st.markdown(f"### **{primary_mgr} — Direct 2018 vs 2022 Comparison**")
                st.markdown("This manager has coached in both the 2018 and 2022 World Cups. Below is a side-by-side comparison of their tactical profile across tournaments:")
                
                style_18 = style_mgr[style_mgr["year"] == 2018]
                style_22 = style_mgr[style_mgr["year"] == 2022]
                
                comp_records = []
                for yr, s_yr in [("2018", style_18), ("2022", style_22)]:
                    if not s_yr.empty:
                        m_form = s_yr["primary_formation"].mode().iloc[0] if not s_yr["primary_formation"].empty else "Unknown"
                        avg_pos = s_yr["possession_score"].mean()
                        low_b = s_yr["low_block_score"].mean()
                        high_p = s_yr["high_press_score"].mean()
                        shots_avg = s_yr["shots"].mean()
                        goals = s_yr["goals_scored"].sum()
                        conceded = s_yr["goals_conceded"].sum()
                        comp_records.append({
                            "Tournament": f"FIFA World Cup {yr}",
                            "Matches": len(s_yr),
                            "Record": f"{len(s_yr[s_yr['result'] == 'Win'])}W-{len(s_yr[s_yr['result'] == 'Draw'])}D-{len(s_yr[s_yr['result'] == 'Loss'])}L",
                            "Primary Formation": m_form,
                            "Avg Possession %": f"{avg_pos * 100:.1f}%",
                            "High Press Index": f"{high_p * 100:.0f}",
                            "Low Block Index": f"{low_b * 100:.0f}",
                            "Avg Shots": f"{shots_avg:.1f}",
                            "Goals Scored / Conceded": f"{goals} / {conceded}"
                        })
                        
                if comp_records:
                    st.table(pd.DataFrame(comp_records).set_index("Tournament"))
                else:
                    st.info("No comparative details found.")
                
        # Category B percentile ranks (single tournament)
        else:
            if not compare_mode:
                st.markdown(f"### **{primary_mgr} — Tournament Percentiles**")
                st.markdown("Category B manager (coached in a single tournament). Displaying tactical percentiles relative to all World Cup managers:")
                
                percentiles = [
                    ("Tactical Flexibility", p_data["flexibility_percentile"]),
                    ("Tactical Shift Frequency", p_data["shifts_percentile"]),
                    ("Formation Instability (Fluidity)", p_data["stability_percentile"]),
                    ("Adaptability Index", p_data["adaptability_percentile"]),
                ]
                
                for label, val in percentiles:
                    st.markdown(f'<div class="percentile-label">{label}: <span class="percentile-num">{val:.1f}th percentile</span></div>', unsafe_allow_html=True)
                    st.progress(float(val) / 100.0)
            else:
                # Comparison mode details
                st.markdown(f"### **Manager Comparison: {primary_mgr} vs {compare_mgr}**")
                
                comp_df = pd.DataFrame([
                    {
                        "Metric": "Tournament Category",
                        primary_mgr: p_data["category"],
                        compare_mgr: c_data["category"]
                    },
                    {
                        "Metric": "Total Matches",
                        primary_mgr: int(p_data["matches"]),
                        compare_mgr: int(c_data["matches"])
                    },
                    {
                        "Metric": "Wins / Draws / Losses",
                        primary_mgr: f"{p_data['wins']}W-{p_data['draws']}D-{p_data['losses']}L",
                        compare_mgr: f"{c_data['wins']}W-{c_data['draws']}D-{c_data['losses']}L"
                    },
                    {
                        "Metric": "Most Used Formation",
                        primary_mgr: p_data["most_used_formation"],
                        compare_mgr: c_data["most_used_formation"]
                    },
                    {
                        "Metric": "Total Tactical Shifts",
                        primary_mgr: int(p_data["tactical_shifts"]),
                        compare_mgr: int(c_data["tactical_shifts"])
                    },
                    {
                        "Metric": "Formation Stability Index",
                        primary_mgr: f"{p_data['formation_stability'] * 100:.1f}%",
                        compare_mgr: f"{c_data['formation_stability'] * 100:.1f}%"
                    },
                    {
                        "Metric": "Avg Formation Duration",
                        primary_mgr: f"{p_data['avg_formation_duration']:.1f} min",
                        compare_mgr: f"{c_data['avg_formation_duration']:.1f} min"
                    }
                ])
                st.table(comp_df.set_index("Metric"))

        # ── Automated Insights ──────────────────────────────────────────
        st.markdown('<div class="section-header">Tactical Insights & DNA Blueprint</div>', unsafe_allow_html=True)
        
        # Generator for primary manager
        insights1 = []
        
        if evolution_mode and dna_row_18 is not None and dna_row_22 is not None:
            c18 = int(dna_row_18["counter_attack_usage"])
            c22 = int(dna_row_22["counter_attack_usage"])
            insights1.append(
                f"<strong>Transition Evolution:</strong> In 2018, {primary_mgr}'s side registered a counter-attack usage score of <strong>{c18}/100</strong> "
                f"which adjusted to <strong>{c22}/100</strong> in 2022. This highlights an evolution "
                f"towards a {'more transitional' if c22 > c18 else 'more structured possession'} playstyle."
            )
            
            f18 = int(dna_row_18["tactical_flexibility"])
            f22 = int(dna_row_22["tactical_flexibility"])
            flex_diff = f22 - f18
            insights1.append(
                f"<strong>Flexibility Evolution:</strong> Tactical flexibility shifted by <strong>{flex_diff:+.0f} points</strong> between tournaments "
                f"(2018: {f18} ➔ 2022: {f22}). This indicates a "
                f"{'higher' if flex_diff > 0 else 'lower'} tendency to adjust structural lines and formations in their second tournament."
            )
        else:
            insights1.append(
                f"<strong>System Blueprint:</strong> {primary_mgr} deployed a <strong>{p_data['most_used_formation']}</strong> formation as the core shape, "
                f"retaining this structure for <strong>{p_data['formation_stability'] * 100:.1f}%</strong> of match duration."
            )
            if p_data["tactical_shifts"] > 0:
                insights1.append(
                    f"<strong>In-Game Management:</strong> Averaged <strong>{p_data['avg_formation_duration']:.1f} minutes</strong> between formation adjustments, "
                    f"initiating a total of <strong>{int(p_data['tactical_shifts'])} tactical shifts</strong>. Defensive adaptability registers at <strong>{dna_row['defensive_adaptability']:.0f}/100</strong>."
                )
            else:
                insights1.append(
                    f"<strong>Tactical Rigidity:</strong> Executed <strong>0 tactical shifts</strong> during the tournament, showing complete adherence to the starting shape."
                )
            
            styles_list = []
            for m_style in style_mgr["styles"].dropna().tolist():
                styles_list.extend([s.strip() for s in m_style.split(",") if s.strip()])
            if styles_list:
                top_style = pd.Series(styles_list).value_counts().index[0]
                insights1.append(
                    f"<strong>Style Footprint:</strong> The team's playing style was frequently classified as <strong>{top_style}</strong>. "
                    f"They exhibited a Counter Attack score of <strong>{dna_row['counter_attack_usage']:.0f}/100</strong> and a Press Resistance score of <strong>{dna_row['press_resistance']:.0f}/100</strong>."
                )
            
        for ins in insights1:
            st.markdown(f'<div class="insight-box">{ins}</div>', unsafe_allow_html=True)
            
        # Insights for compare manager if present
        if compare_mode and c_data is not None and c_dna_row is not None:
            st.markdown(f"#### **Comparison Insight: {compare_mgr}**")
            insights2 = []
            insights2.append(
                f"<strong>System Blueprint:</strong> Deployed a <strong>{c_data['most_used_formation']}</strong> formation as the core shape, "
                f"retaining it for <strong>{c_data['formation_stability'] * 100:.1f}%</strong> of match duration."
            )
            if c_data["tactical_shifts"] > 0:
                insights2.append(
                    f"<strong>In-Game Management:</strong> Averaged <strong>{c_data['avg_formation_duration']:.1f} minutes</strong> between formation adjustments, "
                    f"initiating a total of <strong>{int(c_data['tactical_shifts'])} tactical shifts</strong>. Defensive adaptability registers at <strong>{c_dna_row['defensive_adaptability']:.0f}/100</strong>."
                )
            for ins in insights2:
                st.markdown(f'<div class="insight-box" style="border-left-color: var(--accent-rose);">{ins}</div>', unsafe_allow_html=True)
