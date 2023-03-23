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
st.header('Men\'s 1k Time Trial')
st.subheader('All results')

@st.cache_data
def get_data_from_excel():
    df = pd.read_excel(
        io='pages/MensRaceResults.xlsm',
        engine ='openpyxl',
        sheet_name='1k TT',
        skiprows=0,
        usecols='A:S',
        nrows=1000
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

df_topten = df_orig.sort_values('Time').head(10)

st.dataframe(df_topten)

st.markdown("---")
    
st.title(":bicyclist: Athlete History")

athletes = df_orig['Athlete'].drop_duplicates().sort_values()
athlete = st.multiselect("Select Athlete(s):", athletes)

df_athleteHistory = df_orig.query(
    "Athlete == @athlete"
)

st.dataframe(df_athleteHistory)

fig_athlete_history = px.line(df_athleteHistory, x="Date", y = "Time", title = "Times by Date", markers = "True", text = "Location", color="Athlete")
fig_athlete_history.update_traces(textposition="top right")

st.plotly_chart(fig_athlete_history)

fig_athlete_history = px.line(df_athleteHistory, x="Date", y = "Rank", title = "Rank by Date", markers = "True", color="Athlete")
fig_athlete_history.update_traces(textposition="top right")

st.plotly_chart(fig_athlete_history)

fig_athlete_history = px.line(df_athleteHistory, x="Age", y = "Time", title = "Times by Age", markers = "True", color="Athlete")
fig_athlete_history.update_traces(textposition="top right")

st.plotly_chart(fig_athlete_history)

df_athleteHistory["Half"] = df_athleteHistory["125m"]+df_athleteHistory["250m"]+df_athleteHistory["375m"]+df_athleteHistory["500m"]

fig_athlete_history = px.line(df_athleteHistory, x="Age", y = "Half", title = "500m Times by Age", markers = "True", color="Athlete")


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

df_an_year_location_event = df_an_year_location.query(
    "Year == @an_year & Location == @an_location & Event == @an_event"
)

uniqueStage = df_an_year_location_event['Stage'].drop_duplicates().sort_values()

left_column, middle_column, right_column = st.columns(3)
with left_column:
    an_stage = st.selectbox("Select Stage:", uniqueStage)
    
df_an = df_an_year_location_event.query(
    "Year == @an_year & Location == @an_location & Event == @an_event & Stage == @an_stage"
)

st.dataframe(df_an)



fig_event = px.line(df_an, y=["125m","250m","375m","500m","625m","750m","875m","1000m"], x = "Athlete")

st.plotly_chart(fig_event)

### Worm dataframe and plot
# st.write("Running Time")
df_worm = pd.DataFrame()
df_worm["Marker"] = ["125m","250m","375m","500m","625m","750m","875m","1000m"]

for i in range(len(df_an)):
    var = str(df_an["Athlete"].iloc[i])
    df_worm[f"{var}"]=df_an.iloc[i][9:17].values.cumsum()

st.dataframe(df_worm)

fig_event = px.line(df_worm, x="Marker", y = df_worm.columns, title="The Worm")

st.plotly_chart(fig_event)


