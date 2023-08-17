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
from st_aggrid import AgGrid

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

    df_master = pd.read_excel(f'pages/CdA Testing/Track CdA Testing.xlsx')
    
    st.image("https://www.google.com/url?sa=i&url=https%3A%2F%2Fwww.searchenginejournal.com%2Fbest-image-search-engines%2F299963%2F&psig=AOvVaw01VD3L75czzGxif3e00nQu&ust=1692315357969000&source=images&cd=vfe&opi=89978449&ved=0CBAQjRxqFwoTCLjI_o-s4oADFQAAAAAdAAAAABAE")
    

    df_master['Date'] = pd.to_datetime(df_master['Date'],format= '%Y/%m/%d' ).dt.date
    
    df_master
    
    st.header("Video")
    
    c1,c2,c3=st.columns(3)
    with c1:
        athlete = st.selectbox(
        "Select Athlete:",
        options=df_master["Name"].unique()
        ) 
        
    df=df_master.loc[df_master["Name"]==athlete]
    with c2:
        dates = st.multiselect(
        "Select Dates:",
        options=df["Date"].unique()
        ) 
    if len(dates)>0:
        df=df.loc[df["Date"].isin(dates)]
    df=df.reset_index()
    df
    with c3:
        video = st.selectbox(
        "Show Video?",
        options=["No","Yes"]
        )     

    
    ##Download buttons
    @st.cache_data
    def convert_to_csv(df):
        return df.to_csv(index=False,sep = ",").encode('utf-32')
    csv = convert_to_csv(df)
    download1 = st.download_button(
        label=f"Download {athlete}'s CdA data as CSV",
        data=csv,
        file_name=f'{athlete}_Data.csv',
        mime='text/csv'
    )
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Sheet1', index=False)
        writer.save()
        download2 = st.download_button(
            label=f"Download {athlete}'s CdA data as Excel",
            data=buffer,
            file_name=f'{athlete}_CdA_Data.xlsx',
            mime='application/vnd.ms-excel'
        )
    ##Download buttons complete
    st.markdown("---")
    if video == "Yes":
        
        for i in range(len(df)):
            if len(str(df["Video"][i]))>4:
                c1,c2 = st.columns(2)
                with c1:
                    st.write(f'Rider: {df["Name"][i]}')
                    st.write(f'Date (Y-M-D): {df["Date"][i]}')
                    st.write(f'Position: {df["Position"][i]}')
                    st.write(f'Clothing: {df["Clothing"][i]}')
                    st.write(f'Shoe covers: {df["Shoe cover"][i]}')
                    st.write(f'Shoes: {df["Shoes"][i]}')
                    st.write(f'Helmet: {df["Helmet"][i]}')
                    st.write(f'Bike: {df["Bike"][i]}')
                    st.write(f'Wheels: {df["Wheels"][i]}')
                    st.write(f'Cranks: {df["Cranks"][i]}')
                    st.write(f'Rider weight: {df["Rider weight"][i]}')
                    st.write(f'Bike weight: {df["System weight (kg)"][i]}')
                    st.write(f'System weight: {df["Clothing"][i]}')
                    st.write(f'Tyre pressure: {df["Tyre pressure"][i]}')
                    st.write(f'Gear: {df["Gear"][i]}')
                    
                    st.write(f'Notio CdA: {df["CdA - Notio"][i]}')
                    st.write(f'Goldmine CdA: {df["CdA"][i]}')
                    st.write(f'Speed: {df["Speed"][i]}')
                    st.write(f'Power: {df["Power"][i]}')
                    st.write(f'Distance: {df["Distance (m)"][i]}m')
                    
                    st.write(f'Speed: {df["Speed"][i]}')
                    st.write(f'Speed: {df["Speed"][i]}')
                    st.write(f'Speed: {df["Speed"][i]}')
                    
                    
                with c2:
                    video_name = df["Video"][i]

                    st.video(f"{video_name}")
                st.markdown('---')
    
    
    
