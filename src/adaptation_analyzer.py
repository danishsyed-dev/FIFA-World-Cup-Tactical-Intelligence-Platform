"""
adaptation_analyzer.py — Tactical Adaptation Intelligence Engine.

Tracks the performance metrics of a team 10 minutes before and 10 minutes after
a tactical shift to calculate an adaptation success score (0-100).
"""

import numpy as np

def _get_period_metrics(events: list[dict], team: str, start_t: float, end_t: float) -> dict:
    """Compute performance metrics inside the time interval [start_t, end_t]."""
    metrics = {
        "passes": 0,
        "opp_passes": 0,
        "shots": 0,
        "shots_conceded": 0,
        "xg": 0.0,
        "xg_conceded": 0.0,
        "final_third_entries": 0,
        "pressures": 0,
    }
    
    for ev in events:
        period = ev.get("period", 1)
        minute = ev.get("minute", 0)
        second = ev.get("second", 0)
        t = minute + second / 60.0
        
        if t < start_t or t > end_t:
            continue
            
        ev_team = ev.get("team", {}).get("name", "")
        etype = ev.get("type", {}).get("name", "")
        
        # 1. Passes & possession proxy
        if etype == "Pass":
            outcome = ev.get("pass", {}).get("outcome", {}).get("name", "")
            if outcome == "": # Complete
                if ev_team == team:
                    metrics["passes"] += 1
                else:
                    metrics["opp_passes"] += 1
                    
        # 2. Shots & xG
        elif etype == "Shot":
            xg = ev.get("shot", {}).get("xg", 0.0)
            if ev_team == team:
                metrics["shots"] += 1
                metrics["xg"] += xg
            else:
                metrics["shots_conceded"] += 1
                metrics["xg_conceded"] += xg
                
        # 3. Final third entries
        # Pass or carry that starts outside final third and ends inside final third (X > 80)
        elif etype in ("Pass", "Carry"):
            loc = ev.get("location")
            if loc and loc[0] < 80: # Started outside final third
                # Check destination
                dest = None
                if etype == "Pass":
                    dest = ev.get("pass", {}).get("end_location")
                elif etype == "Carry":
                    dest = ev.get("carry", {}).get("end_location")
                    
                if dest and len(dest) >= 2 and dest[0] > 80:
                    if ev_team == team:
                        metrics["final_third_entries"] += 1
                        
        # 4. Pressures
        elif etype == "Pressure":
            if ev_team == team:
                metrics["pressures"] += 1
                
    # Calculate possession percentage
    total_p = metrics["passes"] + metrics["opp_passes"]
    metrics["possession_pct"] = float(metrics["passes"] / total_p) if total_p > 0 else 0.5
    
    return metrics


def analyze_tactical_shift(
    events: list[dict],
    team: str,
    shift_minute: float,
    formation_before: str,
    formation_after: str,
) -> dict:
    """
    Compare team performance 10 minutes before and 10 minutes after a tactical shift.
    Computes adaptation score (0-100) and classifies tactical shift success.
    """
    before_metrics = _get_period_metrics(events, team, max(0.0, shift_minute - 10), shift_minute)
    after_metrics = _get_period_metrics(events, team, shift_minute, shift_minute + 10)
    
    # ── Calculate adaptation effectiveness score ──
    # Base score is 50. Adjust based on performance changes.
    # Positive points for increased shots, increased xG, decreased shots conceded, decreased xG conceded, more possession
    
    shot_diff_before = before_metrics["shots"] - before_metrics["shots_conceded"]
    shot_diff_after = after_metrics["shots"] - after_metrics["shots_conceded"]
    shot_improvement = shot_diff_after - shot_diff_before
    
    xg_diff_before = before_metrics["xg"] - before_metrics["xg_conceded"]
    xg_diff_after = after_metrics["xg"] - after_metrics["xg_conceded"]
    xg_improvement = xg_diff_after - xg_diff_before
    
    possession_improvement = after_metrics["possession_pct"] - before_metrics["possession_pct"]
    entry_improvement = after_metrics["final_third_entries"] - before_metrics["final_third_entries"]
    
    # Weights for adjustments
    score_change = (
        (shot_improvement * 5.0) +
        (xg_improvement * 40.0) +
        (possession_improvement * 50.0) +
        (entry_improvement * 2.0)
    )
    
    adaptation_score = min(max(int(50 + score_change), 0), 100)
    
    # Classify success
    if adaptation_score > 60:
        classification = "Successful Tactical Change"
    elif adaptation_score < 40:
        classification = "Unsuccessful Tactical Change"
    else:
        classification = "Neutral Tactical Change"
        
    return {
        "minute": shift_minute,
        "formation_before": formation_before,
        "formation_after": formation_after,
        "before": before_metrics,
        "after": after_metrics,
        "adaptation_score": adaptation_score,
        "classification": classification,
    }
