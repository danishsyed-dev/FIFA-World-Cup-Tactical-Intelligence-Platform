"""
train.py — Build the formation-classification dataset from every
World Cup match, train a Random Forest classifier, and serialise
the model to  models/formation_classifier.joblib.

Usage:
    python -m src.train
"""

import json
import sys
import os
import time
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score, StratifiedKFold
from sklearn.preprocessing import LabelEncoder
import joblib

# Allow running both as `python src/train.py` and `python -m src.train`
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.data_loader import get_all_matches, get_events, match_label
from src.features import (
    extract_tactical_timeline,
    rolling_formation_analysis,
)

MODEL_DIR = Path(__file__).resolve().parent.parent / "models"


# Map fine-grained formations to broader structural families.
# This dramatically improves classification accuracy because the
# difference between e.g. 4-2-3-1 and 4-1-4-1 in average positions
# is nearly indistinguishable, but the difference between a 4-back
# and a 3-back system is clearly visible in the spatial data.
FORMATION_FAMILIES = {
    # 4-back flat
    "4-4-2":     "4-4-2",
    "4-4-1-1":   "4-4-2",
    "4-2-2-2":   "4-4-2",
    # 4-back with CAM / #10
    "4-2-3-1":   "4-2-3-1",
    "4-3-2-1":   "4-2-3-1",
    "4-1-2-1-2": "4-2-3-1",
    # 4-back three forwards
    "4-3-3":     "4-3-3",
    # 4-back packed midfield
    "4-5-1":     "4-5-1",
    "4-1-4-1":   "4-5-1",
    # 3/5 back systems
    "3-4-3":     "3-at-back",
    "3-5-2":     "3-at-back",
    "3-4-2-1":   "3-at-back",
    "3-4-1-2":   "3-at-back",
    "3-5-1-1":   "3-at-back",
    "5-4-1":     "3-at-back",
    "5-3-2":     "3-at-back",
    "5-2-3":     "3-at-back",
    "3-1-4-2":   "3-at-back",
}


def _normalise_formation_label(label: str) -> str:
    """
    Collapse fine-grained formations into structural families so
    the classifier works on visually distinct tactical shapes.
    """
    label = label.strip()
    return FORMATION_FAMILIES.get(label, label)


def build_dataset() -> pd.DataFrame:
    """
    Iterate over every World Cup match → every team → every rolling
    window.  Returns a DataFrame where each row is one window with
    its feature columns and the 'formation_label' target.
    """
    all_matches = get_all_matches()
    rows = []
    total = len(all_matches)

    print(f"Processing {total} matches …")

    for idx, match in enumerate(all_matches, 1):
        mid = match["match_id"]
        year = match.get("_wc_year", "?")
        label = match_label(match)

        if idx % 10 == 0 or idx == 1:
            print(f"  [{idx}/{total}] {label}  (WC {year})")

        try:
            events = get_events(mid)
        except Exception as exc:
            print(f"    ⚠ skipping — {exc}")
            continue

        timeline = extract_tactical_timeline(events)

        for team in timeline:
            windows = rolling_formation_analysis(events, team)
            for w in windows:
                feat = w["features"]
                if feat is None:
                    continue
                feat["match_id"] = mid
                feat["team"] = team
                feat["wc_year"] = year
                feat["window_start"] = w["window_start"]
                feat["window_end"] = w["window_end"]
                feat["formation_label"] = _normalise_formation_label(
                    w["announced_formation"]
                )
                feat["detected_formation"] = w["detected_formation"]
                rows.append(feat)

    df = pd.DataFrame(rows)
    print(f"\nDataset: {len(df)} rows, {len(df.columns)} columns")
    return df


FEATURE_COLS = [
    *[f"sorted_x_{i}" for i in range(10)],
    *[f"sorted_y_{i}" for i in range(10)],
    "team_centroid_x", "team_centroid_y",
    "team_length", "team_width",
    "std_x", "std_y",
    "kmeans_def", "kmeans_mid", "kmeans_att",
]


def train_model(df: pd.DataFrame):
    """
    Train a Random Forest on the feature columns, targeting formation_label.
    Returns (model, label_encoder, accuracy, report_dict).
    """
    # Drop formations with very few samples
    counts = df["formation_label"].value_counts()
    keep = counts[counts >= 5].index
    df_train = df[df["formation_label"].isin(keep)].copy()

    dropped = set(counts.index) - set(keep)
    if dropped:
        print(f"Dropped rare formations ({len(dropped)}): {dropped}")

    print(f"Training on {len(df_train)} rows, "
          f"{df_train['formation_label'].nunique()} formation classes")
    print(f"Classes: {dict(df_train['formation_label'].value_counts())}")

    le = LabelEncoder()
    y = le.fit_transform(df_train["formation_label"])
    X = df_train[FEATURE_COLS].values

    clf = RandomForestClassifier(
        n_estimators=200,
        max_depth=20,
        min_samples_leaf=3,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1,
    )

    # Cross-validate
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    scores = cross_val_score(clf, X, y, cv=cv, scoring="accuracy")
    print(f"\n5-Fold CV accuracy: {scores.mean():.3f} ± {scores.std():.3f}")

    # Fit final model on all data
    clf.fit(X, y)

    # Feature importances
    importances = sorted(
        zip(FEATURE_COLS, clf.feature_importances_),
        key=lambda t: t[1],
        reverse=True,
    )
    print("\nTop 10 features:")
    for fname, imp in importances[:10]:
        print(f"  {fname:25s} {imp:.4f}")

    return clf, le, scores.mean()


def save_artifacts(clf, le, df, accuracy):
    """Persist model, encoder, feature list, and dataset."""
    MODEL_DIR.mkdir(parents=True, exist_ok=True)

    joblib.dump(clf, MODEL_DIR / "formation_classifier.joblib")
    joblib.dump(le, MODEL_DIR / "label_encoder.joblib")
    joblib.dump(FEATURE_COLS, MODEL_DIR / "feature_cols.joblib")

    # Save the full dataset as CSV for the dashboard
    data_dir = Path(__file__).resolve().parent.parent / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    df.to_csv(data_dir / "formation_dataset.csv", index=False)

    # Save a metadata JSON
    meta = {
        "accuracy": float(accuracy),
        "n_classes": int(le.classes_.shape[0]),
        "classes": le.classes_.tolist(),
        "n_samples": int(len(df)),
        "feature_cols": FEATURE_COLS,
    }
    with open(MODEL_DIR / "metadata.json", "w") as f:
        json.dump(meta, f, indent=2)

    print(f"\nSaved model to {MODEL_DIR}")
    print(f"  Classes: {le.classes_.tolist()}")


# ── Main ────────────────────────────────────────────────────────────
def main():
    t0 = time.time()

    print("=" * 60)
    print("  Tactical Formation Classifier — Training Pipeline")
    print("=" * 60)

    df = build_dataset()
    if df.empty:
        print("No data extracted. Aborting.")
        return

    clf, le, accuracy = train_model(df)
    save_artifacts(clf, le, df, accuracy)

    elapsed = time.time() - t0
    print(f"\nDone in {elapsed:.1f}s")


if __name__ == "__main__":
    main()
