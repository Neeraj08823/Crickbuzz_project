import os
import  requests
import streamlit as st
import mysql.connector
from dotenv import load_dotenv
import pandas as pd
from pathlib import Path
import base64

st.set_page_config(page_title="SQL Analytics", page_icon="🏏", layout="wide")

load_dotenv()
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "cricbuzz_db")

def get_connection():
    if "mysql" in st.secrets:  # when running on Streamlit Cloud
        return mysql.connector.connect(
            host=st.secrets["mysql"]["host"],
            port=st.secrets["mysql"].get("port", "3306"),
            user=st.secrets["mysql"]["user"],
            password=st.secrets["mysql"]["password"],
            database=st.secrets["mysql"]["database"]
        )
    else:  # local development with .env
        return mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
# ---------- Load Queries from GitHub ----------
@st.cache_data
def load_queries():
    url = "https://github.com/Neeraj08823/Crickbuzz_project/blob/main/queries.sql"
    sql_text = requests.get(url).text
    queries = [q.strip() for q in sql_text.split(";") if q.strip()]
    return queries

queries = load_queries()


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
st.title("📑 SQL Analytics")

# ---------- Load and Parse SQL Queries ----------
def parse_queries_with_comments(script):
    blocks = []
    current_comment = None
    current_query = []
    for line in script.splitlines():
        if line.strip().startswith('--'):
            if current_comment and current_query:
                blocks.append( (current_comment, '\n'.join(current_query).strip().rstrip(';') + ';') )
                current_query = []
            current_comment = line.strip()
        else:
            if line.strip() or current_query:
                current_query.append(line)
    if current_comment and current_query:
        blocks.append( (current_comment, '\n'.join(current_query).strip().rstrip(';') + ';') )
    return [block for block in blocks if block[1] and len(block[1].strip()) > 2]

with open("queries.sql", "r") as f:
    sql_script = f.read()
queries = parse_queries_with_comments(sql_script)
comment_list = [item[0][2:].strip() if item[0].startswith('--') else item[0] for item in queries]

# ---------- Layout ----------
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("🧩 Select Analysis Query")
    selected_label = st.selectbox("", comment_list, label_visibility='collapsed')
    selected_idx = comment_list.index(selected_label)
    run_query = st.button("Ask ❔", use_container_width=True)
    if run_query:
        st.success("✅ Query Executed Successfully!")

with col2:
    if run_query:
        st.subheader("📊 Details")
        try:
            conn = get_connection()
            df = pd.read_sql(queries[selected_idx][1], conn)
            st.dataframe(df, use_container_width=True)
        except Exception as e:
            st.error(f"❌ Error: {e}")
        finally:
            if 'conn' in locals() and conn.is_connected():
                conn.close()


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