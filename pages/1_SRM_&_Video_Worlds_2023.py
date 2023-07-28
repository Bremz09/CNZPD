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
import os.path



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

    df_master = pd.read_excel(f'pages/Worlds_2023/Master.xlsx')
    
    st.header("Single Rider SRM data and video")
   
    filename = st.selectbox(
        "Select Race:",
        options=df_master["FileName"].unique()
        ) 
    
    df = pd.read_csv(f'pages/Worlds_2023/{filename}.csv')
    
    #df=df.drop(columns=["Heartrate","L/R Balance(if available) [percentage of right Leg]","Altitude [m]","latitude","longitude"])
    df=df.iloc[: , :-6]
    
    c1,c2=st.columns((1,2))
    with c1:
        df
        ##Download buttons
        @st.cache_data
        def convert_to_csv(df):
            return df.to_csv(index=False,sep = ",").encode('utf-32')
        csv = convert_to_csv(df)
        download1 = st.download_button(
            label="Download SRM data as CSV",
            data=csv,
            file_name=f'{filename} SRM Data.csv',
            mime='text/csv'
        )
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='Sheet1', index=False)
            writer.save()
            download2 = st.download_button(
                label="Download SRM data as Excel",
                data=buffer,
                file_name=f'{filename} SRM Data.xlsx',
                mime='application/vnd.ms-excel'
            )
        ##Download buttons complete
    with c2:
        ind = df_master.index[df_master["FileName"]==filename][0]
        video_name = df_master["Video"].iloc[ind]
        st.video(f"{video_name}")
    
        ##Now compare riders for tp etc. Another component which uses multiselect. If all videos match, show video. Also plot the 
        ##Powers etc for all riders on one plot.
    
    fig_all = px.line(df, x="Time", y = ["Cadence","Speed [km/h]","Power [watt]"], title="Cadence")

    st.plotly_chart(fig_all, use_container_width=True)
    
    
    st.markdown("---")
    st.header("Rider comparison (must be from the same race)")
    selections = st.multiselect(
            "Select rides to compare:",
            options=df_master["FileName"].unique()
            ) 
    
    if len(selections)>1:
        df_comp = pd.read_csv(f'pages/Worlds_2023/{selections[0]}.csv')
        df_comp=df_comp.iloc[: , :-6]
        init = selections[0].split('_')[3]
        
        df_comp.rename(columns={'Cadence': f'{init} Cadence', 'Speed [km/h]': f'{init} Speed', 'Power [watt]': f'{init} Power'}, inplace=True)
        
        for i in range(1,len(selections)):
            df2 = pd.read_csv(f'pages/Worlds_2023/{selections[i]}.csv')
            df2=df2.iloc[: , :-6]
            init = selections[i].split('_')[3]
            df2.rename(columns={'Cadence': f'{init} Cadence', 'Speed [km/h]': f'{init} Speed', 'Power [watt]': f'{init} Power'}, inplace=True)
            df_comp = pd.merge(df_comp,df2,on="Time", how="inner")
        c1,c2=st.columns((1,2))
        with c1:
            if len(df_comp)>0:
                df_comp
                ##Download buttons
                @st.cache_data
                def convert_to_csv(df_comp):
                    return df_comp.to_csv(index=False,sep = ",").encode('utf-32')
                csv = convert_to_csv(df_comp)
                download1 = st.download_button(
                    label="Download combined SRM data as CSV",
                    data=csv,
                    file_name=f'Combined SRM Data.csv',
                    mime='text/csv'
                )
                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                    df_comp.to_excel(writer, sheet_name='Sheet1', index=False)
                    writer.save()
                    download2 = st.download_button(
                        label="Download combined SRM data as Excel",
                        data=buffer,
                        file_name=f'Combined SRM Data.xlsx',
                        mime='application/vnd.ms-excel'
                    )
                ##Download buttons complete
        with c2:
            if len(df_comp)>0:
                ind2 = df_master.index[df_master["FileName"]==selections[0]][0]
                video_name_2 = df_master["Video"].iloc[ind2]
                st.video(f"{video_name_2}")
        if len(df_comp)>0:
            fig_comp = px.line(df_comp, x="Time", y = df_comp.columns, title="Cadence")

            st.plotly_chart(fig_comp, use_container_width=True)
    else:
        st.subheader("Pick two or more riders in the same race")
    
    
    
    