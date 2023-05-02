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
st.header('Women\'s Team Sprint')
st.subheader('All results')
marker = ["125m","250m","375m","500m","625m","750m"]
@st.cache_data
def get_data_from_excel():
    df = pd.read_excel(
        io='pages/WomensRaceResults.xlsm',
        engine ='openpyxl',
        sheet_name='Team Sprint',
        skiprows=0,
        usecols='A:V',
        nrows=520
        )
    df = df.replace(',','', regex=True)
    df['Date'] = pd.to_datetime(df['Date']).dt.date
#     for i in range(len(df)):
#         df["Date"][i] = df["Date"][i].date()
        #if df["125m"][i] != "NULL":
            #df["125m"][i] = df["125m"][i].strftime("%M:%S.%f")
    return df
df= get_data_from_excel()
@st.cache_data
def convert_to_csv(df):
    return df.to_csv(index=False,sep = ",").encode('utf-32')
format_dict = {'Date': '{:%d-%m-%y}', 'Age1': '{0:,.2f}', 'Age2': '{0:,.2f}'}
df_orig = df
c1,c2,c3 = st.columns(3)
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

st.dataframe(df)
##Download buttons
csv = convert_to_csv(df)
download1 = st.download_button(
    label="Download Team Sprint data as CSV",
    data=csv,
    file_name='Team_Sprint_Data.csv',
    mime='text/csv',
    key="buffer1"
)
buffer = io.BytesIO()
with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
    df.to_excel(writer, sheet_name='Sheet1', index=False)
    writer.save()
    download2 = st.download_button(
        label="Download Team Sprint data as Excel",
        data=buffer,
        file_name='Team_Sprint_Data.xlsx',
        mime='application/vnd.ms-excel',
        key="buffer2"
    )
##Download buttons complete    
st.markdown("---")
    
st.title(":bar_chart: Top Ten Performances")

df_topten = df_orig.sort_values("Time").head(10)

st.dataframe(df_topten, use_container_width=True)
##Download buttons
csvtt = convert_to_csv(df_topten)
download1 = st.download_button(
    label="Download Top Ten data as CSV",
    data=csvtt,
    file_name='Team_Sprint_Data.csv',
    mime='text/csv',
    key="buffertt1"
)
buffertt = io.BytesIO()
with pd.ExcelWriter(buffertt, engine='xlsxwriter') as writer:
    df_topten.to_excel(writer, sheet_name='Sheet1', index=False)
    writer.save()
    download2 = st.download_button(
        label="Download Top Ten data as Excel",
        data=buffertt,
        file_name='Team_Sprint_Data.xlsx',
        mime='application/vnd.ms-excel',
        key="buffertt2"
    )
##Download buttons complete  
df_splits_tt = pd.DataFrame()
df_splits_tt["Marker"] = ["125m","250m","375m","500m","625m","750m"]
for i in range(len(df_topten)):
    var = str(i+1)+" "+str(df_topten["Country"].iloc[i]) + " " + str(df_topten["Year"].iloc[i]) + " " +str(df_topten["Location"].iloc[i])+" " +str(df_topten["Event"].iloc[i]) + " " +str(df_topten["Stage"].iloc[i])
    df_splits_tt[f"{var}"]=df_topten.iloc[i][15:21].values

    
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

if len(country)>0:
    #DATAFRAME
    df_countryHistory = df_countryHistory.sort_values("Date")


    st.dataframe(df_countryHistory)

    #DOWNLOAD BUTTONS
    csv_CH = convert_to_csv(df_countryHistory)
    buffer_ch = io.BytesIO()
    # download button 1 to download dataframe as csv
    downloadCH1 = st.download_button(
        label="Download Country History data as CSV",
        data=csv_CH,
        file_name='Team_Sprint_Country_History_Data.csv',
        mime='text/csv',
        key="DLCH1"
    )

    # download button 2 to download dataframe as xlsx
    with pd.ExcelWriter(buffer_ch, engine='xlsxwriter') as writer:
        # Write each dataframe to a different worksheet.
        df_countryHistory.to_excel(writer, sheet_name='Sheet1', index=False)
        # Close the Pandas Excel writer and output the Excel file to the buffer
        writer.save()

        downloadCH2 = st.download_button(
            label="Download Country History data as Excel",
            data=buffer_ch,
            file_name='Teamp_Sprint_Country_History_Data.xlsx',
            mime='application/vnd.ms-excel',
            key="DLCH2"
        )

    ##Download buttons complete


    #FIRST FIGURE -- FINAL TIME PROGRESSION

    fig_country_history = px.line(df_countryHistory, x="Date", y = "Time", title = "Times by Date",text="Location", color="Country",markers=True)
    fig_country_history.update_traces(textposition="top right")

    st.plotly_chart(fig_country_history, use_container_width=True)

    #Second Figure -- Chart with rider names

    df_splits_CH,df_worm_CH = pd.DataFrame(),pd.DataFrame()
    df_splits_CH["Marker"],df_worm_CH["Marker"] = marker,marker
    for i in range(len(df_countryHistory)):
        var = str(i+1)+" " +str(df_countryHistory["Country"].iloc[i]) + " " + str(df_countryHistory["Year"].iloc[i]) + " " +str(df_countryHistory["Event"].iloc[i]) + " " +str(df_countryHistory["Stage"].iloc[i])+ " " +str(df_countryHistory["Rider1"].iloc[i].split(" ")[0])+ " " +str(df_countryHistory["Rider2"].iloc[i].split(" ")[0])+ " " +str(df_countryHistory["Rider3"].iloc[i].split(" ")[0])
        df_splits_CH[f"{var}"]=df_countryHistory.iloc[i][15:21].values
        df_worm_CH[f"{var}"]=df_countryHistory.iloc[i][15:21].values.cumsum()


    fig_CH = px.line(df_splits_CH, x="Marker", y = df_splits_CH.columns, title="All Rides")


    st.plotly_chart(fig_CH, use_container_width=True)

    #Third Figure - Worm

    fig_event_CH = px.line(df_worm_CH, x="Marker", y = df_worm_CH.columns, title="The Worm")
    st.plotly_chart(fig_event_CH, use_container_width=True)

    
    
    #Fourth Figure - Ranges

    fig_ranges_CH = px.line(df_countryHistory, x=df_splits_CH.columns[1:], y = [125,250,375,500,625,750], title="The Ranges",markers=True)
    st.plotly_chart(fig_ranges_CH, use_container_width=True)





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

### Splits dataframe and plot

df_splits,df_worm = pd.DataFrame(),pd.DataFrame()
df_splits["Marker"],df_worm["Marker"] = marker,marker
for i in range(len(df_an)):
    var = str(df_an["Rank"].iloc[i])+" "+str(df_an["Country"].iloc[i])
    df_splits[f"{var}"]=df_an.iloc[i][15:21].values
    df_worm[f"{var}"]=df_an.iloc[i][15:21].values.cumsum()
st.dataframe(df_an, use_container_width=True)

fig_event = px.line(df_splits, x="Marker", y = df_splits.columns, title="Splits")
st.plotly_chart(fig_event, use_container_width=True)

### Worm dataframe and plot

fig_event = px.line(df_worm, x="Marker", y = df_worm.columns, title="The Worm")
st.plotly_chart(fig_event, use_container_width=True)


###Ranges

fig_event = px.line(df_an, y=[125,250,375,500,625,750], x = df_worm.columns[1:], title="The Ranges", markers=True)
st.plotly_chart(fig_event, use_container_width=True)






    
