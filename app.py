"""
app.py — Tactical Formation Classifier Dashboard

A Streamlit application that visualises announced vs. actual formations
detected via K-Means clustering, tracks mid-game formation shifts with
a trained Random Forest classifier, and surfaces tactical insights.

Launch:  streamlit run app.py
"""

import sys
from pathlib import Path

# Ensure project root is on the path
sys.path.insert(0, str(Path(__file__).resolve().parent))

import json
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import LinearSegmentedColormap
import seaborn as sns
from mplsoccer import Pitch
import joblib

from src.data_loader import get_matches, get_events, match_label, WORLD_CUP_SEASONS
from src.features import (
    extract_tactical_timeline,
    rolling_formation_analysis,
    detect_formation_kmeans,
    collect_player_locations,
    build_feature_vector,
    CANONICAL_FORMATIONS,
)

# ── Page configuration ──────────────────────────────────────────────
st.set_page_config(
    page_title="Tactical Formation Classifier",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ──────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,500;0,9..40,700;1,9..40,400&family=Space+Grotesk:wght@400;600;700&display=swap');

:root {
    --bg-primary: #0a0f1a;
    --bg-card: #111827;
    --bg-elevated: #1a2332;
    --accent-green: #22c55e;
    --accent-amber: #f59e0b;
    --accent-rose: #f43f5e;
    --accent-sky: #38bdf8;
    --text-primary: #e2e8f0;
    --text-muted: #94a3b8;
    --border-subtle: #1e293b;
}

.stApp {
    background: var(--bg-primary) !important;
    font-family: 'DM Sans', sans-serif;
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
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 700;
    font-size: 2.4rem;
    letter-spacing: -0.03em;
    color: var(--text-primary);
    margin-bottom: 0;
    line-height: 1.1;
}

.hero-sub {
    font-size: 1rem;
    color: var(--text-muted);
    margin-top: 4px;
    margin-bottom: 2rem;
}

.metric-card {
    background: var(--bg-card);
    border: 1px solid var(--border-subtle);
    border-radius: 12px;
    padding: 1.2rem 1.4rem;
    text-align: center;
}

.metric-card .label {
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--text-muted);
    margin-bottom: 4px;
}

.metric-card .value {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.8rem;
    font-weight: 700;
    color: var(--text-primary);
}

.formation-badge {
    display: inline-block;
    padding: 6px 16px;
    border-radius: 8px;
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 700;
    font-size: 1.3rem;
    letter-spacing: 0.04em;
}

.badge-announced {
    background: rgba(56, 189, 248, 0.12);
    color: var(--accent-sky);
    border: 1px solid rgba(56, 189, 248, 0.25);
}

.badge-detected {
    background: rgba(34, 197, 94, 0.12);
    color: var(--accent-green);
    border: 1px solid rgba(34, 197, 94, 0.25);
}

.badge-mismatch {
    background: rgba(244, 63, 94, 0.12);
    color: var(--accent-rose);
    border: 1px solid rgba(244, 63, 94, 0.25);
}

.section-header {
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 600;
    font-size: 1.15rem;
    color: var(--text-primary);
    border-bottom: 2px solid var(--accent-green);
    padding-bottom: 6px;
    margin-top: 2rem;
    margin-bottom: 1rem;
    display: inline-block;
}

.insight-box {
    background: var(--bg-elevated);
    border-left: 3px solid var(--accent-amber);
    border-radius: 0 8px 8px 0;
    padding: 0.8rem 1.2rem;
    margin: 0.5rem 0;
    color: var(--text-primary);
    font-size: 0.9rem;
    line-height: 1.5;
}

.player-tag {
    display: inline-block;
    background: var(--bg-elevated);
    border: 1px solid var(--border-subtle);
    border-radius: 6px;
    padding: 3px 10px;
    margin: 2px 3px;
    font-size: 0.8rem;
    color: var(--text-primary);
}

div[data-testid="stMetric"] {
    background: var(--bg-card);
    border: 1px solid var(--border-subtle);
    border-radius: 12px;
    padding: 1rem;
}

div[data-testid="stMetric"] label {
    color: var(--text-muted) !important;
}

div[data-testid="stMetric"] [data-testid="stMetricValue"] {
    color: var(--text-primary) !important;
    font-family: 'Space Grotesk', sans-serif !important;
}
</style>
""", unsafe_allow_html=True)

# ── Colour palette for clusters ─────────────────────────────────────
CLUSTER_COLORS = {
    0: "#38bdf8",  # sky — defense
    1: "#f59e0b",  # amber — midfield
    2: "#22c55e",  # green — attack
}
CLUSTER_NAMES = {0: "Defense", 1: "Midfield", 2: "Attack"}


# ── Model loader ────────────────────────────────────────────────────
@st.cache_resource
def load_model():
    model_dir = Path(__file__).resolve().parent / "models"
    if not (model_dir / "formation_classifier.joblib").exists():
        return None, None, None, None
    clf = joblib.load(model_dir / "formation_classifier.joblib")
    le = joblib.load(model_dir / "label_encoder.joblib")
    feature_cols = joblib.load(model_dir / "feature_cols.joblib")
    with open(model_dir / "metadata.json") as f:
        meta = json.load(f)
    return clf, le, feature_cols, meta


# ── Match data loader ──────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def load_match_data(year: int):
    return get_matches(year)


@st.cache_data(show_spinner=False)
def load_events(match_id: int):
    return get_events(match_id)


PITCH_DISPLAY_NAMES = {
    # Portugal
    "Cristiano Ronaldo dos Santos Aveiro": "C. Ronaldo",
    "Cristiano Ronaldo": "C. Ronaldo",
    "Klépere Laveran Lima Ferreira": "Pepe",
    "Kléper Laveran Lima Ferreira": "Pepe",
    "Pepe": "Pepe",
    "Rúben Santos Gato Alves Dias": "R. Dias",
    "Ruben Dias": "R. Dias",
    "Bruno Miguel Borges Fernandes": "B. Fernandes",
    "Bruno Fernandes": "B. Fernandes",
    "Bernardo Mota Veiga de Carvalho e Silva": "B. Silva",
    "Bernardo Silva": "B. Silva",
    "João Félix Sequeira": "J. Félix",
    "Joao Felix": "J. Félix",
    "Rúben Diogo Da Silva Neves": "R. Neves",
    "Ruben Neves": "R. Neves",
    "João Pedro Cavaco Cancelo": "Cancelo",
    "Joao Cancelo": "Cancelo",
    "Raphaël Adelino José Guerreiro": "Guerreiro",
    "Raphaël Guerreiro": "Guerreiro",
    "Josá Diogo Dalot Teixeira": "Dalot",
    "José Diogo Dalot Teixeira": "Dalot",
    "Diogo Dalot": "Dalot",
    "Otávio Edmilson da Silva Monteiro": "Otávio",
    "Otávio": "Otávio",
    "Vitor Machado Ferreira": "Vitinha",
    "Vitinha": "Vitinha",
    "Diogo Meireles Costa": "Diogo Costa",
    "Diogo Costa": "Diogo Costa",
    "Ricardo Jorge Luz Horta": "Horta",
    "Ricardo Horta": "Horta",
    "Rafael Alexandre Conceição Leão": "R. Leão",
    "Rafael Alexandre Conceiço Leão": "R. Leão",
    "Rafael Leão": "R. Leão",
    "William Carvalho": "Carvalho",
    
    # Argentina
    "Lionel Andrés Messi Cuccittini": "Messi",
    "Lionel Messi": "Messi",
    "Ángel Fabián Di María Hernández": "Di María",
    "Ángel Di María": "Di María",
    "Emiliano Martínez Romero": "E. Martínez",
    "Emiliano Martínez": "E. Martínez",
    "Alexis Mac Allister": "Mac Allister",
    "Enzo Jeremías Fernández": "Enzo",
    "Rodrigo Javier De Paul": "De Paul",
    
    # Brazil
    "Neymar da Silva Santos Júnior": "Neymar Jr",
    "Thiago Emiliano da Silva": "Thiago Silva",
    "Marcos Aoás Corrêa": "Marquinhos",
    "Alisson Becker": "Alisson",
    "Gabriel Magalhaes": "G. Magalhães",
    "Bruno Guimaraes": "B. Guimarães",
    "Joao Gomes": "J. Gomes",
    "Lucas Paqueta": "Paquetá",
    "Vinicius Junior": "Vini Jr.",
    
    # Spain
    "Sergio Busquets i Burgos": "Busquets",
    "Jordi Alba Ramos": "Jordi Alba",
    "Gerard Piqué Bernabéu": "Piqué",
    "Sergio Ramos García": "S. Ramos",
    "José Ignacio Fernández Iglesias": "Nacho",
    "Jorge Resurrección Merodio": "Koke",
    "Andrés Iniesta Luján": "Iniesta",
    "Isco Alarcón Suárez": "Isco",
    "Marc Cucurella": "Cucurella",
    "Robin Le Normand": "Le Normand",
    "Dani Carvajal": "Carvajal",
    "Fabian Ruiz": "F. Ruiz",
    "Nico Williams": "N. Williams",
    "Lamine Yamal": "L. Yamal",
    "Alvaro Morata": "Morata",

    # Germany
    "Maximilian Mittelstadt": "Mittelstädt",
    "Antonio Rudiger": "Rüdiger",
    "Ilkay Gundogan": "Gündoğan",

    # Netherlands
    "Virgil van Dijk": "van Dijk",
    "Stefan de Vrij": "de Vrij",
    "Memphis Depay": "Memphis",

    # Belgium
    "Kevin De Bruyne": "De Bruyne",

    # Uruguay
    "Federico Valverde": "Valverde",
    "Darwin Nunez": "D. Núñez",
    "Luis Suarez": "L. Suárez",

    # South Africa
    "R. Williams": "Williams",
    "A. Modiba": "Modiba",
    "M. Mvala": "Mvala",
    "G. Kekana": "Kekana",
    "K. Mudau": "Mudau",
    "S. Sithole": "Sithole",
    "T. Mokoena": "Mokoena",
    "T. Zwane": "Zwane",
    "P. Tau": "Tau",
    "E. Makgopa": "Makgopa",
    "T. Morena": "Morena",
}

def get_short_name(player_name: str) -> str:
    """Return a clean short name for display on the pitch and lists."""
    player_name = player_name.strip()
    if player_name in PITCH_DISPLAY_NAMES:
        return PITCH_DISPLAY_NAMES[player_name]
    # Fallback to last word
    return player_name.split()[-1] if " " in player_name else player_name


# ── Pitch visualisation ────────────────────────────────────────────
def draw_formation_pitch(
    avg_positions: dict,
    kmeans_result: dict,
    team_name: str,
    announced: str,
    detected: str,
    title_suffix: str = "",
):
    """Draw a premium football pitch with player positions colour-coded."""
    fig, ax = plt.subplots(figsize=(10, 6.8))
    fig.patch.set_facecolor("#0a0f1a")
    ax.set_facecolor("#0a0f1a")

    pitch = Pitch(
        pitch_type="statsbomb",
        pitch_color="#0f1b2d",
        line_color="#1e3a5f",
        linewidth=1.2,
        goal_type="box",
    )
    pitch.draw(ax=ax)

    player_cluster = kmeans_result["player_cluster"]

    for player, (x, y) in avg_positions.items():
        cluster = player_cluster.get(player, 1)
        color = CLUSTER_COLORS[cluster]

        # Outer glow
        pitch.scatter(
            x, y, ax=ax, s=600, color=color, alpha=0.15, edgecolors="none",
        )
        # Main dot
        pitch.scatter(
            x, y, ax=ax, s=180, color=color, alpha=0.9,
            edgecolors="#0a0f1a", linewidths=1.5, zorder=5,
        )
        # Label
        short_name = get_short_name(player)
        if len(short_name) > 12:
            short_name = short_name[:11] + "."
        ax.text(
            x, y - 3.5, short_name,
            fontsize=7, fontweight=600, color="#e2e8f0",
            ha="center", va="top", zorder=6,
            fontfamily="sans-serif",
            bbox=dict(
                boxstyle="round,pad=0.15",
                facecolor="#0a0f1a",
                edgecolor="none",
                alpha=0.7,
            ),
        )

    # Legend
    legend_elements = [
        mpatches.Patch(facecolor=CLUSTER_COLORS[i], label=CLUSTER_NAMES[i])
        for i in range(3)
    ]
    ax.legend(
        handles=legend_elements,
        loc="upper right",
        fontsize=8,
        frameon=True,
        facecolor="#111827",
        edgecolor="#1e293b",
        labelcolor="#e2e8f0",
        borderpad=0.8,
    )

    # Title
    title = f"{team_name}{title_suffix}"
    ax.set_title(
        title,
        fontsize=13, fontweight=700, color="#e2e8f0",
        fontfamily="sans-serif", pad=12,
    )

    plt.tight_layout()
    return fig


# ── Rolling timeline chart ──────────────────────────────────────────
def draw_formation_timeline(
    windows: list[dict],
    team_name: str,
    clf=None,
    le=None,
    feature_cols=None,
):
    """Draw a timeline of formation probabilities across the match."""
    if not windows:
        return None

    fig, (ax_top, ax_bot) = plt.subplots(
        2, 1, figsize=(12, 6), height_ratios=[3, 1],
        sharex=True, gridspec_kw={"hspace": 0.08},
    )
    fig.patch.set_facecolor("#0a0f1a")

    for ax in (ax_top, ax_bot):
        ax.set_facecolor("#0f1b2d")
        ax.tick_params(colors="#94a3b8", labelsize=8)
        for spine in ax.spines.values():
            spine.set_color("#1e293b")

    minutes = [w["window_start"] + 5 for w in windows]
    detected = [w["detected_formation"] for w in windows]
    announced = [w["announced_formation"] for w in windows]

    # Top: classifier probabilities (if model available)
    if clf is not None and le is not None and feature_cols is not None:
        prob_data = {}
        for w in windows:
            feat = w["features"]
            if feat is None:
                continue
            X = np.array([[feat.get(c, 0) for c in feature_cols]])
            probs = clf.predict_proba(X)[0]
            for cls_idx, cls_name in enumerate(le.classes_):
                prob_data.setdefault(cls_name, []).append(probs[cls_idx])

        # Plot top-3 most common classes
        avg_probs = {k: np.mean(v) for k, v in prob_data.items()}
        top_classes = sorted(avg_probs, key=avg_probs.get, reverse=True)[:5]

        palette = ["#38bdf8", "#22c55e", "#f59e0b", "#f43f5e", "#a78bfa"]
        for i, cls in enumerate(top_classes):
            vals = prob_data[cls]
            mins = minutes[:len(vals)]
            ax_top.plot(
                mins, vals,
                color=palette[i % len(palette)],
                linewidth=2,
                alpha=0.85,
                label=cls,
            )
            ax_top.fill_between(mins, vals, alpha=0.08, color=palette[i % len(palette)])

        ax_top.set_ylabel("Probability", fontsize=9, color="#94a3b8")
        ax_top.set_ylim(-0.05, 1.05)
        ax_top.legend(
            fontsize=7.5, frameon=True,
            facecolor="#111827", edgecolor="#1e293b",
            labelcolor="#e2e8f0", loc="upper right", ncol=3,
        )
        ax_top.set_title(
            f"{team_name} — Formation Probability Over Time",
            fontsize=12, fontweight=700, color="#e2e8f0",
            fontfamily="sans-serif", pad=10,
        )
    else:
        ax_top.text(
            0.5, 0.5, "Train the model first to see\nformation probabilities",
            transform=ax_top.transAxes, ha="center", va="center",
            fontsize=11, color="#64748b", fontstyle="italic",
        )
        ax_top.set_title(
            f"{team_name} — Formation Timeline",
            fontsize=12, fontweight=700, color="#e2e8f0",
            fontfamily="sans-serif", pad=10,
        )

    # Bottom: detected formation (categorical bar)
    unique_formations = sorted(set(detected))
    formation_to_idx = {f: i for i, f in enumerate(unique_formations)}
    det_idx = [formation_to_idx[d] for d in detected]

    colors_timeline = []
    for d, a in zip(detected, announced):
        if d == a:
            colors_timeline.append("#22c55e")
        else:
            colors_timeline.append("#f43f5e")

    ax_bot.bar(minutes, [1] * len(minutes), width=4, color=colors_timeline, alpha=0.7)

    # Annotate detected formations
    for m, d in zip(minutes, detected):
        ax_bot.text(
            m, 0.5, d, ha="center", va="center",
            fontsize=6, color="#e2e8f0", fontweight=600, rotation=90,
        )

    ax_bot.set_ylabel("K-Means\nFormation", fontsize=8, color="#94a3b8")
    ax_bot.set_xlabel("Match Minute", fontsize=9, color="#94a3b8")
    ax_bot.set_yticks([])

    # Add match vs announce legend
    legend_items = [
        mpatches.Patch(facecolor="#22c55e", alpha=0.7, label="Matches Announced"),
        mpatches.Patch(facecolor="#f43f5e", alpha=0.7, label="Differs from Announced"),
    ]
    ax_bot.legend(
        handles=legend_items, fontsize=7, frameon=True,
        facecolor="#111827", edgecolor="#1e293b",
        labelcolor="#e2e8f0", loc="lower right",
    )

    plt.tight_layout()
    return fig


# ── Tactical insights ──────────────────────────────────────────────
def generate_insights(windows, timeline_entries, team):
    """Generate tactical insight strings."""
    insights = []

    if not windows:
        return insights

    # Count formation shifts
    formations_seen = [w["detected_formation"] for w in windows]
    unique_formations = set(formations_seen)
    if len(unique_formations) > 1:
        insights.append(
            f"**{team}** shifted between {len(unique_formations)} detected formations "
            f"during the match: {', '.join(sorted(unique_formations))}."
        )

    # Mismatch analysis
    mismatches = sum(
        1 for w in windows
        if w["detected_formation"] != w["announced_formation"]
    )
    match_pct = 100 * (1 - mismatches / len(windows)) if windows else 0
    if match_pct < 50:
        insights.append(
            f"The K-Means detected formation matched the announced formation "
            f"only **{match_pct:.0f}%** of the time — suggesting the team's "
            f"actual shape differed significantly from their announced lineup."
        )
    elif match_pct == 100:
        insights.append(
            f"The detected formation matched the announced formation in "
            f"**every window** — the team held their announced shape precisely."
        )

    # Formation shifts from tactical timeline
    shifts = [e for e in timeline_entries if e["event_type"] == "Tactical Shift"]
    if shifts:
        for s in shifts:
            insights.append(
                f"Tactical shift at **{s['minute']}'** → changed to **{s['formation']}**."
            )

    return insights


# ═══════════════════════════════════════════════════════════════════
#  MAIN APP
# ═══════════════════════════════════════════════════════════════════

def main():
    # ── Sidebar ─────────────────────────────────────────────────────
    with st.sidebar:
        st.markdown("## ⚽ Match Selector")

        year = st.selectbox(
            "World Cup",
            options=sorted(WORLD_CUP_SEASONS.keys(), reverse=True),
            format_func=lambda y: f"FIFA World Cup {y}",
        )

        with st.spinner("Loading matches…"):
            matches = load_match_data(year)

        # Extract available stages
        available_stages = []
        for m in matches:
            stage_name = m.get("competition_stage", {}).get("name")
            if stage_name == "Group Stage":
                if "Group Stage" not in available_stages:
                    available_stages.append("Group Stage")
            elif stage_name == "Round of 16":
                if "Round of 16" not in available_stages:
                    available_stages.append("Round of 16")
            elif stage_name in ("Quarter-finals", "Quarter-final", "Quarterfinals"):
                if "Quarter-finals" not in available_stages:
                    available_stages.append("Quarter-finals")
            elif stage_name in ("Semi-finals", "Semi-final", "Semifinals"):
                if "Semi-finals" not in available_stages:
                    available_stages.append("Semi-finals")
            elif stage_name in ("Final", "3rd Place Play-off", "3rd Place", "Third-place play-off"):
                if "Final / 3rd Place" not in available_stages:
                    available_stages.append("Final / 3rd Place")

        stage_order = ["Group Stage", "Round of 16", "Quarter-finals", "Semi-finals", "Final / 3rd Place"]
        display_stages = [s for s in stage_order if s in available_stages]

        filtered_matches = []
        if display_stages:
            stage_type = st.selectbox("Stage", display_stages)

            if stage_type == "Group Stage":
                # Find all unique groups
                groups = sorted(list(set(
                    m["home_team"]["home_team_group"]
                    for m in matches
                    if m.get("competition_stage", {}).get("name") == "Group Stage"
                    and m.get("home_team", {}).get("home_team_group") is not None
                )))
                if groups:
                    selected_group = st.selectbox(
                        "Group",
                        options=groups,
                        format_func=lambda g: f"Group {g}"
                    )
                    filtered_matches = [
                        m for m in matches
                        if m.get("competition_stage", {}).get("name") == "Group Stage"
                        and m.get("home_team", {}).get("home_team_group") == selected_group
                    ]
                else:
                    filtered_matches = [
                        m for m in matches
                        if m.get("competition_stage", {}).get("name") == "Group Stage"
                    ]
            elif stage_type == "Round of 16":
                filtered_matches = [
                    m for m in matches
                    if m.get("competition_stage", {}).get("name") == "Round of 16"
                ]
            elif stage_type == "Quarter-finals":
                filtered_matches = [
                    m for m in matches
                    if m.get("competition_stage", {}).get("name") in ("Quarter-finals", "Quarter-final", "Quarterfinals")
                ]
            elif stage_type == "Semi-finals":
                filtered_matches = [
                    m for m in matches
                    if m.get("competition_stage", {}).get("name") in ("Semi-finals", "Semi-final", "Semifinals")
                ]
            elif stage_type == "Final / 3rd Place":
                filtered_matches = [
                    m for m in matches
                    if m.get("competition_stage", {}).get("name") in ("Final", "3rd Place Play-off", "3rd Place", "Third-place play-off")
                ]
        else:
            filtered_matches = matches

        if filtered_matches:
            match_options = {
                match_label(m): m for m in sorted(
                    filtered_matches, key=lambda m: m.get("match_date", "")
                )
            }
            selected_label = st.selectbox("Match", list(match_options.keys()))
            match = match_options[selected_label]
        else:
            st.warning("No matches found for this stage.")
            return

        # Team selector
        home = match["home_team"]["home_team_name"]
        away = match["away_team"]["away_team_name"]
        team = st.radio("Team", [home, away], horizontal=True)

        st.markdown("---")
        st.markdown(
            f"**Date:** {match.get('match_date', 'N/A')}  \n"
            f"**Stage:** {match.get('competition_stage', {}).get('name', 'N/A')}  \n"
            f"**Stadium:** {match.get('stadium', {}).get('name', 'N/A')}"
        )

        st.markdown("---")
        st.markdown(
            "<p style='color:#64748b; font-size:0.75rem;'>"
            "Data: StatsBomb Open Data<br>"
            "Model: Random Forest (scikit-learn)"
            "</p>",
            unsafe_allow_html=True,
        )

    # ── Load data ───────────────────────────────────────────────────
    with st.spinner("Fetching match events…"):
        events = load_events(match["match_id"])

    timeline = extract_tactical_timeline(events)
    team_timeline = timeline.get(team, [])

    # Load model (might not exist yet)
    clf, le, feature_cols, model_meta = load_model()

    # ── Header ──────────────────────────────────────────────────────
    st.markdown(
        '<p class="hero-title">Tactical Formation Classifier</p>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<p class="hero-sub">'
        f'Analysing <strong>{team}</strong> in {selected_label} — '
        f'FIFA World Cup {year}</p>',
        unsafe_allow_html=True,
    )

    # ── Rolling analysis ────────────────────────────────────────────
    with st.spinner("Running formation analysis…"):
        windows = rolling_formation_analysis(events, team)

    if not windows:
        st.warning("Not enough positional data for this team in this match.")
        return

    # Render Time Window slider at the top
    st.markdown("### ⏱️ Select Time Window")
    window_labels = [f"{w['window_start']}′–{w['window_end']}′" for w in windows]
    # Default to the middle of the first half (or midpoint of match)
    first_half_windows = [w for w in windows if w["window_end"] <= 50]
    default_val = len(first_half_windows) // 2 if first_half_windows else 0
    sel_idx = st.select_slider(
        "Move the slider to analyze tactical shapes over different periods of the match:",
        options=list(range(len(windows))),
        format_func=lambda i: window_labels[i],
        value=default_val,
        key="window_slider",
    )
    viz_window = windows[sel_idx]

    # ── Metric cards ────────────────────────────────────────────────
    announced_f = viz_window["announced_formation"]
    detected_f = viz_window["detected_formation"]
    match_status = "✓ Match" if announced_f == detected_f else "✗ Mismatch"

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(
            f'<div class="metric-card">'
            f'<div class="label">Announced Formation</div>'
            f'<div class="value"><span class="formation-badge badge-announced">{announced_f}</span></div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    with col2:
        badge_cls = "badge-detected" if announced_f == detected_f else "badge-mismatch"
        st.markdown(
            f'<div class="metric-card">'
            f'<div class="label">K-Means Detected</div>'
            f'<div class="value"><span class="formation-badge {badge_cls}">{detected_f}</span></div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    with col3:
        n_shifts = sum(1 for e in team_timeline if e["event_type"] == "Tactical Shift")
        st.markdown(
            f'<div class="metric-card">'
            f'<div class="label">Tactical Shifts</div>'
            f'<div class="value">{n_shifts}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    with col4:
        if model_meta:
            acc = f"{model_meta['accuracy'] * 100:.1f}%"
        else:
            acc = "—"
        st.markdown(
            f'<div class="metric-card">'
            f'<div class="label">Classifier Accuracy</div>'
            f'<div class="value">{acc}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    # ── Pitch Visualisation ─────────────────────────────────────────
    st.markdown(
        '<p class="section-header">Average Player Positions & Detected Clusters</p>',
        unsafe_allow_html=True,
    )

    col_pitch, col_info = st.columns([3, 2])

    with col_pitch:
        fig = draw_formation_pitch(
            viz_window["avg_positions"],
            viz_window["kmeans_result"],
            team,
            announced_f,
            detected_f,
            title_suffix=f"  •  {viz_window['window_start']}′–{viz_window['window_end']}′",
        )
        st.pyplot(fig, width="stretch")
        plt.close(fig)

    with col_info:
        st.markdown("**Cluster Breakdown**")
        km = viz_window["kmeans_result"]
        for i in range(3):
            color_hex = CLUSTER_COLORS[i]
            players = km["clusters"][i]
            st.markdown(
                f"<div style='margin:8px 0;'>"
                f"<span style='display:inline-block;width:12px;height:12px;"
                f"background:{color_hex};border-radius:50%;margin-right:6px;"
                f"vertical-align:middle;'></span>"
                f"<strong style='color:{color_hex}'>{CLUSTER_NAMES[i]}</strong> "
                f"<span style='color:#94a3b8;'>({len(players)} players)</span>"
                f"</div>",
                unsafe_allow_html=True,
            )
            for p in sorted(players):
                short = get_short_name(p)
                pos = viz_window["avg_positions"][p]
                st.markdown(
                    f"<span class='player-tag'>{short} "
                    f"<span style='color:#64748b;font-size:0.7rem;'>"
                    f"({pos[0]:.0f}, {pos[1]:.0f})</span></span>",
                    unsafe_allow_html=True,
                )

        st.markdown("---")

        st.markdown("**Active Formation Summary**")
        st.markdown(
            f"During the **{viz_window['window_start']}′–{viz_window['window_end']}′** window:  \n"
            f"*   **Announced:** `{viz_window['announced_formation']}`  \n"
            f"*   **K-Means Detected:** `{viz_window['detected_formation']}`"
        )

    # ── Formation Timeline ──────────────────────────────────────────
    st.markdown(
        '<p class="section-header">Formation Shifts Over Time</p>',
        unsafe_allow_html=True,
    )

    fig_timeline = draw_formation_timeline(
        windows, team, clf, le, feature_cols,
    )
    if fig_timeline:
        st.pyplot(fig_timeline, width="stretch")
        plt.close(fig_timeline)

    # ── Tactical Insights ───────────────────────────────────────────
    st.markdown(
        '<p class="section-header">Tactical Insights</p>',
        unsafe_allow_html=True,
    )

    insights = generate_insights(windows, team_timeline, team)
    if insights:
        for insight in insights:
            st.markdown(
                f'<div class="insight-box">{insight}</div>',
                unsafe_allow_html=True,
            )
    else:
        st.info("No notable tactical shifts detected.")

    # ── All-windows data table ──────────────────────────────────────
    with st.expander("📊 Raw Window Data", expanded=False):
        table_data = []
        for w in windows:
            row = {
                "Window": f"{w['window_start']}′–{w['window_end']}′",
                "Announced": w["announced_formation"],
                "Detected (K-Means)": w["detected_formation"],
                "Match": "✓" if w["announced_formation"] == w["detected_formation"] else "✗",
            }
            if clf is not None and le is not None and feature_cols is not None:
                feat = w["features"]
                if feat:
                    X = np.array([[feat.get(c, 0) for c in feature_cols]])
                    pred = le.inverse_transform(clf.predict(X))[0]
                    row["Classifier Prediction"] = pred
            table_data.append(row)

        st.dataframe(
            pd.DataFrame(table_data),
            width="stretch",
            hide_index=True,
        )


if __name__ == "__main__":
    main()
