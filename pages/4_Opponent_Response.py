import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# Configure page
st.set_page_config(
    page_title="Opponent Response — World Cup Tactical Intelligence Platform",
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
from src.opponent_response import calculate_style_effectiveness

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

@st.cache_data
def load_opponent_responses():
    r_file = DATA_DIR / "opponent_responses.csv"
    if not r_file.exists():
        return None
    return pd.read_csv(r_file)

responses_df = load_opponent_responses()

# ── Title ───────────────────────────────────────────────────────────
st.markdown(
    '<p class="hero-title">Opponent Response Profiler</p>',
    unsafe_allow_html=True,
)
st.markdown(
    '<p class="hero-sub">Trace how managers adapt shapes against distinct tactical play styles, mapping out success rates and goal shares.</p>',
    unsafe_allow_html=True,
)

if responses_df is None:
    st.error("Database files not found. Please compile the database first by running: python -m src.generate_tactical_db")
else:
    # ── Sidebar selectors ───────────────────────────────────────────
    with st.sidebar:
        st.markdown("## Response Options")
        
        # Select Manager
        available_managers = sorted(responses_df["manager"].unique())
        selected_manager = st.selectbox(
            "Select Manager",
            options=available_managers,
            index=available_managers.index("Didier Deschamps") if "Didier Deschamps" in available_managers else 0
        )
        
        # Filter responses to selected manager
        mgr_responses = responses_df[responses_df["manager"] == selected_manager].copy()

    # ── Summary Metrics for Manager ─────────────────────────────────
    effectiveness = calculate_style_effectiveness(responses_df, selected_manager)
    
    # Render overall metrics
    total_opponent_styles = len(effectiveness)
    best_opponent_style = "N/A"
    best_win_rate = 0.0
    if not effectiveness.empty:
        best_row = effectiveness.sort_values(by="win_rate", ascending=False).iloc[0]
        best_opponent_style = best_row["opponent_style"]
        best_win_rate = best_row["win_rate"] * 100

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(
            f'<div class="metric-card">'
            f'<div class="label">Opponent Styles Faced</div>'
            f'<div class="value">{total_opponent_styles}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            f'<div class="metric-card">'
            f'<div class="label">Best Style Matchup</div>'
            f'<div class="value" style="font-size:1.5rem; padding-top:0.3rem;">{best_opponent_style}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
    with col3:
        st.markdown(
            f'<div class="metric-card">'
            f'<div class="label">Best Style Win Rate</div>'
            f'<div class="value">{best_win_rate:.0f}%</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
    with col4:
        # Average goals scored overall in database
        avg_goals = mgr_responses["goals_scored"].mean()
        st.markdown(
            f'<div class="metric-card">'
            f'<div class="label">Avg Goals Scored</div>'
            f'<div class="value">{avg_goals:.2f}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    # ── Columns Layout ──────────────────────────────────────────────
    c_left, c_right = st.columns([1, 1])

    with c_left:
        st.markdown('<div class="section-header">Match Record by Opponent Playstyle</div>', unsafe_allow_html=True)
        
        if not effectiveness.empty:
            # Horizontal stacked bar chart of outcomes: Win, Draw, Loss
            fig, ax = plt.subplots(figsize=(7, 5))
            fig.patch.set_facecolor("#09090b")
            ax.set_facecolor("#18181b")
            
            categories = effectiveness["opponent_style"].tolist()
            wins = (effectiveness["win_rate"] * 100).tolist()
            draws = (effectiveness["draw_rate"] * 100).tolist()
            losses = (effectiveness["loss_rate"] * 100).tolist()
            
            y_pos = np.arange(len(categories))
            
            # Plot stacked horizontal bars
            bar_width = 0.55
            ax.barh(y_pos, wins, bar_width, label="Win", color="#10b981", alpha=0.9)
            ax.barh(y_pos, draws, bar_width, left=wins, label="Draw", color="#71717a", alpha=0.9)
            ax.barh(y_pos, [l_val for l_val in losses], bar_width, left=[w + d for w, d in zip(wins, draws)], label="Loss", color="#f43f5e", alpha=0.9)
            
            # Formatting
            ax.set_yticks(y_pos)
            ax.set_yticklabels(categories, color="#f4f4f5", fontsize=9, fontfamily='sans-serif')
            ax.set_xlabel("Match Outcome Distribution (%)", color="#a1a1aa", fontsize=9, fontfamily='sans-serif')
            ax.tick_params(colors="#a1a1aa", labelsize=8)
            ax.spines['bottom'].set_color('#27272a')
            ax.spines['left'].set_color('#27272a')
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.set_xlim(0, 100)
            
            legend = ax.legend(loc="lower right", facecolor='#18181b', edgecolor='#27272a', labelcolor='#f4f4f5')
            for text in legend.get_texts():
                text.set_fontfamily('sans-serif')
                
            plt.tight_layout()
            st.pyplot(fig)
            
            st.dataframe(
                effectiveness.rename(
                    columns={
                        "opponent_style": "Opponent Style",
                        "matches": "Matches",
                        "win_rate": "Win Rate",
                        "avg_goals_scored": "Avg Goals For",
                        "avg_goals_conceded": "Avg Goals Against"
                    }
                )[["Opponent Style", "Matches", "Win Rate", "Avg Goals For", "Avg Goals Against"]].style.format(
                    {
                        "Win Rate": "{:.1%}",
                        "Avg Goals For": "{:.2f}",
                        "Avg Goals Against": "{:.2f}"
                    }
                ),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("No opponent style statistics found.")

    with c_right:
        st.markdown('<div class="section-header">Tactical Response (Formation Deployment)</div>', unsafe_allow_html=True)
        
        # Calculate most deployed formations against different opponent styles
        deployment = mgr_responses.groupby(["opponent_style", "formation_used"]).size().reset_index(name="count")
        
        if not deployment.empty:
            # Let's pivot or filter
            style_filter = st.selectbox(
                "Filter Formations by Opponent Playstyle",
                options=sorted(deployment["opponent_style"].unique())
            )
            
            deployment_filtered = deployment[deployment["opponent_style"] == style_filter].sort_values(by="count", ascending=False)
            
            # Simple bar chart of formations
            fig_f, ax_f = plt.subplots(figsize=(7, 5.2))
            fig_f.patch.set_facecolor("#09090b")
            ax_f.set_facecolor("#18181b")
            
            forms = deployment_filtered["formation_used"].tolist()
            counts = deployment_filtered["count"].tolist()
            
            y_pos_f = np.arange(len(forms))
            
            ax_f.barh(y_pos_f, counts, color="#38bdf8", height=0.5)
            ax_f.set_yticks(y_pos_f)
            ax_f.set_yticklabels(forms, color="#f4f4f5", fontsize=9, fontfamily='sans-serif')
            ax_f.set_xlabel("Deployment Frequency (Matches)", color="#a1a1aa", fontsize=9, fontfamily='sans-serif')
            ax_f.tick_params(colors="#a1a1aa", labelsize=8)
            ax_f.spines['bottom'].set_color('#27272a')
            ax_f.spines['left'].set_color('#27272a')
            ax_f.spines['top'].set_visible(False)
            ax_f.spines['right'].set_visible(False)
            
            # Force integer ticks on x-axis
            import matplotlib.ticker as ticker
            ax_f.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))
            
            plt.tight_layout()
            st.pyplot(fig_f)
            
            # Highlight favorite responses
            fav_formation = deployment_filtered.iloc[0]["formation_used"]
            fav_count = deployment_filtered.iloc[0]["count"]
            st.markdown(
                f'<div class="insight-box" style="border-left-color: var(--accent-green);">'
                f"Facing a <strong>{style_filter}</strong> shape, {selected_manager}'s go-to formation was the "
                f"<strong>{fav_formation}</strong>, deploying it in <strong>{fav_count}</strong> matches."
                f"</div>",
                unsafe_allow_html=True
            )
        else:
            st.info("No formation deployment data recorded.")

    # ── Matchup Profiles & Insights ─────────────────────────────────
    st.markdown('<div class="section-header">Opponent Matchup Profile Insights</div>', unsafe_allow_html=True)
    
    insights = []
    
    # Parse effectiveness for interesting facts
    for idx, row in effectiveness.iterrows():
        style = row["opponent_style"]
        win_pct = row["win_rate"] * 100
        avg_gf = row["avg_goals_scored"]
        avg_ga = row["avg_goals_conceded"]
        
        if win_pct >= 65:
            insights.append(
                f"<strong>Elite Performance:</strong> Highly effective facing <strong>{style}</strong> systems, registering a <strong>{win_pct:.0f}%</strong> win rate "
                f"and maintaining a strong +{(avg_gf - avg_ga):.2f} average goal difference per match."
            )
        elif win_pct <= 35:
            insights.append(
                f"<strong>Tactical Vulnerability:</strong> Struggles when matched against <strong>{style}</strong> systems, securing a win in only "
                f"<strong>{win_pct:.0f}%</strong> of matchups, conceding an average of <strong>{avg_ga:.2f}</strong> goals."
            )
            
    # Add a fallback insight if empty
    if not insights:
        insights.append(
            f"<strong>Balanced Blueprint:</strong> Deployed consistent tactical answers across opponent archetypes, demonstrating a balanced "
            f"win share and goal difference profile regardless of opponent style."
        )
        
    for text in insights:
        st.markdown(f'<div class="insight-box">{text}</div>', unsafe_allow_html=True)
