import streamlit as st
from pathlib import Path
import base64

st.set_page_config(page_title="MatchInfo", page_icon="🏏", layout="wide")

# ---------- CUSTOM CSS ----------
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
            
.page-row {
    display: flex;
    justify-content: center;
    padding: 30px 10vw 70px 10vw;
}

.st-emotion-cache-17c7e5f{
    width: 320px;
    height: 240px;
    font-size: 1.6rem;
    font-weight: 600;
    color: #232136;
    background: linear-gradient(120deg, #a8edea 0%, #fed6e3 100%);
    border-radius: 14px;
    display: flex;
    align-items: center; 
    justify-content: center;
    box-shadow: 0 3px 18px rgba(80,90,120,0.09);
    transition: box-shadow 0.2s;
    cursor: pointer;
}
            
.st-emotion-cache-17c7e5f:hover {
    background: linear-gradient(250deg, #a8edea 0%, #fed6e3 100%)
}
            
.footer-bar {
    width: 100%;
    text-align: center;
    font-size: 1.15rem;
    padding: 16px 0;
    color: #373666;
    margin-top: -30px;
}
            
</style>
""", unsafe_allow_html=True)

# ---------- HEADER & NAVIGATION ----------
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
# --- PAGE LINKS ---
st.markdown('<div class="page-row">', unsafe_allow_html=True)
cols = st.columns(3, gap="large")
with cols[0]:
    st.page_link("pages/Match Timelines.py", label="Match Timelines")
with cols[1]:
    st.page_link("pages/Top Player.py", label="Top Players")
with cols[2]:
    st.page_link("pages/Queries.py", label="Queries")

st.markdown('<div class="page-row">', unsafe_allow_html=True)


# --- FOOTER ---
st.markdown(
    """
    <div style="text-align: center; padding: 12px; font-size: 14px; color: #aaa;">
        Build using <a href="https://streamlit.io/" target="_blank" style="color:#FF4B4B; text-decoration: none;">Streamlit</a> & MySQL<br>
        © 2025 Neeraj Kumar | 
        <a href="https://github.com/Neeraj08823/Crickbuzz_project" target="_blank" style="color:#FF4B4B; text-decoration: none;">GitHub Repo</a>
    </div>
    """,
    unsafe_allow_html=True
)
st.markdown('</div>', unsafe_allow_html=True)
