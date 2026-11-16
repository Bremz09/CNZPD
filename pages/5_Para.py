#!/usr/bin/env python
# coding: utf-8

import pickle
import re
from datetime import time

import pandas as pd
import streamlit as st
import streamlit_authenticator as stauth
from openpyxl import load_workbook

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


@st.cache_data
def load_paralympics_sheets() -> dict[str, pd.DataFrame]:
    workbook_path = "pages/Para data/Para Guidelines with factoring post 25 worlds_v2.xlsx"
    return {
        "Para Guidelines": pd.read_excel(
            io=workbook_path,
            engine="openpyxl",
            sheet_name="Para Guidelines",
        ),
        "Track Data": pd.read_excel(
            io=workbook_path,
            engine="openpyxl",
            sheet_name="Track Data",
        ),
        "Road Data": pd.read_excel(
            io=workbook_path,
            engine="openpyxl",
            sheet_name="Road Data",
        ),
    }


@st.cache_data
def load_paralympics_factor_groups() -> tuple[dict[int, int], dict[int, tuple[int, int]]]:
    workbook_path = "pages/Para data/Para Guidelines with factoring post 25 worlds_v2.xlsx"
    workbook = load_workbook(workbook_path, data_only=False, read_only=True)
    track_groups = {}
    for row_number in range(2, workbook["Track Data"].max_row + 1):
        formula = workbook["Track Data"].cell(row_number, 8).value
        if isinstance(formula, str):
            match = re.fullmatch(r"=G\$?(\d+)/F\$?\d+", formula)
            if match:
                track_groups[row_number] = int(match.group(1))

    road_groups = {}
    for row_number in range(2, workbook["Road Data"].max_row + 1):
        formula = workbook["Road Data"].cell(row_number, 8).value
        if isinstance(formula, str):
            match = re.fullmatch(r"=MAX\(\$G\$(\d+):\$G\$(\d+)\)\*F\d+", formula)
            if match:
                road_groups[row_number] = (int(match.group(1)), int(match.group(2)))
    workbook.close()
    return track_groups, road_groups


def build_paralympics_guideline_lookup(
    track_results: pd.DataFrame,
    road_results: pd.DataFrame,
    selected_years: list[int],
) -> tuple[
    dict[tuple[str, str, str], object],
    dict[tuple[str, str, str], float],
    dict[tuple[str, str, str], float],
]:
    guideline_lookup = {}
    track_participants_lookup = {}
    road_participants_lookup = {}
    for results, metric_column, precision, is_track in (
        (track_results, "Time_seconds", 3, True),
        (road_results, "Speed", 2, False),
    ):
        rank_three = results[
            results["Year"].isin(selected_years) & results["Rank"].eq(3)
        ]
        averages = rank_three.groupby(["Sex", "Class", "Event"])[metric_column].mean()
        for key, value in averages.items():
            lookup_key = tuple(str(part) for part in key)
            if pd.notna(value):
                guideline_lookup[lookup_key] = round(float(value), precision)
            group = rank_three[
                (rank_three["Sex"] == key[0])
                & (rank_three["Class"] == key[1])
                & (rank_three["Event"] == key[2])
            ]
            participants = average_participants_with_missing_years(
                group,
                selected_years,
            )
            if pd.notna(participants):
                participants_lookup = (
                    track_participants_lookup
                    if is_track
                    else road_participants_lookup
                )
                participants_lookup[lookup_key] = round(participants, 2)

    road_results_in_years = road_results[road_results["Year"].isin(selected_years)]
    for key, group in road_results_in_years.groupby(["Sex", "Class", "Event"]):
        lookup_key = tuple(str(part) for part in key)
        if lookup_key in road_participants_lookup:
            continue
        participants = average_participants_with_missing_years(group, selected_years)
        if pd.notna(participants):
            road_participants_lookup[lookup_key] = round(participants, 2)

    return guideline_lookup, track_participants_lookup, road_participants_lookup


def apply_track_paralympics_factors(
    track_df: pd.DataFrame,
    guideline_lookup: dict[tuple[str, str, str], object],
    participants_lookup: dict[tuple[str, str, str], float],
    factor_groups: dict[int, int],
) -> pd.DataFrame:
    result = track_df.copy()
    guideline_seconds = {}
    factors = {}
    group_keys = {}
    group_best_times = {}

    for index, row in result.iterrows():
        key = (str(row["Sex"]), str(row["Class"]), str(row["Event"]))
        seconds = parse_time_to_seconds(guideline_lookup.get(key))
        if seconds is not None and pd.notna(seconds):
            guideline_seconds[index] = float(seconds)

        factor = pd.to_numeric(row["Factor"], errors="coerce")
        factors[index] = factor
        if pd.notna(factor):
            row_number = int(index) + 2
            group_id = factor_groups.get(row_number)
            if group_id is None:
                raise ValueError(f"Missing track factoring group for workbook row {row_number}.")
            group_key = (str(row["Sex"]), str(row["Event"]), group_id)
            group_keys[index] = group_key
            if index in guideline_seconds:
                factored_time = guideline_seconds[index] * float(factor)
                group_best_times[group_key] = min(
                    group_best_times.get(group_key, factored_time),
                    factored_time,
                )

    result["Guideline Time"] = [
        format_track_time(guideline_seconds[index], result.at[index, "Event"])
        if index in guideline_seconds
        else None
        for index in result.index
    ]
    result["Factored"] = [
        format_track_time(
            guideline_seconds[index] * float(factors[index]),
            row["Event"],
        )
        if pd.notna(factors[index]) and index in guideline_seconds
        else None
        for index, row in result.iterrows()
    ]
    result["Factored Guideline"] = [
        format_track_time(
            group_best_times[group_keys[index]] / float(factors[index]),
            row["Event"],
        )
        if pd.notna(factors[index]) and group_keys[index] in group_best_times
        else None
        for index, row in result.iterrows()
    ]
    result["Avg Participants"] = [
        participants_lookup.get(
            (str(row["Sex"]), str(row["Class"]), str(row["Event"]))
        )
        for _, row in result.iterrows()
    ]
    return result


def apply_road_paralympics_factors(
    road_df: pd.DataFrame,
    guideline_lookup: dict[tuple[str, str, str], object],
    participants_lookup: dict[tuple[str, str, str], float],
    factor_groups: dict[int, tuple[int, int]],
) -> pd.DataFrame:
    result = road_df.copy()
    guideline_speeds = {}
    factors = {}
    group_keys = {}
    group_best_speeds = {}

    for index, row in result.iterrows():
        key = (str(row["Sex"]), str(row["Class"]), str(row["Event"]))
        speed = pd.to_numeric(guideline_lookup.get(key), errors="coerce")
        if pd.notna(speed):
            guideline_speeds[index] = float(speed)

        factor = pd.to_numeric(row["Factor"], errors="coerce")
        factors[index] = factor
        if pd.notna(factor):
            row_number = int(index) + 2
            group_range = factor_groups.get(row_number)
            if group_range is None:
                raise ValueError(f"Missing road factoring group for workbook row {row_number}.")
            group_key = (str(row["Sex"]), str(row["Event"]), group_range)
            group_keys[index] = group_key
            if index in guideline_speeds:
                factored_speed = guideline_speeds[index] / float(factor)
                group_best_speeds[group_key] = max(
                    group_best_speeds.get(group_key, factored_speed),
                    factored_speed,
                )

    result["Guideline Speed"] = [guideline_speeds.get(index) for index in result.index]
    result["Participants"] = [
        participants_lookup.get((str(row["Sex"]), str(row["Class"]), str(row["Event"])))
        for _, row in result.iterrows()
    ]
    result["Factored"] = [
        guideline_speeds[index] / float(factors[index])
        if pd.notna(factors[index]) and index in guideline_speeds
        else None
        for index in result.index
    ]
    result["Factored Guidelines"] = [
        (
            group_best_speeds[group_keys[index]] * float(factors[index])
            if group_keys[index] in group_best_speeds
            else None
        )
        if pd.notna(factors[index])
        else guideline_speeds.get(index)
        for index in result.index
    ]
    return result


def build_paralympics_guideline_tables(
    track_df: pd.DataFrame,
    road_df: pd.DataFrame,
) -> tuple[dict[str, pd.DataFrame], dict[str, pd.DataFrame]]:
    track_classes = ["C1", "C2", "C3", "C4", "C5", "B"]
    road_classes = track_classes + [
        "H1", "H2", "H3", "H4", "H5", "T1", "T2"
    ]
    track_tables = {}
    road_tables = {}

    for sex, label in (("M", "Men"), ("W", "Women")):
        track_rows = {
            class_name: {
                "Class": class_name,
                "Kilo": float("nan"),
                "IP": float("nan"),
                "Sprint": float("nan"),
            }
            for class_name in track_classes
        }
        for _, row in track_df[track_df["Sex"] == sex].iterrows():
            event_column = {"Kilo": "Kilo", "4k IP": "IP", "200m": "Sprint"}.get(
                row["Event"]
            )
            if event_column is None or row["Class"] not in track_rows:
                continue
            value = (
                row["Factored Guideline"]
                if pd.notna(row["Factored Guideline"])
                else row["Guideline Time"]
            )
            track_rows[row["Class"]][event_column] = parse_time_to_seconds(value)
        track_tables[label] = pd.DataFrame(track_rows.values())

        road_rows = {
            class_name: {
                "Class": class_name,
                "RR": float("nan"),
                "TT": float("nan"),
            }
            for class_name in road_classes
        }
        for _, row in road_df[road_df["Sex"] == sex].iterrows():
            if row["Event"] not in ("RR", "TT") or row["Class"] not in road_rows:
                continue
            factor = pd.to_numeric(row["Factor"], errors="coerce")
            value = (
                row["Factored Guidelines"]
                if pd.notna(factor)
                else row["Guideline Speed"]
            )
            road_rows[row["Class"]][row["Event"]] = pd.to_numeric(
                value,
                errors="coerce",
            )
        road_tables[label] = pd.DataFrame(road_rows.values())

    return track_tables, road_tables


def format_paralympics_track_guideline(value: float, event: str) -> str:
    if pd.isna(value):
        return ""
    if event == "200m":
        return f"{value:.3f}"
    minutes = int(value // 60)
    remainder = value - minutes * 60
    return f"{minutes:02d}:{remainder:04.1f}"


def style_paralympics_track_guideline_table(table: pd.DataFrame):
    styled = table.style.format(
        {
            "Kilo": lambda value: format_paralympics_track_guideline(value, "Kilo"),
            "IP": lambda value: format_paralympics_track_guideline(value, "4k IP"),
            "Sprint": lambda value: format_paralympics_track_guideline(value, "200m"),
        },
        na_rep="",
    )
    if table["Kilo"].notna().any():
        styled = styled.background_gradient(cmap="RdYlGn_r", subset=["Kilo"])
    return styled


def style_paralympics_road_guideline_table(table: pd.DataFrame):
    styled = table.style.format(
        {"RR": "{:.2f}", "TT": "{:.2f}"},
        na_rep="",
    )
    if table[["RR", "TT"]].notna().any().any():
        styled = styled.background_gradient(cmap="RdYlGn", subset=["RR", "TT"])
    return styled


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

    minute_second_match = re.fullmatch(r"(\d+):(\d{2}(?:\.\d+)?)", text)
    if minute_second_match:
        return int(minute_second_match.group(1)) * 60 + float(
            minute_second_match.group(2)
        )

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

authenticator = stauth.Authenticate(credentials, "CNZPD_v2", "abcdef", cookie_expiry_days=30)
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

    mode_label = st.selectbox("Select View:", ["Standards", "Guidelines", "Paralympics"], index=0)
    if mode_label == "Paralympics":
        track_results = load_track_data()
        road_results = load_road_data()
        track_available_years = sorted(
            int(year) for year in track_results["Year"].dropna().unique()
        )
        road_available_years = sorted(
            int(year) for year in road_results["Year"].dropna().unique()
        )
        year_options = sorted(set(track_available_years) | set(road_available_years))
        default_track_start = track_available_years[max(0, len(track_available_years) - 3)]
        default_road_start = road_available_years[max(0, len(road_available_years) - 3)]
        selected_year_range = st.select_slider(
            "Select year range:",
            options=year_options,
            value=(
                min(default_track_start, default_road_start),
                max(track_available_years[-1], road_available_years[-1]),
            ),
        )
        selected_years = [
            year
            for year in year_options
            if selected_year_range[0] <= year <= selected_year_range[1]
        ]
        track_years_used = [
            year for year in track_available_years if year in selected_years
        ]
        road_years_used = [
            year for year in road_available_years if year in selected_years
        ]
        track_years_text = ", ".join(map(str, track_years_used)) or "none"
        road_years_text = ", ".join(map(str, road_years_used)) or "none"
        st.caption(
            f"Years used — Track: {track_years_text}; Road: {road_years_text}. "
            "Guidelines use average rank 3 results; factors adjust track times "
            "and road speeds within the workbook's defined groups."
        )
        paralympics_sheets = load_paralympics_sheets()
        track_factor_groups, road_factor_groups = load_paralympics_factor_groups()
        (
            guideline_lookup,
            track_participants_lookup,
            road_participants_lookup,
        ) = build_paralympics_guideline_lookup(
            track_results,
            road_results,
            selected_years,
        )
        track_data = paralympics_sheets["Track Data"]
        track_events = (
            track_data["Class"].eq("B")
            & track_data["Event"].isin(["200m", "4k IP"])
        ) | (
            track_data["Class"].isin(["C1", "C2", "C3", "C4", "C5"])
            & track_data["Event"].eq("Kilo")
        )
        paralympics_sheets["Track Data"] = apply_track_paralympics_factors(
            track_data.loc[track_events].copy(),
            guideline_lookup,
            track_participants_lookup,
            track_factor_groups,
        )
        paralympics_sheets["Road Data"] = apply_road_paralympics_factors(
            paralympics_sheets["Road Data"],
            guideline_lookup,
            road_participants_lookup,
            road_factor_groups,
        )
        paralympics_sheets["Track Data"] = paralympics_sheets["Track Data"].reset_index(drop=True)
        paralympics_sheets["Road Data"] = paralympics_sheets["Road Data"].reset_index(drop=True)
        track_guideline_tables, road_guideline_tables = build_paralympics_guideline_tables(
            paralympics_sheets["Track Data"],
            paralympics_sheets["Road Data"],
        )
        tabs = st.tabs(list(paralympics_sheets))
        for tab, (sheet_name, sheet_df) in zip(tabs, paralympics_sheets.items()):
            with tab:
                if sheet_name == "Para Guidelines":
                    st.markdown("#### Track")
                    men_col, women_col = st.columns(2)
                    with men_col:
                        st.caption("Men")
                        st.dataframe(
                            style_paralympics_track_guideline_table(
                                track_guideline_tables["Men"]
                            ),
                            use_container_width=True,
                            hide_index=True,
                        )
                    with women_col:
                        st.caption("Women")
                        st.dataframe(
                            style_paralympics_track_guideline_table(
                                track_guideline_tables["Women"]
                            ),
                            use_container_width=True,
                            hide_index=True,
                        )
                    st.markdown("#### Road")
                    men_col, women_col = st.columns(2)
                    with men_col:
                        st.caption("Men")
                        st.dataframe(
                            style_paralympics_road_guideline_table(
                                road_guideline_tables["Men"]
                            ),
                            use_container_width=True,
                            hide_index=True,
                        )
                    with women_col:
                        st.caption("Women")
                        st.dataframe(
                            style_paralympics_road_guideline_table(
                                road_guideline_tables["Women"]
                            ),
                            use_container_width=True,
                            hide_index=True,
                        )
                else:
                    st.dataframe(sheet_df, use_container_width=True)
        st.stop()

    col1, col2 = st.columns(2)
    with col1:
        source_label = st.selectbox("Select Source:", ["Road", "Track"], index=0)
    use_track = source_label == "Track"
    use_guidelines = mode_label == "Guidelines"

    df = load_track_data() if use_track else load_road_data()
    available_years = sorted(int(year) for year in df["Year"].dropna().unique())

    with col2:
        selected_year_range = st.select_slider(
            "Select year range:",
            options=available_years,
            value=(
                available_years[max(0, len(available_years) - 3)],
                available_years[-1],
            ),
        )

    selected_years = [
        year
        for year in available_years
        if selected_year_range[0] <= year <= selected_year_range[1]
    ]

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
