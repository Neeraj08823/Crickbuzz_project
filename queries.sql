-- Que 1 - Find all players who represent India
SELECT
  player_id,
  name AS full_name,
  role AS playing_role,
  bat_style AS batting_style,
  bowl_style AS bowling_style
FROM players
WHERE country = 'India'
ORDER BY name;

-- Que 2 - Consistency (Avg Runs + StdDev of Runs, since 2022)
SELECT 
    mb.batsman_id AS player_id,
    p.name AS player_name,
    AVG(mb.runs) AS avg_runs,
    STDDEV_POP(mb.runs) AS run_stddev,
    COUNT(DISTINCT mb.match_id) AS matches_played
FROM match_batting mb
JOIN matches m ON mb.match_id = m.match_id
JOIN players p ON mb.batsman_id = p.player_id
WHERE m.start_date >= '2022-01-01'
  AND mb.balls >= 10
GROUP BY mb.batsman_id, p.name
HAVING matches_played >= 5
ORDER BY run_stddev ASC, avg_runs DESC;


-- Que 3 - Top 10 highest run scorers in ODI cricket
SELECT
  p.player_id,
  p.name,
  SUM(mb.runs) AS total_runs,
  ROUND(SUM(mb.runs) / NULLIF(SUM(CASE WHEN mb.dismissal IS NOT NULL AND mb.dismissal NOT LIKE '%not out%' THEN 1 ELSE 0 END),0), 2) AS batting_avg,
  SUM(CASE WHEN mb.runs >= 100 THEN 1 ELSE 0 END) AS centuries
FROM match_batting mb
JOIN matches m ON m.match_id = mb.match_id
JOIN players p ON p.player_id = mb.batsman_id
WHERE m.format = 'ODI'
GROUP BY p.player_id, p.name
ORDER BY total_runs DESC
LIMIT 10;

-- Que 4 - Venues with capacity >= 50000
SELECT
  venue_id,
  name AS venue_name,
  city,
  country,
  capacity
FROM venues
WHERE
  CAST(REPLACE(COALESCE(capacity, '0'), ',', '') AS UNSIGNED) >= 50000
ORDER BY CAST(REPLACE(COALESCE(capacity, '0'), ',', '') AS UNSIGNED) DESC;

-- Que 5 - How many matches each team has won
SELECT
  t.team_id,
  t.name AS team_name,
  COUNT(*) AS wins
FROM match_result mr
JOIN teams t ON t.team_id = mr.winning_team_id
GROUP BY t.team_id, t.name
ORDER BY wins DESC;

-- Que 6 - Count players by playing role
SELECT
  COALESCE(role, 'Unknown') AS role,
  COUNT(*) AS num_players
FROM players
GROUP BY role
ORDER BY num_players DESC;

-- Que 7 - Highest individual batting score per format
SELECT
  m.format,
  MAX(mb.runs) AS highest_score
FROM match_batting mb
JOIN matches m ON m.match_id = mb.match_id
GROUP BY m.format;

-- Que 8 - Series that started in 2024
SELECT 
    s.series_id,
    s.name AS series_name,
    hc.host_country,
    s.type AS match_type,
    s.start_date,
    COUNT(m.match_id) AS total_matches
FROM series s
LEFT JOIN matches m ON m.series_id = s.series_id
LEFT JOIN (
    SELECT x.series_id, x.host_country
    FROM (
        SELECT 
            m.series_id,
            v.country AS host_country,
            COUNT(*) AS cnt,
            ROW_NUMBER() OVER (PARTITION BY m.series_id ORDER BY COUNT(*) DESC) AS rn
        FROM matches m
        JOIN venues v ON v.venue_id = m.venue_id
        GROUP BY m.series_id, v.country
    ) x
    WHERE x.rn = 1
) hc ON hc.series_id = s.series_id
WHERE YEAR(s.start_date) = 2024
GROUP BY s.series_id, s.name, hc.host_country, s.type, s.start_date
ORDER BY s.start_date;


-- Que 9 - All-rounders with >1000 runs AND >50 wickets
SELECT 
    p.player_id,
    p.name AS player_name,
    b.format,
    b.runs AS total_runs,
    bw.wickets AS total_wickets
FROM players p
JOIN player_stats b 
    ON p.player_id = b.player_id
JOIN player_bowling_stats bw 
    ON p.player_id = bw.player_id 
    AND b.format = bw.format   -- Match format consistency
WHERE b.runs > 1000
  AND bw.wickets > 50
ORDER BY b.runs DESC;

-- Que 10 - Yearly Batting Performance Since 2020
SELECT 
    mb.batsman_id AS player_id,
    p.name AS player_name,
    YEAR(m.start_date) AS match_year,
    AVG(mb.runs) AS avg_runs_per_match,
    AVG(mb.strike_rate) AS avg_strike_rate,
    COUNT(DISTINCT mb.match_id) AS matches_played
FROM match_batting mb
JOIN matches m ON mb.match_id = m.match_id
JOIN players p ON mb.batsman_id = p.player_id
WHERE YEAR(m.start_date) >= 2020
GROUP BY mb.batsman_id, p.name, YEAR(m.start_date)
HAVING COUNT(DISTINCT mb.match_id) >= 5
ORDER BY player_name, match_year;

-- Que 11 - Compare player performance across formats (players who played ≥2 formats)
SELECT
  p.player_id,
  p.name,
  SUM(CASE WHEN m.format = 'Test' THEN mb.runs ELSE 0 END) AS runs_test,
  SUM(CASE WHEN m.format = 'ODI'  THEN mb.runs ELSE 0 END) AS runs_odi,
  SUM(CASE WHEN m.format = 'T20I' THEN mb.runs ELSE 0 END) AS runs_t20,
  ROUND(SUM(mb.runs) / NULLIF(SUM(CASE WHEN mb.dismissal IS NOT NULL AND mb.dismissal NOT LIKE '%not out%' THEN 1 ELSE 0 END),0),2) AS overall_avg,
  COUNT(DISTINCT m.format) AS formats_played
FROM players p
JOIN match_batting mb ON mb.batsman_id = p.player_id
JOIN matches m ON m.match_id = mb.match_id
GROUP BY p.player_id, p.name
HAVING formats_played >= 2
ORDER BY overall_avg DESC;

-- Que 12 - Home vs Away performance per team (wins)
SELECT
  t.team_id,
  t.name AS team_name,
  SUM(CASE WHEN v.country = t.country AND mr.winning_team_id = t.team_id THEN 1 ELSE 0 END) AS home_wins,
  SUM(CASE WHEN v.country <> t.country AND mr.winning_team_id = t.team_id THEN 1 ELSE 0 END) AS away_wins
FROM teams t
LEFT JOIN matches m ON (m.match_id IS NOT NULL)  -- placeholder to allow venue join
LEFT JOIN match_result mr ON mr.match_id = m.match_id
LEFT JOIN venues v ON v.venue_id = m.venue_id
LEFT JOIN match_teams mt ON mt.match_id = m.match_id AND mt.team_id = t.team_id
WHERE mt.team_id IS NOT NULL
GROUP BY t.team_id, t.name
ORDER BY (home_wins + away_wins) DESC;

-- Que 13 - Bowlers performance per venue
WITH bowler_match AS (
    SELECT 
        mbw.bowler_id,
        m.venue_id,
        mbw.match_id,
        SUM(mbw.overs) AS overs_in_match,
        SUM(mbw.wickets) AS wickets_in_match,
        AVG(mbw.economy) AS avg_econ_in_match
    FROM match_bowling mbw
    JOIN matches m ON m.match_id = mbw.match_id
    GROUP BY mbw.bowler_id, m.venue_id, mbw.match_id
),
eligible AS (
    SELECT * 
    FROM bowler_match
    WHERE overs_in_match >= 4
)
SELECT 
    e.bowler_id,
    p.name AS bowler_name,
    e.venue_id,
    v.name AS venue_name,
    COUNT(DISTINCT e.match_id) AS matches_played,
    ROUND(SUM(e.wickets_in_match) / NULLIF(COUNT(DISTINCT e.match_id),0), 2) AS avg_wickets_per_match,
    ROUND(AVG(e.avg_econ_in_match), 2) AS avg_economy,
    SUM(e.wickets_in_match) AS total_wickets
FROM eligible e
JOIN players p ON p.player_id = e.bowler_id
JOIN venues v ON v.venue_id = e.venue_id
GROUP BY e.bowler_id, e.venue_id, p.name, v.name
HAVING COUNT(DISTINCT e.match_id) >= 3
ORDER BY total_wickets DESC;

-- Que 14 - Players who excel in close matches
WITH close_matches AS (
  SELECT mr.match_id
  FROM match_result mr
  WHERE (mr.win_by_runs IS NOT NULL AND mr.win_by_runs < 50)
     OR (mr.win_by_innings IS NOT NULL AND mr.win_by_innings < 5)
)
SELECT
  p.player_id,
  p.name,
  ROUND(AVG(mb.runs),2) AS avg_runs_in_close_matches,
  COUNT(DISTINCT mb.match_id) AS close_matches_played,
  SUM(CASE WHEN mr.winning_team_id = mr_team.team_id THEN 1 ELSE 0 END) AS close_matches_won_when_they_batted
FROM match_batting mb
JOIN players p ON p.player_id = mb.batsman_id
JOIN close_matches cm ON cm.match_id = mb.match_id
JOIN match_roster mr_team ON mr_team.match_id = mb.match_id AND mr_team.player_id = p.player_id
LEFT JOIN match_result mr ON mr.match_id = mb.match_id
GROUP BY p.player_id, p.name
HAVING close_matches_played >= 1
ORDER BY avg_runs_in_close_matches DESC;

-- Que 15 - Does winning the toss give advantage? % won by toss winner by toss decision
SELECT
  mt.decision AS toss_decision,
  COUNT(*) AS total_matches,
  SUM(CASE WHEN mt.toss_winner_id = mr.winning_team_id THEN 1 ELSE 0 END) AS matches_won_by_toss_winner,
  ROUND(100 * SUM(CASE WHEN mt.toss_winner_id = mr.winning_team_id THEN 1 ELSE 0 END) / COUNT(*), 2) AS pct_won_by_toss_winner
FROM match_toss mt
JOIN match_result mr ON mr.match_id = mt.match_id
GROUP BY mt.decision;

-- Que 16 - Matches + Batting Avg per Format
SELECT 
    p.player_id,
    p.name AS player_name,
    SUM(CASE WHEN ps.format = 'Test' THEN ps.matches ELSE 0 END) AS test_matches,
    SUM(CASE WHEN ps.format = 'ODI' THEN ps.matches ELSE 0 END) AS odi_matches,
    SUM(CASE WHEN ps.format = 'T20' OR ps.format = 'T20I' THEN ps.matches ELSE 0 END) AS t20_matches,
    MAX(CASE WHEN ps.format = 'Test' THEN ps.average END) AS test_avg,
    MAX(CASE WHEN ps.format = 'ODI' THEN ps.average END) AS odi_avg,
    MAX(CASE WHEN ps.format = 'T20' OR ps.format = 'T20I' THEN ps.average END) AS t20_avg,
    SUM(ps.matches) AS total_matches
FROM players p
JOIN player_stats ps ON p.player_id = ps.player_id
GROUP BY p.player_id, p.name
HAVING SUM(ps.matches) >= 20
ORDER BY total_matches DESC;
