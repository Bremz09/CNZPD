#!/usr/bin/env python
# coding: utf-8

import pickle
from datetime import time

import pandas as pd
import streamlit as st
import streamlit_authenticator as stauth

st.set_page_config(
    page_title="CNZ Performance Database",
    page_icon=":bike:",
    layout="wide",
)


@st.cache_data
def load_road_data() -> pd.DataFrame:
    df = pd.read_excel(
        io="pages/Para data/Para_road_results.xlsx",
        engine="openpyxl",
        sheet_name="Sheet1",
        skiprows=0,
    )
    df = df[["Year", "Event", "Class", "Sex", "Rank", "Time", "Distance", "Speed", "Participants"]].copy()
    df["Year"] = pd.to_numeric(df["Year"], errors="coerce")
    df["Rank"] = pd.to_numeric(df["Rank"], errors="coerce")
    df["Speed"] = pd.to_numeric(df["Speed"], errors="coerce")
    df["Distance"] = pd.to_numeric(df["Distance"], errors="coerce")
    df["Participants"] = pd.to_numeric(df["Participants"], errors="coerce")
    df = df.dropna(subset=["Year", "Rank", "Speed", "Sex", "Class", "Event"])
    df["Year"] = df["Year"].astype(int)
    df["Rank"] = df["Rank"].astype(int)
    return df


@st.cache_data
def load_track_data() -> pd.DataFrame:
    df = pd.read_excel(
        io="pages/Para data/Para_track_results.xlsx",
        engine="openpyxl",
        sheet_name="Sheet1",
        skiprows=0,
    )
    base_cols = ["Year", "Event", "Class", "Sex", "Rank", "Time", "Participants"]
    df = df[base_cols].copy()
    df["Year"] = pd.to_numeric(df["Year"], errors="coerce")
    df["Rank"] = pd.to_numeric(df["Rank"], errors="coerce")
    df["Participants"] = pd.to_numeric(df["Participants"], errors="coerce")
    df = df.dropna(subset=["Year", "Rank", "Time", "Sex", "Class", "Event"])
    df["Year"] = df["Year"].astype(int)
    df["Rank"] = df["Rank"].astype(int)
    df["Time_seconds"] = df["Time"].apply(parse_time_to_seconds)
    df = df.dropna(subset=["Time_seconds"])
    return df


def parse_time_to_seconds(value) -> float:
    if pd.isna(value):
        return None

    # Track files contain mixed numeric formats:
    # - values >= 1 are already seconds
    # - values < 1 are Excel day fractions
    if isinstance(value, (int, float)):
        numeric_value = float(value)
        if numeric_value < 1:
            return numeric_value * 86400.0
        return numeric_value

    if isinstance(value, pd.Timestamp):
        return (
            value.hour * 3600
            + value.minute * 60
            + value.second
            + value.microsecond / 1_000_000
        )

    if isinstance(value, time):
        return (
            value.hour * 3600
            + value.minute * 60
            + value.second
            + value.microsecond / 1_000_000
        )

    text = str(value).strip()
    if text == "":
        return None

    delta = pd.to_timedelta(text, errors="coerce")
    if pd.isna(delta):
        as_num = pd.to_numeric(text, errors="coerce")
        if pd.notna(as_num):
            numeric_value = float(as_num)
            if numeric_value < 1:
                return numeric_value * 86400.0
            return numeric_value
        return None

    return float(delta.total_seconds())


def format_seconds(seconds: float) -> str:
    if pd.isna(seconds):
        return "-"

    total = float(seconds)
    minutes = int(total // 60)
    remainder = total - minutes * 60
    return f"{minutes:02d}:{remainder:05.2f}"


def format_track_time(seconds: float, event: str) -> str:
    if pd.isna(seconds):
        return "-"

    total = float(seconds)
    event_text = str(event).strip()

    if event_text in ["200m", "500m"]:
        return f"{total:.3f}"

    minutes = int(total // 60)
    remainder = total - minutes * 60
    return f"{minutes}:{remainder:06.3f}"


def format_track_times_for_display(df: pd.DataFrame) -> pd.DataFrame:
    display_df = df.copy()
    if "Time_seconds" in display_df.columns and "Event" in display_df.columns:
        display_df["Time"] = display_df.apply(
            lambda row: format_track_time(row["Time_seconds"], row["Event"]),
            axis=1,
        )
    return display_df


def arrow_safe_for_display(df: pd.DataFrame) -> pd.DataFrame:
    display_df = df.copy()
    for col in display_df.columns:
        if any(token in col for token in ["Speed", "Distance", "Participants", "Time (s)", "Time_seconds"]):
            display_df[col] = pd.to_numeric(display_df[col], errors="coerce")
            display_df[col] = display_df[col].map(lambda x: f"{x:.2f}" if pd.notna(x) else "")
    for col in display_df.columns:
        if display_df[col].dtype == "object":
            display_df[col] = display_df[col].astype(str)
    return display_df


def average_participants_with_missing_years(df_subset: pd.DataFrame, years: list) -> float:
    if len(years) == 0 or "Participants" not in df_subset.columns:
        return float("nan")

    per_year = df_subset.dropna(subset=["Participants"]).groupby("Year")["Participants"].mean()
    years_with_data = [year for year in years if year in per_year.index]

    if len(years_with_data) == 0:
        return float("nan")

    yearly_values = [float(per_year.loc[year]) for year in years_with_data]
    return sum(yearly_values) / len(yearly_values)


def build_overview_table(df: pd.DataFrame, use_track: bool, use_guidelines: bool, selected_years: list) -> pd.DataFrame:
    rows = []
    grouped = df.groupby(["Sex", "Class", "Event"], dropna=True)

    for (sex, class_name, event), group in grouped:
        df_window = group[group["Year"].isin(selected_years)].copy()

        if use_guidelines:
            df_guideline = df_window[df_window["Rank"] == 3].copy()
            avg_participants = average_participants_with_missing_years(df_guideline, selected_years)

            if use_track:
                metric_seconds = df_guideline["Time_seconds"].mean() if len(df_guideline) > 0 else None
                rows.append(
                    {
                        "Sex": sex,
                        "Class": class_name,
                        "Event": event,
                        "Guideline Time": format_track_time(metric_seconds, event) if metric_seconds is not None else "-",
               
                        "Avg Participants": round(avg_participants, 2),
                    }
                )
            else:
                metric_speed = df_guideline["Speed"].mean() if len(df_guideline) > 0 else None
                rows.append(
                    {
                        "Sex": sex,
                        "Class": class_name,
                        "Event": event,
                        "Guideline Speed": round(metric_speed, 2) if metric_speed is not None else None,
                        "Avg Participants": round(avg_participants, 2),
                    }
                )

        else:
            rank_bands = {
                "A": [1, 2, 3],
                "B": [4, 5, 6],
                "C": [7, 8, 9, 10],
            }

            row = {
                "Sex": sex,
                "Class": class_name,
                "Event": event,
            }

            a_avg_participants = None

            for standard, ranks in rank_bands.items():
                df_band = df_window[df_window["Rank"].isin(ranks)].copy()
                avg_participants = average_participants_with_missing_years(df_band, selected_years)

                if use_track:
                    mean_seconds = df_band["Time_seconds"].mean() if len(df_band) > 0 else None
                    row[f"{standard} Standard"] = format_track_time(mean_seconds, event) if mean_seconds is not None else "-"
                else:
                    mean_speed = df_band["Speed"].mean() if len(df_band) > 0 else None
                    row[f"{standard} Standard"] = round(mean_speed, 2) if mean_speed is not None else None

                if standard == "A":
                    a_avg_participants = round(avg_participants, 2)

            row["Avg Participants"] = a_avg_participants

            rows.append(row)

    overview_df = pd.DataFrame(rows)
    if len(overview_df) == 0:
        return overview_df

    return overview_df.sort_values(["Sex", "Class", "Event"]).reset_index(drop=True)


def standard_from_rank(rank: int) -> str:
    if rank in [1, 2, 3]:
        return "A"
    if rank in [4, 5, 6]:
        return "B"
    if rank in [7, 8, 9, 10]:
        return "C"
    return ""


STANDARD_COLORS = {
    "A": "#f8cd56",
    "B": "#a8a7a4",
    "C": "#dba758",
}


def style_rows_by_standard(df: pd.DataFrame, standard_col: str):
    def _style_row(row):
        color = STANDARD_COLORS.get(str(row[standard_col]), "")
        if color == "":
            return ["" for _ in row]
        return [f"background-color: {color}" for _ in row]

    return df.style.apply(_style_row, axis=1)


with open("hashed_pw.pkl", "rb") as file:
    hashed_passwords = pickle.load(file)

usernames = ["CNZ"]
names = ["CNZ"]

credentials = {"usernames": {}}
for uname, name, pwd in zip(usernames, names, hashed_passwords):
    credentials["usernames"].update({uname: {"name": name, "password": pwd}})

authenticator = stauth.Authenticate(credentials, "CNZPD", "abcdef", cookie_expiry_days=30)
try:
    login_result = authenticator.login(location="main", fields={'Form name':'Login', 'Username':'Username', 'Password':'Password', 'Login':'Login'})
except TypeError:
    login_result = authenticator.login("Login", "main")

if isinstance(login_result, tuple) and len(login_result) == 3:
    name, authentication_status, username = login_result
    st.session_state["name"] = name
    st.session_state["authentication_status"] = authentication_status
    st.session_state["username"] = username
else:
    name = st.session_state.get("name")
    authentication_status = st.session_state.get("authentication_status")
    username = st.session_state.get("username")

if authentication_status is False:
    st.error("Username/password is incorrect")

if authentication_status is None:
    st.warning("Please enter your username and password")

if authentication_status:
    st.title("Para Standards and Guidelines")

    col1, col2, col3 = st.columns(3)
    with col1:
        source_label = st.selectbox("Select Source:", ["Road", "Track"], index=0)
    with col2:
        mode_label = st.selectbox("Select View:", ["Standards", "Guidelines"], index=0)

    use_track = source_label == "Track"
    use_guidelines = mode_label == "Guidelines"

    df = load_track_data() if use_track else load_road_data()
    available_years = sorted(df["Year"].dropna().unique(), reverse=True)

    with col3:
        years_to_use = st.slider(
            "How many past years should be used?",
            min_value=1,
            max_value=len(available_years),
            value=min(3, len(available_years)),
        )

    selected_years = available_years[:years_to_use]

    st.caption(f"Source: {source_label} | View: {mode_label} | Years used: {', '.join([str(y) for y in selected_years])}")
    st.subheader("Overview")
    overview_df = build_overview_table(df, use_track, use_guidelines, selected_years)
    st.dataframe(arrow_safe_for_display(overview_df), use_container_width=True)

    filter_col1, filter_col2, filter_col3 = st.columns(3)

    with filter_col1:
        sex_options = sorted(df["Sex"].dropna().unique())
        selected_sex = st.selectbox("Select Sex:", sex_options)

    df_sex = df[df["Sex"] == selected_sex]

    with filter_col2:
        class_options = sorted(df_sex["Class"].dropna().unique())
        selected_class = st.selectbox("Select Class:", class_options)

    df_class = df_sex[df_sex["Class"] == selected_class]

    with filter_col3:
        event_options = sorted(df_class["Event"].dropna().unique())
        selected_event = st.selectbox("Select Event:", event_options)

    df_filtered = df_class[df_class["Event"] == selected_event].copy()

    df_window = df_filtered[df_filtered["Year"].isin(selected_years)].copy()

    if len(df_window) == 0:
        st.warning("No data found for the selected Sex/Class/Event within the selected year window.")
        st.stop()

    st.write(f"Using years: {', '.join([str(y) for y in selected_years])}")

    if use_guidelines:
        df_guideline = df_window[df_window["Rank"] == 3].copy()

        if len(df_guideline) == 0:
            st.warning("No rank 3 data found in the selected year window.")
            st.stop()

        if use_track:
            guideline_seconds = df_guideline["Time_seconds"].mean()
            guideline_avg_participants = average_participants_with_missing_years(df_guideline, selected_years)
            result = pd.DataFrame(
                {
                    "Metric": ["Guideline (avg rank 3 time)"],
                    "Time": [format_track_time(guideline_seconds, selected_event)],
                    "Time (s)": [round(guideline_seconds, 2)],
                    "Avg Participants": [round(guideline_avg_participants, 2)],
                }
            )
        else:
            guideline_speed = df_guideline["Speed"].mean()
            guideline_avg_participants = average_participants_with_missing_years(df_guideline, selected_years)
            result = pd.DataFrame(
                {
                    "Metric": ["Guideline (avg rank 3 speed)"],
                    "Speed": [round(guideline_speed, 2)],
                    "Avg Participants": [round(guideline_avg_participants, 2)],
                }
            )

        st.subheader("Guideline")
        st.dataframe(arrow_safe_for_display(result), use_container_width=True)

        with st.expander("Show filtered source data used"):
            guideline_source_df = df_guideline.sort_values(["Year", "Rank"], ascending=[False, True])
            if use_track:
                guideline_source_df = format_track_times_for_display(guideline_source_df)
            st.dataframe(arrow_safe_for_display(guideline_source_df), use_container_width=True)

    else:
        rank_bands = {
            "A": [1, 2, 3],
            "B": [4, 5, 6],
            "C": [7, 8, 9, 10],
        }

        rows = []
        for standard, ranks in rank_bands.items():
            df_band = df_window[df_window["Rank"].isin(ranks)].copy()
            avg_participants = average_participants_with_missing_years(df_band, selected_years)

            if use_track:
                mean_seconds = df_band["Time_seconds"].mean()
                rows.append(
                    {
                        "Standard": standard,
                        "Ranks": ", ".join([str(r) for r in ranks]),
                        "Time": format_track_time(mean_seconds, selected_event) if len(df_band) > 0 else "-",
                        "Avg Participants": round(avg_participants, 2),
                    }
                )
            else:
                mean_speed = df_band["Speed"].mean()
                rows.append(
                    {
                        "Standard": standard,
                        "Ranks": ", ".join([str(r) for r in ranks]),
                        "Speed": round(mean_speed, 2) if len(df_band) > 0 else None,
                        "Avg Participants": round(avg_participants, 2),
                    }
                )

        result = pd.DataFrame(rows)
        st.subheader("Standards")
        result_display = arrow_safe_for_display(result)
        st.dataframe(style_rows_by_standard(result_display, "Standard"), use_container_width=True)

        with st.expander("Show filtered source data used"):
            source_df = df_window[df_window["Rank"].between(1, 10)].copy()
            source_df["Standard"] = source_df["Rank"].apply(standard_from_rank)
            source_df = source_df.sort_values(["Year", "Standard", "Rank"], ascending=[False, True, True])
            if use_track:
                source_df = format_track_times_for_display(source_df)
            source_display = arrow_safe_for_display(source_df)
            st.dataframe(style_rows_by_standard(source_display, "Standard"), use_container_width=True)
