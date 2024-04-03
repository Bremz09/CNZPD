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
                options=df_images["Album"].sort_values(ascending=False).unique()
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
        df_master=df_master.sort_values(['Date','Name', 'Rep'], ascending=[True, True, True])
        c1,c2=st.columns(2)
        with c1:
            athlete = st.selectbox(
            "Select Athlete:",
            options=df_master["Name"].sort_values().unique()
            ) 

        df=df_master.loc[df_master["Name"]==athlete]
        with c2:
            dates = st.multiselect(
            "Select Dates:",
            options=df["Date"].sort_values(ascending=False).unique(),
                default = df["Date"].sort_values(ascending=False).unique()[0]
            ) 
        if len(dates)>0:
            df=df.loc[df["Date"].isin(dates)]
        df_filt=df.reset_index(drop=True)
        df_filt
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
            writer.close()
            download2 = st.download_button(
                label=f"Download CdA data as Excel",
                data=buffer,
                file_name=f'CdA_Data.xlsx',
                mime='application/vnd.ms-excel'
            )
        ##Download buttons complete
        
        figJP = px.scatter(df_filt, y="CdA - JP - PF corrected", x = "DateRep", error_y="CdA - JP std",title="Pitman CdA by DateRep")
        st.plotly_chart(figJP, use_container_width=True)

        figGM = px.line(df_filt, y=["CdA - GM","CdA - JP - PF corrected","CdA - Notio"], x = "DateRep",title="CdA comparison")
        st.plotly_chart(figGM, use_container_width=True)
        c1,c2,c3=st.columns(3)
        with c1:
            comp_by = st.selectbox(
            "Compare by:",
            options=["Position", "Clothing", "Helmet", "Shoe cover"]
            ) 



        df_test=df_filt.groupby([f'{comp_by}']).mean(numeric_only=True).reset_index()
        df_test['Average_CdA'] = df_test[["CdA - GM","CdA - JP - PF corrected","CdA - Notio"]].mean(axis=1)
        

        if len(df_test)>1:
            df_test["Delta"] = df_test['Average_CdA']-df_test["Average_CdA"][0]
            figPos = px.bar(df_test, y=df_test["Delta"], x = df_test[f"{comp_by}"],title=f"Average CdA shifts by {comp_by}")
            st.plotly_chart(figPos, use_container_width=True)   
        else:
            st.header("Nothing to compare - try something else")
        st.markdown("---")
        st.markdown("<h1 style='text-align: center; color: white;'>Session Breakdowns</h1>", unsafe_allow_html=True)
        dates=sorted(dates)
        for ind,date in enumerate(dates):
            
            df_date = df_filt.loc[df_filt["Date"]==date].reset_index(drop=True)
            df_date["filt"]=""         
            st.subheader(f'Session {ind+1} on {date}')
            for i in range(len(df_date)):
                Position = str(df_date["Position"][i])
                Clothing = str(df_date["Clothing"][i])
                Helmet = str(df_date["Helmet"][i])
                Shoe_cover = str(df_date["Shoe cover"][i])
                if Helmet=="nan":
                    Helmet="not specified"
                if Position=="nan":
                    Position="not specified"
                if Shoe_cover=="nan":
                    Shoe_cover="not specified"
                if Clothing=="nan":
                    Clothing="not specified"
                df_date["filt"][i]=f'{Position}, {Clothing}, {Helmet}, {Shoe_cover}'
                
            
            df_date_mean = df_date.groupby('filt', sort=False).agg({"Position":"first","Clothing":"first","Helmet":"first","Shoe cover":"first","CdA - JP - PF corrected": "mean","CdA - GM": "mean"}).reset_index()
            df_date_min = df_date.groupby('filt', sort=False).agg({"Position":"first","Clothing":"first","Helmet":"first","Shoe cover":"first","CdA - JP - PF corrected": "min","CdA - GM": "min"}).reset_index()
            df_date_max = df_date.groupby('filt', sort=False).agg({"Position":"first","Clothing":"first","Helmet":"first","Shoe cover":"first","CdA - JP - PF corrected": "max","CdA - GM": "max"}).reset_index()
            
#             df_date.insert(1, "Configuration", "Baseline", True)
            df_date_mean['CdA Average'] = df_date_mean[["CdA - JP - PF corrected","CdA - GM"]].mean(axis=1)
            df_date_mean["CdA - JP Min"] = df_date_min["CdA - JP - PF corrected"]
            df_date_mean["CdA - JP Max"] = df_date_max["CdA - JP - PF corrected"]
            df_date_mean["CdA - GM Min"] = df_date_min["CdA - GM"]
            df_date_mean["CdA - GM Max"] = df_date_max["CdA - GM"]
            
            df_date_mean=df_date_mean.drop(['filt'], axis=1)
            c1,c2 = st.columns(2)
            with c1:
                df_date_mean
                
                configuration=["Baseline"]
                for i in range(len(df_date_mean)):

                    Position = str(df_date_mean["Position"][i])
                    Clothing = str(df_date_mean["Clothing"][i])
                    Helmet = str(df_date_mean["Helmet"][i])
                    Shoe_cover = str(df_date_mean["Shoe cover"][i])
                    if Helmet=="nan":
                        Helmet="not specified"
                    if Position=="nan":
                        Position="not specified"
                    if Shoe_cover=="nan":
                        Shoe_cover="not specified"
                    if Clothing=="nan":
                        Clothing="not specified"
                    if i == 0:
                        st.write(f'Baseline runs used position "{Position}". The skinsuit was {Clothing}, the helmet was {Helmet}, the shoe covers were {Shoe_cover}. The average JP CdA was {round(df_date_mean["CdA - JP - PF corrected"][i],4)}')
                        baseline = round(df_date_mean["CdA - JP - PF corrected"][i],4)
                    else:
                        st.write(f'Configuration {i} used position "{Position}". The skinsuit was {Clothing}, the helmet was {Helmet}, the shoe covers were {Shoe_cover}. The average JP CdA was {round(df_date_mean["CdA - JP - PF corrected"][i],4)}, a shift from baseline of {round(df_date_mean["CdA - JP - PF corrected"][i]-baseline,4)}')
                        configuration.append(f'Config {i}')
                 
            with c2:  
                if len(df_date_mean["CdA - JP - PF corrected"].value_counts()) > 0:
                    figPos = px.bar(df_date_mean, y=df_date_mean["CdA - JP - PF corrected"], x = configuration,title=f"Average JP CdA by config - Error bars show complete range of config values").update_traces(
                        error_y={
                #"type":'data',
                "symmetric":False,
                "array":df_date_mean["CdA - JP Max"]-df_date_mean["CdA - JP - PF corrected"],
                "arrayminus":df_date_mean["CdA - JP - PF corrected"]-df_date_mean["CdA - JP Min"]}
            )
                    figPos.update_yaxes(range = [min(df_date_mean["CdA - JP Min"])-0.001,max(df_date_mean["CdA - JP Max"])])
                    figPos.update_layout(xaxis_title="Configuration")
                    st.plotly_chart(figPos, use_container_width=True)
                else:
                    figPos = px.bar(df_date_mean, y=df_date_mean["CdA - GM"], x = configuration,title=f"Average GM CdA by config - Error bars show complete range of config values").update_traces(
                        error_y={
                #"type":'data',
                "symmetric":False,
                "array":df_date_mean["CdA - GM Max"]-df_date_mean["CdA - GM"],
                "arrayminus":df_date_mean["CdA - GM"]-df_date_mean["CdA - GM Min"]}
            )
                    figPos.update_yaxes(range = [min(df_date_mean["CdA - GM Min"])-0.001,max(df_date_mean["CdA - GM Max"])])
                    figPos.update_layout(xaxis_title="Configuration")
                    st.plotly_chart(figPos, use_container_width=True)
            st.markdown("---")
            
            
            
        c1,c2,c3=st.columns(3)
        with c1:
            video = st.selectbox(
            "Show Video? (Filter first to avoid loading 1 million videos)",
            options=["No","Yes"]
            )     



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
                            st.write(f'Goldmine CdA: {df_filt["CdA - GM"][i]}')
                            st.write(f'Pitman CdA: {df_filt["CdA - JP - PF corrected"][i]}')
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


    
