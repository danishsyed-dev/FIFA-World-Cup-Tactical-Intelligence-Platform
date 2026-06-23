import streamlit as st

# Configure page
st.set_page_config(
    page_title="Methodology — World Cup Tactical Intelligence Platform",
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

.methodology-card {
    background: var(--bg-card);
    border: 1px solid var(--border-subtle);
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 1.5rem;
    color: var(--text-primary);
}

.methodology-card h3 {
    color: var(--accent-green);
    margin-top: 0;
    font-weight: 600;
}

code, pre {
    font-family: 'Geist Mono', monospace !important;
    color: #f4f4f5 !important;
}
</style>
""", unsafe_allow_html=True)

# ── Title ───────────────────────────────────────────────────────────
st.markdown(
    '<p class="hero-title">Methodology & Mathematical Framework</p>',
    unsafe_allow_html=True,
)
st.markdown(
    '<p class="hero-sub">Documentation detailing the unsupervised clustering, machine learning models, and heuristic metrics driving the platform.</p>',
    unsafe_allow_html=True,
)

# ── Content Layout ──────────────────────────────────────────────────
c_left, c_right = st.columns([1, 1])

with c_left:
    st.markdown('<div class="section-header">1. Actual shape Detection & ML Classifier</div>', unsafe_allow_html=True)
    
    st.markdown(r"""
    <div class="methodology-card">
        <h3>Unsupervised K-Means Shape Detection</h3>
        <p>To identify the team's actual structural lines (rather than their announced Starting XI shape), we capture spatial event coordinates in rolling 10-minute windows. For the 10 active outfield players:</p>
        <ol>
            <li>We collect all coordinates (passes, carries, tackles, recoveries) to calculate each player's average spatial center $(X_i, Y_i)$.</li>
            <li>We sort players by their average depth $X_i$ and fit a <b>1-dimensional K-Means clustering algorithm</b> (with $K=3$ clusters).</li>
            <li>Outfield players are partitioned into three tactical lines: <b>Defense</b> (Cluster 0), <b>Midfield</b> (Cluster 1), and <b>Attack</b> (Cluster 2).</li>
            <li>The distribution of players across these clusters defines the actual layout (e.g., 4 players in Cluster 0, 3 in Cluster 1, and 3 in Cluster 2 yields a <b>4-3-3</b> actual shape).</li>
        </ol>
    </div>
    <div class="methodology-card">
        <h3>Supervised Tactical Shift Random Forest Model</h3>
        <p>We trained a supervised machine learning model to classify noisy average coordinates into standardized formation families:</p>
        <ul>
            <li><b>Training Set:</b> 128 World Cup matches containing <b>4,433 sliding intervals</b>.</li>
            <li><b>Standardization:</b> 15 announced shapes are mapped to 5 core structural families: <code>3-at-back</code>, <code>4-2-3-1</code>, <code>4-3-3</code>, <code>4-4-2</code>, and <code>4-5-1</code>.</li>
            <li><b>Features:</b> Standardized player depths, team width, team length, and standard deviations of player coordinates to capture structural compactness.</li>
            <li><b>Model:</b> Stratified 5-Fold Random Forest classifier (scikit-learn).</li>
            <li><b>Performance:</b> Achieves a <b>32.0% cross-validation accuracy</b> (representing a 1.6x improvement over the 20% random guess baseline).</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-header">2. Playstyle Classification Rules</div>', unsafe_allow_html=True)
    
    st.markdown(r"""
    <div class="methodology-card">
        <h3>Style Detection Rules</h3>
        <p>Playing styles are detected by analyzing coordinates of defensive and transition events within match phases:</p>
        <ul>
            <li><b>Low Block:</b> Labeled if $\ge 50\%$ of defensive actions (Tackles, Interceptions, Recoveries, Pressures) occur inside the defensive third ($X < 40$).</li>
            <li><b>Mid Block:</b> Labeled if $\ge 50\%$ of defensive actions occur in the middle third ($40 \le X \le 80$).</li>
            <li><b>High Press:</b> Labeled if average pressure coordinate $X > 70$ or $\ge 40\%$ of pressures occur inside the opponent third ($X > 80$).</li>
            <li><b>Possession-Based:</b> Labeled if team average possession share is $\ge 55\%$ and pass completions exceed 450.</li>
            <li><b>Direct Play:</b> Labeled if team average possession share is under $45\%$.</li>
            <li><b>Wide Attack:</b> Labeled if $\ge 40\%$ of final-third touches ($X > 80$) occur in wide zones ($Y < 20$ or $Y > 60$).</li>
            <li><b>Central Attack:</b> Labeled if $\ge 60\%$ of final-third touches occur centrally ($20 \le Y \le 60$).</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with c_right:
    st.markdown('<div class="section-header">3. Tactical Adaptation Success Score</div>', unsafe_allow_html=True)
    
    st.markdown(r"""
    <div class="methodology-card">
        <h3>Adaptation Formula</h3>
        <p>Tactical shifts (formation changes) are evaluated by comparing the team's performance metrics 10 minutes <b>before</b> vs. 10 minutes <b>after</b> the adjustment.</p>
        <p>We calculate net metrics representing the performance margin (Team minus Opponent):</p>
        $$\Delta \text{Shots}_{\text{net}} = (\text{Shots}_{\text{after}} - \text{Shots Conceded}_{\text{after}}) - (\text{Shots}_{\text{before}} - \text{Shots Conceded}_{\text{before}})$$
        $$\Delta \text{xG}_{\text{net}} = (\text{xG}_{\text{after}} - \text{xG Conceded}_{\text{after}}) - (\text{xG}_{\text{before}} - \text{xG Conceded}_{\text{before}})$$
        $$\Delta \text{Possession} = \text{Possession Pct}_{\text{after}} - \text{Possession Pct}_{\text{before}}$$
        $$\Delta \text{Entries} = \text{Final Third Entries}_{\text{after}} - \text{Final Third Entries}_{\text{before}}$$
        <p>The adjustments are aggregated using the following weights:</p>
        $$
        \text{score\_change} = (\Delta \text{Shots}_{\text{net}} \times 5.0) + (\Delta \text{xG}_{\text{net}} \times 40.0) + (\Delta \text{Possession} \times 50.0) + (\Delta \text{Entries} \times 2.0)
        $$
        <p>The score is centered around a neutral baseline of 50 and bounded between 0 and 100:</p>
        $$\text{adaptation\_score} = \min\left(\max\left(\lfloor 50 + \text{score\_change} \rfloor, 0\right), 100\right)$$
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-header">4. Tactical DNA Heuristic Scoring</div>', unsafe_allow_html=True)
    
    st.markdown(r"""
    <div class="methodology-card">
        <h3>Tactical DNA Dimensions</h3>
        <p>The 6 radar metrics are computed to profile manager play styles:</p>
        <ol>
            <li><b>Defensive Adaptability:</b> Average success score of defensive tactical shifts. If no shifts are recorded, falls back to defensive goals conceded share in low block matches.</li>
            <li><b>Attacking Flexibility:</b> Diversity of offensive structures used in matches categorized under attacking playstyles. Evaluated using a lookup scale (1 formation = 50, 2 = 72, 3 = 86, $\ge 4$ = 96).</li>
            <li><b>Formation Stability:</b> The average share of match duration spent in the manager's primary structural shape.</li>
            <li><b>Press Resistance:</b> Scaled pass completion rate under pressure: $\max(10, \min(100, (\text{completion\_rate} - 0.5) \times 200 + 40))$.</li>
            <li><b>Counter Attack Usage:</b> Recalibrated transition shot ratio to avoid early saturation: $\max(0, \min(100, \text{counter\_ratio} \times 200 + 30))$.</li>
            <li><b>Tactical Flexibility:</b> Combined score of tactical shifts per match and number of unique shapes used throughout the tournament.</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)
