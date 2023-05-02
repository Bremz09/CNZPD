#!/usr/bin/env python
# coding: utf-8



import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image
import numpy as np
import io



st.set_page_config(page_title='CNZ Performance Database',
                  page_icon=":bike:",
                  layout="wide")
st.header('Men\'s Individual Pursuit')
st.subheader('All results')
marker = ["125m","250m","375m","500m","625m","750m","875m","1000m","1125m","1250m","1375m","1500m","1625m","1750m","1875m","2000m","2125m","2250m","2375m","2500m","2625m","2750m","2875m","3000m","3125m","3250m","3375m","3500m","3625m","3750m","3875m","4000m"]
markerx = [125,250,375,500,625,750,875,1000,1125,1250,1375,1500,1625,1750,1875,2000,2125,2250,2375,2500,2625,2750,2875,3000,3125,3250,3375,3500,3625,3750,3875,4000]
@st.cache_data
def get_data_from_excel():
    df = pd.read_excel(
        io='pages/MensRaceResults.xlsm',
        engine ='openpyxl',
        sheet_name='Individual Pursuit',
        skiprows=0,
        usecols='A:AQ',
        nrows=2500
        )
    df = df.replace(',','', regex=True)
    for i in range(len(df)):
        df["Date"][i] = df["Date"][i].date()
        #if df["125m"][i] != "NULL":
            #df["125m"][i] = df["125m"][i].strftime("%M:%S.%f")
    return df
df= get_data_from_excel()
@st.cache_data
def convert_to_csv(df):
    return df.to_csv(index=False,sep = ",").encode('utf-32')
df_orig = df
c1,c2,c3=st.columns(3)
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
#DOWNLOAD BUTTONS
csv = convert_to_csv(df)
buffer = io.BytesIO()
download1 = st.download_button(
    label="Download IP data as CSV",
    data=csv,
    file_name='IP_Data.csv',
    mime='text/csv',
    key="IP1"
)
with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
    df.to_excel(writer, sheet_name='Sheet1', index=False)
    writer.save()
    download2 = st.download_button(
        label="Download IP data as Excel",
        data=buffer,
        file_name='IP_Data.xlsx',
        mime='application/vnd.ms-excel',
        key="IP2"
    )

##Download buttons complete
st.markdown("---")
    
st.title(":bar_chart: Top Ten Performances")

df_topten = df_orig.sort_values("Time").head(10)

st.dataframe(df_topten)
#DOWNLOAD BUTTONS
csvtt = convert_to_csv(df_topten)
buffertt = io.BytesIO()
download1 = st.download_button(
    label="Download Top Ten as CSV",
    data=csvtt,
    file_name='IP_Top_Ten_Data.csv',
    mime='text/csv',
    key="IPtt1"
)
with pd.ExcelWriter(buffertt, engine='xlsxwriter') as writer:
    df_topten.to_excel(writer, sheet_name='Sheet1', index=False)
    writer.save()
    download2 = st.download_button(
        label="Download Top Ten as Excel",
        data=buffertt,
        file_name='IP_Top_Ten_Data.xlsx',
        mime='application/vnd.ms-excel',
        key="IPtt2"
    )

##Download buttons complete
st.markdown("---")
    
st.title(":bicyclist: Athlete History")

#FILTERS FOR DATAFRAME

athletes = df_orig['Athlete'].drop_duplicates().sort_values()
athlete = st.multiselect("Select Athlete(s):", athletes)

df_athleteHistory = df_orig.query(
    "Athlete == @athlete"
)

if len(athlete)>0:
    st.dataframe(df_athleteHistory,use_container_width=True)
    #DOWNLOAD BUTTONS
    csvah = convert_to_csv(df_athleteHistory)
    buffertt = io.BytesIO()
    download1 = st.download_button(
        label="Download Athlete History as CSV",
        data=csvah,
        file_name='IP_Athlete_History_Data.csv',
        mime='text/csv',
        key="IPah1"
    )
    with pd.ExcelWriter(buffertt, engine='xlsxwriter') as writer:
        df_athleteHistory.to_excel(writer, sheet_name='Sheet1', index=False)
        writer.save()
        download2 = st.download_button(
            label="Download Athlete History as Excel",
            data=buffertt,
            file_name='IP_Athlete_History_Data.xlsx',
            mime='application/vnd.ms-excel',
            key="IPah2"
        )
    ##Download buttons complete

    df_splits_CH = pd.DataFrame()
    df_splits_CH["Marker"] = marker
    df_worm_CH = pd.DataFrame()
    df_worm_CH["Marker"] = marker
    for i in range(len(df_athleteHistory)):
        var = str(i+1)+" "+str(df_athleteHistory["Athlete"].iloc[i])+" "+str(df_athleteHistory["Location"].iloc[i]) + " " + str(df_athleteHistory["Year"].iloc[i]) + " " +str(df_athleteHistory["Event"].iloc[i]) + " " +str(df_athleteHistory["Stage"].iloc[i])
        df_splits_CH[f"{var}"]=df_athleteHistory.iloc[i][9:41].values
        df_worm_CH[f"{var}"]=df_athleteHistory.iloc[i][9:41].values.cumsum()


    fig_CH = px.line(df_splits_CH, x="Marker", y = df_splits_CH.columns, title="Splits")
    st.plotly_chart(fig_CH, use_container_width=True)

    #Third Figure - Worm

    fig_event_CH = px.line(df_worm_CH, x="Marker", y = df_worm_CH.columns, title="The Worm")
    st.plotly_chart(fig_event_CH, use_container_width=True)

    #Fourth Figure - Ranges
    fig_ranges_CH = px.line(df_athleteHistory, x=df_splits_CH.columns[1:], y = markerx, title="The Ranges",markers=True)
    st.plotly_chart(fig_ranges_CH, use_container_width=True)


    #FIRST FIGURE -- FINAL TIME PROGRESSION

    fig_athlete_history = px.line(df_athleteHistory, x="Date", y = "Time", title = "Times by Date", markers = "True", color="Athlete")
    fig_athlete_history.update_traces(textposition="top right")

    st.plotly_chart(fig_athlete_history,use_container_width=True)

    ### Time by Age

    fig_athlete_history = px.line(df_athleteHistory, x="Age", y = "Time", title = "Times by Age", markers = "True", color="Athlete")
    fig_athlete_history.update_traces(textposition="top right")

    st.plotly_chart(fig_athlete_history,use_container_width=True)




st.markdown("---")

st.title(":mag_right: Race Analysis Tool")
uniqueYear = df_orig['Year'].drop_duplicates().sort_values(ascending=False)


left_column, middle_column, right_column,col4 = st.columns(4)
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


with col4:

    uniqueStage = df_an_year_location_event['Stage'].drop_duplicates().sort_values()
    an_stage = st.selectbox("Select Stage:", uniqueStage)

df_an = df_an_year_location_event.query(
    "Year == @an_year & Location == @an_location & Event == @an_event & Stage == @an_stage"
)



### Splits dataframe and plot
st.dataframe(df_an)
df_splits,df_worm = pd.DataFrame(),pd.DataFrame()
df_splits["Marker"],df_worm["Marker"] = marker,marker
for i in range(len(df_an)):
    var = str(df_an["Rank"].iloc[i])+ " "+ str(df_an["Athlete"].iloc[i])
    df_splits[f"{var}"]=df_an.iloc[i][9:41].values
    df_worm[f"{var}"]=df_an.iloc[i][9:41].values.cumsum()

fig_event = px.line(df_splits, x="Marker", y = df_splits.columns, title="Splits")

st.plotly_chart(fig_event,use_container_width=True)

### Worm dataframe and plot
# st.write("Running Time")
# df_worm = pd.DataFrame()
# df_worm["Marker"] = ["125m","250m","375m","500m","625m","750m","875m","1000m","1125m","1250m","1375m","1500m","1625m","1750m","1875m","2000m","2125m","2250m","2375m","2500m","2625m","2750m","2875m","3000m","3125m","3250m","3375m","3500m","3625m","3750m","3875m","4000m"]
# for i in range(len(df_an)):
#     var = str(df_an["Athlete"].iloc[i])
#     df_worm[f"{var}"]=df_an.iloc[i][9:41].values.cumsum()



fig_event = px.line(df_worm, x="Marker", y = df_worm.columns, title="The Worm")

st.plotly_chart(fig_event,use_container_width=True)

fig_event = px.line(df_an, y=[125,250,375,500,625,750,875,1000,1125,1250,1375,1500,1625,1750,1875,2000,2125,2250,2375,2500,2625,2750,2875,3000,3125,3250,3375,3500,3625,3750,3875,4000], x = "Athlete", title="The Ranges", markers=True)

st.plotly_chart(fig_event,use_container_width=True)

# st.markdown("---")
    
# st.title(":two_men_holding_hands: Head to Head")
# st.subheader("Select First Athlete Ride")


# ### HEAD TO HEAD


# hh_uniqueAthlete = df_orig['Athlete'].drop_duplicates().sort_values(ascending=True)

# left_column, middle_column, right_column,c4,c5 = st.columns(5)
# with left_column:
#     hh_athlete = st.selectbox("Select Athlete:", hh_uniqueAthlete, key="hh_athlete")
    
# df_hh_athlete = df_orig.query(
#     "Athlete == @hh_athlete"
# )
# hh_uniqueYear = df_hh_athlete['Year'].drop_duplicates().sort_values()



# with middle_column:
#     hh_year = st.selectbox("Select Year:", hh_uniqueYear, key="hh_year")
    
# df_hh_athlete_year = df_hh_athlete.query(
#     "Year == @hh_year & Athlete == @hh_athlete"
# )
    
# hh_uniqueLocation = df_hh_athlete_year['Location'].drop_duplicates().sort_values()
# with right_column:
#     hh_location = st.selectbox("Select Location:", hh_uniqueLocation, key="hh_location")

# df_hh_athlete_year_location = df_hh_athlete_year.query(
#     "Year == @hh_year & Location == @hh_location & Athlete == @hh_athlete"
# )

# hh_uniqueEvent = df_hh_athlete_year_location['Event'].drop_duplicates().sort_values(ascending=True)




# with c4:
#     hh_event = st.selectbox("Select Event:", hh_uniqueEvent, key="hh_event")
    
# df_hh_athlete_year_location_event = df_hh_athlete_year_location.query(
#     "Year == @hh_year & Location == @hh_location & Athlete == @hh_athlete & Event == @hh_event"
# )

# hh_uniqueStage = df_hh_athlete_year_location_event['Stage'].drop_duplicates().sort_values()

# with c5:
#     hh_stage = st.selectbox("Select Stage:", hh_uniqueStage, key="hh_stage")
    
# df_hh_final = df_hh_athlete_year_location_event.query(
#     "Year == @hh_year & Location == @hh_location & Athlete == @hh_athlete & Event == @hh_event & Stage == @hh_stage"
# )

# st.dataframe(df_hh_final)



# ### HEAD TO HEAD RIDER 2 

# st.subheader("Select Second Athlete Ride")

# hh2_uniqueAthlete = df_orig['Athlete'].drop_duplicates().sort_values(ascending=True)

# left_column, middle_column, right_column,c4,c5 = st.columns(5)
# with left_column:
#     hh2_athlete = st.selectbox("Select Athlete:", hh2_uniqueAthlete, key="hh2_athlete")

# df_hh2_athlete = df_orig.query(
#     "Athlete == @hh2_athlete"
# )
# hh2_uniqueYear = df_hh2_athlete['Year'].drop_duplicates().sort_values()



# with middle_column:
#     hh2_year = st.selectbox("Select Year:", hh2_uniqueYear, key="hh2_year")
    
# df_hh2_athlete_year = df_hh2_athlete.query(
#     "Year == @hh2_year & Athlete == @hh2_athlete"
# )
    
# hh2_uniqueLocation = df_hh2_athlete_year['Location'].drop_duplicates().sort_values()
# with right_column:
#     hh2_location = st.selectbox("Select Location:", hh2_uniqueLocation, key="hh2_location")

# df_hh2_athlete_year_location = df_hh2_athlete_year.query(
#     "Year == @hh2_year & Location == @hh2_location & Athlete == @hh2_athlete"
# )

# hh2_uniqueEvent = df_hh2_athlete_year_location['Event'].drop_duplicates().sort_values(ascending=True)




# with c4:
#     hh2_event = st.selectbox("Select Event:", hh2_uniqueEvent, key="hh2_event")
    
# df_hh2_athlete_year_location_event = df_hh2_athlete_year_location.query(
#     "Year == @hh2_year & Location == @hh2_location & Athlete == @hh2_athlete & Event == @hh2_event"
# )

# hh2_uniqueStage = df_hh2_athlete_year_location_event['Stage'].drop_duplicates().sort_values()

# with c5:
#     hh2_stage = st.selectbox("Select Stage:", hh2_uniqueStage, key="hh2_stage")
    
# df_hh2_final = df_hh2_athlete_year_location_event.query(
#     "Year == @hh2_year & Location == @hh2_location & Athlete == @hh2_athlete & Event == @hh2_event & Stage == @hh2_stage"
# )

# st.dataframe(df_hh2_final)

# merge = [df_hh_final,df_hh2_final]

# df_hh_comp = pd.concat(merge)
# st.subheader("Comparison")

# df_hh_splits = pd.DataFrame()
# df_hh_splits["Marker"] = ["125m","250m","375m","500m","625m","750m","875m","1000m","1125m","1250m","1375m","1500m","1625m","1750m","1875m","2000m","2125m","2250m","2375m","2500m","2625m","2750m","2875m","3000m","3125m","3250m","3375m","3500m","3625m","3750m","3875m","4000m"]

# var1 = str(df_hh_comp["Athlete"].iloc[0] + " " +str(df_hh_comp["Year"].iloc[0]))
# df_hh_splits[f"{var1}"]=df_an.iloc[0][9:41].values

# var2 = str(df_hh_comp["Athlete"].iloc[1] + " " +str(df_hh_comp["Year"].iloc[1]))
# df_hh_splits[f"{var2}"]=df_an.iloc[1][9:41].values

# st.dataframe(df_hh_splits)

# fig_hh=px.line(df_hh_splits,x="Marker", y=df_hh_splits.columns) # fill down to xaxis

# st.plotly_chart(fig_hh,use_container_width=True)