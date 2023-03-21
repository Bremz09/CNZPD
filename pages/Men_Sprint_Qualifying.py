#!/usr/bin/env python
# coding: utf-8



import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image





st.set_page_config(page_title='CNZ Performance Database',
                  page_icon=":bike:",
                  layout="wide")
st.header('Men\'s Sprint Qualifying')
st.subheader('All results')

@st.cache_data
def get_data_from_excel():
    df = pd.read_excel(
        io='pages\MensRaceResults.xlsm',
        engine ='openpyxl',
        sheet_name='Sprint Qual',
        skiprows=0,
        usecols='A:M',
        nrows=691
        )
    df = df.replace(',','')
    return df
df= get_data_from_excel()

df_orig = df

year = st.multiselect(
    "Select Year:",
    options=df["Year"].unique(),
    default=df["Year"].unique()[0]
)    
if year:
    df = df.query(
        "Year == @year"
        )
else:
    df=df_orig


location = st.multiselect(
    "Select Location:",
    options=df["Location"].unique(),
    default=df["Location"].unique()[0]
)

if location:
    df = df.query(
        "Location == @location"
        )
else:
    df=df_orig

event = st.multiselect(
    "Select Event Type:",
    options=df["Event"].unique(),
    default=df["Event"].unique()[0]
)

if event:
    df = df.query(
        "Event == @event"
        )
else:
    df=df_orig

    
st.dataframe(df)
    
st.markdown("---")
    
st.title(":bar_chart: Top Ten Performances")

df_topten = df_orig.sort_values('200m').head(10)

st.dataframe(df_topten)

st.markdown("---")
    
st.title(":bicyclist: Athlete History")

athletes = df_orig['Athlete'].drop_duplicates().sort_values()
athlete = st.multiselect("Select Athlete(s):", athletes)

df_athleteHistory = df_orig.query(
    "Athlete == @athlete"
)

st.dataframe(df_athleteHistory)

fig_athlete_history = px.line(df_athleteHistory, x="Date", y = "200m", title = "Times by Date", markers = "True", text = "Location", color="Athlete")
fig_athlete_history.update_traces(textposition="top right")

st.plotly_chart(fig_athlete_history)

fig_athlete_history = px.line(df_athleteHistory, x="Date", y = "Rank", title = "Rank by Date", markers = "True", color="Athlete")
fig_athlete_history.update_traces(textposition="top right")

st.plotly_chart(fig_athlete_history)

fig_athlete_history = px.line(df_athleteHistory, x="Age", y = "200m", title = "Times by Age", markers = "True", color="Athlete")
fig_athlete_history.update_traces(textposition="top right")

st.plotly_chart(fig_athlete_history)

fig_athlete_history = px.line(df_athleteHistory, x="Age", y = "100m", title = "100m Times by Age", markers = "True", color="Athlete")


st.plotly_chart(fig_athlete_history)

fig_athlete_history = px.line(df_athleteHistory, x="Age", y = "100-200m", title = "100-200m Times by Age", markers = "True", color="Athlete")


st.plotly_chart(fig_athlete_history)


st.markdown("---")
    
st.title(":mag_right: Race Analysis Tool")
uniqueYear = df_orig['Year'].drop_duplicates().sort_values(ascending=False)


left_column, middle_column, right_column = st.columns(3)
with left_column:
    an_year = st.selectbox("Select Year:", uniqueYear)
    
df_an_year = df_orig.query(
    "Year == @an_year"
)
uniqueLocation = df_an_year['Location'].drop_duplicates().sort_values()

with middle_column:
    an_location = st.selectbox("Select Location:", uniqueLocation)
    
df_an_year_location = df_an_year.query(
    "Year == @an_year & Location == @an_location"
)
    
uniqueEvent = df_an_year_location['Event'].drop_duplicates().sort_values()
with right_column:
    an_event = st.selectbox("Select Event:", uniqueEvent)

df_an = df_an_year_location.query(
    "Year == @an_year & Location == @an_location & Event == @an_event"
)

st.dataframe(df_an)



fig_event = px.line(df_an, y=["100m","200m","Diff"], x = "Athlete")

st.plotly_chart(fig_event)

#t.write(df_and["100m"])


