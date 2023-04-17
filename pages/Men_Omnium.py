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
st.header('Men\'s Omnium')
st.subheader('All results')

@st.cache_data
def get_points_data_from_excel():
    df_points = pd.read_excel(
        io='pages/MensRaceResults.xlsm',
        engine ='openpyxl',
        sheet_name='OM-Points',
        skiprows=0,
        usecols='A:AA',
        nrows=3000
        )
    df_points = df_points.replace(',','')
    df_points.Age = round(df_points.Age,2)
    return df_points
df_points= get_points_data_from_excel()

def get_scracth_data_from_excel():
    df_scratch = pd.read_excel(
        io='pages/MensRaceResults.xlsm',
        engine ='openpyxl',
        sheet_name='OM-Scratch',
        skiprows=0,
        usecols='A:J',
        nrows=3000
        )
    df_scratch = df_scratch.replace(',','')
    df_scratch.Age = round(df_scratch.Age,2)
    return df_scratch
df_scratch= get_scracth_data_from_excel()

def get_tempo_data_from_excel():
    df_tempo = pd.read_excel(
        io='pages/MensRaceResults.xlsm',
        engine ='openpyxl',
        sheet_name='OM-Tempo',
        skiprows=0,
        usecols='A:AW',
        nrows=3000
        )
    df_tempo = df_tempo.replace(',','')
    df_tempo.Age = round(df_tempo.Age,2)
    return df_tempo
df_tempo= get_tempo_data_from_excel()

def get_elimination_data_from_excel():
    df_elim = pd.read_excel(
        io='pages/MensRaceResults.xlsm',
        engine ='openpyxl',
        sheet_name='OM-Elimination',
        skiprows=0,
        usecols='A:J',
        nrows=3000
        )
    df_elim = df_elim.replace(',','')
    df_elim.Age = round(df_elim.Age,2)
    return df_elim
df_elim= get_elimination_data_from_excel()

df_scratch_orig = df_scratch
df_elim_orig = df_elim
df_tempo_orig = df_tempo
df_points_orig = df_points


year = st.multiselect(
    "Select Year:",
    options=df_points["Year"].unique(),
    default=df_points["Year"].unique()[0]
)    
if year:
    df_points = df_points.query(
        "Year == @year"
        )
    df_scratch = df_scratch.query(
        "Year == @year"
        )
    df_elim = df_elim.query(
        "Year == @year"
        )
    df_tempo = df_tempo.query(
        "Year == @year"
        )
else:
    df_points=df_points_orig
    df_scratch=df_scratch_orig
    df_tempo=df_tempo_orig
    df_elim=df_elim_orig


location = st.multiselect(
    "Select Location:",
    options=df_points["Location"].unique(),
    default=df_points["Location"].unique()[0]
)

if location:
    df_points = df_points.query(
        "Location == @location"
        )
    df_scratch = df_scratch.query(
        "Location == @location"
        )
    df_elim = df_elim.query(
        "Location == @location"
        )
    df_tempo = df_tempo.query(
        "Location == @location"
        )
else:
    df_points=df_points_orig
    df_scratch=df_scratch_orig
    df_tempo=df_tempo_orig
    df_elim=df_elim_orig

event = st.multiselect(
    "Select Event Type:",
    options=df_points["Event"].unique(),
    default=df_points["Event"].unique()[0]
)

if event:
    df_points = df_points.query(
        "Event == @event"
        )
    df_scratch = df_scratch.query(
        "Event == @event"
        )
    df_elim = df_elim.query(
        "Event == @event"
        )
    df_tempo = df_tempo.query(
        "Event == @event"
        )
else:
    df_points=df_points_orig
    df_scratch=df_scratch_orig
    df_tempo=df_tempo_orig
    df_elim=df_elim_orig

st.subheader('Summary & Points Race')
st.dataframe(df_points)
st.subheader('Scratch Race')
st.dataframe(df_scratch)
st.subheader('Tempo Race')
st.dataframe(df_tempo)
st.subheader('Elimination Race')
st.dataframe(df_elim)
    
st.markdown("---")
    
st.title(":bicyclist: Event History")

names = df_points_orig['Name'].drop_duplicates().sort_values()
name = st.multiselect("Select Rider(s):", names)

df_countryHistory = df_points_orig.query(
    "Name == @name"
)

## Totals by Date -- DB and plot

st.dataframe(df_countryHistory)

fig_country_history = px.line(df_countryHistory, x="Date", y = "Final", title = "Totals by Date", markers = "True", text = "Location", color="Country")
fig_country_history.update_traces(textposition="top right")

st.plotly_chart(fig_country_history)

## Ranks by Date -- DB and plot

fig_country_history = px.line(df_countryHistory, x="Date", y = "Rank", title = "Rank by Date", markers = "True", color="Country")
#fig_country_history.update_traces(textposition="top right")

st.plotly_chart(fig_country_history)

## Laps taken by date -- DB and plot

fig_country_history = px.line(df_countryHistory, x="Date", y = "Lap +", title = "Laps Taken by Date", markers = "True", color="Country")
#fig_country_history.update_traces(textposition="top right")

st.plotly_chart(fig_country_history)

## Laps lost by date -- DB and plot

fig_country_history = px.line(df_countryHistory, x="Date", y = "Lap -", title = "Laps Lost by Date", markers = "True", color="Country")


st.plotly_chart(fig_country_history)




st.markdown("---")
    
st.title(":mag_right: Race Analysis Tool")
uniqueYear = df_points_orig['Year'].drop_duplicates().sort_values(ascending=False)


left_column, middle_column, right_column = st.columns(3)
with left_column:
    an_year = st.selectbox("Select Year:", uniqueYear)
    
df_an_year = df_points_orig.query(
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

### Splits dataframe and plot

df_splits = pd.DataFrame()
df_splits["Marker"] = ["Sprint 1","Sprint 2","Sprint 3","Sprint 4","Sprint 5","Sprint 6","Sprint 7","Sprint 8","Sprint 9","Sprint 10"]
for i in range(len(df_an)):
    var = str(df_an["Name"].iloc[i])
    df_splits[f"{var}"]=df_an.iloc[i][12:22].values

#st.dataframe(df_splits)

fig_event = px.line(df_splits, x="Marker", y = df_splits.columns, title="Points Race Sprint Points", markers=True)

st.plotly_chart(fig_event)

### Worm dataframe and plot
st.write("Running Time")
df_worm = pd.DataFrame()
df_worm["Marker"] = ["Sprint 1","Sprint 2","Sprint 3","Sprint 4","Sprint 5","Sprint 6","Sprint 7","Sprint 8","Sprint 9","Sprint 10"]
for i in range(len(df_an)):
    var = str(df_an["Name"].iloc[i])
    df_worm[f"{var}"]=df_an.iloc[i][12:22].values.cumsum()

#st.dataframe(df_worm)

fig_worm = px.line(df_worm, x="Marker", y = df_worm.columns, title="Points Race Worm")

st.plotly_chart(fig_worm)


###Markers Dataframe and plot
st.write("Random Useless thing")
st.dataframe(df_an)



fig_event = px.line(df_an, y=["Sprint 1","Sprint 2","Sprint 3","Sprint 4","Sprint 5","Sprint 6","Sprint 7","Sprint 8","Sprint 9","Sprint 10","Sprint 11","Sprint 12","Sprint 13","Sprint 14","Sprint 15","Sprint 16","Sprint 17","Sprint 18","Sprint 19","Sprint 20"], x = "Country", title="Pretty useless????", markers=True)
#fig_event.update_layout(legend_title="legend")
st.plotly_chart(fig_event)

##

df_mean = df_orig.groupby('Country', as_index=False).mean()

st.write("Points Average")
df_splits_mean = pd.DataFrame()
df_splits_mean["Marker"] = ["Sprint 1","Sprint 2","Sprint 3","Sprint 4","Sprint 5","Sprint 6","Sprint 7","Sprint 8","Sprint 9","Sprint 10","Sprint 11","Sprint 12","Sprint 13","Sprint 14","Sprint 15","Sprint 16","Sprint 17","Sprint 18","Sprint 19","Sprint 20"]
for i in range(len(df_mean)):
    var = str(df_mean["Country"].iloc[i])
    df_splits_mean[f"{var}"]=df_mean.iloc[i][3:23].values

st.dataframe(df_splits_mean)

fig_event_mean = px.line(df_splits_mean, x="Marker", y = df_splits.columns, title="Points Scoring Average", markers=True)

st.plotly_chart(fig_event_mean)
df_mean_total = df_orig[df_orig.Total != "DNF"]
df_mean_total = df_mean_total.groupby('Country', as_index=False)["Total"].mean()
st.dataframe(df_mean_total)

fig_total_mean = px.bar(df_mean_total, x="Country", y = "Total", title="Total Scoring Average")
st.plotly_chart(fig_total_mean)