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
st.header('Men\'s Madison')
st.subheader('All results')

@st.cache_data
def get_data_from_excel():
    df = pd.read_excel(
        io='pages/MensRaceResults.xlsm',
        engine ='openpyxl',
        sheet_name='Madison',
        skiprows=0,
        usecols='A:AI',
        nrows=599
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
    
st.title(":bicyclist: Event History")

countries = df_orig['Country'].drop_duplicates().sort_values()
country = st.multiselect("Select Country(s):", countries)

df_countryHistory = df_orig.query(
    "Country == @country"
)

## Totals by Date -- DB and plot

st.dataframe(df_countryHistory)

fig_country_history = px.line(df_countryHistory, x="Date", y = "Total", title = "Totals by Date", markers = "True", text = "Location", color="Country")
fig_country_history.update_traces(textposition="top right")

st.plotly_chart(fig_country_history)

## Ranks by Date -- DB and plot

fig_country_history = px.line(df_countryHistory, x="Date", y = "Rank", title = "Rank by Date", markers = "True", color="Country")
#fig_country_history.update_traces(textposition="top right")

st.plotly_chart(fig_country_history)

## Laps taken by date -- DB and plot

fig_country_history = px.line(df_countryHistory, x="Date", y = "P.Laps", title = "Laps Taken by Date", markers = "True", color="Country")
#fig_country_history.update_traces(textposition="top right")

st.plotly_chart(fig_country_history)

## Laps lost by date -- DB and plot

fig_country_history = px.line(df_countryHistory, x="Date", y = "M.Laps", title = "Laps Lost by Date", markers = "True", color="Country")


st.plotly_chart(fig_country_history)




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

### Splits dataframe and plot
st.write("Splits")
df_splits = pd.DataFrame()
df_splits["Marker"] = ["Sprint 1","Sprint 2","Sprint 3","Sprint 4","Sprint 5","Sprint 6","Sprint 7","Sprint 8","Sprint 9","Sprint 10","Sprint 11","Sprint 12","Sprint 13","Sprint 14","Sprint 15","Sprint 16","Sprint 17","Sprint 18","Sprint 19","Sprint 20"]
for i in range(len(df_an)):
    var = str(df_an["Country"].iloc[i])
    df_splits[f"{var}"]=df_an.iloc[i][11:31].values

st.dataframe(df_splits)

fig_event = px.line(df_splits, x="Marker", y = df_splits.columns, title="Splits", markers=True)

st.plotly_chart(fig_event)

### Worm dataframe and plot
st.write("Running Time")
df_worm = pd.DataFrame()
df_worm["Marker"] = ["Sprint 1","Sprint 2","Sprint 3","Sprint 4","Sprint 5","Sprint 6","Sprint 7","Sprint 8","Sprint 9","Sprint 10","Sprint 11","Sprint 12","Sprint 13","Sprint 14","Sprint 15","Sprint 16","Sprint 17","Sprint 18","Sprint 19","Sprint 20"]
for i in range(len(df_an)):
    var = str(df_an["Country"].iloc[i])
    df_worm[f"{var}"]=df_an.iloc[i][11:31].values.cumsum()

st.dataframe(df_worm)

fig_event = px.line(df_worm, x="Marker", y = df_worm.columns, title="The Worm")

st.plotly_chart(fig_event)


###Markers Dataframe and plot
st.write("Random Useless thing")
st.dataframe(df_an)



fig_event = px.line(df_an, y=["Sprint 1","Sprint 2","Sprint 3","Sprint 4","Sprint 5","Sprint 6","Sprint 7","Sprint 8","Sprint 9","Sprint 10","Sprint 11","Sprint 12","Sprint 13","Sprint 14","Sprint 15","Sprint 16","Sprint 17","Sprint 18","Sprint 19","Sprint 20"], x = "Country", title="Pretty useless????", markers=True)
#fig_event.update_layout(legend_title="legend")
st.plotly_chart(fig_event)

