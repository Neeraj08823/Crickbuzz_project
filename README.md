# 🏏 Cricbuzz LiveStats: Real-Time Cricket Insights & SQL-Based Analytics

[![MySQL](https://img.shields.io/badge/MySQL-Database-orange?logo=mysql)](https://www.mysql.com/)
[![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-App-red?logo=streamlit)](https://streamlit.io/)
[![VS Code](https://img.shields.io/badge/VSCode-Editor-0078d7?logo=visualstudiocode&logoColor=white)](https://code.visualstudio.com/)  
[![pandas](https://img.shields.io/badge/pandas-Data%20Analysis-blue?logo=pandas)](https://pandas.pydata.org/)
[![REST API](https://img.shields.io/badge/REST-API-purple?logo=fastapi&logoColor=white)](https://restfulapi.net/)
[![Cricket](https://img.shields.io/badge/Cricket-Analytics-green?logo=cricket&logoColor=white)](#)
![Status](https://img.shields.io/badge/Status-Completed-brightgreen)

---

## 📑 Table of Contents

- 📌 [Overview](#-overview)
- 🔍 [Features](#-Features)
- 🗄 [Database Schema](#-Database-Schema)
- 🚀 [Tech Stack](#-Tech-Stack)
- 📖 [SQL Practice Questions](#-SQL-Practice-Questions)
- 🏗 [Project Structure](#-Project-Structure)

---

## 📌 Overview

A comprehensive **Cricket Analytics Dashboard** that integrates **live match data from the Cricbuzz API** with a **MySQL database** to deliver **player statistics, and advanced SQL-driven analytics**. Built using **Python, Streamlit, SQL, and REST API integration**.

---

## 🔍 Features

### 🔴 Live Match Page

- Real-time match updates fetched via **Cricbuzz API**.
- Detailed scorecards with batsmen, bowlers, match status, and venue info.

### 🏆 Top Player Stats Page

- Display **top player statistics** (most runs, highest scores, etc.).

### 📊 SQL Queries & Analytics Page

- Includes insights like **top scorers, venue stats, partnerships, toss analysis, form trends**.

---

## 🗄 Database Schema

The MySQL schema is normalized to support all analytics use cases:

- **players** → Player info (id, name, role, styles, country).
- **teams** → Team details.
- **venues** → Venue info (city, country, capacity).
- **series** → Series details (name, host, type, dates).
- **matches** → Match metadata (teams, winner, toss, venue).
- **batting_stats** → Player batting performances.
- **bowling_stats** → Player bowling performances.

---

## 🚀 Tech Stack

- **Python** → Data fetching & processing.
- **Streamlit** → Interactive dashboard.
- **MySQL** → Database storage & SQL analytics.
- **REST API (Cricbuzz via RapidAPI)** → Live Cricbuzz cricket data.
- **pandas** → Data manipulation.
- **requests** → API integration.

---

## 📖 SQL Practice Questions

This project includes **16 SQL queries** across levels:

Example:

```sql
-- Q1: Find all players who represent India
SELECT full_name, role, batting_style, bowling_style
FROM players
WHERE country = 'India';
```

---

## 🏗 Project Structure

```
📦 Cricbuzz
 ┣ 📂 utils
 ┃ ┣ 📜 db_loader.py
 ┃ ┣ 📜 fetch_api.py
 ┃ ┗ 📜 fetch_api_base.py
 ┣ 📂 assets
 ┃ ┣ 📜 Match-logo.png
 ┣ 📂 pages
 ┃ ┣ 📜 1_LiveMatch.py
 ┃ ┣ 📜 2_PlayerStats.py
 ┃ ┣ 📜 3_SQLAnalytics.py
 ┣ 📜 app.py
 ┣ 📜 schema.sql
 ┣ 📜 queries.sql
 ┣ 📜 requirements.txt
 ┣ 📜 README.md
```

---

## 👨‍💻 Author

**Neeraj Kumar**

---
