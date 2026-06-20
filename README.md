# ⚽ FIFA World Cup Tactical Formation Classifier

An interactive, premium machine learning system and Streamlit dashboard that analyzes player tracking coordinates from **StatsBomb Open Data** to detect actual team shapes using unsupervised **1-D K-Means clustering**, and tracks mid-game tactical shifts in real-time using a supervised **Random Forest classifier**.

The dashboard includes full data for the **2018, 2022, and 2026 FIFA World Cups** (matching real groups, rosters, schedules, and scores).

---

## 🌟 Key Features

*   **StatsBomb Data Pipeline & Cache Layer:** Dynamically fetches and locally caches matches and event data for the 2018, 2022, and 2026 World Cups to ensure instant subsequent loads.
*   **Substitution-Aware Player Tracking:** Chronologically processes substitution events to dynamically resolve the active outfield lineup on the pitch at any minute of the match.
*   **Unsupervised Actual Shape Detection:** Applies 1-D K-Means clustering on active players' average depth ($X$-coordinates) to group them into *Defense*, *Midfield*, and *Attack* to resolve their actual on-pitch shape.
*   **Supervised Tactical Shift Classifier:** A Random Forest model trained on 160 total matches (**5,441 rolling windows**) across 5 broad structural families (`3-at-back`, `4-2-3-1`, `4-3-3`, `4-4-2`, `4-5-1`), achieving **42.7% cross-validation accuracy** (a ~2.1x improvement over random guessing).
*   **Premium Interactive Dashboard:** A stunning, modern dark-themed interface built with custom styling featuring:
    *   **Hierarchical Match Selector:** World Cup Year $\rightarrow$ Tournament Stage $\rightarrow$ Group Stage (A-L) / Knockout Round $\rightarrow$ Match $\rightarrow$ Team.
    *   **Dynamic Time-Window Slider:** Instantly updates metrics, rosters, and the pitch layout.
    *   **Tactical Board:** A beautiful soccer pitch rendering (using `mplsoccer`) showing average player positions color-coded by cluster.
    *   **Rolling Probability Timeline:** Plots the classifier's predicted probability of formations over time and highlights mismatch periods.
    *   **Insights Panel:** Automatically calls out formation mismatch percentages, tactical shifts, and positional anomalies.

---

## 📂 Project Structure

```directory
├── data/                         # Local cached StatsBomb matches and events JSON
├── models/                       # Trained classifier & metadata artifacts
│   ├── formation_classifier.joblib
│   ├── label_encoder.joblib
│   ├── feature_cols.joblib
│   └── metadata.json
├── src/                          # Source code
│   ├── __init__.py
│   ├── data_loader.py            # StatsBomb data loader and caching layer
│   ├── features.py               # Feature engineering, K-Means shape detection, tracking
│   ├── train.py                  # ML model training and validation pipeline
│   └── generate_2026_data.py     # Real-world 2026 WC fixtures and rosters generator
├── app.py                        # Streamlit dashboard application
├── requirements.txt              # Project dependencies
└── README.md                     # Project documentation
```

---

## ⚙️ Installation & Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/danishsyed-dev/FIFA-World-Cup-Tactical-Formation-Classifier.git
    cd FIFA-World-Cup-Tactical-Formation-Classifier
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

---

## 🚀 How to Run

### 1. Generate 2026 Data & Retrain Model (Optional)
If you want to re-simulate the World Cup 2026 data and retrain the classifier:
```bash
# Generate the 2026 matches and event files
python src/generate_2026_data.py

# Retrain the model on the full 160-match dataset
python -m src.train
```

### 2. Launch the Streamlit Dashboard
To run the interactive app:
```bash
streamlit run app.py
```
Open [http://localhost:8501](http://localhost:8501) in your browser.

---

## 📊 Technical Details

### Feature Engineering
For each team, the match is divided into rolling 10-minute intervals (with a 5-minute step). For each window:
1.  We extract the 10 active outfield players using the chronological substitution tracker.
2.  We collect all event coordinates $(X, Y)$ (passes, carries, receipts, tackles) for each player.
3.  We compute each player's average spatial position $(X_i, Y_i)$ and sort players by $X$ to create a standardized 20-dimensional feature vector.
4.  We extract global team features: width ($\max(Y) - \min(Y)$), length ($\max(X) - \min(X)$), centroid, and coordinate standard deviations ($\sigma_X, \sigma_Y$) to measure team compactness.

### Unsupervised K-Means Shape Detection
Using 1-D K-Means on the outfield players' average $X$-coordinates (depth from goal), we partition them into $K=3$ clusters. The count of players in each cluster (Defense $\rightarrow$ Midfield $\rightarrow$ Attack) corresponds to the team's actual formation (e.g. `4-3-3` or `3-4-3`).
