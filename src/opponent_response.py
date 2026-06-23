"""
opponent_response.py — Opponent-Specific Tactical Response Engine.

Analyzes manager decisions (formations, play styles) against the detected style
of the opponent and tracks effectiveness (win/draw/loss rates, goals).
"""

import pandas as pd

def compile_opponent_responses(match_records: list[dict]) -> pd.DataFrame:
    """
    Compile opponent response records from all processed matches.
    Expects match_records with fields:
      - manager: manager name
      - opponent_style: active style labels of the opponent
      - formation_used: primary formation used
      - tactical_style: active styles of the team
      - result: 'Win', 'Draw', or 'Loss'
      - goals_scored: goals scored by manager's team
      - goals_conceded: goals conceded by manager's team
    """
    rows = []
    for record in match_records:
        opp_styles = record.get("opponent_styles", [])
        if not opp_styles:
            opp_styles = ["Balanced"] # Default if no strong style detected
            
        for opp_style in opp_styles:
            rows.append({
                "manager": record["manager"],
                "opponent_style": opp_style,
                "formation_used": record["formation_used"],
                "tactical_style": ", ".join(record.get("tactical_style", [])),
                "result": record["result"],
                "goals_scored": record["goals_scored"],
                "goals_conceded": record["goals_conceded"],
            })
            
    return pd.DataFrame(rows)


def calculate_style_effectiveness(df_responses: pd.DataFrame, manager: str) -> pd.DataFrame:
    """
    Calculate win/draw/loss rates and average goals scored/conceded
    for each opponent style for a given manager.
    """
    df_mgr = df_responses[df_responses["manager"] == manager]
    if df_mgr.empty:
        return pd.DataFrame()
        
    stats = []
    grouped = df_mgr.groupby("opponent_style")
    
    for opp_style, group in grouped:
        total = len(group)
        wins = sum(1 for r in group["result"] if r == "Win")
        draws = sum(1 for r in group["result"] if r == "Draw")
        losses = sum(1 for r in group["result"] if r == "Loss")
        
        stats.append({
            "opponent_style": opp_style,
            "matches": total,
            "win_rate": float(wins / total) if total > 0 else 0.0,
            "draw_rate": float(draws / total) if total > 0 else 0.0,
            "loss_rate": float(losses / total) if total > 0 else 0.0,
            "avg_goals_scored": float(group["goals_scored"].mean()),
            "avg_goals_conceded": float(group["goals_conceded"].mean()),
        })
        
    return pd.DataFrame(stats)
