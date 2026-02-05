import streamlit as st
import pandas as pd
from sqlalchemy import create_engine

# -------------------------------------------------
# Page Config
# -------------------------------------------------
st.set_page_config(
    page_title="NCAA Football Analytics Platform",
    page_icon="🏈",
    layout="wide"
)

st.title("🏈 NCAA Football Analytics Platform")
st.write("Centralized system for teams, players, rankings, and performance trends.")

# -------------------------------------------------
# Database Connection
# -------------------------------------------------
engine = create_engine(
    "postgresql://postgres:Tejas%40123@localhost:5432/ncaafb_db"
)

# -------------------------------------------------
# Sidebar Navigation
# -------------------------------------------------
st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Go to",
    [
        "🏠 Home",
        "🧩 Teams Explorer",
        "👥 Players Explorer",
        "📅 Seasons",
        "🏆 Rankings",
        "📌 Team Profile",
        "🏟️ Venues",
        "🧑‍🏫 Coaches",
        "📊 Analysis"
    ]
)

# =================================================
# HOME PAGE
# =================================================
if page == "🏠 Home":

    st.header("🏠 Home Dashboard")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("Teams & Conferences")
        teams_df = pd.read_sql(
            "SELECT market, name, conference_id FROM teams",
            engine
        )
        st.dataframe(teams_df)

    with col2:
        st.subheader("Active Players")
        players_df = pd.read_sql(
            """
            SELECT first_name, last_name, position, status
            FROM players
            WHERE status = 'Active'
            LIMIT 50
            """,
            engine
        )
        st.dataframe(players_df)

    with col3:
        st.subheader("Seasons")
        seasons_df = pd.read_sql(
            "SELECT year, start_date, end_date, status FROM seasons",
            engine
        )
        st.dataframe(seasons_df)

# =================================================
# TEAMS EXPLORER
# =================================================
elif page == "🧩 Teams Explorer":

    st.header("🧩 Teams Explorer")

    query = """
    SELECT 
        t.team_id,
        t.market,
        t.name,
        t.alias,
        t.founded,
        t.championships_won,
        c.name AS conference,
        d.division_name AS division
    FROM teams t
    LEFT JOIN conferences c ON t.conference_id = c.conference_id
    LEFT JOIN divisions d ON t.division_id = d.division_id
    """

    teams_df = pd.read_sql(query, engine)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        conf_filter = st.selectbox(
            "Conference",
            ["All"] + sorted(teams_df["conference"].dropna().unique())
        )

    with col2:
        div_filter = st.selectbox(
            "Division",
            ["All"] + sorted(teams_df["division"].dropna().unique())
        )

    with col3:
        search = st.text_input("Search Team")

    with col4:
        min_champ = st.number_input(
            "Min championships",
            min_value=0,
            step=1
        )

    if conf_filter != "All":
        teams_df = teams_df[teams_df["conference"] == conf_filter]

    if div_filter != "All":
        teams_df = teams_df[teams_df["division"] == div_filter]

    teams_df = teams_df[teams_df["championships_won"] >= min_champ]

    if search:
        teams_df = teams_df[
            teams_df["name"].str.contains(search, case=False, na=False)
            | teams_df["market"].str.contains(search, case=False, na=False)
            | teams_df["alias"].str.contains(search, case=False, na=False)
        ]

    st.dataframe(teams_df, use_container_width=True)

# =================================================
# PLAYERS EXPLORER
# =================================================
elif page == "👥 Players Explorer":

    st.header("👥 Players Explorer")

    query = """
    SELECT 
        p.first_name,
        p.last_name,
        p.position,
        p.height,
        p.weight,
        p.eligibility,
        p.status,
        t.name AS team_name
    FROM players p
    LEFT JOIN teams t ON p.team_id = t.team_id
    """

    players_df = pd.read_sql(query, engine)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        position_filter = st.selectbox(
            "Position",
            ["All"] + sorted(players_df["position"].dropna().unique())
        )

    with col2:
        status_filter = st.selectbox(
            "Status",
            ["All"] + sorted(players_df["status"].dropna().unique())
        )

    with col3:
        eligibility_filter = st.selectbox(
            "Eligibility",
            ["All"] + sorted(players_df["eligibility"].dropna().astype(str).unique())
        )

    with col4:
        search = st.text_input("Search Player / Team")

    if position_filter != "All":
        players_df = players_df[players_df["position"] == position_filter]

    if status_filter != "All":
        players_df = players_df[players_df["status"] == status_filter]

    if eligibility_filter != "All":
        players_df = players_df[
            players_df["eligibility"].astype(str) == eligibility_filter
        ]

    if search:
        players_df = players_df[
            players_df["first_name"].str.contains(search, case=False, na=False)
            | players_df["last_name"].str.contains(search, case=False, na=False)
            | players_df["team_name"].str.contains(search, case=False, na=False)
        ]

    st.dataframe(players_df, use_container_width=True)
# -------------------- SEASONS PAGE --------------------
elif page == "📅 Seasons":
    st.header("📅 Seasons & Schedule")

    seasons_df = pd.read_sql("SELECT * FROM seasons", engine)

    # make sure dates are datetime
    seasons_df["start_date"] = pd.to_datetime(seasons_df["start_date"], errors="coerce")
    seasons_df["end_date"] = pd.to_datetime(seasons_df["end_date"], errors="coerce")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        year_filter = st.selectbox(
            "Year",
            ["All"] + sorted(seasons_df["year"].dropna().unique().tolist())
        )

    with col2:
        status_filter = st.selectbox(
            "Status",
            ["All"] + sorted(seasons_df["status"].dropna().unique().tolist())
        )

    with col3:
        type_filter = st.selectbox(
            "Type",
            ["All"] + sorted(seasons_df["type_code"].dropna().unique().tolist())
        )

    with col4:
        start_after = st.date_input(
            "Start after",
            value=None
        )

    # -------- apply filters --------

    if year_filter != "All":
        seasons_df = seasons_df[seasons_df["year"] == year_filter]

    if status_filter != "All":
        seasons_df = seasons_df[seasons_df["status"] == status_filter]

    if type_filter != "All":
        seasons_df = seasons_df[seasons_df["type_code"] == type_filter]

    if start_after is not None:
        seasons_df = seasons_df[
            seasons_df["start_date"] >= pd.to_datetime(start_after)
        ]

    st.dataframe(seasons_df, use_container_width=True)

# -------------------- RANKINGS PAGE --------------------
elif page == "🏆 Rankings":
    st.header("🏆 Team Rankings")

    # ---------- READ CSV ----------
    rankings_df = pd.read_csv("rankings.csv")

    if rankings_df.empty:
        st.error("rankings.csv is empty")
        st.stop()

    # ---------- CHECK REQUIRED COLUMN ----------
    if "team_id" not in rankings_df.columns:
        st.error("team_id column not found in rankings.csv")
        st.stop()

    # ---------- SELECTBOX (TEAM IDS) ----------
    team_ids = sorted(rankings_df["team_id"].dropna().unique())

    selected_team_id = st.selectbox(
        "Select Team ID",
        team_ids,
        index=0
    )

    team_df = rankings_df[rankings_df["team_id"] == selected_team_id]

    # ---------- OPTIONAL DISPLAY ----------
    st.subheader("Team Ranking Data")
    st.dataframe(
        team_df.sort_values(by=team_df.columns.tolist()),
        use_container_width=True
    )
# -------------------- VENUES PAGE --------------------
elif page == "🏟️ Venues":
    st.header("🏟️ Venue Directory")

    venues_df = pd.read_sql("SELECT * FROM venues", engine)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        country_filter = st.selectbox(
            "Country",
            ["All"] + sorted(venues_df["country"].dropna().unique().tolist())
        )

    with col2:
        state_filter = st.selectbox(
            "State",
            ["All"] + sorted(venues_df["state"].dropna().unique().tolist())
        )

    with col3:
        surface_filter = st.selectbox(
            "Surface",
            ["All"] + sorted(venues_df["surface"].dropna().unique().tolist())
        )

    with col4:
        roof_filter = st.selectbox(
            "Roof type",
            ["All"] + sorted(venues_df["roof_type"].dropna().unique().tolist())
        )

    col5, col6 = st.columns(2)

    with col5:
        min_capacity = st.number_input(
            "Minimum capacity",
            min_value=0,
            value=0,
            step=1000
        )

    with col6:
        search = st.text_input("Search venue or city")

    # -------- Apply filters --------

    if country_filter != "All":
        venues_df = venues_df[venues_df["country"] == country_filter]

    if state_filter != "All":
        venues_df = venues_df[venues_df["state"] == state_filter]

    if surface_filter != "All":
        venues_df = venues_df[venues_df["surface"] == surface_filter]

    if roof_filter != "All":
        venues_df = venues_df[venues_df["roof_type"] == roof_filter]

    venues_df = venues_df[
        venues_df["capacity"].fillna(0) >= min_capacity
    ]

    if search:
        venues_df = venues_df[
            venues_df["name"].str.contains(search, case=False, na=False) |
            venues_df["city"].str.contains(search, case=False, na=False)
        ]

    st.dataframe(venues_df, use_container_width=True)


# -------------------- COACHES PAGE --------------------
elif page == "🧑‍🏫 Coaches":
    st.header("🧑‍🏫 Coaches")

    coaches_df = pd.read_sql("SELECT * FROM coaches", engine)

    col1, col2, col3 = st.columns(3)

    with col1:
        position_filter = st.selectbox(
            "Position",
            ["All"] + sorted(coaches_df["position"].dropna().unique().tolist())
        )

    with col2:
        team_filter = st.selectbox(
            "Team ID",
            ["All"] + sorted(coaches_df["team_id"].dropna().unique().tolist())
        )

    with col3:
        search = st.text_input("Search coach name")

    # ---------- Apply filters ----------

    if position_filter != "All":
        coaches_df = coaches_df[coaches_df["position"] == position_filter]

    if team_filter != "All":
        coaches_df = coaches_df[coaches_df["team_id"] == team_filter]

    if search:
        coaches_df = coaches_df[
            coaches_df["full_name"].str.contains(search, case=False, na=False) |
            coaches_df["first_name"].str.contains(search, case=False, na=False) |
            coaches_df["last_name"].str.contains(search, case=False, na=False)
        ]

    st.dataframe(coaches_df, use_container_width=True)

elif page == "📌 Team Profile":
    st.header("📌 Team 360° Profile")

    # Select Team
    teams_df = pd.read_sql("SELECT team_id, name FROM teams ORDER BY name", engine)
    team_name = st.selectbox("Select a Team", teams_df["name"])
    team_id = teams_df[teams_df["name"] == team_name]["team_id"].values[0]

    # Team Info
    team_info_query = """
    SELECT 
        t.name,
        t.market,
        c.name AS conference,
        d.division_name AS division
    FROM teams t
    LEFT JOIN conferences c ON t.conference_id = c.conference_id
    LEFT JOIN divisions d ON t.division_id = d.division_id
    WHERE t.team_id = %s
    """
    team_info = pd.read_sql(team_info_query, engine, params=(team_id,))

    st.subheader("🏫 Team Information")
    st.dataframe(team_info, use_container_width=True)

   # Coach Info
    coach_query = """
    SELECT full_name, position
    FROM coaches
    WHERE team_id = %s
    """
    coach_df = pd.read_sql(coach_query, engine, params=(team_id,))

    st.subheader("🧑‍🏫 Coach")
    st.dataframe(coach_df, use_container_width=True)

    # Venue Info
    venue_query = """
    SELECT v.name, v.city, v.state, v.capacity, v.roof_type
    FROM venues v
    JOIN teams t ON v.venue_id = t.venue_id
    WHERE t.team_id = %s
    """
    venue_df = pd.read_sql(venue_query, engine, params=(team_id,))

    st.subheader("🏟️ Venue")
    st.dataframe(venue_df, use_container_width=True)

    # Roster
    roster_query = """
    SELECT first_name, last_name, position, height, weight, eligibility, status
    FROM players
    WHERE team_id = %s
    ORDER BY position
    """
    roster_df = pd.read_sql(roster_query, engine, params=(team_id,))

    st.subheader("👥 Roster")
    st.dataframe(roster_df, use_container_width=True)

    # Player Position Distribution
    st.subheader("📊 Position Distribution")
    position_counts = roster_df["position"].value_counts()
    st.bar_chart(position_counts)
# =================================================
# ANALYSIS PAGE (FIXED ✅)
# =================================================
elif page == "📊 Analysis":

    st.header("📊 Analysis & Insights")
    st.write("Select a business question to generate insights from the database.")

    questions = [
        "Which teams have maintained Top 5 rankings across multiple seasons?",
        "What are the average ranking points per team by season?",
        "How many first-place votes did each team receive across weeks?",
        "Which players have appeared in multiple seasons for the same team?",
        "What are the most common player positions and their distribution across teams?"
    ]

    selected_question = st.selectbox(
        "Select an analysis question",
        questions
    )

    st.divider()

    # ---------- QUESTION 1 ----------
    if selected_question == questions[0]:

        st.subheader("Teams in Top 5 rankings")

        rankings_df = pd.read_csv("rankings.csv")
        top5_df = rankings_df[rankings_df["rank"] <= 5]

        result = (
            top5_df
            .groupby(["team_id", "team_name"])["season"]
            .nunique()
            .reset_index(name="seasons_in_top5")
            .sort_values("seasons_in_top5", ascending=False)
        )

        st.dataframe(result, use_container_width=True)

    # ---------- QUESTION 2 ----------
    elif selected_question == questions[1]:

        st.subheader("Average ranking points per team by season")

        rankings_df = pd.read_csv("rankings.csv")

        result = (
            rankings_df
            .groupby(["team_id", "team_name", "season"])["points"]
            .mean()
            .reset_index(name="avg_points")
            .sort_values(["team_name", "season"])
        )

        st.dataframe(result, use_container_width=True)

    # ---------- QUESTION 3 ----------
    elif selected_question == questions[2]:

        st.subheader("First-place votes by team")

        rankings_df = pd.read_csv("rankings.csv")

        result = (
            rankings_df
            .groupby(["team_id", "team_name"])["fp_votes"]
            .sum()
            .reset_index(name="total_fp_votes")
            .sort_values("total_fp_votes", ascending=False)
        )

        st.dataframe(result, use_container_width=True)

    # ---------- QUESTION 4 ----------
    elif selected_question == questions[3]:

        st.subheader("Teams appearing across multiple seasons")

        rankings_df = pd.read_csv("rankings.csv")

        result = (
            rankings_df
            .groupby(["team_id", "team_name"])["season"]
            .nunique()
            .reset_index(name="num_seasons")
            .sort_values("num_seasons", ascending=False)
        )

        st.dataframe(result, use_container_width=True)

    # ---------- QUESTION 5 ----------
    elif selected_question == questions[4]:

        st.subheader("Player position distribution across teams")

        query = """
        SELECT
            t.name AS team_name,
            p.position,
            COUNT(*) AS player_count
        FROM players p
        JOIN teams t ON p.team_id = t.team_id
        WHERE p.position IS NOT NULL
        GROUP BY t.name, p.position
        ORDER BY t.name, player_count DESC
        """

        df = pd.read_sql(query, engine)
        st.dataframe(df, use_container_width=True)
