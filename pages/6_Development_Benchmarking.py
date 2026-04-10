#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import streamlit as st
import plotly.express as px
import io

st.set_page_config(page_title='High Performance Development Benchmarking',
                   page_icon=":bike:",
                   layout="wide")

# --- USER AUTHENTICATION ---
import streamlit_authenticator as stauth
import pickle

with open("hashed_pw.pkl", "rb") as file:
    hashed_passwords = pickle.load(file)

usernames = ['CNZ']
names = ['CNZ']

credentials = {"usernames": {}}
for uname, name, pwd in zip(usernames, names, hashed_passwords):
    credentials["usernames"].update({uname: {"name": name, "password": pwd}})

authenticator = stauth.Authenticate(credentials, "CNZPD", "abcdef", cookie_expiry_days=30)
name, authentication_status, username = authenticator.login("Login", "main")

if authentication_status == False:
    st.error("Username/password is incorrect")

if authentication_status == None:
    st.warning("Please enter your username and password")

if authentication_status:

    st.title(":bike: High Performance Development Benchmarking")
    st.markdown("---")

    databases = ["Men's Endurance HPD", "Women's Endurance HPD", "Sprint HPD"]
    database = st.selectbox("Select Database:", databases, key="Database_Selector")

    @st.cache_data
    def convert_to_csv(df):
        return df.to_csv(index=False, sep=",").encode('utf-32')

    # ============================================================
    # Sprint HPD
    # ============================================================
    if database == "Sprint HPD":
        st.header("Sprint HPD")

        @st.cache_data
        def get_sprint_sheet_names():
            xls = pd.ExcelFile('pages/Sprint_HPD.xlsx', engine='openpyxl')
            return [sheet for sheet in xls.sheet_names if sheet.strip().lower() != "sheet1"]

        sprint_sheet_types = get_sprint_sheet_names()

        if len(sprint_sheet_types) == 0:
            st.warning("No Sprint HPD sheets available after excluding Sheet1.")
        else:
            sprint_sheet = st.selectbox("Select Sheet:", sprint_sheet_types, key="Sheet_Selector_Sprint")

            @st.cache_data
            def get_sprint_sheet(sheet_name):
                df = pd.read_excel(
                    io='pages/Sprint_HPD.xlsx',
                    engine='openpyxl',
                    sheet_name=sheet_name,
                    skiprows=0,
                    nrows=5000
                )
                return df

            df_orig = get_sprint_sheet(sprint_sheet)
            df = df_orig.copy()

            filter_columns = ["Year", "Location", "Event", "Athlete"]
            available_filter_columns = [col for col in filter_columns if col in df_orig.columns]

            if len(available_filter_columns) != 0:
                filter_cols = st.columns(len(available_filter_columns))
                for idx, col_name in enumerate(available_filter_columns):
                    with filter_cols[idx]:
                        options = df_orig[col_name].dropna().unique()
                        selected_values = st.multiselect(
                            f"Select {col_name}:",
                            options=options,
                            key=f"sprint_{sprint_sheet}_{col_name}"
                        )
                        if selected_values:
                            df = df[df[col_name].isin(selected_values)]

            st.dataframe(df, use_container_width=True)

            csv = convert_to_csv(df)
            st.download_button(label="Download as CSV", data=csv, file_name='Sprint_HPD_Data.csv', mime='text/csv', key="sprint_csv")

            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                df.to_excel(writer, sheet_name='Sheet1', index=False)
                writer.close()
                st.download_button(label="Download as Excel", data=buffer, file_name='Sprint_HPD_Data.xlsx', mime='application/vnd.ms-excel', key="sprint_xlsx")

    # ============================================================
    # Men's Endurance HPD
    # ============================================================
    if database == "Men's Endurance HPD":
        st.header("Men's Endurance HPD")

        sheet_types = ["B750", "F1000", "IP"]
        sheet_type = st.selectbox("Select Sheet:", sheet_types, key="Sheet_Selector")

    # ============================================================
    # B750
    # ============================================================
    if database == "Men's Endurance HPD" and sheet_type == "B750":
        st.header("B750")

        @st.cache_data
        def get_b750():
            df = pd.read_excel(
                io='pages/Mens_Endurance_HPD.xlsx',
                engine='openpyxl',
                sheet_name='B750',
                skiprows=0,
                usecols='A:H',
                nrows=2000
            )
            return df

        df_orig = get_b750()
        df = df_orig.copy()

        col1, col2, col3 = st.columns(3)
        with col1:
            year = st.multiselect(
                "Select Year:",
                options=df_orig["Year"].unique(),
                default=df_orig["Year"].unique()[0],
                key="b750_year"
            )
            if year:
                df = df.query("Year == @year")

        with col2:
            location = st.multiselect(
                "Select Location:",
                options=df_orig["Location"].unique(),
                default=df_orig["Location"].unique()[0],
                key="b750_location"
            )
            if location:
                df = df.query("Location == @location")

        with col3:
            event = st.multiselect(
                "Select Event Type:",
                options=df_orig["Event"].unique(),
                default=df_orig["Event"].unique()[0],
                key="b750_event"
            )
            if event:
                df = df.query("Event == @event")

        st.dataframe(df, use_container_width=True)

        csv = convert_to_csv(df)
        st.download_button(label="Download as CSV", data=csv, file_name='B750_Data.csv', mime='text/csv', key="b750_csv")
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='Sheet1', index=False)
            writer.close()
            st.download_button(label="Download as Excel", data=buffer, file_name='B750_Data.xlsx', mime='application/vnd.ms-excel', key="b750_xlsx")

        st.markdown("---")
        st.title(":bar_chart: Top Performances")
        df_top = df_orig.sort_values('F500').head(10)
        st.dataframe(df_top, use_container_width=True)

        st.markdown("---")
        st.title(":bicyclist: Athlete History")

        athletes = df_orig['Athlete'].drop_duplicates().sort_values()
        athlete = st.multiselect("Select Athlete(s):", athletes, key="b750_athletes")
        df_ah = df_orig.query("Athlete == @athlete").sort_values("Date", ascending=False)

        if len(athlete) != 0:
            st.dataframe(df_ah, use_container_width=True)
            csv_ah = convert_to_csv(df_ah)
            st.download_button(label="Download athlete history as CSV", data=csv_ah, file_name='B750_Athlete_History.csv', mime='text/csv', key="b750_ah_csv")

            fig = px.line(df_ah, x="Date", y="F500", title="F500 Times by Date", markers=True, text="Location", color="Athlete", labels={"F500": "F500 (seconds)"})
            fig.update_traces(textposition="top right")
            st.plotly_chart(fig, use_container_width=True)

            fig2 = px.line(df_ah, x="Date", y="S250", title="S250 Times by Date", markers=True, text="Location", color="Athlete", labels={"S250": "S250 (seconds)"})
            fig2.update_traces(textposition="top right")
            st.plotly_chart(fig2, use_container_width=True)

        st.markdown("---")
        st.title(":mag_right: Race Analysis Tool")

        uniqueYear = df_orig['Year'].drop_duplicates().sort_values(ascending=False)
        left_col, mid_col, right_col = st.columns(3)
        with left_col:
            an_year = st.selectbox("Select Year:", uniqueYear, key="b750_an_year")
        df_an_year = df_orig.query("Year == @an_year")
        uniqueLocation = df_an_year['Location'].drop_duplicates().sort_values()
        with mid_col:
            an_location = st.selectbox("Select Location:", uniqueLocation, key="b750_an_loc")
        df_an_loc = df_an_year.query("Location == @an_location")
        uniqueEvent = df_an_loc['Event'].drop_duplicates().sort_values()
        with right_col:
            an_event = st.selectbox("Select Event:", uniqueEvent, key="b750_an_event")
        df_an = df_an_loc.query("Event == @an_event")
        st.dataframe(df_an, use_container_width=True)
        fig_event = px.line(df_an, y=["S250", "F500"], x="Athlete", markers=True, labels={"value": "Seconds"})
        st.plotly_chart(fig_event, use_container_width=True)

    # ============================================================
    # F1000
    # ============================================================
    elif database == "Men's Endurance HPD" and sheet_type == "F1000":
        st.header("F1000")

        @st.cache_data
        def get_f1000():
            df = pd.read_excel(
                io='pages/Mens_Endurance_HPD.xlsx',
                engine='openpyxl',
                sheet_name='F1000',
                skiprows=0,
                usecols='A:K',
                nrows=2000
            )
            return df

        df_orig = get_f1000()
        df = df_orig.copy()

        col1, col2, col3 = st.columns(3)
        with col1:
            year = st.multiselect(
                "Select Year:",
                options=df_orig["Year"].unique(),
                default=df_orig["Year"].unique()[0],
                key="f1000_year"
            )
            if year:
                df = df.query("Year == @year")

        with col2:
            location = st.multiselect(
                "Select Location:",
                options=df_orig["Location"].unique(),
                default=df_orig["Location"].unique()[0],
                key="f1000_location"
            )
            if location:
                df = df.query("Location == @location")

        with col3:
            event = st.multiselect(
                "Select Event Type:",
                options=df_orig["Event"].unique(),
                default=df_orig["Event"].unique()[0],
                key="f1000_event"
            )
            if event:
                df = df.query("Event == @event")

        st.dataframe(df, use_container_width=True)

        csv = convert_to_csv(df)
        st.download_button(label="Download as CSV", data=csv, file_name='F1000_Data.csv', mime='text/csv', key="f1000_csv")
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='Sheet1', index=False)
            writer.close()
            st.download_button(label="Download as Excel", data=buffer, file_name='F1000_Data.xlsx', mime='application/vnd.ms-excel', key="f1000_xlsx")

        st.markdown("---")
        st.title(":bar_chart: Top Performances")
        df_top = df_orig.sort_values('Total').head(10)
        st.dataframe(df_top, use_container_width=True)

        st.markdown("---")
        st.title(":bicyclist: Athlete History")

        athletes = df_orig['Athlete'].drop_duplicates().sort_values()
        athlete = st.multiselect("Select Athlete(s):", athletes, key="f1000_athletes")
        df_ah = df_orig.query("Athlete == @athlete").sort_values("Date", ascending=False)

        if len(athlete) != 0:
            st.dataframe(df_ah, use_container_width=True)
            csv_ah = convert_to_csv(df_ah)
            st.download_button(label="Download athlete history as CSV", data=csv_ah, file_name='F1000_Athlete_History.csv', mime='text/csv', key="f1000_ah_csv")

            fig = px.line(df_ah, x="Date", y="Total", title="Total Time by Date", markers=True, text="Location", color="Athlete", labels={"Total": "Total (seconds)"})
            fig.update_traces(textposition="top right")
            st.plotly_chart(fig, use_container_width=True)

            df_splits = pd.DataFrame()
            df_splits["Marker"] = [250, 500, 750, 1000]
            for i in range(len(df_ah)):
                var = str(df_ah["Athlete"].iloc[i]) + " " + str(df_ah["Year"].iloc[i]) + " " + str(df_ah["Event"].iloc[i])
                df_splits[f"{var}"] = df_ah.iloc[i][[250, 500, 750, 1000]].values
            fig2 = px.line(df_splits, x="Marker", y=df_splits.columns[1:], title="Lap Splits", markers=True, labels={"value": "Seconds", "Marker": "Distance (m)"})
            st.plotly_chart(fig2, use_container_width=True)

        st.markdown("---")
        st.title(":mag_right: Race Analysis Tool")

        uniqueYear = df_orig['Year'].drop_duplicates().sort_values(ascending=False)
        left_col, mid_col, right_col = st.columns(3)
        with left_col:
            an_year = st.selectbox("Select Year:", uniqueYear, key="f1000_an_year")
        df_an_year = df_orig.query("Year == @an_year")
        uniqueLocation = df_an_year['Location'].drop_duplicates().sort_values()
        with mid_col:
            an_location = st.selectbox("Select Location:", uniqueLocation, key="f1000_an_loc")
        df_an_loc = df_an_year.query("Location == @an_location")
        uniqueEvent = df_an_loc['Event'].drop_duplicates().sort_values()
        with right_col:
            an_event = st.selectbox("Select Event:", uniqueEvent, key="f1000_an_event")
        df_an = df_an_loc.query("Event == @an_event")
        st.dataframe(df_an, use_container_width=True)
        fig_event = px.line(df_an, y=[250, 500, 750, 1000, "Total"], x="Athlete", markers=True, labels={"value": "Seconds"})
        st.plotly_chart(fig_event, use_container_width=True)

    # ============================================================
    # IP
    # ============================================================
    elif database == "Men's Endurance HPD" and sheet_type == "IP":
        st.header("Individual Pursuit (IP)")

        @st.cache_data
        def get_ip():
            df = pd.read_excel(
                io='pages/Mens_Endurance_HPD.xlsx',
                engine='openpyxl',
                sheet_name='IP',
                skiprows=0,
                usecols='A:K',
                nrows=2000
            )
            return df

        df_orig = get_ip()
        df = df_orig.copy()

        col1, col2, col3 = st.columns(3)
        with col1:
            year = st.multiselect(
                "Select Year:",
                options=df_orig["Year"].unique(),
                default=df_orig["Year"].unique()[0],
                key="ip_year"
            )
            if year:
                df = df.query("Year == @year")

        with col2:
            location = st.multiselect(
                "Select Location:",
                options=df_orig["Location"].unique(),
                default=df_orig["Location"].unique()[0],
                key="ip_location"
            )
            if location:
                df = df.query("Location == @location")

        with col3:
            event = st.multiselect(
                "Select Event Type:",
                options=df_orig["Event"].unique(),
                default=df_orig["Event"].unique()[0],
                key="ip_event"
            )
            if event:
                df = df.query("Event == @event")

        st.dataframe(df, use_container_width=True)

        csv = convert_to_csv(df)
        st.download_button(label="Download as CSV", data=csv, file_name='IP_Data.csv', mime='text/csv', key="ip_csv")
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='Sheet1', index=False)
            writer.close()
            st.download_button(label="Download as Excel", data=buffer, file_name='IP_Data.xlsx', mime='application/vnd.ms-excel', key="ip_xlsx")

        st.markdown("---")
        st.title(":bar_chart: Top Performances")
        df_top = df_orig.sort_values('Total').head(10)
        st.dataframe(df_top, use_container_width=True)

        st.markdown("---")
        st.title(":bicyclist: Athlete History")

        athletes = df_orig['Athlete'].drop_duplicates().sort_values()
        athlete = st.multiselect("Select Athlete(s):", athletes, key="ip_athletes")
        df_ah = df_orig.query("Athlete == @athlete").sort_values("Date", ascending=False)

        if len(athlete) != 0:
            st.dataframe(df_ah, use_container_width=True)
            csv_ah = convert_to_csv(df_ah)
            st.download_button(label="Download athlete history as CSV", data=csv_ah, file_name='IP_Athlete_History.csv', mime='text/csv', key="ip_ah_csv")

            fig = px.line(df_ah, x="Date", y="Total", title="Total Time by Date", markers=True, text="Location", color="Athlete", labels={"Total": "Total Time"})
            fig.update_traces(textposition="top right")
            st.plotly_chart(fig, use_container_width=True)

            df_splits = pd.DataFrame()
            df_splits["Marker"] = ["1km", "2km", "3km", "4km"]
            for i in range(len(df_ah)):
                var = str(df_ah["Athlete"].iloc[i]) + " " + str(df_ah["Year"].iloc[i]) + " " + str(df_ah["Event"].iloc[i])
                df_splits[f"{var}"] = df_ah.iloc[i][["1km", "2km", "3km", "4km"]].values
            fig2 = px.line(df_splits, x="Marker", y=df_splits.columns[1:], title="Lap Splits", markers=True, labels={"value": "Time", "Marker": "Distance"})
            st.plotly_chart(fig2, use_container_width=True)

        st.markdown("---")
        st.title(":mag_right: Race Analysis Tool")

        uniqueYear = df_orig['Year'].drop_duplicates().sort_values(ascending=False)
        left_col, mid_col, right_col = st.columns(3)
        with left_col:
            an_year = st.selectbox("Select Year:", uniqueYear, key="ip_an_year")
        df_an_year = df_orig.query("Year == @an_year")
        uniqueLocation = df_an_year['Location'].drop_duplicates().sort_values()
        with mid_col:
            an_location = st.selectbox("Select Location:", uniqueLocation, key="ip_an_loc")
        df_an_loc = df_an_year.query("Location == @an_location")
        uniqueEvent = df_an_loc['Event'].drop_duplicates().sort_values()
        with right_col:
            an_event = st.selectbox("Select Event:", uniqueEvent, key="ip_an_event")
        df_an = df_an_loc.query("Event == @an_event")
        st.dataframe(df_an, use_container_width=True)
        fig_event = px.line(df_an, y=["1km", "2km", "3km", "4km", "Total"], x="Athlete", markers=True, labels={"value": "Time"})
        st.plotly_chart(fig_event, use_container_width=True)

    # ============================================================
    # Women's Endurance HPD
    # ============================================================
    if database == "Women's Endurance HPD":
        st.header("Women's Endurance HPD")

        sheet_types_w = ["B750", "F1000", "IP"]
        sheet_type_w = st.selectbox("Select Sheet:", sheet_types_w, key="Sheet_Selector_W")

    # ============================================================
    # Women's B750
    # ============================================================
    if database == "Women's Endurance HPD" and sheet_type_w == "B750":
        st.header("B750")

        @st.cache_data
        def get_w_b750():
            df = pd.read_excel(
                io='pages/Womens_Endurance_HPD.xlsx',
                engine='openpyxl',
                sheet_name='B750',
                skiprows=0,
                usecols='A:I',
                nrows=2000
            )
            return df

        df_orig = get_w_b750()
        df = df_orig.copy()

        col1, col2, col3 = st.columns(3)
        with col1:
            year = st.multiselect(
                "Select Year:",
                options=df_orig["Year"].unique(),
                default=df_orig["Year"].unique()[0],
                key="w_b750_year"
            )
            if year:
                df = df.query("Year == @year")

        with col2:
            location = st.multiselect(
                "Select Location:",
                options=df_orig["Location"].unique(),
                default=df_orig["Location"].unique()[0],
                key="w_b750_location"
            )
            if location:
                df = df.query("Location == @location")

        with col3:
            event = st.multiselect(
                "Select Event Type:",
                options=df_orig["Event"].unique(),
                default=df_orig["Event"].unique()[0],
                key="w_b750_event"
            )
            if event:
                df = df.query("Event == @event")

        st.dataframe(df, use_container_width=True)

        csv = convert_to_csv(df)
        st.download_button(label="Download as CSV", data=csv, file_name='W_B750_Data.csv', mime='text/csv', key="w_b750_csv")
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='Sheet1', index=False)
            writer.close()
            st.download_button(label="Download as Excel", data=buffer, file_name='W_B750_Data.xlsx', mime='application/vnd.ms-excel', key="w_b750_xlsx")

        st.markdown("---")
        st.title(":bar_chart: Top Performances")
        df_top = df_orig.sort_values('F500').head(10)
        st.dataframe(df_top, use_container_width=True)

        st.markdown("---")
        st.title(":bicyclist: Athlete History")

        athletes = df_orig['Athlete'].drop_duplicates().sort_values()
        athlete = st.multiselect("Select Athlete(s):", athletes, key="w_b750_athletes")
        df_ah = df_orig.query("Athlete == @athlete").sort_values("Date", ascending=False)

        if len(athlete) != 0:
            st.dataframe(df_ah, use_container_width=True)
            csv_ah = convert_to_csv(df_ah)
            st.download_button(label="Download athlete history as CSV", data=csv_ah, file_name='W_B750_Athlete_History.csv', mime='text/csv', key="w_b750_ah_csv")

            fig = px.line(df_ah, x="Date", y="F500", title="F500 Times by Date", markers=True, text="Location", color="Athlete", labels={"F500": "F500 (seconds)"})
            fig.update_traces(textposition="top right")
            st.plotly_chart(fig, use_container_width=True)

            fig2 = px.line(df_ah, x="Date", y="S250", title="S250 Times by Date", markers=True, text="Location", color="Athlete", labels={"S250": "S250 (seconds)"})
            fig2.update_traces(textposition="top right")
            st.plotly_chart(fig2, use_container_width=True)

        st.markdown("---")
        st.title(":mag_right: Race Analysis Tool")

        uniqueYear = df_orig['Year'].drop_duplicates().sort_values(ascending=False)
        left_col, mid_col, right_col = st.columns(3)
        with left_col:
            an_year = st.selectbox("Select Year:", uniqueYear, key="w_b750_an_year")
        df_an_year = df_orig.query("Year == @an_year")
        uniqueLocation = df_an_year['Location'].drop_duplicates().sort_values()
        with mid_col:
            an_location = st.selectbox("Select Location:", uniqueLocation, key="w_b750_an_loc")
        df_an_loc = df_an_year.query("Location == @an_location")
        uniqueEvent = df_an_loc['Event'].drop_duplicates().sort_values()
        with right_col:
            an_event = st.selectbox("Select Event:", uniqueEvent, key="w_b750_an_event")
        df_an = df_an_loc.query("Event == @an_event")
        st.dataframe(df_an, use_container_width=True)
        fig_event = px.line(df_an, y=["S250", "F500"], x="Athlete", markers=True, labels={"value": "Seconds"})
        st.plotly_chart(fig_event, use_container_width=True)

    # ============================================================
    # Women's F1000
    # ============================================================
    elif database == "Women's Endurance HPD" and sheet_type_w == "F1000":
        st.header("F1000")

        @st.cache_data
        def get_w_f1000():
            df = pd.read_excel(
                io='pages/Womens_Endurance_HPD.xlsx',
                engine='openpyxl',
                sheet_name='F1000',
                skiprows=0,
                usecols='A:K',
                nrows=2000
            )
            return df

        df_orig = get_w_f1000()
        df = df_orig.copy()

        col1, col2, col3 = st.columns(3)
        with col1:
            year = st.multiselect(
                "Select Year:",
                options=df_orig["Year"].unique(),
                default=df_orig["Year"].unique()[0],
                key="w_f1000_year"
            )
            if year:
                df = df.query("Year == @year")

        with col2:
            location = st.multiselect(
                "Select Location:",
                options=df_orig["Location"].unique(),
                default=df_orig["Location"].unique()[0],
                key="w_f1000_location"
            )
            if location:
                df = df.query("Location == @location")

        with col3:
            event = st.multiselect(
                "Select Event Type:",
                options=df_orig["Event"].unique(),
                default=df_orig["Event"].unique()[0],
                key="w_f1000_event"
            )
            if event:
                df = df.query("Event == @event")

        st.dataframe(df, use_container_width=True)

        csv = convert_to_csv(df)
        st.download_button(label="Download as CSV", data=csv, file_name='W_F1000_Data.csv', mime='text/csv', key="w_f1000_csv")
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='Sheet1', index=False)
            writer.close()
            st.download_button(label="Download as Excel", data=buffer, file_name='W_F1000_Data.xlsx', mime='application/vnd.ms-excel', key="w_f1000_xlsx")

        st.markdown("---")
        st.title(":bar_chart: Top Performances")
        df_top = df_orig.sort_values('Total').head(10)
        st.dataframe(df_top, use_container_width=True)

        st.markdown("---")
        st.title(":bicyclist: Athlete History")

        athletes = df_orig['Athlete'].drop_duplicates().sort_values()
        athlete = st.multiselect("Select Athlete(s):", athletes, key="w_f1000_athletes")
        df_ah = df_orig.query("Athlete == @athlete").sort_values("Date", ascending=False)

        if len(athlete) != 0:
            st.dataframe(df_ah, use_container_width=True)
            csv_ah = convert_to_csv(df_ah)
            st.download_button(label="Download athlete history as CSV", data=csv_ah, file_name='W_F1000_Athlete_History.csv', mime='text/csv', key="w_f1000_ah_csv")

            fig = px.line(df_ah, x="Date", y="Total", title="Total Time by Date", markers=True, text="Location", color="Athlete", labels={"Total": "Total (seconds)"})
            fig.update_traces(textposition="top right")
            st.plotly_chart(fig, use_container_width=True)

            df_splits = pd.DataFrame()
            df_splits["Marker"] = [250, 500, 750, 1000]
            for i in range(len(df_ah)):
                var = str(df_ah["Athlete"].iloc[i]) + " " + str(df_ah["Year"].iloc[i]) + " " + str(df_ah["Event"].iloc[i])
                df_splits[f"{var}"] = df_ah.iloc[i][[250, 500, 750, 1000]].values
            fig2 = px.line(df_splits, x="Marker", y=df_splits.columns[1:], title="Lap Splits", markers=True, labels={"value": "Seconds", "Marker": "Distance (m)"})
            st.plotly_chart(fig2, use_container_width=True)

        st.markdown("---")
        st.title(":mag_right: Race Analysis Tool")

        uniqueYear = df_orig['Year'].drop_duplicates().sort_values(ascending=False)
        left_col, mid_col, right_col = st.columns(3)
        with left_col:
            an_year = st.selectbox("Select Year:", uniqueYear, key="w_f1000_an_year")
        df_an_year = df_orig.query("Year == @an_year")
        uniqueLocation = df_an_year['Location'].drop_duplicates().sort_values()
        with mid_col:
            an_location = st.selectbox("Select Location:", uniqueLocation, key="w_f1000_an_loc")
        df_an_loc = df_an_year.query("Location == @an_location")
        uniqueEvent = df_an_loc['Event'].drop_duplicates().sort_values()
        with right_col:
            an_event = st.selectbox("Select Event:", uniqueEvent, key="w_f1000_an_event")
        df_an = df_an_loc.query("Event == @an_event")
        st.dataframe(df_an, use_container_width=True)
        fig_event = px.line(df_an, y=[250, 500, 750, 1000, "Total"], x="Athlete", markers=True, labels={"value": "Seconds"})
        st.plotly_chart(fig_event, use_container_width=True)

    # ============================================================
    # Women's IP
    # ============================================================
    elif database == "Women's Endurance HPD" and sheet_type_w == "IP":
        st.header("Individual Pursuit (IP)")

        @st.cache_data
        def get_w_ip():
            df = pd.read_excel(
                io='pages/Womens_Endurance_HPD.xlsx',
                engine='openpyxl',
                sheet_name='IP',
                skiprows=0,
                usecols='A:L',
                nrows=2000
            )
            return df

        df_orig = get_w_ip()
        df = df_orig.copy()

        col1, col2, col3 = st.columns(3)
        with col1:
            year = st.multiselect(
                "Select Year:",
                options=df_orig["Year"].unique(),
                default=df_orig["Year"].unique()[0],
                key="w_ip_year"
            )
            if year:
                df = df.query("Year == @year")

        with col2:
            location = st.multiselect(
                "Select Location:",
                options=df_orig["Location"].unique(),
                default=df_orig["Location"].unique()[0],
                key="w_ip_location"
            )
            if location:
                df = df.query("Location == @location")

        with col3:
            event = st.multiselect(
                "Select Event Type:",
                options=df_orig["Event"].unique(),
                default=df_orig["Event"].unique()[0],
                key="w_ip_event"
            )
            if event:
                df = df.query("Event == @event")

        st.dataframe(df, use_container_width=True)

        csv = convert_to_csv(df)
        st.download_button(label="Download as CSV", data=csv, file_name='W_IP_Data.csv', mime='text/csv', key="w_ip_csv")
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='Sheet1', index=False)
            writer.close()
            st.download_button(label="Download as Excel", data=buffer, file_name='W_IP_Data.xlsx', mime='application/vnd.ms-excel', key="w_ip_xlsx")

        st.markdown("---")
        st.title(":bar_chart: Top Performances")
        df_top = df_orig.sort_values('Total').head(10)
        st.dataframe(df_top, use_container_width=True)

        st.markdown("---")
        st.title(":bicyclist: Athlete History")

        athletes = df_orig['Athlete'].drop_duplicates().sort_values()
        athlete = st.multiselect("Select Athlete(s):", athletes, key="w_ip_athletes")
        df_ah = df_orig.query("Athlete == @athlete").sort_values("Date", ascending=False)

        if len(athlete) != 0:
            st.dataframe(df_ah, use_container_width=True)
            csv_ah = convert_to_csv(df_ah)
            st.download_button(label="Download athlete history as CSV", data=csv_ah, file_name='W_IP_Athlete_History.csv', mime='text/csv', key="w_ip_ah_csv")

            fig = px.line(df_ah, x="Date", y="Total", title="Total Time by Date", markers=True, text="Location", color="Athlete", labels={"Total": "Total Time"})
            fig.update_traces(textposition="top right")
            st.plotly_chart(fig, use_container_width=True)

            df_splits = pd.DataFrame()
            df_splits["Marker"] = ["1km", "2km", "3km", "4km"]
            for i in range(len(df_ah)):
                var = str(df_ah["Athlete"].iloc[i]) + " " + str(df_ah["Year"].iloc[i]) + " " + str(df_ah["Event"].iloc[i])
                df_splits[f"{var}"] = df_ah.iloc[i][["1km", "2km", "3km", "4km"]].values
            fig2 = px.line(df_splits, x="Marker", y=df_splits.columns[1:], title="Lap Splits", markers=True, labels={"value": "Time", "Marker": "Distance"})
            st.plotly_chart(fig2, use_container_width=True)

        st.markdown("---")
        st.title(":mag_right: Race Analysis Tool")

        uniqueYear = df_orig['Year'].drop_duplicates().sort_values(ascending=False)
        left_col, mid_col, right_col = st.columns(3)
        with left_col:
            an_year = st.selectbox("Select Year:", uniqueYear, key="w_ip_an_year")
        df_an_year = df_orig.query("Year == @an_year")
        uniqueLocation = df_an_year['Location'].drop_duplicates().sort_values()
        with mid_col:
            an_location = st.selectbox("Select Location:", uniqueLocation, key="w_ip_an_loc")
        df_an_loc = df_an_year.query("Location == @an_location")
        uniqueEvent = df_an_loc['Event'].drop_duplicates().sort_values()
        with right_col:
            an_event = st.selectbox("Select Event:", uniqueEvent, key="w_ip_an_event")
        df_an = df_an_loc.query("Event == @an_event")
        st.dataframe(df_an, use_container_width=True)
        fig_event = px.line(df_an, y=["1km", "2km", "3km", "4km", "Total"], x="Athlete", markers=True, labels={"value": "Time"})
        st.plotly_chart(fig_event, use_container_width=True)
