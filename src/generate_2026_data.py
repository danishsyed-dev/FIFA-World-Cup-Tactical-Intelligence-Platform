"""
generate_2026_data.py — Generate mock matches and event JSON files for the
2026 FIFA World Cup matching the actual groups (A-L) and fixtures.
"""

import json
import uuid
import random
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

# Create directories if they don't exist
(DATA_DIR / "matches" / "43").mkdir(parents=True, exist_ok=True)
(DATA_DIR / "events").mkdir(parents=True, exist_ok=True)

# ── 1. Match List for Season 120 (WC 2026) ──
matches_2026 = [
    # Group A
    {
        "match_id": 2026001, "match_date": "2026-06-11", "kick_off": "18:00:00.000",
        "competition": {"competition_id": 43, "country_name": "International", "competition_name": "FIFA World Cup"},
        "season": {"season_id": 120, "season_name": "2026"},
        "home_team": {"home_team_id": 201, "home_team_name": "Mexico", "home_team_group": "A"},
        "away_team": {"away_team_id": 202, "away_team_name": "South Africa", "away_team_group": "A"},
        "home_score": 2, "away_score": 0, "match_status": "available", "match_week": 1,
        "competition_stage": {"id": 10, "name": "Group Stage"},
        "stadium": {"name": "Estadio Azteca", "country": {"name": "Mexico"}},
        "referee": {"name": "Gianluca Rocchi", "country": {"name": "Italy"}}
    },
    {
        "match_id": 2026002, "match_date": "2026-06-12", "kick_off": "15:00:00.000",
        "competition": {"competition_id": 43, "country_name": "International", "competition_name": "FIFA World Cup"},
        "season": {"season_id": 120, "season_name": "2026"},
        "home_team": {"home_team_id": 203, "home_team_name": "South Korea", "home_team_group": "A"},
        "away_team": {"away_team_id": 204, "away_team_name": "Czechia", "away_team_group": "A"},
        "home_score": 2, "away_score": 1, "match_status": "available", "match_week": 1,
        "competition_stage": {"id": 10, "name": "Group Stage"},
        "stadium": {"name": "Guadalajara Stadium", "country": {"name": "Mexico"}},
        "referee": {"name": "Szymon Marciniak", "country": {"name": "Poland"}}
    },
    {
        "match_id": 2026003, "match_date": "2026-06-18", "kick_off": "20:00:00.000",
        "competition": {"competition_id": 43, "country_name": "International", "competition_name": "FIFA World Cup"},
        "season": {"season_id": 120, "season_name": "2026"},
        "home_team": {"home_team_id": 201, "home_team_name": "Mexico", "home_team_group": "A"},
        "away_team": {"away_team_id": 203, "away_team_name": "South Korea", "away_team_group": "A"},
        "home_score": 1, "away_score": 0, "match_status": "available", "match_week": 2,
        "competition_stage": {"id": 10, "name": "Group Stage"},
        "stadium": {"name": "Guadalajara Stadium", "country": {"name": "Mexico"}},
        "referee": {"name": "Michael Oliver", "country": {"name": "England"}}
    },
    {
        "match_id": 2026004, "match_date": "2026-06-18", "kick_off": "17:00:00.000",
        "competition": {"competition_id": 43, "country_name": "International", "competition_name": "FIFA World Cup"},
        "season": {"season_id": 120, "season_name": "2026"},
        "home_team": {"home_team_id": 202, "home_team_name": "South Africa", "home_team_group": "A"},
        "away_team": {"away_team_id": 204, "away_team_name": "Czechia", "away_team_group": "A"},
        "home_score": 1, "away_score": 1, "match_status": "available", "match_week": 2,
        "competition_stage": {"id": 10, "name": "Group Stage"},
        "stadium": {"name": "Estadio Monterrey", "country": {"name": "Mexico"}},
        "referee": {"name": "Wilton Sampaio", "country": {"name": "Brazil"}}
    },
    # Group B
    {
        "match_id": 2026005, "match_date": "2026-06-12", "kick_off": "18:00:00.000",
        "competition": {"competition_id": 43, "country_name": "International", "competition_name": "FIFA World Cup"},
        "season": {"season_id": 120, "season_name": "2026"},
        "home_team": {"home_team_id": 205, "home_team_name": "Canada", "home_team_group": "B"},
        "away_team": {"away_team_id": 206, "away_team_name": "Bosnia and Herzegovina", "away_team_group": "B"},
        "home_score": 1, "away_score": 1, "match_status": "available", "match_week": 1,
        "competition_stage": {"id": 10, "name": "Group Stage"},
        "stadium": {"name": "BC Place", "country": {"name": "Canada"}},
        "referee": {"name": "Clement Turpin", "country": {"name": "France"}}
    },
    {
        "match_id": 2026006, "match_date": "2026-06-13", "kick_off": "15:00:00.000",
        "competition": {"competition_id": 43, "country_name": "International", "competition_name": "FIFA World Cup"},
        "season": {"season_id": 120, "season_name": "2026"},
        "home_team": {"home_team_id": 207, "home_team_name": "Qatar", "home_team_group": "B"},
        "away_team": {"away_team_id": 208, "away_team_name": "Switzerland", "away_team_group": "B"},
        "home_score": 1, "away_score": 1, "match_status": "available", "match_week": 1,
        "competition_stage": {"id": 10, "name": "Group Stage"},
        "stadium": {"name": "Toronto Stadium", "country": {"name": "Canada"}},
        "referee": {"name": "Daniele Orsato", "country": {"name": "Italy"}}
    },
    {
        "match_id": 2026007, "match_date": "2026-06-17", "kick_off": "18:00:00.000",
        "competition": {"competition_id": 43, "country_name": "International", "competition_name": "FIFA World Cup"},
        "season": {"season_id": 120, "season_name": "2026"},
        "home_team": {"home_team_id": 208, "home_team_name": "Switzerland", "home_team_group": "B"},
        "away_team": {"away_team_id": 206, "away_team_name": "Bosnia and Herzegovina", "away_team_group": "B"},
        "home_score": 4, "away_score": 1, "match_status": "available", "match_week": 2,
        "competition_stage": {"id": 10, "name": "Group Stage"},
        "stadium": {"name": "BC Place", "country": {"name": "Canada"}},
        "referee": {"name": "Gianluca Rocchi", "country": {"name": "Italy"}}
    },
    {
        "match_id": 2026008, "match_date": "2026-06-17", "kick_off": "20:00:00.000",
        "competition": {"competition_id": 43, "country_name": "International", "competition_name": "FIFA World Cup"},
        "season": {"season_id": 120, "season_name": "2026"},
        "home_team": {"home_team_id": 205, "home_team_name": "Canada", "home_team_group": "B"},
        "away_team": {"away_team_id": 207, "away_team_name": "Qatar", "home_team_group": "B"},
        "home_score": 6, "away_score": 0, "match_status": "available", "match_week": 2,
        "competition_stage": {"id": 10, "name": "Group Stage"},
        "stadium": {"name": "Toronto Stadium", "country": {"name": "Canada"}},
        "referee": {"name": "Michael Oliver", "country": {"name": "England"}}
    },
    # Group C
    {
        "match_id": 2026009, "match_date": "2026-06-13", "kick_off": "18:00:00.000",
        "competition": {"competition_id": 43, "country_name": "International", "competition_name": "FIFA World Cup"},
        "season": {"season_id": 120, "season_name": "2026"},
        "home_team": {"home_team_id": 209, "home_team_name": "Brazil", "home_team_group": "C"},
        "away_team": {"away_team_id": 210, "away_team_name": "Morocco", "away_team_group": "C"},
        "home_score": 1, "away_score": 1, "match_status": "available", "match_week": 1,
        "competition_stage": {"id": 10, "name": "Group Stage"},
        "stadium": {"name": "Mercedes-Benz Stadium", "country": {"name": "United States"}},
        "referee": {"name": "Szymon Marciniak", "country": {"name": "Poland"}}
    },
    {
        "match_id": 2026010, "match_date": "2026-06-13", "kick_off": "20:00:00.000",
        "competition": {"competition_id": 43, "country_name": "International", "competition_name": "FIFA World Cup"},
        "season": {"season_id": 120, "season_name": "2026"},
        "home_team": {"home_team_id": 211, "home_team_name": "Scotland", "home_team_group": "C"},
        "away_team": {"away_team_id": 212, "away_team_name": "Haiti", "away_team_group": "C"},
        "home_score": 1, "away_score": 0, "match_status": "available", "match_week": 1,
        "competition_stage": {"id": 10, "name": "Group Stage"},
        "stadium": {"name": "Hard Rock Stadium", "country": {"name": "United States"}},
        "referee": {"name": "Gianluca Rocchi", "country": {"name": "Italy"}}
    },
    {
        "match_id": 2026011, "match_date": "2026-06-20", "kick_off": "15:00:00.000",
        "competition": {"competition_id": 43, "country_name": "International", "competition_name": "FIFA World Cup"},
        "season": {"season_id": 120, "season_name": "2026"},
        "home_team": {"home_team_id": 209, "home_team_name": "Brazil", "home_team_group": "C"},
        "away_team": {"away_team_id": 212, "away_team_name": "Haiti", "away_team_group": "C"},
        "home_score": 3, "away_score": 0, "match_status": "available", "match_week": 2,
        "competition_stage": {"id": 10, "name": "Group Stage"},
        "stadium": {"name": "Philadelphia Stadium", "country": {"name": "United States"}},
        "referee": {"name": "Clement Turpin", "country": {"name": "France"}}
    },
    {
        "match_id": 2026012, "match_date": "2026-06-20", "kick_off": "18:00:00.000",
        "competition": {"competition_id": 43, "country_name": "International", "competition_name": "FIFA World Cup"},
        "season": {"season_id": 120, "season_name": "2026"},
        "home_team": {"home_team_id": 211, "home_team_name": "Scotland", "home_team_group": "C"},
        "away_team": {"away_team_id": 210, "away_team_name": "Morocco", "away_team_group": "C"},
        "home_score": 0, "away_score": 1, "match_status": "available", "match_week": 2,
        "competition_stage": {"id": 10, "name": "Group Stage"},
        "stadium": {"name": "NRG Stadium", "country": {"name": "United States"}},
        "referee": {"name": "Daniele Orsato", "country": {"name": "Italy"}}
    },
    # Group D
    {
        "match_id": 2026013, "match_date": "2026-06-12", "kick_off": "20:00:00.000",
        "competition": {"competition_id": 43, "country_name": "International", "competition_name": "FIFA World Cup"},
        "season": {"season_id": 120, "season_name": "2026"},
        "home_team": {"home_team_id": 213, "home_team_name": "United States", "home_team_group": "D"},
        "away_team": {"away_team_id": 214, "away_team_name": "Paraguay", "away_team_group": "D"},
        "home_score": 4, "away_score": 1, "match_status": "available", "match_week": 1,
        "competition_stage": {"id": 10, "name": "Group Stage"},
        "stadium": {"name": "SoFi Stadium", "country": {"name": "United States"}},
        "referee": {"name": "Szymon Marciniak", "country": {"name": "Poland"}}
    },
    {
        "match_id": 2026014, "match_date": "2026-06-13", "kick_off": "20:00:00.000",
        "competition": {"competition_id": 43, "country_name": "International", "competition_name": "FIFA World Cup"},
        "season": {"season_id": 120, "season_name": "2026"},
        "home_team": {"home_team_id": 215, "home_team_name": "Australia", "home_team_group": "D"},
        "away_team": {"away_team_id": 216, "away_team_name": "Turkey", "away_team_group": "D"},
        "home_score": 2, "away_score": 0, "match_status": "available", "match_week": 1,
        "competition_stage": {"id": 10, "name": "Group Stage"},
        "stadium": {"name": "MetLife Stadium", "country": {"name": "United States"}},
        "referee": {"name": "Michael Oliver", "country": {"name": "England"}}
    },
    {
        "match_id": 2026015, "match_date": "2026-06-17", "kick_off": "15:00:00.000",
        "competition": {"competition_id": 43, "country_name": "International", "competition_name": "FIFA World Cup"},
        "season": {"season_id": 120, "season_name": "2026"},
        "home_team": {"home_team_id": 213, "home_team_name": "United States", "home_team_group": "D"},
        "away_team": {"away_team_id": 215, "away_team_name": "Australia", "away_team_group": "D"},
        "home_score": 2, "away_score": 0, "match_status": "available", "match_week": 2,
        "competition_stage": {"id": 10, "name": "Group Stage"},
        "stadium": {"name": "SoFi Stadium", "country": {"name": "United States"}},
        "referee": {"name": "Gianluca Rocchi", "country": {"name": "Italy"}}
    },
    {
        "match_id": 2026016, "match_date": "2026-06-17", "kick_off": "18:00:00.000",
        "competition": {"competition_id": 43, "country_name": "International", "competition_name": "FIFA World Cup"},
        "season": {"season_id": 120, "season_name": "2026"},
        "home_team": {"home_team_id": 216, "home_team_name": "Turkey", "home_team_group": "D"},
        "away_team": {"away_team_id": 214, "away_team_name": "Paraguay", "away_team_group": "D"},
        "home_score": 0, "away_score": 1, "match_status": "available", "match_week": 2,
        "competition_stage": {"id": 10, "name": "Group Stage"},
        "stadium": {"name": "Houston Stadium", "country": {"name": "United States"}},
        "referee": {"name": "Wilton Sampaio", "country": {"name": "Brazil"}}
    },
    # Group E
    {
        "match_id": 2026017, "match_date": "2026-06-14", "kick_off": "18:00:00.000",
        "competition": {"competition_id": 43, "country_name": "International", "competition_name": "FIFA World Cup"},
        "season": {"season_id": 120, "season_name": "2026"},
        "home_team": {"home_team_id": 217, "home_team_name": "Germany", "home_team_group": "E"},
        "away_team": {"away_team_id": 218, "away_team_name": "Curaçao", "away_team_group": "E"},
        "home_score": 7, "away_score": 1, "match_status": "available", "match_week": 1,
        "competition_stage": {"id": 10, "name": "Group Stage"},
        "stadium": {"name": "Toronto Stadium", "country": {"name": "Canada"}},
        "referee": {"name": "Szymon Marciniak", "country": {"name": "Poland"}}
    },
    {
        "match_id": 2026018, "match_date": "2026-06-14", "kick_off": "20:00:00.000",
        "competition": {"competition_id": 43, "country_name": "International", "competition_name": "FIFA World Cup"},
        "season": {"season_id": 120, "season_name": "2026"},
        "home_team": {"home_team_id": 219, "home_team_name": "Ivory Coast", "home_team_group": "E"},
        "away_team": {"away_team_id": 220, "away_team_name": "Ecuador", "away_team_group": "E"},
        "home_score": 1, "away_score": 0, "match_status": "available", "match_week": 1,
        "competition_stage": {"id": 10, "name": "Group Stage"},
        "stadium": {"name": "BC Place", "country": {"name": "Canada"}},
        "referee": {"name": "Michael Oliver", "country": {"name": "England"}}
    },
    # Group F
    {
        "match_id": 2026019, "match_date": "2026-06-14", "kick_off": "15:00:00.000",
        "competition": {"competition_id": 43, "country_name": "International", "competition_name": "FIFA World Cup"},
        "season": {"season_id": 120, "season_name": "2026"},
        "home_team": {"home_team_id": 221, "home_team_name": "Netherlands", "home_team_group": "F"},
        "away_team": {"away_team_id": 222, "away_team_name": "Japan", "away_team_group": "F"},
        "home_score": 2, "away_score": 2, "match_status": "available", "match_week": 1,
        "competition_stage": {"id": 10, "name": "Group Stage"},
        "stadium": {"name": "Lumen Field", "country": {"name": "United States"}},
        "referee": {"name": "Clement Turpin", "country": {"name": "France"}}
    },
    {
        "match_id": 2026020, "match_date": "2026-06-14", "kick_off": "18:00:00.000",
        "competition": {"competition_id": 43, "country_name": "International", "competition_name": "FIFA World Cup"},
        "season": {"season_id": 120, "season_name": "2026"},
        "home_team": {"home_team_id": 223, "home_team_name": "Sweden", "home_team_group": "F"},
        "away_team": {"away_team_id": 224, "away_team_name": "Tunisia", "away_team_group": "F"},
        "home_score": 5, "away_score": 1, "match_status": "available", "match_week": 1,
        "competition_stage": {"id": 10, "name": "Group Stage"},
        "stadium": {"name": "Seattle Stadium", "country": {"name": "United States"}},
        "referee": {"name": "Daniele Orsato", "country": {"name": "Italy"}}
    },
    # Group G
    {
        "match_id": 2026021, "match_date": "2026-06-15", "kick_off": "18:00:00.000",
        "competition": {"competition_id": 43, "country_name": "International", "competition_name": "FIFA World Cup"},
        "season": {"season_id": 120, "season_name": "2026"},
        "home_team": {"home_team_id": 225, "home_team_name": "Belgium", "home_team_group": "G"},
        "away_team": {"away_team_id": 226, "away_team_name": "Egypt", "away_team_group": "G"},
        "home_score": 1, "away_score": 1, "match_status": "available", "match_week": 1,
        "competition_stage": {"id": 10, "name": "Group Stage"},
        "stadium": {"name": "Houston Stadium", "country": {"name": "United States"}},
        "referee": {"name": "Gianluca Rocchi", "country": {"name": "Italy"}}
    },
    {
        "match_id": 2026022, "match_date": "2026-06-15", "kick_off": "20:00:00.000",
        "competition": {"competition_id": 43, "country_name": "International", "competition_name": "FIFA World Cup"},
        "season": {"season_id": 120, "season_name": "2026"},
        "home_team": {"home_team_id": 227, "home_team_name": "Iran", "home_team_group": "G"},
        "away_team": {"away_team_id": 228, "away_team_name": "New Zealand", "away_team_group": "G"},
        "home_score": 2, "away_score": 2, "match_status": "available", "match_week": 1,
        "competition_stage": {"id": 10, "name": "Group Stage"},
        "stadium": {"name": "Los Angeles Stadium", "country": {"name": "United States"}},
        "referee": {"name": "Wilton Sampaio", "country": {"name": "Brazil"}}
    },
    # Group H
    {
        "match_id": 2026023, "match_date": "2026-06-15", "kick_off": "15:00:00.000",
        "competition": {"competition_id": 43, "country_name": "International", "competition_name": "FIFA World Cup"},
        "season": {"season_id": 120, "season_name": "2026"},
        "home_team": {"home_team_id": 229, "home_team_name": "Spain", "home_team_group": "H"},
        "away_team": {"away_team_id": 230, "away_team_name": "Cape Verde", "away_team_group": "H"},
        "home_score": 0, "away_score": 0, "match_status": "available", "match_week": 1,
        "competition_stage": {"id": 10, "name": "Group Stage"},
        "stadium": {"name": "Mercedes-Benz Stadium", "country": {"name": "United States"}},
        "referee": {"name": "Clement Turpin", "country": {"name": "France"}}
    },
    {
        "match_id": 2026024, "match_date": "2026-06-15", "kick_off": "18:00:00.000",
        "competition": {"competition_id": 43, "country_name": "International", "competition_name": "FIFA World Cup"},
        "season": {"season_id": 120, "season_name": "2026"},
        "home_team": {"home_team_id": 231, "home_team_name": "Saudi Arabia", "home_team_group": "H"},
        "away_team": {"away_team_id": 232, "away_team_name": "Uruguay", "away_team_group": "H"},
        "home_score": 1, "away_score": 1, "match_status": "available", "match_week": 1,
        "competition_stage": {"id": 10, "name": "Group Stage"},
        "stadium": {"name": "Hard Rock Stadium", "country": {"name": "United States"}},
        "referee": {"name": "Michael Oliver", "country": {"name": "England"}}
    },
    # Group I
    {
        "match_id": 2026025, "match_date": "2026-06-16", "kick_off": "18:00:00.000",
        "competition": {"competition_id": 43, "country_name": "International", "competition_name": "FIFA World Cup"},
        "season": {"season_id": 120, "season_name": "2026"},
        "home_team": {"home_team_id": 233, "home_team_name": "France", "home_team_group": "I"},
        "away_team": {"away_team_id": 234, "away_team_name": "Senegal", "away_team_group": "I"},
        "home_score": 3, "away_score": 1, "match_status": "available", "match_week": 1,
        "competition_stage": {"id": 10, "name": "Group Stage"},
        "stadium": {"name": "MetLife Stadium", "country": {"name": "United States"}},
        "referee": {"name": "Szymon Marciniak", "country": {"name": "Poland"}}
    },
    {
        "match_id": 2026026, "match_date": "2026-06-16", "kick_off": "20:00:00.000",
        "competition": {"competition_id": 43, "country_name": "International", "competition_name": "FIFA World Cup"},
        "season": {"season_id": 120, "season_name": "2026"},
        "home_team": {"home_team_id": 235, "home_team_name": "Norway", "home_team_group": "I"},
        "away_team": {"away_team_id": 236, "away_team_name": "Iraq", "away_team_group": "I"},
        "home_score": 4, "away_score": 1, "match_status": "available", "match_week": 1,
        "competition_stage": {"id": 10, "name": "Group Stage"},
        "stadium": {"name": "Boston Stadium", "country": {"name": "United States"}},
        "referee": {"name": "Gianluca Rocchi", "country": {"name": "Italy"}}
    },
    # Group J
    {
        "match_id": 2026027, "match_date": "2026-06-16", "kick_off": "15:00:00.000",
        "competition": {"competition_id": 43, "country_name": "International", "competition_name": "FIFA World Cup"},
        "season": {"season_id": 120, "season_name": "2026"},
        "home_team": {"home_team_id": 237, "home_team_name": "Argentina", "home_team_group": "J"},
        "away_team": {"away_team_id": 238, "away_team_name": "Algeria", "away_team_group": "J"},
        "home_score": 3, "away_score": 0, "match_status": "available", "match_week": 1,
        "competition_stage": {"id": 10, "name": "Group Stage"},
        "stadium": {"name": "Dallas Stadium", "country": {"name": "United States"}},
        "referee": {"name": "Daniele Orsato", "country": {"name": "Italy"}}
    },
    {
        "match_id": 2026028, "match_date": "2026-06-17", "kick_off": "18:00:00.000",
        "competition": {"competition_id": 43, "country_name": "International", "competition_name": "FIFA World Cup"},
        "season": {"season_id": 120, "season_name": "2026"},
        "home_team": {"home_team_id": 239, "home_team_name": "Austria", "home_team_group": "J"},
        "away_team": {"away_team_id": 240, "away_team_name": "Jordan", "away_team_group": "J"},
        "home_score": 3, "away_score": 1, "match_status": "available", "match_week": 1,
        "competition_stage": {"id": 10, "name": "Group Stage"},
        "stadium": {"name": "Mercedes-Benz Stadium", "country": {"name": "United States"}},
        "referee": {"name": "Clement Turpin", "country": {"name": "France"}}
    },
    # Group K
    {
        "match_id": 2026029, "match_date": "2026-06-17", "kick_off": "20:00:00.000",
        "competition": {"competition_id": 43, "country_name": "International", "competition_name": "FIFA World Cup"},
        "season": {"season_id": 120, "season_name": "2026"},
        "home_team": {"home_team_id": 241, "home_team_name": "Portugal", "home_team_group": "K"},
        "away_team": {"away_team_id": 242, "away_team_name": "DR Congo", "away_team_group": "K"},
        "home_score": 1, "away_score": 1, "match_status": "available", "match_week": 1,
        "competition_stage": {"id": 10, "name": "Group Stage"},
        "stadium": {"name": "Houston Stadium", "country": {"name": "United States"}},
        "referee": {"name": "Michael Oliver", "country": {"name": "England"}}
    },
    {
        "match_id": 2026030, "match_date": "2026-06-17", "kick_off": "15:00:00.000",
        "competition": {"competition_id": 43, "country_name": "International", "competition_name": "FIFA World Cup"},
        "season": {"season_id": 120, "season_name": "2026"},
        "home_team": {"home_team_id": 243, "home_team_name": "Colombia", "home_team_group": "K"},
        "away_team": {"away_team_id": 244, "away_team_name": "Uzbekistan", "away_team_group": "K"},
        "home_score": 3, "away_score": 1, "match_status": "available", "match_week": 1,
        "competition_stage": {"id": 10, "name": "Group Stage"},
        "stadium": {"name": "Monterrey Stadium", "country": {"name": "Mexico"}},
        "referee": {"name": "Wilton Sampaio", "country": {"name": "Brazil"}}
    },
    # Group L
    {
        "match_id": 2026031, "match_date": "2026-06-17", "kick_off": "18:00:00.000",
        "competition": {"competition_id": 43, "country_name": "International", "competition_name": "FIFA World Cup"},
        "season": {"season_id": 120, "season_name": "2026"},
        "home_team": {"home_team_id": 245, "home_team_name": "England", "home_team_group": "L"},
        "away_team": {"away_team_id": 246, "away_team_name": "Croatia", "away_team_group": "L"},
        "home_score": 4, "away_score": 2, "match_status": "available", "match_week": 1,
        "competition_stage": {"id": 10, "name": "Group Stage"},
        "stadium": {"name": "Dallas Stadium", "country": {"name": "United States"}},
        "referee": {"name": "Gianluca Rocchi", "country": {"name": "Italy"}}
    },
    {
        "match_id": 2026032, "match_date": "2026-06-17", "kick_off": "20:00:00.000",
        "competition": {"competition_id": 43, "country_name": "International", "competition_name": "FIFA World Cup"},
        "season": {"season_id": 120, "season_name": "2026"},
        "home_team": {"home_team_id": 247, "home_team_name": "Ghana", "home_team_group": "L"},
        "away_team": {"away_team_id": 248, "away_team_name": "Panama", "away_team_group": "L"},
        "home_score": 1, "away_score": 0, "match_status": "available", "match_week": 1,
        "competition_stage": {"id": 10, "name": "Group Stage"},
        "stadium": {"name": "Dallas Stadium", "country": {"name": "United States"}},
        "referee": {"name": "Wilton Sampaio", "country": {"name": "Brazil"}}
    }
]

# Write matches JSON
with open(DATA_DIR / "matches" / "43" / "120.json", "w", encoding="utf-8") as f:
    json.dump(matches_2026, f, indent=2)


# ── 2. Squad Definitions ──
SQUADS = {
    # Hosts
    "United States": {
        "GK": "Matt Turner",
        "outfield": ["Antonee Robinson", "Tim Ream", "Chris Richards", "Sergino Dest", "Tyler Adams", "Weston McKennie", "Yunus Musah", "Christian Pulisic", "Folarin Balogun", "Timothy Weah"]
    },
    "Mexico": {
        "GK": "Guillermo Ochoa",
        "outfield": ["Jesus Gallardo", "Cesar Montes", "Johan Vasquez", "Jorge Sanchez", "Edson Alvarez", "Luis Chavez", "Erick Sanchez", "Hirving Lozano", "Santiago Gimenez", "Uriel Antuna"]
    },
    "Canada": {
        "GK": "Maxime Crepeau",
        "outfield": ["Alphonso Davies", "Kamal Miller", "Alistair Johnston", "Richie Laryea", "Stephen Eustaquio", "Ismael Kone", "Jonathan Osorio", "Cyle Larin", "Jonathan David", "Tajon Buchanan"]
    },
    # Main Teams
    "England": {
        "GK": "Jordan Pickford",
        "outfield": ["Luke Shaw", "John Stones", "Harry Maguire", "Kyle Walker", "Declan Rice", "Jude Bellingham", "Conor Gallagher", "Phil Foden", "Harry Kane", "Bukayo Saka"]
    },
    "Iran": {
        "GK": "Alireza Beiranvand",
        "outfield": ["Milad Mohammadi", "Majid Hosseini", "Morteza Pouraliganji", "Sadegh Moharrami", "Saeid Ezatolahi", "Ahmad Nourollahi", "Ehsan Hajsafi", "Mehdi Taremi", "Sardar Azmoun", "Alireza Jahanbakhsh"]
    },
    "Argentina": {
        "GK": "Emiliano Martinez",
        "outfield": ["Nicolas Tagliafico", "Nicolas Otamendi", "Cristian Romero", "Nahuel Molina", "Enzo Fernandez", "Alexis Mac Allister", "Rodrigo De Paul", "Angel Di Maria", "Lautaro Martinez", "Lionel Messi"]
    },
    "Portugal": {
        "GK": "Diogo Costa",
        "outfield": ["Joao Cancelo", "Ruben Dias", "Pepe", "Nuno Mendes", "Bruno Fernandes", "Ruben Neves", "Vitinha", "Bernardo Silva", "Cristiano Ronaldo", "Joao Felix"]
    },
    "France": {
        "GK": "Mike Maignan",
        "outfield": ["Theo Hernandez", "Dayot Upamecano", "William Saliba", "Jules Kounde", "Aurelien Tchouameni", "Adrien Rabiot", "Antoine Griezmann", "Kylian Mbappe", "Olivier Giroud", "Ousmane Dembele"]
    },
    "Morocco": {
        "GK": "Yassine Bounou",
        "outfield": ["Achraf Hakimi", "Nayef Aguerd", "Romain Saiss", "Noussair Mazraoui", "Sofyan Amrabat", "Azzedine Ounahi", "Selim Amallah", "Hakim Ziyech", "Youssef En-Nesyri", "Sofiane Boufal"]
    },
    "South Africa": {
        "GK": "R. Williams",
        "outfield": ["A. Modiba", "M. Mvala", "G. Kekana", "K. Mudau", "S. Sithole", "T. Mokoena", "T. Zwane", "P. Tau", "E. Makgopa", "T. Morena"]
    },
    "Czechia": {
        "GK": "J. Stanek",
        "outfield": ["V. Coufal", "T. Holes", "D. Zima", "L. Krejci", "T. Soucek", "L. Provod", "A. Barak", "V. Cerny", "P. Schick", "J. Kuchta"]
    },
    "South Korea": {
        "GK": "Jo Hyeon-woo",
        "outfield": ["Kim Min-jae", "Kim Young-gwon", "Kim Jin-su", "Kim Moon-hwan", "Hwang In-beom", "Lee Jae-sung", "Jung Woo-young", "Son Heung-min", "Hwang Hee-chan", "Cho Gue-sung"]
    },
    "Bosnia and Herzegovina": {
        "GK": "N. Vasilj",
        "outfield": ["A. Dedic", "N. Radeljic", "D. Hadzikadunic", "S. Kolasinac", "R. Krunic", "B. Tahirovic", "H. Hajradinovic", "E. Demirovic", "E. Dzeko", "H. Tabakovic"]
    },
    "Qatar": {
        "GK": "Meshaal Barsham",
        "outfield": ["Lucas Mendes", "Al-Mahdi Ali", "Pedro Miguel", "Homam Ahmed", "Jassem Gaber", "Ahmed Fathy", "Hassan Al-Haydos", "Akram Afif", "Almoez Ali", "Yusuf Abdurisag"]
    },
    "Switzerland": {
        "GK": "Yann Sommer",
        "outfield": ["Manuel Akanji", "Nico Elvedi", "Ricardo Rodriguez", "Silvan Widmer", "Remo Freuler", "Granit Xhaka", "Michel Aebischer", "Ruben Vargas", "Dan Ndoye", "Breel Embolo"]
    },
    "Brazil": {
        "GK": "Alisson",
        "outfield": ["Danilo", "Marquinhos", "Gabriel Magalhaes", "Wendell", "Bruno Guimaraes", "Joao Gomes", "Lucas Paqueta", "Raphinha", "Rodrygo", "Vinicius Junior"]
    },
    "Haiti": {
        "GK": "J. Placide",
        "outfield": ["Carlens Arcus", "Garven Metusala", "Ricardo Ade", "Alex Christian", "Bryan Alceus", "Danley Jean Jacques", "W. Guerrier", "Derrick Etienne", "Frantzdy Pierrot", "Duckens Nazon"]
    },
    "Scotland": {
        "GK": "Angus Gunn",
        "outfield": ["Jack Hendry", "Grant Hanley", "Kieran Tierney", "Anthony Ralston", "Billy Gilmour", "Callum McGregor", "Andrew Robertson", "Scott McTominay", "John McGinn", "Che Adams"]
    },
    "Paraguay": {
        "GK": "Carlos Coronel",
        "outfield": ["Gustavo Gomez", "Fabian Balbuena", "Junior Alonso", "Robert Rojas", "Mathias Villasanti", "Andres Cubas", "Diego Gomez", "Miguel Almiron", "Julio Enciso", "Ramon Sosa"]
    },
    "Australia": {
        "GK": "Mathew Ryan",
        "outfield": ["Aziz Behich", "Harry Souttar", "Kye Rowles", "Gethin Jones", "Jackson Irvine", "Keanu Baccus", "Connor Metcalfe", "Craig Goodwin", "Kusini Yengi", "Jordan Bos"]
    },
    "Turkey": {
        "GK": "Mert Gunok",
        "outfield": ["Merih Demiral", "Abdulkerim Bardakci", "Ferdi Kadioglu", "Zeki Celik", "Kaan Ayhan", "H. Calhanoglu", "Orkun Kokcu", "Arda Guler", "Kenan Yildiz", "B. Yilmaz"]
    },
    "Germany": {
        "GK": "Manuel Neuer",
        "outfield": ["Maximilian Mittelstadt", "Jonathan Tah", "Antonio Rudiger", "Joshua Kimmich", "Robert Andrich", "Toni Kroos", "Ilkay Gundogan", "Jamal Musiala", "Florian Wirtz", "Kai Havertz"]
    },
    "Curaçao": {
        "GK": "Eloy Room",
        "outfield": ["Sherel Floranus", "Jurien Gaari", "Cuco Martina", "Jurnet Brand", "Vurnon Anita", "Leandro Bacuna", "Juninho Bacuna", "Kenji Gorre", "Rangelo Janga", "Gervane Kastaneer"]
    },
    "Ivory Coast": {
        "GK": "Yahia Fofana",
        "outfield": ["Ghislain Konan", "Evan Ndicka", "Ousmane Diomande", "Wilfried Singo", "Seko Fofana", "Franck Kessie", "Ibrahim Sangare", "Simon Adingra", "Sebastien Haller", "Christian Kouame"]
    },
    "Ecuador": {
        "GK": "Alexander Dominguez",
        "outfield": ["Piero Hincapie", "Willian Pacho", "Felix Torres", "Angelo Preciado", "Moises Caicedo", "Carlos Gruezo", "Alan Franco", "Jeremy Sarmiento", "Enner Valencia", "Kendry Paez"]
    },
    "Netherlands": {
        "GK": "Bart Verbruggen",
        "outfield": ["Nathan Ake", "Virgil van Dijk", "Stefan de Vrij", "Denzel Dumfries", "Jerdy Schouten", "Tijjani Reijnders", "Joey Veerman", "Cody Gakpo", "Memphis Depay", "Xavi Simons"]
    },
    "Japan": {
        "GK": "Zion Suzuki",
        "outfield": ["Hiroki Ito", "Koki Machida", "Ko Itakura", "Yukinari Sugawara", "Wataru Endo", "Hidemasa Morita", "Keito Nakamura", "Takumi Minamino", "Takefusa Kubo", "Ayase Ueda"]
    },
    "Sweden": {
        "GK": "Robin Olsen",
        "outfield": ["Ludwig Augustinsson", "Victor Lindelof", "Isak Hien", "Emil Holm", "Jens Cajuste", "Anton Saletros", "Dejan Kulusevski", "Alexander Isak", "Viktor Gyokeres", "Anthony Elanga"]
    },
    "Tunisia": {
        "GK": "Bechir Ben Said",
        "outfield": ["Ali Abdi", "Yassine Meriah", "Montassar Talbi", "Wajdi Kechrida", "Ellyes Skhiri", "Aissa Laidouni", "Hamza Rafia", "Sayfallah Ltaief", "Elias Achouri", "Haythem Jouini"]
    },
    "Belgium": {
        "GK": "Koen Casteels",
        "outfield": ["Arthur Theate", "Wout Faes", "Zeno Debast", "Timothy Castagne", "Amadou Onana", "Orel Mangala", "Kevin De Bruyne", "Jeremy Doku", "Leandro Trossard", "Romelu Lukaku"]
    },
    "Egypt": {
        "GK": "Mohamed El Shenawy",
        "outfield": ["Ahmed Hegazi", "Mohamed Abdelmonem", "Mohamed Hany", "Mohamed Hamdy", "Hamdi Fathi", "Mohamed Elneny", "Imam Ashour", "M. Trezeguet", "Mostafa Mohamed", "Mohamed Salah"]
    },
    "New Zealand": {
        "GK": "Stefan Marinovic",
        "outfield": ["Tommy Smith", "Michael Boxall", "Libby Cacace", "Tim Payne", "Joe Bell", "Marko Stamenic", "Sarpreet Singh", "Elijah Just", "Chris Wood", "K. Barbarouses"]
    },
    "Spain": {
        "GK": "Unai Simon",
        "outfield": ["Marc Cucurella", "Aymeric Laporte", "Robin Le Normand", "Dani Carvajal", "Rodri", "Fabian Ruiz", "Pedri", "Nico Williams", "Lamine Yamal", "Alvaro Morata"]
    },
    "Cape Verde": {
        "GK": "Vozinha",
        "outfield": ["Joao Paulo", "Logan Costa", "Picote", "Steven Moreira", "Kevin Pina", "Jamiro Monteiro", "Deroy Duarte", "Ryan Mendes", "Jovane Cabral", "Bebé"]
    },
    "Saudi Arabia": {
        "GK": "Mohammed Al-Owais",
        "outfield": ["Ali Al-Bulaihi", "Ali Lajami", "Hassan Tambakti", "Saud Abdulhamid", "Abdulelah Al-Malki", "Mohamed Kanno", "Faisal Al-Ghamdi", "Salem Al-Dawsari", "Firas Al-Buraikan", "Saleh Al-Shehri"]
    },
    "Uruguay": {
        "GK": "Sergio Rochet",
        "outfield": ["Matias Vina", "Ronald Araujo", "Jose Maria Gimenez", "Nahitan Nandez", "Manuel Ugarte", "Federico Valverde", "Nicolas de la Cruz", "Facundo Pellistri", "Darwin Nunez", "Maximiliano Araujo"]
    },
    "Senegal": {
        "GK": "Edouard Mendy",
        "outfield": ["Kalidou Koulibaly", "Abdou Diallo", "Ismail Jakobs", "Youssouf Sabaly", "Idrissa Gueye", "Pape Matar Sarr", "Lamine Camara", "Ismaila Sarr", "Nicolas Jackson", "Sadio Mane"]
    },
    "Iraq": {
        "GK": "Jalal Hassan",
        "outfield": ["Rebin Sulaka", "Saad Natiq", "Hussein Ali", "Merchas Doski", "Amir Al-Ammari", "Osama Rashid", "Ibrahim Bayesh", "Ali Jasim", "Youssef Amyn", "Aymen Hussein"]
    },
    "Norway": {
        "GK": "Orjan Nyland",
        "outfield": ["Leo Ostigard", "Kristoffer Ajer", "Birger Meling", "Marcus Pedersen", "Martin Odegaard", "Sander Berge", "Patrick Berg", "M. Elyounoussi", "Erling Haaland", "Alexander Sorloth"]
    },
    "Algeria": {
        "GK": "Anthony Mandrea",
        "outfield": ["Aissa Mandi", "Ramy Bensebaini", "Rayan Ait-Nouri", "Youcef Atal", "Nabil Bentaleb", "Ismael Bennacer", "Houssem Aouar", "Riyad Mahrez", "Baghdad Bounedjah", "Amine Gouiri"]
    },
    "Jordan": {
        "GK": "Yazeed Abulaila",
        "outfield": ["Yazan Al-Arab", "Abdallah Nasib", "Salem Al-Ajalin", "Ehsan Haddad", "Nizar Al-Rashdan", "Noor Al-Rawabdeh", "Mahmoud Al-Mardi", "Ali Olwan", "Musa Al-Taamari", "Yazan Al-Naimat"]
    },
    "DR Congo": {
        "GK": "Lionel Mpasi",
        "outfield": ["Chancel Mbemba", "Henoc Inonga", "Arthur Masuaku", "Gedeon Kalulu", "S. Moutoussamy", "Charles Pickel", "Theo Bongonda", "Gael Kakuta", "Yoane Wissa", "Cedric Bakambu"]
    },
    "Uzbekistan": {
        "GK": "Utkir Yusupov",
        "outfield": ["Abdukodir Khusanov", "Rustam Ashurmatov", "Sherzod Nasrullaev", "Farrukh Sayfiev", "Odiljon Hamrobekov", "Otabek Shukurov", "Jaloliddin Masharipov", "Abbosbek Fayzullaev", "Oston Urunov", "Eldor Shomurodov"]
    },
    "Colombia": {
        "GK": "Camilo Vargas",
        "outfield": ["Davinson Sanchez", "Jhon Lucumi", "Johan Mojica", "Daniel Munoz", "Jefferson Lerma", "Richard Rios", "James Rodriguez", "Jhon Arias", "Luis Diaz", "Jhon Duran"]
    },
    "Croatia": {
        "GK": "Dominik Livakovic",
        "outfield": ["Josko Gvardiol", "Josip Sutalo", "Borna Sosa", "Josip Stanisic", "Luka Modric", "Mateo Kovacic", "Marcelo Brozovic", "Ivan Perisic", "Andrej Kramaric", "Mario Pasalic"]
    },
    "Panama": {
        "GK": "Orlando Mosquera",
        "outfield": ["Jose Cordoba", "Andres Andrade", "Eric Davis", "M. Murillo", "A. Carrasquilla", "Cristian Martinez", "Edgar Barcenas", "Puma Rodriguez", "Jose Fajardo", "Ismael Diaz"]
    },
    "Ghana": {
        "GK": "Lawrence Ati-Zigi",
        "outfield": ["Mohammed Salisu", "Alexander Djiku", "Gideon Mensah", "Alidu Seidu", "Salis Abdul Samed", "Elisha Owusu", "Mohammed Kudus", "Jordan Ayew", "Ernest Nuamah", "Inaki Williams"]
    },
    "Austria": {
        "GK": "Alexander Schlager",
        "outfield": ["David Alaba", "Kevin Danso", "Maximilian Wober", "Stefan Posch", "Nicolas Seiwald", "Konrad Laimer", "Marcel Sabitzer", "Christoph Baumgartner", "Konrad Laimer", "Michael Gregoritsch"]
    }
}

# ── 3. Position Coordinate Center Maps ──
POSITION_CENTERS = {
    "4-3-3": {
        "GK": (4, 40),
        "LB": (35, 12), "CB_L": (25, 28), "CB_R": (25, 52), "RB": (35, 68),
        "DM": (48, 40), "CM_L": (58, 25), "CM_R": (58, 55),
        "LW": (76, 15), "ST": (88, 40), "RW": (76, 65)
    },
    "4-2-3-1": {
        "GK": (4, 40),
        "LB": (35, 12), "CB_L": (25, 28), "CB_R": (25, 52), "RB": (35, 68),
        "DM_L": (50, 28), "DM_R": (50, 52),
        "AM_L": (72, 16), "AM_C": (68, 40), "AM_R": (72, 64),
        "ST": (88, 40)
    },
    "3-5-2": {
        "GK": (4, 40),
        "CB_L": (25, 24), "CB_C": (23, 40), "CB_R": (25, 56),
        "LWB": (45, 10), "RWB": (45, 70),
        "DM": (46, 40), "CM_L": (56, 26), "CM_R": (56, 54),
        "ST_L": (82, 30), "ST_R": (82, 50)
    },
    "4-4-2": {
        "GK": (4, 40),
        "LB": (35, 12), "CB_L": (25, 28), "CB_R": (25, 52), "RB": (35, 68),
        "LM": (58, 14), "CM_L": (55, 30), "CM_R": (55, 50), "RM": (58, 66),
        "ST_L": (84, 30), "ST_R": (84, 50)
    }
}

FORMATION_PLAYERS_MAPS = {
    "4-3-3": ["LB", "CB_L", "CB_R", "RB", "DM", "CM_L", "CM_R", "LW", "ST", "RW"],
    "4-2-3-1": ["LB", "CB_L", "CB_R", "RB", "DM_L", "DM_R", "AM_L", "AM_C", "AM_R", "ST"],
    "3-5-2": ["CB_L", "CB_C", "CB_R", "LWB", "RWB", "DM", "CM_L", "CM_R", "ST_L", "ST_R"],
    "4-4-2": ["LB", "CB_L", "CB_R", "RB", "LM", "CM_L", "CM_R", "RM", "ST_L", "ST_R"]
}


# ── 4. Event Generator ──
def generate_match_events(match):
    match_id = match["match_id"]
    h_team = match["home_team"]["home_team_name"]
    a_team = match["away_team"]["away_team_name"]
    
    h_form = "4-3-3" if h_team in ("United States", "France", "England", "Portugal", "Brazil", "Germany", "Spain", "Belgium", "Netherlands") else "4-2-3-1"
    if h_team == "Argentina":
        h_form = "4-4-2"
    
    a_form = "4-3-3" if a_team in ("Morocco", "Canada", "Croatia", "Senegal", "Uruguay", "Colombia", "Sweden") else "4-2-3-1"
    if a_team in ("Switzerland", "Bosnia and Herzegovina", "Czechia", "South Korea"):
        a_form = "4-2-3-1"
    
    events = []
    h_squad = SQUADS[h_team]
    a_squad = SQUADS[a_team]
    
    # Lineups Starting XI
    for team, squad, form, id_offset in [(h_team, h_squad, h_form, 0), (a_team, a_squad, a_form, 100)]:
        lineup = []
        lineup.append({
            "player": {"id": 1000 + id_offset, "name": squad["GK"]},
            "position": {"name": "Goalkeeper"}
        })
        roles = FORMATION_PLAYERS_MAPS[form]
        for i, player in enumerate(squad["outfield"]):
            lineup.append({
                "player": {"id": 1001 + i + id_offset, "name": player},
                "position": {"name": roles[i]}
            })
            
        events.append({
            "id": str(uuid.uuid4()), "index": len(events) + 1, "period": 1,
            "timestamp": "00:00:00.000", "minute": 0, "second": 0,
            "type": {"id": 35, "name": "Starting XI"},
            "team": {"name": team},
            "tactics": {
                "formation": int(form.replace("-", "")),
                "lineup": lineup
            }
        })

    # Custom Substitutions
    sub_players = {
        "United States": ("Timothy Weah", "Gio Reyna"),
        "Mexico": ("Uriel Antuna", "Erick Sanchez"),
        "Canada": ("Tajon Buchanan", "Jonathan Osorio"),
        "England": ("Bukayo Saka", "Phil Foden"),
        "Iran": ("Alireza Jahanbakhsh", "Saman Ghoddos"),
        "Argentina": ("Angel Di Maria", "Julian Alvarez"),
        "Portugal": ("Joao Felix", "Rafael Leao"),
        "France": ("Ousmane Dembele", "Marcus Thuram"),
        "Morocco": ("Sofiane Boufal", "Zakaria Aboukhlal"),
        "South Africa": ("T. Morena", "O. Appollis"),
        "Czechia": ("J. Kuchta", "M. Chytil"),
        "South Korea": ("Cho Gue-sung", "Lee Kang-in"),
        "Bosnia and Herzegovina": ("H. Tabakovic", "M. Stevanovic"),
        "Qatar": ("Yusuf Abdurisag", "Akram Afif"),
        "Switzerland": ("Breel Embolo", "X. Shaqiri"),
        "Brazil": ("Raphinha", "Gabriel Martinelli"),
        "Haiti": ("Duckens Nazon", "Mondy Prunier"),
        "Scotland": ("Che Adams", "Lawrence Shankland"),
        "Paraguay": ("Ramon Sosa", "Alejandro Romero"),
        "Australia": ("Kusini Yengi", "Mitchell Duke"),
        "Turkey": ("B. Yilmaz", "Kerem Akturkoglu"),
        "Germany": ("Kai Havertz", "Niclas Fullkrug"),
        "Curaçao": ("Gervane Kastaneer", "Brandley Kuwas"),
        "Ivory Coast": ("Christian Kouame", "Nicolas Pepe"),
        "Ecuador": ("Kendry Paez", "Jordy Caicedo"),
        "Netherlands": ("Memphis Depay", "Wout Weghorst"),
        "Japan": ("Ayase Ueda", "Ritsu Doan"),
        "Sweden": ("Anthony Elanga", "Emil Forsberg"),
        "Tunisia": ("Haythem Jouini", "Seifeddine Jaziri"),
        "Belgium": ("Leandro Trossard", "Dodi Lukebakio"),
        "Egypt": ("Mostafa Mohamed", "Trezeguet"),
        "New Zealand": ("K. Barbarouses", "Ben Waine"),
        "Spain": ("Alvaro Morata", "Ferran Torres"),
        "Cape Verde": ("Jovane Cabral", "Garry Rodrigues"),
        "Saudi Arabia": ("Saleh Al-Shehri", "Abdullah Radif"),
        "Uruguay": ("Darwin Nunez", "Luis Suarez"),
        "Senegal": ("Nicolas Jackson", "Boulaye Dia"),
        "Iraq": ("Aymen Hussein", "Mohanad Ali"),
        "Norway": ("Alexander Sorloth", "Antonio Nusa"),
        "Algeria": ("Amine Gouiri", "Said Benrahma"),
        "Jordan": ("Yazan Al-Naimat", "Anas Al-Jarat"),
        "DR Congo": ("Cedric Bakambu", "Fiston Mayele"),
        "Uzbekistan": ("Eldor Shomurodov", "Igor Sergeev"),
        "Colombia": ("Jhon Duran", "Rafael Santos Borre"),
        "Croatia": ("Mario Pasalic", "Bruno Petkovic"),
        "Panama": ("Ismael Diaz", "Eduardo Guerrero"),
        "Ghana": ("Inaki Williams", "Antoine Semenyo"),
        "Austria": ("Michael Gregoritsch", "Marko Arnautovic"),
    }

    # Generate substitution events
    h_sub_off, h_sub_on = sub_players[h_team]
    events.append({
        "id": str(uuid.uuid4()), "index": len(events) + 1, "period": 2,
        "timestamp": "00:15:00.000", "minute": 60, "second": 0,
        "type": {"id": 19, "name": "Substitution"}, "team": {"name": h_team},
        "player": {"name": h_sub_off}, "substitution": {"replacement": {"name": h_sub_on}}
    })

    a_sub_off, a_sub_on = sub_players[a_team]
    events.append({
        "id": str(uuid.uuid4()), "index": len(events) + 1, "period": 2,
        "timestamp": "00:20:00.000", "minute": 65, "second": 0,
        "type": {"id": 19, "name": "Substitution"}, "team": {"name": a_team},
        "player": {"name": a_sub_off}, "substitution": {"replacement": {"name": a_sub_on}}
    })

    # Tactical Shift for Morocco if present
    if h_team == "Morocco" or a_team == "Morocco":
        mor_id_offset = 0 if h_team == "Morocco" else 100
        mor_roles = FORMATION_PLAYERS_MAPS["3-5-2"]
        mor_lineup = []
        mor_lineup.append({
            "player": {"id": 1000 + mor_id_offset, "name": SQUADS["Morocco"]["GK"]},
            "position": {"name": "Goalkeeper"}
        })
        
        mor_outfield = list(SQUADS["Morocco"]["outfield"])
        if "Sofiane Boufal" in mor_outfield:
            idx = mor_outfield.index("Sofiane Boufal")
            mor_outfield[idx] = "Zakaria Aboukhlal"
            
        for i, player in enumerate(mor_outfield):
            mor_lineup.append({
                "player": {"id": 1001 + i + mor_id_offset, "name": player},
                "position": {"name": mor_roles[i]}
            })

        events.append({
            "id": str(uuid.uuid4()), "index": len(events) + 1, "period": 2,
            "timestamp": "00:30:00.000", "minute": 75, "second": 0,
            "type": {"id": 36, "name": "Tactical Shift"}, "team": {"name": "Morocco"},
            "tactics": {"formation": 352, "lineup": mor_lineup}
        })

    # Generate spatial event locations
    for team, squad, form, is_home in [(h_team, h_squad, h_form, True), (a_team, a_squad, a_form, False)]:
        sub_off, sub_on = sub_players[team]
        for player in squad["outfield"] + [sub_on]:
            if player == sub_off:
                start_min, end_min = 0, 60 if is_home else 65
            elif player == sub_on:
                start_min, end_min = 60 if is_home else 65, 95
            else:
                start_min, end_min = 0, 95
                
            num_events = int((end_min - start_min) * 1.5)
            for _ in range(num_events):
                m = random.uniform(start_min, end_min)
                curr_form = form
                if team == "Morocco" and m > 75:
                    curr_form = "3-5-2"
                    
                roles = FORMATION_PLAYERS_MAPS[curr_form]
                curr_active_outfield = list(squad["outfield"])
                if m > (60 if is_home else 65):
                    if sub_off in curr_active_outfield:
                        idx = curr_active_outfield.index(sub_off)
                        curr_active_outfield[idx] = sub_on
                
                if player in curr_active_outfield:
                    role_idx = curr_active_outfield.index(player)
                    role = roles[role_idx]
                else:
                    role = "ST"
                    
                center = POSITION_CENTERS[curr_form].get(role, (50, 40))
                x = max(0.5, min(119.5, random.gauss(center[0], 8.0)))
                y = max(0.5, min(79.5, random.gauss(center[1], 12.0)))
                
                events.append({
                    "id": str(uuid.uuid4()), "index": len(events) + 1,
                    "period": 1 if m <= 45 else 2,
                    "minute": int(m), "second": int((m - int(m)) * 60),
                    "type": {"name": "Pass"}, "team": {"name": team},
                    "player": {"name": player}, "location": [round(x, 1), round(y, 1)]
                })
                
    events.sort(key=lambda x: (x.get("minute", 0), x.get("second", 0)))
    with open(DATA_DIR / "events" / f"{match_id}.json", "w", encoding="utf-8") as f:
        json.dump(events, f, indent=2)


# Generate events for all 32 matches
print("Generating events for 2026 matches...")
for match in matches_2026:
    generate_match_events(match)
    print(f"  Generated events for match {match['match_id']}: {match['home_team']['home_team_name']} vs {match['away_team']['away_team_name']}")

print("\nMock 2026 World Cup data successfully generated!")
