"""
generate_tactical_db.py — Tactical Platform Data Compiler.

Processes the entire World Cup 2018 & 2022 dataset to build and cache
tactical profiles, shifts, styles, DNA, and opponent responses.
"""

import sys
import os
import json
from pathlib import Path
import pandas as pd
import numpy as np

# Ensure project root is in path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.data_loader import get_all_matches, get_events, match_label
from src.features import extract_tactical_timeline, rolling_formation_analysis
from src.style_detector import detect_playing_styles
from src.adaptation_analyzer import analyze_tactical_shift
from src.opponent_response import compile_opponent_responses
from src.tactical_dna import generate_tactical_dna
from src.manager_analysis import build_manager_profiles, get_manager_percentiles

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

def compile_database():
    print("=" * 60)
    print("  Tactical Platform Compiler — Generating Datasets")
    print("=" * 60)
    
    all_matches = get_all_matches()
    total_matches = len(all_matches)
    
    style_records = []
    shift_records = []
    match_stats_for_dna = {} # Key: manager, Value: list of match stats
    
    print(f"Processing {total_matches} matches...")
    
    for idx, match in enumerate(all_matches, 1):
        match_id = match["match_id"]
        year = match.get("_wc_year", 2022)
        h_team = match["home_team"]["home_team_name"]
        a_team = match["away_team"]["away_team_name"]
        h_score = match.get("home_score", 0)
        a_score = match.get("away_score", 0)
        
        # Extract managers
        h_managers = match["home_team"].get("managers", [])
        h_mgr = h_managers[0]["nickname"] or h_managers[0]["name"] if h_managers else "Unknown Manager"
        
        a_managers = match["away_team"].get("managers", [])
        a_mgr = a_managers[0]["nickname"] or a_managers[0]["name"] if a_managers else "Unknown Manager"
        
        if idx % 15 == 0 or idx == 1:
            print(f"  [{idx}/{total_matches}] {h_team} vs {a_team} ({year})")
            
        try:
            events = get_events(match_id)
        except Exception as exc:
            print(f"    ⚠ skipping {match_id} — {exc}")
            continue
            
        timeline = extract_tactical_timeline(events)
        
        # Process each team
        for team, mgr, score, opp_score, opponent in [
            (h_team, h_mgr, h_score, a_score, a_team),
            (a_team, a_mgr, a_score, h_score, h_team)
        ]:
            if team not in timeline or not timeline[team]:
                continue
                
            # 1. Style analysis for the match
            style_res = detect_playing_styles(events, team, start_min=0, end_min=95)
            
            # Find all formations used
            team_timeline = timeline[team]
            formations_used = list(set(e["formation"] for e in team_timeline))
            primary_form = team_timeline[0]["formation"] # Starting XI
            
            # Stability score
            # Calculate proportion of match spent in primary formation
            # If no shifts, stability = 1.0
            stability = 1.0
            shifts_events = [e for e in team_timeline if e["event_type"] == "Tactical Shift"]
            if shifts_events:
                # Approximate duration of primary shape
                primary_end = shifts_events[0]["minute"]
                stability = float(primary_end / 90.0)
                stability = min(max(stability, 0.1), 1.0)
                
            # Match outcome
            if score > opp_score:
                result = "Win"
            elif score < opp_score:
                result = "Loss"
            else:
                result = "Draw"
                
            style_records.append({
                "match_id": match_id,
                "year": year,
                "manager": mgr,
                "team": team,
                "opponent": opponent,
                "result": result,
                "goals_scored": int(score),
                "goals_conceded": int(opp_score),
                "primary_formation": primary_form,
                "formations_used": ", ".join(formations_used),
                "formation_stability": stability,
                "styles": ", ".join(style_res["styles"]),
                "low_block_score": style_res["scores"]["low_block_score"],
                "mid_block_score": style_res["scores"]["mid_block_score"],
                "high_press_score": style_res["scores"]["high_press_score"],
                "average_pressure_x": style_res["scores"]["average_pressure_x"],
                "possession_score": style_res["scores"]["possession_score"],
                "counter_attacks": style_res["scores"]["counter_attack_count"],
                "wide_attack_score": style_res["scores"]["wide_attack_score"],
                "central_attack_score": style_res["scores"]["central_attack_score"],
                "shots": len([e for e in events if e.get("type", {}).get("name") == "Shot" and e.get("team", {}).get("name") == team]),
            })
            
            # 2. Shift analysis
            for i, shift in enumerate(shifts_events):
                form_before = team_timeline[i]["formation"] # previous entry
                form_after = shift["formation"]
                shift_min = shift["minute"]
                
                try:
                    shift_analysis = analyze_tactical_shift(events, team, shift_min, form_before, form_after)
                    shift_records.append({
                        "match_id": match_id,
                        "year": year,
                        "manager": mgr,
                        "team": team,
                        "opponent": opponent,
                        "minute": shift_min,
                        "formation_before": form_before,
                        "formation_after": form_after,
                        "adaptation_score": shift_analysis["adaptation_score"],
                        "classification": shift_analysis["classification"],
                        "possession_before": shift_analysis["before"]["possession_pct"],
                        "possession_after": shift_analysis["after"]["possession_pct"],
                        "shots_before": shift_analysis["before"]["shots"],
                        "shots_after": shift_analysis["after"]["shots"],
                        "xg_before": shift_analysis["before"]["xg"],
                        "xg_after": shift_analysis["after"]["xg"],
                    })
                except Exception as exc:
                    pass
            
            # 3. Compile stats for DNA (passes under pressure)
            pressure_passes = [
                e for e in events 
                if e.get("type", {}).get("name") == "Pass" 
                and e.get("team", {}).get("name") == team
                and e.get("under_pressure", False)
            ]
            
            pressure_completions = sum(
                1 for e in pressure_passes 
                if e.get("pass", {}).get("outcome", {}).get("name", "") == ""
            )
            
            match_stats_for_dna.setdefault(mgr, []).append({
                "year": year,
                "passes_under_pressure_attempts": len(pressure_passes),
                "passes_under_pressure_completions": pressure_completions,
            })
            
    # Convert lists to DataFrames
    style_df = pd.DataFrame(style_records)
    shifts_df = pd.DataFrame(shift_records)
    
    # ── 4. Compile Opponent Responses ──
    opponent_records = []
    for record in style_records:
        # Find opponent's style profile in this match
        opp_style_row = [r for r in style_records if r["match_id"] == record["match_id"] and r["team"] == record["opponent"]]
        opp_styles = []
        if opp_style_row:
            opp_styles = [s.strip() for s in opp_style_row[0]["styles"].split(",") if s.strip() != ""]
            
        opponent_records.append({
            "manager": record["manager"],
            "opponent_styles": opp_styles,
            "formation_used": record["primary_formation"],
            "tactical_style": [s.strip() for s in record["styles"].split(",") if s.strip() != ""],
            "result": record["result"],
            "goals_scored": record["goals_scored"],
            "goals_conceded": record["goals_conceded"],
        })
        
    opponent_df = compile_opponent_responses(opponent_records)
    
    # ── 5. Build Manager Profiles (Percentiles & Categories) ──
    raw_profiles = build_manager_profiles(style_df, shifts_df)
    profiles_df = get_manager_percentiles(raw_profiles)
    
    # ── 6. Generate Tactical DNA ──
    dna_records = []
    for mgr in style_df["manager"].unique():
        mgr_matches = match_stats_for_dna.get(mgr, [])
        mgr_shifts = [r for r in shift_records if r["manager"] == mgr]
        mgr_styles = [r for r in style_records if r["manager"] == mgr]
        
        # Overall
        dna = generate_tactical_dna(mgr_matches, mgr_shifts, mgr_styles)
        dna["manager"] = mgr
        dna["year"] = "Overall"
        dna_records.append(dna)
        
        # Split by year if Category A
        years_managed = sorted(list(set(r["year"] for r in mgr_styles)))
        if len(years_managed) > 1:
            for yr in years_managed:
                yr_matches = [m for m in mgr_matches if m["year"] == yr]
                yr_shifts = [s for s in mgr_shifts if s["year"] == yr]
                yr_styles = [st for st in mgr_styles if st["year"] == yr]
                
                dna_yr = generate_tactical_dna(yr_matches, yr_shifts, yr_styles)
                dna_yr["manager"] = mgr
                dna_yr["year"] = str(yr)
                dna_records.append(dna_yr)
        
    dna_df = pd.DataFrame(dna_records)
    
    # ── Save CSVs ──
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    style_df.to_csv(DATA_DIR / "style_analysis.csv", index=False)
    shifts_df.to_csv(DATA_DIR / "tactical_shifts.csv", index=False)
    opponent_df.to_csv(DATA_DIR / "opponent_responses.csv", index=False)
    profiles_df.to_csv(DATA_DIR / "manager_profiles.csv", index=False)
    dna_df.to_csv(DATA_DIR / "tactical_dna.csv", index=False)
    
    print("\nSuccessfully compiled and saved all tactical databases:")
    print(f"  • {DATA_DIR}/style_analysis.csv     ({len(style_df)} rows)")
    print(f"  • {DATA_DIR}/tactical_shifts.csv     ({len(shifts_df)} rows)")
    print(f"  • {DATA_DIR}/opponent_responses.csv  ({len(opponent_df)} rows)")
    print(f"  • {DATA_DIR}/manager_profiles.csv    ({len(profiles_df)} rows)")
    print(f"  • {DATA_DIR}/tactical_dna.csv        ({len(dna_df)} rows)")

if __name__ == "__main__":
    compile_database()
