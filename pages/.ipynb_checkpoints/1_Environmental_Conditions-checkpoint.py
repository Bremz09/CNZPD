#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image
import numpy as np
from io import StringIO
from openpyxl import load_workbook
from plotly.subplots import make_subplots
import xlwings as xw
import datetime
import io
import time

st.set_page_config(page_title='CNZ Performance Database',
                  page_icon=":bike:",
                  layout="wide")

# --- USER AUTHENTICATION ---
import streamlit_authenticator as stauth 
import pickle
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

    ##This bit is the historical visualiser

    st.header("All Data")
    t0=time.time()
    @st.cache_data
    def get_master():
        df=pd.read_excel(f'pages/Environmental_Data/Uni_t_data_master.xlsx',usecols='A:E', nrows=183000)
        return df
    df_master = get_master()
    t1=time.time()
    st.write(f"read excel takes {t1-t0} seconds")
    df_master["Date"] = df_master["DateTime"].dt.date
    df_master["Time"] = df_master["DateTime"].dt.time
    t2=time.time()
    st.write(f"adding dates stuff takes {t2-t1} seconds")


    ##Gross start/end date getting stuff

    df_master=df_master[["DateTime","Date","Time","Temperature(C)","Relative_Humidity(%)","Pressure(hPa)","Dew_Point(C)"]]
    
    
    
    ##Adding Air Density
    c0=0.99999683
    c1 = -0.90826951e-2
    c2 = 0.78736169e-4
    c3 = -0.61117958e-6
    c4 = 0.43884187e-8
    c5 = -0.29883885e-10
    c6 = 0.21874425e-12
    c7 = -0.17892321e-14
    c8 = 0.11112018e-16
    c9 = -0.30994571e-19
    df_master["Temperature(K)"] = df_master["Temperature(C)"]+273.15
    df_master["p(T)"] = c0 + df_master["Temperature(C)"]*(c1 + df_master["Temperature(C)"]*(c2 + df_master["Temperature(C)"]*(c3 + df_master["Temperature(C)"]*(c4 + df_master["Temperature(C)"]*(c5 + df_master["Temperature(C)"]*(c6 + df_master["Temperature(C)"]*(c7 + df_master["Temperature(C)"]*(c8 + df_master["Temperature(C)"]*(c9)))))))))
    df_master["Es(T)"] = 6.1078/(pow(df_master["p(T)"],8))
    df_master["Pwvp(Pa)"] = df_master["Relative_Humidity(%)"]*df_master["Es(T)"]

    df_master["Air_Density(kg/m^3)"] = (df_master["Pwvp(Pa)"])/(461.495*(df_master["Temperature(K)"])) + ((df_master["Pressure(hPa)"]*100) - df_master["Pwvp(Pa)"])/(287.05*(df_master["Temperature(K)"]))
   
    col1,col2,c3,c4 = st.columns(4)
    with col1:
        start = st.date_input(
            "Select Start Date:",
            value = df_master["Date"][len(df_master)-2],
            key="start")
    with col2:
        finish = st.date_input(
            "Select End Date:",
            value = df_master["Date"][len(df_master)-2],
            key="fin_date")
    
    
    start=start+pd.Timedelta(days=-1)
    mask = (df_master['Date'] > start) & (df_master['Date'] <= finish)
    df = df_master.loc[mask]
    df=df.reset_index(drop=True)
    if len(df)>0:

        with c3:
            start_time = st.time_input(
                "Refine Start Time:",
                df["Time"][0],
                key="start_time")
        with c4:
            finish_time = st.time_input(
                "Refine End Time:",
                df["Time"][len(df)-1],
            key="fin_time")    




        mask_time = (df['Time'] > start_time) & (df['Time'] <= finish_time)
        df = df.loc[mask_time]
        df

        st.header("Data Summary")
        m_temp=round(df["Temperature(C)"].mean(),4)
        sd_temp=round(df["Temperature(C)"].std(),4)
        m_humid=round(df["Relative_Humidity(%)"].mean(),4)
        sd_humid=round(df["Relative_Humidity(%)"].std(),4)
        m_pressure=round(df["Pressure(hPa)"].mean(),4)
        sd_pressure=round(df["Pressure(hPa)"].std(),4)
        m_density=round(df["Air_Density(kg/m^3)"].mean(),4)
        sd_density=round(df["Air_Density(kg/m^3)"].std(),4)
        st.write(f"Mean Air Density is {m_density} kg/m^3 with standard deviation {sd_density} kg/m^3")
        st.write(f"Mean Temperature is {m_temp} C with standard deviation {sd_temp} C")
        st.write(f"Mean Relative Humidity is {m_humid}% with standard deviation {sd_humid}%")
        st.write(f"Mean Pressure is {m_pressure} hPa with standard deviation {sd_pressure} hPa")


        ##Download buttons
        @st.cache_data
        def convert_to_csv(df):
            return df.to_csv(index=False,sep = ",").encode('utf-32')
        csv = convert_to_csv(df)
        download1 = st.download_button(
            label="Download Environmental data as CSV",
            data=csv,
            file_name='Enviro_Data.csv',
            mime='text/csv'
        )
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='Sheet1', index=False)
            writer.close()
            download2 = st.download_button(
                label="Download Environmental data as Excel",
                data=buffer,
                file_name='Enviro_Data.xlsx',
                mime='application/vnd.ms-excel'
            )
        ##Download buttons complete

        fig = px.scatter(df, x="DateTime", y = "Air_Density(kg/m^3)", title="Air Density (kg/m^3)")
        st.plotly_chart(fig, use_container_width=True)

        fig = px.scatter(df, x="DateTime", y = "Temperature(C)", title="Temperature(C)")
        st.plotly_chart(fig, use_container_width=True)

        fig = px.scatter(df, x="DateTime", y = "Relative_Humidity(%)", title="Relative Humidity (%)")
        st.plotly_chart(fig, use_container_width=True)

        fig = px.scatter(df, x="DateTime", y = "Pressure(hPa)", title="Pressure (hPa)")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.write("No data yet, tell Sam to hurry up!")



    
