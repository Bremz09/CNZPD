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
st.header('Women\'s Madison')
st.subheader('All results')
all_sprints=["Sprint 1","Sprint 2","Sprint 3","Sprint 4","Sprint 5","Sprint 6","Sprint 7","Sprint 8","Sprint 9","Sprint 10","Sprint 11","Sprint 12"]
@st.cache_data
def get_data_from_excel():
    df = pd.read_excel(
        io='pages/WomensRaceResults.xlsm',
        engine ='openpyxl',
        sheet_name='Madison',
        skiprows=0,
        usecols='A:AA',
        nrows=2000
        )
    df = df.replace(',','')
    return df
df= get_data_from_excel()
@st.cache_data
def convert_to_csv(df):
    return df.to_csv(index=False,sep = ",").encode('utf-32')
format_dict = { 'Date': '{:%d-%m-%y}', 'Age1': '{0:,.2f}', 'Age2': '{0:,.2f}', 'Avg Speed': '{0:,.3f}'}
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

c1,c2,c3=st.columns(3)
with c1:
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

df_styled = (df
                    .style
                    .applymap(color_points, subset=pd.IndexSlice[:, ["Sprint 1","Sprint 2","Sprint 3","Sprint 4","Sprint 5","Sprint 6","Sprint 7","Sprint 8","Sprint 9","Sprint 10","Sprint 11"]])
                    .applymap(color_points_10, subset=pd.IndexSlice[:, ["Sprint 12"]])
                    .applymap(color_plus_laps, subset=pd.IndexSlice[:, ["P.Laps"]])
                    .applymap(color_minus_laps, subset=pd.IndexSlice[:, ["M.Laps"]])
                    .format(format_dict))
st.dataframe(df_styled,use_container_width=True)
##Download buttons
csv = convert_to_csv(df)
download1 = st.download_button(
    label="Download Madison Data as CSV",
    data=csv,
    file_name='Madison_Data.csv',
    mime='text/csv',
    key="mad1"
)
buffer = io.BytesIO()
with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
    df.to_excel(writer, sheet_name='Sheet1', index=False)
    writer.save()
    download2 = st.download_button(
        label="Download Madison Data as Excel",
        data=buffer,
        file_name='Madison_Data.xlsx',
        mime='application/vnd.ms-excel',
    key="mad2"
    )
##Download buttons complete
st.markdown("---")
    
st.title(":bicyclist: Event History")

countries = df_orig['Country'].drop_duplicates().sort_values()
country = st.multiselect("Select Country(s):", countries)
if len(country)>0:
    df_countryHistory = df_orig.query(
        "Country == @country"
    )

    ## Totals by Date -- DB and plot
    df_countryHistory = df_countryHistory.sort_values("Date", ascending=False)
    df_countryHistory_styled = (df_countryHistory
                        .style
                        .applymap(color_points, subset=pd.IndexSlice[:, ["Sprint 1","Sprint 2","Sprint 3","Sprint 4","Sprint 5","Sprint 6","Sprint 7","Sprint 8","Sprint 9","Sprint 10","Sprint 11"]])
                        .applymap(color_points_10, subset=pd.IndexSlice[:, ["Sprint 12"]])
                        .applymap(color_plus_laps, subset=pd.IndexSlice[:, ["P.Laps"]])
                        .applymap(color_minus_laps, subset=pd.IndexSlice[:, ["M.Laps"]])
                        .format(format_dict))
    st.dataframe(df_countryHistory_styled,use_container_width=True)
    ##Download buttons
    csv_ch = convert_to_csv(df_countryHistory)
    download1 = st.download_button(
        label="Download Country History as CSV",
        data=csv_ch,
        file_name='Madison_Country_History.csv',
        mime='text/csv',
        key="madch1"
    )
    buffer_ch = io.BytesIO()
    with pd.ExcelWriter(buffer_ch, engine='xlsxwriter') as writer:
        df_countryHistory.to_excel(writer, sheet_name='Sheet1', index=False)
        writer.save()
        download2 = st.download_button(
            label="Download Country History as Excel",
            data=buffer_ch,
            file_name='Madison_Country_History.xlsx',
            mime='application/vnd.ms-excel',
        key="madch2"
        )
    ##Download buttons complete
    fig_country_history = px.line(df_countryHistory, x="Date", y = "Total", title = "Totals by Date", markers = "True", text = "Location", color="Country")
    fig_country_history.update_traces(textposition="top right")

    st.plotly_chart(fig_country_history,use_container_width=True)


    ##All races summary
    df_ch_trans,df_ch_worm = pd.DataFrame(),pd.DataFrame()
    df_ch_trans["Sprints"],df_ch_worm["Sprints"] = all_sprints,all_sprints
    
    for i in range(len(df_countryHistory)):
        var = str(i+1)+" "+str(df_countryHistory["Country"].iloc[i])+" "+str(df_countryHistory["Location"].iloc[i])+" " +str(df_countryHistory["Event"].iloc[i])+" "+str(df_countryHistory["Stage"].iloc[i])+" " +str(df_countryHistory["Year"].iloc[i])
        df_ch_trans[f"{var}"]=df_countryHistory.iloc[i][10:22].values
        df_ch_worm[f"{var}"]=df_countryHistory.iloc[i][10:22].values.cumsum()

    fig_event_mean = px.line(df_ch_trans, x="Sprints", y = df_ch_trans.columns[1:], title="All races Summary", markers=True)
    st.plotly_chart(fig_event_mean,use_container_width=True)

    ##All races Worm
    fig_worm = px.line(df_ch_worm, x="Sprints", y = df_ch_worm.columns, title="The Worm", markers=True)
    st.plotly_chart(fig_worm,use_container_width=True)

    ##The Ranges
    fig_ranges = px.line(df_countryHistory, x=df_ch_worm.columns[1:], y = ["Sprint 1","Sprint 2","Sprint 3","Sprint 4","Sprint 5","Sprint 6","Sprint 7","Sprint 8","Sprint 9","Sprint 10","Sprint 11","Sprint 12"], title="The Ranges", markers=True)

    st.plotly_chart(fig_ranges,use_container_width=True)

    ## Ranks by Date -- DB and plot
    fig_country_history = px.line(df_countryHistory, x="Date", y = "Rank", title = "Rank by Date", markers = "True", color="Country")
    #fig_country_history.update_traces(textposition="top right")

    st.plotly_chart(fig_country_history,use_container_width=True)

    ## Laps taken by date -- DB and plot
    fig_country_history = px.line(df_countryHistory, x="Date", y = "P.Laps", title = "Laps Taken by Date", markers = "True", color="Country")
    st.plotly_chart(fig_country_history,use_container_width=True)

    ## Laps lost by date -- DB and plot
    fig_country_history = px.line(df_countryHistory, x="Date", y = "M.Laps", title = "Laps Lost by Date", markers = "True", color="Country")
    st.plotly_chart(fig_country_history,use_container_width=True)




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

### Splits dataframe and plot

df_splits = pd.DataFrame()
df_splits["Marker"] = ["Sprint 1","Sprint 2","Sprint 3","Sprint 4","Sprint 5","Sprint 6","Sprint 7","Sprint 8","Sprint 9","Sprint 10","Sprint 11","Sprint 12"]
for i in range(len(df_an)):
    var = str(df_an["Country"].iloc[i])
    df_splits[f"{var}"]=df_an.iloc[i][10:22].values



fig_event = px.line(df_splits, x="Marker", y = df_splits.columns, title="Splits", markers=True)

st.plotly_chart(fig_event,use_container_width=True)

### Worm dataframe and plot
st.write("Running Time")
df_worm = pd.DataFrame()
df_worm["Marker"] = ["Sprint 1","Sprint 2","Sprint 3","Sprint 4","Sprint 5","Sprint 6","Sprint 7","Sprint 8","Sprint 9","Sprint 10","Sprint 11","Sprint 12"]
for i in range(len(df_an)):
    var = str(df_an["Country"].iloc[i])
    df_worm[f"{var}"]=df_an.iloc[i][10:22].values.cumsum()


fig_worm = px.line(df_worm, x="Marker", y = df_worm.columns, title="The Worm")

st.plotly_chart(fig_worm,use_container_width=True)


###Markers Dataframe and plot

fig_event = px.line(df_an, y=["Sprint 1","Sprint 2","Sprint 3","Sprint 4","Sprint 5","Sprint 6","Sprint 7","Sprint 8","Sprint 9","Sprint 10","Sprint 11","Sprint 12"], x = "Country", title="The Ranges", markers=True)
#fig_event.update_layout(legend_title="legend")
st.plotly_chart(fig_event,use_container_width=True)

##
st.markdown("---")
st.header(":chart: Historical Averages")
df_mean = df_orig.groupby('Country', as_index=False).mean()

st.write("Points Average")
df_splits_mean = pd.DataFrame()
df_splits_mean["Marker"] = ["Sprint 1","Sprint 2","Sprint 3","Sprint 4","Sprint 5","Sprint 6","Sprint 7","Sprint 8","Sprint 9","Sprint 10","Sprint 11","Sprint 12"]
for i in range(len(df_mean)):
    var = str(df_mean["Country"].iloc[i])
    df_splits_mean[f"{var}"]=df_mean.iloc[i][2:14].values

st.dataframe(df_splits_mean,use_container_width=True)

fig_event_mean = px.line(df_splits_mean, x="Marker", y = df_splits.columns, title="Points Scoring Average", markers=True)

st.plotly_chart(fig_event_mean,use_container_width=True)
df_mean_total = df_orig[df_orig.Total != "DNF"]
df_mean_total = df_mean_total.groupby('Country', as_index=False)["Total"].mean()


fig_total_mean = px.bar(df_mean_total, x="Country", y = "Total", title="Total Scoring Average")
st.plotly_chart(fig_total_mean,use_container_width=True)