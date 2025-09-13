import argparse
import os
from glob import glob
from utils.fetch_api_base import fetch_with_cache
import json


# --------------------------
# Live and Upcoming Matches
# --------------------------
def fetch_live_matches():
    return fetch_with_cache("matches/v1/live", "matches_live.json")

def fetch_upcoming_matches():
    return fetch_with_cache("matches/v1/upcoming", "matches_upcoming.json")

def fetch_recent_matches():
    return fetch_with_cache("matches/v1/recent", "matches_recent.json")

# ----------------------
# Matches
# ----------------------
def fetch_all_matches():
    live = fetch_with_cache("matches/v1/live", "matches_live.json")
    upcoming = fetch_with_cache("matches/v1/upcoming", "matches_upcoming.json")
    recent = fetch_with_cache("matches/v1/recent", "matches_recent.json")

    all_matches = []
    venue_ids = set()

    for block in (live.get("typeMatches", []) +
                upcoming.get("typeMatches", []) +
                recent.get("typeMatches", [])):
        for series in block.get("seriesMatches", []):
            if "seriesAdWrapper" in series:
                matches = series["seriesAdWrapper"].get("matches", [])
                for m in matches:
                    match_id = m.get("matchInfo", {}).get("matchId")
                    venue_id = m.get("matchInfo", {}).get("venueInfo", {}).get("id")
                    if match_id:
                        all_matches.append(match_id)
                    if venue_id:
                        venue_ids.add(venue_id)

    for mid in set(all_matches):
        fetch_with_cache(f"mcenter/v1/{mid}", f"match_{mid}_info.json")

    print(f"✅ Cached details for {len(set(all_matches))} matches")
    return all_matches, venue_ids


# ----------------------
# Series
# ----------------------
def fetch_all_series():
    series_list = fetch_with_cache("series/v1/international", "series_list.json")
    archives = fetch_with_cache("series/v1/archives/international", "series_archives.json")

    series_ids = []
    venue_ids = set()

    for block in series_list.get("seriesMapProto", []):
        for s in block.get("series", []):
            sid = s.get("id")
            if sid:
                series_ids.append(sid)

    for sid in series_ids:
        data = fetch_with_cache(f"series/v1/{sid}", f"series_{sid}_matches.json")
        for m in data.get("matchDetails", []):
            md_map = m.get("matchDetailsMap", {})
            if isinstance(md_map, dict):
                for match in md_map.get("match", []):
                    venue_id = match.get("matchInfo", {}).get("venueInfo", {}).get("id")
                    if venue_id:
                        venue_ids.add(venue_id)

    print(f"✅ Cached {len(series_ids)} series matches")
    return series_ids, venue_ids


# ----------------------
# Teams
# ----------------------
def fetch_all_teams():
    teams = fetch_with_cache("teams/v1/international", "teams_list.json")
    for team in teams.get("list", []):
        tid = team.get("id")
        if tid:
            fetch_with_cache(f"teams/v1/{tid}/schedule", f"team_{tid}_schedule.json")
            fetch_with_cache(f"teams/v1/{tid}/results", f"team_{tid}_results.json")
            fetch_with_cache(f"teams/v1/{tid}/players", f"team_{tid}_players.json")
    print(f"✅ Cached data for {len(teams.get('list', []))} teams")


def fetch_all_team_players():
    """
    Fetch players only for teams in allowed_countries.
    """
    team_ids = list(range(1, 27))  # Example: checking team IDs 1 to 27
    all_players = set()

    for tid in team_ids:
        country = get_team_country(tid)
        if country not in allowed_countries:
            continue  # skip disallowed teams

        data = fetch_with_cache(f"teams/v1/{tid}/players", f"team_{tid}_players.json")
        if not data:
            continue

        for p in data.get("player", []):
            pid = p.get("id")
            if not pid:
                continue

            all_players.add(pid)

            # Cache player details
            fetch_with_cache(f"stats/v1/player/{pid}", f"player_{pid}_info.json")
            fetch_with_cache(f"stats/v1/player/{pid}/career", f"player_{pid}_career.json")
            fetch_with_cache(f"stats/v1/player/{pid}/batting", f"player_{pid}_batting.json")
            fetch_with_cache(f"stats/v1/player/{pid}/bowling", f"player_{pid}_bowling.json")

    print(f"✅ Cached {len(all_players)} unique players across allowed teams")
    return all_players


# ----------------------
# Venues
# ----------------------
def fetch_all_venues(extra_ids=None):
    if extra_ids is None:
        extra_ids = set()

    successful_venues = 0

    for vid in extra_ids:
        info = fetch_with_cache(f"venues/v1/{vid}", f"venue_{vid}_info.json")
        if info is None:
            print(f"⚠️ Venue {vid} info could not be fetched.")
            continue

        matches = fetch_with_cache(f"venues/v1/{vid}/matches", f"venue_{vid}_matches.json")
        if matches is None:
            print(f"⚠️ Venue {vid} has no matches or failed to fetch.")
        else:
            successful_venues += 1

    print(f"✅ Cached info for {successful_venues}/{len(extra_ids)} venues successfully.")


# ----------------------
# Players
# ----------------------
def fetch_all_players():
    player_files = glob(os.path.join("cache", "player_*_info.json"))
    print(f"➡️ Found {len(player_files)} cached player info files")

    players = []
    for fpath in player_files:
        try:
            with open(fpath, "r", encoding="utf-8") as f:
                data = json.load(f)
            pid = int(os.path.basename(fpath).split("_")[1])
            name = data.get("name")
            country = data.get("country")
            role = data.get("role")
            bat_style = data.get("battingStyle")
            bowl_style = data.get("bowlingStyle")

            players.append({
                "id": pid,
                "name": name,
                "country": country,
                "role": role,
                "bat_style": bat_style,
                "bowl_style": bowl_style
            })
        except Exception as e:
            print(f"⚠️ Could not parse {fpath}: {e}")
            continue

    print(f"✅ Loaded {len(players)} players from cache")
    return players




# ----------------------
# Players (Full Stats from rosters)
# ----------------------
def fetch_all_player_stats():
    """Fetch batting & bowling stats for all players found in cached match rosters."""
    match_files = glob(os.path.join("cache", "match_*_info.json"))
    player_ids = set()

    for fpath in match_files:
        try:
            with open(fpath, "r", encoding="utf-8") as f:
                data = json.load(f)
            for tkey in ["team1", "team2"]:
                team = data.get("matchInfo", {}).get(tkey, {})
                for p in team.get("playerDetails", []):
                    pid = p.get("id")
                    if pid:
                        player_ids.add(pid)
        except Exception:
            continue

    print(f"➡️ Found {len(player_ids)} unique players across all matches")

    fetched = 0
    skipped = 0
    for pid in player_ids:
        fname = f"player_{pid}_batting.json"
        fpath = os.path.join("cache", fname)
        if os.path.exists(fpath):
            skipped += 1
            continue

        fetch_with_cache(f"stats/v1/player/{pid}", f"player_{pid}_info.json")
        fetch_with_cache(f"stats/v1/player/{pid}/career", f"player_{pid}_career.json")
        fetch_with_cache(f"stats/v1/player/{pid}/batting", f"player_{pid}_batting.json")
        fetch_with_cache(f"stats/v1/player/{pid}/bowling", f"player_{pid}_bowling.json")
        fetched += 1

    print(f"✅ Player stats fetched: {fetched}, skipped (already cached): {skipped}")


# ----------------------
# Stats
# ----------------------
def fetch_all_stats():
    fetch_with_cache("stats/v1/rankings/batsmen?formatType=test", "stats_rankings_batsmen_test.json")
    fetch_with_cache("stats/v1/iccstanding/team/matchtype/1", "stats_icc_standings.json")
    fetch_with_cache("stats/v1/topstats", "stats_topstats_filters.json")
    fetch_with_cache("stats/v1/topstats/0?statsType=mostRuns", "stats_topstats_most_runs.json")
    print("✅ Cached ICC stats and records")


# ----------------------
# Scorecards
# ----------------------
def fetch_scorecard(match_id):
    """Fetch full scorecard for a match and cache it."""
    return fetch_with_cache(f"mcenter/v1/{match_id}/scard", f"match_{match_id}_scorecard.json")

def fetch_all_scorecards():
    """Fetch scorecards for all cached matches."""
    match_files = glob(os.path.join("cache", "match_*_info.json"))
    fetched = 0
    skipped = 0

    total = len(match_files)
    for idx, fpath in enumerate(match_files, 1):
        mid = os.path.basename(fpath).split("_")[1]
        scorecard_file = os.path.join("cache", f"match_{mid}_scorecard.json")

        if os.path.exists(scorecard_file):
            skipped += 1
            continue

        print(f"➡️ [{idx}/{total}] Fetching scorecard for match {mid}...")
        fetch_scorecard(mid)
        fetched += 1

    print(f"✅ Scorecards fetched: {fetched}, skipped (already cached): {skipped}")


# ----------------------
# CLI
# ----------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Cricbuzz API Data Fetcher")

    parser.add_argument("--all", action="store_true", help="Fetch everything (all endpoints)")
    parser.add_argument("--matches", action="store_true", help="Fetch all matches")
    parser.add_argument("--series", action="store_true", help="Fetch all series")
    parser.add_argument("--teams", action="store_true", help="Fetch all teams")
    parser.add_argument("--team-players", action="store_true", help="Fetch players for team IDs 1–6")
    parser.add_argument("--venues", action="store_true", help="Fetch venues dynamically")
    parser.add_argument("--players", action="store_true", help="Fetch players (trending only)")
    parser.add_argument("--player-stats", action="store_true", help="Fetch full player stats for all cached players")
    parser.add_argument("--stats", action="store_true", help="Fetch stats")
    parser.add_argument("--scorecard", type=int, help="Fetch scorecard for a specific match_id")
    parser.add_argument("--scorecards-all", action="store_true", help="Fetch scorecards for all cached matches")
    fetch_live_matches()
    fetch_upcoming_matches()
    fetch_recent_matches()

    args = parser.parse_args()

    if args.all:
        matches, venue_ids_1 = fetch_all_matches()
        series, venue_ids_2 = fetch_all_series()
        fetch_all_teams()
        fetch_all_venues(venue_ids_1 | venue_ids_2)
        fetch_all_players()
        fetch_all_player_stats()
        fetch_all_stats()
        fetch_all_scorecards()

    if args.matches:
        fetch_all_matches()

    if args.series:
        fetch_all_series()

    if args.teams:
        fetch_all_teams()
    
    if args.team_players:
        fetch_all_team_players()

    if args.venues:
        _, venue_ids_1 = fetch_all_matches()
        _, venue_ids_2 = fetch_all_series()
        fetch_all_venues(venue_ids_1 | venue_ids_2)

    if args.players:
        fetch_all_players()

    if args.player_stats:
        fetch_all_player_stats()

    if args.stats:
        fetch_all_stats()

    if args.scorecard:
        fetch_scorecard(args.scorecard)
        print(f"✅ Cached scorecard for match {args.scorecard}")

    if args.scorecards_all:
        fetch_all_scorecards()

    if not any(vars(args).values()):
        print("⚠️ No arguments provided. Use --help for options.")
