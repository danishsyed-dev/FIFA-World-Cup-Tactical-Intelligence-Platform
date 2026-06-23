"""
style_detector.py — Style Of Play Detection Engine.

Classifies team playing styles based on spatial and event distributions:
  - Low Block, Mid Block, High Press
  - Counter Attack
  - Possession-Based, Direct Play, Balanced
  - Wide Attack, Central Attack
"""

import numpy as np

def detect_playing_styles(events: list[dict], team: str, start_min: float = 0, end_min: float = 999) -> dict:
    """
    Analyze events within [start_min, end_min] for a given team,
    compute scores for each tactical style, and determine active style labels.
    """
    # ── Filter events in window ──────────────────────────────────────
    window_events = []
    opponent_events = []
    
    for ev in events:
        period = ev.get("period", 1)
        minute = ev.get("minute", 0)
        second = ev.get("second", 0)
        t = minute + second / 60.0
        
        if t < start_min or t > end_min:
            continue
            
        ev_team = ev.get("team", {}).get("name", "")
        if ev_team == team:
            window_events.append(ev)
        elif ev_team != "":
            opponent_events.append(ev)

    # ── Initialize scores ────────────────────────────────────────────
    scores = {
        "low_block_score": 0.0,
        "mid_block_score": 0.0,
        "high_press_score": 0.0,
        "average_pressure_x": 40.0,
        "possession_score": 0.5,
        "counter_attack_count": 0,
        "counter_attack_frequency": 0.0,
        "wide_attack_score": 0.0,
        "central_attack_score": 0.0,
    }
    
    # ── 1. Defensive Block & Pressing Analysis ───────────────────────
    defensive_actions = []
    pressures = []
    
    for ev in window_events:
        etype = ev.get("type", {}).get("name", "")
        loc = ev.get("location")
        if not loc or len(loc) < 2:
            continue
            
        # Defensive Action: Pressure, Interception, Ball Recovery, or Duel (Tackle)
        is_defensive = False
        if etype in ("Pressure", "Interception", "Ball Recovery"):
            is_defensive = True
        elif etype == "Duel":
            dtype = ev.get("duel", {}).get("type", {}).get("name", "")
            if dtype == "Tackle":
                is_defensive = True
                
        if is_defensive:
            defensive_actions.append(ev)
        if etype == "Pressure":
            pressures.append(ev)
            
    # Calculate block scores
    if defensive_actions:
        low_count = sum(1 for ev in defensive_actions if ev["location"][0] < 40)
        mid_count = sum(1 for ev in defensive_actions if 40 <= ev["location"][0] <= 80)
        scores["low_block_score"] = float(low_count / len(defensive_actions))
        scores["mid_block_score"] = float(mid_count / len(defensive_actions))
        
    if pressures:
        att_press_count = sum(1 for ev in pressures if ev["location"][0] > 80)
        scores["high_press_score"] = float(att_press_count / len(pressures))
        scores["average_pressure_x"] = float(np.mean([ev["location"][0] for ev in pressures]))
    else:
        scores["average_pressure_x"] = 0.0
        
    # ── 2. Counter Attack Detection ──────────────────────────────────
    # Find all Shot events in this window
    shots = [ev for ev in window_events if ev.get("type", {}).get("name") == "Shot"]
    counter_count = 0
    
    # Trace preceding events for each shot (up to 20 seconds)
    for shot in shots:
        shot_minute = shot.get("minute", 0)
        shot_second = shot.get("second", 0)
        shot_time = shot_minute * 60 + shot_second
        
        # Check if there was a recovery in own half within 20s before the shot
        for ev in window_events:
            etype = ev.get("type", {}).get("name", "")
            if etype not in ("Ball Recovery", "Interception", "Duel"):
                continue
                
            if etype == "Duel":
                dtype = ev.get("duel", {}).get("type", {}).get("name", "")
                if dtype != "Tackle":
                    continue
                outcome = ev.get("duel", {}).get("outcome", {}).get("name", "")
                if "Success" not in outcome and "Won" not in outcome:
                    continue
            
            ev_min = ev.get("minute", 0)
            ev_sec = ev.get("second", 0)
            ev_time = ev_min * 60 + ev_sec
            
            # Match timeframe and location (own half X < 60)
            if 0 < (shot_time - ev_time) <= 20:
                loc = ev.get("location")
                if loc and loc[0] < 60:
                    counter_count += 1
                    break
                    
    scores["counter_attack_count"] = counter_count
    window_len = float(end_min - start_min)
    scores["counter_attack_frequency"] = float(counter_count / (window_len if window_len > 0 else 10))

    # ── 3. Possession Style Classification ───────────────────────────
    passes = [ev for ev in window_events if ev.get("type", {}).get("name") == "Pass"]
    opp_passes = [ev for ev in opponent_events if ev.get("type", {}).get("name") == "Pass"]
    
    total_passes = len(passes) + len(opp_passes)
    possession_pct = len(passes) / total_passes if total_passes > 0 else 0.5
    scores["possession_score"] = float(possession_pct)

    # ── 4. Attacking Direction (Wide vs Central) ─────────────────────
    # Touches in the final third (X > 80)
    final_third_touches = []
    for ev in window_events:
        etype = ev.get("type", {}).get("name", "")
        # Events indicating active ball touches
        if etype in ("Pass", "Carry", "Ball Receipt", "Shot", "Dribble"):
            loc = ev.get("location")
            if loc and len(loc) >= 2 and loc[0] > 80:
                final_third_touches.append(ev)
                
    if final_third_touches:
        # Width Y goes from 0 to 80. Wings are Y < 22 or Y > 58. Center is 22 <= Y <= 58.
        wing_count = sum(1 for ev in final_third_touches if ev["location"][1] < 22 or ev["location"][1] > 58)
        center_count = sum(1 for ev in final_third_touches if 22 <= ev["location"][1] <= 58)
        scores["wide_attack_score"] = float(wing_count / len(final_third_touches))
        scores["central_attack_score"] = float(center_count / len(final_third_touches))

    # ── Style Classification Logic ───────────────────────────────────
    styles = []
    
    # Defensive line classification
    if scores["low_block_score"] > 0.45:
        styles.append("Low Block")
    elif scores["mid_block_score"] > 0.45:
        styles.append("Mid Block")
        
    # Pressing classification
    if scores["average_pressure_x"] > 68 or scores["high_press_score"] > 0.35:
        styles.append("High Press")
        
    # Counter attack classification
    if scores["counter_attack_count"] >= 1:
        styles.append("Counter Attack")
        
    # Possession classification
    # Scale counts to window length (assuming full match has 90 min)
    min_scale = (window_len / 90.0) if window_len < 90 else 1.0
    pass_threshold_high = 450 * min_scale
    pass_threshold_low = 300 * min_scale
    
    possession_label = "Balanced"
    if possession_pct > 0.53 or len(passes) > pass_threshold_high:
        styles.append("Possession-Based")
        possession_label = "Possession-Based"
    elif possession_pct < 0.45 or len(passes) < pass_threshold_low:
        styles.append("Direct Play")
        possession_label = "Direct Play"
    else:
        possession_label = "Balanced"
        
    # Attacking direction classification
    if scores["wide_attack_score"] > 0.40:
        styles.append("Wide Attack")
    if scores["central_attack_score"] > 0.58:
        styles.append("Central Attack")

    return {
        "styles": styles,
        "possession_label": possession_label,
        "scores": scores,
    }
