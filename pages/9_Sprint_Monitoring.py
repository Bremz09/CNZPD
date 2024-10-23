#!/usr/bin/env python
# coding: utf-8



import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image
import io
import datetime
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm
from datetime import datetime
import statsmodels.api as sm
import streamlit.components.v1 as components
from pandas.api.types import (
is_categorical_dtype,
is_datetime64_any_dtype,
is_numeric_dtype,
is_object_dtype,
)




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
    data_types=["Gym Monitoring","Track Monitoring"]
    data_type = st.selectbox("Select Data:", data_types, key="Data Selector")
    if data_type=="Gym Monitoring":
        
        @st.cache_data
        def get_gym_data_from_excel():
            df = pd.read_excel(
                io='pages/Sprint Monitoring/TeamBuildr - Track Sprint.xlsx',
                engine ='openpyxl',
                sheet_name='TeamBuildr',
                skiprows=0,
                usecols='A:AU',
                nrows=130000
                )
            #df = df.replace(',','')

#             df["Datetime"]=df["Date"]
#             df["Date"]=df["Date"].dt.strftime("%d/%m/%Y")
            return df
        df_master =get_gym_data_from_excel()
        df_master["Completed Date"] = pd.to_datetime(df_master["Completed Date"]).dt.date
        df_master["Name"]=df_master["First Name"].astype(str)+" "+df_master["Last Name"].astype(str)

        c1,c2,c3,c4=st.columns(4)
        with c1:
            athlete = st.selectbox("Select Athlete:",df_master["Name"].sort_values().unique(),key="Athlete Select")
            df=df_master.loc[df_master["Name"]==athlete]
        with c2:
            exercise = st.selectbox("Select Exercise:",df["Exercise Name"].sort_values().unique(),key="Exercise Select")
            df=df.loc[df["Exercise Name"]==exercise]
        df = df.reset_index()
        df
        df_small = df[['Name', 'Exercise Name','Completed Date','Result 1','Reps 1','Result 2','Reps 2','Result 3','Reps 3','Result 4','Reps 4','Result 5','Reps 5','Result 6','Reps 6','Result 7','Reps 7','Result 8','Reps 8','Result 9','Reps 9','Result 10','Reps 10']].copy()
#         df_small
        height=len(df_small)
        df_tall = df_small[["Name", 'Exercise Name','Completed Date','Result 1','Reps 1']]
        for i in range(2,11):
            df_tall = pd.concat([df_tall, df_small[["Name", 'Exercise Name','Completed Date',f'Result {i}',f'Reps {i}']]], ignore_index=True)
            for j in range((i-1)*height,i*height):
                df_tall["Result 1"][j]=df_tall[f"Result {i}"][j]
                df_tall["Reps 1"][j]=df_tall[f"Reps {i}"][j]
                
        
        

        
        df_tall=df_tall.drop(columns=['Result 2','Reps 2','Result 3','Reps 3','Result 4','Reps 4','Result 5','Reps 5','Result 6','Reps 6','Result 7','Reps 7','Result 8','Reps 8','Result 9','Reps 9','Result 10','Reps 10'])
        df_tall = df_tall.rename(columns={'Result 1': 'Weight', 'Reps 1': 'Reps'})
        df_tall.dropna(subset=['Reps'], inplace=True)
        df_tall.index.name = 'Index'
        df_tall=df_tall.sort_values(by=["Completed Date","Index"])
#         df_tall
        
        fig_exercise_hist = px.line(df_tall, x="Completed Date", y = "Weight", title = "Weight by Date", markers = "True",  color="Reps")
        st.plotly_chart(fig_exercise_hist,use_container_width=True)
        
        
