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
st.header('Men\'s 1k Time Trial')
st.subheader('All results')
marker=["125m","250m","375m","500m","625m","750m","875m","1000m"]
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
@st.cache_data
def convert_to_csv(df):
    return df.to_csv(index=False,sep = ",").encode('utf-32')
c1,c2,c3=st.columns(3)
df_orig = df
with c1:
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


with c2:
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
with c3:
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
    label="Download Time Trial Data as CSV",
    data=csv,
    file_name='TT_Data.csv',
    mime='text/csv',
    key="tt1"
)
buffer = io.BytesIO()
with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
    df.to_excel(writer, sheet_name='Sheet1', index=False)
    writer.save()
    download2 = st.download_button(
        label="Download Time Trial Data as Excel",
        data=buffer,
        file_name='TT_Data.xlsx',
        mime='application/vnd.ms-excel',
    key="tt2"
    )
##Download buttons complete
st.markdown("---")
    
st.title(":bar_chart: Top Ten Performances")

df_topten = df_orig.sort_values('Time').head(10)

st.dataframe(df_topten,use_container_width=True)

##Download buttons
csvtt = convert_to_csv(df_topten)
download1 = st.download_button(
    label="Download Top Ten Data as CSV",
    data=csvtt,
    file_name='TT_Data.csv',
    mime='text/csv',
    key="tttt1"
)
buffertt = io.BytesIO()
with pd.ExcelWriter(buffertt, engine='xlsxwriter') as writer:
    df_topten.to_excel(writer, sheet_name='Sheet1', index=False)
    writer.save()
    download2 = st.download_button(
        label="Download Top Ten Data as Excel",
        data=buffertt,
        file_name='TT_Data.xlsx',
        mime='application/vnd.ms-excel',
    key="tttt2"
    )
##Download buttons complete

df_splits_tt = pd.DataFrame()
df_splits_tt["Marker"] = marker
for i in range(len(df_topten)):
    var = str(i+1)+" "+str(df_topten["Country"].iloc[i]) + " " + str(df_topten["Year"].iloc[i]) + " " +str(df_topten["Location"].iloc[i])+" " +str(df_topten["Event"].iloc[i]) + " " +str(df_topten["Stage"].iloc[i])
    df_splits_tt[f"{var}"]=df_topten.iloc[i][9:17].values

    
fig_tt = px.line(df_splits_tt, x="Marker", y = df_splits_tt.columns, title="Top Ten")

st.plotly_chart(fig_tt, use_container_width=True)

st.markdown("---")
    
st.title(":bicyclist: Athlete History")

athletes = df_orig['Athlete'].drop_duplicates().sort_values()
athlete = st.multiselect("Select Athlete(s):", athletes)
if len(athlete)>0:
    df_athleteHistory = df_orig.query(
        "Athlete == @athlete"
    )

    st.dataframe(df_athleteHistory,use_container_width=True)
    ##Download buttons
    csvah = convert_to_csv(df_athleteHistory)
    download1 = st.download_button(
        label="Download Athlete History as CSV",
        data=csvah,
        file_name='Athlete_History_Data.csv',
        mime='text/csv',
        key="ttah1"
    )
    bufferah = io.BytesIO()
    with pd.ExcelWriter(bufferah, engine='xlsxwriter') as writer:
        df_athleteHistory.to_excel(writer, sheet_name='Sheet1', index=False)
        writer.save()
        download2 = st.download_button(
            label="Download Athlete History as Excel",
            data=bufferah,
            file_name='Athlete_History_Data.xlsx',
            mime='application/vnd.ms-excel',
        key="ttah2"
        )
    ##Download buttons complete
    
    df_athleteHistory_sh = df_athleteHistory[(df_athleteHistory.Rank != "DSQ") & (df_athleteHistory.Rank != "DNF")]
    ##First Figure -- All Races
    df_ah_Trans,df_ch_worm = pd.DataFrame(),pd.DataFrame()
    df_ah_Trans["Distance"],df_ch_worm["Distance"] = marker,marker
    for i in range(len(df_athleteHistory_sh)):
        var =str(i+1)+" "+str(df_athleteHistory_sh["Athlete"].iloc[i])+" "+str(df_athleteHistory_sh["Location"].iloc[i])+" "+str(df_athleteHistory_sh["Event"].iloc[i])+" "+str(df_athleteHistory_sh["Stage"].iloc[i])+" "+str(df_athleteHistory_sh["Year"].iloc[i])
        df_ah_Trans[f"{var}"]=df_athleteHistory_sh.iloc[i][9:17].values
        df_ch_worm[f"{var}"]=df_athleteHistory_sh.iloc[i][9:17].values.cumsum()

    fig_event = px.line(df_ah_Trans, x="Distance", y = df_ah_Trans.columns, title="All races", markers=True)
    st.plotly_chart(fig_event,use_container_width=True)
    ##Second Figure -- The Worm
    
    fig_event_CH = px.line(df_ch_worm, x="Distance", y = df_ch_worm.columns, title="The Worm")
    st.plotly_chart(fig_event_CH, use_container_width=True)
    
    #Third Figure -- Ranges
    fig_ranges_CH = px.line(df_athleteHistory, x=df_ch_worm.columns[1:], y = marker, title="The Ranges",markers=True)
    st.plotly_chart(fig_ranges_CH, use_container_width=True)
    
    fig_athlete_history = px.line(df_athleteHistory, x="Date", y = "Time", title = "Times by Date", markers = "True", text = "Location", color="Athlete")
    fig_athlete_history.update_traces(textposition="top right")

    st.plotly_chart(fig_athlete_history,use_container_width=True)

    fig_athlete_history = px.line(df_athleteHistory, x="Date", y = "Rank", title = "Rank by Date", markers = "True", color="Athlete")
    fig_athlete_history.update_traces(textposition="top right")

    st.plotly_chart(fig_athlete_history,use_container_width=True)

    fig_athlete_history = px.line(df_athleteHistory, x="Age", y = "Time", title = "Times by Age", markers = "True", color="Athlete")
    fig_athlete_history.update_traces(textposition="top right")

    st.plotly_chart(fig_athlete_history,use_container_width=True)

    df_athleteHistory["Half"] = df_athleteHistory["125m"]+df_athleteHistory["250m"]+df_athleteHistory["375m"]+df_athleteHistory["500m"]

    fig_athlete_history = px.line(df_athleteHistory, x="Age", y = "Half", title = "500m Times by Age", markers = "True", color="Athlete")


    st.plotly_chart(fig_athlete_history,use_container_width=True)




st.markdown("---")
    
st.title(":mag_right: Race Analysis Tool")
uniqueYear = df_orig['Year'].drop_duplicates().sort_values(ascending=False)


left_column, middle_column, right_column,c4 = st.columns(4)
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


with c4:
    an_stage = st.selectbox("Select Stage:", uniqueStage)
    
df_an = df_an_year_location_event.query(
    "Year == @an_year & Location == @an_location & Event == @an_event & Stage == @an_stage"
)

st.dataframe(df_an,use_container_width=True)
df_splits = pd.DataFrame()
df_splits["Marker"] = ["125m","250m","375m","500m","625m","750m","875m","1000m"]
for i in range(len(df_an)):
    var = str(df_an["Athlete"].iloc[i])
    df_splits[f"{var}"]=df_an.iloc[i][9:17].values

fig_event = px.line(df_splits, x="Marker", y = df_splits.columns, title="Splits")

st.plotly_chart(fig_event, use_container_width=True)    
    
### Worm dataframe and plot
# st.write("Running Time")
df_worm = pd.DataFrame()
df_worm["Marker"] = ["125m","250m","375m","500m","625m","750m","875m","1000m"]

for i in range(len(df_an)):
    var = str(df_an["Athlete"].iloc[i])
    df_worm[f"{var}"]=df_an.iloc[i][9:17].values.cumsum()



fig_event = px.line(df_worm, x="Marker", y = df_worm.columns, title="The Worm")

st.plotly_chart(fig_event,use_container_width=True)




fig_event = px.line(df_an, y=["125m","250m","375m","500m","625m","750m","875m","1000m"], x = "Athlete", title="The Ranges")

st.plotly_chart(fig_event,use_container_width=True)




