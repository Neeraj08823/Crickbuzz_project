import os
import json
import re
import mysql.connector
from dotenv import load_dotenv
from glob import glob
from datetime import datetime

# ----------------------
# Helpers
# ----------------------
# Load environment variables
load_dotenv()

DB_HOST = os.getenv("DB_HOST", "")
DB_USER = os.getenv("DB_USER", "")
DB_PORT = os.getenv("DB_PORT", "")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "cricbuzz_db")

CACHE_DIR = "cache"

# Database connection
def get_connection():
    return mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        port=DB_PORT,
        password=DB_PASSWORD,
        database=DB_NAME
    )

# Safe integer conversion
def safe_int(val):
    try:
        return int(val)
    except Exception:
        return None
# Safe float conversion    
def safe_float(val):
    """Safely convert a value to float or return None if not possible."""
    try:
        return float(val) if val is not None and val != "" else None
    except (ValueError, TypeError):
        return None

# Epoch millis → Python datetime
def epoch_to_datetime(epoch_ms):
    """Convert epoch millis to Python datetime (for MySQL DATETIME)."""
    if not epoch_ms:
        return None
    try:
        return datetime.fromtimestamp(int(epoch_ms) / 1000)
    except Exception:
        return None



# ----------------------
# Loaders
# ----------------------

def load_teams():
    path = os.path.join(CACHE_DIR, "teams_list.json")
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
    for team in data.get("list", []):
        if "teamId" not in team:
            continue

        country = team.get("countryName")
        if not country:
            # fallback: use teamName if no country provided
            country = team.get("teamName")

        cursor.execute("""
            INSERT INTO teams (team_id, name, short_name, country, image_url)
            VALUES (%s,%s,%s,%s,%s)
            ON DUPLICATE KEY UPDATE name=VALUES(name), short_name=VALUES(short_name),
            country=VALUES(country), image_url=VALUES(image_url)
        """, (
            safe_int(team.get("teamId")),
            team.get("teamName"),
            team.get("teamSName"),
            country,
            f"http://i.cricketcb.com/i/stats/images/{team.get('imageId')}.jpg" if team.get("imageId") else None
        ))

    conn.commit()
    cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
    cursor.close()
    conn.close()
    print("✅ Teams loaded")

def load_players():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SET FOREIGN_KEY_CHECKS = 0")

    for fname in os.listdir(CACHE_DIR):
        if not fname.startswith("player_") or not fname.endswith("_info.json"):
            continue
        path = os.path.join(CACHE_DIR, fname)
        with open(path, "r", encoding="utf-8") as f:
            p = json.load(f)

        cursor.execute("""
            INSERT INTO players (player_id, name, nickname, role, bat_style, bowl_style, dob, birthplace, country, image_url)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            ON DUPLICATE KEY UPDATE 
                    name=VALUES(name), 
                    nickname=VALUES(nickname),
                    role=VALUES(role),
                    bat_style=VALUES(bat_style), 
                    bowl_style=VALUES(bowl_style), 
                    dob=VALUES(dob),
                    birthplace=VALUES(birthplace), 
                    country=VALUES(country), 
                    image_url=VALUES(image_url)
        """, (
            safe_int(p.get("id")),
            p.get("name"),
            p.get("nickName"),
            p.get("role"),
            p.get("bat"),
            p.get("bowl"),
            p.get("DoBFormat"),
            p.get("birthPlace"),
            p.get("intlTeam"),
            p.get("image")
        ))

        for t in p.get("teamNameIds", []):
            cursor.execute("""
                INSERT IGNORE INTO player_team (player_id, team_id)
                VALUES (%s,%s)
            """, (
                safe_int(p.get("id")),
                safe_int(t.get("teamId"))
            ))

    conn.commit()
    cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
    cursor.close()
    conn.close()
    print("✅ Players loaded")

def load_venues():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
    for fname in os.listdir(CACHE_DIR):
        if not fname.startswith("venue_") or not fname.endswith("_info.json"):
            continue
        path = os.path.join(CACHE_DIR, fname)
        with open(path, "r", encoding="utf-8") as f:
            v = json.load(f)

        vid = int(fname.split("_")[1])
        cursor.execute("""
            INSERT INTO venues (venue_id, name, city, country, timezone, established, capacity, known_as, ends, home_team, floodlights, image_url)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            ON DUPLICATE KEY UPDATE name=VALUES(name), city=VALUES(city), country=VALUES(country),
            timezone=VALUES(timezone), established=VALUES(established), capacity=VALUES(capacity),
            known_as=VALUES(known_as), ends=VALUES(ends), home_team=VALUES(home_team),
            floodlights=VALUES(floodlights), image_url=VALUES(image_url)
        """, (
            vid,
            v.get("ground"),
            v.get("city"),
            v.get("country"),
            v.get("timezone"),
            str(v.get("established")),
            v.get("capacity"),
            v.get("knownAs"),
            v.get("ends"),
            v.get("homeTeam"),
            v.get("floodlights"),
            v.get("imageUrl")
        ))

    conn.commit()
    cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
    cursor.close()
    conn.close()
    print("✅ Venues loaded")

def load_series_and_matches():
    from glob import glob

    files = glob(os.path.join(CACHE_DIR, "series_*_matches.json"))
    if not files:
        print("⚠️ No series_*_matches.json files found in cache.")
        return

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SET FOREIGN_KEY_CHECKS = 0")
    series_count = 0
    match_count = 0
    mt_teams = 0
    mt_scores = 0

    for path in files:
        try:
            with open(path, "r", encoding="utf-8") as fh:
                data = json.load(fh)
        except Exception:
            continue

        for detail in data.get("matchDetails", []):
            m_map = detail.get("matchDetailsMap") or {}
            matches_list = m_map.get("match") if isinstance(m_map, dict) else None
            if not matches_list:
                continue

            for m in matches_list:
                info = m.get("matchInfo") or {}
                if not info:
                    continue

                # --- SERIES UPSERT ---
                sid = safe_int(info.get("seriesId"))
                sname = info.get("seriesName")
                sstart = epoch_to_datetime(info.get("seriesStartDt"))
                send = epoch_to_datetime(info.get("seriesEndDt"))

                # Use seriesType, else fallback to matchFormat
                stype = info.get("seriesType") or info.get("matchFormat")

                if sid:
                    cur.execute("""
                        INSERT INTO series (series_id, name, type, start_date, end_date)
                        VALUES (%s,%s,%s,%s,%s)
                        ON DUPLICATE KEY UPDATE
                            name=VALUES(name),
                            type=VALUES(type),
                            start_date=VALUES(start_date),
                            end_date=VALUES(end_date)
                    """, (sid, sname, stype, sstart, send))
                    series_count += 1

                # --- MATCH INSERT ---
                mid = safe_int(info.get("matchId"))
                if not mid:
                    continue
                mdesc = info.get("matchDesc")
                mformat = info.get("matchFormat")
                mstart = epoch_to_datetime(info.get("startDate"))
                mend = epoch_to_datetime(info.get("endDate"))
                state = info.get("state")
                status = info.get("status")
                vid = None
                venue_info = info.get("venueInfo")
                if venue_info:
                    vid = safe_int(venue_info.get("id"))

                cur.execute("""
                    INSERT INTO matches (match_id, series_id, name, format, start_date, end_date, state, status, venue_id)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
                    ON DUPLICATE KEY UPDATE
                        series_id=VALUES(series_id),
                        name=VALUES(name),
                        format=VALUES(format),
                        start_date=VALUES(start_date),
                        end_date=VALUES(end_date),
                        state=VALUES(state),
                        status=VALUES(status),
                        venue_id=VALUES(venue_id)
                """, (mid, sid, mdesc, mformat, mstart, mend, state, status, vid))
                match_count += 1

                # --- match_teams ---
                for side in ("team1", "team2"):
                    t = info.get(side) or {}
                    tid = safe_int(t.get("teamId"))
                    if tid:
                        cur.execute("""
                            INSERT IGNORE INTO match_teams (match_id, team_id, team_role)
                            VALUES (%s,%s,%s)
                        """, (mid, tid, side))
                        mt_teams += 1

    conn.commit()
    cur.execute("SET FOREIGN_KEY_CHECKS = 1")
    cur.close()
    conn.close()

    print(f"✅ Series inserted")
    print(f"✅ Matches inserted")
    print(f"✅ Match Teams inserted")
    if mt_scores:
        print(f"✅ match_scores inserts: {mt_scores}")



def load_match_details():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SET FOREIGN_KEY_CHECKS = 0")

    results_count = toss_count = officials_count = awards_count = roster_count = 0

    for fname in os.listdir(CACHE_DIR):
        if not fname.startswith("match_") or not fname.endswith("_info.json"):
            continue

        path = os.path.join(CACHE_DIR, fname)
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        mi = data.get("matchInfo", {})
        match_id = mi.get("matchId")
        if not match_id:
            continue

        # --- Match Result ---
        result = mi.get("result")
        if result:
            cursor.execute("""
                INSERT INTO match_result (match_id, result_type, winning_team, winning_team_id,
                                        winning_margin, win_by_runs, win_by_innings)
                VALUES (%s,%s,%s,%s,%s,%s,%s)
                ON DUPLICATE KEY UPDATE result_type=VALUES(result_type),
                                        winning_team=VALUES(winning_team),
                                        winning_team_id=VALUES(winning_team_id),
                                        winning_margin=VALUES(winning_margin),
                                        win_by_runs=VALUES(win_by_runs),
                                        win_by_innings=VALUES(win_by_innings)
            """, (
                match_id,
                result.get("resultType"),
                result.get("winningTeam"),
                result.get("winningteamId"),
                result.get("winningMargin"),
                result.get("winByRuns"),
                result.get("winByInnings")
            ))
            results_count += cursor.rowcount

        # --- Toss ---
        toss = mi.get("tossResults")
        if toss:
            cursor.execute("""
                INSERT INTO match_toss (match_id, toss_winner_id, toss_winner_name, decision)
                VALUES (%s,%s,%s,%s)
                ON DUPLICATE KEY UPDATE toss_winner_id=VALUES(toss_winner_id),
                                        toss_winner_name=VALUES(toss_winner_name),
                                        decision=VALUES(decision)
            """, (
                match_id,
                toss.get("tossWinnerId"),
                toss.get("tossWinnerName"),
                toss.get("decision")
            ))
            toss_count += cursor.rowcount

        # --- Officials ---
        columns = {
            "umpire1": ("umpire1_id", "umpire1_name", "umpire1_country"),
            "umpire2": ("umpire2_id", "umpire2_name", "umpire2_country"),
            "umpire3": ("umpire3_id", "umpire3_name", "umpire3_country"),
            "referee": ("referee_id", "referee_name", "referee_country"),
        }
        for role in ["umpire1", "umpire2", "umpire3", "referee"]:
            official = mi.get(role)
            if official:
                id_col, name_col, country_col = columns[role]

                cursor.execute(f"""
                    INSERT INTO match_officials (match_id, {id_col}, {name_col}, {country_col})
                    VALUES (%s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                        {id_col} = VALUES({id_col}),
                        {name_col} = VALUES({name_col}),
                        {country_col} = VALUES({country_col})
                """, (
                    match_id,
                    official.get("id"),
                    official.get("name"),
                    official.get("country")
                ))
                officials_count += cursor.rowcount

        # --- Awards ---
        for p in mi.get("playersOfTheMatch", []):
            cursor.execute("""
                INSERT INTO match_awards (match_id, award_type, player_id, player_name, team_name)
                VALUES (%s,%s,%s,%s,%s)
                ON DUPLICATE KEY UPDATE player_name=VALUES(player_name),
                                        team_name=VALUES(team_name)
            """, (
                match_id, "PlayerOfMatch",
                p.get("id"), p.get("fullName") or p.get("name"), p.get("teamName")
            ))
            awards_count += cursor.rowcount

        for p in mi.get("playersOfTheSeries", []):
            cursor.execute("""
                INSERT INTO match_awards (match_id, award_type, player_id, player_name, team_name)
                VALUES (%s,%s,%s,%s,%s)
                ON DUPLICATE KEY UPDATE player_name=VALUES(player_name),
                                        team_name=VALUES(team_name)
            """, (
                match_id, "PlayerOfSeries",
                p.get("id"), p.get("fullName") or p.get("name"), p.get("teamName")
            ))
            awards_count += cursor.rowcount

        # --- Roster (players & staff) ---
        for team_key in ["team1", "team2"]:
            team = mi.get(team_key)
            if not team:
                continue
            team_id = team.get("id")
            for p in team.get("playerDetails", []):
                player_id = p.get("id")
                if not player_id:
                    continue

                cursor.execute("""
                    INSERT INTO players (player_id, name, country, role, bat_style, bowl_style)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                        name = VALUES(name),
                        country = VALUES(country),
                        role = VALUES(role),
                        bat_style = VALUES(bat_style),
                        bowl_style = VALUES(bowl_style)
                """, (
                    player_id,
                    p.get("name"),
                    p.get("teamName"),
                    p.get("role"),
                    p.get("battingStyle"),
                    p.get("bowlingStyle"),
                ))

                cursor.execute("""
                    INSERT INTO match_roster
                        (match_id, team_id, player_id, player_name, full_name, nick_name,
                        role, batting_style, bowling_style, face_image_id,
                        is_captain, is_keeper, is_substitute)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                    ON DUPLICATE KEY UPDATE
                        player_name=VALUES(player_name),
                        full_name=VALUES(full_name),
                        nick_name=VALUES(nick_name),
                        role=VALUES(role),
                        batting_style=VALUES(batting_style),
                        bowling_style=VALUES(bowling_style),
                        face_image_id=VALUES(face_image_id),
                        is_captain=VALUES(is_captain),
                        is_keeper=VALUES(is_keeper),
                        is_substitute=VALUES(is_substitute)
                """, (
                    match_id,
                    team_id,
                    player_id,
                    p.get("name"),
                    p.get("fullName"),
                    p.get("nickName"),
                    p.get("role"),
                    p.get("battingStyle"),
                    p.get("bowlingStyle"),
                    p.get("faceImageId"),
                    p.get("captain", False),
                    p.get("keeper", False),
                    p.get("substitute", False)
                ))
                roster_count += cursor.rowcount

    conn.commit()
    cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
    cursor.close()
    conn.close()

    print("✅ Match Details inserted")

def load_player_stats():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SET FOREIGN_KEY_CHECKS = 0")

    for fname in os.listdir(CACHE_DIR):
        if not fname.startswith("player_") or not fname.endswith("_batting.json"):
            continue

        # Extract player_id from filename
        try:
            player_id = int(fname.split("_")[1])
        except:
            continue

        path = os.path.join(CACHE_DIR, fname)
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        headers = data.get("headers", [])[1:]   # skip "ROWHEADER"
        rows = data.get("values", [])

        for i, fmt in enumerate(headers):       # each format (Test, ODI, T20, IPL, etc.)
            fmt = fmt.strip()
            stats = {r["values"][0]: r["values"][i+1] for r in rows}

            cursor.execute("""
                INSERT INTO player_stats
                (player_id, format, matches, innings, runs, balls, highest,
                average, strike_rate, not_outs, fours, sixes, ducks,
                fifties, hundreds, double_hundreds, triple_hundreds, quadruple_hundreds)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                ON DUPLICATE KEY UPDATE
                    matches=VALUES(matches), innings=VALUES(innings),
                    runs=VALUES(runs), balls=VALUES(balls), highest=VALUES(highest),
                    average=VALUES(average), strike_rate=VALUES(strike_rate),
                    not_outs=VALUES(not_outs), fours=VALUES(fours), sixes=VALUES(sixes),
                    ducks=VALUES(ducks), fifties=VALUES(fifties), hundreds=VALUES(hundreds),
                    double_hundreds=VALUES(double_hundreds),
                    triple_hundreds=VALUES(triple_hundreds),
                    quadruple_hundreds=VALUES(quadruple_hundreds)
            """, (
                player_id, fmt,
                safe_int(stats.get("Matches")),
                safe_int(stats.get("Innings")),
                safe_int(stats.get("Runs")),
                safe_int(stats.get("Balls")),
                stats.get("Highest"),
                safe_float(stats.get("Average")),
                safe_float(stats.get("SR")),
                safe_int(stats.get("Not Out")),
                safe_int(stats.get("Fours")),
                safe_int(stats.get("Sixes")),
                safe_int(stats.get("Ducks")),
                safe_int(stats.get("50s")),
                safe_int(stats.get("100s")),
                safe_int(stats.get("200s")),
                safe_int(stats.get("300s")),
                safe_int(stats.get("400s"))
            ))

    conn.commit()
    cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
    cursor.close()
    conn.close()
    print("✅ Player stats inserted")

def load_player_bowling_stats():
    from glob import glob

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SET FOREIGN_KEY_CHECKS = 0")

    files = glob(os.path.join(CACHE_DIR, "player_*_bowling.json"))

    inserted = 0
    for fpath in files:
        player_id = int(os.path.basename(fpath).split("_")[1])
        with open(fpath, "r", encoding="utf-8") as f:
            data = json.load(f)

        headers = data.get("headers", [])[1:]
        rows = data.get("values", [])

        stats = {fmt: {} for fmt in headers}

        for row in rows:
            values = row.get("values", [])
            if not values:
                continue
            metric = values[0]
            for i, fmt in enumerate(headers, start=1):
                stats[fmt][metric] = values[i]

        for fmt, vals in stats.items():
            cursor.execute("""
                INSERT INTO player_bowling_stats
                (player_id, format, matches, innings, balls, runs, maidens,
                wickets, average, economy, strike_rate,
                best_bowling_innings, best_bowling_match,
                four_wickets, five_wickets, ten_wickets)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                ON DUPLICATE KEY UPDATE
                    matches=VALUES(matches),
                    innings=VALUES(innings),
                    balls=VALUES(balls),
                    runs=VALUES(runs),
                    maidens=VALUES(maidens),
                    wickets=VALUES(wickets),
                    average=VALUES(average),
                    economy=VALUES(economy),
                    strike_rate=VALUES(strike_rate),
                    best_bowling_innings=VALUES(best_bowling_innings),
                    best_bowling_match=VALUES(best_bowling_match),
                    four_wickets=VALUES(four_wickets),
                    five_wickets=VALUES(five_wickets),
                    ten_wickets=VALUES(ten_wickets)
            """, (
                player_id, fmt,
                safe_int(vals.get("Matches")),
                safe_int(vals.get("Innings")),
                safe_int(vals.get("Balls")),
                safe_int(vals.get("Runs")),
                safe_int(vals.get("Maidens")),
                safe_int(vals.get("Wickets")),
                safe_float(vals.get("Avg")),
                safe_float(vals.get("Eco")),
                safe_float(vals.get("SR")),
                vals.get("BBI"),
                vals.get("BBM"),
                safe_int(vals.get("4w")),
                safe_int(vals.get("5w")),
                safe_int(vals.get("10w"))
            ))
            inserted += 1

    conn.commit()
    cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
    cursor.close()
    conn.close()

    print(f"✅ Bowling Stats inserted")


def load_scorecards():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SET FOREIGN_KEY_CHECKS = 0")

    files = glob(os.path.join(CACHE_DIR, "match_*_scorecard.json"))
    inserted = 0

    for fpath in files:
        with open(fpath, "r", encoding="utf-8") as f:
            sc = json.load(f)

        mid = safe_int(sc.get("matchId"))
        if not mid:
            mid = safe_int(re.search(r"match_(\d+)_", fpath).group(1))
        if not mid:
            continue

        for inng in sc.get("scorecard", []):
            iid = safe_int(inng.get("inningsid"))

            # 🏏 Batting
            for b in inng.get("batsman", []):
                pid = safe_int(b.get("id"))
                if not pid:
                    continue

                try:
                    cursor.execute("""
                        INSERT IGNORE INTO match_batting
                        (match_id, innings_id, batsman_id, player_name, runs, balls, fours, sixes,
                        strike_rate, dismissal)
                        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                        ON DUPLICATE KEY UPDATE player_name=VALUES(player_name)
                    """, (
                        mid, iid, pid,
                        b.get("name"), safe_int(b.get("runs")), safe_int(b.get("balls")),
                        safe_int(b.get("fours")), safe_int(b.get("sixes")),
                        safe_float(b.get("strkrate")), b.get("outdec")
                    ))
                except mysql.connector.IntegrityError:
                    continue

            # 🎯 Bowling
            for bow in inng.get("bowler", []):
                pid = safe_int(bow.get("id"))
                if not pid:
                    continue

                try:
                    cursor.execute("""
                        INSERT IGNORE INTO match_bowling
                        (match_id, innings_id, bowler_id, player_name, overs, maidens, runs, wickets, economy, balls)
                        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                        ON DUPLICATE KEY UPDATE player_name=VALUES(player_name)
                    """, (
                        mid, iid, pid,
                        bow.get("name"), 
                        safe_float(bow.get("overs")), 
                        safe_int(bow.get("maidens")),
                        safe_int(bow.get("runs")), 
                        safe_int(bow.get("wickets")),
                        safe_float(bow.get("economy")), 
                        safe_int(bow.get("balls"))
                    ))
                except mysql.connector.IntegrityError:
                    continue

            # Fall of Wickets
            for idx, fow in enumerate(inng.get("fow", {}).get("fow", []), start=1):
                pid = safe_int(fow.get("batsmanid"))
                if not pid:
                    continue

                try:
                    cursor.execute("""
                        INSERT IGNORE INTO match_fow
                        (match_id, innings_id, fow_order, batsman_id, player_name, score, overs)
                        VALUES (%s,%s,%s,%s,%s,%s,%s)
                        ON DUPLICATE KEY UPDATE player_name=VALUES(player_name)
                    """, (
                        mid, iid, idx, pid,
                        str(fow.get("batsmanname")), str(fow.get("runs")), str(fow.get("overnbr"))
                    ))
                except mysql.connector.IntegrityError:
                    continue

        inserted += 1

    conn.commit()
    cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
    cursor.close()
    conn.close()
    print(f"✅ Match Scorecards inserted")



# ----------------------
# Main
# ----------------------
if __name__ == "__main__":
    load_teams()
    load_players()
    load_venues()
    load_series_and_matches()
    load_match_details()
    load_player_stats()
    load_player_bowling_stats()
    load_scorecards()
    print("🎉 Full data load complete (all tables)")

