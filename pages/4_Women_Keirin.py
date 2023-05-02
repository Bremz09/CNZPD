#!/usr/bin/env python
# coding: utf-8
#change


import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image
import datetime
#from matplotlib.pyplot import figure
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm
import io



st.set_page_config(page_title='CNZ Performance Database',
                  page_icon=":bike:",
                  layout="wide")
st.header('Women\'s Keirin')
st.subheader('All results')

@st.cache_data
def get_data_from_excel():
    df = pd.read_excel(
        io='pages/WomensRaceResults.xlsm',
        engine ='openpyxl',
        sheet_name='Keirin_Trueskill',
        skiprows=0,
        usecols='A:Q',
        nrows=5000
        )
    df = df.replace(',','')
    df['Date'] = pd.to_datetime(df['Date']).dt.date
    #df=df.drop(["UCI_ID","ExpectedRank","RatingChange"],axis=1)
    return df
df= get_data_from_excel()


c1,c2,c3=st.columns(3)
df_orig = df

@st.cache_data
def convert_to_csv(df):
    return df.to_csv(index=False,sep = ",").encode('utf-32')

with c1:
    year = st.multiselect(
        "Select Year:",
        options=df["Year"].unique(),
        default=df["Year"].unique()[-1]
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
    label="Download Keirin data as CSV",
    data=csv,
    file_name='Keirin_Data.csv',
    mime='text/csv',
    key="buffer1"
)
buffer = io.BytesIO()
with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
    df.to_excel(writer, sheet_name='Sheet1', index=False)
    writer.save()
    download2 = st.download_button(
        label="Download Keirin data as Excel",
        data=buffer,
        file_name='Keirin_Data.xlsx',
        mime='application/vnd.ms-excel',
        key="buffer2"
    )
##Download buttons complete

st.markdown("---")
    
st.title(":bicyclist: Athlete History")

athletes = df_orig['Athlete'].drop_duplicates().sort_values()
athlete = st.multiselect("Select Athlete(s):", athletes)

df_athleteHistory = df_orig.query(
    "Athlete == @athlete"
)
if len(athlete)!=0:
    st.dataframe(df_athleteHistory,use_container_width=True)
    ##Download buttons
    csv_ah = convert_to_csv(df_athleteHistory)
    download1 = st.download_button(
        label="Download Keirin data as CSV",
        data=csv_ah,
        file_name='Keirin_Data.csv',
        mime='text/csv',
        key="bufferah1"
    )
    buffer_ah = io.BytesIO()
    with pd.ExcelWriter(buffer_ah, engine='xlsxwriter') as writer:
        df_athleteHistory.to_excel(writer, sheet_name='Sheet1', index=False)
        writer.save()
        download2 = st.download_button(
            label="Download Keirin data as Excel",
            data=buffer_ah,
            file_name='Keirin_Data.xlsx',
            mime='application/vnd.ms-excel',
            key="bufferah2"
        )
    ##Download buttons complete

    fig_athlete_history = px.scatter(df_athleteHistory, x="Date", y = ["Rank"], title = "Rank by Date", text = "Location", color="Athlete")
    fig_athlete_history.update_traces(textposition="top right")

    st.plotly_chart(fig_athlete_history,use_container_width=True)

    fig_athlete_history = px.line(df_athleteHistory, x="Date", y = "Final CSE", title = "Trueskill by Date", markers = "True", color="Athlete")
    fig_athlete_history.update_traces(textposition="top right")

    st.plotly_chart(fig_athlete_history,use_container_width=True)

    fig_athlete_history = px.scatter(df_athleteHistory, x="Age", y = ["Rank"], title = "Rank by Age", color="Athlete")
    fig_athlete_history.update_traces(textposition="top right")

    st.plotly_chart(fig_athlete_history,use_container_width=True)

    fig_athlete_history = px.line(df_athleteHistory, x="Age", y = "Final CSE", title = "Trueskill by Age", markers = "True", color="Athlete")


    st.plotly_chart(fig_athlete_history,use_container_width=True)





st.markdown("---")
    
st.title(":brain: Trueskill - Head to Head")

df_TS = df_orig.drop_duplicates("Athlete",keep="last")
#athlete_TS = st.multiselect("Select Athlete(s):", latest_TS)
c1,c2=st.columns(2)
with c1:
    ath1 = st.selectbox("Select Athlete 1:", df_TS["Athlete"].sort_values(), key="df_TS")
with c2:
    ath2 = st.selectbox("Select Athlete 2:", df_TS["Athlete"].sort_values(), key="df_TS_2")
trials=10000
#x-axis ranges from -3 and 3 with .001 steps
x = np.arange(0, 50, 0.001)
if ath1!=ath2:

    ind1 = df_TS.index[df_TS['Athlete'] == ath1]
    ind2 = df_TS.index[df_TS['Athlete'] == ath2]
    sig1 = df_TS["Sigma"][ind1].item()
    sig2 = df_TS["Sigma"][ind2].item()
    mu1 = df_TS["Mu"][ind1].item()
    mu2 = df_TS["Mu"][ind2].item()
    name1 = df_TS["Athlete"][ind1].item()
    name2 = df_TS["Athlete"][ind2].item()
    


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
        st.write("From " +str(trials) + " trials, " + name2 + " has a " + str(s2_win_prob)+ "% chance of beating " + name1)
    
    
    
    
###Multi competitor race simulator    
    
    
    

st.markdown("---")
    
st.title(":brain: Trueskill - Race Simulator")

df_TS_multi = df_orig.drop_duplicates("Athlete",keep="last")
plt.figure(1)
aths = st.multiselect("Select Athletes:", df_TS_multi["Athlete"].sort_values(), key="df_TS_multi")
if len(aths)>1:

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
        exec(f'st.subheader(aths[i]+ " has average rank " + str(round(sum(ranks{i})/len(ranks{i}),2)))')
        for j in range(len(aths)):
            exec(f'st.write("His likelihood of gaining rank " + str(j+1) + " is "+ str(round(ranks{i}.count(j+1)/len(ranks{i}),3)))')
        st.write("")