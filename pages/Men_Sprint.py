#!/usr/bin/env python
# coding: utf-8



import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image
import datetime





st.set_page_config(page_title='CNZ Performance Database',
                  page_icon=":bike:",
                  layout="wide")
st.header('Men\'s Sprint')
st.subheader('All results')

@st.cache_data
def get_data_from_excel():
    df = pd.read_excel(
        io='pages/MensRaceResults.xlsm',
        engine ='openpyxl',
        sheet_name='Sprint',
        skiprows=0,
        usecols='A:S',
        nrows=1137
        )
    df = df.replace(',','')
    df['Date'] = pd.to_datetime(df['Date']).dt.date
    return df
df= get_data_from_excel()

def get_points_data_from_excel():
    df = pd.read_excel(
        io='pages/MensSprintPoints.xlsm',
        engine ='openpyxl',
        sheet_name='MensSprintPoints',
        skiprows=0,
        usecols='A:J',
        nrows=3000
        )
    df = df.replace(',','')
    df['Date'] = pd.to_datetime(df['Date']).dt.date
    return df
df_points = get_points_data_from_excel()

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
    
st.title(":bicyclist: Athlete History")

athletes = df_orig['Athlete'].drop_duplicates().sort_values()
athlete = st.multiselect("Select Athlete(s):", athletes)

df_athleteHistory = df_orig.query(
    "Athlete == @athlete"
)

st.dataframe(df_athleteHistory)

fig_athlete_history = px.line(df_athleteHistory, x="Date", y = ["200m R1"], title = "Times by Date", markers = "True", text = "Location", color="Athlete")
fig_athlete_history.update_traces(textposition="top right")

st.plotly_chart(fig_athlete_history)

fig_athlete_history = px.line(df_athleteHistory, x="Date", y = "Final_Rank", title = "Rank by Date", markers = "True", color="Athlete")
fig_athlete_history.update_traces(textposition="top right")

st.plotly_chart(fig_athlete_history)

fig_athlete_history = px.line(df_athleteHistory, x="Age", y = ["200m R1"], title = "R1 Times by Age", markers = "True", color="Athlete")
fig_athlete_history.update_traces(textposition="top right")

st.plotly_chart(fig_athlete_history)

fig_athlete_history = px.line(df_athleteHistory, x="Age", y = "200m R2", title = "R2 Times by Age", markers = "True", color="Athlete")


st.plotly_chart(fig_athlete_history)

fig_athlete_history = px.line(df_athleteHistory, x="Age", y = "200m R3", title = "R3 Times by Age", markers = "True", color="Athlete")


st.plotly_chart(fig_athlete_history)


# st.markdown("---")
    
# st.title(":mag_right: Race Analysis Tool")
# uniqueYear = df_orig['Year'].drop_duplicates().sort_values(ascending=False)


# left_column, middle_column, right_column = st.columns(3)
# with left_column:
#     an_year = st.selectbox("Select Year:", uniqueYear)
    
# df_an_year = df_orig.query(
#     "Year == @an_year"
# )
# uniqueLocation = df_an_year['Location'].drop_duplicates().sort_values()

# with middle_column:
#     an_location = st.selectbox("Select Location:", uniqueLocation)
    
# df_an_year_location = df_an_year.query(
#     "Year == @an_year & Location == @an_location"
# )
    
# uniqueEvent = df_an_year_location['Event'].drop_duplicates().sort_values()
# with right_column:
#     an_event = st.selectbox("Select Event:", uniqueEvent)

# df_an = df_an_year_location.query(
#     "Year == @an_year & Location == @an_location & Event == @an_event"
# )

# st.dataframe(df_an)

# df_and=df_an



# fig_event = px.line(df_an, y=["100m","200m"], x = "Athlete")

# st.plotly_chart(fig_event)

#t.write(df_and["100m"])








st.markdown("---")
    
st.title(":date: Points Tool")

dates = df_points['Date'].drop_duplicates().sort_values()

today = datetime.date.today()
year_ago = today + datetime.timedelta(days=-365)


start_date = st.date_input('Period Start:', year_ago)
end_date = st.date_input('Period Finish:', today)
df_points_dates = df_points[(df_points['Date'] > start_date) & (df_points['Date'] < end_date)]
st.write("Number of days: "+str((end_date-start_date).days))

df_points_dates=df_points_dates.sort_values("Current_Rank")

st.dataframe(df_points_dates)
#df_points_topten = df_points.sort_values("Time").head(10)

names = df_points_dates['Name'].drop_duplicates()


df_grouped = df_points_dates.groupby(by="Name")["Points"].sum()

df_grouped = df_grouped.to_frame()
df_grouped = df_grouped.sort_values(by="Points",ascending=False)
    
st.header(":moneybag: Top 50")
df_grouped.insert(0, 'Rank', range(1, 1+len(df_grouped)))
st.dataframe(df_grouped.head(50))
