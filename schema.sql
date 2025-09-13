-- schema.sql
CREATE DATABASE cricbuzz_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE cricbuzz_db;

-- Teams
CREATE TABLE IF NOT EXISTS teams (
    team_id INT PRIMARY KEY,
    name VARCHAR(255),
    short_name VARCHAR(50),
    country VARCHAR(100),
    image_url VARCHAR(500)
);

-- Players
CREATE TABLE IF NOT EXISTS players (
    player_id INT PRIMARY KEY,
    name VARCHAR(255),
    nickname VARCHAR(255),
    role VARCHAR(100),
    bat_style VARCHAR(100),
    bowl_style VARCHAR(100),
    dob VARCHAR(100),
    birthplace VARCHAR(255),
    country VARCHAR(100),
    image_url VARCHAR(500)
);

-- Player-Team mapping
CREATE TABLE IF NOT EXISTS player_team (
    player_id INT,
    team_id INT,
    PRIMARY KEY (player_id, team_id),
    FOREIGN KEY (player_id) REFERENCES players(player_id),
    FOREIGN KEY (team_id) REFERENCES teams(team_id)
);

-- Venues
CREATE TABLE IF NOT EXISTS venues (
    venue_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255),
    city VARCHAR(255),
    country VARCHAR(100),
    timezone VARCHAR(20),
    established VARCHAR(50),
    capacity VARCHAR(50),
    known_as VARCHAR(500),
    ends VARCHAR(255),
    home_team VARCHAR(255),
    floodlights BOOLEAN,
    image_url VARCHAR(500)
);

-- Series
CREATE TABLE IF NOT EXISTS series (
    series_id INT PRIMARY KEY,
    name VARCHAR(255),
    type VARCHAR(100),
    start_date DATETIME,
    end_date DATETIME
);

-- Matches
CREATE TABLE IF NOT EXISTS matches (
    match_id INT PRIMARY KEY,
    series_id INT,
    name VARCHAR(255),
    format VARCHAR(50),
    start_date DATETIME,
    end_date DATETIME,
    state VARCHAR(50),
    status VARCHAR(500),
    venue_id INT,
    FOREIGN KEY (series_id) REFERENCES series(series_id),
    FOREIGN KEY (venue_id) REFERENCES venues(venue_id)
);

-- Match Teams
CREATE TABLE IF NOT EXISTS match_teams (
    match_id INT NOT NULL,
    team_id INT NOT NULL,
    team_role VARCHAR(10) NOT NULL,
    PRIMARY KEY (match_id, team_id, team_role)
);

-- Match Player Batting
CREATE TABLE IF NOT EXISTS player_stats (
    player_id INT,
    format VARCHAR(50),
    matches INT,
    innings INT,
    runs INT,
    balls INT,
    highest VARCHAR(20),
    average FLOAT,
    strike_rate FLOAT,
    not_outs INT,
    fours INT,
    sixes INT,
    ducks INT,
    fifties INT,
    hundreds INT,
    double_hundreds INT,
    triple_hundreds INT,
    quadruple_hundreds INT,
    PRIMARY KEY (player_id, format),
    FOREIGN KEY (player_id) REFERENCES players(player_id)
);

-- Match Player Bowling
CREATE TABLE IF NOT EXISTS player_bowling_stats (
    player_id INT,
    format VARCHAR(50),
    matches INT,
    innings INT,
    balls INT,
    runs INT,
    maidens INT,
    wickets INT,
    average FLOAT,
    economy FLOAT,
    strike_rate FLOAT,
    best_bowling_innings VARCHAR(20),
    best_bowling_match VARCHAR(20),
    four_wickets INT,
    five_wickets INT,
    ten_wickets INT,
    PRIMARY KEY (player_id, format),
    FOREIGN KEY (player_id) REFERENCES players(player_id)
);


-- Match-Result mapping
CREATE TABLE IF NOT EXISTS match_result (
    match_id INT PRIMARY KEY,
    result_type VARCHAR(50),
    winning_team VARCHAR(100),
    winning_team_id INT,
    winning_margin INT,
    win_by_runs BOOLEAN,
    win_by_innings BOOLEAN,
    FOREIGN KEY (match_id) REFERENCES matches(match_id)
);

-- Match Awards
CREATE TABLE IF NOT EXISTS match_awards (
    award_id INT AUTO_INCREMENT PRIMARY KEY,
    match_id INT,
    award_type VARCHAR(50),
    player_id INT,
    player_name VARCHAR(100),
    team_name VARCHAR(100),
    FOREIGN KEY (match_id) REFERENCES matches(match_id)
);

-- Match Toss
CREATE TABLE IF NOT EXISTS match_toss (
    match_id INT PRIMARY KEY,
    toss_winner_id INT,
    toss_winner_name VARCHAR(100),
    decision VARCHAR(50),
    FOREIGN KEY (match_id) REFERENCES matches(match_id)
);


-- Match Officials
CREATE TABLE IF NOT EXISTS match_officials (
    match_id INT PRIMARY KEY,
    umpire1_id INT, umpire1_name VARCHAR(100), umpire1_country VARCHAR(50),
    umpire2_id INT, umpire2_name VARCHAR(100), umpire2_country VARCHAR(50),
    umpire3_id INT, umpire3_name VARCHAR(100), umpire3_country VARCHAR(50),
    referee_id INT, referee_name VARCHAR(100), referee_country VARCHAR(50),
    FOREIGN KEY (match_id) REFERENCES matches(match_id)
);

-- Match Roster
CREATE TABLE IF NOT EXISTS match_roster (
    match_id INT,
    team_id INT,
    player_id INT,
    player_name VARCHAR(100),
    full_name VARCHAR(150),
    nick_name VARCHAR(100),
    role VARCHAR(100),
    batting_style VARCHAR(50),
    bowling_style VARCHAR(50),
    is_captain BOOLEAN,
    is_keeper BOOLEAN,
    is_substitute BOOLEAN,
    face_image_id BIGINT,
    PRIMARY KEY (match_id, player_id),
    FOREIGN KEY (match_id) REFERENCES matches(match_id),
    FOREIGN KEY (team_id) REFERENCES teams(team_id),
    FOREIGN KEY (player_id) REFERENCES players(player_id)
);


-- Match Batting
CREATE TABLE IF NOT EXISTS match_batting (
    match_id INT,
    innings_id INT,
    batsman_id INT,
    player_name VARCHAR(100),
    runs INT,
    balls INT,
    fours INT,
    sixes INT,
    strike_rate FLOAT,
    dismissal VARCHAR(255),
    PRIMARY KEY (match_id, innings_id, batsman_id),
    FOREIGN KEY (match_id) REFERENCES matches(match_id),
    FOREIGN KEY (batsman_id) REFERENCES players(player_id)
);

-- Match Bowling
CREATE TABLE IF NOT EXISTS match_bowling (
    match_id INT,
    innings_id INT,
    bowler_id INT,
    player_name VARCHAR(100),
    overs FLOAT,
    maidens INT,
    runs INT,
    wickets INT,
    economy FLOAT,
    balls INT,
    PRIMARY KEY (match_id, innings_id, bowler_id),
    FOREIGN KEY (match_id) REFERENCES matches(match_id),
    FOREIGN KEY (bowler_id) REFERENCES players(player_id)
);

-- Match Fall of Wickets
CREATE TABLE IF NOT EXISTS match_fow (
    match_id INT,
    innings_id INT,
    fow_order INT,
    batsman_id INT,
    player_name VARCHAR(100),
    score VARCHAR(50),
    overs VARCHAR(20),
    PRIMARY KEY (match_id, innings_id, fow_order),
    FOREIGN KEY (match_id) REFERENCES matches(match_id),
    FOREIGN KEY (batsman_id) REFERENCES players(player_id)
);



