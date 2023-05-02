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
st.header('Women\'s Omnium')
st.subheader('All results')

@st.cache_data
def get_points_data_from_excel():
    df_points = pd.read_excel(
        io='pages/WomensRaceResults.xlsm',
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
@st.cache_data
def get_scracth_data_from_excel():
    df_scratch = pd.read_excel(
        io='pages/WomensRaceResults.xlsm',
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
@st.cache_data
def get_tempo_data_from_excel():
    df_tempo = pd.read_excel(
        io='pages/WomensRaceResults.xlsm',
        engine ='openpyxl',
        sheet_name='OM-Tempo',
        skiprows=0,
        usecols='A:AW',
        nrows=3000
        )
    df_tempo = df_tempo.replace(',','')
    return df_tempo
df_tempo= get_tempo_data_from_excel()
@st.cache_data
def get_elimination_data_from_excel():
    df_elim = pd.read_excel(
        io='pages/WomensRaceResults.xlsm',
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
@st.cache_data
def convert_to_csv(df):
    return df.to_csv(index=False,sep = ",").encode('utf-32')
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

##Defining colouring functions for dataframes
format_dict = {'Scratch':'{0:,.0f}', 'Date': '{:%d-%m-%y}', 'Age': '{0:,.2f}', 'Sub Total': '{0:,.0f}', 'Avg Speed': '{0:,.3f}'}
def color_points(val):
    if val == 5:
        background_color = 'darkgoldenrod'    
        return 'background-color: %s' % background_color
    elif val == 3:
        background_color = 'Silver'    
        return 'background-color: %s' % background_color 
    elif val == 2:
        background_color = 'Coral'    
        return 'background-color: %s' % background_color
    elif val == 1:
        background_color = 'darkcyan'    
        return 'background-color: %s' % background_color 
    else:
        background_color = ''    
        return 'background-color: %s' % background_color  
def color_points_10(val):
    if val == 10:
        background_color = 'darkgoldenrod'    
        return 'background-color: %s' % background_color
    elif val == 6:
        background_color = 'Silver'    
        return 'background-color: %s' % background_color 
    elif val == 4:
        background_color = 'Coral'    
        return 'background-color: %s' % background_color
    elif val == 2:
        background_color = 'darkcyan'    
        return 'background-color: %s' % background_color 
    else:
        background_color = ''    
        return 'background-color: %s' % background_color  
def color_plus_laps(val):
    if val >19:
        background_color = 'green'    
        return 'background-color: %s' % background_color
    else:
        background_color = ''    
        return 'background-color: %s' % background_color    
def color_minus_laps(val):
    if val > 19:
        background_color = 'red'    
        return 'background-color: %s' % background_color
    else:
        background_color = ''    
        return 'background-color: %s' % background_color    
def tempo_color_wins(val):
    background_color = 'yellow' if val == 1 else ""
    return 'background-color: %s' % background_color
##Displaying all dataframes, some styled
df_points_styled = (df_points
                    .style
                    .applymap(color_points, subset=pd.IndexSlice[:, ["Sprint 1","Sprint 2","Sprint 3","Sprint 4","Sprint 5","Sprint 6","Sprint 7"]])
                    .applymap(color_points_10, subset=pd.IndexSlice[:, ["Sprint 8"]])
                    .applymap(color_plus_laps, subset=pd.IndexSlice[:, ["Lap +"]])
                    .applymap(color_minus_laps, subset=pd.IndexSlice[:, ["Lap -"]])
                    .format(format_dict))
st.dataframe(df_points_styled,use_container_width=True)
##Download buttons
csv_points = convert_to_csv(df_points)
download1 = st.download_button(
    label="Download Omnium Summary as CSV",
    data=csv_points,
    file_name='Ommnium_Summary_Data.csv',
    mime='text/csv',
    key="OmSum1"
)
buffer = io.BytesIO()
with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
    df_points.to_excel(writer, sheet_name='Sheet1', index=False)
    writer.save()
    download2 = st.download_button(
        label="Download Ommnium Summary as Excel",
        data=buffer,
        file_name='Ommnium_Summary_Data.xlsx',
        mime='application/vnd.ms-excel',
    key="OmSum2"
    )
##Download buttons complete

st.subheader('Scratch Race')
st.dataframe(df_scratch.style.format(format_dict),use_container_width=True)
##Download buttons
csv_scratch = convert_to_csv(df_scratch)
download1 = st.download_button(
    label="Download Omnium Scratch Data as CSV",
    data=csv_scratch,
    file_name='Ommnium_Scratch_Data.csv',
    mime='text/csv',
    key="OmSc1"
)
buffer_scratch = io.BytesIO()
with pd.ExcelWriter(buffer_scratch, engine='xlsxwriter') as writer:
    df_scratch.to_excel(writer, sheet_name='Sheet1', index=False)
    writer.save()
    download2 = st.download_button(
        label="Download Ommnium Scratch Data as Excel",
        data=buffer_scratch,
        file_name='Ommnium_Scratch_Data.xlsx',
        mime='application/vnd.ms-excel',
    key="OmSc2"
    )
##Download buttons complete
st.subheader('Tempo Race')
df_tempo_styled = (df_tempo
                   .style
                   .format(format_dict)
                   .applymap(tempo_color_wins, subset=pd.IndexSlice[:, [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26]]
                  )
                   .applymap(color_plus_laps, subset=pd.IndexSlice[:, ["P.Laps"]]
                  )
                   .applymap(color_minus_laps, subset=pd.IndexSlice[:, ["M.Laps"]]
                  )
                  )
st.dataframe(df_tempo_styled,use_container_width=True)
##Download buttons
csv_tempo = convert_to_csv(df_tempo)
download1 = st.download_button(
    label="Download Omnium Tempo Data as CSV",
    data=csv_tempo,
    file_name='Ommnium_Tempo_Data.csv',
    mime='text/csv',
    key="OmTem1"
)
buffer_Tempo = io.BytesIO()
with pd.ExcelWriter(buffer_Tempo, engine='xlsxwriter') as writer:
    df_tempo.to_excel(writer, sheet_name='Sheet1', index=False)
    writer.save()
    download2 = st.download_button(
        label="Download Ommnium Tempo Data as Excel",
        data=buffer_Tempo,
        file_name='Ommnium_Tempo_Data.xlsx',
        mime='application/vnd.ms-excel',
    key="OmTem2"
    )
##Download buttons complete
st.subheader('Elimination Race')
st.dataframe(df_elim.style.format(format_dict),use_container_width=True)
##Download buttons
csv_elim = convert_to_csv(df_elim)
download1 = st.download_button(
    label="Download Omnium Elim Data as CSV",
    data=csv_elim,
    file_name='Ommnium_Elim_Data.csv',
    mime='text/csv',
    key="OmEl1"
)
buffer_Elim = io.BytesIO()
with pd.ExcelWriter(buffer_Elim, engine='xlsxwriter') as writer:
    df_elim.to_excel(writer, sheet_name='Sheet1', index=False)
    writer.save()
    download2 = st.download_button(
        label="Download Ommnium Elim Data as Excel",
        data=buffer_Elim,
        file_name='Ommnium_Elim_Data.xlsx',
        mime='application/vnd.ms-excel',
    key="OmEl2"
    )
##Download buttons complete
    
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
if len(name)>0:
    ## Sorting and displaying rider history plots
    df_countryHistory = df_countryHistory.sort_values("Date",ascending=False)
    df_countryHistory_styled = (df_countryHistory
                                 .style
                                 .applymap(color_points, subset=pd.IndexSlice[:, ["Sprint 1","Sprint 2","Sprint 3","Sprint 4","Sprint 5","Sprint 6","Sprint 7"]])
                                 .format(format_dict)
                                 .applymap(color_points_10, subset=pd.IndexSlice[:, ["Sprint 8"]])
                                 .applymap(color_plus_laps, subset=pd.IndexSlice[:, ["Lap +"]])
                                 .applymap(color_minus_laps, subset=pd.IndexSlice[:, ["Lap -"]])
                     )

    st.dataframe(df_countryHistory_styled)
    ##Download buttons
    csv_ah = convert_to_csv(df_countryHistory)
    download1 = st.download_button(
        label="Download Omnium Athlete History Data as CSV",
        data=csv_ah,
        file_name='Ommnium_Athlete_History.csv',
        mime='text/csv',
        key="Omah1"
    )
    buffer_ah = io.BytesIO()
    with pd.ExcelWriter(buffer_ah, engine='xlsxwriter') as writer:
        df_countryHistory.to_excel(writer, sheet_name='Sheet1', index=False)
        writer.save()
        download2 = st.download_button(
            label="Download Omnium Athlete History Data as Excel",
            data=buffer_ah,
            file_name='Ommnium_Athlete_History.xlsx',
            mime='application/vnd.ms-excel',
        key="Omah2"
        )
    ##Download buttons complete

    df_countryHistory_short = df_countryHistory[(df_countryHistory.Rank != "DSQ") & (df_countryHistory.Rank != "DNF")&(df_countryHistory.Final != "DSQ") & (df_countryHistory.Final != "DNF")]
    #st.dataframe(df_countryHistory_short)


    ##Overall Scoring Summary

    df_summ=df_countryHistory_short.drop(["Age",'Time','Avg Speed','Lap +','Lap -',"Sprint 1","Sprint 2","Sprint 3","Sprint 4","Sprint 5","Sprint 6","Sprint 7","Sprint 8"],axis=1)
    df_summ.insert(10, 'Points', df_summ["Final"]-df_summ["Sub Total"])
    df_summ_trans = pd.DataFrame()
    df_summ_trans["Race"] = ["Scratch","Tempo","Elimination","Points"]
    df_ch_Trans = pd.DataFrame()
    df_ch_Trans["Sprint"] = ["Sprint 1","Sprint 2","Sprint 3","Sprint 4","Sprint 5","Sprint 6","Sprint 7","Sprint 8"]
    for i in range(len(df_summ)):
        var = str(i+1)+" "+str(df_summ["Name"].iloc[i])+" " +str(df_summ["Location"].iloc[i])+" " +str(df_summ["Event"].iloc[i])+" " +str(df_summ["Year"].iloc[i])
        df_summ_trans[f"{var}"]=df_summ.iloc[i][7:11].values
        df_ch_Trans[f"{var}"]=df_countryHistory_short.iloc[i][12:20].values
    st.dataframe(df_summ_trans)
    fig_event_mean = px.line(df_summ_trans, x="Race", y = df_summ_trans.columns[1:], title="Overall Scoring", markers=True)
    st.plotly_chart(fig_event_mean,use_container_width=True)

    ##Points race scoring
    fig_event = px.line(df_ch_Trans, x="Sprint", y = df_ch_Trans.columns, title="Points Race Scoring", markers=True)
    st.plotly_chart(fig_event,use_container_width=True)

    #Totals by Date
    fig_country_history = px.line(df_countryHistory, x="Date", y = "Final", title = "Totals by Date", markers = "True", text = "Location", color="Name")
    fig_country_history.update_traces(textposition="top right")
    st.plotly_chart(fig_country_history,use_container_width=True)

    ##Scratch totals by date
    fig_country_history = px.line(df_countryHistory, x="Date", y = "Scratch", title = "Scratch by Date", markers = "True", text = "Location", color="Name")
    fig_country_history.update_traces(textposition="top right")
    st.plotly_chart(fig_country_history,use_container_width=True)

    ##Tempo totals by date
    fig_country_history = px.line(df_countryHistory, x="Date", y = "Tempo", title = "Tempo by Date", markers = "True", text = "Location", color="Name")
    fig_country_history.update_traces(textposition="top right")
    st.plotly_chart(fig_country_history,use_container_width=True)

    ##Tempo distribution by date
    df_tempo_hist = df_tempo_hist[(df_tempo_hist.Rank != "DSQ") & (df_points_orig.Rank != "DNF")]
    df_tempo_hist = df_tempo_hist.sort_values("Date",ascending=False)
    df_tempo_hist_styled = df_tempo_hist.style.applymap(tempo_color_wins, subset=pd.IndexSlice[:, [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26]])                   .applymap(color_plus_laps, subset=pd.IndexSlice[:, ["P.Laps"]]
                  ).applymap(color_minus_laps, subset=pd.IndexSlice[:, ["M.Laps"]]
                  )
    st.dataframe(df_tempo_hist_styled)

    df_tempo_trans = pd.DataFrame()
    df_tempo_trans["Sprint"] = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26]
    for i in range(len(df_tempo_hist)):
        var =str(df_tempo_hist["Name"].iloc[i])+" "+str(df_tempo_hist["Location"].iloc[i])+" "+str(df_tempo_hist["Event"].iloc[i])+" "+str(df_tempo_hist["Year"].iloc[i])
        df_tempo_trans[f"{var}"]=df_tempo_hist.iloc[i][8:34].values

    fig_event = px.line(df_tempo_trans, x="Sprint", y = df_tempo_trans.columns, title="Tempo Distribution by Date", markers=True)
    st.plotly_chart(fig_event,use_container_width=True)

    ##Elimination totals by date
    fig_country_history = px.line(df_countryHistory, x="Date", y = "Elimination", title = "Elimination by Date", markers = "True", text = "Location", color="Name")
    fig_country_history.update_traces(textposition="top right")
    st.plotly_chart(fig_country_history,use_container_width=True)

    ## Ranks by Date 
    fig_country_history = px.line(df_countryHistory, x="Date", y = "Rank", title = "Rank by Date", markers = "True", color="Name")
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


df_an_styled = (df_an
                    .style
                    .applymap(color_points, subset=pd.IndexSlice[:, ["Sprint 1","Sprint 2","Sprint 3","Sprint 4","Sprint 5","Sprint 6","Sprint 7"]])
                    .applymap(color_points_10, subset=pd.IndexSlice[:, ["Sprint 8"]])
                    .applymap(color_plus_laps, subset=pd.IndexSlice[:, ["Lap +"]])
                    .applymap(color_minus_laps, subset=pd.IndexSlice[:, ["Lap -"]])
                    .format(format_dict))
st.dataframe(df_an_styled)

df_summary = df_an.drop(["Year","Age",'Time','Avg Speed','Lap +','Lap -',"Sprint 1","Sprint 2","Sprint 3","Sprint 4","Sprint 5","Sprint 6","Sprint 7","Sprint 8","Nat","Event","Date","Year","Location"],axis=1)
df_summary = df_summary[(df_summary.Rank != "DSQ") & (df_summary.Rank != "DNF")&(df_summary.Final != "DSQ") & (df_summary.Final != "DNF")]
df_summary.insert(5, 'Points', df_summary["Final"]-df_summary["Sub Total"])

df_summary = df_summary.drop(["Sub Total"],axis=1)
#st.dataframe(df_summary)


df_summary_transpose = pd.DataFrame()
df_summary_transpose["Race"] = ["Scratch","Tempo","Elimination","Points"]
for i in range(len(df_summary)):
    var = str(df_summary["Name"].iloc[i])
    df_summary_transpose[f"{var}"]=df_summary.iloc[i][2:6].values

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
df_splits["Marker"] = ["Sprint 1","Sprint 2","Sprint 3","Sprint 4","Sprint 5","Sprint 6","Sprint 7","Sprint 8"]
for i in range(len(df_an)):
    var = str(df_an["Name"].iloc[i])
    df_splits[f"{var}"]=df_an.iloc[i][12:20].values


fig_event = px.line(df_splits, x="Marker", y = df_splits.columns, title="Points Race Sprint Points", markers=True)

st.plotly_chart(fig_event,use_container_width=True)

### Worm 

df_worm = pd.DataFrame()
df_worm["Marker"] = ["Sprint 1","Sprint 2","Sprint 3","Sprint 4","Sprint 5","Sprint 6","Sprint 7","Sprint 8"]
for i in range(len(df_an)):
    var = str(df_an["Name"].iloc[i])
    df_worm[f"{var}"]=df_an.iloc[i][12:20].values.cumsum()

fig_worm = px.line(df_worm, x="Marker", y = df_worm.columns, title="Points Race Worm")
st.plotly_chart(fig_worm,use_container_width=True)

##Tempo Distribution

df_tempo_an = df_tempo_orig.query(
    "Year == @an_year & Location == @an_location & Event == @an_event"
)

df_tempo_an_trans = pd.DataFrame()
df_tempo_an_trans["Sprint"] = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26]
for i in range(len(df_tempo_an)):
    var =str(df_tempo_an["Name"].iloc[i])
    df_tempo_an_trans[f"{var}"]=df_tempo_an.iloc[i][8:34].values

fig_event = px.line(df_tempo_an_trans, x="Sprint", y = df_tempo_an_trans.columns, title="Tempo Distribution", markers=True)
st.plotly_chart(fig_event,use_container_width=True)

###The Ranges


fig_event = px.line(df_an, y=["Sprint 1","Sprint 2","Sprint 3","Sprint 4","Sprint 5","Sprint 6","Sprint 7","Sprint 8"], x = "Name", title="Points race Ranges", markers=True)
#fig_event.update_layout(legend_title="legend")
st.plotly_chart(fig_event,use_container_width=True)


##
st.markdown("---")
st.header("Dataset Averages")

df_mean_points = df_points_orig.groupby('Name', as_index=False).mean()
df_mean_tempo = df_tempo_orig.groupby('Name', as_index=False).mean()
df_mean_points=df_mean_points.drop(['Year','Age','Lap +','Lap -','Avg Speed'],axis=1)
df_mean_total = df_points_orig[(df_points_orig.Final != "DSQ") & (df_points_orig.Final != "DNF")]







riders_avg= st.multiselect(
        "Select Rider(s):",
        options=df_points_orig['Name'].drop_duplicates().sort_values(),
        key="rider averages",
        #default=df_points_orig['Name'].drop_duplicates().sort_values()[0]
    )    
if len(riders_avg) !=0:
    df_mean_points=df_mean_points[(df_mean_points.Name.isin(riders_avg))]
    df_mean_tempo=df_mean_tempo[(df_mean_tempo.Name.isin(riders_avg))]
    df_mean_total=df_mean_total[(df_mean_total.Name.isin(riders_avg))]
    df_mean_total.Final = pd.to_numeric(df_mean_total.Final)
    df_mean_total.Tempo = pd.to_numeric(df_mean_total.Tempo)
    df_mean_total.Elimination = pd.to_numeric(df_mean_total.Elimination)
    df_mean_total.Scratch = pd.to_numeric(df_mean_total.Scratch)
    df_mean_total["Sub Total"] = pd.to_numeric(df_mean_total["Sub Total"])
    df_mean_total["Points"] = df_mean_total["Final"]-df_mean_total["Sub Total"]
    df_mean_total=df_mean_total.drop(["Year","Age",'Time','Avg Speed','Lap +','Lap -',"Sprint 1","Sprint 2","Sprint 3","Sprint 4","Sprint 5","Sprint 6","Sprint 7","Sprint 8","Sub Total","Final"],axis=1)
    df_mean_total = df_mean_total.groupby('Name', as_index=False).mean()
    


    df_mean_points_transpose = pd.DataFrame()
    df_mean_points_transpose["Marker"] = ["Sprint 1","Sprint 2","Sprint 3","Sprint 4","Sprint 5","Sprint 6","Sprint 7","Sprint 8"]
    df_mean_tempo_transpose = pd.DataFrame()
    df_mean_tempo_transpose["Marker"] = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26]
    df_mean_total_transpose = pd.DataFrame()
    df_mean_total_transpose["Marker"] = ["Scratch","Tempo","Elimination","Points"]

    for i in range(len(df_mean_points)):
        var = str(df_mean_points["Name"].iloc[i])
        df_mean_points_transpose[f"{var}"]=df_mean_points.iloc[i][2:10].values
        df_mean_total_transpose[f"{var}"]=df_mean_total.iloc[i][1:5].values
        df_mean_tempo_transpose[f"{var}"]=df_mean_tempo.iloc[i][3:29].values
        
    ##Points scoring average plot
    fig_point_mean = px.line(df_mean_points_transpose, x="Marker", y = df_mean_points_transpose.columns[1:], title="Points Scoring Average", markers=True)
    st.plotly_chart(fig_point_mean,use_container_width=True)
    
    ##Tempo scoring average plot

    fig_tempo_mean = px.line(df_mean_tempo_transpose, x="Marker", y = df_mean_tempo_transpose.columns[1:], title="Tempo Scoring Average", markers=True)
    st.plotly_chart(fig_tempo_mean,use_container_width=True)
    
    
    
    ##Overall Averages plot
    fig_overall_mean = px.line(df_mean_total_transpose, x="Marker", y = df_mean_total_transpose.columns[1:], title="Overall Averages", markers=True)
    st.plotly_chart(fig_overall_mean,use_container_width=True)