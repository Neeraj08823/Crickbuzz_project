import os
import streamlit as st
import mysql.connector
from dotenv import load_dotenv
import pandas as pd
from pathlib import Path
import base64

st.set_page_config(page_title="Top Player Stats", page_icon="🏏", layout="wide")

load_dotenv()
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "cricbuzz_db")

def get_connection():
    return mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )


st.markdown("""
<style>
.logo-box {
    width: 100px; height: 10px;
}
            
.title {
    font-size: 3rem;
    font-weight: 700;
    text-align: center;
    flex: 1;
    color: #273348;
    color: linear-gradient(90deg, #72e4fe 0%, #7b7ffe 50%, #eebcf7 100%);
    letter-spacing: 0.5px;
}

.st-emotion-cache-r44huj h1 {
    font-size: 2.75rem;
    font-weight: 700;
    text-align: center;
    padding: 1.25rem 0px 1rem;
}

</style>
""", unsafe_allow_html=True)

def get_team_list(conn):
    teams_sql = """
    SELECT team_id, country
    FROM teams
    WHERE team_id BETWEEN 2 AND 27
    ORDER BY country
    """
    df_teams = pd.read_sql(teams_sql, conn)
    return df_teams

def get_top_players(conn, country):
    top_sql = """
    SELECT
        p.player_id,
        p.name
    FROM players p
    JOIN player_stats ps ON p.player_id = ps.player_id
    WHERE p.country = %s
    GROUP BY p.player_id, p.name
    ORDER BY SUM(ps.runs) DESC
    LIMIT 10
    """
    df_top = pd.read_sql(top_sql, conn, params=(country,))
    return df_top

def get_player_stats(conn, player_id):
    stat_sql = """
    SELECT format, matches, runs, highest, sixes, hundreds, double_hundreds
    FROM player_stats
    WHERE player_id = %s
    """
    df_stats = pd.read_sql(stat_sql, conn, params=(int(player_id),))
    return df_stats.set_index('format').to_dict(orient='index')


# Logo
logo_path = Path("assets/Match-logo.png")
if logo_path.exists():
    with open(logo_path, "rb") as img_file:
        b64_img = base64.b64encode(img_file.read()).decode()
        logo_html = f'<img src="data:image/png;base64,{b64_img}" style="height:100px;">'
else:
    logo_html = 'LOGO Here'
st.markdown(f'<div class="logo-box">{logo_html}</div>', unsafe_allow_html=True)
# Title
st.markdown('<div class="title">🏏 MatchInfo</div>', unsafe_allow_html=True)
st.markdown(""" <div style="border: 2px solid #01b489; margin-bottom: 15px;"> </div>""", unsafe_allow_html=True)
st.title("🌟 Top Player Stats")
# List of allowed countries
allowed_countries = [
    "India",
    "Australia",
    "Sri Lanka",
    "Afghanistan",
    "Bangladesh",
    "England",
    "West Indies",
    "Afghanistan"
]

try:
    conn = get_connection()
    df_teams = get_team_list(conn)
    # Filter to allowed countries only
    df_teams_filtered = df_teams[df_teams['country'].isin(allowed_countries)]
    country_names = df_teams_filtered['country'].tolist()

    col1, col2 = st.columns([1, 2])

    with col1:
        default_index = country_names.index("India") if "India" in country_names else 0
        selected_country = st.selectbox("Select Country", country_names, index=default_index)
        df_players = get_top_players(conn, selected_country)
        player_names = df_players['name'].tolist()
        selected_player = st.selectbox("Select Player", player_names)
        st.markdown(f"<h1 style='margin-top: 60px; font-weight:bold; font-size:48px; color:#222;'>{selected_player}</h1>", unsafe_allow_html=True)

    with col2:
        if selected_player:
            selected_player_row = df_players[df_players['name'] == selected_player].iloc[0]
            player_id = int(selected_player_row['player_id'])

            stats = get_player_stats(conn, player_id)

            for fmt in ['ODI', 'T20', 'Test']:
                if fmt in stats:
                    fmt_stats = stats[fmt]
                    st.markdown(f"### {fmt} Stats")
                    card_cols = st.columns(6)
                    icons = [
                        "🏏",  # Matches
                        "🎮",  # Runs
                        "📊",  # Highest
                        "6️⃣",  # Sixes
                        "💯",  # 100s
                        "🎯",  # 200s
                    ]
                    fields = ['matches', 'runs', 'highest', 'sixes', 'hundreds', 'double_hundreds']
                    labels = ['Matches', 'Runs', 'Highest', 'Sixes', "100's", "200's"]

                    for i, (icon, field, label) in enumerate(zip(icons, fields, labels)):
                        with card_cols[i]:
                            st.markdown(f"""
                                <div style='border:1px solid #EEE; border-radius:8px; padding:8px; text-align:center;'>
                                    <span style='font-size:32px'>{icon}</span><br>
                                    <span style='font-weight:bold'>{label}</span><br>
                                    <span style='font-size:22px'>{fmt_stats.get(field, 0)}</span>
                                </div>
                            """, unsafe_allow_html=True)
except Exception as e:
    st.error(f"Error loading stats: {e}")
finally:
    if 'conn' in locals() and conn.is_connected():
        conn.close()

# --- FOOTER ---
st.markdown(
    """
    <div style="text-align: center; padding: 12px; font-size: 14px; color: #aaa;">
        Build using <a href="https://streamlit.io/" target="_blank" style="color:#FF4B4B; text-decoration: none;">Streamlit</a> & MySQL<br>
        © 2025 Neeraj Kumar | 
        <a href="https://github.com/Neeraj08823/Local-Food-Wastage-Management-System" target="_blank" style="color:#FF4B4B; text-decoration: none;">GitHub Repo</a>
    </div>
    """,
    unsafe_allow_html=True
)
st.markdown('</div>', unsafe_allow_html=True)