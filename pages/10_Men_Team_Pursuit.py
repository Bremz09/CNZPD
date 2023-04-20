#!/usr/bin/env python
# coding: utf-8



import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image
import numpy as np
import datetime as dt
import io



st.set_page_config(page_title='CNZ Performance Database',
                  page_icon=":bike:",
                  layout="wide",
                  )
st.header('Men\'s Team Pursuit')
st.subheader('All results')

marker = ["125m","250m","375m","500m","625m","750m","875m","1000m","1125m","1250m","1375m","1500m","1625m","1750m","1875m","2000m","2125m","2250m","2375m","2500m","2625m","2750m","2875m","3000m","3125m","3250m","3375m","3500m","3625m","3750m","3875m","4000m"]
    
format_dict = {'Date': '{:%d-%m-%y}', 'Age1': '{0:,.2f}', 'Age2': '{0:,.2f}'}
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
    df.Age1=round(df.Age1,2)
    df.Age2=round(df.Age2,2)
    df.Age3=round(df.Age3,2)
    df.Age4=round(df.Age4,2)
    df["Avg Speed"]=round(df["Avg Speed"],3)
 
   
    for i in range(len(df)):
        df["Date"][i] = df["Date"][i].date()

    return df
df= get_data_from_excel()

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


st.dataframe(df)



##Download buttons
@st.cache_data
def convert_to_csv(df):
    return df.to_csv(index=False,sep = ",").encode('utf-32')
csv = convert_to_csv(df)
download1 = st.download_button(
    label="Download TP data as CSV",
    data=csv,
    file_name='CNZ_Data.csv',
    mime='text/csv'
)
buffer = io.BytesIO()
with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
    df.to_excel(writer, sheet_name='Sheet1', index=False)
    writer.save()
    download2 = st.download_button(
        label="Download TP data as Excel",
        data=buffer,
        file_name='CNZ_Data.xlsx',
        mime='application/vnd.ms-excel'
    )
##Download buttons complete



    
st.markdown("---")
    
st.title(":bar_chart: Top Ten Performances")

df_topten = df_orig.sort_values("Time").head(10)

st.dataframe(df_topten,use_container_width=True)


#DOWNLOAD BUTTONS
csv_tt = convert_to_csv(df_topten)
buffer_tt = io.BytesIO()
# download button 1 to download dataframe as csv
downloadtt1 = st.download_button(
    label="Download Top Ten data as CSV",
    data=csv_tt,
    file_name='CNZ_Data.csv',
    mime='text/csv',
    key="DLTT1"
)

# download button 2 to download dataframe as xlsx
with pd.ExcelWriter(buffer_tt, engine='xlsxwriter') as writer:
    # Write each dataframe to a different worksheet.
    df_topten.to_excel(writer, sheet_name='Sheet1', index=False)
    # Close the Pandas Excel writer and output the Excel file to the buffer
    writer.save()

    downloadtt2 = st.download_button(
        label="Download Top Ten data as Excel",
        data=buffer_tt,
        file_name='CNZ_TT_Data.xlsx',
        mime='application/vnd.ms-excel',
        key="DLTT2"
    )

##Download buttons complete


df_splits_tt = pd.DataFrame()
df_splits_tt["Marker"] = marker
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
if len(country)>0:
    df_countryHistory = df_countryHistory.sort_values("Date")
    df_countryHistory.insert(49,'Final Time',df_countryHistory.iloc[:,16:48].sum(axis=1))
    df_countryHistory=df_countryHistory.reset_index(drop=True)
    st.dataframe(df_countryHistory)

    #DOWNLOAD BUTTONS
    csv_CH = convert_to_csv(df_countryHistory)
    buffer_ch = io.BytesIO()
    # download button 1 to download dataframe as csv
    downloadCH1 = st.download_button(
        label="Download Country History data as CSV",
        data=csv_CH,
        file_name='CNZ_Country_History_Data.csv',
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
            file_name='CNZ_Country_History_Data.xlsx',
            mime='application/vnd.ms-excel',
            key="DLCH2"
        )

    ##Download buttons complete


    #FIRST FIGURE -- FINAL TIME PROGRESSION

    fig_country_history = px.line(df_countryHistory, x="Date", y = "Final Time", title = "Times by Date", text="Location",color="Country",markers=True)
    fig_country_history.update_traces(textposition="top right")
    st.plotly_chart(fig_country_history, use_container_width=True)

    #Second Figure -- Splits

    
    df_splits_CH = pd.DataFrame()
    df_splits_CH["Marker"] = marker
    df_worm_CH = pd.DataFrame()
    df_worm_CH["Marker"] = marker
    for i in range(len(df_countryHistory)):
        var = str(i)+" "+str(df_countryHistory["Country"].iloc[i])+" "+str(df_countryHistory["Location"].iloc[i]) + " " + str(df_countryHistory["Year"].iloc[i]) + " " +str(df_countryHistory["Event"].iloc[i]) + " " +str(df_countryHistory["Stage"].iloc[i])
        df_splits_CH[f"{var}"]=df_countryHistory.iloc[i][16:48].values
        df_worm_CH[f"{var}"]=df_countryHistory.iloc[i][16:48].values.cumsum()


    fig_CH = px.line(df_splits_CH, x="Marker", y = df_splits_CH.columns, title="Splits")
    st.plotly_chart(fig_CH, use_container_width=True)

    #Third Figure - Worm

    fig_event_CH = px.line(df_worm_CH, x="Marker", y = df_worm_CH.columns, title="The Worm")
    st.plotly_chart(fig_event_CH, use_container_width=True)

    #Fourth Figure - Ranges
   
    fig_ranges_CH = px.line(df_countryHistory, x=df_splits_CH.columns[1:], y = marker, title="The Ranges",markers=True)
    st.plotly_chart(fig_ranges_CH, use_container_width=True)


    
#Race Analaysis Tool
st.markdown("---")
    
st.title(":mag_right: Race Analysis Tool")
uniqueYear = df_orig['Year'].drop_duplicates().sort_values(ascending=False)


left_column, middle_column, right_column,fourth_column = st.columns(4)
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
with fourth_column:
    uniqueStage = df_an_year_location_event['Stage'].drop_duplicates().sort_values()
    an_stage = st.selectbox("Select Stage:", uniqueStage)

    df_an = df_an_year_location_event.query(
        "Year == @an_year & Location == @an_location & Event == @an_event & Stage == @an_stage"
    )
st.dataframe(df_an)

### Splits dataframe and plot
df_splits,df_worm = pd.DataFrame(),pd.DataFrame()
df_splits["Marker"],df_worm["Marker"] = marker,marker
# df_worm = pd.DataFrame()
# df_worm["Marker"] = marker
for i in range(len(df_an)):
    var = str(df_an["Rank"].iloc[i])+" "+str(df_an["Country"].iloc[i])
    df_splits[f"{var}"]=df_an.iloc[i][16:48].values
    df_worm[f"{var}"]=df_an.iloc[i][16:48].values.cumsum()
fig_event = px.line(df_splits, x="Marker", y = df_splits.columns, title="Splits")
st.plotly_chart(fig_event, use_container_width=True)

### The Worm
fig_event = px.line(df_worm, x="Marker", y = df_worm.columns, title="The Worm")
st.plotly_chart(fig_event, use_container_width=True)


###The Ranges
fig_event = px.line(df_an, y=marker, x = "Country", title="The Ranges", markers=True)
st.plotly_chart(fig_event, use_container_width=True)






    
