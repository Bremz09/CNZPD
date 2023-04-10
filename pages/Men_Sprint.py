#!/usr/bin/env python
# coding: utf-8



import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image
import datetime
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm




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
        io='pages/Sprint_Points_Men.xlsx',
        engine ='openpyxl',
        sheet_name='Sprint_Points_Men',
        skiprows=0,
        usecols='A:J',
        nrows=3000
        )
    df = df.replace(',','')
    df['Date'] = pd.to_datetime(df['Date']).dt.date
    return df
df_points = get_points_data_from_excel()

def get_trueskill_data_from_excel():
    df = pd.read_excel(
        io='pages/MensRaceResults.xlsm',
        engine ='openpyxl',
        sheet_name='Sprint_Trueskill',
        skiprows=0,
        usecols='A:R',
        nrows=3000
        )
    df = df.replace(',','')
    df['Date'] = pd.to_datetime(df['Date']).dt.date
    return df
df_TS = get_trueskill_data_from_excel()

df_orig = df_TS

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

fig_athlete_history = px.line(df_athleteHistory, x="Date", y = ["200m"], title = "Times by Date", markers = "True", text = "Location", color="Athlete")
fig_athlete_history.update_traces(textposition="top right")

st.plotly_chart(fig_athlete_history)

fig_athlete_history = px.line(df_athleteHistory, x="Date", y = "Final Rank", title = "Rank by Date", markers = "True", color="Athlete")
fig_athlete_history.update_traces(textposition="top right")

st.plotly_chart(fig_athlete_history)

fig_athlete_history = px.line(df_athleteHistory, x="Age", y = ["200m"], title = "Times by Age", markers = "True", color="Athlete")
fig_athlete_history.update_traces(textposition="top right")

st.plotly_chart(fig_athlete_history)

fig_athlete_history = px.line(df_athleteHistory, x="Age", y = "Final Rank", title = "Final Rank by Age", markers = "True", color="Athlete")


st.plotly_chart(fig_athlete_history)

fig_athlete_history = px.line(df_athleteHistory, x="Age", y = "Final CSE", title = "Conservative Skill Estimate by Age", markers = "True", color="Athlete")


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








# st.markdown("---")
    
# st.title(":date: Points Tool")

# dates = df_points['Date'].drop_duplicates().sort_values()

# today = datetime.date.today()
# year_ago = today + datetime.timedelta(days=-365)


# start_date = st.date_input('Period Start:', year_ago)
# end_date = st.date_input('Period Finish:', today)
# df_points_dates = df_points[(df_points['Date'] > start_date) & (df_points['Date'] < end_date)]
# st.write("Number of days: "+str((end_date-start_date).days))

# df_points_dates=df_points_dates.sort_values("Current_Rank")

# st.dataframe(df_points_dates)
# #df_points_topten = df_points.sort_values("Time").head(10)

# names = df_points_dates['Name'].drop_duplicates()


# df_grouped = df_points_dates.groupby(by="Name")["Points"].sum()

# df_grouped = df_grouped.to_frame()
# df_grouped = df_grouped.sort_values(by="Points",ascending=False)
    
# st.header(":moneybag: Top 50")
# df_grouped.insert(0, 'Rank', range(1, 1+len(df_grouped)))
# st.dataframe(df_grouped.head(50))

###Trueskill Stuff

st.markdown("---")
    
st.title(":brain: Trueskill - Head to Head")

df_TS = df_TS.drop_duplicates("Athlete",keep="last")
#athlete_TS = st.multiselect("Select Athlete(s):", latest_TS)

ath1 = st.selectbox("Select Athlete 1:", df_TS["Athlete"].sort_values(), key="df_TS")
ath2 = st.selectbox("Select Athlete 2:", df_TS["Athlete"].sort_values(), key="df_TS_2")

ind1 = df_TS.index[df_TS['Athlete'] == ath1]
ind2 = df_TS.index[df_TS['Athlete'] == ath2]
sig1 = df_TS["Sigma"][ind1].item()
sig2 = df_TS["Sigma"][ind2].item()
mu1 = df_TS["Mu"][ind1].item()
mu2 = df_TS["Mu"][ind2].item()
name1 = df_TS["Athlete"][ind1].item()
name2 = df_TS["Athlete"][ind2].item()
trials=10000
### -TESTING




#x-axis ranges from -3 and 3 with .001 steps
x = np.arange(0, 50, 0.001)

#plot normal distribution with mean 0 and standard deviation 1
plt.plot(x, norm.pdf(x, mu1, sig1), label=df_TS["Athlete"][ind1].iloc[0])
plt.plot(x, norm.pdf(x, mu2, sig2), label=df_TS["Athlete"][ind2].iloc[0])
plt.legend()


s1 = np.random.normal(mu1, sig1, trials)
s2 = np.random.normal(mu2, sig2, trials)
s1_wins=0
for i in range(len(s1)):
    if s1[i]>s2[i]:
        s1_wins+=1
s1_win_prob = s1_wins/trials*100
s2_win_prob=100-s1_win_prob
left_column, middle_column, right_column = st.columns(3)
with left_column:

    st.write(name1 + " has mu value " + str(mu1) + " and sigma value " + str(sig1))
    st.write("From " +str(trials) + " trials, " + name1 + " has a " + str(round(s1_win_prob,2))+ "% chance of beating " + name2)
    
with middle_column:

    st.pyplot(plt)


with right_column:

    st.write(name2 + " has mu value " + str(mu2) + " and sigma value " + str(sig2))
    st.write("From " +str(trials) + " trials, " + name2 + " has a " + str(round(s2_win_prob,2))+ "% chance of beating " + name1)
    
    
    
    
###Multi competitor race simulator    
    
    
    

st.markdown("---")
    
st.title(":brain: Trueskill - Race Simulator")

df_TS_multi = df_TS.drop_duplicates("Athlete",keep="last")
plt.figure(1)
aths = st.multiselect("Select Athletes:", df_TS_multi["Athlete"].sort_values(), key="df_TS_multi")


for j in range(len(aths)):
    exec(f'scores{j} = []')
    exec(f'ranks{j} = []')
    ind = df_TS_multi.index[df_TS_multi['Athlete'] == aths[j]]
    sig = df_TS_multi["Sigma"][ind].item()
    mu = df_TS_multi["Mu"][ind].item()
    plt.figure(0)
    plt.plot(x, norm.pdf(x, mu, sig), label=aths[j])
    
    exec(f'scores{j} = np.random.normal(mu, sig, trials)')
    
left_column, middle_column, right_column = st.columns(3)

with middle_column:
    plt.legend()
    st.pyplot(plt)
    
    
for i in range(trials): 
    scores = []
    for j in range(len(aths)):
        exec(f'scores.append(scores{j}[i])')
    for k in range(len(aths)):
        exec(f'ranks{k}.append(sorted(scores,reverse=True).index(scores[k])+1)')

i=1


# sum(int(f'ranks{i}[0]')) / len(int(f'ranks{i}[0]'))        
        
for i in range(len(aths)):
    exec(f'st.write(aths[i]+ " has average rank " + str(round(sum(ranks{i})/len(ranks{i}),2)))')
    for j in range(len(aths)):
        exec(f'st.write("His likelihood of gaining rank " + str(j+1) + " is "+ str(round(ranks{i}.count(j+1)/len(ranks{i}),3)))')
    st.write("")