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
def color_wins(val):
    background_color = 'yellow' if val == 1 else ""
    return 'background-color: %s' % background_color


df_tempo_styled = df_tempo.style.applymap(color_wins)



st.dataframe(df_tempo_styled,use_container_width=True)
st.subheader('Elimination Race')
st.dataframe(df_elim,use_container_width=True)
    
st.markdown("---")
    
st.title(":bicyclist: Rider History")

names = df_points_orig['Name'].drop_duplicates().sort_values()
name = st.multiselect("Select Rider(s):", names)

df_countryHistory = df_points_orig.query(
    "Name == @name"
)
df_tempo_hist = df_tempo_orig.query(
    "Name == @name"
)

## Sorting and displaying rider history plots
df_countryHistory = df_countryHistory.sort_values("Date",ascending=False)

st.dataframe(df_countryHistory)
df_countryHistory_short = df_countryHistory[(df_countryHistory.Rank != "DSQ") & (df_points_orig.Rank != "DNF")]
#st.dataframe(df_countryHistory_short)


##Historical Omnium Summary

df_summ=df_countryHistory_short.drop(["Age",'Time','Avg Speed','Lap +','Lap -',"Sprint 1","Sprint 2","Sprint 3","Sprint 4","Sprint 5","Sprint 6","Sprint 7","Sprint 8","Sprint 9","Sprint 10"],axis=1)
df_summ.insert(9, 'Points', df_summ["Final"]-df_summ["Sub Total"])
#st.dataframe(df_summ)

df_summ_trans = pd.DataFrame()
df_summ_trans["Race"] = ["Scratch","Tempo","Elimination","Points"]
for i in range(len(df_summ)):
    var = str(df_summ["Name"].iloc[i])+" " +str(df_summ["Location"].iloc[i])+" " +str(df_summ["Event"].iloc[i])+" " +str(df_summ["Year"].iloc[i])
    df_summ_trans[f"{var}"]=df_summ.iloc[i][7:11].values

#st.dataframe(df_summ_trans)

fig_event_mean = px.line(df_summ_trans, x="Race", y = df_summ_trans.columns[1:], title="Overall Scoring", markers=True)

st.plotly_chart(fig_event_mean,use_container_width=True)




##Hostorical Points race scoring
df_ch_Trans = pd.DataFrame()
df_ch_Trans["Marker"] = ["Sprint 1","Sprint 2","Sprint 3","Sprint 4","Sprint 5","Sprint 6","Sprint 7","Sprint 8","Sprint 9","Sprint 10"]
for i in range(len(df_countryHistory_short)):
    var =str(df_countryHistory_short["Name"].iloc[i])+" "+str(df_countryHistory_short["Location"].iloc[i])+" "+str(df_countryHistory_short["Event"].iloc[i])+" "+str(df_countryHistory_short["Year"].iloc[i])
    df_ch_Trans[f"{var}"]=df_countryHistory_short.iloc[i][12:22].values

fig_event = px.line(df_ch_Trans, x="Marker", y = df_ch_Trans.columns, title="Points Race Scoring", markers=True)
#st.dataframe(df_ch_Trans)
st.plotly_chart(fig_event,use_container_width=True)






















fig_country_history = px.line(df_countryHistory, x="Date", y = "Final", title = "Totals by Date", markers = "True", text = "Location", color="Name")
fig_country_history.update_traces(textposition="top right")

st.plotly_chart(fig_country_history,use_container_width=True)




fig_country_history = px.line(df_countryHistory, x="Date", y = "Scratch", title = "Scratch by Date", markers = "True", text = "Location", color="Name")
fig_country_history.update_traces(textposition="top right")

st.plotly_chart(fig_country_history,use_container_width=True)




fig_country_history = px.line(df_countryHistory, x="Date", y = "Tempo", title = "Tempo by Date", markers = "True", text = "Location", color="Name")
fig_country_history.update_traces(textposition="top right")

st.plotly_chart(fig_country_history,use_container_width=True)


##Tempo distribution by date
df_tempo_hist = df_tempo_hist[(df_tempo_hist.Rank != "DSQ") & (df_points_orig.Rank != "DNF")]
df_tempo_hist = df_tempo_hist.sort_values("Date",ascending=False)
df_tempo_hist_styled = df_tempo_hist.style.applymap(color_wins, subset=pd.IndexSlice[:, [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36]])

st.dataframe(df_tempo_hist_styled)


df_tempo_trans = pd.DataFrame()
df_tempo_trans["Sprint"] = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36]
for i in range(len(df_tempo_hist)):
    var =str(df_tempo_hist["Name"].iloc[i])+" "+str(df_tempo_hist["Location"].iloc[i])+" "+str(df_tempo_hist["Event"].iloc[i])+" "+str(df_tempo_hist["Year"].iloc[i])
    df_tempo_trans[f"{var}"]=df_tempo_hist.iloc[i][8:44].values

fig_event = px.line(df_tempo_trans, x="Sprint", y = df_tempo_trans.columns, title="Tempo Distribution by date", markers=True)
#st.dataframe(df_tempo_trans)
st.plotly_chart(fig_event,use_container_width=True)






fig_country_history = px.line(df_countryHistory, x="Date", y = "Elimination", title = "Elimination by Date", markers = "True", text = "Location", color="Name")
fig_country_history.update_traces(textposition="top right")

st.plotly_chart(fig_country_history,use_container_width=True)

## Ranks by Date -- DB and plot

fig_country_history = px.line(df_countryHistory, x="Date", y = "Rank", title = "Rank by Date", markers = "True", color="Name")
#fig_country_history.update_traces(textposition="top right")

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

df_summary = df_an.drop(["Year","Age",'Time','Avg Speed','Lap +','Lap -',"Sprint 1","Sprint 2","Sprint 3","Sprint 4","Sprint 5","Sprint 6","Sprint 7","Sprint 8","Sprint 9","Sprint 10","Country","Event","Date","Year","Location"],axis=1)
df_summary = df_summary[(df_summary.Rank != "DSQ") & (df_summary.Rank != "DNF")&(df_summary.Final != "DSQ") & (df_summary.Final != "DNF")]
df_summary.insert(5, 'Points', df_summary["Final"]-df_summary["Sub Total"])

df_summary = df_summary.drop(["Sub Total"],axis=1)
#st.dataframe(df_summary)


df_summary_transpose = pd.DataFrame()
df_summary_transpose["Race"] = ["Scratch","Tempo","Elimination","Points"]
for i in range(len(df_summary)):
    var = str(df_summary["Name"].iloc[i])
    df_summary_transpose[f"{var}"]=df_summary.iloc[i][2:6].values

#st.dataframe(df_mean_total_transpose)

fig_event_mean = px.line(df_summary_transpose, x="Race", y = df_summary_transpose.columns[1:], title="Omnium Summary", markers=True)

st.plotly_chart(fig_event_mean,use_container_width=True)

df_summary = df_summary[(df_summary.Rank != "DSQ") & (df_summary.Rank != "DNF")]
df_summary_worm = pd.DataFrame()
df_summary_worm["Race"] = ["Scratch","Tempo","Elimination","Points"]
for i in range(len(df_summary)):
    var = str(df_summary["Name"].iloc[i])
    df_summary_worm[f"{var}"]=df_summary.iloc[i][2:6].values.cumsum()


fig_worm = px.line(df_summary_worm, x="Race", y = df_summary_worm.columns, title="Omnium Worm")

st.plotly_chart(fig_worm,use_container_width=True)

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

##Tempo Distribution

df_tempo_an = df_tempo_orig.query(
    "Year == @an_year & Location == @an_location & Event == @an_event"
)

df_tempo_an_trans = pd.DataFrame()
df_tempo_an_trans["Sprint"] = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36]
for i in range(len(df_tempo_an)):
    var =str(df_tempo_an["Name"].iloc[i])
    df_tempo_an_trans[f"{var}"]=df_tempo_an.iloc[i][8:44].values

fig_event = px.line(df_tempo_an_trans, x="Sprint", y = df_tempo_an_trans.columns, title="Tempo Distribution", markers=True)

st.plotly_chart(fig_event,use_container_width=True)


















###Markers Dataframe and plot

#st.dataframe(df_an)



fig_event = px.line(df_an, y=["Sprint 1","Sprint 2","Sprint 3","Sprint 4","Sprint 5","Sprint 6","Sprint 7","Sprint 8","Sprint 9","Sprint 10"], x = "Name", title="Points Sprint Distribution", markers=True)
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