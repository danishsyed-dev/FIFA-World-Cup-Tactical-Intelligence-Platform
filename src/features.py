"""
features.py — Formation detection via K-Means and feature extraction.

Core pipeline:
  1.  Extract the starting XI and tactical-shift events to know the
      *announced* formation at each moment.
  2.  Collect (x, y) event locations per outfield player in rolling
      time windows.
  3.  Compute average positions → run 1-D K-Means on the X-axis to
      detect the *actual* formation shape.
  4.  Build a feature vector for supervised classification.
"""

import numpy as np
from collections import defaultdict

# ── Standard formation labels ───────────────────────────────────────
CANONICAL_FORMATIONS = {
    "442",  "4411", "433", "4231", "4321", "4141",
    "352", "343", "3412", "3421", "3511", "3142",
    "532", "541", "523",
}


def _formation_str(code: int | str) -> str:
    """Normalise a StatsBomb formation code like 433 → '4-3-3'."""
    s = str(code)
    return "-".join(s)


# ── 1. Parse lineups & tactical shifts ──────────────────────────────

def extract_tactical_timeline(events: list[dict]) -> dict:
    """
    Return a dict keyed by team name, each value being a sorted list:
      [ { "minute": int, "formation": str, "players": [str, …] }, … ]

    The first entry per team is the Starting XI; subsequent entries
    are Tactical Shift events.
    """
    timeline: dict[str, list] = {}

    for ev in events:
        etype = ev.get("type", {}).get("name", "")
        if etype not in ("Starting XI", "Tactical Shift"):
            continue

        team = ev["team"]["name"]
        tactics = ev.get("tactics", {})
        formation_raw = tactics.get("formation")
        lineup = tactics.get("lineup", [])

        outfield = []
        for p in lineup:
            if p["position"]["name"] != "Goalkeeper":
                outfield.append(p["player"]["name"])

        entry = {
            "minute": ev.get("minute", 0),
            "second": ev.get("second", 0),
            "formation": _formation_str(formation_raw) if formation_raw else "?",
            "formation_raw": str(formation_raw) if formation_raw else "?",
            "players": outfield,
            "event_type": etype,
        }

        timeline.setdefault(team, []).append(entry)

    for team in timeline:
        timeline[team].sort(key=lambda e: (e["minute"], e["second"]))

    return timeline


# ── 2. Collect per-player locations in time windows ─────────────────

def _event_minute(ev: dict) -> float:
    """Return the absolute match minute (period-adjusted)."""
    period = ev.get("period", 1)
    minute = ev.get("minute", 0)
    second = ev.get("second", 0)
    return minute + second / 60.0


def collect_player_locations(
    events: list[dict],
    team: str,
    players: list[str],
    min_minute: float = 0,
    max_minute: float = 999,
) -> dict[str, list]:
    """
    Return {player_name: [(x, y), …]} for events within [min_minute, max_minute].
    Only includes events that have a location field.
    """
    locs: dict[str, list] = {p: [] for p in players}

    for ev in events:
        if ev.get("team", {}).get("name") != team:
            continue
        player = ev.get("player", {}).get("name")
        if player not in locs:
            continue
        if "location" not in ev:
            continue

        m = _event_minute(ev)
        if m < min_minute or m > max_minute:
            continue

        loc = ev["location"]
        if len(loc) >= 2:
            locs[player].append((loc[0], loc[1]))

    return locs


# ── 3. K-Means clustering on X-coordinates ─────────────────────────

def _kmeans_1d(values: list[float], k: int = 3, max_iter: int = 100):
    """
    Minimal 1-D K-Means.  Returns (labels, centroids) both as lists.
    """
    if len(values) < k:
        return list(range(len(values))), list(values)

    # initialise centroids at even quantiles
    sorted_v = sorted(values)
    centroids = [sorted_v[int(i * (len(sorted_v) - 1) / (k - 1))] for i in range(k)]

    for _ in range(max_iter):
        # assign
        labels = []
        for v in values:
            dists = [abs(v - c) for c in centroids]
            labels.append(dists.index(min(dists)))

        # update
        new_c = []
        for ci in range(k):
            members = [values[j] for j in range(len(values)) if labels[j] == ci]
            new_c.append(sum(members) / len(members) if members else centroids[ci])

        if new_c == centroids:
            break
        centroids = new_c

    # re-assign final
    labels = []
    for v in values:
        dists = [abs(v - c) for c in centroids]
        labels.append(dists.index(min(dists)))

    return labels, centroids


def detect_formation_kmeans(
    avg_positions: dict[str, tuple[float, float]],
    k: int = 3,
) -> dict:
    """
    Given {player_name: (mean_x, mean_y)} for 10 outfield players,
    cluster by X-coordinate into *k* lines and return:

      {
        "formation_str": "4-3-3",
        "clusters": {0: [...], 1: [...], 2: [...]},
        "cluster_sizes": [4, 3, 3],
        "centroids": [c0, c1, c2],
        "player_cluster": {name: cluster_idx, …},
      }
    """
    names = list(avg_positions.keys())
    xs = [avg_positions[n][0] for n in names]

    labels, centroids = _kmeans_1d(xs, k=k)

    # sort clusters back→front (low X → high X)
    sorted_idx = sorted(range(k), key=lambda i: centroids[i])
    label_map = {old: new for new, old in enumerate(sorted_idx)}
    mapped = [label_map[l] for l in labels]

    clusters: dict[int, list] = {i: [] for i in range(k)}
    player_cluster: dict[str, int] = {}
    for name, lbl in zip(names, mapped):
        clusters[lbl].append(name)
        player_cluster[name] = lbl

    sizes = [len(clusters[i]) for i in range(k)]
    formation_str = "-".join(str(s) for s in sizes)

    sorted_centroids = [centroids[sorted_idx[i]] for i in range(k)]

    return {
        "formation_str": formation_str,
        "clusters": clusters,
        "cluster_sizes": sizes,
        "centroids": sorted_centroids,
        "player_cluster": player_cluster,
    }


# ── 4. Feature vector for supervised classification ─────────────────

def build_feature_vector(avg_positions: dict[str, tuple[float, float]]) -> dict:
    """
    From {player: (x, y)} build a flat feature dict suitable for
    scikit-learn.

    Features:
      - sorted_x_0 … sorted_x_9, sorted_y_0 … sorted_y_9
        (positions sorted by ascending X — i.e. back to front)
      - team_centroid_x, team_centroid_y
      - team_length  (max X − min X)
      - team_width   (max Y − min Y)
      - std_x, std_y
      - kmeans_def, kmeans_mid, kmeans_att  (cluster sizes)
    """
    if len(avg_positions) < 10:
        return None  # not enough data

    names = list(avg_positions.keys())
    coords = np.array([avg_positions[n] for n in names])

    # Sort by X (back → front)
    order = np.argsort(coords[:, 0])
    sorted_coords = coords[order]

    feat: dict[str, float] = {}

    for i in range(10):
        feat[f"sorted_x_{i}"] = float(sorted_coords[i, 0])
        feat[f"sorted_y_{i}"] = float(sorted_coords[i, 1])

    feat["team_centroid_x"] = float(np.mean(coords[:, 0]))
    feat["team_centroid_y"] = float(np.mean(coords[:, 1]))
    feat["team_length"] = float(np.ptp(coords[:, 0]))
    feat["team_width"] = float(np.ptp(coords[:, 1]))
    feat["std_x"] = float(np.std(coords[:, 0]))
    feat["std_y"] = float(np.std(coords[:, 1]))

    # K-Means cluster sizes
    km = detect_formation_kmeans(avg_positions, k=3)
    feat["kmeans_def"] = km["cluster_sizes"][0]
    feat["kmeans_mid"] = km["cluster_sizes"][1]
    feat["kmeans_att"] = km["cluster_sizes"][2]

    return feat


# ── 5. Rolling-window analysis over a full match ────────────────────

def rolling_formation_analysis(
    events: list[dict],
    team: str,
    window_minutes: int = 10,
    step_minutes: int = 5,
    match_length: int = 95,
) -> list[dict]:
    """
    Slide a *window_minutes*-wide window across the match in steps of
    *step_minutes*.  For each window, compute:
      - avg player positions
      - K-Means detected formation
      - feature vector

    Returns a list of dicts, one per window.
    """
    # Figure out current players from tactical timeline
    timeline = extract_tactical_timeline(events)
    team_timeline = timeline.get(team, [])
    if not team_timeline:
        return []

    # Find all substitutions for this team in the match
    subs = []
    for ev in events:
        if ev.get("type", {}).get("name") == "Substitution" and ev.get("team", {}).get("name") == team:
            minute = ev.get("minute", 0)
            second = ev.get("second", 0)
            player_off = ev.get("player", {}).get("name")
            player_on = ev.get("substitution", {}).get("replacement", {}).get("name")
            if player_off and player_on:
                subs.append({
                    "time": minute + second / 60.0,
                    "player_off": player_off,
                    "player_on": player_on
                })
    subs.sort(key=lambda x: x["time"])

    results = []

    for start in range(0, match_length - window_minutes + 1, step_minutes):
        end = start + window_minutes
        window_midpoint = start + (end - start) / 2.0

        # Determine which outfield players are announced active at this time
        active_entry = team_timeline[0]
        for entry in team_timeline:
            if entry["minute"] <= window_midpoint:
                active_entry = entry
            else:
                break

        announced = active_entry["formation"]
        players = list(active_entry["players"])

        # Apply substitutions that occurred before or at the window's midpoint
        for sub in subs:
            if sub["time"] <= window_midpoint:
                if sub["player_off"] in players:
                    idx = players.index(sub["player_off"])
                    players[idx] = sub["player_on"]

        # Collect locations
        locs = collect_player_locations(events, team, players, start, end)

        # Calculate averages (only include players with enough data)
        avg_pos = {}
        for player, coords in locs.items():
            if len(coords) >= 1:  # need at least 1 event to estimate position
                xs = [c[0] for c in coords]
                ys = [c[1] for c in coords]
                avg_pos[player] = (sum(xs) / len(xs), sum(ys) / len(ys))

        if len(avg_pos) < 8:  # too few players with data
            continue

        # Pad to 10 if we have 8 or 9 — use centroid estimate
        # (This happens rarely; skip padding for cleanliness)
        if len(avg_pos) < 10:
            continue

        km = detect_formation_kmeans(avg_pos, k=3)
        feat = build_feature_vector(avg_pos)

        results.append({
            "window_start": start,
            "window_end": end,
            "announced_formation": announced,
            "detected_formation": km["formation_str"],
            "avg_positions": avg_pos,
            "kmeans_result": km,
            "features": feat,
        })

    return results


# ── CLI smoke test ──────────────────────────────────────────────────
if __name__ == "__main__":
    from data_loader import get_matches, get_events, match_label

    matches = get_matches(2022)
    m = matches[0]
    print(f"Match: {match_label(m)}")

    events = get_events(m["match_id"])
    timeline = extract_tactical_timeline(events)

    for team, entries in timeline.items():
        print(f"\n{team}:")
        for e in entries:
            print(f"  {e['minute']}' [{e['event_type']}] -> {e['formation']}")

        results = rolling_formation_analysis(events, team)
        print(f"  Rolling windows: {len(results)}")
        for r in results[:3]:
            print(f"    {r['window_start']}–{r['window_end']}': "
                  f"announced={r['announced_formation']}  "
                  f"detected={r['detected_formation']}")
