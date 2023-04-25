#!/usr/bin/env python
# coding: utf-8



import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image
import io




st.set_page_config(page_title='CNZ Performance Database',
                  page_icon=":bike:",
                  layout="wide")
st.header('Women\'s Sprint Qualifying')




@st.cache_data
def get_data_from_excel():
    df = pd.read_excel(
        io='pages/WomensRaceResults.xlsm',
        engine ='openpyxl',
        sheet_name='Sprint Qual',
        skiprows=0,
        usecols='A:M',
        nrows=2000
        )
    df = df.replace(',','')
    #df['Date'] = pd.to_datetime(df['Date']).dt.date
    return df
df= get_data_from_excel()


def get_dev_data_from_excel():
    df_dev = pd.read_excel(
        io='pages/SprintPerformanceDatabase.xlsx',
        engine ='openpyxl',
        sheet_name='Sprint Qual Women',
        skiprows=0,
        usecols='A:M',
        nrows=3000
        )
    df_dev = df_dev.replace(',','')
    #df['Date'] = pd.to_datetime(df['Date']).dt.date
    return df_dev
df_dev= get_dev_data_from_excel()
@st.cache_data
def convert_to_csv(df):
    return df.to_csv(index=False,sep = ",").encode('utf-32')

col1, col2, col3, col4 = st.columns(4)
with col1:

    Devs = ["No","Yes"]
    Dev = st.selectbox("Include Age Grade Competitions?:", Devs, key="Dev_selector")

    if Dev == "Yes":
        df = pd.concat([df,df_dev])
        df=df.sort_values("Date", ascending=False)

with col2:
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

with col3:
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
        
        
with col4:
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

    
st.dataframe(df,use_container_width=True)
##Download buttons
csv = convert_to_csv(df)
download1 = st.download_button(
    label="Download sprint qualifying data as CSV",
    data=csv,
    file_name='Sprint_Qual_Data.csv',
    mime='text/csv',
    key="buffer1"
)
buffer = io.BytesIO()
with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
    df.to_excel(writer, sheet_name='Sheet1', index=False)
    writer.save()
    download2 = st.download_button(
        label="Download sprint qualifying data as Excel",
        data=buffer,
        file_name='Sprint_Qual_Data.xlsx',
        mime='application/vnd.ms-excel',
        key="buffer2"
    )
##Download buttons complete
    
st.markdown("---")
    
st.title(":bar_chart: Top Ten Performances")

df_topten = df_orig.sort_values('200m').head(10)

st.dataframe(df_topten,use_container_width=True)

##Download buttons
csv_tt = convert_to_csv(df_topten)
download1 = st.download_button(
    label="Download top ten data as CSV",
    data=csv_tt,
    file_name='Sprint_Qual_Data.csv',
    mime='text/csv',
    key="buffertt1"
)
buffer_tt = io.BytesIO()
with pd.ExcelWriter(buffer_tt, engine='xlsxwriter') as writer:
    df_topten.to_excel(writer, sheet_name='Sheet1', index=False)
    writer.save()
    download2 = st.download_button(
        label="Download top ten data as Excel",
        data=buffer_tt,
        file_name='Sprint_Qual_Data.xlsx',
        mime='application/vnd.ms-excel',
        key="buffertt2"
    )
##Download buttons complete

st.markdown("---")
    
st.title(":bicyclist: Athlete History")

athletes = df_orig['Athlete'].drop_duplicates().sort_values()
athlete = st.multiselect("Select Athlete(s):", athletes)

df_athleteHistory = df_orig.query(
    "Athlete == @athlete"
)
df_athleteHistory=df_athleteHistory.sort_values("Date",ascending=False)
if len(athlete) !=0:
    st.dataframe(df_athleteHistory,use_container_width=True)
    ##Download buttons
    csv_ah = convert_to_csv(df_athleteHistory)
    download1 = st.download_button(
        label="Download athlete history data as CSV",
        data=csv_ah,
        file_name='Sprint_Qual_Data.csv',
        mime='text/csv',
        key="bufferah1"
    )
    buffer_ah = io.BytesIO()
    with pd.ExcelWriter(buffer_ah, engine='xlsxwriter') as writer:
        df_athleteHistory.to_excel(writer, sheet_name='Sheet1', index=False)
        writer.save()
        download2 = st.download_button(
            label="Download athlete history data as Excel",
            data=buffer_ah,
            file_name='Sprint_Qual_Data.xlsx',
            mime='application/vnd.ms-excel',
            key="bufferah2"
        )
    ##Download buttons complete
    
    #First Figure -- All races

    df_splits_CH = pd.DataFrame()
    df_splits_CH["Marker"] = ["100m","200m"]
    for i in range(len(df_athleteHistory)):
        var = str(i+1)+" " +str(df_athleteHistory["Athlete"].iloc[i]) + " " + str(df_athleteHistory["Year"].iloc[i]) + " " +str(df_athleteHistory["Event"].iloc[i]) + " " +str(df_athleteHistory["Location"].iloc[i])
        df_splits_CH[f"{var}"]=df_athleteHistory.iloc[i][8:10].values
    fig_CH = px.line(df_splits_CH, x="Marker", y = df_splits_CH.columns, title="All Rides")
    st.plotly_chart(fig_CH, use_container_width=True)
    
    ##Second Figure -- 200m times by Date
    fig_athlete_history = px.line(df_athleteHistory, x="Date", y = "200m", title = "Times by Date", markers = "True", text = "Location", color="Athlete")
    fig_athlete_history.update_traces(textposition="top right")
    st.plotly_chart(fig_athlete_history,use_container_width=True)
    ##Third Figure -- Rank by Date
    fig_athlete_history = px.line(df_athleteHistory, x="Date", y = "Rank", title = "Rank by Date", markers = "True", color="Athlete")
    fig_athlete_history.update_traces(textposition="top right")
    st.plotly_chart(fig_athlete_history,use_container_width=True)
    
    ##Fourth Figure -- 200m times by Age
    fig_athlete_history = px.line(df_athleteHistory, x="Age", y = "200m", title = "Times by Age", markers = "True", color="Athlete")
    fig_athlete_history.update_traces(textposition="top right")
    st.plotly_chart(fig_athlete_history,use_container_width=True)
    
    ##Fifth Figure -- 100m times by Age    
    fig_athlete_history = px.line(df_athleteHistory, x="Age", y = "100m", title = "100m Times by Age", markers = "True", color="Athlete")
    st.plotly_chart(fig_athlete_history,use_container_width=True)
    
    ##Sixth Figure -- 100-200m times by Age
    fig_athlete_history = px.line(df_athleteHistory, x="Age", y = "100-200m", title = "100-200m Times by Age", markers = "True", color="Athlete")
    st.plotly_chart(fig_athlete_history,use_container_width=True)


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

st.dataframe(df_an,use_container_width=True)



fig_event = px.line(df_an, y=["100m","200m","Diff"], x = "Athlete")

st.plotly_chart(fig_event,use_container_width=True)




