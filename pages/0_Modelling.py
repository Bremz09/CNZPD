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
    
#     st.title("Simple CSS Shape Generator")

#     activity = ['Design','About',]
#     choice = st.selectbox("Select Activity",activity)

#     if choice == 'Design':
#         st.subheader("Design")
#         bgcolor = st.color_picker("Pick a Background color")
#         fontcolor = st.color_picker("Pick a Font Color","#fff")

#         html_temp = """
#         <div style="background-color:{};padding:10px">
#         <h1 style="color:{};text-align:center;">Streamlit Simple CSS Shape Generator </h1>
#         </div>
#         """
#         st.markdown(html_temp.format(bgcolor,fontcolor),unsafe_allow_html=True)
#         st.markdown("<div><p style='color:{}'>Hello Streamlit</p></div>".format(bgcolor),unsafe_allow_html=True)


#         st.subheader("Modify Shape")
#         bgcolor2 = st.color_picker("Pick a Bckground color")
#         height = st.slider('Height Size',50,200,50)
#         width = st.slider("Width Size",50,200,50)
#         # border = st.slider("Border Radius",10,60,10)
#         top_left_border = st.number_input('Top Left Border',10,50,10)
#         top_right_border = st.number_input('Top Right Border',10,50,10)
#         bottom_left_border = st.number_input('Bottom Left Border',10,50,10)
#         bottom_right_border = st.number_input('Bottom Right Border',10,50,10)

#         border_style = st.selectbox("Border Style",["dotted","dashed","solid","double","groove","ridge","inset","outset","none","hidden"])
#         border_color = st.color_picker("Pick a Border Color","#654FEF")
#         st.markdown(html_temp.format(height,width,bgcolor2,top_left_border,top_right_border,bottom_left_border,bottom_right_border,border_style,border_color),unsafe_allow_html=True)

#     if st.checkbox("View Results"):
#             st.subheader("Result")
#             result_of_design = html_temp.format(height,width,bgcolor2,top_left_border,top_right_border,bottom_left_border,bottom_right_border,border_style,border_color)
#             st.code(result_of_design)

#     if choice =="About":
#         st.subheader("About")

    
    st.subheader("Bike Specs")
    c1,c2,c3,c4,c5,c6,c7 =st.columns(7)
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
    with c7:
        gear_ratio = st.number_input("Gear Ratio:", min_value=0.00, max_value=150.00,value=120.00)
    st.subheader("Environment")
    #8 sections of the track, 4 sections where angle increases linearly from straight to bank angle (or vice versa)
    #Maybe add lengths of these sections in
    #Use circumference and bank angles to determine r_m radius of curvature for COM
    c1,c2,c3,c4,c5,c6 =st.columns(6)
    with c1:
        circumferences = [250,333,500]
        track_circumference = st.selectbox("Track Circumference:", circumferences, key="Track_circumference")
    with c2:
        straight_bank_angle = st.number_input("Straight Bank Angle:", min_value=0.00, max_value=90.00,value=16.00)
    with c4:
        transition_length = st.number_input("Straight to corner transition length:", min_value=0.00, max_value=90.00,value=10.00)
    with c3:
        bend_bank_angle = st.number_input("Bend Bank Angle:", min_value=0.00, max_value=90.00,value=42.00)
    with c5:
        air_density = st.number_input("Air Density (kg/m^3):", min_value=0.0000, max_value=10.0000,value=1.1818,
    step=1e-4, format="%.4f")
    with c6:
        mu_rr = st.number_input("Rolling Resistance Coefficient:", min_value=0.0000, max_value=0.0050,value=0.0016,
    step=1e-4, format="%.4f")
    st.subheader("Rider Specs")
    c1,c2,c3,c4,c5 =st.columns(5)
    with c1:
        cda = st.number_input("CdA:", min_value=0.0000, max_value=1.0000,value=0.1780,
    step=1e-4, format="%.4f")
    with c2:
        rider_weight = st.number_input("Rider Weight (kit on):", min_value=30.00, max_value=150.00,value=80.00)
    with c3:
        vo2_max = st.number_input("VO2 Max:", min_value=0.00, max_value=100.00,value=80.00)
    with c4:
        co2_def = st.number_input("O2 Deficit:", min_value=0.00, max_value=20.00,value=20.00)
    with c5:
        max_torque = st.number_input("Max Torque (Nm):", min_value=0.00, max_value=70.00,value=35.00)
    st.subheader("5 Minute Power Profile Editor")
    c1, c2 = st.columns([1, 3])
    with c1:
        max_power = st.number_input("Max Power:", min_value=0.00, max_value=3000.00,value=1500.17,
    step=1e-4, format="%.2f")
        max_power_time = st.number_input("Time Max Power is Achieved:", min_value=0.00, max_value=60.00,value=10.17,
    step=1e-4, format="%.2f")
        steady_power = st.number_input("Steady State Power:", min_value=0.00, max_value=800.00,value=450.17,
    step=1e-4, format="%.2f")
        steady_power_time = st.number_input("Time Steady Power is Reached:", min_value=0.00, max_value=60.00,value=20.17,
    step=1e-4, format="%.2f")
    with c2:
        increment=1000
        x = np.linspace(0, 300, num=300*increment + 1)
        i = 1
        y=np.linspace(0, 0, num=300*increment + 1)
        y[0] = 0
        if x[i] <= max_power_time:
            y[i] = y[i-1] + max_power/max_power_time
            i+=1
        elif x[i] <= steady_power_time:
            y[i] = y[i-1] - (max_power-steady_power)/(steady_power_time-max_power_time)
            i+=1
        fig = px.line(x=x, y = y, title="5 Minute Power")
        fig.update_xaxes(title="Seconds")
        fig.update_yaxes(title="Power (W)")
        st.plotly_chart(fig, use_container_width=True)
    ###Modelling bit
    
    beta = straight_bank_angle
    k_s = 0.0072
    def initial_accel():
        f_w = 9.80665*(bike_weight+rider_weight)
        mu_s = 1 + beta*k_s
        f_rr = f_w*mu_rr*mu_s
        a_cm = (max_torque/(gear_ratio*wheel_radius) - f_rr)/(bike_weight+rider_weight)
        return a_cm
    a_cm = initial_accel()
    st.write(a_cm)
    