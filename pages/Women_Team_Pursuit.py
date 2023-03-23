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
                  layout="wide")
st.header('Women\'s Team Pursuit')
st.subheader('All results')

@st.cache_data
def get_data_from_excel():
    df = pd.read_excel(
        io='pages/WomensRaceResults.xlsm',
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
    var = str(df_topten["Country"].iloc[i]) + " " + str(df_topten["Year"].iloc[i]) + " " +str(df_topten["Event"].iloc[i]) + " " +str(df_topten["Stage"].iloc[i])
    df_splits_tt[f"{var}"]=df_topten.iloc[i][16:48].values

    
fig_tt = px.line(df_splits_tt, x="Marker", y = df_splits_tt.columns, title="Splits")

st.plotly_chart(fig_tt)

st.markdown("---")
    
st.title(":bicyclist: Country History")

#FILTERS FOR DATAFRAME

countries = df_orig['Country'].drop_duplicates().sort_values()
country = st.multiselect("Select Country:", countries)

df_countryHistory = df_orig.query(
    "Country == @country"
)

#DATAFRAME

st.dataframe(df_countryHistory)

#FIRST FIGURE -- FINAL TIME PROGRESSION

fig_country_history = px.line(df_countryHistory, x="Date", y = "Time", title = "Times by Date", markers = "True", color="Country")
fig_country_history.update_traces(textposition="top right")

st.plotly_chart(fig_country_history)

#Could try do an average age thing here

# fig_athlete_history = px.line(df_athleteHistory, x="Age", y = "200m", title = "Times by Age", markers = "True", color="Athlete")
# fig_athlete_history.update_traces(textposition="top right")

# st.plotly_chart(fig_athlete_history)




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

st.plotly_chart(fig_event)

### Worm dataframe and plot
st.write("Running Time")
df_worm = pd.DataFrame()
df_worm["Marker"] = ["125m","250m","375m","500m","625m","750m","875m","1000m","1125m","1250m","1375m","1500m","1625m","1750m","1875m","2000m","2125m","2250m","2375m","2500m","2625m","2750m","2875m","3000m","3125m","3250m","3375m","3500m","3625m","3750m","3875m","4000m"]
for i in range(len(df_an)):
    var = str(df_an["Country"].iloc[i])
    df_worm[f"{var}"]=df_an.iloc[i][16:48].values.cumsum()

st.dataframe(df_worm)

fig_event = px.line(df_worm, x="Marker", y = df_worm.columns, title="The Worm")

st.plotly_chart(fig_event)


###Markers Dataframe and plot
st.write("Random Useless thing")
st.dataframe(df_an)

st.title(":two_women_holding_hands: Head to Head")
st.subheader("Select First Athlete Ride")

### HEAD TO HEAD


hh_uniqueAthlete = df_orig['Country'].drop_duplicates().sort_values(ascending=True)

left_column, middle_column, right_column = st.columns(3)
with left_column:
    hh_athlete = st.selectbox("Select Country:", hh_uniqueAthlete, key="hh_athlete")
    
df_hh_athlete = df_orig.query(
    "Country == @hh_athlete"
)
hh_uniqueYear = df_hh_athlete['Year'].drop_duplicates().sort_values()



with middle_column:
    hh_year = st.selectbox("Select Year:", hh_uniqueYear, key="hh_year")
    
df_hh_athlete_year = df_hh_athlete.query(
    "Year == @hh_year & Country == @hh_athlete"
)
    
hh_uniqueLocation = df_hh_athlete_year['Location'].drop_duplicates().sort_values()
with right_column:
    hh_location = st.selectbox("Select Location:", hh_uniqueLocation, key="hh_location")

df_hh_athlete_year_location = df_hh_athlete_year.query(
    "Year == @hh_year & Location == @hh_location & Country == @hh_athlete"
)

hh_uniqueEvent = df_hh_athlete_year_location['Event'].drop_duplicates().sort_values(ascending=True)



left_column, middle_column, right_column = st.columns(3)
with left_column:
    hh_event = st.selectbox("Select Event:", hh_uniqueEvent, key="hh_event")
    
df_hh_athlete_year_location_event = df_hh_athlete_year_location.query(
    "Year == @hh_year & Location == @hh_location & Country == @hh_athlete & Event == @hh_event"
)

hh_uniqueStage = df_hh_athlete_year_location_event['Stage'].drop_duplicates().sort_values()

with middle_column:
    hh_stage = st.selectbox("Select Stage:", hh_uniqueStage, key="hh_stage")
    
df_hh_final = df_hh_athlete_year_location_event.query(
    "Year == @hh_year & Location == @hh_location & Country == @hh_athlete & Event == @hh_event & Stage == @hh_stage"
)

st.dataframe(df_hh_final)



### HEAD TO HEAD RIDER 2 

st.subheader("Select Second Country Ride")

hh2_uniqueAthlete = df_orig['Country'].drop_duplicates().sort_values(ascending=True)

left_column, middle_column, right_column = st.columns(3)
with left_column:
    hh2_athlete = st.selectbox("Select Country:", hh2_uniqueAthlete, key="hh2_athlete")
    
df_hh2_athlete = df_orig.query(
    "Country == @hh2_athlete"
)
hh2_uniqueYear = df_hh2_athlete['Year'].drop_duplicates().sort_values()



with middle_column:
    hh2_year = st.selectbox("Select Year:", hh2_uniqueYear, key="hh2_year")
    
df_hh2_athlete_year = df_hh2_athlete.query(
    "Year == @hh2_year & Country == @hh2_athlete"
)
    
hh2_uniqueLocation = df_hh2_athlete_year['Location'].drop_duplicates().sort_values()
with right_column:
    hh2_location = st.selectbox("Select Location:", hh2_uniqueLocation, key="hh2_location")

df_hh2_athlete_year_location = df_hh2_athlete_year.query(
    "Year == @hh2_year & Location == @hh2_location & Country == @hh2_athlete"
)

hh2_uniqueEvent = df_hh2_athlete_year_location['Event'].drop_duplicates().sort_values(ascending=True)



left_column, middle_column, right_column = st.columns(3)
with left_column:
    hh2_event = st.selectbox("Select Event:", hh2_uniqueEvent, key="hh2_event")
    
df_hh2_athlete_year_location_event = df_hh2_athlete_year_location.query(
    "Year == @hh2_year & Location == @hh2_location & Country == @hh2_athlete & Event == @hh2_event"
)

hh2_uniqueStage = df_hh2_athlete_year_location_event['Stage'].drop_duplicates().sort_values()

with middle_column:
    hh2_stage = st.selectbox("Select Stage:", hh2_uniqueStage, key="hh2_stage")
    
df_hh2_final = df_hh2_athlete_year_location_event.query(
    "Year == @hh2_year & Location == @hh2_location & Country == @hh2_athlete & Event == @hh2_event & Stage == @hh2_stage"
)

st.dataframe(df_hh2_final)

merge = [df_hh_final,df_hh2_final]

df_hh_comp = pd.concat(merge)
st.subheader("Comparison")

df_hh_splits = pd.DataFrame()
df_hh_splits["Marker"] = ["125m","250m","375m","500m","625m","750m","875m","1000m","1125m","1250m","1375m","1500m","1625m","1750m","1875m","2000m","2125m","2250m","2375m","2500m","2625m","2750m","2875m","3000m","3125m","3250m","3375m","3500m","3625m","3750m","3875m","4000m"]

var1 = str(df_hh_comp["Country"].iloc[0] + " " +str(df_hh_comp["Year"].iloc[0]))
df_hh_splits[f"{var1}"]=df_an.iloc[0][16:48].values

var2 = str(df_hh_comp["Country"].iloc[1] + " " +str(df_hh_comp["Year"].iloc[1]))
df_hh_splits[f"{var2}"]=df_an.iloc[1][16:48].values

st.dataframe(df_hh_splits)

fig_hh=px.line(df_hh_splits,x="Marker", y=df_hh_splits.columns) # fill down to xaxis

st.plotly_chart(fig_hh)





    
