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
    st.header('Modelling Tool')

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


    
    
    calcs = ["Power for Speed","Time for Power","CdA at Speed"]
    
    Calc = st.selectbox("Select Calculator:", calcs, key="Calc_selector")
    st.subheader("Bike Specs")
    c1,c2,c3,c4,c5,c6 =st.columns(6)
    with c1:
        bike_stiffness = st.number_input("Bike Stiffness:", min_value=0.00, max_value=100.00,value=99.99)
    with c2:
        chain_efficiency = st.number_input("Chain Efficiency:", min_value=0.00, max_value=100.00,value=99.99)
    with c3:
        bearing_efficiency = st.number_input("Bearing Efficiency:", min_value=0.00, max_value=100.00,value=99.99)
    with c4:
        bike_weight = st.number_input("Bike Weight (kg):", min_value=0.00, max_value=20.00,value=8.50)
    with c5:
        wheel_radius = st.number_input("Wheel Radius (m):", min_value=0.00, max_value=1.00,value=0.40)
    with c6:
        seat_height = st.number_input("Seat Height (m):", min_value=0.00, max_value=2.00,value=1.00)
    st.subheader("Environment")
    #8 sections of the track, 4 sections where angle increases linearly from straight to bank angle (or vice versa)
    #Maybe add lengths of these sections in
    #Use circumference and bank angles to determine r_m radius of curvature for COM
    c1,c2,c3,c4,c5 =st.columns(5)
    with c1:
        circumferences = [250,333,500]
        track_circumference = st.selectbox("Track Circumference:", circumferences, key="Track_circumference")
    with c2:
        straight_bank_angle = st.number_input("Straight Bank Angle:", min_value=0.00, max_value=90.00,value=16.00)
    with c3:
        bend_bank_angle = st.number_input("Bend Bank Angle:", min_value=0.00, max_value=90.00,value=42.00)
    with c4:
        air_density = st.number_input("Air Density (kg/m^3):", min_value=0.0000, max_value=10.0000,value=1.1818,
    step=1e-4, format="%.4f")
    with c5:
        rolling_resistance_coefficient = st.number_input("Rolling Resistance Coefficient:", min_value=0.0000, max_value=0.0050,value=0.0016,
    step=1e-4, format="%.4f")
    st.subheader("Rider Specs")
    c1,c2,c3,c4 =st.columns(4)
    with c1:
        cda = st.number_input("CdA:", min_value=0.0000, max_value=1.0000,value=0.1780,
    step=1e-4, format="%.4f")
    with c2:
        rider_weight = st.number_input("Rider Weight (kit on):", min_value=30.00, max_value=150.00,value=80.00)
    with c3:
        vo2_max = st.number_input("VO2 Max:", min_value=0.00, max_value=100.00,value=80.00)
    with c4:
        co2_def = st.number_input("CO2 Deficit:", min_value=0.00, max_value=20.00,value=20.00)
 



