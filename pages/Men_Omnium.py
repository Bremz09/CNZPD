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

c1,c2,c3=st.columns(3)
with c1:
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

with c2:
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
with c3:
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
st.dataframe(df_points,use_container_width=True)
st.subheader('Scratch Race')
st.dataframe(df_scratch,use_container_width=True)
st.subheader('Tempo Race')
st.dataframe(df_tempo,use_container_width=True)
st.subheader('Elimination Race')
st.dataframe(df_elim,use_container_width=True)
    
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

st.plotly_chart(fig_country_history,use_container_width=True)

## Ranks by Date -- DB and plot

fig_country_history = px.line(df_countryHistory, x="Date", y = "Rank", title = "Rank by Date", markers = "True", color="Country")
#fig_country_history.update_traces(textposition="top right")

st.plotly_chart(fig_country_history,use_container_width=True)

## Laps taken by date -- DB and plot

fig_country_history = px.line(df_countryHistory, x="Date", y = "Lap +", title = "Laps Taken by Date", markers = "True", color="Country")
#fig_country_history.update_traces(textposition="top right")

st.plotly_chart(fig_country_history,use_container_width=True)

## Laps lost by date -- DB and plot

fig_country_history = px.line(df_countryHistory, x="Date", y = "Lap -", title = "Laps Lost by Date", markers = "True", color="Country")


st.plotly_chart(fig_country_history,use_container_width=True)








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

st.plotly_chart(fig_event,use_container_width=True)

### Worm dataframe and plot

df_worm = pd.DataFrame()
df_worm["Marker"] = ["Sprint 1","Sprint 2","Sprint 3","Sprint 4","Sprint 5","Sprint 6","Sprint 7","Sprint 8","Sprint 9","Sprint 10"]
for i in range(len(df_an)):
    var = str(df_an["Name"].iloc[i])
    df_worm[f"{var}"]=df_an.iloc[i][12:22].values.cumsum()

#st.dataframe(df_worm)

fig_worm = px.line(df_worm, x="Marker", y = df_worm.columns, title="Points Race Worm")

st.plotly_chart(fig_worm,use_container_width=True)


###Markers Dataframe and plot

#st.dataframe(df_an)



fig_event = px.line(df_an, y=["Sprint 1","Sprint 2","Sprint 3","Sprint 4","Sprint 5","Sprint 6","Sprint 7","Sprint 8","Sprint 9","Sprint 10"], x = "Name", title="Pretty useless????", markers=True)
#fig_event.update_layout(legend_title="legend")
st.plotly_chart(fig_event,use_container_width=True)

##
st.markdown("---")
st.header("Historical Points Race Averages")

df_mean_points = df_points_orig.groupby('Name', as_index=False).mean()

df_mean_points=df_mean_points.drop(['Year','Age','Scratch','Lap +','Lap -','Avg Speed'],axis=1)

#st.dataframe(df_mean_points,use_container_width=True)





df_mean_points_transpose = pd.DataFrame()
df_mean_points_transpose["Marker"] = ["Sprint 1","Sprint 2","Sprint 3","Sprint 4","Sprint 5","Sprint 6","Sprint 7","Sprint 8","Sprint 9","Sprint 10"]
for i in range(len(df_mean_points)):
    var = str(df_mean_points["Name"].iloc[i])
    df_mean_points_transpose[f"{var}"]=df_mean_points.iloc[i][1:12].values

#st.dataframe(df_mean_points_transpose)

fig_event_mean = px.line(df_mean_points_transpose, x="Marker", y = df_mean_points_transpose.columns[1:], title="Historical Points Scoring Average", markers=True)

st.plotly_chart(fig_event_mean,use_container_width=True)


df_mean_total = df_points_orig[(df_points_orig.Final != "DSQ") & (df_points_orig.Final != "DNF")]
#st.dataframe(df_mean_total)
df_mean_total.Final = pd.to_numeric(df_mean_total.Final)
df_mean_total.Tempo = pd.to_numeric(df_mean_total.Tempo)
df_mean_total.Elimination = pd.to_numeric(df_mean_total.Elimination)
df_mean_total["Sub Total"] = pd.to_numeric(df_mean_total["Sub Total"])
#st.write(df_mean_total.Tempo.dtype)
df_mean_total["Points"] = df_mean_total["Final"]-df_mean_total["Sub Total"]
df_mean_total=df_mean_total.drop(["Year","Age",'Time','Avg Speed','Lap +','Lap -',"Sprint 1","Sprint 2","Sprint 3","Sprint 4","Sprint 5","Sprint 6","Sprint 7","Sprint 8","Sprint 9","Sprint 10","Sub Total","Final"],axis=1)

df_mean_total = df_mean_total.groupby('Name', as_index=False).mean()


















df_mean_total_transpose = pd.DataFrame()
df_mean_total_transpose["Marker"] = ["Scratch","Tempo","Elimination","Points"]
for i in range(len(df_mean_total)):
    var = str(df_mean_total["Name"].iloc[i])
    df_mean_total_transpose[f"{var}"]=df_mean_total.iloc[i][1:5].values

#st.dataframe(df_mean_total_transpose)

fig_event_mean = px.line(df_mean_total_transpose, x="Marker", y = df_mean_total_transpose.columns[1:], title="Historical Overall Averages", markers=True)

st.plotly_chart(fig_event_mean,use_container_width=True)