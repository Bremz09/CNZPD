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
    st.header("All Data")
    df_master = pd.read_excel(f'pages/ParaFactorTool/Para_results.xlsx')
    
    df_master
    
        # buffer to use for excel writer
    buffer = io.BytesIO()
    @st.cache_data
    def convert_to_csv(df_master):
        # IMPORTANT: Cache the conversion to prevent computation on every rerun
        return df_master.to_csv(index=False).encode('utf-8')
    csv = convert_to_csv(df_master)
    # download button 1 to download dataframe as csv
    download1 = st.download_button(
        label="Download All Data as CSV",
        data=csv,
        file_name='All_Para_Factor_Data.csv',
        mime='text/csv'
    )

    # download button 2 to download dataframe as xlsx
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        # Write each dataframe to a different worksheet.
        df_master.to_excel(writer, sheet_name='Sheet1', index=False)
        # Close the Pandas Excel writer and output the Excel file to the buffer
        writer.save()

        download2 = st.download_button(
            label="Download All Data as Excel",
            data=buffer,
            file_name='All_Para_Factor_Data.xlsx',
            mime='application/vnd.ms-excel'
        )  
    
    


    c1,c2,c3 = st.columns(3)
    with c1:

        cats = df_master["Category"].sort_values().unique()
        category = st.selectbox("Select Category:", options = cats, 
                                    
                                    key="categories")

        df_filt = df_master.query(
            "Category == @category"
        )
    with c2:

        sexs = df_filt["Sex"].unique()
        sex = st.selectbox("Select Sex:", options = sexs, 
                                    
                                    key="sexs")

        df_filt = df_filt.query(
            "Sex == @sex"
        )
    if len(df_filt["Stage"].unique()) > 1:
        with c3:

            stages = ["All","Q","F"]
            stage = st.selectbox("Select Stage:", options = stages, 

                                        key="stages")
            if stage == "All":
                df_filt=df_filt.sort_values("Time")
                df_filt=df_filt.drop_duplicates(subset=["Athlete"])
            else:
                df_filt = df_filt.query(
                    "Stage == @stage"
                )
        
    df_filt=df_filt.sort_values("Factored")
    df_filt.insert(11, 'FactoredRank', range(1, 1 + len(df_filt)))
    df_filt
    

        
        
        
        
        
        
        
        

    

    ###Fix this!!!!!!1
    
#     # buffer to use for excel writer
#     buffer = io.BytesIO()
#     @st.cache_data
#     def convert_to_csv(df_filt):
#         # IMPORTANT: Cache the conversion to prevent computation on every rerun
#         return df_filt.to_csv(index=False).encode('utf-8')
#     csv = convert_to_csv(df_filt)
#     # download button 1 to download dataframe as csv
#     download1 = st.download_button(
#         label="Download Filtered Data as CSV",
#         data=csv,
#         file_name='Filtered_Gear_Data.csv',
#         mime='text/csv'
#     )

#     # download button 2 to download dataframe as xlsx
#     with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
#         # Write each dataframe to a different worksheet.
#         df_filt.to_excel(writer, sheet_name='Sheet1', index=False)
#         # Close the Pandas Excel writer and output the Excel file to the buffer
#         writer.save()

#         download2 = st.download_button(
#             label="Download Filtered Data as Excel",
#             data=buffer,
#             file_name='Filtered_Gear_Data.xlsx',
#             mime='application/vnd.ms-excel'
#         )  

    
    
    



