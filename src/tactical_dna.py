"""
tactical_dna.py — Manager Tactical DNA Generator.

Computes 6 core metrics (0-100 scale) for each manager:
  - Defensive Adaptability (success of defensive tactical shifts)
  - Attacking Flexibility (formation diversity in attacking phases)
  - Formation Stability (how long the manager retains the primary shape)
  - Press Resistance (pass completion rate under pressure)
  - Counter Attack Usage (frequency of shots generated from counters)
  - Tactical Flexibility (number of tactical shifts / distinct formations)
"""

import numpy as np


def generate_tactical_dna(
    matches_data: list[dict],
    manager_shifts: list[dict],
    manager_styles: list[dict],
) -> dict:
    """
    Generate Tactical DNA scores (0-100) for a manager.
    Expects aggregated statistics for a manager's matches:
      - matches_data: list of match stats (goals, result, passes, passes_under_pressure, etc.)
      - manager_shifts: list of all tactical shifts made by the manager (with adaptation scores)
      - manager_styles: list of Style Analysis entries for the manager's team
    """
    dna = {
        "defensive_adaptability": 50,
        "attacking_flexibility": 50,
        "formation_stability": 50,
        "press_resistance": 50,
        "counter_attack_usage": 50,
        "tactical_flexibility": 50,
    }
    
    if not matches_data:
        return dna
        
    # ── 1. Defensive Adaptability ────────────────────────────────────
    # Look at shifts where the formation became more defensive (e.g. going to a 5-back, or adding a defender)
    # Or average score of tactical shifts overall.
    defensive_shifts = [
        s for s in manager_shifts 
        if s.get("adaptation_score") is not None
    ]
    if defensive_shifts:
        dna["defensive_adaptability"] = int(np.mean([s["adaptation_score"] for s in defensive_shifts]))
    else:
        # Fallback to general defensive performance (proportion of low block matches where they conceded <= 1 goal)
        low_block_matches = [m for m in manager_styles if "Low Block" in m.get("styles", [])]
        if low_block_matches:
            low_block_goals = np.mean([m.get("goals_conceded", 0) for m in low_block_matches])
            dna["defensive_adaptability"] = int(max(0, min(100, 100 - (low_block_goals * 30))))
        else:
            dna["defensive_adaptability"] = 60 # Standard baseline
            
    # Import numpy here internally if needed, but we can do standard python math
    # ── 2. Attacking Flexibility ─────────────────────────────────────
    # Number of distinct formations used in matches that had attacking style labels (Wide/Central Attack)
    attacking_formations = set()
    for m in manager_styles:
        if "Wide Attack" in m.get("styles", []) or "Central Attack" in m.get("styles", []):
            attacking_formations.add(m.get("primary_formation", ""))
            
    distinct_att_count = len(attacking_formations)
    # Scale: 1 formation = 50, 2 = 70, 3 = 85, >=4 = 95
    if distinct_att_count <= 1:
        dna["attacking_flexibility"] = 50
    elif distinct_att_count == 2:
        dna["attacking_flexibility"] = 72
    elif distinct_att_count == 3:
        dna["attacking_flexibility"] = 86
    else:
        dna["attacking_flexibility"] = 96
        
    # ── 3. Formation Stability ───────────────────────────────────────
    # stability score = average stability from styles (primary formation duration share)
    stabilities = [m.get("formation_stability", 0.8) for m in manager_styles]
    if stabilities:
        dna["formation_stability"] = int(sum(stabilities) / len(stabilities) * 100)
    else:
        dna["formation_stability"] = 75
        
    # ── 4. Press Resistance ──────────────────────────────────────────
    # pass completion rate under pressure
    comp_under_press = []
    for m in matches_data:
        p_attempts = m.get("passes_under_pressure_attempts", 0)
        p_completions = m.get("passes_under_pressure_completions", 0)
        if p_attempts > 0:
            comp_under_press.append(p_completions / p_attempts)
            
    if comp_under_press:
        # Standard pass completion under pressure is around 65%-80%. Let's scale it.
        avg_press_comp = sum(comp_under_press) / len(comp_under_press)
        # Scale: 60% completion = 50, 70% = 75, 80% = 90, 85%+ = 98
        dna["press_resistance"] = int(max(10, min(100, (avg_press_comp - 0.5) * 200 + 40)))
    else:
        dna["press_resistance"] = 65
        
    # ── 5. Counter Attack Usage ──────────────────────────────────────
    # Ratio of counter attacks to total shots
    counters = [m.get("counter_attacks", 0) for m in manager_styles]
    shots = [m.get("shots", 8) for m in manager_styles]
    
    total_counters = sum(counters)
    total_shots = sum(shots)
    
    if total_shots > 0:
        counter_ratio = total_counters / total_shots
        # Recalibrated to prevent rapid saturation: ratio * 200 + 30 (e.g. 10% ratio = 50, 20% ratio = 70, 35%+ ratio = 100)
        dna["counter_attack_usage"] = int(max(0, min(100, counter_ratio * 200 + 30)))
    else:
        dna["counter_attack_usage"] = 45
        
    # ── 6. Tactical Flexibility ──────────────────────────────────────
    # Combined score of (shifts per match) and (total distinct formations used)
    total_matches = len(matches_data)
    total_shifts = len(manager_shifts)
    shifts_per_match = total_shifts / total_matches if total_matches > 0 else 0
    
    distinct_formations = set(m.get("primary_formation", "") for m in manager_styles)
    n_formations = len(distinct_formations)
    
    # Shifts component: 0 shifts = 30, 0.5 per match = 55, 1.0 = 75, 1.5+ = 90
    shifts_score = shifts_per_match * 40 + 35
    # Formations component: 1 shape = 40, 2 shapes = 65, 3 shapes = 85, 4+ shapes = 95
    form_score = 40 + (n_formations - 1) * 20
    
    dna["tactical_flexibility"] = int(max(10, min(100, (shifts_score + form_score) / 2.0)))
    
    return dna
