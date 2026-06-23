"""
manager_analysis.py — Manager Tactical Profile Engine.

Tracks manager statistics (wins, draws, losses, goals, shifts) and divides them
into Category A (both tournaments) or Category B (single tournament).
"""

import pandas as pd
import numpy as np

def build_manager_profiles(
    style_df: pd.DataFrame, 
    shifts_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Build manager profiles from style and shift datasets.
    Calculates matches, wins, draws, losses, goals, shifts, stability, categories.
    """
    if style_df.empty:
        return pd.DataFrame()
        
    profiles = []
    managers = style_df["manager"].unique()
    
    for mgr in managers:
        df_mgr = style_df[style_df["manager"] == mgr]
        df_shifts = shifts_df[shifts_df["manager"] == mgr] if not shifts_df.empty else pd.DataFrame()
        
        years = sorted(df_mgr["year"].unique())
        category = "Category A" if len(years) > 1 else "Category B"
        
        matches = len(df_mgr)
        wins = sum(1 for r in df_mgr["result"] if r == "Win")
        draws = sum(1 for r in df_mgr["result"] if r == "Draw")
        losses = sum(1 for r in df_mgr["result"] if r == "Loss")
        
        goals_scored = df_mgr["goals_scored"].sum()
        goals_conceded = df_mgr["goals_conceded"].sum()
        
        # Formation metrics
        all_formations = []
        for form_list in df_mgr["formations_used"]:
            if isinstance(form_list, str):
                all_formations.extend([f.strip() for f in form_list.split(",")])
            elif isinstance(form_list, list):
                all_formations.extend(form_list)
                
        formations_used_count = len(set(all_formations))
        
        # Most used formation
        primary_formations = df_mgr["primary_formation"].tolist()
        most_used_form = max(set(primary_formations), key=primary_formations.count) if primary_formations else "Unknown"
        
        # Tactical shifts
        shifts_count = len(df_shifts)
        
        # Stability
        stability = df_mgr["formation_stability"].mean() if "formation_stability" in df_mgr.columns else 0.80
        
        # Average duration of a formation (roughly 90 min / (shifts + 1))
        avg_duration = (matches * 90) / (shifts_count + matches) if (shifts_count + matches) > 0 else 90.0
        
        profiles.append({
            "manager": mgr,
            "world_cups": ", ".join(str(y) for y in years),
            "matches": matches,
            "wins": wins,
            "draws": draws,
            "losses": losses,
            "goals_scored": int(goals_scored),
            "goals_conceded": int(goals_conceded),
            "formations_used": formations_used_count,
            "most_used_formation": most_used_form,
            "tactical_shifts": shifts_count,
            "formation_stability": float(stability),
            "avg_formation_duration": float(avg_duration),
            "category": category,
        })
        
    return pd.DataFrame(profiles)


def get_manager_percentiles(profiles_df: pd.DataFrame) -> pd.DataFrame:
    """
    For Category B managers, calculate percentile ranks against
    all tournament managers to prevent unfair absolute comparisons.
    """
    if profiles_df.empty:
        return pd.DataFrame()
        
    df = profiles_df.copy()
    
    # Calculate percentiles across all managers
    df["flexibility_percentile"] = df["formations_used"].rank(pct=True) * 100.0
    df["shifts_percentile"] = df["tactical_shifts"].rank(pct=True) * 100.0
    df["stability_percentile"] = (100.0 - df["formation_stability"].rank(pct=True) * 100.0) # Lower stability = higher flexibility percentile
    
    # Adaptability percentile based on avg duration (lower duration = higher adaptation frequency)
    df["adaptability_percentile"] = (100.0 - df["avg_formation_duration"].rank(pct=True) * 100.0)
    
    return df
