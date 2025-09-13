import streamlit as st
from utils.fetch_api import fetch_live_matches, fetch_recent_matches, fetch_upcoming_matches  # you may need to create fetch_recent_matches
from datetime import datetime
from pathlib import Path
import base64


st.set_page_config(page_title="Matches Dashboard", page_icon="🏏", layout="wide")


def format_milliseconds(ms):
    try:
        return datetime.fromtimestamp(ms / 1000).strftime("%Y-%m-%d %H:%M:%S")
    except:
        return "N/A"


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


# --- Section: Live & Upcoming Matches ---
st.title("🔴 Live Matches")
live_data = fetch_live_matches()

if not live_data or "typeMatches" not in live_data:
    st.warning("⚠️ No live or upcoming matches found.")
else:
    for block in live_data["typeMatches"]:
        match_type = block.get("matchType", "Unknown")
        st.header(f"🏏 {match_type} Matches")

        for series in block.get("seriesMatches", []):
            if "seriesAdWrapper" not in series:
                continue

            series_info = series["seriesAdWrapper"]
            st.subheader(f"📌 {series_info.get('seriesName', 'Unnamed Series')}")

            for match in series_info.get("matches", []):
                match_info = match.get("matchInfo", {})
                if not match_info:
                    continue

                col1, col2 = st.columns([2, 3])
                with col1:
                    team1 = match_info.get('team1', {}).get('teamName', 'Team 1')
                    team2 = match_info.get('team2', {}).get('teamName', 'Team 2')
                    st.markdown(f"**{team1} 🆚 {team2}**")
                    st.caption(f"Format: {match_info.get('matchFormat', 'N/A')}")
                    st.caption(f"Status: {match_info.get('status', 'N/A')}")

                with col2:
                    venue = match_info.get('venueInfo', {}).get('ground', 'Unknown')
                    city = match_info.get('venueInfo', {}).get('city', '')
                    st.markdown(f"🏟️ Venue: {venue}, {city}")
                    raw_ts = match_info.get('startDate')
                    readable_ts = format_milliseconds(int(raw_ts)) if raw_ts else "N/A"
                    st.markdown(f"🕒 Start Date: {readable_ts}")

                st.divider()


# --- Section: Upcoming Matches (Future) ---

st.title("📅 Upcoming Matches")

upcoming_data = fetch_upcoming_matches()  # Ideally fetch from a dedicated upcoming matches endpoint

if not upcoming_data or "typeMatches" not in upcoming_data:
    st.warning("⚠️ No upcoming matches found.")
else:
    for block in upcoming_data["typeMatches"]:
        match_type = block.get("matchType", "Unknown")
        st.header(f"🏏 {match_type} Upcoming Matches")

        for series in block.get("seriesMatches", []):
            if "seriesAdWrapper" not in series:
                continue

            series_info = series["seriesAdWrapper"]
            st.subheader(f"📌 {series_info.get('seriesName', 'Unnamed Series')}")

            for match in series_info.get("matches", [])[:5]:  # Limit to first 5 upcoming matches 
                match_info = match.get("matchInfo", {})
                if not match_info:
                    continue

                # Filter for future start dates only (optional, depending on your API)
                raw_start = match_info.get('startDate')
                if raw_start and int(raw_start) > int(datetime.now().timestamp() * 1000):
                    col1, col2 = st.columns([2, 3])
                    with col1:
                        team1 = match_info.get('team1', {}).get('teamName', 'Team 1')
                        team2 = match_info.get('team2', {}).get('teamName', 'Team 2')
                        st.markdown(f"**{team1} 🆚 {team2}**")
                        st.caption(f"Format: {match_info.get('matchFormat', 'N/A')}")
                        st.caption(f"Status: {match_info.get('status', 'N/A')}")

                    with col2:
                        venue = match_info.get('venueInfo', {}).get('ground', 'Unknown')
                        city = match_info.get('venueInfo', {}).get('city', '')
                        st.markdown(f"🏟️ Venue: {venue}, {city}")
                        readable_ts = format_milliseconds(int(raw_start)) if raw_start else "N/A"
                        st.markdown(f"🕒 Start Date: {readable_ts}")
                    st.divider()


# --- Section: Recent Matches (Past) ---

st.title("⏮️ Recent Matches")
recent_data = fetch_recent_matches()

if not recent_data or "typeMatches" not in recent_data:
    st.warning("⚠️ No recent matches found.")
else:
    for block in recent_data["typeMatches"]:
        match_type = block.get("matchType", "Unknown")
        st.header(f"🏏 {match_type} Recent Matches")

        for series in block.get("seriesMatches", []):
            if "seriesAdWrapper" not in series:
                continue

            series_info = series["seriesAdWrapper"]
            st.subheader(f"📌 {series_info.get('seriesName', 'Unnamed Series')}")

            for match in series_info.get("matches", [])[:5]: # Limit to first 5 recent matches
                match_info = match.get("matchInfo", {})
                if not match_info:
                    continue

                # Filter matches with startDate less than now
                raw_start = match_info.get('startDate')
                if raw_start and int(raw_start) <= int(datetime.now().timestamp() * 1000):
                    col1, col2 = st.columns([2, 3])
                    with col1:
                        team1 = match_info.get('team1', {}).get('teamName', 'Team 1')
                        team2 = match_info.get('team2', {}).get('teamName', 'Team 2')
                        st.markdown(f"**{team1} 🆚 {team2}**")
                        st.caption(f"Format: {match_info.get('matchFormat', 'N/A')}")
                        st.caption(f"Status: {match_info.get('status', 'N/A')}")

                    with col2:
                        venue = match_info.get('venueInfo', {}).get('ground', 'Unknown')
                        city = match_info.get('venueInfo', {}).get('city', '')
                        st.markdown(f"🏟️ Venue: {venue}, {city}")
                        readable_ts = format_milliseconds(int(raw_start)) if raw_start else "N/A"
                        st.markdown(f"🕒 Start Date: {readable_ts}")
                    st.divider()


# --- FOOTER ---
st.markdown(
    """
    <div style="text-align: center; padding: 12px; font-size: 14px; color: #aaa;">
        Build using <a href="https://streamlit.io/" target="_blank" style="color:#FF4B4B; text-decoration: none;">Streamlit</a> & MySQL<br>
        © 2025 Neeraj Kumar | 
        <a href="https://github.com/Neeraj08823/Local-Food-Wastage-Management-System" target="_blank" style="color:#FF4B4B; text-decoration: none;">GitHub Repo</a>
    </div>
    """,
    unsafe_allow_html=True,
)
st.markdown('</div>', unsafe_allow_html=True)
