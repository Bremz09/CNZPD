#!/usr/bin/env python
# coding: utf-8



import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image
import numpy as np
from io import StringIO
from openpyxl import load_workbook
from plotly.subplots import make_subplots
import xlwings as xw
import datetime
import io
import os.path
import streamlit.components.v1 as components
from pandas.api.types import (
is_categorical_dtype,
is_datetime64_any_dtype,
is_numeric_dtype,
is_object_dtype,
)



st.set_page_config(page_title='CNZ Performance Database',
                  page_icon=":bike:",
                  layout="wide")
# --- USER AUTHENTICATION ---
import streamlit_authenticator as stauth 
import pickle
# load hashed passwords
with open("hashed_pw.pkl","rb") as file:
    hashed_passwords = pickle.load(file)



usernames = ['CNZ']
names = ['CNZ']


credentials = {"usernames":{}}
        
for uname,name,pwd in zip(usernames,names,hashed_passwords):
    user_dict = {"name": name, "password": pwd}
    credentials["usernames"].update({uname: user_dict})
        
authenticator = stauth.Authenticate(credentials, "CNZPD", "abcdef", cookie_expiry_days=30)

authenticator.login(location="main", fields={'Form name':'Login', 'Username':'Username', 'Password':'Password', 'Login':'Login'})
name = st.session_state.get("name")
authentication_status = st.session_state.get("authentication_status")
username = st.session_state.get("username")

if authentication_status == False:
    st.error("Username/password is incorrect")

if authentication_status == None:
    st.warning("Please enter your username and password")

if authentication_status:
    checkboxid=0
    ##This bit is the historical visualiser
    def filter_dataframe(df: pd.DataFrame, widget_key_prefix: str = "default") -> pd.DataFrame:

        modify = st.checkbox("Add filters", key=f"{widget_key_prefix}_add_filters")

        if not modify:
            return df

        df = df.copy()

        # Try to convert datetimes into a standard format (datetime, no timezone)
        for col in df.columns:
            if is_object_dtype(df[col]):
                try:
                    df[col] = pd.to_datetime(df[col])
                except Exception:
                    pass

            if is_datetime64_any_dtype(df[col]):
                df[col] = df[col].dt.tz_localize(None)

        modification_container = st.container()

        with modification_container:
            to_filter_columns = st.multiselect(
                "Filter dataframe on",
                df.columns,
                key=f"{widget_key_prefix}_filter_columns",
            )
            for col_idx, column in enumerate(to_filter_columns):
                left, right = st.columns((1, 20))
                # Treat columns with < 10 unique values as categorical
                if is_categorical_dtype(df[column]) or df[column].nunique() < 10:
                    user_cat_input = right.multiselect(
                        f"Values for {column}",
                        df[column].unique(),
                        default=[],
                        key=f"{widget_key_prefix}_cat_{col_idx}_{column}",
                    )
                    if user_cat_input:
                        if len(user_cat_input) == 1:
                            df = df[df[column].isin(user_cat_input)]
                        else:
                            column_text = df[column].astype(str).str.lower()
                            selected_text = [str(value).strip().lower() for value in user_cat_input if str(value).strip()]
                            if selected_text:
                                match_mask = pd.Series(True, index=df.index)
                                for value_text in selected_text:
                                    match_mask &= column_text.str.contains(value_text, regex=False, na=False)
                                df = df[match_mask]
                elif is_numeric_dtype(df[column]):
                    _min = float(df[column].min())
                    _max = float(df[column].max())
                    step = (_max - _min) / 100
                    user_num_input = right.slider(
                        f"Values for {column}",
                        min_value=_min,
                        max_value=_max,
                        value=(_min, _max),
                        step=step,
                        key=f"{widget_key_prefix}_num_{col_idx}_{column}",
                    )
                    df = df[df[column].between(*user_num_input)]
                elif is_datetime64_any_dtype(df[column]):
                    user_date_input = right.date_input(
                        f"Values for {column}",
                        value=(
                            df[column].min(),
                            df[column].max(),
                        ),
                        key=f"{widget_key_prefix}_date_{col_idx}_{column}",
                    )
                    if len(user_date_input) == 2:
                        user_date_input = tuple(map(pd.to_datetime, user_date_input))
                        start_date, end_date = user_date_input
                        df = df.loc[df[column].between(start_date, end_date)]
                else:
                    user_text_input = right.text_input(
                        f"Substring or regex in {column}",
                        key=f"{widget_key_prefix}_text_{col_idx}_{column}",
                    )
                    if user_text_input:
                        df = df[df[column].astype(str).str.contains(user_text_input)]

        return df


   
    racetype = st.selectbox(
        "Select Race Type:",
        options=["Women's TP", "Men's TP", "Women's Team Sprint","Men's Team Sprint","Mens' Keirin","WTS Starts","Men's IP","Women's IP","Women's Madison","Men's Madison","Bunch"]
        ) 

    def render_madison_analysis(file_path, header_text, view_mode="all"):
        excel_book = pd.ExcelFile(file_path)
        sheet_names = excel_book.sheet_names
        df_master = pd.read_excel(excel_book, sheet_name=sheet_names[0])
        df_event_tags = pd.DataFrame()
        df_changes = pd.DataFrame()
        if len(sheet_names) > 1:
            try:
                df_event_tags = pd.read_excel(excel_book, sheet_name=sheet_names[1])
            except Exception:
                df_event_tags = pd.DataFrame()
        if len(sheet_names) > 2:
            try:
                df_changes = pd.read_excel(excel_book, sheet_name=sheet_names[2])
            except Exception:
                df_changes = pd.DataFrame()

        view_mode = view_mode or "all"
        show_summary_view = view_mode in ("all", "watts_kj")
        show_laps_view = view_mode in ("all", "ten_laps")
        show_changes_view = view_mode == "changes"

        sort_columns = [column for column in ["Save_Date", "Title"] if column in df_master.columns]
        if sort_columns:
            df_master = df_master.sort_values(by=sort_columns, ascending=[False] * len(sort_columns))

        drop_columns = [column for column in ["Save_Date", "Action", "Video"] if column in df_master.columns]

        title_column = "Title" if "Title" in df_master.columns else df_master.columns[0]

        def _find_best_column(columns, candidates):
            normalized_to_actual = {str(col).strip().lower(): col for col in columns}
            for candidate in candidates:
                found = normalized_to_actual.get(str(candidate).strip().lower())
                if found is not None:
                    return found
            return None

        def _pick_best_display_column(df, candidates, fallback):
            existing = []
            for candidate in candidates:
                col = _find_best_column(df.columns, [candidate])
                if col is not None and col not in existing:
                    existing.append(col)

            if fallback in df.columns and fallback not in existing:
                existing.append(fallback)

            if not existing:
                return fallback

            def _score(col):
                values = df[col].dropna().astype(str).str.strip()
                values = values[values != ""]
                if values.empty:
                    return (-1.0, -1.0, -1.0)

                numeric = pd.to_numeric(values, errors="coerce")
                numeric_ratio = float(numeric.notna().mean())
                text_ratio = 1.0 - numeric_ratio
                uniqueness = float(values.nunique() / max(len(values), 1))
                avg_len = float(values.str.len().mean())

                return (text_ratio, uniqueness, avg_len)

            return max(existing, key=_score)

        # Prefer showing session titles in the selector, while using Race ID for joins/matching.
        session_title_candidates = [
            "Session Title",
            "Session title",
            "Session_Title",
            "SessionName",
            "Session Name",
            "Session",
            "Race Title",
            "Title",
        ]
        # Per workflow request, use Race column for the effort selector when available.
        race_display_col = _find_best_column(df_master.columns, ["Race"])
        if race_display_col is not None:
            session_title_col = race_display_col
        else:
            session_title_col = _pick_best_display_column(df_master, session_title_candidates, title_column)

        race_id_candidates = ["Race ID", "RaceID", "Race_Id", "Race #", "Race#", "Race Number", "RaceNumber", "ID"]
        race_id_col = _find_best_column(df_master.columns, race_id_candidates)

        def _get_master_rows_for_selection(selection):
            _selection_text = str(selection).strip()
            _selected_race_id = np.nan
            if session_title_col in df_master.columns:
                _match_title = df_master[session_title_col].astype(str).str.strip() == _selection_text
                if race_id_col and race_id_col in df_master.columns:
                    _ids = pd.to_numeric(df_master.loc[_match_title, race_id_col], errors="coerce").dropna().unique()
                    if len(_ids) > 0:
                        _selected_race_id = _ids[0]
                        _df_temp = df_master.loc[pd.to_numeric(df_master[race_id_col], errors="coerce") == _selected_race_id].copy()
                    else:
                        _df_temp = df_master.loc[_match_title].copy()
                else:
                    _df_temp = df_master.loc[_match_title].copy()
            else:
                _df_temp = df_master.loc[df_master[title_column].astype(str).str.strip() == _selection_text].copy()
            return _df_temp, _selected_race_id

        def _get_related_rows_for_selection(df_source, selection, selected_race_id=np.nan):
            if df_source is None or df_source.empty:
                return pd.DataFrame()

            if pd.notna(selected_race_id):
                for _candidate in race_id_candidates:
                    _found_col = _find_best_column(df_source.columns, [_candidate])
                    if _found_col is None:
                        continue
                    _source_ids = pd.to_numeric(df_source[_found_col], errors="coerce")
                    _id_mask = _source_ids == selected_race_id
                    if _id_mask.any():
                        return df_source.loc[_id_mask].copy()

            _selection_text = str(selection).strip()
            _candidate_columns = []
            for _candidate in [
                session_title_col,
                title_column,
                "Selected Race",
                "Title",
                "Session Title",
                "Session title",
                "Session_Title",
                "SessionName",
                "Session Name",
                "Session",
                "Race",
                "Race Name",
                "Race Title",
                "Event",
                "Label",
                "Name",
            ]:
                if _candidate is not None:
                    _found = _find_best_column(df_source.columns, [_candidate])
                    if _found is not None and _found not in _candidate_columns:
                        _candidate_columns.append(_found)

                _selector_keywords = ["race", "session", "title", "event", "name", "meet"]
                for _col in df_source.columns:
                    _col_l = str(_col).strip().lower()
                    if any(_kw in _col_l for _kw in _selector_keywords) and _col not in _candidate_columns:
                        _candidate_columns.append(_col)

            for _col in _candidate_columns:
                _series = df_source[_col].astype(str).str.strip()
                _exact_mask = _series == _selection_text
                if _exact_mask.any():
                    return df_source.loc[_exact_mask].copy()

            for _col in _candidate_columns:
                _series = df_source[_col].astype(str).str.strip()
                _contains_mask = _series.str.contains(_selection_text, case=False, na=False)
                if _contains_mask.any():
                    return df_source.loc[_contains_mask].copy()

            return pd.DataFrame()

        def _build_selector_options_for_df(df_source, preferred_candidates):
            if df_source is None or df_source.empty:
                return []

            _candidate_cols = []
            for _candidate in preferred_candidates:
                _found = _find_best_column(df_source.columns, [_candidate])
                if _found is not None and _found not in _candidate_cols:
                    _candidate_cols.append(_found)

            _selector_keywords = ["race", "session", "title", "event", "name", "meet"]
            for _col in df_source.columns:
                _col_l = str(_col).strip().lower()
                if any(_kw in _col_l for _kw in _selector_keywords) and _col not in _candidate_cols:
                    _candidate_cols.append(_col)

            if not _candidate_cols:
                _fallback_col = _pick_best_display_column(df_source, preferred_candidates, df_source.columns[0])
                if _fallback_col in df_source.columns:
                    _candidate_cols.append(_fallback_col)

            _options = []
            for _col in _candidate_cols:
                _series = df_source[_col].dropna().astype(str).str.strip()
                _series = _series[_series != ""]
                _series = _series[_series.str.lower() != "nan"]
                _options.extend(_series.tolist())

            return list(dict.fromkeys(_options))

        def _get_changes_race_options(df_source):
            if df_source is None or df_source.empty:
                return []

            _race_col = _find_best_column(df_source.columns, ["Race"])
            if _race_col is None:
                return []

            _race_values = df_source[_race_col].dropna().astype(str).str.strip()
            _race_values = _race_values[_race_values != ""]
            _race_values = _race_values[_race_values.str.lower() != "nan"]
            return list(dict.fromkeys(_race_values.tolist()))

        def _get_event_tags_for_selection(selection):
            if df_event_tags.empty:
                return pd.DataFrame()

            # Prefer matching by numeric Race ID between tabs.
            selection_num = pd.to_numeric(pd.Series([selection]), errors="coerce").iloc[0]
            race_id_candidates = [
                "Race ID",
                "RaceID",
                "Race_Id",
                "Race #",
                "Race#",
                "Race Number",
                "RaceNumber",
                "ID",
            ]
            race_id_candidates = [
                _find_best_column(df_event_tags.columns, [c])
                for c in race_id_candidates
            ]
            race_id_candidates = [c for c in race_id_candidates if c is not None]
            if pd.notna(selection_num) and race_id_candidates:
                for col in race_id_candidates:
                    tag_ids = pd.to_numeric(df_event_tags[col], errors="coerce")
                    id_mask = tag_ids == selection_num
                    if id_mask.any():
                        return df_event_tags.loc[id_mask].dropna(axis=1, how="all")

            candidate_columns = [
                title_column,
                "Title",
                "Race",
                "Event",
                "Race Label",
                "Label",
                "Name",
            ]
            candidate_columns = [c for c in candidate_columns if c in df_event_tags.columns]
            selection_text = str(selection).strip()

            for col in candidate_columns:
                series = df_event_tags[col].astype(str).str.strip()
                exact_mask = series == selection_text
                if exact_mask.any():
                    return df_event_tags.loc[exact_mask].copy()

            for col in candidate_columns:
                series = df_event_tags[col].astype(str).str.strip()
                contains_mask = series.str.contains(selection_text, case=False, na=False)
                if contains_mask.any():
                    return df_event_tags.loc[contains_mask].copy()

            if len(df_event_tags) == 1:
                return df_event_tags.copy()

            return pd.DataFrame()

        def _select_rider_metric_columns(df_event, metric_tokens):
            columns = list(df_event.columns)
            metric_cols = [
                col for col in columns
                if any(token in str(col).lower() for token in metric_tokens)
            ]
            if not metric_cols:
                return None, None

            def _pick(metric_candidates, rider_tokens):
                for candidate in metric_candidates:
                    lowered = str(candidate).lower()
                    if any(token in lowered for token in rider_tokens):
                        return candidate
                return None

            rider_1_tokens = ["rider 1", "rider1", "r1", "athlete 1", "athlete1", "p1"]
            rider_2_tokens = ["rider 2", "rider2", "r2", "athlete 2", "athlete2", "p2"]

            rider_1_col = _pick(metric_cols, rider_1_tokens)
            rider_2_col = _pick(metric_cols, rider_2_tokens)

            if rider_1_col is None and len(metric_cols) >= 1:
                rider_1_col = metric_cols[0]
            if rider_2_col is None and len(metric_cols) >= 2:
                rider_2_col = metric_cols[1] if metric_cols[1] != rider_1_col else None

            return rider_1_col, rider_2_col

        def _coerce_numeric_values(series):
            _text = series.astype(str).str.replace(",", "", regex=False).str.extract(r"(-?\d+(?:\.\d+)?)")[0]
            return pd.to_numeric(_text, errors="coerce")

        def _find_columns_by_aliases(df_obj, aliases):
            _matches = []
            for _col in df_obj.columns:
                _col_l = str(_col).strip().lower()
                if any(str(_alias).strip().lower() in _col_l for _alias in aliases):
                    _matches.append(_col)
            return list(dict.fromkeys(_matches))

        def _find_watt_columns(df_obj):
            _matches = []
            for _col in df_obj.columns:
                _col_l = str(_col).strip().lower()
                if "w" == _col_l:
                    _matches.append(_col)
                    continue
                if "w" in _col_l:
                    _matches.append(_col)
                    continue
            return list(dict.fromkeys(_matches))

        def _build_unweighted_madison_summary(df_event):
            columns = [str(col) for col in df_event.columns]
            lowered_map = {str(col): str(col).lower() for col in df_event.columns}

            def _find_column(pattern_groups):
                for patterns in pattern_groups:
                    for col in columns:
                        col_lower = lowered_map[col]
                        if all(token in col_lower for token in patterns):
                            return col
                return None

            rider_name_col = _find_column([
                ["rider", "name"],
            ])
            type_col = _find_column([
                ["type"],
            ])

            # Extract rider names first to use for dynamic column detection
            # Priority: Detail column > Rider Name > Front column
            if "Detail" in df_event.columns:
                rider_series_temp = df_event["Detail"].astype(str).str.strip()
            elif rider_name_col and rider_name_col in df_event.columns:
                rider_series_temp = df_event[rider_name_col].astype(str).str.strip()
            elif "Front" in df_event.columns:
                rider_series_temp = df_event["Front"].astype(str).str.strip()
            else:
                rider_series_temp = pd.Series(["" for _ in range(len(df_event))], index=df_event.index)

            ordered_names_temp = [name for name in rider_series_temp.tolist() if name and name.lower() != "nan"]
            ordered_unique_names_temp = list(dict.fromkeys(ordered_names_temp))
            
            rider_1_name_temp = ordered_unique_names_temp[0] if len(ordered_unique_names_temp) >= 1 else "Rider 1"
            rider_2_name_temp = ordered_unique_names_temp[1] if len(ordered_unique_names_temp) >= 2 else "Rider 2"

            # Try to find columns using rider names - flexible pattern matching
            power_col_1 = _find_column([
                ["rider 1", "avg", "w"],
                ["rider 1", "av", "w"],
                ["rider1", "avg", "w"],
                ["rider1", "av", "w"],
                ["rider 1", "w"],
                ["rider1", "w"],
                ["rider 1 av"],
                ["rider 1 avg"],
                ["rider1 av"],
                ["rider1 avg"],
            ])
            power_col_2 = _find_column([
                ["rider 2", "avg", "w"],
                ["rider 2", "av", "w"],
                ["rider2", "avg", "w"],
                ["rider2", "av", "w"],
                ["rider 2", "w"],
                ["rider2", "w"],
                ["rider 2 av"],
                ["rider 2 avg"],
                ["rider2 av"],
                ["rider2 avg"],
            ])
            kj_col_1 = _find_column([
                ["rider 1", "kj"],
                ["rider1", "kj"],
                ["rider 1 kj"],
                ["rider1 kj"],
                ["rider 1", "energy"],
                ["rider1", "energy"],
            ])
            kj_col_2 = _find_column([
                ["rider 2", "kj"],
                ["rider2", "kj"],
                ["rider 2 kj"],
                ["rider2 kj"],
                ["rider 2", "energy"],
                ["rider2", "energy"],
            ])

            if power_col_1 is None or power_col_2 is None:
                power_col_1, power_col_2 = _select_rider_metric_columns(df_event, ["power", "watt", "watts", "avg_w", "avgw", " w"])
            if kj_col_1 is None or kj_col_2 is None:
                kj_col_1, kj_col_2 = _select_rider_metric_columns(df_event, ["kj", "energy"])

            if power_col_1 is None and power_col_2 is None and kj_col_1 is None and kj_col_2 is None:
                return None

            # Extract rider series for active/inactive filtering
            # Priority: Detail column > Rider Name > Front column
            if "Detail" in df_event.columns:
                rider_series = df_event["Detail"].astype(str).str.strip()
            elif rider_name_col and rider_name_col in df_event.columns:
                rider_series = df_event[rider_name_col].astype(str).str.strip()
            elif "Front" in df_event.columns:
                rider_series = df_event["Front"].astype(str).str.strip()
            else:
                rider_series = pd.Series(["" for _ in range(len(df_event))], index=df_event.index)

            ordered_names = [name for name in rider_series.tolist() if name and name.lower() != "nan"]
            ordered_unique_names = list(dict.fromkeys(ordered_names))
            if len(ordered_unique_names) >= 2:
                rider_1_name = ordered_unique_names[0]
                rider_2_name = ordered_unique_names[1]
            else:
                rider_1_name = "Rider 1"
                rider_2_name = "Rider 2"

            def _to_numeric(series):
                if series is None:
                    return None
                return pd.to_numeric(series, errors="coerce")

            p1 = _to_numeric(df_event[power_col_1]) if power_col_1 and power_col_1 in df_event.columns else None
            p2 = _to_numeric(df_event[power_col_2]) if power_col_2 and power_col_2 in df_event.columns else None
            k1 = _to_numeric(df_event[kj_col_1]) if kj_col_1 and kj_col_1 in df_event.columns else None
            k2 = _to_numeric(df_event[kj_col_2]) if kj_col_2 and kj_col_2 in df_event.columns else None

            def _mean_or_nan(series, mask=None):
                if series is None:
                    return np.nan
                values = series[mask] if mask is not None else series
                return float(values.mean()) if values.notna().any() else np.nan

            def _sum_or_nan(series, mask=None):
                if series is None:
                    return np.nan
                values = series[mask] if mask is not None else series
                return float(values.sum()) if values.notna().any() else np.nan

            if type_col and type_col in df_event.columns:
                type_series = df_event[type_col].astype(str).str.lower().str.replace("_", " ", regex=False).str.replace("-", " ", regex=False)
            elif "Action" in df_event.columns:
                type_series = df_event["Action"].astype(str).str.lower().str.replace("_", " ", regex=False).str.replace("-", " ", regex=False)
            else:
                type_series = pd.Series(["bunch" for _ in range(len(df_event))], index=df_event.index)

            kind_masks = {
                "Bunch": ~(type_series.str.contains("sprint") | type_series.str.contains("lap") | type_series.str.contains("change")),
                "Sprint": type_series.str.contains("sprint"),
                "Lap Take": type_series.str.contains("lap"),
                "Change": type_series.str.contains("change"),
            }

            def _role_mask(target_rider, role):
                """Create mask for rows where target rider is active or inactive"""
                if target_rider == 1:
                    target_active_name = rider_1_name
                else:
                    target_active_name = rider_2_name
                
                if role == "active":
                    return rider_series == target_active_name
                else:
                    return rider_series != target_active_name
            
            def _get_rider_data(rider_num):
                """Get watts and kj series for a specific rider number"""
                if rider_num == 1:
                    return p1, k1
                else:
                    return p2, k2

            metric_config = [
                (f"Active {rider_1_name} W", 1, "active", "w"),
                (f"Active {rider_1_name} KJ", 1, "active", "kj"),
                (f"Inactive {rider_1_name} W", 1, "inactive", "w"),
                (f"Inactive {rider_1_name} KJ", 1, "inactive", "kj"),
                (f"Active {rider_2_name} W", 2, "active", "w"),
                (f"Active {rider_2_name} KJ", 2, "active", "kj"),
                (f"Inactive {rider_2_name} W", 2, "inactive", "w"),
                (f"Inactive {rider_2_name} KJ", 2, "inactive", "kj"),
            ]

            rows = []
            for row_label, rider_idx, role, metric in metric_config:
                watts_series, kj_series = _get_rider_data(rider_idx)
                source = watts_series if metric == "w" else kj_series
                role_mask = _role_mask(rider_idx, role)
                result_row = {"Row": row_label}

                for kind_name, kind_mask in kind_masks.items():
                    combined_mask = role_mask & kind_mask
                    if metric == "w":
                        result_row[kind_name] = _mean_or_nan(source, combined_mask)
                    else:
                        result_row[kind_name] = _sum_or_nan(source, combined_mask)

                if metric == "w":
                    result_row["Total"] = _mean_or_nan(source, role_mask)
                else:
                    result_row["Total"] = _sum_or_nan(source, role_mask)

                rows.append(result_row)

            summary = pd.DataFrame(rows, columns=["Row", "Bunch", "Sprint", "Lap Take", "Change", "Total"])
            for col in ["Bunch", "Sprint", "Lap Take", "Change", "Total"]:
                summary[col] = summary[col].map(lambda x: round(x, 3) if pd.notna(x) else np.nan)

            summary.attrs["rider_map"] = f"Rider 1: {rider_1_name} | Rider 2: {rider_2_name}"
            return summary

        def _split_tag_tokens(cell_value):
            _text = str(cell_value).strip()
            if not _text or _text.lower() == "nan":
                return []
            for _sep in [";", "/", "|", "\n"]:
                _text = _text.replace(_sep, ",")
            return [t.strip() for t in _text.split(",") if t.strip()]

        def _first_tag_token(cell_value):
            _tokens = _split_tag_tokens(cell_value)
            return _tokens[0] if _tokens else ""

        def _build_note_group(value_map):
            _parts = []
            for _label, _value in value_map:
                _first = _first_tag_token(_value)
                if _first:
                    _parts.append(f"{_label}: {_first}")
            return " | ".join(_parts) if _parts else "Unlabeled"

        def _get_change_metric_columns(df_obj):
            _excluded_exact = {
                "id",
                "race id",
                "race #",
                "race number",
                "bib",
                "lap",
                "block",
                "index",
                "rank",
                "position",
                "order",
            }

            def _is_excluded_column_name(col_name):
                _col_l = str(col_name).strip().lower()
                _col_norm = " ".join(_col_l.replace("_", " ").split())

                # Exclude explicit ID/meta columns, but do not exclude rider metrics such as
                # "Rider 1 kJ" where "id" appears inside "rider".
                if _col_norm in _excluded_exact:
                    return True

                _prefixes = ["race id", "race #", "race number", "bib", "lap", "block", "index", "rank", "position", "order"]
                for _prefix in _prefixes:
                    if _col_norm.startswith(f"{_prefix} "):
                        return True

                if _col_norm.startswith("id ") or _col_norm.endswith(" id"):
                    return True

                return False

            _metric_cols = []
            for _col in df_obj.columns:
                if _is_excluded_column_name(_col):
                    continue
                _numeric_values = _coerce_numeric_values(df_obj[_col])
                if _numeric_values.notna().sum() > 0:
                    _metric_cols.append(_col)
            return _metric_cols

        def _get_change_thrower_column(df_obj):
            _candidate_aliases = [
                "Outgoing rider",
                "Outgoing Rider",
                "Outgoing",
                "Rider detail",
                "Rider Detail",
                "Throwing Rider",
                "Throw Rider",
                "Thrower",
                "Rider Throwing",
                "Throw",
                "Rider",
                "Athlete",
                "Front",
                "Detail",
            ]
            for _alias in _candidate_aliases:
                _found = _find_best_column(df_obj.columns, [_alias])
                if _found is None:
                    continue
                _values = df_obj[_found].dropna().astype(str).str.strip()
                _values = _values[_values != ""]
                if _values.nunique() >= 1:
                    return _found
            return None

        def _get_change_rider_pair_columns(df_obj):
            if df_obj is None or df_obj.empty:
                return None, None

            _outgoing_col = _find_best_column(
                df_obj.columns,
                ["Outgoing rider", "Outgoing Rider", "Outgoing", "Throwing Rider", "Thrower"],
            )
            _incoming_col = _find_best_column(
                df_obj.columns,
                ["Incoming rider", "Incoming Rider", "Incoming", "Receiving Rider", "Received Rider"],
            )
            return _outgoing_col, _incoming_col

        def _extract_change_thrower_label(cell_value):
            _text = str(cell_value).strip()
            if not _text or _text.lower() == "nan":
                return ""

            for _arrow in ["--->", "->", "→"]:
                if _arrow in _text:
                    return _text.split(_arrow, 1)[0].strip()

            return _text

        def _split_change_rider_detail(cell_value):
            _text = str(cell_value).strip()
            if not _text or _text.lower() == "nan":
                return "", ""

            for _arrow in ["--->", "->", "→"]:
                if _arrow in _text:
                    _parts = _text.split(_arrow, 1)
                    _left = str(_parts[0]).strip()
                    _right = str(_parts[1]).strip() if len(_parts) > 1 else ""
                    return _left, _right

            return _text, ""

        def _rgb_to_hex(_rgb):
            return "#{:02x}{:02x}{:02x}".format(
                int(max(0, min(255, _rgb[0]))),
                int(max(0, min(255, _rgb[1]))),
                int(max(0, min(255, _rgb[2]))),
            )

        def _hex_to_rgb(_hex):
            _h = str(_hex).strip().lstrip("#")
            if len(_h) != 6:
                return (59, 130, 246)
            try:
                return tuple(int(_h[i:i + 2], 16) for i in (0, 2, 4))
            except Exception:
                return (59, 130, 246)

        def _shade_color(_hex, factor):
            _r, _g, _b = _hex_to_rgb(_hex)
            if factor >= 1.0:
                _r = _r + (255 - _r) * (factor - 1.0)
                _g = _g + (255 - _g) * (factor - 1.0)
                _b = _b + (255 - _b) * (factor - 1.0)
            else:
                _r = _r * factor
                _g = _g * factor
                _b = _b * factor
            return _rgb_to_hex((int(_r), int(_g), int(_b)))

        def _describe_change_metric(metric_name):
            _metric_text = str(metric_name).strip()
            _metric_lower = " ".join(_metric_text.lower().replace("_", " ").split())

            # Treat rider-specific suffixes consistently after header updates.
            for _token in [" - rider", " (rider", " | rider", " / rider"]:
                if _token in _metric_lower:
                    _metric_lower = _metric_lower.split(_token, 1)[0].strip()

            _exact_definitions = {
                "speed @ change (km/h)": "Speed at the exact change timestamp.",
                "avg power over change (w)": "The average power over the change window.",
                "before change speed (km/h)": "The average speed of the active rider before the change over the change window.",
                "after change speed (km/h)": "The average speed of the active rider after the change over the change window.",
                "speed retention (%)": "After change speed / Before change speed * 100.",
                "team speed gain (km/h)": "After change speed - Before change speed.",
                "incoming speed gain (km/h)": "Incoming rider speed after the change - incoming rider speed before the change (how much the incoming rider accelerates).",
                "ke gain (kj)": "How much the change accelerated the incoming rider: 0.5*m*(v_out^2 - v_in^2).",
            }
            if _metric_lower in _exact_definitions:
                return f"{_metric_text}: {_exact_definitions[_metric_lower]}"

            if any(_token in _metric_lower for _token in ["watt", "power", " avg w", "avg_w", "mean w", " watts", " w "]):
                return f"{_metric_text}: power output for each change row, shown in watts."
            if any(_token in _metric_lower for _token in ["kj", "energy"]):
                return f"{_metric_text}: energy used during each change row, shown in kilojoules."
            if any(_token in _metric_lower for _token in ["speed", "velocity"]):
                return f"{_metric_text}: speed recorded for each change row."
            if any(_token in _metric_lower for _token in ["cadence", "rpm"]):
                return f"{_metric_text}: pedalling cadence for each change row."
            if any(_token in _metric_lower for _token in ["time", "duration", "elapsed", "second", " sec", "(s)"]):
                return f"{_metric_text}: time-based measure for each change row."
            if any(_token in _metric_lower for _token in ["distance", "metre", "meter", "lap"]):
                return f"{_metric_text}: distance or lap-based measure for each change row."
            if any(_token in _metric_lower for _token in ["heart rate", "hr", "bpm"]):
                return f"{_metric_text}: heart-rate measure for each change row."
            if any(_token in _metric_lower for _token in ["torque", "force"]):
                return f"{_metric_text}: torque or force-related measure for each change row."
            return f"{_metric_text}: numeric value from the changes tab for each plotted row."

        def _build_change_relationship_stats(df_obj, x_metric, y_metric):
            _stats = {"count": int(len(df_obj))}
            if len(df_obj) < 2:
                return _stats

            _x_values = pd.to_numeric(df_obj[x_metric], errors="coerce")
            _y_values = pd.to_numeric(df_obj[y_metric], errors="coerce")
            _valid_mask = _x_values.notna() & _y_values.notna()
            _x_values = _x_values[_valid_mask]
            _y_values = _y_values[_valid_mask]
            _stats["count"] = int(len(_x_values))

            if len(_x_values) < 2:
                return _stats

            if _x_values.nunique() > 1 and _y_values.nunique() > 1:
                _stats["pearson_r"] = float(_x_values.corr(_y_values, method="pearson"))
                _stats["spearman_r"] = float(_x_values.corr(_y_values, method="spearman"))
                _slope, _intercept = np.polyfit(_x_values.to_numpy(dtype=float), _y_values.to_numpy(dtype=float), 1)
                _stats["slope"] = float(_slope)
                _stats["intercept"] = float(_intercept)
                if pd.notna(_stats["pearson_r"]):
                    _stats["r_squared"] = float(_stats["pearson_r"] ** 2)

            return _stats

        def _describe_relationship_summary(stats_obj, x_metric, y_metric):
            _count = int(stats_obj.get("count", 0))
            _pearson_r = stats_obj.get("pearson_r")
            _slope = stats_obj.get("slope")

            if _count < 3 or _pearson_r is None or pd.isna(_pearson_r) or _slope is None or pd.isna(_slope):
                return f"Not enough variation to reliably describe the relationship between {x_metric} and {y_metric}."

            _abs_r = abs(float(_pearson_r))
            if _abs_r >= 0.7:
                _strength = "strong"
            elif _abs_r >= 0.4:
                _strength = "moderate"
            elif _abs_r >= 0.2:
                _strength = "weak"
            else:
                _strength = "very weak"

            if float(_pearson_r) > 0:
                _direction = "positive"
            elif float(_pearson_r) < 0:
                _direction = "negative"
            else:
                _direction = "no clear"

            if float(_slope) > 0:
                _slope_text = f"On average, {y_metric} increases by about {float(_slope):.3f} for each +1 unit of {x_metric}."
            elif float(_slope) < 0:
                _slope_text = f"On average, {y_metric} decreases by about {abs(float(_slope)):.3f} for each +1 unit of {x_metric}."
            else:
                _slope_text = f"The fitted linear slope is near zero, so changes in {x_metric} do not consistently shift {y_metric}."

            return f"This plot shows a {_strength} {_direction} relationship between {x_metric} and {y_metric}. {_slope_text}"

        def _find_speed_retention_column(df_obj):
            if df_obj is None or df_obj.empty:
                return None

            _exact_candidates = [
                "Speed retention (%)",
                "Speed Retention (%)",
                "Speed Retention %",
                "Speed retention %",
                "Speed Retention",
                "Speed retention",
            ]
            for _candidate in _exact_candidates:
                _found = _find_best_column(df_obj.columns, [_candidate])
                if _found is not None:
                    return _found

            for _col in df_obj.columns:
                _col_l = str(_col).strip().lower()
                if "speed" in _col_l and "retention" in _col_l:
                    return _col

            return None

        def _build_speed_retention_bucket_table(df_obj):
            if df_obj is None or df_obj.empty:
                return None

            _speed_col = _find_speed_retention_column(df_obj)
            _outgoing_col, _incoming_col = _get_change_rider_pair_columns(df_obj)
            _throw_col = _find_best_column(df_obj.columns, ["Rider detail", "Rider Detail"])
            if _throw_col is None and (_outgoing_col is None or _incoming_col is None):
                _throw_col = _get_change_thrower_column(df_obj)
            if _speed_col is None or ((_outgoing_col is None or _incoming_col is None) and _throw_col is None):
                return None

            _work = df_obj.copy()
            _work["_speed_retention_numeric"] = _coerce_numeric_values(_work[_speed_col])

            def _normalize_rider_name(_value):
                _name = str(_value).strip()
                _name = " ".join(_name.split())
                return _name

            def _parse_throw_direction(_raw_detail):
                _text = str(_raw_detail).strip()
                if not _text or _text.lower() == "nan":
                    return "", ""

                # Most common directional formats first.
                for _arrow in ["--->", "->", "→", ">"]:
                    if _arrow in _text:
                        _left, _right = _text.split(_arrow, 1)
                        return _normalize_rider_name(_left), _normalize_rider_name(_right)

                _text_l = _text.lower()
                if " throwing " in _text_l:
                    _idx = _text_l.find(" throwing ")
                    _left = _text[:_idx]
                    _right = _text[_idx + len(" throwing "):]
                    return _normalize_rider_name(_left), _normalize_rider_name(_right)

                if " to " in _text_l:
                    _idx = _text_l.find(" to ")
                    _left = _text[:_idx]
                    _right = _text[_idx + len(" to "):]
                    return _normalize_rider_name(_left), _normalize_rider_name(_right)

                _left, _right = _split_change_rider_detail(_text)
                return _normalize_rider_name(_left), _normalize_rider_name(_right)

            _work = _work.loc[_work["_speed_retention_numeric"].notna()].copy()
            if _work.empty:
                return pd.DataFrame(columns=["Throw direction", "Changes (<100% retention)", "Changes (100%-105%)", "Changes (>105%)"])

            if _outgoing_col is not None and _incoming_col is not None:
                _work["_outgoing_rider"] = _work[_outgoing_col].astype(str).str.strip()
                _work["_incoming_rider"] = _work[_incoming_col].astype(str).str.strip()
                _work.loc[_work["_outgoing_rider"].str.lower() == "nan", "_outgoing_rider"] = ""
                _work.loc[_work["_incoming_rider"].str.lower() == "nan", "_incoming_rider"] = ""
                _work["_outgoing_rider"] = _work["_outgoing_rider"].apply(_normalize_rider_name)
                _work["_incoming_rider"] = _work["_incoming_rider"].apply(_normalize_rider_name)
            else:
                _parsed_pairs = _work[_throw_col].apply(_parse_throw_direction)
                _work["_outgoing_rider"] = _parsed_pairs.apply(lambda x: x[0])
                _work["_incoming_rider"] = _parsed_pairs.apply(lambda x: x[1])

            _valid_pair_mask = (
                _work["_outgoing_rider"].ne("")
                & _work["_incoming_rider"].ne("")
                & (_work["_outgoing_rider"].str.lower() != _work["_incoming_rider"].str.lower())
            )
            _work = _work.loc[_valid_pair_mask].copy()
            if _work.empty:
                return pd.DataFrame(columns=["Throw direction", "Changes (<100% retention)", "Changes (100%-105%)", "Changes (>105%)"])

            _work["_bucket"] = np.where(
                _work["_speed_retention_numeric"] < 100.0,
                "Changes (<100% retention)",
                np.where(
                    _work["_speed_retention_numeric"] <= 105.0,
                    "Changes (100%-105%)",
                    "Changes (>105%)",
                ),
            )

            _summary = (
                _work
                .groupby(["_outgoing_rider", "_incoming_rider", "_bucket"], dropna=False)
                .size()
                .reset_index(name="count")
                .pivot_table(
                    index=["_outgoing_rider", "_incoming_rider"],
                    columns="_bucket",
                    values="count",
                    aggfunc="sum",
                    fill_value=0,
                )
                .reset_index()
            )

            for _col in ["Changes (<100% retention)", "Changes (100%-105%)", "Changes (>105%)"]:
                if _col not in _summary.columns:
                    _summary[_col] = 0

            _summary["Throw direction"] = _summary.apply(
                lambda _r: f"{str(_r['_outgoing_rider']).strip()} throwing {str(_r['_incoming_rider']).strip()}",
                axis=1,
            )
            _summary = _summary.sort_values(
                by=["Changes (<100% retention)", "Changes (100%-105%)", "Changes (>105%)", "Throw direction"],
                ascending=[False, False, False, True],
            )
            return _summary[
                ["Throw direction", "Changes (<100% retention)", "Changes (100%-105%)", "Changes (>105%)"]
            ].reset_index(drop=True)

        st.markdown("---")
        st.header(header_text)
        c1, c2 = st.columns(2)
        _header_key = header_text.replace(" ", "_").replace("'", "")

        with c1:
            _master_selector_options = _build_selector_options_for_df(
                df_master,
                [session_title_col, title_column, "Title", "Race", "Race Name", "Session Title", "Event", "Name"],
            )

            if show_changes_view:
                _changes_selector_options = _get_changes_race_options(df_changes)
                if not _changes_selector_options:
                    _changes_selector_options = _build_selector_options_for_df(
                        df_changes,
                        ["Race", "Race Name"],
                    )
                _selector_options = _changes_selector_options
            else:
                _selector_options = _master_selector_options

            selections = st.multiselect(
                "Select race/session(s):",
                options=_selector_options,
                key=f"madison_selection_{_header_key}",
            )

        with c2:
            Videos = "No"
            if show_summary_view:
                show_vids = ["No", "Yes"]
                Videos = st.selectbox("Show Race Videos?", show_vids, key=f"Show_Vids_{title_column}")
            elif show_changes_view and len(sheet_names) > 2:
                st.caption(f"Changes source: {sheet_names[2]}")
            elif show_laps_view:
                st.caption("10 Laps view")

        if show_changes_view:
            if len(sheet_names) <= 2:
                st.warning("No changes tab was found in the Men's Madison workbook.")
            elif df_changes.empty:
                st.warning("The changes tab could not be loaded or is empty.")
            elif len(selections) == 0:
                st.info("Select one or more races/sessions to view the changes data.")
            else:
                _change_frames = []
                _change_frames_by_selection = []
                _changes_race_col = _find_best_column(df_changes.columns, ["Race"]) if not df_changes.empty else None
                for selection in selections:
                    _change_source_rows, _change_race_id = _get_master_rows_for_selection(selection)
                    if _changes_race_col is not None and _changes_race_col in df_changes.columns:
                        _selection_text = str(selection).strip()
                        _race_series = df_changes[_changes_race_col].astype(str).str.strip()
                        _race_mask = _race_series == _selection_text
                        _change_rows = df_changes.loc[_race_mask].copy()
                    else:
                        _change_rows = _get_related_rows_for_selection(df_changes, selection, _change_race_id)
                    if _change_rows.empty:
                        continue
                    if "Selected Race" not in _change_rows.columns:
                        _change_rows = _change_rows.copy()
                        _change_rows.insert(0, "Selected Race", str(selection).strip())
                    _change_frames.append(_change_rows)
                    _change_frames_by_selection.append((str(selection).strip(), _change_rows.copy()))

                if not _change_frames:
                    st.info("No changes rows matched the selected race/session.")
                else:
                    _changes_display = pd.concat(_change_frames, ignore_index=True)
                    st.subheader("Speed Retention by Throw Direction")
                    for _sel_name, _sel_df in _change_frames_by_selection:
                        st.markdown(f"**{_sel_name}**")
                        _bucket_table = _build_speed_retention_bucket_table(_sel_df)
                        if _bucket_table is None:
                            st.info("Could not build the summary for this race/session. Ensure this selection has speed-retention values and outgoing/incoming rider columns (or legacy Rider detail format).")
                        else:
                            st.table(_bucket_table)

                    with st.expander("Detailed changes table and chart controls", expanded=False):
                        st.subheader("Changes Data")
                        st.dataframe(_changes_display, use_container_width=True, hide_index=True)

                        _metric_options = _get_change_metric_columns(_changes_display)
                        if len(_metric_options) < 2:
                            st.warning("The changes tab does not contain at least two numeric metric columns for a scatter plot.")
                        else:
                            _default_y_index = 1 if len(_metric_options) > 1 else 0
                            _cx1, _cx2 = st.columns(2)
                            with _cx1:
                                _x_metric = st.selectbox(
                                    "Scatter X-axis",
                                    options=_metric_options,
                                    index=0,
                                    key=f"changes_x_metric_{_header_key}",
                                )
                                st.caption(_describe_change_metric(_x_metric))
                            with _cx2:
                                _y_metric = st.selectbox(
                                    "Scatter Y-axis",
                                    options=_metric_options,
                                    index=_default_y_index,
                                    key=f"changes_y_metric_{_header_key}",
                                )
                                st.caption(_describe_change_metric(_y_metric))

                            _plot_df = _changes_display.copy()
                            _plot_df[_x_metric] = _coerce_numeric_values(_plot_df[_x_metric])
                            _plot_df[_y_metric] = _coerce_numeric_values(_plot_df[_y_metric])
                            _plot_df = _plot_df.dropna(subset=[_x_metric, _y_metric])

                            if _plot_df.empty:
                                st.info("No changes rows remain after converting the selected axes to numeric values.")
                            else:
                                _scatter_race_col = _find_best_column(
                                    _plot_df.columns,
                                    ["Selected Race", session_title_col, "Session Title", "Race", "Title"]
                                )
                                _scatter_thrower_col = _get_change_thrower_column(_plot_df)
                                _scatter_hover_cols = [
                                    _col for _col in ["Selected Race", session_title_col, "Race", "Title", _scatter_thrower_col, _x_metric, _y_metric]
                                    if _col is not None and _col in _plot_df.columns
                                ]
                                _color_kwargs = {}
                                if _scatter_thrower_col is not None and _scatter_thrower_col in _plot_df.columns:
                                    _plot_df = _plot_df.copy()
                                    _outgoing_col, _incoming_col = _get_change_rider_pair_columns(_plot_df)
                                    if _outgoing_col is not None and _incoming_col is not None:
                                        _plot_df["Throwing Rider"] = _plot_df[_outgoing_col].astype(str).str.strip()
                                        _plot_df["Incoming Rider"] = _plot_df[_incoming_col].astype(str).str.strip()
                                        _plot_df.loc[_plot_df["Throwing Rider"].str.lower() == "nan", "Throwing Rider"] = ""
                                        _plot_df.loc[_plot_df["Incoming Rider"].str.lower() == "nan", "Incoming Rider"] = ""
                                        _plot_df["Outgoing Rider"] = _plot_df["Throwing Rider"]
                                    else:
                                        _plot_df["Throwing Rider"] = _plot_df[_scatter_thrower_col].apply(_extract_change_thrower_label)
                                        _pair_split = _plot_df[_scatter_thrower_col].apply(_split_change_rider_detail)
                                        _plot_df["Outgoing Rider"] = _pair_split.apply(lambda x: x[0])
                                        _plot_df["Incoming Rider"] = _pair_split.apply(lambda x: x[1])
                                    _thrower_values = [
                                        str(_value).strip() for _value in _plot_df["Throwing Rider"].dropna().astype(str).tolist()
                                        if str(_value).strip()
                                    ]
                                    _thrower_values = list(dict.fromkeys(_thrower_values))
                                    if _thrower_values:
                                        _race_color_col = _scatter_race_col if _scatter_race_col is not None and _scatter_race_col in _plot_df.columns else "Selected Race"
                                        if _race_color_col not in _plot_df.columns:
                                            _plot_df[_race_color_col] = "Race"

                                        _plot_df["Thrower (Race)"] = _plot_df.apply(
                                            lambda _r: f"{str(_r.get('Throwing Rider', '')).strip()} | {str(_r.get(_race_color_col, '')).strip()}",
                                            axis=1,
                                        )

                                        _base_palette = [
                                            "#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#17becf",
                                            "#bcbd22", "#8c564b", "#9467bd", "#e377c2", "#7f7f7f",
                                        ]
                                        _race_values = [
                                            str(_r).strip() for _r in _plot_df[_race_color_col].dropna().astype(str).tolist()
                                            if str(_r).strip()
                                        ]
                                        _race_values = list(dict.fromkeys(_race_values))
                                        _race_base_color = {
                                            _race: _base_palette[_idx % len(_base_palette)]
                                            for _idx, _race in enumerate(_race_values)
                                        }

                                        _race_thrower_color_map = {}
                                        for _race in _race_values:
                                            _race_mask = _plot_df[_race_color_col].astype(str).str.strip() == _race
                                            _race_throwers = [
                                                str(_t).strip()
                                                for _t in _plot_df.loc[_race_mask, "Throwing Rider"].dropna().astype(str).tolist()
                                                if str(_t).strip()
                                            ]
                                            _race_throwers = list(dict.fromkeys(_race_throwers))
                                            _race_throwers = sorted(_race_throwers, key=lambda _n: _n.lower())
                                            _base_col = _race_base_color.get(_race, "#1f77b4")

                                            if len(_race_throwers) == 1:
                                                _race_thrower_color_map[f"{_race_throwers[0]} | {_race}"] = _base_col
                                            elif len(_race_throwers) >= 2:
                                                _race_thrower_color_map[f"{_race_throwers[0]} | {_race}"] = _shade_color(_base_col, 0.72)
                                                _race_thrower_color_map[f"{_race_throwers[1]} | {_race}"] = _shade_color(_base_col, 1.28)
                                                for _extra_thrower in _race_throwers[2:]:
                                                    _race_thrower_color_map[f"{_extra_thrower} | {_race}"] = _base_col

                                        _color_kwargs["color"] = "Thrower (Race)"
                                        if _race_thrower_color_map:
                                            _color_kwargs["color_discrete_map"] = _race_thrower_color_map
                                        if "Throwing Rider" not in _scatter_hover_cols:
                                            _scatter_hover_cols.append("Throwing Rider")
                                        if "Incoming Rider" not in _scatter_hover_cols and "Incoming Rider" in _plot_df.columns:
                                            _scatter_hover_cols.append("Incoming Rider")
                                        if _race_color_col not in _scatter_hover_cols and _race_color_col in _plot_df.columns:
                                            _scatter_hover_cols.append(_race_color_col)
                                        st.caption("Each race keeps one base colour, and riders in that race are shown as darker/lighter shades of that race colour.")
                                elif _scatter_race_col is not None and _scatter_race_col in _plot_df.columns:
                                    _color_kwargs["color"] = _scatter_race_col

                                _scatter_fig = px.scatter(
                                    _plot_df,
                                    x=_x_metric,
                                    y=_y_metric,
                                    hover_data=_scatter_hover_cols,
                                    title=f"{_y_metric} vs {_x_metric}",
                                    **_color_kwargs,
                                )
                                st.plotly_chart(_scatter_fig, use_container_width=True)

                                _relationship_stats = _build_change_relationship_stats(_plot_df, _x_metric, _y_metric)
                                st.caption("Relationship summary for the currently filtered rows and selected axes.")
                                _rs1, _rs2, _rs3, _rs4 = st.columns(4)
                                with _rs1:
                                    st.metric("Points", str(_relationship_stats.get("count", 0)))
                                with _rs2:
                                    _pearson_r = _relationship_stats.get("pearson_r")
                                    st.metric("Pearson r", f"{_pearson_r:.3f}" if _pearson_r is not None and pd.notna(_pearson_r) else "N/A")
                                with _rs3:
                                    _r_squared = _relationship_stats.get("r_squared")
                                    st.metric("R²", f"{_r_squared:.3f}" if _r_squared is not None and pd.notna(_r_squared) else "N/A")
                                with _rs4:
                                    _slope = _relationship_stats.get("slope")
                                    st.metric("Slope", f"{_slope:.3f}" if _slope is not None and pd.notna(_slope) else "N/A")

                                _spearman_r = _relationship_stats.get("spearman_r")
                                _intercept = _relationship_stats.get("intercept")
                                if _spearman_r is not None or _intercept is not None:
                                    _extra_parts = []
                                    if _spearman_r is not None and pd.notna(_spearman_r):
                                        _extra_parts.append(f"Spearman rank correlation: {_spearman_r:.3f}")
                                    if _intercept is not None and pd.notna(_intercept):
                                        _extra_parts.append(f"Linear intercept: {_intercept:.3f}")
                                    if _extra_parts:
                                        st.caption(" | ".join(_extra_parts))

                                st.caption(_describe_relationship_summary(_relationship_stats, _x_metric, _y_metric))
            return

        _jump_anchor_suffix = "none"
        if show_laps_view and len(selections) != 0:
            _jump_anchor_suffix = "_".join(
                [str(s).strip().replace(" ", "_").replace("'", "") for s in selections]
            )[:120]
        _jump_anchor_id = f"event-note-trends-{_jump_anchor_suffix}"
        _jump_trend_state_key = f"jump_to_trends_click_{title_column}"
        if _jump_trend_state_key not in st.session_state:
            st.session_state[_jump_trend_state_key] = False

        if show_laps_view and len(selections) != 0:
            if st.button("Jump to Trend Lines", key=f"jump_to_trends_btn_{title_column}"):
                st.session_state[_jump_trend_state_key] = True

        if len(selections) != 0:
            df_combine = pd.DataFrame()
            _selected_efforts_meta = []
            for selection in selections:
                st.markdown("---")
                _selection_text = str(selection).strip()

                if show_summary_view:
                    col_1, col_2 = st.columns(2)

                # Resolve selected race rows by session title, then prefer filtering by Race ID.
                df_temp, _selected_race_id = _get_master_rows_for_selection(selection)

                _selected_efforts_meta.append(
                    {
                        "effort": _selection_text,
                        "race_id": _selected_race_id,
                        "rider_names": "",
                    }
                )

                madison_summary = _build_unweighted_madison_summary(df_temp)
                rider_map_str = madison_summary.attrs.get("rider_map", "") if madison_summary is not None else ""
                if madison_summary is not None:
                    _rider_map = dict(part.split(": ", 1) for part in rider_map_str.split(" | ") if ": " in part)
                    _r1_name = str(_rider_map.get("Rider 1", "")).strip()
                    _r2_name = str(_rider_map.get("Rider 2", "")).strip()
                    _riders_joined = " / ".join([n for n in [_r1_name, _r2_name] if n])
                    _selected_efforts_meta[-1]["rider_names"] = _riders_joined

                if show_laps_view and not show_summary_view:
                    st.subheader(f"{_selection_text}")
                    st.dataframe(
                        df_temp.drop(columns=drop_columns, errors="ignore"),
                        use_container_width=True,
                        hide_index=True,
                    )

                if show_summary_view:
                    with col_1:
                        df_combine = pd.concat([df_combine, df_temp], axis=0)
                        st.subheader(f"{_selection_text}")
                        st.dataframe(
                            df_temp.drop(columns=drop_columns, errors="ignore"),
                            use_container_width=True,
                            hide_index=True,
                        )

                        if {"Distance", "Avg_Speed"}.issubset(df_temp.columns):
                            hover_columns = [column for column in ["Split", "Avg_Speed"] if column in df_temp.columns]
                            fig = px.bar(df_temp, x="Distance", y="Avg_Speed", hover_data=hover_columns)
                            fig.update_layout(
                                title={
                                    "text": str(df_temp[title_column].iloc[0]),
                                    "y": 0.9,
                                    "x": 0.5,
                                    "xanchor": "center",
                                    "yanchor": "top",
                                }
                            )
                            st.plotly_chart(fig, use_container_width=True)

                    with col_2:
                        if madison_summary is not None:
                            st.subheader("Watt and kJ (Unweighted)")
                            st.caption(rider_map_str)
                            st.dataframe(madison_summary, use_container_width=True)

                        if Videos == "Yes" and "Video" in df_temp.columns:
                            if pd.isnull(df_temp["Video"].iloc[0]):
                                st.header("No video available")
                            else:
                                st.header(str(df_temp[title_column].iloc[0]))
                                st.video(f"{df_temp['Video'].iloc[0]}")

                # --- Filtered detail view (full width) ---
                if show_laps_view and madison_summary is not None:
                    st.subheader("Filtered Detail View")

                    _rmap = dict(part.split(": ", 1) for part in rider_map_str.split(" | ") if ": " in part)
                    _r1 = _rmap.get("Rider 1", "Rider 1")
                    _r2 = _rmap.get("Rider 2", "Rider 2")

                    _safe_sel = _selection_text.replace(" ", "_").replace("'", "")
                    _fc1, _fc2, _fc3 = st.columns(3)
                    with _fc1:
                        _rider_filter = st.multiselect(
                            "Filter by Rider:",
                            options=[_r1, _r2],
                            default=[],
                            key=f"rider_filter_{_safe_sel}",
                        )
                    with _fc2:
                        _event_filter = st.multiselect(
                            "Filter by Event:",
                            options=["Bunch", "Sprint", "Lap Take", "Change"],
                            default=[],
                            key=f"event_filter_{_safe_sel}",
                        )
                    with _fc3:
                        _role_filter = st.multiselect(
                            "Filter by Active/Inactive:",
                            options=["Active", "Inactive"],
                            default=[],
                            key=f"role_filter_{_safe_sel}",
                        )

                    _detail_col = "Detail" if "Detail" in df_temp.columns else None
                    _type_col = "Type" if "Type" in df_temp.columns else None
                    _race_id_drop_candidates = ["Race ID", "RaceID", "Race_Id", "Race #", "Race#", "Race Number", "RaceNumber", "ID", "Race"]
                    _race_id_drop_cols = [
                        _find_best_column(df_temp.columns, [_c])
                        for _c in _race_id_drop_candidates
                    ]
                    _race_id_drop_cols = [c for c in _race_id_drop_cols if c is not None]

                    _exclude_cols = drop_columns + _race_id_drop_cols + [c for c in ["Start Time (s)", "End Time (s)", "Elapsed (s)"] if c in df_temp.columns]
                    _df_filtered = df_temp.copy()

                    if _type_col and _event_filter:
                        _type_lower = _df_filtered[_type_col].astype(str).str.lower().str.replace("_", " ", regex=False).str.replace("-", " ", regex=False)
                        _event_masks = []
                        for _ev in _event_filter:
                            if _ev == "Bunch":
                                _event_masks.append(~(_type_lower.str.contains("sprint") | _type_lower.str.contains("lap") | _type_lower.str.contains("change")))
                            elif _ev == "Sprint":
                                _event_masks.append(_type_lower.str.contains("sprint"))
                            elif _ev == "Lap Take":
                                _event_masks.append(_type_lower.str.contains("lap"))
                            elif _ev == "Change":
                                _event_masks.append(_type_lower.str.contains("change"))
                        if _event_masks:
                            import functools, operator
                            _combined_event_mask = functools.reduce(operator.or_, _event_masks)
                            _df_filtered = _df_filtered[_combined_event_mask]

                    # Active/inactive row filtering is only applied when exactly one rider and one role are selected.
                    if _detail_col and len(_rider_filter) == 1 and len(_role_filter) == 1:
                        _chosen_rider = _rider_filter[0]
                        _detail_series = _df_filtered[_detail_col].astype(str).str.strip()
                        if _role_filter[0] == "Active":
                            _df_filtered = _df_filtered[_detail_series == _chosen_rider]
                        elif _role_filter[0] == "Inactive":
                            _df_filtered = _df_filtered[_detail_series != _chosen_rider]

                    # Hide metric columns for the non-selected rider when exactly one rider is chosen.
                    _metric_drop_cols = []

                    def _find_rider_metric_cols(rider_aliases, metric_tokens):
                        _aliases_l = [str(a).strip().lower() for a in rider_aliases if str(a).strip()]
                        _matches = []
                        for _col in _df_filtered.columns:
                            _col_l = str(_col).strip().lower()
                            if (
                                _aliases_l
                                and any(_alias in _col_l for _alias in _aliases_l)
                                and any(_metric in _col_l for _metric in metric_tokens)
                            ):
                                _matches.append(_col)
                        return list(dict.fromkeys(_matches))

                    _r1_aliases = [_r1, "Rider 1", "Rider1"]
                    _r2_aliases = [_r2, "Rider 2", "Rider2"]

                    _watt_tokens = [" w", "w ", " watt", " power", "avg"]
                    _kj_tokens = [" kj", "kj ", " energy"]

                    _r1_w_cols = _find_rider_metric_cols(_r1_aliases, _watt_tokens)
                    _r1_kj_cols = _find_rider_metric_cols(_r1_aliases, _kj_tokens)
                    _r2_w_cols = _find_rider_metric_cols(_r2_aliases, _watt_tokens)
                    _r2_kj_cols = _find_rider_metric_cols(_r2_aliases, _kj_tokens)

                    _r1_metric_cols_all = list(dict.fromkeys(_r1_w_cols + _r1_kj_cols))
                    _r2_metric_cols_all = list(dict.fromkeys(_r2_w_cols + _r2_kj_cols))

                    if len(_rider_filter) == 1:
                        if _rider_filter[0] == _r1:
                            _metric_drop_cols.extend(_r2_metric_cols_all)
                        elif _rider_filter[0] == _r2:
                            _metric_drop_cols.extend(_r1_metric_cols_all)

                    _final_drop_cols = _exclude_cols + _metric_drop_cols
                    _df_display = _df_filtered.drop(columns=_final_drop_cols, errors="ignore").reset_index(drop=True)

                    if _detail_col and len(_role_filter) == 1 and _detail_col in _df_display.columns:
                        _selected_role = _role_filter[0].strip().lower()
                        _detail_series_display = _df_display[_detail_col].astype(str).str.strip()
                        _detail_series_display_l = _detail_series_display.str.lower()
                        _r1_metric_cols_display = [c for c in _r1_metric_cols_all if c in _df_display.columns]
                        _r2_metric_cols_display = [c for c in _r2_metric_cols_all if c in _df_display.columns]
                        _r1_active_mask = _detail_series_display_l == str(_r1).strip().lower()
                        _r2_active_mask = _detail_series_display_l == str(_r2).strip().lower()

                        if _selected_role == "active":
                            for _col in _r1_metric_cols_display:
                                _df_display.loc[~_r1_active_mask, _col] = np.nan
                            for _col in _r2_metric_cols_display:
                                _df_display.loc[~_r2_active_mask, _col] = np.nan
                        elif _selected_role == "inactive":
                            for _col in _r1_metric_cols_display:
                                _df_display.loc[_r1_active_mask, _col] = np.nan
                            for _col in _r2_metric_cols_display:
                                _df_display.loc[_r2_active_mask, _col] = np.nan

                    if session_title_col in df_temp.columns and session_title_col not in _df_display.columns:
                        _session_values = df_temp[session_title_col].dropna().astype(str).str.strip()
                        _session_values = _session_values[_session_values != ""]
                        _session_value = _session_values.iloc[0] if len(_session_values) > 0 else _selection_text
                        _df_display.insert(0, "Session Title", _session_value)

                    # Rename Rider 1/2 headers to actual rider names in the filtered detail table.
                    _rename_map = {}
                    for _col in _df_display.columns:
                        _col_l = str(_col).lower()
                        _new_col = str(_col)
                        if "rider 1" in _col_l:
                            _new_col = _new_col.replace("Rider 1", _r1).replace("rider 1", _r1)
                        if "rider1" in _col_l:
                            _new_col = _new_col.replace("Rider1", _r1).replace("rider1", _r1)
                        if "rider 2" in _col_l:
                            _new_col = _new_col.replace("Rider 2", _r2).replace("rider 2", _r2)
                        if "rider2" in _col_l:
                            _new_col = _new_col.replace("Rider2", _r2).replace("rider2", _r2)
                        if _new_col != _col:
                            _rename_map[_col] = _new_col
                    if _rename_map:
                        _df_display = _df_display.rename(columns=_rename_map)

                    _ordered_metric_cols = [
                        *_r1_w_cols,
                        *_r1_kj_cols,
                        *_r2_w_cols,
                        *_r2_kj_cols,
                    ]
                    _ordered_metric_cols = [c for c in _ordered_metric_cols if c in _df_display.columns]
                    _ordered_metric_cols = list(dict.fromkeys(_ordered_metric_cols))

                    _front_cols = []
                    if "Session Title" in _df_display.columns:
                        _front_cols.append("Session Title")

                    _remaining_cols = [c for c in _df_display.columns if c not in _front_cols and c not in _ordered_metric_cols]
                    _df_display = _df_display.loc[:, _front_cols + _ordered_metric_cols + _remaining_cols]

                    st.dataframe(_df_display, use_container_width=True)

                    # Live summary from currently filtered metrics.
                    _summary_frame = _df_filtered
                    _watt_cols = _find_watt_columns(_summary_frame)
                    if not _watt_cols:
                        _watt_cols = _find_watt_columns(_df_display)
                    _kj_cols = _find_columns_by_aliases(_summary_frame, ["kj", "energy"])
                    if not _kj_cols:
                        _kj_cols = _find_columns_by_aliases(_df_display, ["kj", "energy"])

                    _avg_watts = np.nan
                    _total_kj = np.nan

                    if _watt_cols:
                        _watt_values = _coerce_numeric_values(_summary_frame[_watt_cols].stack())
                        if _watt_values.notna().any():
                            _avg_watts = float(_watt_values.sum() / _watt_values.count())

                    if _kj_cols:
                        _kj_values = _coerce_numeric_values(_summary_frame[_kj_cols].stack())
                        if _kj_values.notna().any():
                            _total_kj = float(_kj_values.sum())

                    st.subheader("Filtered Metrics Summary")
                    _m1, _m2 = st.columns(2)
                    with _m1:
                        st.metric("Average Wattage", f"{_avg_watts:.2f}" if pd.notna(_avg_watts) else "N/A")
                    with _m2:
                        st.metric("Accumulated kJ", f"{_total_kj:.3f}" if pd.notna(_total_kj) else "N/A")

                    _show_tags_state_key = f"show_event_tags_state_{_safe_sel}"
                    if _show_tags_state_key not in st.session_state:
                        st.session_state[_show_tags_state_key] = False

                    _tags_btn_label = "Hide event tags" if st.session_state[_show_tags_state_key] else "Show event tags"
                    if st.button(_tags_btn_label, key=f"show_event_tags_btn_{_safe_sel}"):
                        st.session_state[_show_tags_state_key] = not st.session_state[_show_tags_state_key]
                        if hasattr(st, "rerun"):
                            st.rerun()
                        else:
                            st.experimental_rerun()

                    if st.session_state[_show_tags_state_key]:
                        _tags_lookup_key = _selected_race_id if pd.notna(_selected_race_id) else _selection_text
                        _tags_df = _get_event_tags_for_selection(_tags_lookup_key)
                        if _tags_df.empty:
                            st.info("No event tags found for this selected race.")
                        else:
                            def _find_tag_col(df_tags, aliases):
                                for _alias in aliases:
                                    _found = _find_best_column(df_tags.columns, [_alias])
                                    if _found is not None:
                                        return _found
                                for _col in df_tags.columns:
                                    _col_l = str(_col).strip().lower()
                                    if any(str(_a).strip().lower() in _col_l for _a in aliases):
                                        return _col
                                return None

                            def _find_tag_cols(df_tags, aliases):
                                _matches = []
                                for _col in df_tags.columns:
                                    _col_l = str(_col).strip().lower()
                                    if "w" in _col_l:
                                        _matches.append(_col)
                                        continue
                                    if any(str(_alias).strip().lower() in _col_l for _alias in aliases):
                                        _matches.append(_col)
                                return list(dict.fromkeys(_matches))

                            _tags_drop_cols = []
                            _tags_drop_tokens = [
                                "race id",
                                "raceid",
                                "race #",
                                "race number",
                                "start",
                                "end",
                            ]
                            for _col in _tags_df.columns:
                                _col_l = str(_col).strip().lower()
                                if any(_tok in _col_l for _tok in _tags_drop_tokens):
                                    _tags_drop_cols.append(_col)
                            _tags_df = _tags_df.drop(columns=_tags_drop_cols, errors="ignore")

                            _block_notes_col = _find_tag_col(_tags_df, ["Block Note", "Block Notes", "Note", "Notes", "black"])
                            if _block_notes_col is None:
                                _tags_df["Block Notes"] = ""
                                _block_notes_col = "Block Notes"

                            _race_col = _find_tag_col(_tags_df, ["Race Name", "Race", "Session Title", "Session Title ", "Title"])

                            _requested_tag_columns = []
                            for _aliases in [
                                ["Bunch Shape", "Bunch Shape 2", "Bunch"],
                                ["Kiwi Position", "Kiwi Pos", "Kiwi"],
                                ["Sprint"],
                            ]:
                                _found_col = None
                                for _alias in _aliases:
                                    _found_col = _find_best_column(_tags_df.columns, [_alias])
                                    if _found_col is not None:
                                        break
                                if _found_col is not None and _found_col not in _requested_tag_columns:
                                    _requested_tag_columns.append(_found_col)

                            _priority_tag_columns = [c for c in [_race_col, _block_notes_col] if c is not None]
                            _requested_tag_columns = _priority_tag_columns + [c for c in _requested_tag_columns if c not in _priority_tag_columns]

                            _rider_like_tag_cols = [
                                col for col in _tags_df.columns
                                if "rider" in str(col).strip().lower()
                            ]
                            _tag_display_columns = [
                                col for col in _requested_tag_columns + list(_tags_df.columns)
                                if col not in _rider_like_tag_cols and col != _race_col
                            ]
                            _tag_display_columns = list(dict.fromkeys(_tag_display_columns))

                            _bunch_col = _find_tag_col(_tags_df, ["Bunch Shape", "Bunch", "Shape"])
                            _kiwi_col = _find_tag_col(_tags_df, ["Kiwi Position", "Kiwi Pos", "Position"])
                            _sprint_col = _find_tag_col(_tags_df, ["Sprint"])

                            _priority_display_cols = [
                                c for c in [_block_notes_col, _bunch_col, _kiwi_col, _sprint_col]
                                if c is not None
                            ]
                            _tag_display_columns = _priority_display_cols + [
                                c for c in _tag_display_columns if c not in _priority_display_cols
                            ]

                            _bunch_options = ["Split", "Stretched", "Group", "Lap occurring", "Line"]
                            _kiwi_options = ["Front", "Mid", "Back", "Mixed"]
                            _sprint_options = ["5 Points", "3 Points", "2 Points", "1 Point", "Uncontested", "Contested didn't win", "Lap win", "Early split", "Close", "Led out", "Won from back"]

                            _t1, _t2, _t3 = st.columns(3)
                            with _t1:
                                _bunch_filter = st.multiselect(
                                    "Bunch Shape",
                                    options=_bunch_options,
                                    default=[],
                                    key=f"tags_bunch_shape_{_safe_sel}",
                                )
                            with _t2:
                                _kiwi_filter = st.multiselect(
                                    "Kiwi Position",
                                    options=_kiwi_options,
                                    default=[],
                                    key=f"tags_kiwi_position_{_safe_sel}",
                                )
                            with _t3:
                                _sprint_filter = st.multiselect(
                                    "Sprint",
                                    options=_sprint_options,
                                    default=[],
                                    key=f"tags_sprint_{_safe_sel}",
                                )

                            _tags_filtered = _tags_df.copy()

                            def _row_matches_tag_filter(cell_value, selected_values):
                                if not selected_values:
                                    return True
                                _text = str(cell_value).strip().lower()
                                if not _text or _text == "nan":
                                    return False

                                for _sep in [";", "/", "|", "\n"]:
                                    _text = _text.replace(_sep, ",")
                                _tokens = [t.strip() for t in _text.split(",") if t.strip()]
                                if not _tokens:
                                    _tokens = [_text]

                                _selected = {str(v).strip().lower() for v in selected_values if str(v).strip()}
                                if not _selected:
                                    return True

                                return all(_sel in _tokens for _sel in _selected)

                            if _bunch_col and _bunch_filter:
                                _tags_filtered = _tags_filtered[
                                    _tags_filtered[_bunch_col].apply(lambda v: _row_matches_tag_filter(v, _bunch_filter))
                                ]
                            if _kiwi_col and _kiwi_filter:
                                _tags_filtered = _tags_filtered[
                                    _tags_filtered[_kiwi_col].apply(lambda v: _row_matches_tag_filter(v, _kiwi_filter))
                                ]
                            if _sprint_col and _sprint_filter:
                                _tags_filtered = _tags_filtered[
                                    _tags_filtered[_sprint_col].apply(lambda v: _row_matches_tag_filter(v, _sprint_filter))
                                ]

                            _tag_watt_cols = _find_tag_cols(
                                _tags_filtered,
                                ["Average Wattage", "Avg Watt", "Avg_W", "Average W", "Watts Avg", "Watts", "Watt", "Power", "Avg Power", "Mean Power"],
                            )
                            _tag_kj_cols = [c for c in _tags_filtered.columns if ("kj" in str(c).lower() or "energy" in str(c).lower())]
                            _tag_avg_watts = np.nan
                            _tag_total_kj = np.nan
                            if _tag_watt_cols:
                                _tag_watt_values = _coerce_numeric_values(_tags_filtered[_tag_watt_cols].stack())
                                if _tag_watt_values.notna().any():
                                    _tag_avg_watts = float(_tag_watt_values.sum() / _tag_watt_values.count())
                            if _tag_kj_cols:
                                _tag_kj_values = _coerce_numeric_values(_tags_filtered[_tag_kj_cols].stack())
                                if _tag_kj_values.notna().any():
                                    _tag_total_kj = float(_tag_kj_values.sum())

                            if not _tag_watt_cols:
                                _fallback_avg_col = _find_tag_col(_tags_filtered, ["Average Wattage", "Avg Watt", "Avg_W", "Average W", "Watts Avg", "Watts"])
                                if _fallback_avg_col is not None:
                                    _tag_watt_values = _coerce_numeric_values(_tags_filtered[_fallback_avg_col])
                                    if _tag_watt_values.notna().any():
                                        _tag_avg_watts = float(_tag_watt_values.sum() / _tag_watt_values.count())

                            st.subheader("Event Tags")
                            _tag_display_frame = _tags_filtered.reindex(columns=_tag_display_columns).reset_index(drop=True)
                            _tag_num_cols = _tag_display_frame.select_dtypes(include=[np.number]).columns.tolist()
                            _tag_display_show = _tag_display_frame.copy()
                            if _tag_num_cols:
                                _tag_display_show[_tag_num_cols] = _tag_display_show[_tag_num_cols].round(2)
                            _tag_col_config = {}
                            for _col in _tag_display_show.columns:
                                if _col in _tag_num_cols:
                                    _tag_col_config[_col] = st.column_config.NumberColumn(str(_col), format="%.2f", width="small")
                                else:
                                    _tag_col_config[_col] = st.column_config.TextColumn(str(_col), width="medium")
                            st.dataframe(
                                _tag_display_show,
                                use_container_width=True,
                                hide_index=True,
                                column_config=_tag_col_config,
                            )
                            st.subheader("Filtered Event Tag Summary")
                            _tag_m1, _tag_m2 = st.columns(2)
                            with _tag_m1:
                                st.metric("Average Wattage", f"{_tag_avg_watts:.2f}" if pd.notna(_tag_avg_watts) else "N/A")
                            with _tag_m2:
                                st.metric("Accumulated kJ", f"{_tag_total_kj:.3f}" if pd.notna(_tag_total_kj) else "N/A")

                st.markdown("---")

            if show_summary_view and {"Distance", "Avg_Speed"}.issubset(df_combine.columns):
                fig_tt = px.line(df_combine, x="Distance", y="Avg_Speed", title="Comparison", color=title_column)
                st.plotly_chart(fig_tt, use_container_width=True)

            # --- Event-note trends across selected races ---
            _trend_rows = []
            _progress_rows = []
            for _effort_idx, _effort_meta in enumerate(_selected_efforts_meta):
                _effort_name = _effort_meta.get("effort", "")
                _lookup_key = _effort_meta.get("race_id")
                if pd.isna(_lookup_key):
                    _lookup_key = _effort_name

                _trend_tags_df = _get_event_tags_for_selection(_lookup_key)
                if _trend_tags_df is None or _trend_tags_df.empty:
                    continue

                _trend_bunch_col = _find_best_column(_trend_tags_df.columns, ["Bunch Shape", "Bunch Shape 2", "Bunch"])
                _trend_kiwi_col = _find_best_column(_trend_tags_df.columns, ["Kiwi Position", "Kiwi Pos", "Kiwi"])
                _trend_sprint_col = _find_best_column(_trend_tags_df.columns, ["Sprint"])
                _trend_block_col = _find_best_column(_trend_tags_df.columns, ["Block Note", "Block Notes", "Note", "Notes"])

                _trend_w_cols = _find_watt_columns(_trend_tags_df)
                _trend_kj_cols = _find_columns_by_aliases(_trend_tags_df, ["kj", "energy"])
                if not _trend_w_cols and not _trend_kj_cols:
                    continue

                _w_row_values = pd.Series(np.nan, index=_trend_tags_df.index, dtype="float64")
                _w_row_values_active = pd.Series(np.nan, index=_trend_tags_df.index, dtype="float64")
                _w_row_values_inactive = pd.Series(np.nan, index=_trend_tags_df.index, dtype="float64")
                _kj_row_values = pd.Series(np.nan, index=_trend_tags_df.index, dtype="float64")
                if _trend_w_cols:
                    _w_numeric = _trend_tags_df[_trend_w_cols].apply(_coerce_numeric_values)
                    _w_row_values = _w_numeric.mean(axis=1, skipna=True)

                    _active_w_cols = [c for c in _trend_w_cols if ("active" in str(c).strip().lower() and "inactive" not in str(c).strip().lower())]
                    _inactive_w_cols = [c for c in _trend_w_cols if "inactive" in str(c).strip().lower()]
                    if _active_w_cols:
                        _w_numeric_active = _trend_tags_df[_active_w_cols].apply(_coerce_numeric_values)
                        _w_row_values_active = _w_numeric_active.mean(axis=1, skipna=True)
                    if _inactive_w_cols:
                        _w_numeric_inactive = _trend_tags_df[_inactive_w_cols].apply(_coerce_numeric_values)
                        _w_row_values_inactive = _w_numeric_inactive.mean(axis=1, skipna=True)
                if _trend_kj_cols:
                    _kj_numeric = _trend_tags_df[_trend_kj_cols].apply(_coerce_numeric_values)
                    _kj_row_values = _kj_numeric.sum(axis=1, skipna=True)

                _effort_work = _trend_tags_df.copy().reset_index(drop=True)
                _effort_work["Avg Watts"] = _w_row_values.reset_index(drop=True)
                _effort_work["Avg Watts Active"] = _w_row_values_active.reset_index(drop=True)
                _effort_work["Avg Watts Inactive"] = _w_row_values_inactive.reset_index(drop=True)
                _effort_work["kJ"] = _kj_row_values.reset_index(drop=True)
                _effort_work["Event Index"] = np.arange(1, len(_effort_work) + 1)
                _effort_work["Block Reminder"] = (
                    _effort_work[_trend_block_col].apply(_first_tag_token)
                    if _trend_block_col and _trend_block_col in _effort_work.columns
                    else ""
                )
                _effort_work["Trend Bunch"] = (
                    _effort_work[_trend_bunch_col].apply(_first_tag_token)
                    if _trend_bunch_col and _trend_bunch_col in _effort_work.columns
                    else ""
                )
                _effort_work["Trend Kiwi"] = (
                    _effort_work[_trend_kiwi_col].apply(_first_tag_token)
                    if _trend_kiwi_col and _trend_kiwi_col in _effort_work.columns
                    else ""
                )
                _effort_work["Trend Sprint"] = (
                    _effort_work[_trend_sprint_col].apply(_first_tag_token)
                    if _trend_sprint_col and _trend_sprint_col in _effort_work.columns
                    else ""
                )

                _effort_work["Note Group"] = _effort_work.apply(
                    lambda row: _build_note_group(
                        [
                            ("Bunch", row[_trend_bunch_col] if _trend_bunch_col in _effort_work.columns else ""),
                            ("Kiwi", row[_trend_kiwi_col] if _trend_kiwi_col in _effort_work.columns else ""),
                            ("Sprint", row[_trend_sprint_col] if _trend_sprint_col in _effort_work.columns else ""),
                        ]
                    ),
                    axis=1,
                )

                _valid_progress = _effort_work[["Event Index", "Note Group", "Avg Watts", "Avg Watts Active", "Avg Watts Inactive", "kJ", "Block Reminder", "Trend Bunch", "Trend Kiwi", "Trend Sprint"]].copy()
                _valid_progress["Race"] = _effort_name
                _valid_progress["Race Order"] = _effort_idx
                _progress_rows.append(_valid_progress)

                _agg = (
                    _valid_progress.groupby("Note Group", dropna=False)
                    .agg(
                        Avg_Watts=("Avg Watts", "mean"),
                        Total_kJ=("kJ", "sum"),
                        Events=("Event Index", "count"),
                        Block_Reminders=(
                            "Block Reminder",
                            lambda s: " | ".join(
                                list(dict.fromkeys([
                                    str(v).strip() for v in s.tolist()
                                    if str(v).strip() and str(v).strip().lower() != "nan"
                                ]))[:4]
                            ),
                        ),
                    )
                    .reset_index()
                )
                _agg["Race"] = _effort_name
                _agg["Race Order"] = _effort_idx
                _trend_rows.append(_agg)

            if show_laps_view and _progress_rows:
                st.markdown("---")
                st.markdown(f'<div id="{_jump_anchor_id}"></div>', unsafe_allow_html=True)
                if st.session_state.get(_jump_trend_state_key, False):
                    components.html(
                        f"""
                        <script>
                        setTimeout(() => {{
                            const _jumpTarget = window.parent.document.getElementById('{_jump_anchor_id}');
                            if (_jumpTarget) {{
                                _jumpTarget.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
                            }}
                        }}, 50);
                        </script>
                        """,
                        height=0,
                    )
                    st.session_state[_jump_trend_state_key] = False
                st.subheader("Event-Note Trends")
                _trend_key_safe = header_text.replace(" ", "_").replace("'", "")
                _progress_df = pd.concat(_progress_rows, ignore_index=True)

                def _trend_note_options(series):
                    _vals = [
                        str(n).strip() for n in series.dropna().astype(str).tolist()
                        if str(n).strip() and str(n).strip().lower() != "nan"
                    ]
                    return list(dict.fromkeys(sorted(_vals)))

                _bunch_opts = _trend_note_options(_progress_df["Trend Bunch"])
                _kiwi_opts = _trend_note_options(_progress_df["Trend Kiwi"])
                _sprint_opts = _trend_note_options(_progress_df["Trend Sprint"])

                _f1, _f2, _f3 = st.columns(3)
                with _f1:
                    _trend_bunch_filter = st.multiselect(
                        "Trend Bunch Shape:",
                        options=_bunch_opts,
                        default=[],
                        key=f"trend_bunch_notes_{_trend_key_safe}",
                    )
                with _f2:
                    _trend_kiwi_filter = st.multiselect(
                        "Trend Kiwi Notes:",
                        options=_kiwi_opts,
                        default=[],
                        key=f"trend_kiwi_notes_{_trend_key_safe}",
                    )
                with _f3:
                    _trend_sprint_filter = st.multiselect(
                        "Trend Sprint Notes:",
                        options=_sprint_opts,
                        default=[],
                        key=f"trend_sprint_notes_{_trend_key_safe}",
                    )

                _mt1, _mt2 = st.columns(2)
                with _mt1:
                    _show_avg_watts = st.checkbox(
                        "Avg Watts",
                        value=False,
                        key=f"trend_show_avg_watts_{_trend_key_safe}",
                    )
                with _mt2:
                    _show_total_kj = st.checkbox(
                        "Total kJ",
                        value=False,
                        key=f"trend_show_total_kj_{_trend_key_safe}",
                    )

                _wr1, _wr2 = st.columns(2)
                with _wr1:
                    _show_active_rider_watts = st.checkbox(
                        "Active Rider Watts",
                        value=False,
                        key=f"trend_show_active_watts_{_trend_key_safe}",
                    )
                with _wr2:
                    _show_inactive_rider_watts = st.checkbox(
                        "Inactive Rider Watts",
                        value=False,
                        key=f"trend_show_inactive_watts_{_trend_key_safe}",
                    )

                if _show_active_rider_watts and not _show_inactive_rider_watts:
                    _watts_role_mode = "Active Rider"
                elif _show_inactive_rider_watts and not _show_active_rider_watts:
                    _watts_role_mode = "Inactive Rider"
                else:
                    _watts_role_mode = "Both Riders"

                if not _show_avg_watts and not _show_total_kj:
                    _active_metrics = ["Avg_Watts", "Total_kJ"]
                else:
                    _active_metrics = []
                    if _show_avg_watts:
                        _active_metrics.append("Avg_Watts")
                    if _show_total_kj:
                        _active_metrics.append("Total_kJ")

                _progress_plot_df = _progress_df.copy()

                if _watts_role_mode == "Active Rider":
                    _progress_plot_df["Watts Selected"] = _progress_plot_df["Avg Watts Active"]
                elif _watts_role_mode == "Inactive Rider":
                    _progress_plot_df["Watts Selected"] = _progress_plot_df["Avg Watts Inactive"]
                else:
                    _progress_plot_df["Watts Selected"] = _progress_plot_df["Avg Watts"]

                def _contains_any(text_value, selected_values):
                    if not selected_values:
                        return True
                    _txt = str(text_value).strip().lower()
                    return any(str(_sel).strip().lower() in _txt for _sel in selected_values if str(_sel).strip())

                _progress_plot_df = _progress_plot_df[
                    _progress_plot_df.apply(
                        lambda row: (
                            _contains_any(row.get("Trend Bunch", ""), _trend_bunch_filter)
                            and _contains_any(row.get("Trend Kiwi", ""), _trend_kiwi_filter)
                            and _contains_any(row.get("Trend Sprint", ""), _trend_sprint_filter)
                        ),
                        axis=1,
                    )
                ]

                _trend_plot_df = (
                    _progress_plot_df.groupby(["Race", "Race Order", "Note Group"], dropna=False)
                    .agg(
                        Avg_Watts=("Watts Selected", "mean"),
                        Total_kJ=("kJ", "sum"),
                        Events=("Event Index", "count"),
                        Block_Reminders=(
                            "Block Reminder",
                            lambda s: " | ".join(
                                list(dict.fromkeys([
                                    str(v).strip() for v in s.tolist()
                                    if str(v).strip() and str(v).strip().lower() != "nan"
                                ]))[:4]
                            ),
                        ),
                    )
                    .reset_index()
                )
                _trend_plot_df["Race"] = pd.Categorical(
                    _trend_plot_df["Race"],
                    categories=[m["effort"] for m in _selected_efforts_meta],
                    ordered=True,
                )
                _race_label_by_order = {}
                for _idx, _meta in enumerate(_selected_efforts_meta):
                    _race_name = str(_meta.get("effort", "")).strip()
                    _rider_names = str(_meta.get("rider_names", "")).strip()
                    _race_label_by_order[_idx] = f"{_race_name}<br><sup>{_rider_names}</sup>" if _rider_names else _race_name
                _trend_plot_df["Race Label"] = _trend_plot_df["Race Order"].map(_race_label_by_order)
                _trend_plot_df["Race Label"] = _trend_plot_df["Race Label"].fillna(_trend_plot_df["Race"].astype(str))
                _trend_plot_df["Race Label"] = pd.Categorical(
                    _trend_plot_df["Race Label"],
                    categories=[_race_label_by_order.get(i, str(m.get("effort", "")).strip()) for i, m in enumerate(_selected_efforts_meta)],
                    ordered=True,
                )

                _watts_title_suffix = "(Active)" if _watts_role_mode == "Active Rider" else ("(Inactive)" if _watts_role_mode == "Inactive Rider" else "")

                if not _trend_plot_df.empty:
                    if "Avg_Watts" in _active_metrics:
                        _fig_trend_w = px.line(
                            _trend_plot_df,
                            x="Race Label",
                            y="Avg_Watts",
                            color="Note Group",
                            markers=True,
                            hover_data={"Events": True, "Block_Reminders": True},
                            title=f"Race-to-Race Avg Watts {_watts_title_suffix} by Event Note".strip(),
                        )
                        st.plotly_chart(_fig_trend_w, use_container_width=True)

                    if "Total_kJ" in _active_metrics:
                        _fig_trend_kj = px.line(
                            _trend_plot_df,
                            x="Race Label",
                            y="Total_kJ",
                            color="Note Group",
                            markers=True,
                            hover_data={"Events": True, "Block_Reminders": True},
                            title="Race-to-Race Total kJ by Event Note",
                        )
                        st.plotly_chart(_fig_trend_kj, use_container_width=True)
                else:
                    st.info("No race-to-race trend points for the current note filters.")

                if not _progress_plot_df.empty:
                    st.subheader("Within-Race Event Progression")
                    _progress_sorted = _progress_plot_df.sort_values(["Race Order", "Event Index"]).copy()
                    _progress_sorted["Race Line"] = _progress_sorted.apply(
                        lambda r: f"{str(r.get('Race', '')).strip()} ({int(r.get('Race Order', 0)) + 1})",
                        axis=1,
                    )
                    if "Avg_Watts" in _active_metrics:
                        _fig_prog_w = px.line(
                            _progress_sorted,
                            x="Event Index",
                            y="Watts Selected",
                            color="Race Line",
                            line_group="Race Line",
                            markers=True,
                            hover_data={"Note Group": True, "Block Reminder": True},
                            title=f"Within-Race Watts {_watts_title_suffix} by Event Order".strip(),
                        )
                        _fig_prog_w.update_layout(xaxis_title="Race Blocks")
                        st.plotly_chart(_fig_prog_w, use_container_width=True)

                    if "Total_kJ" in _active_metrics:
                        _fig_prog_kj = px.line(
                            _progress_sorted,
                            x="Event Index",
                            y="kJ",
                            color="Race Line",
                            line_group="Race Line",
                            markers=True,
                            hover_data={"Note Group": True, "Block Reminder": True},
                            title="Within-Race kJ by Event Order",
                        )
                        _fig_prog_kj.update_layout(xaxis_title="Race Blocks")
                        st.plotly_chart(_fig_prog_kj, use_container_width=True)
                else:
                    st.info("No within-race trend points for the current note filters.")
            elif show_laps_view and len(selections) > 0:
                st.info("No event-tag trend data was found for the selected race(s).")
        else:
            if show_changes_view:
                st.info("Select one or more races/sessions to view the changes data.")
            else:
                st.info("Select one or more races to view the Madison analysis.")
    
    
    if racetype == "Bunch":
        @st.cache_data
        def get_data_from_excel():
            df = pd.read_excel(
                io='C:\\Users\\SamB\\OneDrive - SportNZGroup\\Desktop\\2024 Olympics\\Analysis\\W_OM_Moves.xlsx',
                engine ='openpyxl',
                sheet_name='Sheet1',
                skiprows=0,
                usecols='A:K',
                nrows=47
                )
            df = df.replace(',','')
            #df['Date'] = pd.to_datetime(df['Date']).dt.date
            return df
        df_master= get_data_from_excel()
        df=df_master
        
        c1,c2,c3=st.columns(3)
        with c1:
            
            ath_filt = st.multiselect(
    'Filter athletes? Leave blank to see all rides',["Ally Wollaston"]
    )



        with c2:

            selections = st.multiselect(
            "Select past effort(s):",
            options=df["Event"].unique(),#.sort_values(ascending=False)
            ) 

                
            
                
        with c3:
            show_vids = ["No","Yes"]
            Videos = st.selectbox("Show Race Videos?", show_vids, key="Show_Vids")

        # Ensure datetime columns are properly parsed
        df['Start'] = pd.to_datetime(df['Start'])
        df['Finish'] = pd.to_datetime(df['Finish'])
        
        # Create the timeline figure
        fig = px.timeline(df, x_start="Start", x_end="Finish", y="Task", color="Task")

        # Generate ordinal values and labels for the x-axis
        tick_vals = [date.toordinal() for date in pd.date_range(df['Start'].min(), df['Finish'].max(), freq='D')]
        tick_text = [date.strftime('%Y-%m-%d') for date in pd.date_range(df['Start'].min(), df['Finish'].max(), freq='D')]

        # Update layout with serialized x-axis
        fig.update_layout(
            title="Gantt Chart with Serialized X-Axis Dates",
            xaxis=dict(
                tickmode="array",
                tickvals=tick_vals,  # Explicitly use plain integers
                ticktext=tick_text,  # Explicitly use plain strings
                title="Time (Serialized Dates)"
            ),
            yaxis_title="Resource",
            template="plotly_white",
            showlegend=True
        )
        
        
        st.plotly_chart(fig, use_container_width=True)
    
    
    ###################################################### Women's Madison #############################################

    if racetype == "Women's Madison":
        _womens_madison_views = {
            "Watts and kJ": "watts_kj",
            "10 Laps": "ten_laps",
            "Changes": "changes",
        }
        _womens_madison_view_label = st.radio(
            "Women's Madison view",
            options=list(_womens_madison_views.keys()),
            horizontal=True,
            key="womens_madison_view_selector",
        )
        render_madison_analysis(
            'pages/video_analysis/Womens_Madison.xlsx',
            "Women's Madison",
            view_mode=_womens_madison_views[_womens_madison_view_label],
        )

    ###################################################### Men's Madison #############################################

    if racetype == "Men's Madison":
        _mens_madison_views = {
            "Watts and kJ": "watts_kj",
            "10 Laps": "ten_laps",
            "Changes": "changes",
        }
        _mens_madison_view_label = st.radio(
            "Men's Madison view",
            options=list(_mens_madison_views.keys()),
            horizontal=True,
            key="mens_madison_view_selector",
        )
        render_madison_analysis(
            'pages/video_analysis/Mens_Madison.xlsx',
            "Men's Madison",
            view_mode=_mens_madison_views[_mens_madison_view_label],
        )

    ################################################ Women's Team Pursuit ###################################
    
    if racetype == "Women's TP":
        df_master = pd.read_excel(f'pages/video_analysis/TP_Master_Women.xlsx')
        df_master['Sort'] = df_master['Title'].str.replace('Q', 'Z', regex=False)

        df_master = df_master.sort_values(by=["Sort","Distance"], ascending=[False,True])
        
        df_small = df_master.drop(columns=["Save_Date","Action","Video", "Sort"])
        
        c1,c2,c3=st.columns(3)
        with c1:
            
            ath_filt = st.multiselect(
    'Filter athletes? Leave blank to see all rides',["Ally Wollaston","Bryony Botha","Emily Shearman","Micky Drummond","Nicole Shields","Sami Donnelly"]
    )
            st.markdown("[Jump to Full Summary](#full-summary)", unsafe_allow_html=True)

        #st.write(df_small["Title"].unique())
        with c2:
            if len(ath_filt)>0:
                
                options=[]
                for race in df_small["Title"].unique():
                    for name in ath_filt:
                        #st.write(df_small["Front"].loc[df_small["Title"]==race].unique())
                        if name in df_small["Front"].loc[df_small["Title"]==race].unique() and race not in options:
                            #st.write(df_small["Front"].loc[df_small["Title"]==race])
                            options.append(race)
                selections = st.multiselect(
                "Select past effort(s):",
                options=options,#.sort_values(ascending=False)
                ) 
            else:
                selections = st.multiselect(
                "Select past effort(s):",
                options=df_master["Title"].unique())
                
            
                
        with c3:
            show_vids = ["No","Yes"]
            Videos = st.selectbox("Show Race Videos?", show_vids, key="Show_Vids")


        if len(selections) !=0:
            avg_speed_dists=[]
            df_combine = pd.DataFrame()
            for count,event_count in enumerate(selections):
                st.markdown("---")
                col_1,col_2=st.columns(2)
                with col_1:
                    df_temp = df_master.loc[df_master['Title'] == selections[count]]
                    df_combine = pd.concat([df_combine, df_temp], axis=0)
                    df_small = df_temp.drop(columns=["Save_Date","Video","Sort"])
                    df_small=df_small.reset_index(drop="True")
                    r1 = [1]
                    r2 = [2]
                    r3 = [3]
                    r4 = [4]
                    r1WS = [0.971]
                    r2WS = [0.612]
                    r3WS = [0.495]
                    r4WS = [0.459]
                    speed_diff=[df_small["Del_Speed"][0]]

                    no_riders=4
                    drag_feel = [0,0.971,0.612,0.495,0.459]
                    for j in range(1,len(df_small)):
                        speed_diff.append(df_small["Del_Speed"][j]-df_small["Del_Speed"][j-1])
                        if df_small["Action"][j-1] == "Change":
                            r1.append(r1[j-1]-1)
                            r2.append(r2[j-1]-1)
                            r3.append(r3[j-1]-1)
                            r4.append(r4[j-1]-1)
                        elif df_small["Action"][j-1] == "Drop":
                            no_riders = 3
                            drag_feel = [0,0.972,0.617,0.517]
                            r1.append(r1[j-1]-1)
                            r2.append(r2[j-1]-1)
                            r3.append(r3[j-1]-1)
                            r4.append(r4[j-1]-1)
                        else:
                            r1.append(r1[j-1])
                            r2.append(r2[j-1])
                            r3.append(r3[j-1])
                            r4.append(r4[j-1])
                        if r1[j]==0:
                            r1[j]=no_riders
                        if r2[j]==0:
                            r2[j]=no_riders
                        if r3[j]==0:
                            r3[j]=no_riders
                        if r4[j]==0:
                            r4[j]=no_riders
                        r1WS.append(drag_feel[r1[j]])
                        r2WS.append(drag_feel[r2[j]])
                        r3WS.append(drag_feel[r3[j]])
                        r4WS.append(drag_feel[r4[j]])
                    if "Drop" in df_small["Action"].unique():        
                        ind = df_small.index[df_small['Action'] == "Drop"][0]

                        if r1[ind]==1:
                            r1[ind+1:]=[0]*(len(df_small)-ind-1)
                            r1WS[ind+1:]=[0]*(len(df_small)-ind-1)
                        if r2[ind]==1:
                            r2[ind+1:]=[0]*(len(df_small)-ind-1)
                            r2WS[ind+1:]=[0]*(len(df_small)-ind-1)
                        if r3[ind]==1:
                            r3[ind+1:]=[0]*(len(df_small)-ind-1)
                            r3WS[ind+1:]=[0]*(len(df_small)-ind-1)
                        if r4[ind]==1:
                            r4[ind+1:]=[0]*(len(df_small)-ind-1)
                            r4WS[ind+1:]=[0]*(len(df_small)-ind-1)
                    one_turn_1=0
                    two_turn_1=0
                    three_turn_1=0
                    four_turn_1=0
                    one_turn_2=0
                    two_turn_2=0
                    three_turn_2=0
                    four_turn_2=0
                    one_turn_3=0
                    two_turn_3=0
                    three_turn_3=0
                    four_turn_3=0
                    j=0

                    while j<df_small["Time"].count() and r1[j] == 1:
                        one_turn_1+=1
                        j+=1
                    while j<df_small["Time"].count() and r2[j] == 1:
                        two_turn_1+=1
                        j+=1
                    while j<df_small["Time"].count() and r3[j] == 1:
                        three_turn_1+=1
                        j+=1
                    while j<df_small["Time"].count() and r4[j] == 1:
                        four_turn_1+=1
                        j+=1
                    while j<df_small["Time"].count() and r1[j] == 1:
                        one_turn_2+=1
                        j+=1
                    while j<df_small["Time"].count() and r2[j] == 1:
                        two_turn_2+=1
                        j+=1
                    while j<df_small["Time"].count() and r3[j] == 1:
                        three_turn_2+=1
                        j+=1
                    while j <df_small["Time"].count() and r4[j] == 1:
                        four_turn_2+=1
                        j+=1
                    while j <df_small["Time"].count() and r1[j] == 1:
                        one_turn_3+=1
                        j+=1
                    while j <df_small["Time"].count() and r2[j] == 1:
                        two_turn_3+=1
                        j+=1
                    while j<df_small["Time"].count() and r3[j] == 1:
                        three_turn_3+=1
                        j+=1
                    while j <df_small["Time"].count() and r4[j] == 1:
                        four_turn_3+=1
                        j+=1
                    first_turns=[one_turn_1/4,two_turn_1/4,three_turn_1/4,four_turn_1/4]
                    second_turns=[one_turn_2/4,two_turn_2/4,three_turn_2/4,four_turn_2/4]
                    third_turns=[one_turn_3/4,two_turn_3/4,three_turn_3/4,four_turn_3/4]
                    df_small["Rider1"]=r1
                    df_small["Rider2"]=r2
                    df_small["Rider3"]=r3
                    df_small["Rider4"]=r4
                    df_small["Speed_Diff"]=speed_diff
                    df_small["Rider1WS"]=r1WS*(df_small["Del_Speed"]+df_small["Speed_Diff"])
                    df_small["Rider2WS"]=r2WS*(df_small["Del_Speed"]+df_small["Speed_Diff"])
                    df_small["Rider3WS"]=r3WS*(df_small["Del_Speed"]+df_small["Speed_Diff"])
                    df_small["Rider4WS"]=r4WS*(df_small["Del_Speed"]+df_small["Speed_Diff"])


                    df_main = df_small.drop(columns=["Rider1","Rider2","Rider3","Rider4","Action","Speed_Diff","Rider1WS","Rider2WS","Rider3WS","Rider4WS"])
    #                     df_main
                    hl_splits=[]
                    hl_rider =[] 
                    hl_distance=[]
                    hl_del_speed=[]
                    for i in range(2,len(df_main["Split"]),2):
                        hl_splits.append(df_main["Split"][i]+df_main["Split"][i-1])
                        hl_rider.append(df_main["Front"][i])
                        hl_distance.append(df_main["Distance"][i])
                        if df_main["Del_Speed"][i]!=df_main["Avg_Speed"][i]:
                            hl_del_speed.append(df_main["Del_Speed"][i])
                        else:
                            hl_del_speed.append(125*3.6/(df_main["Split"][i]+df_main["Split"][i-1]))
                    df_gm=pd.DataFrame()
                    df_gm["Split"] = hl_splits
                    df_gm["Front"]=hl_rider
                    df_gm["Distance"]=hl_distance
                    df_gm["Avg_Speed"]=125*3.6/df_gm["Split"]
                    df_gm["Del_Speed"]=hl_del_speed
                    lap_splits=[]
                    for i in range(len(df_gm["Split"])):
                        if i % 2==0:
                            lap_splits.append("")
                        else:
                            lap_splits.append(round(df_gm["Split"][i]+df_gm["Split"][i-1],2))
                    df_gm["Lap_Split"]=lap_splits
                    


                with col_2:
                    c1sub,c2sub=st.columns(2)
                    with c1sub:
                        yaxis_min = st.number_input("Y-axis Minimum:", min_value=0.00, max_value=None,value=min(df_temp["Avg_Speed"][1:])-1,key=f"yaxis min{event_count}")
                    with c2sub:
                        yaxis_max = st.number_input("Y-axis Maximum:", min_value=min(df_temp["Avg_Speed"])-1, max_value=None,value=max(df_temp["Avg_Speed"])+1,key=f"yaxis max{event_count}")
                    average = df_small.Split.iloc[4:].mean()
                    fig = px.bar(df_temp, x='Distance', y='Avg_Speed',color=df_temp.Front,hover_data={'Split':':.2f', 'Avg_Speed':':.2f', 'Del_Speed':':.2f'})
                    fig.add_trace(go.Scatter(x=df_temp['Distance'][1:], y=df_temp['Del_Speed'][1:],mode='markers',name="Delivery Speed"))
                    fig.update_layout(
                    title={
                        'text': df_temp.Title.iloc[0],
                        'y':0.9,
                        'x':0.5,
                        'xanchor': 'center',
                        'yanchor': 'top',
                        'font':dict(size=25)})
                    av_speed=3.6*62.5/average
                    
                    
                    av_idx=1
                    below_av = df_small["Del_Speed"][av_idx]
                    above_av=below_av
                    while (below_av <av_speed) or (av_idx<2) :
                        below_av=df_small["Del_Speed"][av_idx]
                        av_idx+=1
                    above_av=df_small["Del_Speed"][av_idx-1]
                    below_av=df_small["Del_Speed"][av_idx-2]
                    
                    
                    below_av_dist = df_small["Distance"][av_idx-2]
                    
                    if below_av==above_av:
                        av_speed_dist = below_av_dist
                    else:
                        av_speed_dist = below_av_dist + 62.5*(av_speed-below_av)/(above_av-below_av)
                    avg_speed_dists.extend([av_speed_dist for i in range(4)])
                    fig.add_hline(y=62.5*3.6/average, line_dash="dash",line_color="yellow",annotation_text="Avg after first lap = " +str(round(average*4,2)))
                    fig.add_vline(x=round(av_speed_dist,2), line_dash="dash",line_color="yellow",annotation_text=f"Avg speed at {round(av_speed_dist,2)}m")
                    yaxis_min = yaxis_min #min(df_temp["Avg_Speed"][1:])-1
                    yaxis_max = yaxis_max #max(df_temp["Avg_Speed"])+1
                    fig.update_layout(yaxis_range=[yaxis_min,yaxis_max])
                    st.header("Quarter lap split speed trace")
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    #Goldmine style Speed Trace
                    st.header("Goldmine style speed trace")
                    
                    fig_gm = px.bar(df_gm, x='Distance', y='Avg_Speed',text="Lap_Split",color=df_gm.Front,hover_data={'Split':':.2f', 'Avg_Speed':':.2f', 'Del_Speed':':.2f'})
                    
                    fig_gm.add_trace(go.Scatter(x=df_gm['Distance'][1:], y=df_gm['Del_Speed'][1:],mode='markers',name="Delivery Speed"))
                    fig_gm.update_layout(
                    title={
                        'text': df_temp.Title.iloc[0],
                        'y':0.9,
                        'x':0.5,
                        'xanchor': 'center',
                        'yanchor': 'top',
                        'font':dict(size=25)})
                    fig_gm.add_hline(y=62.5*3.6/average, line_dash="dash",line_color="yellow",annotation_text="Avg after first lap = " +str(round(average*4,2)))
                    fig_gm.add_vline(x=round(av_speed_dist,2), line_dash="dash",line_color="yellow",annotation_text=f"Avg speed at {round(av_speed_dist,2)}m")
                    fig_gm.update_layout(yaxis_range=[yaxis_min,yaxis_max])
                    fig_gm.update_traces(textfont_size=24, cliponaxis=False)
                    st.plotly_chart(fig_gm, use_container_width=True)
                    

                with col_1:

                    st.header(df_temp["Title"].iloc[0])
                    df_small
                    unq_riders = df_small["Front"].unique().tolist()
                    
                    if len(unq_riders)<4:
                        unq_riders.append("empty")  
                    df_summ=pd.DataFrame(unq_riders)
                    df_summ.columns=["Rider"]
                    df_summ=df_summ.dropna(axis=0)
                    front=[]
                    front.append(len(df_small.loc[df_small['Front'] == df_summ["Rider"][0]])/4)
                    front.append(len(df_small.loc[df_small['Front'] == df_summ["Rider"][1]])/4)
                    front.append(len(df_small.loc[df_small['Front'] == df_summ["Rider"][2]])/4)
                    front.append(len(df_small.loc[df_small['Front'] == df_summ["Rider"][3]])/4)
                    wind_scores = []
                    df_small['Rider1WS'].fillna(0)
                    wind_scores.append(round(sum(df_small['Rider1WS'].fillna(0),1)))
                    wind_scores.append(round(sum(df_small['Rider2WS'].fillna(0),1)))
                    wind_scores.append(round(sum(df_small['Rider3WS'].fillna(0),1)))
                    wind_scores.append(round(sum(df_small['Rider4WS'].fillna(0),1)))
                    df_summ["Front"]=front
                    df_summ["Turn_1"]=first_turns
                    df_summ["Turn_2"]=second_turns
                    df_summ["Turn_3"]=third_turns
                    df_summ["Wind_Score"] = wind_scores
                    # df_summ["Event_Count"]=count
                    
                    # Calculating Splits based off delivery speeds - 900 is a conversion factor
                    avg_splits=[round(900/(df_small[4:].loc[df_small["Front"] ==unq_riders[0]]["Del_Speed"].mean()),2), round(900/df_small[4:].loc[df_small["Front"] ==unq_riders[1]]["Del_Speed"].mean(),2),round(900/df_small[4:].loc[df_small["Front"] ==unq_riders[2]]["Del_Speed"].mean(),2),round(900/df_small[4:len(df_small)-1].loc[df_small["Front"] ==unq_riders[3]]["Del_Speed"].mean(),2)]
                    df_summ["Avg_Del_Split"]=avg_splits
                    
                    st.subheader("Rider Info")
                    
                    speed_var=[df_small[4:len(df_small)-1].loc[df_small["Front"] ==unq_riders[0]]["Del_Speed"].max()-df_small[4:len(df_small)-1].loc[df_small["Front"] ==unq_riders[0]]["Del_Speed"].min(),df_small[4:len(df_small)-1].loc[df_small["Front"] ==unq_riders[1]]["Del_Speed"].max()-df_small[4:len(df_small)-1].loc[df_small["Front"] ==unq_riders[1]]["Del_Speed"].min(),df_small[4:len(df_small)-1].loc[df_small["Front"] ==unq_riders[2]]["Del_Speed"].max()-df_small[4:len(df_small)-1].loc[df_small["Front"] ==unq_riders[2]]["Del_Speed"].min(),df_small[4:len(df_small)-1].loc[df_small["Front"] ==unq_riders[3]]["Del_Speed"].max()-df_small[4:len(df_small)-1].loc[df_small["Front"] ==unq_riders[3]]["Del_Speed"].min()]
                    df_summ["Speed_Var"]=speed_var
#                     st.write("Wind score is a measure of exposure. In each quarter lap split, WS is calculated as WS = Summ [df(delivery_speed + speed_change)]")
#                     st.write("Delivery_speed is the speed assuming no positional change, speed_change is the difference in delivery speeds between intervals, and df is 'drag feel' - the portion of drag felt by a rider in a train, compared to a solo rider.")
#                     st.write("Current values for df are 0.971, 0.612, 0.495, 0.459 for lead, 2nd, 3rd and 4th riders respectively in a 4 person train, and 0.972, 0.617, 0.517 for lead, 2nd and 3rd riders in a 3 person chain.")
#                     st.write("We then sum all values to get the Wind_Score shown below:")

                    
                    df_summ.insert(5, "1&2", [(r1.count(1)+r1.count(2))/4,(r2.count(1)+r2.count(2))/4,(r3.count(1)+r3.count(2))/4,(r4.count(1)+r4.count(2))/4], True)
                    df_summ
                    
                    
                                 
                    st.subheader("Start Splits")
                    df_start=pd.DataFrame(df_small["Distance"][0:4])
                    df_start["Split"]=df_small["Split"][0:4]
                    df_start["Total"]=df_small["Split"][0:4].cumsum()
                    df_start
                    
                    
                    st.subheader("Lap Splits")
                    df_laps=pd.DataFrame(["Lap 1","Lap 2","Lap 3","Lap 4","Lap 5","Lap 6","Lap 7","Lap 8","Lap 9","Lap 10","Lap 11","Lap 12","Lap 13","Lap 14","Lap 15","Lap 16",])
                    df_laps.columns=["Distance"]
                    lap_split = [sum(df_small["Split"][0:4]),sum(df_small["Split"][4:8]),sum(df_small["Split"][8:12]),sum(df_small["Split"][12:16]),sum(df_small["Split"][16:20]),sum(df_small["Split"][20:24]),sum(df_small["Split"][24:28]),sum(df_small["Split"][28:32]),sum(df_small["Split"][32:36]),sum(df_small["Split"][36:40]),sum(df_small["Split"][40:44]),sum(df_small["Split"][44:48]),sum(df_small["Split"][48:52]),sum(df_small["Split"][52:56]),sum(df_small["Split"][56:60]),sum(df_small["Split"][60:64])]
                    df_laps["Split"]=lap_split
                    df_laps["Total"]=df_laps["Split"].cumsum()
                    df_laps['Total'] = pd.to_datetime(df_laps['Total'], unit='s').dt.strftime('%M:%S.%f')
                    df_laps['Diff from avg']=(average*4)-df_laps["Split"]
                    
                    laps_done = (df_laps["Split"].gt(12)).sum()
                    consistency = sum(abs(df_laps["Diff from avg"][1:laps_done]))
                    
                    df_laps
                    
                    
                    st.subheader("Kilo Splits")
                    df_kilos=pd.DataFrame(["1k","2k","3k","4k"])
                    df_kilos.columns=["Distance"]
                    kilo_split = [sum(df_small["Split"][0:16]),sum(df_small["Split"][16:32]),sum(df_small["Split"][32:48]),sum(df_small["Split"][48:64])]
                    df_kilos["Split"]=kilo_split
                    df_kilos["Total"]=df_kilos["Split"].cumsum()
                    df_kilos['Total'] = pd.to_datetime(df_kilos['Total'], unit='s').dt.strftime('%M:%S.%f')
                    df_kilos
                    
                    df_summ_full = df_summ
                    
                    df_summ_full.insert(1,"Event",df_temp["Title"].iloc[0])
                    # df_summ_full = df_summ_full.query(
                    #     "Event == @selections"
                    #     )
                    total_wind=df_summ_full['Wind_Score'].sum()
                    df_summ_full.insert(7,"Wind_Share_%",100*df_summ_full["Wind_Score"]/total_wind)
                    #df_summ_full["Wind_Share_%"]=100*df_summ_full["Wind_Score"]/total_wind
                    df_summ_full["Team_consistency"]=round(consistency,2)
                    df_summ_full.insert(1,"Position",[1,2,3,4])
                    df_summ_full.insert(3,"Time",df_kilos['Total'][3])
                    df_summ_full["62.5"]=round(df_small["Split"][0],3)
                    df_summ_full["125"]=round(df_start["Total"][1],3)
                    df_summ_full["187.5"]=round(df_start["Total"][2],3)
                    df_summ_full["250"]=round(df_start["Total"][3],3)
                    df_summ_full["1k"]=round(df_kilos["Split"][0],3)
                    df_summ_full["2k"]=round(df_kilos["Split"][1],3)
                    df_summ_full["3k"]=round(df_kilos["Split"][2],3)
                    df_summ_full["4k"]=round(df_kilos["Split"][3],3)
                    avg_del_split=df_summ_full['Avg_Del_Split'].mean()
                    df_summ_full.insert(11,"Avg_Del_Split_%",round(100*df_summ_full["Avg_Del_Split"]/avg_del_split,2))
                    df_summ_full["Date"]=df_summ_full["Event"].str[:8]
                    

                # df_start["Split"]=df_small["Split"][0:4]
                #     df_start["Total"]=df_small["Split"][0:4].cumsum()
                with col_2:
                    st.subheader(f"Consistency score is {round(consistency,2)}")
                    st.write("Sum of the absolute difference of lap splits from the average post first lap, pre last quarter (smaller is better).")
                    if Videos == "Yes":
                    
                    
                    
                        if pd.isnull(df_temp["Video"].iloc[0]):
                            st.header("No video available")
                        else:
                            video_name = df_temp["Video"].iloc[0]
                            st.header(df_temp["Title"].iloc[0])
           
                            st.video(f"{video_name}")
                st.markdown("---")
                
                
            
                if count == 0:
                    df_full_summary = pd.DataFrame()
                    df_full_summary=df_summ_full
                else:
                    df_full_summary = pd.concat([df_full_summary, df_summ_full], ignore_index=True)
            # df_full_summary.sort_values("Event_Count",ascending=True)
            st.header("Full Summary")
            df_full_summary["Dist_to_avg_speed"]=avg_speed_dists
            df_full_summary
            buffer = io.BytesIO()



            @st.cache_data
            def convert_to_csv(df_full_summary):
                # IMPORTANT: Cache the conversion to prevent computation on every rerun
                return df_full_summary.to_csv(index=False).encode('utf-8')

            csv = convert_to_csv(df_full_summary)

            # display the dataframe on streamlit app
    #         st.write(df)

            # download button 1 to download dataframe as csv
            download1 = st.download_button(
                label="Download Summary as CSV",
                data=csv,
                file_name='TP_Summary_Women.csv',
                mime='text/csv'
            )

            # download button 2 to download dataframe as xlsx
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                # Write each dataframe to a different worksheet.
                df_full_summary.to_excel(writer, sheet_name='Sheet1', index=False)
                # Close the Pandas Excel writer and output the Excel file to the buffer
                writer.close()

                download2 = st.download_button(
                    label="Download Summary as Excel",
                    data=buffer,
                    file_name='TP_Summary_Women.xlsx',
                    mime='application/vnd.ms-excel'
                ) 
            c1,c2=st.columns(2)
            with c1:
                variable = st.selectbox(
                'Select variable to compare:',
                    df_full_summary.columns[4:]
                )
            with c2:
                show_event = st.selectbox(
                'Show event names?',
                    ["No","Yes"]
                )

            df_full_summary["Date"]=df_full_summary["Event"].str[0:8]
            df_full_summary=df_full_summary.sort_values(by="Date")
            df_full_summary["EventName"]=df_full_summary["Event"].str[9:]
            if show_event == "Yes":
                fig_summary = px.line(df_full_summary, x="Date", color="Rider",y=f'{variable}',markers=True,text="EventName",hover_data=["EventName"])
            else:
                fig_summary = px.line(df_full_summary, x=df_full_summary["Date"], color="Rider",y=f'{variable}',markers=True,hover_data=["EventName"] )
        
            # x_ax=df_full_summary.sort_values("Event_Count",ascending=True)["Event"]
            # fig_summary = px.line(df_full_summary, x="Event_Count", y=f'{variable}',color="Rider",markers=True)
            # # fig_summary.update_xaxes(type='category')
            # fig_summary.update_xaxes(categoryorder='category ascending')
            st.plotly_chart(fig_summary, use_container_width=True)
            st.markdown("---")
                



            col_one, col_two, col_three, col_four = st.columns(4)
            with col_one:
                show_names = ["No","Yes"]
                Names = st.selectbox("Show Athlete Names?", show_names, key="Show_Names")
                df_combine["Initial"]=df_combine["Front"].apply(lambda x: ''.join(i[0] for i in x.split()))#.replace('[^A-Z]', '') 
                
            if Names == "Yes":
                fig_tt = px.line(df_combine, x="Distance", y = "Del_Speed", title="Comparison",color="Title",text="Initial",markers="Front")
                fig_tt.update_traces(textposition='top center')
            else:
                fig_tt = px.line(df_combine, x="Distance", y = "Del_Speed", title="Comparison",color="Title",markers="Front")

            st.plotly_chart(fig_tt, use_container_width=True)




        st.markdown("---")            
        st.header('View, edit and upload a new effort')



        uploaded_file = st.file_uploader("Choose a file",key="uploader")

        if uploaded_file is not None:
            st.markdown("---")

            st.header("Editor")
            df_full = pd.read_excel(uploaded_file)
            df_full['Position'] = df_full['Position'].apply(lambda t: t.hour * 3600 + t.minute * 60 + t.second + t.microsecond / 1_000_000)
#             df_full=df_full.sort_values(by=["Position"]).reset_index(drop=True)
            df_full.drop(['Duration'],
           axis='columns', inplace=True)
            df_full
            c1,c2,c3=st.columns(3)
            with c1:
                start=st.number_input("Start Row (inclusive)", value=0)
            with c2:
                end=st.number_input("End Row (inclusive)", value=start+65)+1
            
            
            df=df_full[start:end]
            
            df
            col_one, col_two, col_three = st.columns(3)
            with col_one:
                rider1 = st.text_input("Select Rider 1:")
                rider2 = st.text_input("Select Rider 2:")
                rider3 = st.text_input("Select Rider 3:")
                rider4 = st.text_input("Select Rider 4:")
            riders=[rider1,rider2,rider3,rider4]*10
            #riders
            df["Avg_Speed"]=0
            df["Del_Speed"]=0
            df["Split"]=0
            df["Front"]="HOLDER"
            front=[rider1]
            splits=[0]
            del_speeds=[0]
            speeds=[0]
            r=0
            df["Time"] = df["Position"] - df["Position"].iloc[0]
            markers = len(df)
            df["Distance"] = np.linspace(0, 62.5*(markers-1), num=markers)
            
            df=df.reset_index(drop=True)
            
            

            #df = df.dropna(axis=0, subset=['Time'])

            with col_two:
                offset = st.number_input("Offset:", min_value=0.00, max_value=None,value=0.12)
                schedule = round(st.number_input("Schedule:", min_value=0.00, max_value=None,value=14.3),2)
                Title = st.text_input("Plot Title:")


            with col_three:
                num_riders=4
                dropped=''
                #df
                rider_ind=0
                for i in range(1,len(df)):
                    df["Split"][i]=df["Time"][i]-df["Time"][i-1]
                    df["Avg_Speed"][i] = 62.5*3.6/(df["Split"][i])
                    if df["Name"][i] == "Change" or df["Name"][i] == "Drop":
                        df["Del_Speed"][i]=round(df["Avg_Speed"][i]*df["Split"][i]/(df["Split"][i]-offset),2)
                    else:
                        df["Del_Speed"][i]=df["Avg_Speed"][i]
                    if df["Name"][i]=="Drop":
                        df["Front"][i]=riders[rider_ind]
                        dropped=df["Front"][i]
                        rider_ind+=1
                    elif df["Name"][i]=="Change":
                        df["Front"][i]=riders[rider_ind]
                        rider_ind+=1
                        if riders[rider_ind] == dropped:
                            rider_ind+=1
                    else:
                        df["Front"][i]=riders[rider_ind]
                    if i == 65:
                        df["Avg_Speed"][i-1] = 62.5*3.6/(df["Time"][i]-df["Time"][i-2])
                
                        
                df = df.iloc[:-1]
                df.drop('Position',
          axis='columns', inplace=True)
                df.rename(columns = {'Name':'Action'}, inplace = True)
                df.drop(index=df.index[0], axis=0, inplace=True)
                #df = df.dropna(axis=0, subset=['Time'])
                st.write("final df")
                df = df.loc[:, ~df.columns.str.match(r'^Unnamed') & df.notna().any()]
                df


            fig = px.bar(df, x='Distance', y='Avg_Speed',color=df.Front,hover_data=[df.Split, df.Avg_Speed,df.Del_Speed])
            fig.add_trace(go.Scatter(x=df['Distance'][1:], y=df['Del_Speed'][1:],mode='markers',name="Delivery Speed"))
            fig.update_layout(
            title={
                'text': Title,
                'y':0.9,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top',
                'font':dict(size=25)})
            fig.add_hline(y=250*3.6/schedule, line_dash="dash",line_color="white",annotation_text="Schedule = " +str(schedule))
            st.plotly_chart(fig, use_container_width=True)






            #master_path=st.text_input("Add path to master file:",key="prompt")
            if st.button("Append this effort to master",key="upload"):




                df_save=df
                df_save.insert(0, 'Save_Date', datetime.date.today())
                df_save["Save_Date"] = pd.to_datetime(df_save['Save_Date'])
                df_save.insert(0, 'Title', Title)
                df = pd.concat([df_master, df_save], axis=0)
                df

                ##Testing downloader


                # buffer to use for excel writer
                buffer = io.BytesIO()



                @st.cache_data
                def convert_to_csv(df):
                    # IMPORTANT: Cache the conversion to prevent computation on every rerun
                    return df.to_csv(index=False).encode('utf-8')

                csv = convert_to_csv(df)

                # display the dataframe on streamlit app
        #         st.write(df)

                # download button 1 to download dataframe as csv
                download1 = st.download_button(
                    label="Download new Master as CSV",
                    data=csv,
                    file_name='TP_Master_Women.csv',
                    mime='text/csv'
                )

                # download button 2 to download dataframe as xlsx
                with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                    # Write each dataframe to a different worksheet.
                    df.to_excel(writer, sheet_name='Sheet1', index=False)
                    # Close the Pandas Excel writer and output the Excel file to the buffer
                    writer.close()

                    download2 = st.download_button(
                        label="Download new Master as Excel",
                        data=buffer,
                        file_name='TP_Master_Women.xlsx',
                        mime='application/vnd.ms-excel'
                    )  
                    
                    
   ###################################################### Men's Team Pursuit ####################################                 
                    
    if racetype == "Men's TP":
        df_master = pd.read_excel(f'pages/video_analysis/TP_Master_Men.xlsx')
        df_master['Sort'] = df_master['Title'].str.replace('Q', 'Z', regex=False)
        df_master = df_master.sort_values(by=["Sort","Distance"], ascending=[False,True])

        df_small = df_master.drop(columns=["Save_Date","Action","Video","Sort"])
#         df_small
        c1,c2,c3=st.columns(3)
        with c1:
            ath_filt = st.multiselect(
    'Filter athletes? Leave blank to see all rides',["Aaron Gate","Campbell Stewart","Dan Bridgwater","George Jackson","Keegan Hornblow","Nick Kergozou","Tom Sexton"]
    )
            st.markdown("[Jump to Full Summary](#full-summary)", unsafe_allow_html=True)
        with c2:
            if len(ath_filt)>0:
                
                options=[]
                for race in df_small["Title"].unique():
                    for name in ath_filt:
                        #st.write(df_small["Front"].loc[df_small["Title"]==race].unique())
                        if name in df_small["Front"].loc[df_small["Title"]==race].unique():
                            #st.write(df_small["Front"].loc[df_small["Title"]==race])
                            options.append(race)
                selections = st.multiselect(
                "Select past effort(s):",
                options=options  #.sort_values(ascending=False)
                ) 
            else:
                selections = st.multiselect(
                "Select past effort(s):",
                options=df_master["Title"].unique()  #.sort_values(ascending=False)
                ) 
        with c3:
            show_vids = ["No","Yes"]
            Videos = st.selectbox("Show Race Videos?", show_vids, key="Show_Vids")

        st.markdown("---")
        if len(selections) !=0:
            avg_speed_dists=[]
            df_combine = pd.DataFrame()
            for event_count in range(len(selections)):
                col_1,col_2=st.columns(2)
                with col_1:
                    
                    df_temp = df_master.loc[df_master['Title'] == selections[event_count]]
                    st.header(df_temp["Title"].iloc[0])
                    df_combine = pd.concat([df_combine, df_temp], axis=0)
                    df_small = df_temp.drop(columns=["Save_Date","Video","Sort"])
                    df_small=df_small.reset_index(drop="True")
                    r1 = [1]
                    r2 = [2]
                    r3 = [3]
                    r4 = [4]
                    r1WS = [0.971]
                    r2WS = [0.612]
                    r3WS = [0.495]
                    r4WS = [0.459]
                    speed_diff=[df_small["Del_Speed"][0]]

                    no_riders=4
                    drag_feel = [0,0.971,0.612,0.495,0.459]
                    for j in range(1,len(df_small)):
                        speed_diff.append(df_small["Del_Speed"][j]-df_small["Del_Speed"][j-1])
                        if df_small["Action"][j-1] == "Change":
                            r1.append(r1[j-1]-1)
                            r2.append(r2[j-1]-1)
                            r3.append(r3[j-1]-1)
                            r4.append(r4[j-1]-1)
                        elif df_small["Action"][j-1] == "Drop":
                            no_riders = 3
                            drag_feel = [0,0.972,0.617,0.517]
                            r1.append(r1[j-1]-1)
                            r2.append(r2[j-1]-1)
                            r3.append(r3[j-1]-1)
                            r4.append(r4[j-1]-1)
                        else:
                            r1.append(r1[j-1])
                            r2.append(r2[j-1])
                            r3.append(r3[j-1])
                            r4.append(r4[j-1])
                        if r1[j]==0:
                            r1[j]=no_riders
                        if r2[j]==0:
                            r2[j]=no_riders
                        if r3[j]==0:
                            r3[j]=no_riders
                        if r4[j]==0:
                            r4[j]=no_riders
                        r1WS.append(drag_feel[r1[j]])
                        r2WS.append(drag_feel[r2[j]])
                        r3WS.append(drag_feel[r3[j]])
                        r4WS.append(drag_feel[r4[j]])
                    if "Drop" in df_small["Action"].unique():        
                        ind = df_small.index[df_small['Action'] == "Drop"][0]

                        if r1[ind]==1:
                            r1[ind+1:]=[0]*(len(df_small)-ind-1)
                            r1WS[ind+1:]=[0]*(len(df_small)-ind-1)
                        if r2[ind]==1:
                            r2[ind+1:]=[0]*(len(df_small)-ind-1)
                            r2WS[ind+1:]=[0]*(len(df_small)-ind-1)
                        if r3[ind]==1:
                            r3[ind+1:]=[0]*(len(df_small)-ind-1)
                            r3WS[ind+1:]=[0]*(len(df_small)-ind-1)
                        if r4[ind]==1:
                            r4[ind+1:]=[0]*(len(df_small)-ind-1)
                            r4WS[ind+1:]=[0]*(len(df_small)-ind-1)
                    one_turn_1=0
                    two_turn_1=0
                    three_turn_1=0
                    four_turn_1=0
                    one_turn_2=0
                    two_turn_2=0
                    three_turn_2=0
                    four_turn_2=0
                    one_turn_3=0
                    two_turn_3=0
                    three_turn_3=0
                    four_turn_3=0
                    j=0

                    while j<len(df_small) and r1[j] == 1:
                        one_turn_1+=1
                        j+=1
                    while j<len(df_small) and r2[j] == 1:
                        two_turn_1+=1
                        j+=1
                    while j<len(df_small) and r3[j] == 1:
                        three_turn_1+=1
                        j+=1
                    while j<len(df_small) and r4[j] == 1:
                        four_turn_1+=1
                        j+=1
                    while j<len(df_small) and r1[j] == 1:
                        one_turn_2+=1
                        j+=1
                    while j<len(df_small) and r2[j] == 1:
                        two_turn_2+=1
                        j+=1
                    while j<len(df_small) and r3[j] == 1:
                        three_turn_2+=1
                        j+=1
                    while j <len(df_small) and r4[j] == 1:
                        four_turn_2+=1
                        j+=1
                    while j <len(df_small) and r1[j] == 1:
                        one_turn_3+=1
                        j+=1
                    while j <len(df_small) and r2[j] == 1:
                        two_turn_3+=1
                        j+=1
                    while j<len(df_small) and r3[j] == 1:
                        three_turn_3+=1
                        j+=1
                    while j <len(df_small) and r4[j] == 1:
                        four_turn_3+=1
                        j+=1
                    first_turns=[one_turn_1/4,two_turn_1/4,three_turn_1/4,four_turn_1/4]
                    second_turns=[one_turn_2/4,two_turn_2/4,three_turn_2/4,four_turn_2/4]
                    third_turns=[one_turn_3/4,two_turn_3/4,three_turn_3/4,four_turn_3/4]
                    df_small["Rider1"]=r1
                    df_small["Rider2"]=r2
                    df_small["Rider3"]=r3
                    df_small["Rider4"]=r4
                    df_small["Speed_Diff"]=speed_diff
                    df_small["Rider1WS"]=r1WS*(df_small["Del_Speed"]+df_small["Speed_Diff"])
                    df_small["Rider2WS"]=r2WS*(df_small["Del_Speed"]+df_small["Speed_Diff"])
                    df_small["Rider3WS"]=r3WS*(df_small["Del_Speed"]+df_small["Speed_Diff"])
                    df_small["Rider4WS"]=r4WS*(df_small["Del_Speed"]+df_small["Speed_Diff"])
                    
                    df_small
                    df_main = df_small.drop(columns=["Rider1","Rider2","Rider3","Rider4","Action","Speed_Diff","Rider1WS","Rider2WS","Rider3WS","Rider4WS"])
                    
                    
                    hl_splits=[]
                    hl_rider =[] 
                    hl_distance=[]
                    hl_del_speed=[]
                    for i in range(2,len(df_main["Split"]),2):
                        hl_splits.append(df_main["Split"][i]+df_main["Split"][i-1])
                        hl_rider.append(df_main["Front"][i])
                        hl_distance.append(df_main["Distance"][i])
                        if df_main["Del_Speed"][i]!=df_main["Avg_Speed"][i]:
                            hl_del_speed.append(df_main["Del_Speed"][i])
                        else:
                            hl_del_speed.append(125*3.6/(df_main["Split"][i]+df_main["Split"][i-1]))
                    df_gm=pd.DataFrame()
                    df_gm["Split"] = hl_splits
                    df_gm["Front"]=hl_rider
                    df_gm["Distance"]=hl_distance
                    df_gm["Avg_Speed"]=125*3.6/df_gm["Split"]
                    df_gm["Del_Speed"]=hl_del_speed
                    lap_splits=[]
                    for i in range(len(df_gm["Split"])):
                        if i % 2==0:
                            lap_splits.append("")
                        else:
                            lap_splits.append(round(df_gm["Split"][i]+df_gm["Split"][i-1],2))
                    df_gm["Lap_Split"]=lap_splits
    #                     df_gm
                   
                    
                with col_2:
                    c1sub,c2sub=st.columns(2)
                    with c1sub:
                        yaxis_min = st.number_input("Y-axis Minimum:", min_value=0.00, max_value=None,value=min(df_temp["Avg_Speed"][1:])-1,key = f"{event_count}ymin")
                    with c2sub:
                        yaxis_max = st.number_input("Y-axis Maximum:", min_value=min(df_temp["Avg_Speed"])-1, max_value=None,value=max(df_temp["Avg_Speed"])+1,key = f"{event_count}ymax")
                    average = df_small.Split.iloc[4:].mean()
                    
                    fig = px.bar(df_temp, x='Distance', y='Avg_Speed',color=df_temp.Front,hover_data={'Split':':.2f', 'Avg_Speed':':.2f', 'Del_Speed':':.2f'})
                    fig.add_trace(go.Scatter(x=df_temp['Distance'][1:], y=df_temp['Del_Speed'][1:],mode='markers',name="Delivery Speed"))
                    fig.update_layout(
                    title={
                        'text': df_temp.Title.iloc[0],
                        'y':0.9,
                        'x':0.5,
                        'xanchor': 'center',
                        'yanchor': 'top',
                        'font':dict(size=25)})

                    av_speed=3.6*62.5/average
                    
                    
                    av_idx=1
                    below_av = df_small["Del_Speed"][av_idx]
                    above_av=below_av
                    while (below_av <av_speed) or (av_idx<2) :
                        below_av=df_small["Del_Speed"][av_idx]
                        av_idx+=1
                    above_av=df_small["Del_Speed"][av_idx-1]
                    below_av=df_small["Del_Speed"][av_idx-2]
                    
                    
                    below_av_dist = df_small["Distance"][av_idx-2]
                    
                    if below_av==above_av:
                        av_speed_dist = below_av_dist
                    else:
                        av_speed_dist = below_av_dist + 62.5*(av_speed-below_av)/(above_av-below_av)
                    avg_speed_dists.extend([av_speed_dist for i in range(4)])
                    fig.add_vline(x=round(av_speed_dist,2), line_dash="dash",line_color="yellow",annotation_text=f"Avg speed at {round(av_speed_dist,2)}m")
                    fig.add_hline(y=62.5*3.6/average, line_dash="dash",line_color="yellow",annotation_text="Avg after first lap = " +str(round(average*4,2)))
                    yaxis_min = yaxis_min #min(df_temp["Avg_Speed"][1:])-1
                    yaxis_max = yaxis_max #max(df_temp["Avg_Speed"])+1
                    fig.update_layout(yaxis_range=[yaxis_min,yaxis_max])
                    st.plotly_chart(fig, use_container_width=True)
                    
                    #Goldmine style Speed Trace
                    st.header("Goldmine style speed trace")
                    
                    fig_gm = px.bar(df_gm, x='Distance', y='Avg_Speed',text="Lap_Split",color=df_gm.Front,hover_data={'Split':':.2f', 'Avg_Speed':':.2f'})
                    
                    fig_gm.add_trace(go.Scatter(x=df_gm['Distance'][1:], y=df_gm['Del_Speed'][1:],mode='markers',name="Delivery Speed"))
                    fig_gm.update_layout(
                    title={
                        'text': df_temp.Title.iloc[0],
                        'y':0.9,
                        'x':0.5,
                        'xanchor': 'center',
                        'yanchor': 'top',
                        'font':dict(size=25)})
                    fig_gm.add_vline(x=round(av_speed_dist,2), line_dash="dash",line_color="yellow",annotation_text=f"Avg speed at {round(av_speed_dist,2)}m")
                    fig_gm.add_hline(y=62.5*3.6/average, line_dash="dash",line_color="yellow",annotation_text="Avg after first lap = " +str(round(average*4,2)))
                    fig_gm.update_layout(yaxis_range=[yaxis_min,yaxis_max])
                    fig_gm.update_traces(textfont_size=24, cliponaxis=False)
                    st.plotly_chart(fig_gm, use_container_width=True)
                c1,c2=st.columns(2)
                with col_1:
                    #st.write("Wind score is a measure of exposure. In each quarter lap split, WS is calculated as WS = Summ [df(delivery_speed + speed_change)]")
                    #st.write("Delivery_speed is the speed assuming no positional change, speed_change is the difference in delivery speeds between intervals, and df is 'drag feel' - the portion of drag felt by a rider in a train, compared to a solo rider.")
                    #st.write("Current values for df are 0.971, 0.612, 0.495, 0.459 for lead, 2nd, 3rd and 4th riders respectively in a 4 person train, and 0.972, 0.617, 0.517 for lead, 2nd and 3rd riders in a 3 person chain.")
                    #st.write("We then sum all values to get the Wind_Score shown below:")
                    
                    unq_riders = df_small["Front"].unique()
                    df_summ=pd.DataFrame(unq_riders)
                    df_summ.columns=["Rider"]
                    df_summ=df_summ.dropna(axis=0)
                    front=[]
                    front.append(len(df_small.loc[df_small['Front'] == df_summ["Rider"][0]])/4)
                    front.append(len(df_small.loc[df_small['Front'] == df_summ["Rider"][1]])/4)
                    front.append(len(df_small.loc[df_small['Front'] == df_summ["Rider"][2]])/4)
                    front.append(len(df_small.loc[df_small['Front'] == df_summ["Rider"][3]])/4)
                    wind_scores = []
                    df_small['Rider1WS'].fillna(0)
                    wind_scores.append(round(sum(df_small['Rider1WS'].fillna(0),1)))
                    wind_scores.append(round(sum(df_small['Rider2WS'].fillna(0),1)))
                    wind_scores.append(round(sum(df_small['Rider3WS'].fillna(0),1)))
                    wind_scores.append(round(sum(df_small['Rider4WS'].fillna(0),1)))
                    df_summ["Front"]=front
                    df_summ["Turn_1"]=first_turns
                    df_summ["Turn_2"]=second_turns
                    df_summ["Turn_3"]=third_turns
                    df_summ["1&2"]=[(df_small['Rider1'].value_counts()[1]+df_small['Rider1'].value_counts()[2])/4,(df_small['Rider2'].value_counts()[1]+df_small['Rider2'].value_counts()[2])/4,(df_small['Rider3'].value_counts()[1]+df_small['Rider3'].value_counts()[2])/4,(df_small['Rider4'].value_counts()[1]+df_small['Rider4'].value_counts()[2])/4]
                    df_summ["Wind_Score"] = wind_scores
                    
                    # Calculating Splits based off delivery speeds - 900 is a conversion factor
                    avg_splits=[round(900/(df_small[4:].loc[df_small["Front"] ==unq_riders[0]]["Del_Speed"].mean()),2), round(900/df_small[4:].loc[df_small["Front"] ==unq_riders[1]]["Del_Speed"].mean(),2),round(900/df_small[4:].loc[df_small["Front"] ==unq_riders[2]]["Del_Speed"].mean(),2),round(900/df_small[4:len(df_small)-1].loc[df_small["Front"] ==unq_riders[3]]["Del_Speed"].mean(),2)]
                    df_summ["Avg_Del_Split"]=avg_splits
                    
                    
                    speed_var=[df_small[4:].loc[df_small["Front"] ==unq_riders[0]]["Del_Speed"].max()-df_small[4:len(df_small)-1].loc[df_small["Front"] ==unq_riders[0]]["Del_Speed"].min(),df_small[4:len(df_small)-1].loc[df_small["Front"] ==unq_riders[1]]["Del_Speed"].max()-df_small[4:len(df_small)-1].loc[df_small["Front"] ==unq_riders[1]]["Del_Speed"].min(),df_small[4:len(df_small)-1].loc[df_small["Front"] ==unq_riders[2]]["Del_Speed"].max()-df_small[4:len(df_small)-1].loc[df_small["Front"] ==unq_riders[2]]["Del_Speed"].min(),df_small[4:len(df_small)-1].loc[df_small["Front"] ==unq_riders[3]]["Del_Speed"].max()-df_small[4:len(df_small)-1].loc[df_small["Front"] ==unq_riders[3]]["Del_Speed"].min()]
                    df_summ["Speed_Var"]=speed_var
                    
                    
                    st.subheader("Rider Info")
                    df_summ
                    st.subheader("Start Splits")
                    df_start=pd.DataFrame(df_small["Distance"][0:4])
                    df_start["Split"]=df_small["Split"][0:4]
                    df_start["Total"]=df_small["Split"][0:4].cumsum()
                    df_start
                    
                    st.subheader("Lap Splits")
                    df_laps=pd.DataFrame(["Lap 1","Lap 2","Lap 3","Lap 4","Lap 5","Lap 6","Lap 7","Lap 8","Lap 9","Lap 10","Lap 11","Lap 12","Lap 13","Lap 14","Lap 15","Lap 16",])
                    df_laps.columns=["Distance"]
                    lap_split = [sum(df_small["Split"][0:4]),sum(df_small["Split"][4:8]),sum(df_small["Split"][8:12]),sum(df_small["Split"][12:16]),sum(df_small["Split"][16:20]),sum(df_small["Split"][20:24]),sum(df_small["Split"][24:28]),sum(df_small["Split"][28:32]),sum(df_small["Split"][32:36]),sum(df_small["Split"][36:40]),sum(df_small["Split"][40:44]),sum(df_small["Split"][44:48]),sum(df_small["Split"][48:52]),sum(df_small["Split"][52:56]),sum(df_small["Split"][56:60]),sum(df_small["Split"][60:64])]
                    df_laps["Split"]=lap_split
                    df_laps["Total"]=df_laps["Split"].cumsum()
                    df_laps['Total'] = pd.to_datetime(df_laps['Total'], unit='s').dt.strftime('%M:%S.%f')
                    
                    laps_done = (df_laps["Split"].gt(12)).sum()
                    
                    df_laps['Diff from avg']=(average*4)-df_laps["Split"]
                    consistency = sum(abs(df_laps["Diff from avg"][1:laps_done]))
                    
                    
                    df_laps
                    
                    st.subheader("Kilo Splits")
                    df_kilos=pd.DataFrame(["1k","2k","3k","4k"])
                    df_kilos.columns=["Distance"]
                    kilo_split = [sum(df_small["Split"][0:16]),sum(df_small["Split"][16:32]),sum(df_small["Split"][32:48]),sum(df_small["Split"][48:64])]
                    df_kilos["Split"]=kilo_split
                    df_kilos["Total"]=df_kilos["Split"].cumsum()
                    df_kilos['Total'] = pd.to_datetime(df_kilos['Total'], unit='s').dt.strftime('%M:%S.%f')
                    df_kilos
                    df_summ_full = df_summ
                    df_summ_full.insert(1,"Event",df_temp["Title"].iloc[0])
                    total_wind=df_summ_full['Wind_Score'].sum()
                    df_summ_full.insert(7,"Wind_Share_%",100*df_summ_full["Wind_Score"]/total_wind)
                    #df_summ_full["Wind_Share_%"]=100*df_summ_full["Wind_Score"]/total_wind
                    df_summ_full["Team_consistency"]=round(consistency,2)
                    df_summ_full.insert(1,"Position",[1,2,3,4])
                    df_summ_full["1&2"]=df_summ["1&2"]
                    df_summ_full.insert(3,"Time",df_kilos['Total'][3])
                    df_summ_full["62.5"]=round(df_small["Split"][0],3)
                    df_summ_full["125"]=round(df_start["Total"][1],3)
                    df_summ_full["187.5"]=round(df_start["Total"][2],3)
                    df_summ_full["250"]=round(df_start["Total"][3],3)
                    df_summ_full["1k"]=round(df_kilos["Split"][0],3)
                    df_summ_full["2k"]=round(df_kilos["Split"][1],3)
                    df_summ_full["3k"]=round(df_kilos["Split"][2],3)
                    df_summ_full["4k"]=round(df_kilos["Split"][3],3)
                    
                    avg_del_split=df_summ_full['Avg_Del_Split'].mean()
                    df_summ_full.insert(11,"Avg_Del_Split_%",round(100*df_summ_full["Avg_Del_Split"]/avg_del_split,2))
                    
                with col_2:
                    st.subheader(f"Consistency score is {round(consistency,2)}")
                    st.write("Sum of the absolute difference of lap splits from the average post first lap, pre last quarter (smaller is better).")
                    if Videos == "Yes":

                        if pd.isnull(df_temp["Video"].iloc[0]):
                            st.header("No video available")
                        else:
                            video_name = df_temp["Video"].iloc[0]
                            st.header(df_temp["Title"].iloc[0])

                            st.video(f"{video_name}")
                st.markdown("---")
                
                
            
                if event_count == 0:
                    df_full_summary = pd.DataFrame()
                    df_full_summary=df_summ_full
                else:
                    df_full_summary = pd.concat([df_full_summary, df_summ_full], ignore_index=True)
            st.header("Full Summary")
            
            df_full_summary["Dist_to_avg_speed"]=avg_speed_dists
            df_full_summary
            
            buffer = io.BytesIO()



            @st.cache_data
            def convert_to_csv(df_full_summary):
                # IMPORTANT: Cache the conversion to prevent computation on every rerun
                return df_full_summary.to_csv(index=False).encode('utf-8')

            csv = convert_to_csv(df_full_summary)

            # display the dataframe on streamlit app
    #         st.write(df)

            # download button 1 to download dataframe as csv
            download1 = st.download_button(
                label="Download Summary as CSV",
                data=csv,
                file_name='TP_Summary_Men.csv',
                mime='text/csv'
            )

            # download button 2 to download dataframe as xlsx
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                # Write each dataframe to a different worksheet.
                df_full_summary.to_excel(writer, sheet_name='Sheet1', index=False)
                # Close the Pandas Excel writer and output the Excel file to the buffer
                writer.close()

                download2 = st.download_button(
                    label="Download Summary as Excel",
                    data=buffer,
                    file_name='TP_Summary_Men.xlsx',
                    mime='application/vnd.ms-excel'
                )  
            c1,c2=st.columns(2)
            with c1:
                variable = st.selectbox(
                'Select variable to compare:',
                    df_full_summary.columns[4:]
                )
            with c2:
                show_event = st.selectbox(
                'Display event name?',
                    ["No","Yes"]
                )   

            # riders=df_full_summary["Rider"].unique()
            # events = df_full_summary["Event"].unique()
            # riders2=[]
            # for idx,event in enumerate(events):
            #     df_temp = df_full_summary.loc[df_full_summary["Event"]==event].reset_index(drop=True)
            #     df_temp
            #     for rider in riders:
            #         for i
            #         if df_temp.Rider.isin([riders]):
            #             riders2.append(rider)
            # riders2
                

            




            ##Horrific code snippet
            
            # df_var_summ=pd.DataFrame()
            # df_event_unq=pd.DataFrame()
            # df_var_summ["Rider"]=df_full_summary["Rider"].unique()
            # df_var_summ = pd.DataFrame(np.repeat(df_var_summ.values, len(df_full_summary["Event"].unique()), axis=0))
            # df_var_summ.rename(columns={ df_var_summ.columns[0]: "Rider" }, inplace = True)
            # events=[]
            # count=0
            # for i in range(len(df_var_summ)):
            #     events.append(df_full_summary["Event"].unique()[count])
            #     count+=1
            #     if count==len(df_full_summary["Event"].unique()):
            #         count=0
            # var_score=[]
            # df_var_summ["Event"]=events
            # df_var_summ
            # for i in range(len(df_var_summ)):
            #     rider = df_var_summ["Rider"][i]
            #     event = df_var_summ["Event"][i]
            #     df_temp=df_full_summary.loc[df_full_summary["Event"]==event]
            #     if rider in df_temp["Rider"].unique():
            #         df_temp
            #         ind = df_temp['Rider'].loc[lambda x: x==True].index
            #         id
            #         var_score.append(df_temp[f'{variable}'][ind])
            #     else:
            #         var_score.append(None)
            # df_var_summ[f"{variable}"]=var_score
            # df_var_summ






            
            df_full_summary["Date"]=df_full_summary["Event"].str[0:8]
            df_full_summary=df_full_summary.sort_values(by="Date")
            df_full_summary["EventName"]=df_full_summary["Event"].str[9:]
            
            
            if show_event == "Yes":
                fig_summary = px.line(df_full_summary, x="Date", color="Rider",y=f'{variable}',markers=True,text="EventName",hover_data=["EventName"])
            else:
                fig_summary = px.line(df_full_summary, x=df_full_summary["Date"], color="Rider",y=f'{variable}',markers=True,hover_data=["EventName"] )
            #for event in df_full_summary["Event"].unique():
        
            # fig_gm.add_trace(go.Scatter(x=df_gm['Distance'][1:], y=df_gm['Del_Speed'][1:],mode='markers',name="Delivery Speed"))
            # fig_gm.update_layout(
            # title={
            #     'text': df_temp.Title.iloc[0],
            #     'y':0.9,
            #     'x':0.5,
            #     'xanchor': 'center',
            #     'yanchor': 'top',
            #     'font':dict(size=25)})
            # fig_gm.add_hline(y=62.5*3.6/average, line_dash="dash",line_color="yellow",annotation_text="Avg after first lap = " +str(round(average*4,2)))
            # fig_gm.update_layout(yaxis_range=[yaxis_min,yaxis_max])
            # fig_gm.update_traces(textfont_size=24, cliponaxis=False)
            
            st.plotly_chart(fig_summary, use_container_width=True)
            st.markdown("---")



            col_one, col_two, col_three, col_four = st.columns(4)
            with col_one:
                show_names = ["No","Yes"]
                Names = st.selectbox("Show Athlete Names?", show_names, key="Show_Names")
                df_combine["Initial"]=df_combine["Front"].apply(lambda x: ''.join(i[0] for i in x.split()))
            
            if Names == "Yes":
                fig_tt = px.line(df_combine, x="Distance", y = "Del_Speed", title="Comparison",color="Title",text="Initial",markers="Front")
                fig_tt.update_traces(textposition='top center')
            else:
                fig_tt = px.line(df_combine, x="Distance", y = "Del_Speed", title="Comparison",color="Title",markers="Front")

            st.plotly_chart(fig_tt, use_container_width=True)
            







        st.markdown("---")            
        st.header('View, edit and upload a new effort')



        uploaded_file = st.file_uploader("Choose a file",key="uploader")

        if uploaded_file is not None:
            st.markdown("---")

            st.header("Editor")
            df_full = pd.read_excel(uploaded_file)
            df_full['Position'] = df_full['Position'].apply(lambda t: t.hour * 3600 + t.minute * 60 + t.second + t.microsecond / 1_000_000)
#             df_full=df_full.sort_values(by=["Position"]).reset_index(drop=True)
            df_full.drop(['Duration'],
           axis='columns', inplace=True)
            df_full
            c1,c2,c3=st.columns(3)
            with c1:
                start=st.number_input("Start Row (inclusive)", value=0)
            with c2:
                end=st.number_input("End Row (inclusive)", value=start+65)+1
            
            
            df=df_full[start:end]
            
            df
            col_one, col_two, col_three = st.columns(3)
            with col_one:
                rider1 = st.text_input("Select Rider 1:")
                rider2 = st.text_input("Select Rider 2:")
                rider3 = st.text_input("Select Rider 3:")
                rider4 = st.text_input("Select Rider 4:")
            riders=[rider1,rider2,rider3,rider4]*10
            #riders
            df["Avg_Speed"]=0
            df["Del_Speed"]=0
            df["Split"]=0
            df["Front"]="HOLDER"
            front=[rider1]
            splits=[0]
            del_speeds=[0]
            speeds=[0]
            r=0
            df["Time"] = df["Position"] - df["Position"].iloc[0]
            markers = len(df)
            df["Distance"] = np.linspace(0, 62.5*(markers-1), num=markers)
            
            df=df.reset_index(drop=True)
            
            

            #df = df.dropna(axis=0, subset=['Time'])

            with col_two:
                offset = st.number_input("Offset:", min_value=0.00, max_value=None,value=0.12)
                schedule = round(st.number_input("Schedule:", min_value=0.00, max_value=None,value=14.3),2)
                Title = st.text_input("Plot Title:")


            with col_three:
                num_riders=4
                dropped=''
                #df
                rider_ind=0
                for i in range(1,len(df)):
                    df["Split"][i]=df["Time"][i]-df["Time"][i-1]
                    df["Avg_Speed"][i] = 62.5*3.6/(df["Split"][i])
                    if df["Name"][i] == "Change" or df["Name"][i] == "Drop":
                        df["Del_Speed"][i]=round(df["Avg_Speed"][i]*df["Split"][i]/(df["Split"][i]-offset),2)
                    else:
                        df["Del_Speed"][i]=df["Avg_Speed"][i]
                    if df["Name"][i]=="Drop":
                        df["Front"][i]=riders[rider_ind]
                        dropped=df["Front"][i]
                        rider_ind+=1
                    elif df["Name"][i]=="Change":
                        df["Front"][i]=riders[rider_ind]
                        rider_ind+=1
                        if riders[rider_ind] == dropped:
                            rider_ind+=1
                    else:
                        df["Front"][i]=riders[rider_ind]
                    if i == 65:
                        df["Avg_Speed"][i-1] = 62.5*3.6/(df["Time"][i]-df["Time"][i-2])
                
                        
                df = df.iloc[:-1]
                df.drop('Position',
          axis='columns', inplace=True)
                df.rename(columns = {'Name':'Action'}, inplace = True)
                df.drop(index=df.index[0], axis=0, inplace=True)
                #df = df.dropna(axis=0, subset=['Time'])
                st.write("final df")
                df = df.loc[:, ~df.columns.str.match(r'^Unnamed') & df.notna().any()]
                df


            fig = px.bar(df, x='Distance', y='Avg_Speed',color=df.Front,hover_data=[df.Split, df.Avg_Speed,df.Del_Speed])
            fig.add_trace(go.Scatter(x=df['Distance'][1:], y=df['Del_Speed'][1:],mode='markers',name="Delivery Speed"))
            fig.update_layout(
            title={
                'text': Title,
                'y':0.9,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top',
                'font':dict(size=25)})
            fig.add_hline(y=250*3.6/schedule, line_dash="dash",line_color="white",annotation_text="Schedule = " +str(schedule))
            st.plotly_chart(fig, use_container_width=True)






            #master_path=st.text_input("Add path to master file:",key="prompt")
            if st.button("Append this effort to master",key="upload"):




                df_save=df
                df_save.insert(0, 'Save_Date', datetime.date.today())
                df_save["Save_Date"] = pd.to_datetime(df_save['Save_Date'])
                df_save.insert(0, 'Title', Title)
                df = pd.concat([df_master, df_save], axis=0)
                df

                ##Testing downloader


                # buffer to use for excel writer
                buffer = io.BytesIO()



                @st.cache_data
                def convert_to_csv(df):
                    # IMPORTANT: Cache the conversion to prevent computation on every rerun
                    return df.to_csv(index=False).encode('utf-8')

                csv = convert_to_csv(df)

                # display the dataframe on streamlit app
        #         st.write(df)

                # download button 1 to download dataframe as csv
                download1 = st.download_button(
                    label="Download new Master as CSV",
                    data=csv,
                    file_name='TP_Master_Men.csv',
                    mime='text/csv'
                )

                # download button 2 to download dataframe as xlsx
                with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                    # Write each dataframe to a different worksheet.
                    df.to_excel(writer, sheet_name='Sheet1', index=False)
                    # Close the Pandas Excel writer and output the Excel file to the buffer
                    writer.close()

                    download2 = st.download_button(
                        label="Download new Master as Excel",
                        data=buffer,
                        file_name='TP_Master_Men.xlsx',
                        mime='application/vnd.ms-excel'
                    )                
                    
    ######################################## Men's Keirin ################################################################                
                    
    elif racetype == "Mens' Keirin":
        df_master = pd.read_csv(f'pages/video_analysis/Mens_Keirin.csv')
        
        #df_small = df_master.drop(columns=["Save_Date","Action","Video"])
        df_select = df_master
        c1,c2,c3,c4 = st.columns(4)
        with c1:
            
            event = st.selectbox(
            "Select Event(s):",
            options=df_master["Event"].unique()
            ) 
            if event:
                df_select = df_master.query(
            "Event == @event"
            )
        with c2:
            Round = st.selectbox(
            "Select Round(s):",
            options=df_select["Round"].unique()
            )
            if Round:
                df_select = df_select.query(
            "Round == @Round"
            )
        with c3:
            Heat = st.selectbox(
            "Select Heat(s):",
            options=df_select["Heat"].unique()
            )
            if Heat:
                df_select = df_select.query(
            "Heat == @Heat"
            )
        with c4:
            show_vids = ["No","Yes"]
            Videos = st.selectbox("Show Race Video?", show_vids, key="Show_Vids")
        df_select["Time"]=df_select["Start time"]-df_select["Start time"].iloc[0]
        df_select=df_select.drop(columns=["Start time"])
        #df_select    
        
        
        
        
        df_gaps = pd.DataFrame()
        df_gaps["To Go"] = ["3 Laps","2.5 Laps","2 Laps","1.5 Laps","1 Lap","0.5 Laps","15m"]
        
        for i in range(len(df_select["Name"].unique())):
            var = str(df_select["Name"].unique()[i])
           
            df_gaps[f"{var}"]=df_select.loc[df_select["Name"]==var]["Time"].values
        
        cols = len(df_gaps.columns)
        
        df_splits=pd.DataFrame()
        df_splits["Half"] = [1,2,3,4,5,6]
        for i in range(1,cols):
            x=[]
            for j in range(1,7):
                x.append(df_gaps[df_gaps.columns[i]][j]-df_gaps[df_gaps.columns[i]][j-1])
            df_splits[df_gaps.columns[i]] = x

        for i in range(1,7):
            small = df_gaps.loc[i][1:].min()
            
            for j in range(1,cols):
                df_gaps.loc[i,df_gaps.columns[j]]=df_gaps.loc[i,df_gaps.columns[j]]-small
     

        
        
        st.subheader("Time Gap to Leader") 
        c1,c2=st.columns([1,3])
        with c1:
            df_gaps 

        fig_tt = px.line(df_gaps, x="To Go", y = df_gaps.columns, title="Time Gap to Leader", markers=True,labels={"value":"Seconds"})
        with c2:
            st.plotly_chart(fig_tt, use_container_width=True)
        
        
        ###Splits
        
        
#         df_splits = pd.DataFrame()
#         df_splits["To Go"] = ["3 Laps","2.5 Laps","2 Laps","1.5 Laps","1 Lap","0.5 Laps","15m"]
#         df_splits
        
            
            
            
            
        
        st.subheader("Splits (Pursuit Lines)")
        c1,c2=st.columns([1,3])
        with c1:
            df_splits
            df_times = df_splits.sum(axis=0)
            df_times=pd.DataFrame(df_times, columns=["3 lap time"])
            df_times = df_times[1:]
            st.subheader("3 lap times")
            df_times
        fig_tt = px.line(df_splits, x="Half", y = df_splits.columns, title="Splits",markers=True,labels={"value":"Seconds"})
        with c2:
            st.plotly_chart(fig_tt, use_container_width=True)
        
        
        c1,c2=st.columns(2)
        if Videos=="Yes":
            video_name=df_select["Video"].iloc[0]
            with c2:
                st.video(f"{video_name}")
        with c1:
            
            len(df_select["Draw"].unique())
            
            
            
            
            ## Getting Position at each pursuit line
            s = df_gaps.iloc[:,1:].stack().sort_values(ascending=True).groupby(level=0).cumcount() + 1
            s1 = (s.reset_index(1)
                .set_index(0, append=True)
                .unstack(1)
                .add_prefix("Position ")
                )
            s1.columns = s1.columns.get_level_values(1)
            
            
            df_gaps=df_gaps.join(s1)
            
            num_riders = len(s1.columns)
            
            for j in range(num_riders):
                name=df_select["Name"].unique()[j]
                
                
                
                
                rider_pos=[]
                
                for i in range(len(df_gaps)):
                    n = df_gaps.iloc[:,num_riders+1:].iloc[i]
                    pos=n[n==name].index[0]
                    to_go = df_gaps["To Go"][i]
                    gap = round(df_gaps[name][i],2)
                    rider_pos.append(int(pos.split(' ')[1]))
                df_gaps[f'{name} rank'] = rider_pos
            df_gaps = df_gaps.iloc[:,num_riders+1:]
            df_gaps
            

            
            
        
        st.markdown("---")
        st.header("Rider Analysis")
        df_riders=df_master
        c1,c2=st.columns([5,1])
        with c1:
            athletes = df_master["Name"].drop_duplicates().sort_values()
            riders = st.multiselect(
                "Select rider(s):",
                options= athletes
                ) 
        with c2:
            show_vids_2 = ["No","Yes"]
            Videos_2 = st.selectbox("Show Race Video?", show_vids_2, key="Show_Vids_2")
        if riders:
            df_riders = df_master.query(
        "Name == @riders"
        )
        
            df_riders=df_riders.sort_values(by=["Event","Name","Start time"])
            df_riders=df_riders.reset_index(drop=True)
            df_riders["Initials"]=df_riders["Name"].apply(lambda x: ''.join(i[0] for i in x.split()))
            #df_riders

    #         for Name in df_riders["Name"].unique():
    #             for Event in df_riders.loc[df_riders["Name"]==Name]["Event"].unique():
    #                 for Round in df_riders.loc[(df_riders["Name"]==Name)]["Round"].unique():
    #                     for Heat in df_riders.loc[df_riders["Name"]==Name]["Heat"].unique():
    #                         st.write(Name+" "+Event+" "+Round+" "+str(Heat))
            tags=[]

            Name=df_riders["Name"][0]
            Event=df_riders["Event"][0]
            Round=df_riders["Round"][0]
            Heat=df_riders["Heat"][0]

            tags.append(df_riders["Initials"][0]+" "+df_riders["Event"][0]+" "+df_riders["Round"][0]+" H"+str(df_riders["Heat"][0]))
            count=0
            tag_count=0
            start=df_riders["Start time"][0]
            videos=[df_riders["Video"][0]]
            times=[df_riders["Start time"][0]-start]
            df_riders
            df_worm=pd.DataFrame()
            df_worm["To Go"]=["3 Laps","2.5 Laps","2 Laps","1.5 Laps","1 Lap","0.5 Laps","15m"]
            df_worm
            for i in range(1,len(df_riders)):
                if count<6:
                    times.append(df_riders["Start time"][i]-start)
                    count+=1
                else:
                    tags.append(df_riders["Initials"][i]+" "+df_riders["Event"][i]+" "+df_riders["Round"][i]+" H"+str(df_riders["Heat"][i]))

                    df_worm[tags[tag_count]]=times
                    count=0
                    tag_count+=1
                    times=[]
                    start = df_riders["Start time"][i]
                    times.append(df_riders["Start time"][i]-start)
                    videos.append(df_riders["Video"][i])
            df_worm[tags[tag_count]]=times
            
            df_worm
            
            fig_worm = px.line(df_worm, x="To Go", y = df_worm.columns, title="Worms",markers=True,labels={"value":"Seconds"})

            st.plotly_chart(fig_worm, use_container_width=True)




            df_split=pd.DataFrame()
            df_split["Half"] = [1,2,3,4,5,6]

            for col in df_worm.columns[1:]:
                x=[]
                for i in range(1,7):
                    x.append(df_worm[col][i]-df_worm[col][i-1])
                df_split[col]=x
                    
            df_split
            
            
            fig_splits = px.line(df_split, x="Half", y = df_split.columns, title="Splits",markers=True,labels={"value":"Seconds"})

            st.plotly_chart(fig_splits, use_container_width=True)
            
            if Videos_2=="Yes":
                count=0
                for i in range(len(videos)):
                    c1,c2=st.columns([1,2])
                    with c1:
                        st.subheader(df_riders["Name"][count])
                        st.subheader(df_riders["Event"][count]+" "+df_riders["Round"][count]+" H"+str(df_riders["Heat"][count]))
                        st.subheader("Half Lap Splits")
                        df_split[["Half",df_split.columns[i+1]]]
                        st.subheader("Running Time")
                        df_worm[["To Go",df_worm.columns[i+1]]]
                        count+=7
                        
                    with c2:
                        video_name=videos[i]
                        st.video(f"{video_name}")
                    st.markdown('---')
                            
                        
                    
                        
        


        #####################################   WTS Starts stuff   #############################################################
            
    elif racetype == "WTS Starts":
        df_master = pd.read_excel(f'pages/video_analysis/WTS_starts.xlsx')
        for i in range(len(df_master)):
            df_master["Date"][i] = df_master["Date"][i].date()
        df_small = df_master.drop(columns=["Back","Forward","Green","PL",62.5,125,187.5,250,312.5,375,437.5,500])
        df_small
        c1,c2,c3=st.columns(3)
        
        with c1:
            riders = st.multiselect(
            "Select rider(s):",
            options=df_master["Name"].unique()
            ) 
            if riders:
                df_small = df_small.query(
            "Name == @riders"
            )
        with c2:
            dates = st.multiselect(
            "Select date(s):",
            options=df_small["Date"].unique()
            )
            if dates:
                df_small = df_small.query(
            "Date == @dates"
            )
        with c3:
            show_vids = ["No","Yes"]
            Videos = st.selectbox("Show Race Videos?", show_vids, key="Show_Vids")


        if len(riders) !=0:
            df_combine = pd.DataFrame()
            for i in range(len(riders)):
                col_1,col_2=st.columns(2)
                with col_1:
                    df_temp = df_small.loc[df_master['Name'] == riders[i]]
                    df_combine = pd.concat([df_combine, df_temp], axis=0)
                    
                    #df_small=df_small.reset_index(drop="True")
            df_combine = df_combine.reset_index(drop="True")
            
            df_combine
            
            df_splits = pd.DataFrame()
            df_splits["Mark"] = ["RT","Q1","Q2","Q3","Q4","Q5","Q6","Q7","Q8"]
            for i in range(len(df_combine)):
                var = str(i+1)+" " +str(df_combine["Name"].iloc[i]) + " " + str(df_combine["Date"].iloc[i]) + " Set " +str(df_combine["Set"].iloc[i])+" Rep " +str(df_combine["Rep"].iloc[i]) + " " +str(df_combine["Team/Solo"].iloc[i])
                df_splits[f"{var}"]=df_combine.iloc[i][8:17].values

            
            fig_tt = px.line(df_splits, x="Mark", y = df_splits.columns, title="Reaction Time + Quarter Splits")

            st.plotly_chart(fig_tt, use_container_width=True)
            #c1,c2=st.columns(2)
            
            if Videos == "Yes":
                for i in range(len(df_combine)):
                    if pd.isnull(df_combine["Video"].iloc[i]):
                        pass
                    else:
                        c1,c2=st.columns(2)
                        video_name = df_combine["Video"].iloc[i]
                        with c1:
                            st.header(df_combine["Name"].iloc[i])
                            st.subheader(df_combine["Date"].iloc[i])
                            st.subheader("Set "+str(df_combine["Set"].iloc[i])+ ", Rep " +str(df_combine["Rep"].iloc[i]))
                            st.subheader(df_combine["Team/Solo"].iloc[i])
                            st.subheader("Position "+str(df_combine["Pos"].iloc[i]))
                            st.subheader("Gear "+str(df_combine["Gear"].iloc[i]))
                            st.write("Reaction Time = "+str(round(df_combine["RT"].iloc[i],3)) + " Seconds")
                            st.write("First Quarter in = "+str(round(df_combine["Q1"].iloc[i],3)) + " Seconds, with a Moving Time of "+str(round(df_combine["Q1_MT"].iloc[i],3)) + " Seconds")
                            if pd.isnull(df_combine["Q2"].iloc[i])==False:
                                st.write("Second Quarter in = "+str(round(df_combine["Q2"].iloc[i],3)) + " Seconds, giving a split of "+str(round(df_combine["H1"].iloc[i],3))+" with a Moving Time of "+str(round(df_combine["H1_MT"].iloc[i],3)) + " Seconds")
                            if pd.isnull(df_combine["Q3"].iloc[i])==False:
                                st.write("Third Quarter in = "+str(round(df_combine["Q3"].iloc[i],3)) + " Seconds")
                            if pd.isnull(df_combine["Q4"].iloc[i])==False:
                                st.write("Fourth Quarter in = "+str(round(df_combine["Q4"].iloc[i],3)) + " Seconds, giving a split of "+str(round(df_combine["H2"].iloc[i],3))+" with a Moving Time of "+str(round(df_combine["Lap_MT"].iloc[i],3)) + " Seconds")
                                

                        with c2:
                            st.video(f"{video_name}")
                        st.markdown("---")





###################################################### Men's Individual Pursuit #############################################                 
                    
    if racetype == "Men's IP":
        df_master = pd.read_excel(f'pages/video_analysis/IP_Master_Men.xlsx')
        df_master = df_master.sort_values(["Save_Date","Title"], ascending=False)
        df_small = df_master.drop(columns=["Save_Date","Action","Video"])
        
        c1,c2=st.columns(2)
        with c1:
            selections = st.multiselect(
            "Select past effort(s):",
            options=df_master["Title"].unique()
            ) 
        with c2:
            show_vids = ["No","Yes"]
            Videos = st.selectbox("Show Race Videos?", show_vids, key="Show_Vids")


        if len(selections) !=0:
            df_combine = pd.DataFrame()
            for i in range(len(selections)):
                col_1,col_2=st.columns(2)
                with col_1:
                    df_temp = df_master.loc[df_master['Title'] == selections[i]]
                    df_combine = pd.concat([df_combine, df_temp], axis=0)
                    df_small = df_temp.drop(columns=["Save_Date","Video"])
                    df_small=df_small.reset_index(drop="True")
                  
                       
                        


                    df_main = df_small.drop(columns=["Action"])
                    df_main
                with col_2:
                    average = df_small.Split.iloc[4:].mean()
                    fig = px.bar(df_temp, x='Distance', y='Avg_Speed',hover_data=[df_temp.Split, df_temp.Avg_Speed])
                    
                    fig.update_layout(
                    title={
                        'text': df_temp.Title.iloc[0],
                        'y':0.9,
                        'x':0.5,
                        'xanchor': 'center',
                        'yanchor': 'top',
                        'font':dict(size=25)})
                    fig.add_hline(y=62.5*3.6/average, line_dash="dash",line_color="yellow",annotation_text="Avg after first lap = " +str(round(average*4,2)))
                    yaxis_min = min(df_temp["Avg_Speed"][1:])-1
                    yaxis_max = max(df_temp["Avg_Speed"])+1
                    fig.update_layout(yaxis_range=[yaxis_min,yaxis_max])
                    st.plotly_chart(fig, use_container_width=True)
                c1,c2=st.columns(2)
                with c1:

                    
                    
                    st.subheader("Start Splits")
                    df_start=pd.DataFrame(df_small["Distance"][0:4])
                    df_start["Split"]=df_small["Split"][0:4]
                    df_start["Total"]=df_small["Split"][0:4].cumsum()
                    df_start
                    
                    st.subheader("Lap Splits")
                    df_laps=pd.DataFrame(["Lap 1","Lap 2","Lap 3","Lap 4","Lap 5","Lap 6","Lap 7","Lap 8","Lap 9","Lap 10","Lap 11","Lap 12","Lap 13","Lap 14","Lap 15","Lap 16",])
                    df_laps.columns=["Distance"]
                    lap_split = [sum(df_small["Split"][0:4]),sum(df_small["Split"][4:8]),sum(df_small["Split"][8:12]),sum(df_small["Split"][12:16]),sum(df_small["Split"][16:20]),sum(df_small["Split"][20:24]),sum(df_small["Split"][24:28]),sum(df_small["Split"][28:32]),sum(df_small["Split"][32:36]),sum(df_small["Split"][36:40]),sum(df_small["Split"][40:44]),sum(df_small["Split"][44:48]),sum(df_small["Split"][48:52]),sum(df_small["Split"][52:56]),sum(df_small["Split"][56:60]),sum(df_small["Split"][60:64])]
                    df_laps["Split"]=lap_split
                    df_laps["Total"]=df_laps["Split"].cumsum()
                    df_laps['Total'] = pd.to_datetime(df_laps['Total'], unit='s').dt.strftime('%M:%S.%f')
                    df_laps
                    
                    st.subheader("Kilo Splits")
                    df_kilos=pd.DataFrame(["1k","2k","3k","4k"])
                    df_kilos.columns=["Distance"]
                    kilo_split = [sum(df_small["Split"][0:16]),sum(df_small["Split"][16:32]),sum(df_small["Split"][32:48]),sum(df_small["Split"][48:64])]
                    df_kilos["Split"]=kilo_split
                    df_kilos["Total"]=df_kilos["Split"].cumsum()
                    df_kilos['Total'] = pd.to_datetime(df_kilos['Total'], unit='s').dt.strftime('%M:%S.%f')
                    df_kilos
                if Videos == "Yes":
                    with c2:
                        if pd.isnull(df_temp["Video"].iloc[0]):
                            st.header("No video available")
                        else:
                            video_name = df_temp["Video"].iloc[0]
                            st.header(df_temp["Title"].iloc[0])
   
                            st.video(f"{video_name}")
                st.markdown("---")



            col_one, col_two, col_three, col_four = st.columns(4)
            
            with col_one:
           
                fig_tt = px.line(df_combine, x="Distance", y = "Avg_Speed", title="Comparison",color="Title",markers="Front")
                
            st.plotly_chart(fig_tt, use_container_width=True)


        st.markdown("---")            
        st.header('View, edit and upload a new effort')

#         with open('pages/TP_demo.xlsx', "rb") as template_file:
#                 template_byte = template_file.read()



#         st.download_button(label="Click to Download Template File",
#                             data=template_byte,
#                             file_name="template.xlsx"
#                           )

        uploaded_file = st.file_uploader("Choose a file",key="uploader_MIP")

#         if uploaded_file is not None:
#             st.markdown("---")

#             st.header('View, edit and upload a new effort')


#         uploaded_file = st.file_uploader("Choose a file",key="uploader")

        if uploaded_file is not None:
            st.markdown("---")

            st.header("Editor")
            df_full = pd.read_excel(uploaded_file)
            df_full['Position'] = df_full['Position'].apply(
    lambda t: t.hour * 3600 + t.minute * 60 + t.second + t.microsecond / 1_000_000
)
            df_full.drop(['Duration'],
           axis='columns', inplace=True)
            df_full
            c1,c2,c3=st.columns(3)
            with c1:
                start=st.number_input("Start Row (inclusive)", value=0)
            with c2:
                end=st.number_input("End Row (inclusive)", value=start+64)+1
            
            
            df=df_full[start:end]
#             df=df.sort_values("Start time", ascending=True)
            
            col_one, col_two, col_three = st.columns(3)
            with col_one:
                rider = st.text_input("Select Rider:")

            
            splits=[0]
            
            speeds=[0]
            r=0
            df["Time"] = df["Position"] - df["Position"].iloc[0]
            markers = len(df)
            df["Distance"] = np.linspace(0, 62.5*(markers-1), num=markers)
            df=df.reset_index(drop=True)
         

            #df = df.dropna(axis=0, subset=['Time'])

            with col_two:
                
                schedule = round(st.number_input("Schedule:", min_value=0.00, max_value=None,value=14.3),2)
                Title = st.text_input("Plot Title:")


            with col_three:
                
                for i in range(len(df)-1):
                    splits.append(round(df.Time[i+1]-df.Time[i],3))
                    speeds.append(round((df.Distance[i+1]-df.Distance[i])*3.6/splits[i+1],2))
                    

                df["Avg_Speed"]=speeds
                df["Split"]=splits
      
                df.rename(columns = {'Name':'Action'}, inplace = True)
                df.drop(index=df.index[0], axis=0, inplace=True)
                df = df.loc[:, ~df.columns.str.match(r'^Unnamed') & df.notna().any()]
                st.write(df)


            fig = px.bar(df, x='Distance', y='Avg_Speed',hover_data=[df.Split, df.Avg_Speed])
   
            fig.update_layout(
            title={
                'text': Title,
                'y':0.9,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top',
                'font':dict(size=25)})
            fig.add_hline(y=250*3.6/schedule, line_dash="dash",line_color="white",annotation_text="Schedule = " +str(schedule))
            st.plotly_chart(fig, use_container_width=True)






            #master_path=st.text_input("Add path to master file:",key="prompt")
            if st.button("Append this effort to master",key="upload"):




                df_save=df
                df_save.drop(['Position'],
           axis='columns', inplace=True)
                df_save.insert(0, 'Save_Date', datetime.date.today())
                df_save["Save_Date"] = pd.to_datetime(df_save['Save_Date'])
                df_save.insert(0, 'Title', Title)
                df = pd.concat([df_master, df_save], axis=0)
                df

                ##Testing downloader


                # buffer to use for excel writer
                buffer = io.BytesIO()



                @st.cache_data
                def convert_to_csv(df):
                    # IMPORTANT: Cache the conversion to prevent computation on every rerun
                    return df.to_csv(index=False).encode('utf-8')

                csv = convert_to_csv(df)

                # display the dataframe on streamlit app
        #         st.write(df)

                # download button 1 to download dataframe as csv
                download1 = st.download_button(
                    label="Download new Master as CSV",
                    data=csv,
                    file_name='IP_Master_Men.csv',
                    mime='text/csv'
                )

                # download button 2 to download dataframe as xlsx
                with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                    # Write each dataframe to a different worksheet.
                    df.to_excel(writer, sheet_name='Sheet1', index=False)
                    # Close the Pandas Excel writer and output the Excel file to the buffer
                    writer.close()

                    download2 = st.download_button(
                        label="Download new Master as Excel",
                        data=buffer,
                        file_name='IP_Master_Men.xlsx',
                        mime='application/vnd.ms-excel'
                    )                
                    

           ###################################################### Women's Individual Pursuit #############################################                 
                    
    if racetype == "Women's IP":
        df_master = pd.read_excel(f'pages/video_analysis/IP_Master_Women.xlsx')
        df_master = df_master.sort_values(["Save_Date","Title"], ascending=False)
        df_small = df_master.drop(columns=["Save_Date","Action","Video"])
        
        c1,c2=st.columns(2)
        with c1:
            selections = st.multiselect(
            "Select past effort(s):",
            options=df_master["Title"].unique()
            ) 
        with c2:
            show_vids = ["No","Yes"]
            Videos = st.selectbox("Show Race Videos?", show_vids, key="Show_Vids")


        if len(selections) !=0:
            df_combine = pd.DataFrame()
            for i in range(len(selections)):
                col_1,col_2=st.columns(2)
                with col_1:
                    df_temp = df_master.loc[df_master['Title'] == selections[i]]
                    df_combine = pd.concat([df_combine, df_temp], axis=0)
                    df_small = df_temp.drop(columns=["Save_Date","Video"])
                    df_small=df_small.reset_index(drop="True")
                  
                       
                        


                    df_main = df_small.drop(columns=["Action"])
                    df_main
                with col_2:
                    average = df_small.Split.iloc[4:].mean()
                    fig = px.bar(df_temp, x='Distance', y='Avg_Speed',hover_data=[df_temp.Split, df_temp.Avg_Speed])
                    
                    fig.update_layout(
                    title={
                        'text': df_temp.Title.iloc[0],
                        'y':0.9,
                        'x':0.5,
                        'xanchor': 'center',
                        'yanchor': 'top',
                        'font':dict(size=25)})
                    fig.add_hline(y=62.5*3.6/average, line_dash="dash",line_color="yellow",annotation_text="Avg after first lap = " +str(round(average*4,2)))
                    yaxis_min = min(df_temp["Avg_Speed"][1:])-1
                    yaxis_max = max(df_temp["Avg_Speed"])+1
                    fig.update_layout(yaxis_range=[yaxis_min,yaxis_max])
                    st.plotly_chart(fig, use_container_width=True)
                c1,c2=st.columns(2)
                with c1:

                    
                    
                    st.subheader("Start Splits")
                    df_start=pd.DataFrame(df_small["Distance"][0:4])
                    df_start["Split"]=df_small["Split"][0:4]
                    df_start["Total"]=df_small["Split"][0:4].cumsum()
                    df_start
                    
                    st.subheader("Lap Splits")
                    df_laps=pd.DataFrame(["Lap 1","Lap 2","Lap 3","Lap 4","Lap 5","Lap 6","Lap 7","Lap 8","Lap 9","Lap 10","Lap 11","Lap 12","Lap 13","Lap 14","Lap 15","Lap 16",])
                    df_laps.columns=["Distance"]
                    lap_split = [sum(df_small["Split"][0:4]),sum(df_small["Split"][4:8]),sum(df_small["Split"][8:12]),sum(df_small["Split"][12:16]),sum(df_small["Split"][16:20]),sum(df_small["Split"][20:24]),sum(df_small["Split"][24:28]),sum(df_small["Split"][28:32]),sum(df_small["Split"][32:36]),sum(df_small["Split"][36:40]),sum(df_small["Split"][40:44]),sum(df_small["Split"][44:48]),sum(df_small["Split"][48:52]),sum(df_small["Split"][52:56]),sum(df_small["Split"][56:60]),sum(df_small["Split"][60:64])]
                    df_laps["Split"]=lap_split
                    df_laps["Total"]=df_laps["Split"].cumsum()
                    df_laps['Total'] = pd.to_datetime(df_laps['Total'], unit='s').dt.strftime('%M:%S.%f')
                    df_laps
                    
                    st.subheader("Kilo Splits")
                    df_kilos=pd.DataFrame(["1k","2k","3k","4k"])
                    df_kilos.columns=["Distance"]
                    
                    kilo_split = [sum(df_small["Split"][0:16]),sum(df_small["Split"][16:32]),sum(df_small["Split"][32:48]),sum(df_small["Split"][48:64])]
                    
                    df_kilos["Split"]=kilo_split
                    
                    df_kilos["Total"]=df_kilos["Split"].cumsum()
                    df_kilos['Total'] = pd.to_datetime(df_kilos['Total'], unit='s').dt.strftime('%M:%S.%f')
                    df_kilos
                if Videos == "Yes":
                    with c2:
                        if pd.isnull(df_temp["Video"].iloc[0]):
                            st.header("No video available")
                        else:
                            video_name = df_temp["Video"].iloc[0]
                            st.header(df_temp["Title"].iloc[0])
   
                            st.video(f"{video_name}")
                st.markdown("---")



            col_one, col_two, col_three, col_four = st.columns(4)
            with col_one:
                
                fig_tt = px.line(df_combine, x="Distance", y = "Avg_Speed", title="Comparison",color="Title",markers="Front")

            st.plotly_chart(fig_tt, use_container_width=True)

#             if len(selections) ==2:

#                 df_zero = df_combine
#                 df_zero = df_zero.reset_index(drop=True)
#                 length = df_zero.Title.value_counts()[selections[0]]
#                 for j in range(length,len(selections)*length):
#                     df_zero.Split[j]=df_zero.Split[j]-df_zero.Split[j-length]
#                     df_zero.Split[j-length]=0



#                 fig_zero = px.line(df_zero, x="Distance", y = "Split", title="Zero",color="Title",markers="Front")
#                 st.plotly_chart(fig_zero, use_container_width=True)
               
#                 fig_worm = px.line(df_zero, x="Distance", y = "Time", title="Worm",color="Title",markers="Front")

#                 st.plotly_chart(fig_worm, use_container_width=True)

#             elif len(selections) >2:

#                 df_zero = df_combine
#                 df_zero = df_zero.reset_index(drop=True)
#                 length = df_zero.Title.value_counts()[selections[0]]
#                 for j in range(length,len(selections)*length):
#                     df_zero.Split[j]=df_zero.Split[j]-df_zero.Split[j-length]
#                     df_zero.Split[j-length]=0




#                 if Names=="Yes":
#                     fig_worm = px.line(df_zero, x="Distance", y = "Time", title="Worm",color="Title",text="Front",markers="Front")
#                     fig_worm.update_traces(textposition='top center')
#                 if Names=="No":
#                     fig_worm = px.line(df_zero, x="Distance", y = "Time", title="Worm",color="Title",markers="Front")

#                 st.plotly_chart(fig_worm, use_container_width=True)






        st.markdown("---")            
        st.header('View, edit and upload a new effort')


        uploaded_file = st.file_uploader("Choose a file",key="uploader")

        if uploaded_file is not None:
            st.markdown("---")

            st.header("Editor")
            df_full = pd.read_excel(uploaded_file)
            df_full['Position'] = df_full['Position'].apply(
    lambda t: t.hour * 3600 + t.minute * 60 + t.second + t.microsecond / 1_000_000
)
            df_full.drop(['Duration'],
           axis='columns', inplace=True)
            df_full
            c1,c2,c3=st.columns(3)
            with c1:
                start=st.number_input("Start Row (inclusive)", value=0)
            with c2:
                end=st.number_input("End Row (inclusive)", value=start+64)+1
            
            
            df=df_full[start:end]
#             df=df.sort_values("Start time", ascending=True)
            
            col_one, col_two, col_three = st.columns(3)
            with col_one:
                rider = st.text_input("Select Rider:")

            
            splits=[0]
            
            speeds=[0]
            r=0
            df["Time"] = df["Position"] - df["Position"].iloc[0]
            markers = len(df)
            df["Distance"] = np.linspace(0, 62.5*(markers-1), num=markers)
            df=df.reset_index(drop=True)
         

            #df = df.dropna(axis=0, subset=['Time'])

            with col_two:
                
                schedule = round(st.number_input("Schedule:", min_value=0.00, max_value=None,value=14.3),2)
                Title = st.text_input("Plot Title:")


            with col_three:
                
                for i in range(len(df)-1):
                    splits.append(round(df.Time[i+1]-df.Time[i],3))
                    speeds.append(round((df.Distance[i+1]-df.Distance[i])*3.6/splits[i+1],2))
                    

                df["Avg_Speed"]=speeds
                df["Split"]=splits
      
                df.rename(columns = {'Name':'Action'}, inplace = True)
                df.drop(index=df.index[0], axis=0, inplace=True)
                df = df.loc[:, ~df.columns.str.match(r'^Unnamed') & df.notna().any()]
                st.write(df)


            fig = px.bar(df, x='Distance', y='Avg_Speed',hover_data=[df.Split, df.Avg_Speed])
   
            fig.update_layout(
            title={
                'text': Title,
                'y':0.9,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top',
                'font':dict(size=25)})
            fig.add_hline(y=250*3.6/schedule, line_dash="dash",line_color="white",annotation_text="Schedule = " +str(schedule))
            st.plotly_chart(fig, use_container_width=True)






            #master_path=st.text_input("Add path to master file:",key="prompt")
            if st.button("Append this effort to master",key="upload"):




                df_save=df
                df_save.drop(['Position'],
           axis='columns', inplace=True)
                df_save.insert(0, 'Save_Date', datetime.date.today())
                df_save["Save_Date"] = pd.to_datetime(df_save['Save_Date'])
                df_save.insert(0, 'Title', Title)
                df = pd.concat([df_master, df_save], axis=0)
                df

                ##Testing downloader


                # buffer to use for excel writer
                buffer = io.BytesIO()



                @st.cache_data
                def convert_to_csv(df):
                    # IMPORTANT: Cache the conversion to prevent computation on every rerun
                    return df.to_csv(index=False).encode('utf-8')

                csv = convert_to_csv(df)

                # display the dataframe on streamlit app
        #         st.write(df)

                # download button 1 to download dataframe as csv
                download1 = st.download_button(
                    label="Download new Master as CSV",
                    data=csv,
                    file_name='IP_Master_Women.csv',
                    mime='text/csv'
                )

                # download button 2 to download dataframe as xlsx
                with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                    # Write each dataframe to a different worksheet.
                    df.to_excel(writer, sheet_name='Sheet1', index=False)
                    # Close the Pandas Excel writer and output the Excel file to the buffer
                    writer.close()

                    download2 = st.download_button(
                        label="Download new Master as Excel",
                        data=buffer,
                        file_name='IP_Master_Women.xlsx',
                        mime='application/vnd.ms-excel'
                    )                
                    
    ################################################ Women's Team Sprint ########################################
    
    if racetype == "Women's Team Sprint":
        
        st.markdown("---")            
        df_master = pd.read_excel(f'pages/video_analysis/WTS_Master_Women.xlsx')
        #df_master = pd.read_excel("C:\\Users\\SamB\\CNZPD\\pages\\video_analysis\\WTS_Master_Women.xlsx")
        st.header("Race Viewer")
        c1,c2=st.columns(2)
        
        with c1:
            selections = st.multiselect(
            "Select past effort(s):",
            options=df_master["Title"].sort_values(ascending=False).unique()
            ) 
        with c2:
            show_vids = ["No","Yes"]
            Videos = st.selectbox("Show Race Videos?", show_vids, key="Show_Vids")
        if len(selections) !=0:
            st.markdown("[Jump to Full Summary](#summary)", unsafe_allow_html=True)
            df_combine = pd.DataFrame()
            for i in range(len(selections)):
                checkboxid+=1
                df_temp = df_master.loc[df_master['Title'] == selections[i]].reset_index(drop=True)
                
                
                df_table = pd.DataFrame([1,2,3],columns=["Position"])
                df_table.insert(0,"Event",df_temp["Title"][0:3])
                df_table["Rider"]=df_temp["Riders"][0:3]
                df_table["Gear"]=df_temp["Gears"][0:3]
                
                ind1=df_temp.index[df_temp['Row'] == "Rider 1 Forward"].tolist()[0]
                ind2=df_temp.index[df_temp['Row'] == "Rider 2 Forward"].tolist()[0]
                ind3=df_temp.index[df_temp['Row'] == "Rider 3 Forward"].tolist()[0]
                indstart=df_temp.index[df_temp['Row'] == "Start"].tolist()[0]
                start = df_temp["Start time"][indstart]
                react1 = round(df_temp["Start time"][ind1]-start,2)
                react2 = round(df_temp["Start time"][ind2]-start,2)
                react3 = round(df_temp["Start time"][ind3]-start,2)
                
                
                df_table["RT"]=[react1,react2,react3]
                df_table["62.5"]=[df_temp["Start time"][4]-start,df_temp["Start time"][5]-start,df_temp["Start time"][6]-start]
                
                df_table["125"]=[df_temp["Start time"][7]-df_temp["Start time"][4],df_temp["Start time"][8]-df_temp["Start time"][5],df_temp["Start time"][9]-df_temp["Start time"][6]]
                
                df_table["187.5"]=[df_temp["Start time"][10]-df_temp["Start time"][7],df_temp["Start time"][11]-df_temp["Start time"][8],df_temp["Start time"][12]-df_temp["Start time"][9]]
                
                df_table["250"]=[df_temp["Start time"][13]-df_temp["Start time"][10],df_temp["Start time"][14]-df_temp["Start time"][11],df_temp["Start time"][15]-df_temp["Start time"][12]]
                df_table["Lap 1"]=[df_temp["Start time"][13]-start,df_temp["Start time"][14]-start,df_temp["Start time"][15]-start]
                
                
                df_table["Gap 1"]= [0.0,df_table["Lap 1"][1]-df_table["Lap 1"][0],df_table["Lap 1"][2]-df_table["Lap 1"][1]]
                
                df_table["312.5"]=[0,df_temp["Start time"][16]-df_temp["Start time"][14],df_temp["Start time"][17]-df_temp["Start time"][15]]
                
                df_table["375"]=[0,df_temp["Start time"][18]-df_temp["Start time"][16],df_temp["Start time"][19]-df_temp["Start time"][17]]
                
                df_table["437.5"]=[0,df_temp["Start time"][20]-df_temp["Start time"][18],df_temp["Start time"][21]-df_temp["Start time"][19]]
                
                df_table["500"]=[0,df_temp["Start time"][22]-df_temp["Start time"][20],df_temp["Start time"][23]-df_temp["Start time"][21]]
                df_table["Lap 2"]=[0,df_temp["Start time"][22]-df_temp["Start time"][14],df_temp["Start time"][23]-df_temp["Start time"][15]]
                df_table["500m Time"] = [0,df_table["Lap 1"][1]+df_table["Lap 2"][1],df_table["Lap 1"][2]+df_table["Lap 2"][2]]
                df_table["Gap 2"]= [0,0,df_table["Lap 2"][2]-df_table["Lap 2"][1] + df_table["Gap 1"][2]]
                
                df_table["562.5"] = [0,0,df_temp["Start time"][24]-df_temp["Start time"][23]]
                df_table["625"] = [0,0,df_temp["Start time"][25]-df_temp["Start time"][24]]
                df_table["687.5"] = [0,0,df_temp["Start time"][26]-df_temp["Start time"][25]]
                df_table["750"] = [0,0,df_temp["Start time"][27]-df_temp["Start time"][26]]
                
                df_table["Lap 3"] = [0,0,df_temp["Start time"][27]-df_temp["Start time"][23]]
                df_table["1"] = [df_table["Lap 1"][0],0,0]
                df_table["2"] = [0,df_table["Lap 2"][1]+df_table["Gap 1"][1],0]
                df_table["3"] = [0,0,df_table["Lap 3"][2]+df_table["Gap 2"][2]]
                df_table["Time"] = [0,0,df_temp["Start time"][27]-start]
                df_table_small = df_table[["Event", "Position", "Rider", "RT", "Lap 1", "Lap 2", "Lap 3", "Time"]].copy()
                df_table_small = df_table_small.rename(columns={"Lap 1": "Lap1", "Lap 2": "Lap2", "Lap 3": "Lap3", "Time": "time"})
                st.header(selections[i])
                df_table
                st.subheader("Compact Summary")
                df_table_small
                
                gap1_2_1 = round(df_table["62.5"][1]-df_table["62.5"][0],2)
                gap1_2_2 = round(df_table["125"][1]-df_table["125"][0] + gap1_2_1,2)
                gap1_2_3 = round(df_table["187.5"][1]-df_table["187.5"][0] + gap1_2_2,2)
                gap1_2_4 = round(df_table["250"][1]-df_table["250"][0] + gap1_2_3,2)
                
                gap2_3_1 = round(df_table["62.5"][2]-df_table["62.5"][1],2)
                gap2_3_2 = round(df_table["125"][2]-df_table["125"][1]+gap2_3_1,2)
                gap2_3_3 = round(df_table["187.5"][2]-df_table["187.5"][1]+gap2_3_2,2)
                gap2_3_4 = round(df_table["250"][2]-df_table["250"][1]+gap2_3_3,2)
                gap2_3_5 = round(df_table["312.5"][2]-df_table["312.5"][1]+gap2_3_4,2)
                gap2_3_6 = round(df_table["375"][2]-df_table["375"][1]+gap2_3_5,2)
                gap2_3_7 = round(df_table["437.5"][2]-df_table["437.5"][1]+gap2_3_6,2)
                gap2_3_8 = round(df_table["500"][2]-df_table["500"][1]+gap2_3_7,2)
                
                gaps1_2=[gap1_2_1,gap1_2_2,gap1_2_3,gap1_2_4,0,0,0,0]
                gaps2_3=[gap2_3_1,gap2_3_2,gap2_3_3,gap2_3_4,gap2_3_5,gap2_3_6,gap2_3_7,gap2_3_8]
                df_gap = pd.DataFrame(gaps1_2)
                df_gap.rename(columns={ df_gap.columns[0]: "Gap1_2" }, inplace = True)
                df_gap["Gap2_3"]=gaps2_3
                
              
            
                f1 = go.Figure(
                data = [
                    go.Scatter(y=gaps1_2[0:4], x=["Q1","Q2","Q3","Q4"], name="Rider 2 to 1"),
                    go.Scatter(x=["Q1","Q2","Q3","Q4","Q5","Q6","Q7","Q8"], y=gaps2_3, name="Rider 3 to 2"),
                ],
                layout = {"xaxis": {"title": "Quarters"}, "yaxis": {"title": "Seconds"}, "title": "Gaps by Quarter"}
                )
                
                st.plotly_chart(f1, use_container_width=True)
                if i==0:
                    df_table_all=df_table
                    df_table_small_all = df_table_small
                else:
                    df_table_all=pd.concat([df_table_all,df_table])
                    df_table_small_all = pd.concat([df_table_small_all, df_table_small], ignore_index=True)
                c1,c2=st.columns(2)
                with c2:
                    if Videos == "Yes":
                    
                        if pd.isnull(df_temp["Video"].iloc[0]):
                            st.header("No video available")
                        else:
                            video_name = df_temp["Video"].iloc[0]
                            st.header(df_temp["Title"].iloc[0])

                            st.video(f"{video_name}")
                
                st.markdown("---")
                
                
                teamsplits = [df_table["62.5"][0],df_table["125"][0],df_table["187.5"][0],df_table["250"][0],df_table["312.5"][1]+df_table["Gap 1"][1],df_table["375"][1],df_table["437.5"][1],df_table["500"][1],df_table["562.5"][2]+df_table["Gap 2"][2],df_table["625"][2],df_table["687.5"][2],df_table["750"][2]]
                
                teamspeeds = [round(3.6*62.5/i,2) for i in teamsplits]
                
                df_speeds = pd.DataFrame(teamspeeds)
                
                df_speeds["Title"] = selections[i]
                df_speeds["Marker"] = ["Q1","Q2","Q3","Q4","Q5","Q6","Q7","Q8","Q9","Q10","Q11","Q12"]
                df_speeds["Splits"] = teamsplits
                df_combine = pd.concat([df_combine, df_speeds], axis=0)
                
            st.header("Full Summary", anchor="summary")
            df = df_table_all
            df_filt = filter_dataframe(df, widget_key_prefix="full_summary")
            df_filt
            st.subheader("Compact Full Summary")
            df_small_filt = filter_dataframe(df_table_small_all, widget_key_prefix="compact_full_summary")
            df_small_filt
            
            buffer = io.BytesIO()
            @st.cache_data
            def convert_to_csv(df):
                # IMPORTANT: Cache the conversion to prevent computation on every rerun
                return df.to_csv(index=False).encode('utf-8')

            csv = convert_to_csv(df)

            # download button 1 to download dataframe as csv
            download1 = st.download_button(
                label="Download Summary as CSV",
                data=csv,
                file_name='WTS_summary.csv',
                mime='text/csv'
            )

            # download button 2 to download dataframe as xlsx
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                # Write each dataframe to a different worksheet.
                df_filt.to_excel(writer, sheet_name='Sheet1', index=False)
                # Close the Pandas Excel writer and output the Excel file to the buffer
                writer.close()

                download2 = st.download_button(
                    label="Download Summary as Excel",
                    data=buffer,
                    file_name='WTS_summary.xlsx',
                    mime='application/vnd.ms-excel'
                ) 

            compact_buffer = io.BytesIO()
            with pd.ExcelWriter(compact_buffer, engine='xlsxwriter') as writer:
                df_small_filt.to_excel(writer, sheet_name='Sheet1', index=False)
                writer.close()

                download3 = st.download_button(
                    label="Download Compact Summary as Excel",
                    data=compact_buffer,
                    file_name='WTS_compact_summary.xlsx',
                    mime='application/vnd.ms-excel'
                )
            
            df_combine.rename(columns={ df_combine.columns[0]: "Speed (km/h)" }, inplace = True)
            
            fig_comp = px.line(df_combine, x="Marker", y = "Speed (km/h)", title="Average Speed Comparison",color="Title",markers="Splits",labels = {
            "Marker":"Quarter"})

            st.plotly_chart(fig_comp, use_container_width=True)
            
            fig_comp_split = px.line(df_combine, x="Marker", y = "Splits", title="Split Comparison",color="Title",markers="Splits",labels = {
            "Marker":"Quarter"})

            st.plotly_chart(fig_comp_split, use_container_width=True)
        st.markdown('---')
        st.header("Editor")


        uploaded_file = st.file_uploader("Choose a file",key="uploader")

        if uploaded_file is not None:
            st.markdown("---")

            st.header("Editor")
            st.write("Initial df")
            df_full = pd.read_excel(uploaded_file)
            df_full['Position'] = df_full['Position'].apply(
    lambda t: t.hour * 3600 + t.minute * 60 + t.second + t.microsecond / 1_000_000
)
#             df_full=df_full.sort_values(by=["Start time"]).reset_index(drop=True)
            df_full.drop(['Duration'],
          axis='columns', inplace=True)
            
            
            c1,c2,c3=st.columns(3)
            with c1:
                df_full
                start=st.number_input("Start Row (inclusive)", value=0)
            with c2:
                df_check = pd.DataFrame(df_full.iloc[::28, :])
#                 df_check.drop(["Start time"],axis='columns', inplace=True)
                st.write("Checking we've got everything")
                df_check = df_check.loc[:, ~df_check.columns.str.match(r'^Unnamed') & df_check.notna().any()]
                df_check
                end=st.number_input("End Row (inclusive)", value=start+27)+1
            
            
            df=df_full[start:end]
#             df=df.sort_values("Start time", ascending=True)
            
            
            with c1:
                rider1 = st.text_input("Select Rider 1:")
                rider2 = st.text_input("Select Rider 2:")
                rider3 = st.text_input("Select Rider 3:")
            
            riders=[rider1,rider2,rider3]
            
            
            
            

            #df = df.dropna(axis=0, subset=['Time'])

            with c2:
                
               
                
                rider1gear = st.text_input("Select Rider 1 gear:")
                rider2gear = st.text_input("Select Rider 2 gear:")
                rider3gear = st.text_input("Select Rider 3 gear:")
                Title = st.text_input("Plot Title:")


            df["Riders"]="NA"
            df["Riders"].iloc[0]=rider1
            df["Riders"].iloc[1]=rider2
            df["Riders"].iloc[2]=rider3
            df["Gears"]=0.0
            df["Title"]=Title
            col = df.pop('Title')
            df.insert(0, col.name, col)
            df["Gears"].iloc[0]=rider1gear
            df["Gears"].iloc[1]=rider2gear
            df["Gears"].iloc[2]=rider3gear
            front=[rider1]
            splits=[0]
            del_speeds=[0]
            speeds=[0]
            r=0
            
   
           
            df = df.loc[:, ~df.columns.str.match(r'^Unnamed') & df.notna().any()]
            df=df.reset_index(drop=True)
            with c3:
                df
                ind1=df.index[df['Name'] == "Rider 1 Forward"].tolist()[0]
                ind2=df.index[df['Name'] == "Rider 2 Forward"].tolist()[0]
                ind3=df.index[df['Name'] == "Rider 3 Forward"].tolist()[0]
                indstart=df.index[df['Name'] == "Start"].tolist()[0]
                react1 = round(df["Position"][ind1]-df["Position"][indstart],2)
                react2 = round(df["Position"][ind2]-df["Position"][indstart],2)
                react3 = round(df["Position"][ind3]-df["Position"][indstart],2)
                st.write(f'Reaction time for rider 1 is {react1} seconds')
                st.write(f'Reaction time for rider 2 is {react2} seconds')
                st.write(f'Reaction time for rider 3 is {react3} seconds')

            
            #master_path=st.text_input("Add path to master file:",key="prompt")
            if st.button("Append this effort to master",key="upload"):




                df_save=df
                df_save = df_save.rename(columns={'Name': 'Row','Position':'Start time'})
                df_save.insert(0, 'Save_Date', datetime.date.today())
                df_save["Save_Date"] = pd.to_datetime(df_save['Save_Date'])
                df = pd.concat([df_master, df_save], axis=0)
                
                df

                ##Testing downloader


                # buffer to use for excel writer
                buffer = io.BytesIO()



                @st.cache_data
                def convert_to_csv(df):
                    # IMPORTANT: Cache the conversion to prevent computation on every rerun
                    return df.to_csv(index=False).encode('utf-8')

                csv = convert_to_csv(df)

                # display the dataframe on streamlit app
        #         st.write(df)

                # download button 1 to download dataframe as csv
                download1 = st.download_button(
                    label="Download new Master as CSV",
                    data=csv,
                    file_name='WTS_Master_Women.csv',
                    mime='text/csv'
                )

                # download button 2 to download dataframe as xlsx
                with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                    # Write each dataframe to a different worksheet.
                    df.to_excel(writer, sheet_name='Sheet1', index=False)
                    # Close the Pandas Excel writer and output the Excel file to the buffer
                    writer.close()

                    download2 = st.download_button(
                        label="Download new Master as Excel",
                        data=buffer,
                        file_name='WTS_Master_Women.xlsx',
                        mime='application/vnd.ms-excel'
                    )       
            
    ################################################ Men's Team Sprint ########################################
    
    if racetype == "Men's Team Sprint":
        
        st.markdown("---")            
        df_master = pd.read_excel(f'pages/video_analysis/MTS_Master_Men.xlsx')
        st.header("Race Viewer")
        c1,c2=st.columns(2)
        
        with c1:
            selections = st.multiselect(
            "Select past effort(s):",
            options=df_master["Title"].sort_values(ascending=False).unique()
            ) 
        with c2:
            show_vids = ["No","Yes"]
            Videos = st.selectbox("Show Race Videos?", show_vids, key="Show_Vids_MTS")
        if len(selections) !=0:
            st.markdown("[Jump to Full Summary](#summary)", unsafe_allow_html=True)
            df_combine = pd.DataFrame()
            for i in range(len(selections)):
                checkboxid+=1
                df_temp = df_master.loc[df_master['Title'] == selections[i]].reset_index(drop=True)
                
                
                df_table = pd.DataFrame([1,2,3],columns=["Position"])
                df_table.insert(0,"Event",df_temp["Title"][0:3])
                df_table["Rider"]=df_temp["Riders"][0:3]
                df_table["Gear"]=df_temp["Gears"][0:3]
                
                ind1=df_temp.index[df_temp['Row'] == "Rider 1 Forward"].tolist()[0]
                ind2=df_temp.index[df_temp['Row'] == "Rider 2 Forward"].tolist()[0]
                ind3=df_temp.index[df_temp['Row'] == "Rider 3 Forward"].tolist()[0]
                indstart=df_temp.index[df_temp['Row'] == "Start"].tolist()[0]
                start = df_temp["Start time"][indstart]
                react1 = round(df_temp["Start time"][ind1]-start,2)
                react2 = round(df_temp["Start time"][ind2]-start,2)
                react3 = round(df_temp["Start time"][ind3]-start,2)
                
                
                df_table["RT"]=[react1,react2,react3]
                df_table["62.5"]=[df_temp["Start time"][4]-start,df_temp["Start time"][5]-start,df_temp["Start time"][6]-start]
                
                df_table["125"]=[df_temp["Start time"][7]-df_temp["Start time"][4],df_temp["Start time"][8]-df_temp["Start time"][5],df_temp["Start time"][9]-df_temp["Start time"][6]]
                
                df_table["187.5"]=[df_temp["Start time"][10]-df_temp["Start time"][7],df_temp["Start time"][11]-df_temp["Start time"][8],df_temp["Start time"][12]-df_temp["Start time"][9]]
                
                df_table["250"]=[df_temp["Start time"][13]-df_temp["Start time"][10],df_temp["Start time"][14]-df_temp["Start time"][11],df_temp["Start time"][15]-df_temp["Start time"][12]]
                df_table["Lap 1"]=[df_temp["Start time"][13]-start,df_temp["Start time"][14]-start,df_temp["Start time"][15]-start]
                
                
                df_table["Gap 1"]= [0.0,df_table["Lap 1"][1]-df_table["Lap 1"][0],df_table["Lap 1"][2]-df_table["Lap 1"][1]]
                
                df_table["312.5"]=[0,df_temp["Start time"][16]-df_temp["Start time"][14],df_temp["Start time"][17]-df_temp["Start time"][15]]
                
                df_table["375"]=[0,df_temp["Start time"][18]-df_temp["Start time"][16],df_temp["Start time"][19]-df_temp["Start time"][17]]
                
                df_table["437.5"]=[0,df_temp["Start time"][20]-df_temp["Start time"][18],df_temp["Start time"][21]-df_temp["Start time"][19]]
                
                df_table["500"]=[0,df_temp["Start time"][22]-df_temp["Start time"][20],df_temp["Start time"][23]-df_temp["Start time"][21]]
                df_table["Lap 2"]=[0,df_temp["Start time"][22]-df_temp["Start time"][14],df_temp["Start time"][23]-df_temp["Start time"][15]]
                df_table["500m Time"] = [0,df_table["Lap 1"][1]+df_table["Lap 2"][1],df_table["Lap 1"][2]+df_table["Lap 2"][2]]
                df_table["Gap 2"]= [0,0,df_table["Lap 2"][2]-df_table["Lap 2"][1] + df_table["Gap 1"][2]]
                
                df_table["562.5"] = [0,0,df_temp["Start time"][24]-df_temp["Start time"][23]]
                df_table["625"] = [0,0,df_temp["Start time"][25]-df_temp["Start time"][24]]
                df_table["687.5"] = [0,0,df_temp["Start time"][26]-df_temp["Start time"][25]]
                df_table["750"] = [0,0,df_temp["Start time"][27]-df_temp["Start time"][26]]
                
                df_table["Lap 3"] = [0,0,df_temp["Start time"][27]-df_temp["Start time"][23]]
                df_table["1"] = [df_table["Lap 1"][0],0,0]
                df_table["2"] = [0,df_table["Lap 2"][1]+df_table["Gap 1"][1],0]
                df_table["3"] = [0,0,df_table["Lap 3"][2]+df_table["Gap 2"][2]]
                df_table["Time"] = [0,0,df_temp["Start time"][27]-start]
                df_table_small = df_table[["Event", "Position", "Rider", "RT", "Lap 1", "Lap 2", "Lap 3", "Time"]].copy()
                df_table_small = df_table_small.rename(columns={"Lap 1": "Lap1", "Lap 2": "Lap2", "Lap 3": "Lap3", "Time": "time"})
                st.header(selections[i])
                df_table
                st.subheader("Compact Summary")
                df_table_small
                
                gap1_2_1 = round(df_table["62.5"][1]-df_table["62.5"][0],2)
                gap1_2_2 = round(df_table["125"][1]-df_table["125"][0] + gap1_2_1,2)
                gap1_2_3 = round(df_table["187.5"][1]-df_table["187.5"][0] + gap1_2_2,2)
                gap1_2_4 = round(df_table["250"][1]-df_table["250"][0] + gap1_2_3,2)
                
                gap2_3_1 = round(df_table["62.5"][2]-df_table["62.5"][1],2)
                gap2_3_2 = round(df_table["125"][2]-df_table["125"][1]+gap2_3_1,2)
                gap2_3_3 = round(df_table["187.5"][2]-df_table["187.5"][1]+gap2_3_2,2)
                gap2_3_4 = round(df_table["250"][2]-df_table["250"][1]+gap2_3_3,2)
                gap2_3_5 = round(df_table["312.5"][2]-df_table["312.5"][1]+gap2_3_4,2)
                gap2_3_6 = round(df_table["375"][2]-df_table["375"][1]+gap2_3_5,2)
                gap2_3_7 = round(df_table["437.5"][2]-df_table["437.5"][1]+gap2_3_6,2)
                gap2_3_8 = round(df_table["500"][2]-df_table["500"][1]+gap2_3_7,2)
                
                gaps1_2=[gap1_2_1,gap1_2_2,gap1_2_3,gap1_2_4,0,0,0,0]
                gaps2_3=[gap2_3_1,gap2_3_2,gap2_3_3,gap2_3_4,gap2_3_5,gap2_3_6,gap2_3_7,gap2_3_8]
                df_gap = pd.DataFrame(gaps1_2)
                df_gap.rename(columns={ df_gap.columns[0]: "Gap1_2" }, inplace = True)
                df_gap["Gap2_3"]=gaps2_3
                
              
            
                f1 = go.Figure(
                data = [
                    go.Scatter(y=gaps1_2[0:4], x=["Q1","Q2","Q3","Q4"], name="Rider 2 to 1"),
                    go.Scatter(x=["Q1","Q2","Q3","Q4","Q5","Q6","Q7","Q8"], y=gaps2_3, name="Rider 3 to 2"),
                ],
                layout = {"xaxis": {"title": "Quarters"}, "yaxis": {"title": "Seconds"}, "title": "Gaps by Quarter"}
                )
                
                st.plotly_chart(f1, use_container_width=True)
                if i==0:
                    df_table_all=df_table
                    df_table_small_all = df_table_small
                else:
                    df_table_all=pd.concat([df_table_all,df_table])
                    df_table_small_all = pd.concat([df_table_small_all, df_table_small], ignore_index=True)
                c1,c2=st.columns(2)
                with c2:
                    if Videos == "Yes":
                    
                        if pd.isnull(df_temp["Video"].iloc[0]):
                            st.header("No video available")
                        else:
                            video_name = df_temp["Video"].iloc[0]
                            st.header(df_temp["Title"].iloc[0])

                            st.video(f"{video_name}")
                
                st.markdown("---")
                
                
                teamsplits = [df_table["62.5"][0],df_table["125"][0],df_table["187.5"][0],df_table["250"][0],df_table["312.5"][1]+df_table["Gap 1"][1],df_table["375"][1],df_table["437.5"][1],df_table["500"][1],df_table["562.5"][2]+df_table["Gap 2"][2],df_table["625"][2],df_table["687.5"][2],df_table["750"][2]]
                
                teamspeeds = [round(3.6*62.5/i,2) for i in teamsplits]
                
                df_speeds = pd.DataFrame(teamspeeds)
                
                df_speeds["Title"] = selections[i]
                df_speeds["Marker"] = ["Q1","Q2","Q3","Q4","Q5","Q6","Q7","Q8","Q9","Q10","Q11","Q12"]
                df_speeds["Splits"] = teamsplits
                df_combine = pd.concat([df_combine, df_speeds], axis=0)
                
            st.header("Full Summary", anchor="summary")
            df = df_table_all
            df_filt = filter_dataframe(df, widget_key_prefix="mts_full_summary")
            df_filt
            st.subheader("Compact Full Summary")
            df_small_filt = filter_dataframe(df_table_small_all, widget_key_prefix="mts_compact_full_summary")
            df_small_filt
            
            buffer = io.BytesIO()
            @st.cache_data
            def convert_to_csv(df):
                # IMPORTANT: Cache the conversion to prevent computation on every rerun
                return df.to_csv(index=False).encode('utf-8')

            csv = convert_to_csv(df)

            # download button 1 to download dataframe as csv
            download1 = st.download_button(
                label="Download Summary as CSV",
                data=csv,
                file_name='MTS_summary.csv',
                mime='text/csv'
            )

            # download button 2 to download dataframe as xlsx
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                # Write each dataframe to a different worksheet.
                df_filt.to_excel(writer, sheet_name='Sheet1', index=False)
                # Close the Pandas Excel writer and output the Excel file to the buffer
                writer.close()

                download2 = st.download_button(
                    label="Download Summary as Excel",
                    data=buffer,
                    file_name='MTS_summary.xlsx',
                    mime='application/vnd.ms-excel'
                ) 

            compact_buffer = io.BytesIO()
            with pd.ExcelWriter(compact_buffer, engine='xlsxwriter') as writer:
                df_small_filt.to_excel(writer, sheet_name='Sheet1', index=False)
                writer.close()

                download3 = st.download_button(
                    label="Download Compact Summary as Excel",
                    data=compact_buffer,
                    file_name='MTS_compact_summary.xlsx',
                    mime='application/vnd.ms-excel'
                )
            
            df_combine.rename(columns={ df_combine.columns[0]: "Speed (km/h)" }, inplace = True)
            
            fig_comp = px.line(df_combine, x="Marker", y = "Speed (km/h)", title="Average Speed Comparison",color="Title",markers="Splits",labels = {
            "Marker":"Quarter"})

            st.plotly_chart(fig_comp, use_container_width=True)
            
            fig_comp_split = px.line(df_combine, x="Marker", y = "Splits", title="Split Comparison",color="Title",markers="Splits",labels = {
            "Marker":"Quarter"})

            st.plotly_chart(fig_comp_split, use_container_width=True)
        st.markdown('---')
        st.header("Editor")


        uploaded_file = st.file_uploader("Choose a file",key="mts_uploader")

        if uploaded_file is not None:
            st.markdown("---")

            st.header("Editor")
            st.write("Initial df")
            df_full = pd.read_excel(uploaded_file)
            df_full['Position'] = df_full['Position'].apply(
    lambda t: t.hour * 3600 + t.minute * 60 + t.second + t.microsecond / 1_000_000
)
            df_full.drop(['Duration'],
          axis='columns', inplace=True)
            
            
            c1,c2,c3=st.columns(3)
            with c1:
                df_full
                start=st.number_input("Start Row (inclusive)", value=0, key="mts_start_row")
            with c2:
                df_check = pd.DataFrame(df_full.iloc[::28, :])
                st.write("Checking we've got everything")
                df_check = df_check.loc[:, ~df_check.columns.str.match(r'^Unnamed') & df_check.notna().any()]
                df_check
                end=st.number_input("End Row (inclusive)", value=start+27, key="mts_end_row")+1
            
            
            df=df_full[start:end]
            
            
            with c1:
                rider1 = st.text_input("Select Rider 1:", key="mts_rider1")
                rider2 = st.text_input("Select Rider 2:", key="mts_rider2")
                rider3 = st.text_input("Select Rider 3:", key="mts_rider3")
            
            riders=[rider1,rider2,rider3]
            
            with c2:
                rider1gear = st.text_input("Select Rider 1 gear:", key="mts_gear1")
                rider2gear = st.text_input("Select Rider 2 gear:", key="mts_gear2")
                rider3gear = st.text_input("Select Rider 3 gear:", key="mts_gear3")
                Title = st.text_input("Plot Title:", key="mts_title")


            df["Riders"]="NA"
            df["Riders"].iloc[0]=rider1
            df["Riders"].iloc[1]=rider2
            df["Riders"].iloc[2]=rider3
            df["Gears"]=0.0
            df["Title"]=Title
            col = df.pop('Title')
            df.insert(0, col.name, col)
            df["Gears"].iloc[0]=rider1gear
            df["Gears"].iloc[1]=rider2gear
            df["Gears"].iloc[2]=rider3gear
            front=[rider1]
            splits=[0]
            del_speeds=[0]
            speeds=[0]
            r=0
            
            df = df.loc[:, ~df.columns.str.match(r'^Unnamed') & df.notna().any()]
            df=df.reset_index(drop=True)
            with c3:
                df
                ind1=df.index[df['Name'] == "Rider 1 Forward"].tolist()[0]
                ind2=df.index[df['Name'] == "Rider 2 Forward"].tolist()[0]
                ind3=df.index[df['Name'] == "Rider 3 Forward"].tolist()[0]
                indstart=df.index[df['Name'] == "Start"].tolist()[0]
                react1 = round(df["Position"][ind1]-df["Position"][indstart],2)
                react2 = round(df["Position"][ind2]-df["Position"][indstart],2)
                react3 = round(df["Position"][ind3]-df["Position"][indstart],2)
                st.write(f'Reaction time for rider 1 is {react1} seconds')
                st.write(f'Reaction time for rider 2 is {react2} seconds')
                st.write(f'Reaction time for rider 3 is {react3} seconds')

            if st.button("Append this effort to master",key="mts_upload"):

                df_save=df
                df_save = df_save.rename(columns={'Name': 'Row','Position':'Start time'})
                df_save.insert(0, 'Save_Date', datetime.date.today())
                df_save["Save_Date"] = pd.to_datetime(df_save['Save_Date'])
                df = pd.concat([df_master, df_save], axis=0)
                
                df

                buffer = io.BytesIO()

                @st.cache_data
                def convert_to_csv(df):
                    # IMPORTANT: Cache the conversion to prevent computation on every rerun
                    return df.to_csv(index=False).encode('utf-8')

                csv = convert_to_csv(df)

                download1 = st.download_button(
                    label="Download new Master as CSV",
                    data=csv,
                    file_name='MTS_Master_Men.csv',
                    mime='text/csv'
                )

                with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                    df.to_excel(writer, sheet_name='Sheet1', index=False)
                    writer.close()

                    download2 = st.download_button(
                        label="Download new Master as Excel",
                        data=buffer,
                        file_name='MTS_Master_Men.xlsx',
                        mime='application/vnd.ms-excel'
                    )       
