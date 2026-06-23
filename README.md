# ⚽ FIFA World Cup Tactical Intelligence Platform

An interactive, premium tactical analytics platform and Streamlit dashboard that analyzes player tracking coordinates and events from **StatsBomb Open Data** (2018 and 2022 FIFA World Cups) to classify playing styles, profile manager signatures, evaluate tactical shifts, and track opponent responses.

The platform retains 100% of the core formation classifier features while adding deep tactical engines.

---

## 🌟 Key Features

*   **Multi-Dimensional Tactical DNA:** Computes 6 core metrics (0-100 scale) for each manager: Defensive Adaptability, Attacking Flexibility, Formation Stability, Press Resistance, Counter Attack Usage, and Tactical Flexibility, visualised as custom radar charts.
*   **In-Game Tactical Shift Efficacy:** Contrasts team performance metrics (possession, shots, expected goals, entries, pressures) 10 minutes before vs. 10 minutes after a tactical shift to calculate an adaptation success score.
*   **Opponent Response Profiler:** Tracks how managers alter formations and tactical styles in reaction to specific opponent play styles, detailing win/draw/loss rates and goals scored/conceded.
*   **Spatial Playstyle Detection:** Analyzes coordinate heatmaps and action zones to classify styles into Low Block, Mid Block, High Press, Possession-Based, Direct, Wide Attack, and Central Attack.
*   **Substitution-Aware actual shape detection:** standardizes player tracking coordinates into actual shapes via K-Means clustering, and classifies shapes using a Random Forest model.

---

## 📂 Project Structure

```directory
├── data/                         # Cached StatsBomb JSON files and compiled CSV databases
│   ├── style_analysis.csv
│   ├── tactical_shifts.csv
│   ├── opponent_responses.csv
│   ├── manager_profiles.csv
│   └── tactical_dna.csv
├── models/                       # Trained classifier & metadata artifacts
├── pages/                        # Multi-page dashboard layouts
│   ├── 1_Manager_Intelligence.py  # DNA radar charts, Category A vs B metrics, insights
│   ├── 2_Style_Analysis.py        # Spatial heatmaps, pressing height, style trends
│   ├── 3_Tactical_Adaptation.py   # Shift lists, before/after metrics comparison grid
│   ├── 4_Opponent_Response.py     # Win rates and formation deployment vs. opponent styles
│   └── 5_Methodology.py           # Mathematical framework and formulas documentation
├── src/                          # Backend Engines
│   ├── data_loader.py            # StatsBomb data loader and caching layer
│   ├── features.py               # Feature engineering, K-Means shape detection, tracking
│   ├── style_detector.py         # Playing style classification engine
│   ├── adaptation_analyzer.py    # Shift performance metrics before/after engine
│   ├── opponent_response.py      # Opponent-specific tactical response engine
│   ├── tactical_dna.py           # Manager DNA calculations
│   ├── manager_analysis.py       # Manager profile compilation and percentiles
│   ├── generate_tactical_db.py   # Database compilation pipeline
│   └── train.py                  # ML model training and validation pipeline
├── app.py                        # Streamlit homepage (Formation Classifier)
├── requirements.txt              # Project dependencies
└── README.md                     # Project documentation
```

---

## ⚙️ Installation & Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/danishsyed-dev/FIFA-World-Cup-Tactical-Intelligence-Platform.git
    cd FIFA-World-Cup-Tactical-Intelligence-Platform
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv predict_env
    # On Windows:
    predict_env\Scripts\activate
    # On macOS/Linux:
    source predict_env/bin/activate
    ```

3.  **Install the dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Compile the Tactical Database:**
    Build the precompiled CSV datasets by running the database compiler:
    ```bash
    python -m src.generate_tactical_db
    ```

---

## 🚀 How to Run

To run the interactive platform:
```bash
streamlit run app.py
```
Open [http://localhost:8501](http://localhost:8501) in your browser. Navigating the sidebar allows exploring the main classifier as well as the new dashboards under the `pages/` directory.

---

## 📊 Technical Details

*   **Defensive Third:** $X < 40$. Low Block is labeled if $> 50\%$ of actions occur in this zone.
*   **Middle Third:** $40 \le X \le 80$. Mid Block is labeled if $> 50\%$ of actions occur in this zone.
*   **Attacking Third:** $X > 80$. High Press is labeled if average pressure $X > 70$ or $> 40\%$ of pressures occur in this zone.
*   **Counter Attack:** Fast transitions from recoveries in own half ($X < 60$) to progressive carry/pass sequence leading to a shot within 20 seconds.
*   **Play style categories:**
    *   *Possession-Based:* $> 55\%$ possession, $> 450$ passes.
    *   *Direct:* $< 45\%$ possession.
    *   *Balanced:* $45\% - 55\%$ possession.
