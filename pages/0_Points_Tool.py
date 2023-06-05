#!/usr/bin/env python
# coding: utf-8


import pickle
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image
import datetime
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm
import os
import pytz
import streamlit_authenticator as stauth


st.set_page_config(page_title='CNZ Performance Database',
                  page_icon=":bike:",
                  layout="wide")

# --- USER AUTHENTICATION ---

# load hashed passwords
with open("hashed_pw.pkl","rb") as file:
    hashed_passwords = pickle.load(file)


usernames = ['CNZ']
names = ['CNZ']


credentials = {"usernames":{}}
        
for uname,name,pwd in zip(usernames,names,hashed_passwords):
    user_dict = {"name": name, "password": pwd}
    credentials["usernames"].update({uname: user_dict})
        
authenticator = stauth.Authenticate(credentials, "CNZPD", "abcdef", cookie_expiry_days=30)

name, authentication_status, username = authenticator.login("Login", "main")

if authentication_status == False:
    st.error("Username/password is incorrect")

if authentication_status == None:
    st.warning("Please enter your username and password")

if authentication_status:
    st.header('Points Tool')

    update = datetime.date.today()+ pd.DateOffset(hour=12)


    #@st.cache_data

    def get_MK_points_data_from_excel():
        df_MK = pd.read_excel(
            io='pages/Kierin_Points_Men.xlsx',
            engine ='openpyxl',
            sheet_name='Kierin_Points_Men',
            skiprows=0,
            usecols='A:J',
            nrows=3000
            )
        df_MK = df_MK.replace(',','')
        df_MK['Date'] = pd.to_datetime(df_MK['Date']).dt.date
        return df_MK
    df_MK = get_MK_points_data_from_excel()



    def get_MS_points_data_from_excel():
        df_MS = pd.read_excel(
            io='pages/Sprint_Points_Men.xlsx',
            engine ='openpyxl',
            sheet_name='Sprint_Points_Men',
            skiprows=0,
            usecols='A:J',
            nrows=3000
            )
        df_MS = df_MS.replace(',','')
        df_MS['Date'] = pd.to_datetime(df_MS['Date']).dt.date
        return df_MS
    df_MS = get_MS_points_data_from_excel()





    def get_WS_points_data_from_excel():
        df_WS = pd.read_excel(
            io='pages/Sprint_Points_Women.xlsx',
            engine ='openpyxl',
            sheet_name='Sprint_Points_Women',
            skiprows=0,
            usecols='A:J',
            nrows=3000
            )
        df_WS = df_WS.replace(',','')
        df_WS['Date'] = pd.to_datetime(df_WS['Date']).dt.date
        return df_WS
    df_WS = get_WS_points_data_from_excel()




    def get_WK_points_data_from_excel():
        df_WK = pd.read_excel(
            io='pages/Kierin_Points_Women.xlsx',
            engine ='openpyxl',
            sheet_name='Kierin_Points_Women',
            skiprows=0,
            usecols='A:J',
            nrows=3000
            )
        df_WK = df_WK.replace(',','')
        df_WK['Date'] = pd.to_datetime(df_WK['Date']).dt.date
        return df_WK
    df_WK = get_WK_points_data_from_excel()

    def get_WTT_points_data_from_excel():
        df_WTT = pd.read_excel(
            io='pages/Time_Trial_Points_Women.xlsx',
            engine ='openpyxl',
            sheet_name='Time_Trial_Points_Women',
            skiprows=0,
            usecols='A:J',
            nrows=3000
            )
        df_WTT = df_WTT.replace(',','')
        df_WTT['Date'] = pd.to_datetime(df_WTT['Date']).dt.date
        return df_WTT
    df_WTT = get_WTT_points_data_from_excel()

    s = os.path.getmtime('pages/Kierin_Points_Women.xlsx')
    dt_m = datetime.date.fromtimestamp(s)+pd.DateOffset(days=1)
    s1 = dt_m.strftime("%d/%m/%Y")
    st.subheader("Last updated on "+ str(s1))
    Events = ["Men's Sprint","Men's Keirin", "Women's Sprint", "Women's Keirin","Women's 500 Time Trial"]

    Event = st.selectbox("Select Event:", Events, key="Event_selector")

    if Event == Events[0]:
        df=df_MS
    elif Event == Events[1]:
        df=df_MK
    elif Event == Events[2]:
        df=df_WS
    elif Event == Events[3]:
        df=df_WK
    else:
        df=df_WTT

    df_orig=df


    #st.subheader("Number of events for inclusion (shouldn't have to change these values)")
    today = datetime.date.today()
    default_start = datetime.date(2022, 6, 22)
    # col_one, col_two, col_three, col_four, col_five = st.columns(5)

    ### This was when you could change the number of events etc

    # with col_one:
    #     WC_events = st.number_input("UCI World Championships", min_value=0, max_value=None, value=1, key="WC")
    # with col_two:
    #     NC_events = st.number_input("Nations' Cup", min_value=0, max_value=None, value=1, key="NC")
    # with col_three:
    #     CC_events = st.number_input("Continental Championships", min_value=0, max_value=None, value=1, key="CC")
    # with col_four:
    #     NCH_events = st.number_input("National Championships", min_value=0, max_value=None, value=1, key="NCH")
    # with col_five:
    #     TCLOR_events = st.number_input("Track Champions League Overall Ranking", min_value=0, max_value=None, value=1, key="TCLOR")
    # col_one, col_two, col_three, col_four,col_five = st.columns(5)
    # with col_three:
    #     CTWO_events = st.number_input("Class 2", min_value=0, max_value=None, value=3, key="C2")
    # with col_one:
    #     TCLRR_events = st.number_input("Track Champions League Round Ranking", min_value=0, max_value=None, value=5, key="TCLRR")
    # with col_two:
    #     CONE_events = st.number_input("Class 1", min_value=0, max_value=None, value=3, key="C1")
    # with col_four:
    #     start_date = st.date_input('Period Start', default_start,key="Start date")
    # with col_five:
    #     end_date = st.date_input('Period Finish', today,key="End date")
    # col_one, col_two, col_three, col_four, col_five = st.columns(5)
    # with col_one:
    #     max_athletes = st.number_input("Max numbers of athletes from each nation", min_value=0, max_value=None, value=2, key="Max_athletes")

    ##Hard coded event numbers
    WC_events=1
    NC_events=1
    CC_events=1
    NCH_events=1
    TCLOR_events=1
    CTWO_events=3
    TCLRR_events=5
    CONE_events=3
    start_date = default_start
    end_date = datetime.date(2023, 6, 21)
    #max_athletes=2



    st.write("This sums the best World Champs, Nations Cup, Continental Champs, National Champs, and Overall Champions League points, as well as top three Class 1 and Class 2 points, and top five Champions League Round points, between " + str(start_date) + " and " + str(end_date))

    col_one, col_two, col_three, col_four = st.columns(4)
    with col_one:
        options = ["All athletes","Top two from each Nation"]
        Max_Ath = st.selectbox("Athletes shown:", options, key="Max Athletes")
    with col_two:
        kiwisOnly = ["No","Yes"]
        JustKiwis = st.selectbox("Show Kiwis Only?:", kiwisOnly, key="kiwis only")

    if Max_Ath=="Top two from each Nation":
        max_athletes = 2
    else:
        max_athletes = 200


    df = df[(df['Date'] > start_date) & (df['Date'] < end_date)]
    athletes = df['Name'].drop_duplicates()
    countries = []

    WC_totals = []
    NC_totals = []
    CC_totals = []
    NCH_totals = []
    TCLRR_totals = []
    TCLOR_totals = []
    CONE_totals = []
    CTWO_totals = []
    totals=[]
    allowed_athletes = []

    for i in range(len(athletes)):
        y = df.loc[(df.Name == athletes.iloc[i]),'Country'].iloc[0]
        if countries.count(y)<max_athletes:
            allowed_athletes.append(athletes.iloc[i])
            countries.append(y)
            total=0
            x = df.loc[(df.Class == "WCh") &  (df.Name == athletes.iloc[i]),'Points'].astype(int).sort_values(ascending=False)
            WC_total = sum(x[:WC_events])
            WC_totals.append(WC_total)
            total+=WC_total

            x = df.loc[(df.Class == "NCp") &  (df.Name == athletes.iloc[i]),'Points'].astype(int).sort_values(ascending=False)
            NC_total = sum(x[:NC_events])
            NC_totals.append(NC_total)
            total+=NC_total

            x = df.loc[(df.Class == "CCh") &  (df.Name == athletes.iloc[i]),'Points'].astype(int).sort_values(ascending=False)
            CC_total = sum(x[:CC_events])
            CC_totals.append(CC_total)
            total+=CC_total

            x = df.loc[(df.Class == "NCh") &  (df.Name == athletes.iloc[i]),'Points'].astype(int).sort_values(ascending=False)
            NCH_total = sum(x[:NCH_events])
            NCH_totals.append(NCH_total)
            total+=NCH_total

            x = df.loc[(df.Class == "ChL") &  (df.Name == athletes.iloc[i]),'Points'].astype(int).sort_values(ascending=False)
            TCLOR_total = sum(x[:TCLOR_events])
            TCLOR_totals.append(TCLOR_total)
            total+=TCLOR_total

            x = df.loc[(df.Class == "ChR") &  (df.Name == athletes.iloc[i]),'Points'].astype(int).sort_values(ascending=False)
            TCLRR_total = sum(x[:TCLRR_events])
            TCLRR_totals.append(TCLRR_total)
            total+=TCLRR_total

            x = df.loc[(df.Class == "CL1") &  (df.Name == athletes.iloc[i]),'Points'].astype(int).sort_values(ascending=False)
            CONE_total = sum(x[:CONE_events])
            CONE_totals.append(CONE_total)
            total+=CONE_total

            x = df.loc[(df.Class == "CL2") &  (df.Name == athletes.iloc[i]),'Points'].astype(int).sort_values(ascending=False)
            CTWO_total = sum(x[:CTWO_events])
            CTWO_totals.append(CTWO_total)
            total+=CTWO_total
            totals.append(total)



    Points = {'Name': allowed_athletes,
              'Country': countries,
              'Total': totals,
              'WCh': WC_totals,
              "NCp": NC_totals,
              'CCh': CC_totals,
              'NCh': NCH_totals,
              'ChL': TCLOR_totals,
              'ChR': TCLRR_totals,
              'CL1': CONE_totals,
              'CL2': CTWO_totals,

             }

    df_points=pd.DataFrame(Points).sort_values('Total',ascending=False)
    Rank = list(range(1,len(allowed_athletes)+1))
    df_points.insert(loc=0, column='Rank', value=Rank)
    if JustKiwis == "Yes":
        df_points = df_points.loc[(df_points.Country == "NZL")]
    df_points


    st.subheader("All Results")
    col_one, col_two = st.columns(2)

    Classes = df_orig['Class'].drop_duplicates().sort_values()
    Events = df_orig['Event'].drop_duplicates().sort_values()
    with col_one:
        Class = st.multiselect("Select Class(es):", Classes)

    df_class = df_orig.query(
        "Class == @Class"
    )

    if Class==[]:
        Events = df_orig['Event'].drop_duplicates().sort_values()
    else:
        Events = df_class['Event'].drop_duplicates().sort_values()
    with col_two:
        Event = st.multiselect("Select Event(s):", Events)

    df_event = df_orig.query(
        "Event == @Event"
    )

    df_both = df_orig.query(
        "Class == @Class & Event == @Event"
    )

    if Class==[] and Event==[]:
        st.dataframe(df_orig)
    elif Event==[]:
        st.dataframe(df_class)
    elif Class==[]:
        st.dataframe(df_event)
    else:
        st.dataframe(df_both)




