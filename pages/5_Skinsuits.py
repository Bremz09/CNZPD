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
import math


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

    st.header("Skinsuit Measurements")


    df_master = pd.read_excel(f'pages/Skinsuit/Measurements.xlsx')
    df_master
    c1,c2=st.columns(2)
    
    options=df_master["Squad"].sort_values().unique().tolist()
    
    options.extend(["Endurance","Sprint","All"])
    with c1:
        squad = st.selectbox(
        "Select Squad:",
        options=options
        ) 
    if squad=="All":
        df=df_master
    elif squad=="Endurance":
        df=df_master.loc[(df_master["Squad"]=="ME") | (df_master["Squad"]=="WE")].reset_index(drop=True)
    elif squad=="Sprint":
        df=df_master.loc[(df_master["Squad"]=="MSP") | (df_master["Squad"]=="WSP")].reset_index(drop=True)
    else:
        df=df_master.loc[df_master["Squad"]==squad].reset_index(drop=True)
    with c2:
        measurement = st.selectbox(
        "Select Measurement:",
        options=df.columns[2:-1]
        ) 
    fig = px.bar(df, y=f"{measurement}", x = "Athlete", title="Measurements")
    fig.add_hline(y=df[f"{measurement}"].mean(), line_dash="dash",line_color="yellow",annotation_text=f"Mean = {round(df[f'{measurement}'].mean(),2)}")
    
    st.plotly_chart(fig, use_container_width=True)
    df.loc[f"{len(df)}"]="Mean"  
    
    df['Squad'].replace('Mean', squad, inplace=True)
    df['Image'].replace('Mean', None, inplace=True)
    
    
    df_pct = df[["Athlete","Squad"]]
    df_rank = df[["Athlete","Squad"]][:-1]
    for i in range(2,len(df.columns)-1):
        x=df[f"{df.columns[i]}"][:-1].mean()
        df[f'{df.columns[i]}'].replace('Mean', x, inplace=True)
        df_pct[f'{df.columns[i]}']=abs(1-df[f'{df.columns[i]}']/df[f'{df.columns[i]}'].iloc[len(df[f'{df.columns[i]}'])-1])*100
        df_rank[f'{df.columns[i]}']=df[f'{df.columns[i]}'][:-1].rank()
    
    
    df

    ##Download buttons
    @st.cache_data
    def convert_to_csv(df):
        return df.to_csv(index=False,sep = ",").encode('utf-32')
    csv = convert_to_csv(df)
    download1 = st.download_button(
        label=f"Download Skinsuit data as CSV",
        data=csv,
        file_name=f'Skinsuit_Data.csv',
        mime='text/csv'
    )
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Sheet1', index=False)
        writer.close()
        download2 = st.download_button(
            label=f"Download Skinsuit data as Excel",
            data=buffer,
            file_name=f'Skinsuit_Data.xlsx',
            mime='application/vnd.ms-excel'
        )
    ##Download buttons complete

    
    df_pct['Mean deviation'] = df_pct.iloc[:, 2:].mean(axis=1)
    st.subheader("Absolute deviation from average as a percentage")
    df_pct[:-1]
    st.subheader("Rankings")
    df_rank['Mean rank'] = df_rank.iloc[:, 2:].mean(axis=1)
    df_rank
    
    
    c1,c2=st.columns(2)
    with c1:
        st.subheader("Order of averageness")
        df_av=df_pct.sort_values('Mean deviation', ascending=True).iloc[1:].reset_index()
        df_av[["Athlete","Mean deviation"]]
    with c2:
        st.subheader("Average ranks")
        
        df_av_rank=df_rank
        df_av_rank["Mean rank deviation"]=abs(((len(df_av_rank)/2) + 0.5)-df_av_rank["Mean rank"])
        df_av_rank=df_av_rank.sort_values('Mean rank deviation', ascending=True).iloc[0:].reset_index()
        df_av_rank[["Athlete","Mean rank","Mean rank deviation"]]
    st.markdown("---")
    st.header("Compare Images")


    with st.form("my_form"):
        c1,c2 = st.columns(2)
        with c1:
            ath1 = st.selectbox(
                "Athlete 1:",
                options=df["Athlete"].loc[df["Image"].notnull()]
                ) 
        
        with c2:
            ath2 = st.selectbox(
                "Athlete 2:",
                options=df["Athlete"].loc[(df["Image"].notnull())]
                ) 
        submitted = st.form_submit_button("Compare")


        
    im1 = df["Image"].loc[df["Athlete"]==ath1].tolist()[0]
    im2 = df["Image"].loc[df["Athlete"]==ath2].tolist()[0]
    @st.cache_resource
    def img_comp(im1,im2):
        image_comparison(
            img1=im1,
            img2=im2,
            label1=ath1,
            label2=ath2,
            width=1000,
            starting_position=50,
            show_labels=True,
            make_responsive=True,
            in_memory=True,
            )
    
    img_comp(im1,im2)
    st.markdown("---")




