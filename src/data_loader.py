"""
data_loader.py — StatsBomb Open Data fetcher and local cache layer.

Downloads match lists and event JSONs from the StatsBomb open-data
GitHub repository and caches them under  data/  so subsequent runs
are instant.
"""

import json
import os
import requests
from pathlib import Path

# ── Constants ───────────────────────────────────────────────────────
BASE_URL = "https://raw.githubusercontent.com/statsbomb/open-data/master/data"
COMPETITION_ID = 43  # FIFA World Cup

WORLD_CUP_SEASONS = {
    2026: 120,
    2022: 106,
    2018: 3,
}

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


# ── Low-level helpers ───────────────────────────────────────────────

def _ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def _fetch_json(url: str) -> dict | list:
    """Download JSON from *url* and return parsed Python object."""
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    return resp.json()


def _read_cache(path: Path):
    """Return parsed JSON from a cached file, or None if missing."""
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


def _write_cache(path: Path, data) -> None:
    """Persist *data* as JSON to *path*."""
    _ensure_dir(path.parent)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)


# ── Public API ──────────────────────────────────────────────────────

def get_matches(year: int) -> list[dict]:
    """
    Return the list of match dicts for the given World Cup *year*.

    Downloads from GitHub on first call; cached locally afterward.
    """
    season_id = WORLD_CUP_SEASONS[year]
    cache_path = DATA_DIR / "matches" / f"{COMPETITION_ID}" / f"{season_id}.json"

    cached = _read_cache(cache_path)
    if cached is not None:
        return cached

    url = f"{BASE_URL}/matches/{COMPETITION_ID}/{season_id}.json"
    data = _fetch_json(url)
    _write_cache(cache_path, data)
    return data


def get_events(match_id: int) -> list[dict]:
    """
    Return the full event list for a single match.

    Downloads from GitHub on first call; cached locally afterward.
    """
    cache_path = DATA_DIR / "events" / f"{match_id}.json"

    cached = _read_cache(cache_path)
    if cached is not None:
        return cached

    url = f"{BASE_URL}/events/{match_id}.json"
    data = _fetch_json(url)
    _write_cache(cache_path, data)
    return data


def get_all_matches() -> list[dict]:
    """Return matches for every World Cup year we support, merged."""
    all_matches = []
    for year in WORLD_CUP_SEASONS:
        matches = get_matches(year)
        for m in matches:
            m["_wc_year"] = year
        all_matches.extend(matches)
    return all_matches


def match_label(match: dict) -> str:
    """Human-readable label for a match dict."""
    home = match["home_team"]["home_team_name"]
    away = match["away_team"]["away_team_name"]
    score_h = match.get("home_score", "?")
    score_a = match.get("away_score", "?")
    return f"{home} {score_h}–{score_a} {away}"


# ── CLI smoke test ──────────────────────────────────────────────────
if __name__ == "__main__":
    for year in WORLD_CUP_SEASONS:
        matches = get_matches(year)
        print(f"World Cup {year}: {len(matches)} matches")
        if matches:
            print(f"  Sample: {match_label(matches[0])}")

    # Smoke-test event fetching
    sample = get_matches(2022)[0]
    events = get_events(sample["match_id"])
    print(f"\nEvents for {match_label(sample)}: {len(events)} events")
