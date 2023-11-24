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
from streamlit_image_comparison import image_comparison
import streamlit.components.v1 as components


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
    show = st.selectbox(
            "Select Tool:",
            options=["Track Testing Video Viewer","Stored Image Comparison","Local Image Comparison"]
            ) 
    
    if show == "Stored Image Comparison":
    

        st.header("Compare Images")


        df_images = pd.read_excel(f'pages/CdA Testing/Wind Tunnel Images.xlsx')
        df_run = pd.read_excel(f'pages/CdA Testing/FullRunSheet.xlsx')
        c1,c2,c3 = st.columns(3)
        with c1:
            album = st.selectbox(
                "Select Album:",
                options=df_images["Album"].sort_values().unique()
                ) 
        df=df_images.loc[df_images["Album"]==album]
        with c2:
            im1 = st.selectbox(
                "Select Image 1:",
                options=df["Image"].unique()
                ) 
        with c3:
            im2 = st.selectbox(
                "Select Image 2:",
                options=df["Image"].unique(),
                index=1
                ) 

        df_run_small=df_run.loc[df_run["Album"]==album].drop(columns=["Album"]).reset_index(drop=True)

        c1,c2=st.columns(2)
        with c1:
            if len(df_run_small)>0:
                df_run_small
        with c2:

            if "Front" in album:
                image_comparison(
                    img1=im1,
                    img2=im2,
                    label1="",
                    label2="",
                    width=150,
                    starting_position=50,
                    show_labels=False,
                    make_responsive=True,
                    in_memory=True,
                    )
            else:
                image_comparison(
                    img1=im1,
                    img2=im2,
                    label1="",
                    label2="",
                    width=700,
                    starting_position=50,
                    show_labels=False,
                    make_responsive=True,
                    in_memory=True,
                    )
        st.markdown("---")
    elif show == "Local Image Comparison":
        st.header("Compare local images")
        upimg2=None
        uppimg1=None
        c1,c2=st.columns(2)
        with c1:
            upim1 = st.file_uploader('', type=['png','jpg'], key=1)
            if upim1 is not None:
                upimg1 = Image.open(upim1)
                st.image(upimg1,width=100)
        with c2:
            upim2 = st.file_uploader('', type=['png','jpg'], key=2)

            if upim2 is not None:
                upimg2 = Image.open(upim2)
                st.image(upimg2,width=100)

        c1,c2=st.columns(2)
        if upimg2 is not None and upimg2 is not None:
            with c1:
                image_comparison(
                img1=upimg1,
                img2=upimg2,
                label1="Image 1",
                label2="Image 2",
                width=700,
                starting_position=50,
                show_labels=True,
                make_responsive=True,
                in_memory=True,
                )





        st.markdown("---")
    else:
        st.header("Track Testing Data/Video")


        df_master = pd.read_excel(f'pages/CdA Testing/Track CdA Testing Streamlit.xlsx')
        df_master['Date'] = pd.to_datetime(df_master['Date']).dt.date
        df_master["DateRep"] = df_master["Date"].astype(str)+" - "+df_master["Rep"].astype(str)

        
        


        c1,c2=st.columns(2)
        with c1:
            athlete = st.selectbox(
            "Select Athlete:",
            options=df_master["Name"].unique()
            ) 

        df=df_master.loc[df_master["Name"]==athlete]
        with c2:
            dates = st.multiselect(
            "Select Dates:",
            options=df["Date"].unique(),
                default = df["Date"].unique()[0]
            ) 
        if len(dates)>0:
            df=df.loc[df["Date"].isin(dates)]
        df_filt=df.reset_index(drop=True)
        df_filt
        
        figJP = px.scatter(df_filt, y="CdA - JP", x = "DateRep", error_y="CdA - JP std",title="Pitman CdA by DateRep")
        st.plotly_chart(figJP, use_container_width=True)
        
        figGM = px.line(df_filt, y=["CdA","CdA - JP","CdA - Notio"], x = "DateRep",title="CdA comparison")
        st.plotly_chart(figGM, use_container_width=True)
        figPos = px.scatter(df_filt, y=["CdA","CdA - JP","CdA - Notio"], x = "Position",title="CdA by Position")
        st.plotly_chart(figPos, use_container_width=True)
       
        c1,c2,c3=st.columns(3)
        with c1:
            video = st.selectbox(
            "Show Video? (Filter first to avoid loading 1 million videos)",
            options=["No","Yes"]
            )     


        ##Download buttons
        @st.cache_data
        def convert_to_csv(df_filt):
            return df_filt.to_csv(index=False,sep = ",").encode('utf-32')
        csv = convert_to_csv(df_filt)
        download1 = st.download_button(
            label=f"Download CdA data as CSV",
            data=csv,
            file_name=f'CdA_Data.csv',
            mime='text/csv'
        )
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            df_filt.to_excel(writer, sheet_name='Sheet1', index=False)
            writer.save()
            download2 = st.download_button(
                label=f"Download CdA data as Excel",
                data=buffer,
                file_name=f'CdA_Data.xlsx',
                mime='application/vnd.ms-excel'
            )
        ##Download buttons complete
        st.markdown("---")
        if video == "Yes":

            for i in range(len(df_filt)):
                if len(str(df_filt["Video"][i]))>4:
                    c1,c2 = st.columns(2)
                    with c1:
                        col1,col2,col3 = st.columns(3)
                        with col1:
                            st.write(f'Rider: {df_filt["Name"][i]}')
                            st.write(f'Date (Y-M-D): {str(df_filt["Date"][i]).split(" ")[0]}')
                            st.write(f'Rep: {df_filt["Rep"][i]}')
                            st.write(f'Position: {df_filt["Position"][i]}')
                        with col2:
                            st.write(f'Clothing: {df_filt["Clothing"][i]}')
                            st.write(f'Shoe covers: {df_filt["Shoe cover"][i]}')
                            st.write(f'Shoes: {df_filt["Shoes"][i]}')
                            st.write(f'Helmet: {df_filt["Helmet"][i]}')
                            st.write(f'Bike: {df_filt["Bike"][i]}')
                            st.write(f'Wheels: {df_filt["Wheels"][i]}')
                            st.write(f'Cranks: {df_filt["Cranks"][i]}')
                            st.write(f'System weight: {df_filt["System weight (kg)"][i]}')
                            st.write(f'Clothing: {df_filt["Clothing"][i]}')
                            st.write(f'Tyre pressure: {df_filt["Tyre pressure"][i]}')
                            st.write(f'Gear: {df_filt["Gear"][i]}')
                        with col3:
                            st.write(f'Notio CdA: {df_filt["CdA - Notio"][i]}')
                            st.write(f'Goldmine CdA: {df_filt["CdA"][i]}')
                            st.write(f'Pitman CdA: {df_filt["CdA - JP"][i]}')
                            st.write(f'Pitman CdA std: {df_filt["CdA - JP std"][i]}')
                            st.write(f'Speed: {df_filt["Speed"][i]}')
                            st.write(f'Power: {df_filt["Power"][i]}')
                            st.write(f'Distance: {df_filt["Distance (m)"][i]} m')
                            st.write(f'Temperature: {df_filt["Temp"][i]} C')
                            st.write(f'Air Pressure: {df_filt["Air pressure"][i]} hP')
                            st.write(f'Humidity: {df_filt["Humidity"][i]}%')
                            st.write(f'Air Density: {df_filt["Air density"][i]} kg/m^3')

                    


                    with c2:
                        video_name = df_filt["Video"][i]

                        st.video(f"{video_name}")
                    st.markdown('---')


    
