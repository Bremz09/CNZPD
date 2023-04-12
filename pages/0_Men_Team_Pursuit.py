#!/usr/bin/env python
# coding: utf-8



import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image
import numpy as np



st.set_page_config(page_title='CNZ Performance Database',
                  page_icon=":bike:",
                  layout="wide",
                  )
st.header('Men\'s Team Pursuit')
st.subheader('All results')

@st.cache_data
def get_data_from_excel():
    df = pd.read_excel(
        io='pages/MensRaceResults.xlsm',
        engine ='openpyxl',
        sheet_name='Team Pursuit',
        skiprows=0,
        usecols='A:AX',
        nrows=2000
        )
    df = df.replace(',','', regex=True)
    for i in range(len(df)):
        df["Date"][i] = df["Date"][i].date()
        #if df["125m"][i] != "NULL":
            #df["125m"][i] = df["125m"][i].strftime("%M:%S.%f")
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

#st.write(df["250m"][1]+df["125m"][1])
st.dataframe(df)
    
st.markdown("---")
    
st.title(":bar_chart: Top Ten Performances")

df_topten = df_orig.sort_values("Time").head(10)

st.dataframe(df_topten)


df_splits_tt = pd.DataFrame()
df_splits_tt["Marker"] = ["125m","250m","375m","500m","625m","750m","875m","1000m","1125m","1250m","1375m","1500m","1625m","1750m","1875m","2000m","2125m","2250m","2375m","2500m","2625m","2750m","2875m","3000m","3125m","3250m","3375m","3500m","3625m","3750m","3875m","4000m"]
for i in range(len(df_topten)):
    var = str(df_topten["Country"].iloc[i]) + " " + str(df_topten["Year"].iloc[i]) + " " +str(df_topten["Location"].iloc[i])+" " +str(df_topten["Event"].iloc[i]) + " " +str(df_topten["Stage"].iloc[i])
    df_splits_tt[f"{var}"]=df_topten.iloc[i][16:48].values

    
fig_tt = px.line(df_splits_tt, x="Marker", y = df_splits_tt.columns, title="Top Ten")

st.plotly_chart(fig_tt, use_container_width=True)

st.markdown("---")
    
st.title(":bicyclist: Country History")

#FILTERS FOR DATAFRAME

countries = df_orig['Country'].drop_duplicates().sort_values()
country = st.multiselect("Select Country:", countries)

df_countryHistory = df_orig.query(
    "Country == @country"
)

#DATAFRAME
df_countryHistory = df_countryHistory.sort_values("Time")
st.dataframe(df_countryHistory)

#FIRST FIGURE -- FINAL TIME PROGRESSION

fig_country_history = px.scatter(df_countryHistory, x="Date", y = "Time", title = "Times by Date", color="Country")
fig_country_history.update_traces(textposition="top right")

st.plotly_chart(fig_country_history, use_container_width=True)

#Second Figure -- Chart with rider names

df_splits_CH = pd.DataFrame()
df_splits_CH["Marker"] = ["125m","250m","375m","500m","625m","750m","875m","1000m","1125m","1250m","1375m","1500m","1625m","1750m","1875m","2000m","2125m","2250m","2375m","2500m","2625m","2750m","2875m","3000m","3125m","3250m","3375m","3500m","3625m","3750m","3875m","4000m"]
for i in range(len(df_countryHistory)):
    var = str(df_countryHistory["Country"].iloc[i]) + " " + str(df_countryHistory["Year"].iloc[i]) + " " +str(df_countryHistory["Event"].iloc[i]) + " " +str(df_countryHistory["Stage"].iloc[i])+ " " +str(df_countryHistory["Rider1"].iloc[i].split(" ")[0])+ " " +str(df_countryHistory["Rider2"].iloc[i].split(" ")[0])+ " " +str(df_countryHistory["Rider3"].iloc[i].split(" ")[0])+ " " +str(df_countryHistory["Rider4"].iloc[i].split(" ")[0])
    df_splits_CH[f"{var}"]=df_countryHistory.iloc[i][16:48].values

    
fig_CH = px.line(df_splits_CH, x="Marker", y = df_splits_CH.columns, title="All Rides")


st.plotly_chart(fig_CH, use_container_width=True)

#Third Figure - Worm

df_worm_CH = pd.DataFrame()
df_worm_CH["Marker"] = ["125m","250m","375m","500m","625m","750m","875m","1000m","1125m","1250m","1375m","1500m","1625m","1750m","1875m","2000m","2125m","2250m","2375m","2500m","2625m","2750m","2875m","3000m","3125m","3250m","3375m","3500m","3625m","3750m","3875m","4000m"]
for i in range(len(df_countryHistory)):
    var = str(df_countryHistory["Country"].iloc[i]) + " " + str(df_countryHistory["Year"].iloc[i]) + " " +str(df_countryHistory["Event"].iloc[i]) + " " +str(df_countryHistory["Stage"].iloc[i])+ " " +str(df_countryHistory["Rider1"].iloc[i].split(" ")[0])+ " " +str(df_countryHistory["Rider2"].iloc[i].split(" ")[0])+ " " +str(df_countryHistory["Rider3"].iloc[i].split(" ")[0])+ " " +str(df_countryHistory["Rider4"].iloc[i].split(" ")[0])
    df_worm_CH[f"{var}"]=df_countryHistory.iloc[i][16:48].values.cumsum()



fig_event_CH = px.line(df_worm_CH, x="Marker", y = df_worm_CH.columns, title="The Worm")

st.plotly_chart(fig_event_CH, use_container_width=True)




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
an_stage = st.selectbox("Select Stage:", uniqueStage)

df_an = df_an_year_location_event.query(
    "Year == @an_year & Location == @an_location & Event == @an_event & Stage == @an_stage"
)

### Splits dataframe and plot
st.write("Splits")
df_splits = pd.DataFrame()
df_splits["Marker"] = ["125m","250m","375m","500m","625m","750m","875m","1000m","1125m","1250m","1375m","1500m","1625m","1750m","1875m","2000m","2125m","2250m","2375m","2500m","2625m","2750m","2875m","3000m","3125m","3250m","3375m","3500m","3625m","3750m","3875m","4000m"]
for i in range(len(df_an)):
    var = str(df_an["Country"].iloc[i])
    df_splits[f"{var}"]=df_an.iloc[i][16:48].values

st.dataframe(df_splits)

fig_event = px.line(df_splits, x="Marker", y = df_splits.columns, title="Splits")

st.plotly_chart(fig_event, use_container_width=True)

### Worm dataframe and plot
st.write("Running Time")
df_worm = pd.DataFrame()
df_worm["Marker"] = ["125m","250m","375m","500m","625m","750m","875m","1000m","1125m","1250m","1375m","1500m","1625m","1750m","1875m","2000m","2125m","2250m","2375m","2500m","2625m","2750m","2875m","3000m","3125m","3250m","3375m","3500m","3625m","3750m","3875m","4000m"]
for i in range(len(df_an)):
    var = str(df_an["Country"].iloc[i])
    df_worm[f"{var}"]=df_an.iloc[i][16:48].values.cumsum()

st.dataframe(df_worm)

fig_event = px.line(df_worm, x="Marker", y = df_worm.columns, title="The Worm")

st.plotly_chart(fig_event, use_container_width=True)


###Markers Dataframe and plot
st.write("Random Useless thing")
st.dataframe(df_an)



fig_event = px.line(df_an, y=["250m","375m","500m","625m","750m","875m","1000m","1125m","1250m","1375m","1500m","1625m","1750m","1875m","2000m","2125m","2250m","2375m","2500m","2625m","2750m","2875m","3000m","3125m","3250m","3375m","3500m","3625m","3750m","3875m","4000m"], x = "Country", title="Pretty useless????", markers=True)
#fig_event.update_layout(legend_title="legend")
st.plotly_chart(fig_event, use_container_width=True)






    
