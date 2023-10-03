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
    df_master = pd.read_excel(f'pages/Gear_Calculator/Gear_Calculator_Master.xlsx')
    df_master["Competition Date"]=pd.to_datetime(df_master["Competition Date"]).dt.date
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
        label="Download All Gear Data as CSV",
        data=csv,
        file_name='All_Gear_Data.csv',
        mime='text/csv'
    )

    # download button 2 to download dataframe as xlsx
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        # Write each dataframe to a different worksheet.
        df_master.to_excel(writer, sheet_name='Sheet1', index=False)
        # Close the Pandas Excel writer and output the Excel file to the buffer
        writer.save()

        download2 = st.download_button(
            label="Download All Gear Data as Excel",
            data=buffer,
            file_name='All_Gear_Data.xlsx',
            mime='application/vnd.ms-excel'
        )  
    
    
    
    ###Filtering Bit -- REALLY GOOD!!
    st.header("Filtered Data")
    import pandas as pd
    import streamlit as st
    import streamlit.components.v1 as components
    from pandas.api.types import (
    is_categorical_dtype,
    is_datetime64_any_dtype,
    is_numeric_dtype,
    is_object_dtype,
    )


    def filter_dataframe(df: pd.DataFrame) -> pd.DataFrame:

        modify = st.checkbox("Add filters")

        if not modify:
            return df

        df = df.copy()

        # Try to convert datetimes into a standard format (datetime, no timezone)
        for col in df.columns:
            if is_object_dtype(df[col]):
                try:
                    df[col] = pd.to_datetime(df[col])
                except Exception:
                    pass

            if is_datetime64_any_dtype(df[col]):
                df[col] = df[col].dt.tz_localize(None)

        modification_container = st.container()

        with modification_container:
            to_filter_columns = st.multiselect("Filter dataframe on", df.columns)
            for column in to_filter_columns:
                left, right = st.columns((1, 20))
                # Treat columns with < 10 unique values as categorical
                if is_categorical_dtype(df[column]) or df[column].nunique() < 10:
                    user_cat_input = right.multiselect(
                        f"Values for {column}",
                        df[column].unique(),
                        default=list(df[column].unique()),
                    )
                    df = df[df[column].isin(user_cat_input)]
                elif is_numeric_dtype(df[column]):
                    _min = float(df[column].min())
                    _max = float(df[column].max())
                    step = (_max - _min) / 100
                    user_num_input = right.slider(
                        f"Values for {column}",
                        min_value=_min,
                        max_value=_max,
                        value=(_min, _max),
                        step=step,
                    )
                    df = df[df[column].between(*user_num_input)]
                elif is_datetime64_any_dtype(df[column]):
                    user_date_input = right.date_input(
                        f"Values for {column}",
                        value=(
                            df[column].min(),
                            df[column].max(),
                        ),
                    )
                    if len(user_date_input) == 2:
                        user_date_input = tuple(map(pd.to_datetime, user_date_input))
                        start_date, end_date = user_date_input
                        df = df.loc[df[column].between(start_date, end_date)]
                else:
                    user_text_input = right.text_input(
                        f"Substring or regex in {column}",
                    )
                    if user_text_input:
                        df = df[df[column].astype(str).str.contains(user_text_input)]

        return df


        
        
        
        
        
        
        
        

    

    df = df_master
    df_filt = filter_dataframe(df)
    df_filt
    
    
    # buffer to use for excel writer
    buffer = io.BytesIO()
    @st.cache_data
    def convert_to_csv(df_filt):
        # IMPORTANT: Cache the conversion to prevent computation on every rerun
        return df_filt.to_csv(index=False).encode('utf-8')
    csv = convert_to_csv(df_filt)
    # download button 1 to download dataframe as csv
    download1 = st.download_button(
        label="Download Filtered Data as CSV",
        data=csv,
        file_name='Filtered_Gear_Data.csv',
        mime='text/csv'
    )

    # download button 2 to download dataframe as xlsx
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        # Write each dataframe to a different worksheet.
        df_filt.to_excel(writer, sheet_name='Sheet1', index=False)
        # Close the Pandas Excel writer and output the Excel file to the buffer
        writer.save()

        download2 = st.download_button(
            label="Download Filtered Data as Excel",
            data=buffer,
            file_name='Filtered_Gear_Data.xlsx',
            mime='application/vnd.ms-excel'
        )  

    
    
    
    
#     c1,c2=st.columns(2)
#     with c1:
#         event_sel = st.multiselect(
#         "Select past effort(s):",
#         options=df_master["Event"].sort_values(ascending=False).unique()
#         ) 
#     with c2:
#         sex_sel = st.multiselect(
#         "Select past effort(s):",
#         options=["M","F"]
#     ) 
#     if len(event_sel)>0:
#         df_sel = df_master.loc[df_master['Event'].isin(event_sel)]
#         df_sel

    st.header("Gear Calculator")
    st.write("Use the Gear Finder window on Hudl")
    
    uploaded_file = st.file_uploader("Choose a file",key="uploader")

    if uploaded_file is not None:
        st.markdown("---")

        st.header("Editor")
        st.write("Full CSV")
        df_full = pd.read_csv(uploaded_file)
        df_full=df_full.sort_values(by=["Start time"]).reset_index(drop=True)
        
        df_full
        c1,c2,c3=st.columns(3)
        with c1:
            start=st.number_input("Start Row (inclusive)", value=0)
        with c2:
            end=st.number_input("End Row (inclusive)", value=start+17)+1


        df=df_full[start:end]
        df=df.sort_values("Start time", ascending=True)
        st.write("Cropped df - Just include all the relevant info and it'll do the rest")
        
        col_one, col_two = st.columns((5,4))
        with col_one:
            df
        with col_two:
            event = st.selectbox("Event:", options=["Sprint Qual","Match Sprint","Keirin","Team Pursuit","Madison","Bunch","Individual Pursuit"])
            position="Null"
            if event == "Team Pursuit":
                position = st.selectbox("Position:", options=[1,2,3,4],key="position")
            name = st.text_input("Rider Name:",df["Row"].iloc[0])
            nation = st.text_input("Nation (eg NZL):")
            sex = st.selectbox("Sex:", options=["M","F"],key="Sex")
            comp = st.text_input("Competition:")
            Round = st.selectbox("Round:", options=["Q","R1","R2","R3","Rep","F","A Final","B Final"],key="Round")
            comp_date = st.date_input("Competition Date:")
            ##I'm using 2.111 instead of wheel circumference. Seems to work better.
            #wheel_circ = st.number_input("Wheel Circumference:",value=2.096,step=1e-3, format="%.3f")
        
        
        #This is to find the revs per second
        rev_start = df.loc[df["Row"]== "Rev Start"]["Start time"].item()
        rev_end = df.loc[df["Row"]== "Rev End"]["Start time"].item()
        rev_count = df['Row'].value_counts()['Full Rev'] +1
        
        rps = rev_count/(rev_end-rev_start)
        
        #This is to find Speed
        pl_start=df.loc[df["Row"]== "Pursuit Line Start"]["Start time"].item()
        pl_end=df.loc[df["Row"]== "Pursuit Line End"]["Start time"].item()
        distance = 125
        if (df['Row'].eq('Red Line')).any():
            distance = 127.199
        mps = distance/(pl_end-pl_start)
        
        mpr = mps/rps
        m_developed = mpr*1.030819675 - 0.128785356
        gear = round(27*m_developed/2.111,2)
        st.subheader(f"Calculated gear is {gear}")
        #Small cog 10 to 25, Chain ring 42 to 80
        
        round_to=[113.40,103.09,94.50,87.23,81.00,75.60,70.88,66.71,63.00,59.68,56.70,54.00,51.55,49.30,47.25,45.36,116.10,105.55,96.75,89.31,82.93,77.40,72.56,68.29,64.50,61.11,58.05,55.29,52.77,50.48,48.38,46.44,118.80,108.00,99.00,91.38,84.86,79.20,74.25,69.88,66.00,62.53,59.40,56.57,51.65,49.50,47.52,121.50,110.45,101.25,93.46,86.79,75.94,71.47,67.50,63.95,60.75,57.86,55.23,52.83,50.63,48.60,124.20,112.91,103.50,95.54,88.71,82.80,77.63,73.06,69.00,65.37,62.10,59.14,56.45,51.75,49.68,126.90,115.36,105.75,97.62,90.64,84.60,79.31,74.65,70.50,66.79,63.45,60.43,57.68,55.17,52.88,50.76,129.60,117.82,99.69,92.57,86.40,76.24,72.00,68.21,64.80,61.71,58.91,56.35,51.84,132.30,120.27,110.25,101.77,88.20,82.69,77.82,73.50,69.63,66.15,60.14,57.52,55.13,52.92,135.00,122.73,112.50,103.85,96.43,90.00,84.38,79.41,75.00,71.05,64.29,61.36,58.70,56.25,137.70,125.18,114.75,105.92,98.36,91.80,86.06,76.50,72.47,68.85,65.57,62.59,59.87,57.38,55.08,140.40,127.64,117.00,100.29,93.60,87.75,82.59,78.00,73.89,70.20,66.86,63.82,61.04,58.50,56.16,143.10,130.09,119.25,110.08,102.21,95.40,89.44,84.18,79.50,75.32,71.55,68.14,65.05,62.22,59.63,57.24,145.80,132.55,112.15,104.14,97.20,91.13,85.76,76.74,72.90,69.43,66.27,63.39,58.32,148.50,123.75,114.23,106.07,92.81,87.35,82.50,78.16,70.71,64.57,61.88,151.20,137.45,126.00,116.31,100.80,88.94,84.00,79.58,68.73,65.74,60.48,153.90,139.91,128.25,118.38,109.93,102.60,96.19,90.53,85.50,76.95,73.29,69.95,66.91,64.13,61.56,156.60,142.36,130.50,120.46,111.86,104.40,97.88,92.12,87.00,82.42,78.30,74.57,71.18,68.09,65.25,62.64,159.30,144.82,132.75,122.54,113.79,106.20,99.56,93.71,88.50,83.84,79.65,75.86,72.41,69.26,66.38,63.72,162.00,147.27,124.62,115.71,95.29,85.26,77.14,73.64,70.43,164.70,149.73,137.25,126.69,117.64,109.80,102.94,96.88,91.50,86.68,82.35,78.43,74.86,71.61,68.63,65.88,167.40,152.18,139.50,128.77,119.57,111.60,104.63,98.47,93.00,88.11,83.70,79.71,76.09,72.78,69.75,66.96,170.10,154.64,141.75,130.85,106.31,100.06,89.53,85.05,77.32,73.96,68.04,172.80,157.09,144.00,132.92,123.43,115.20,101.65,96.00,90.95,82.29,78.55,75.13,69.12,175.50,159.55,146.25,125.36,109.69,103.24,97.50,92.37,83.57,79.77,76.30,73.13,178.20,137.08,127.29,111.38,104.82,93.79,89.10,77.48,71.28,180.90,164.45,150.75,139.15,129.21,120.60,113.06,106.41,100.50,95.21,90.45,86.14,82.23,78.65,75.38,72.36,183.60,166.91,153.00,141.23,131.14,122.40,102.00,96.63,87.43,83.45,79.83,73.44,186.30,169.36,155.25,143.31,133.07,116.44,109.59,98.05,93.15,84.68,74.52,189.00,171.82,157.50,145.38,118.13,111.18,105.00,99.47,85.91,82.17,78.75,191.70,174.27,159.75,147.46,136.93,127.80,119.81,112.76,106.50,100.89,95.85,91.29,87.14,83.35,79.88,76.68,194.40,176.73,149.54,138.86,114.35,102.32,88.36,84.52,77.76,197.10,179.18,164.25,151.62,140.79,131.40,123.19,115.94,109.50,103.74,98.55,93.86,89.59,85.70,82.13,78.84,199.80,181.64,166.50,153.69,142.71,133.20,124.88,117.53,111.00,105.16,99.90,95.14,90.82,86.87,83.25,79.92,202.50,184.09,168.75,155.77,144.64,126.56,119.12,106.58,92.05,88.04,205.20,186.55,171.00,157.85,146.57,136.80,120.71,114.00,97.71,93.27,89.22,82.08,207.90,173.25,159.92,138.60,129.94,122.29,115.50,109.42,103.95,90.39,86.63,83.16,210.60,191.45,150.43,131.63,123.88,110.84,105.30,95.73,91.57,84.24,213.30,193.91,177.75,164.08,152.36,142.20,133.31,125.47,118.50,112.26,106.65,101.57,96.95,92.74,88.88,85.32,216.00,196.36,180.00,166.15,154.29,127.06,120.00,113.68,102.86,98.18,93.91]
        
        
 
        nearest_gear = min(round_to, key=lambda x: abs(x - gear))
        st.subheader(f"Nearest possible gear is {nearest_gear}")
        data = [[name,nation,sex,event,position,comp,Round,comp_date,gear,nearest_gear]]
        df = pd.DataFrame(data, columns=['Name', 'Nation','Sex','Event','Position','Competition','Round','Competition Date','Calculated Gear','Nearest Possible Gear'])
        df
        
        


        
            
        #master_path=st.text_input("Add path to master file:",key="prompt")
        if st.button("Append info to master",key="upload"):




            df_save=df
            #df_save.insert(0, 'Save_Date', datetime.date.today())
            #df_save["Save_Date"] = pd.to_datetime(df_save['Save_Date'])
            
            df = pd.concat([df_master, df_save], axis=0)
            df

            ##Testing downloader


            # buffer to use for excel writer
            buffer = io.BytesIO()



            @st.cache_data
            def convert_to_csv(df):
                # IMPORTANT: Cache the conversion to prevent computation on every rerun
                return df.to_csv(index=False).encode('utf-8')

            csv = convert_to_csv(df)

            # display the dataframe on streamlit app
    #         st.write(df)

            # download button 1 to download dataframe as csv
            download1 = st.download_button(
                label="Download new Master as CSV",
                data=csv,
                file_name='Gear_Calculator_Master.csv',
                mime='text/csv'
            )

            # download button 2 to download dataframe as xlsx
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                # Write each dataframe to a different worksheet.
                df.to_excel(writer, sheet_name='Sheet1', index=False)
                # Close the Pandas Excel writer and output the Excel file to the buffer
                writer.save()

                download2 = st.download_button(
                    label="Download new Master as Excel",
                    data=buffer,
                    file_name='Gear_Calculator_Master.xlsx',
                    mime='application/vnd.ms-excel'
                )  


