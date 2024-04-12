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
from st_aggrid import AgGrid, GridUpdateMode
from st_aggrid.grid_options_builder import GridOptionsBuilder




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
    race_types=["Men's Sprint Qualifying","Women's Sprint Qualifying","Men's Team Sprint","Women's Team Sprint","Men's Team Pursuit","Women's Team Pursuit","Men's Individual Pursuit"]
    race_type = st.selectbox("Select Event:", race_types, key="Event Selector")
    if race_type=="Men's Sprint Qualifying":
        



        c1,c2=st.columns([1,3])
        with c1:
            @st.cache_data
            def get_data_from_excel():
                df = pd.read_excel(
                    io='pages/WR_progressions/Men_F200.xlsx',
                    engine ='openpyxl',
                    sheet_name='Sheet1',
                    skiprows=0,
                    usecols='A:D',
                    nrows=30
                    )
                #df = df.replace(',','')
                
                df["Datetime"]=df["Date"]
                df["Date"]=df["Date"].dt.strftime("%d/%m/%Y")
                return df
            df= get_data_from_excel()
            df_master=df
            df_show = df.drop(columns=["Seconds","DateSerial","Datetime"])
            df_show
            
            
            ##Download buttons
            def convert_to_csv(df_show):
                return df.to_csv(index=False,sep = ",").encode('utf-32')
            csv = convert_to_csv(df_show)
            download1 = st.download_button(
                label="Download Men F200 WR data as CSV",
                data=csv,
                file_name='Men_F200_Data.csv',
                mime='text/csv',
                key="buffertt1"
            )
            buffer_tt = io.BytesIO()
            with pd.ExcelWriter(buffer_tt, engine='xlsxwriter') as writer:
                df_show.to_excel(writer, sheet_name='Sheet1', index=False)
                writer.close()
                download2 = st.download_button(
                    label="Download Men F200 WR data as Excel",
                    data=buffer_tt,
                    file_name='Men_F200_Data.xlsx',
                    mime='application/vnd.ms-excel',
                    key="buffertt2"
                )
            ##Download buttons complete


        with c2:
            date_range = st.slider(
    "Restrict date range?",
            value = (datetime.strptime(df_master["Date"][0], '%d/%m/%Y'),datetime.strptime(df_master["Date"][len(df_master)-1], '%d/%m/%Y')),
                min_value = datetime.strptime(df_master["Date"][0], '%d/%m/%Y'),
                max_value = datetime.strptime(df_master["Date"][len(df_master)-1], '%d/%m/%Y'),
            format="DD/MM/YY")
            
            time_range = st.slider(
    "Restrict time range?",
            value = (df_master["Time"][len(df_master)-1],df_master["Time"][0]),
                max_value = df_master["Time"][0],
                min_value = df_master["Time"][len(df_master)-1])

            df_mask = df.mask(df["Datetime"] < date_range[0])
            df_mask = df_mask.mask(df_mask["Datetime"] > date_range[1])
            df_mask = df_mask.mask(df_mask["Time"] < time_range[0])
            df_mask = df_mask.mask(df_mask["Time"] > time_range[1])
            fig = px.scatter(df_mask, x="DateSerial", y = "Time", title="World Record Progression",labels={"value":"Splits (seconds)"},trendline='ols',trendline_color_override="red")
            customdata = np.stack((df_mask['Seconds'], df_mask['Date']), axis=-1)
            hovertemplate = ('Time: %{customdata[0]}<br>' + 
        'Date: %{customdata[1]}<br>' 
        '<extra></extra>')
            fig.update_traces(customdata=customdata, hovertemplate=hovertemplate)
            st.plotly_chart(fig, use_container_width=True)
            a=px.get_trendline_results(fig).px_fit_results.iloc[0].rsquared
            const = px.get_trendline_results(fig).px_fit_results.iloc[0].params[0]
            x1=px.get_trendline_results(fig).px_fit_results.iloc[0].params[1]
            st.write(f"Time = {round(x1,6)}(DateSerial) + {round(const,3)}")
            st.write(f"R-squared = {round(a,3)}")
            col1,col2=st.columns(2)
            with col1:
                date = st.date_input("Select date for WR prediction:", datetime(2024, 8, 15),format="DD/MM/YYYY")
                date_formatted=date.strftime('%d/%m/%Y')
                
            with col2:
                serial = date - datetime(1899, 12, 30).date()
    
                st.write(f"If a world record was achieved on {date_formatted}, this trend predicts it would be a time of {round(x1*serial.days +const,3)} seconds.")































    if race_type=="Women's Sprint Qualifying":
        
        c1,c2=st.columns([1,3])
        with c1:
            @st.cache_data
            def get_data_from_excel():
                df = pd.read_excel(
                    io='pages/WR_progressions/Women_F200.xlsx',
                    engine ='openpyxl',
                    sheet_name='Sheet1',
                    skiprows=0,
                    usecols='A:D',
                    nrows=30
                    )
                #df = df.replace(',','')
                
                df["Datetime"]=df["Date"]
                df["Date"]=df["Date"].dt.strftime("%d/%m/%Y")
                return df
            df= get_data_from_excel()
            df_master=df
            df_show = df.drop(columns=["Seconds","DateSerial","Datetime"])
            
            st.dataframe(df_show)
            ##Download buttons
            def convert_to_csv(df_show):
                return df.to_csv(index=False,sep = ",").encode('utf-32')
            csv = convert_to_csv(df_show)
            download1 = st.download_button(
                label="Download Women F200 WR data as CSV",
                data=csv,
                file_name='Women_F200_Data.csv',
                mime='text/csv',
                key="buffertt1"
            )
            buffer_tt = io.BytesIO()
            with pd.ExcelWriter(buffer_tt, engine='xlsxwriter') as writer:
                df_show.to_excel(writer, sheet_name='Sheet1', index=False)
                writer.close()
                download2 = st.download_button(
                    label="Download Women F200 WR data as Excel",
                    data=buffer_tt,
                    file_name='Women_F200_Data.xlsx',
                    mime='application/vnd.ms-excel',
                    key="buffertt2"
                )
            ##Download buttons complete


        with c2:
            date_range = st.slider(
    "Restrict date range?",
            value = (datetime.strptime(df_master["Date"][0], '%d/%m/%Y'),datetime.strptime(df_master["Date"][len(df_master)-1], '%d/%m/%Y')),
                min_value = datetime.strptime(df_master["Date"][0], '%d/%m/%Y'),
                max_value = datetime.strptime(df_master["Date"][len(df_master)-1], '%d/%m/%Y'),
            format="DD/MM/YY")
            
            time_range = st.slider(
    "Restrict time range?",
            value = (df_master["Time"][len(df_master)-1],df_master["Time"][0]),
                max_value = df_master["Time"][0],
                min_value = df_master["Time"][len(df_master)-1])
            
            
            df_mask = df.mask(df["Datetime"] < date_range[0])
            df_mask = df_mask.mask(df_mask["Datetime"] > date_range[1])
            df_mask = df_mask.mask(df_mask["Time"] < time_range[0])
            df_mask = df_mask.mask(df_mask["Time"] > time_range[1])
            fig = px.scatter(df_mask, x="DateSerial", y = "Time", title="World Record Progression",labels={"value":"Splits (seconds)"},trendline="ols",trendline_color_override="red")
            customdata = np.stack((df_mask['Seconds'], df_mask['Date']), axis=-1)
            hovertemplate = ('Time: %{customdata[0]}<br>' + 
        'Date: %{customdata[1]}<br>' 
        '<extra></extra>')
            fig.update_traces(customdata=customdata, hovertemplate=hovertemplate)
            st.plotly_chart(fig, use_container_width=True)
            a=px.get_trendline_results(fig).px_fit_results.iloc[0].rsquared
            const = px.get_trendline_results(fig).px_fit_results.iloc[0].params[0]
            x1=px.get_trendline_results(fig).px_fit_results.iloc[0].params[1]
            st.write(f"Time = {round(x1,6)}(DateSerial) + {round(const,3)}")
            st.write(f"R-squared = {round(a,3)}")
            col1,col2=st.columns(2)
            with col1:
                date = st.date_input("Select date for WR prediction:", datetime(2024, 8, 15),format="DD/MM/YYYY")
                date_formatted=date.strftime('%d/%m/%Y')
                
            with col2:
                serial = date - datetime(1899, 12, 30).date()
    
                st.write(f"If a world record was achieved on {date_formatted}, this trend predicts it would be a time of {round(x1*serial.days +const,3)} seconds.")






























    if race_type=="Men's Team Sprint":
        
        c1,c2=st.columns([1,3])
        with c1:
            @st.cache_data
            def get_data_from_excel():
                df = pd.read_excel(
                    io='pages/WR_progressions/Men_TS.xlsx',
                    engine ='openpyxl',
                    sheet_name='Sheet1',
                    skiprows=0,
                    usecols='A:D',
                    nrows=30
                    )
                #df = df.replace(',','')
                
                df["Datetime"]=df["Date"]
                df["Date"]=df["Date"].dt.strftime("%d/%m/%Y")
                return df
            df= get_data_from_excel()
            df_master=df
            df_show = df.drop(columns=["Seconds","DateSerial","Datetime"])
            
            st.dataframe(df_show)
            ##Download buttons
            def convert_to_csv(df_show):
                return df.to_csv(index=False,sep = ",").encode('utf-32')
            csv = convert_to_csv(df_show)
            download1 = st.download_button(
                label="Download Men TS WR data as CSV",
                data=csv,
                file_name='Men_TS_Data.csv',
                mime='text/csv',
                key="buffertt1"
            )
            buffer_tt = io.BytesIO()
            with pd.ExcelWriter(buffer_tt, engine='xlsxwriter') as writer:
                df_show.to_excel(writer, sheet_name='Sheet1', index=False)
                writer.close()
                download2 = st.download_button(
                    label="Download Men TS WR data as Excel",
                    data=buffer_tt,
                    file_name='Men_TS_Data.xlsx',
                    mime='application/vnd.ms-excel',
                    key="buffertt2"
                )
            ##Download buttons complete


        with c2:
            date_range = st.slider(
    "Restrict date range?",
            value = (datetime.strptime(df_master["Date"][0], '%d/%m/%Y'),datetime.strptime(df_master["Date"][len(df_master)-1], '%d/%m/%Y')),
                min_value = datetime.strptime(df_master["Date"][0], '%d/%m/%Y'),
                max_value = datetime.strptime(df_master["Date"][len(df_master)-1], '%d/%m/%Y'),
            format="DD/MM/YY")
            
            time_range = st.slider(
    "Restrict time range?",
            value = (df_master["Time"][len(df_master)-1],df_master["Time"][0]),
                max_value = df_master["Time"][0],
                min_value = df_master["Time"][len(df_master)-1])
            
            
            df_mask = df.mask(df["Datetime"] < date_range[0])
            df_mask = df_mask.mask(df_mask["Datetime"] > date_range[1])
            df_mask = df_mask.mask(df_mask["Time"] < time_range[0])
            df_mask = df_mask.mask(df_mask["Time"] > time_range[1])
            fig = px.scatter(df_mask, x="DateSerial", y = "Time", title="World Record Progression",labels={"value":"Splits (seconds)"},trendline="ols",trendline_color_override="red")
            customdata = np.stack((df_mask['Seconds'], df_mask['Date']), axis=-1)
            hovertemplate = ('Time: %{customdata[0]}<br>' + 
        'Date: %{customdata[1]}<br>' 
        '<extra></extra>')
            fig.update_traces(customdata=customdata, hovertemplate=hovertemplate)
            st.plotly_chart(fig, use_container_width=True)
            a=px.get_trendline_results(fig).px_fit_results.iloc[0].rsquared
            const = px.get_trendline_results(fig).px_fit_results.iloc[0].params[0]
            x1=px.get_trendline_results(fig).px_fit_results.iloc[0].params[1]
            st.write(f"Time = {round(x1,6)}(DateSerial) + {round(const,3)}")
            st.write(f"R-squared = {round(a,3)}")
            col1,col2=st.columns(2)
            with col1:
                date = st.date_input("Select date for WR prediction:", datetime(2024, 8, 15),format="DD/MM/YYYY")
                date_formatted=date.strftime('%d/%m/%Y')
                
            with col2:
                serial = date - datetime(1899, 12, 30).date()
    
                st.write(f"If a world record was achieved on {date_formatted}, this trend predicts it would be a time of {round(x1*serial.days +const,3)} seconds.")
























    if race_type=="Women's Team Sprint":
        
        c1,c2=st.columns([1,3])
        with c1:
            @st.cache_data
            def get_data_from_excel():
                df = pd.read_excel(
                    io='pages/WR_progressions/Women_TS.xlsx',
                    engine ='openpyxl',
                    sheet_name='Sheet1',
                    skiprows=0,
                    usecols='A:D',
                    nrows=30
                    )
                #df = df.replace(',','')
                
                df["Datetime"]=df["Date"]
                df["Date"]=df["Date"].dt.strftime("%d/%m/%Y")
                return df
            df= get_data_from_excel()
            df_master=df
            df_show = df.drop(columns=["Seconds","DateSerial","Datetime"])
            
            st.dataframe(df_show)
            ##Download buttons
            def convert_to_csv(df_show):
                return df.to_csv(index=False,sep = ",").encode('utf-32')
            csv = convert_to_csv(df_show)
            download1 = st.download_button(
                label="Download Women TS WR data as CSV",
                data=csv,
                file_name='Women_TS_Data.csv',
                mime='text/csv',
                key="buffertt1"
            )
            buffer_tt = io.BytesIO()
            with pd.ExcelWriter(buffer_tt, engine='xlsxwriter') as writer:
                df_show.to_excel(writer, sheet_name='Sheet1', index=False)
                writer.close()
                download2 = st.download_button(
                    label="Download Women TS WR data as Excel",
                    data=buffer_tt,
                    file_name='Women_TS_Data.xlsx',
                    mime='application/vnd.ms-excel',
                    key="buffertt2"
                )
            ##Download buttons complete


        with c2:
            date_range = st.slider(
    "Restrict date range?",
            value = (datetime.strptime(df_master["Date"][0], '%d/%m/%Y'),datetime.strptime(df_master["Date"][len(df_master)-1], '%d/%m/%Y')),
                min_value = datetime.strptime(df_master["Date"][0], '%d/%m/%Y'),
                max_value = datetime.strptime(df_master["Date"][len(df_master)-1], '%d/%m/%Y'),
            format="DD/MM/YY")
            
            time_range = st.slider(
    "Restrict time range?",
            value = (df_master["Time"][len(df_master)-1],df_master["Time"][0]),
                max_value = df_master["Time"][0],
                min_value = df_master["Time"][len(df_master)-1])
            
            
            df_mask = df.mask(df["Datetime"] < date_range[0])
            df_mask = df_mask.mask(df_mask["Datetime"] > date_range[1])
            df_mask = df_mask.mask(df_mask["Time"] < time_range[0])
            df_mask = df_mask.mask(df_mask["Time"] > time_range[1])
            fig = px.scatter(df_mask, x="DateSerial", y = "Time", title="World Record Progression",labels={"value":"Splits (seconds)"},trendline="ols",trendline_color_override="red")
            customdata = np.stack((df_mask['Seconds'], df_mask['Date']), axis=-1)
            hovertemplate = ('Time: %{customdata[0]}<br>' + 
        'Date: %{customdata[1]}<br>' 
        '<extra></extra>')
            fig.update_traces(customdata=customdata, hovertemplate=hovertemplate)
            st.plotly_chart(fig, use_container_width=True)
            a=px.get_trendline_results(fig).px_fit_results.iloc[0].rsquared
            const = px.get_trendline_results(fig).px_fit_results.iloc[0].params[0]
            x1=px.get_trendline_results(fig).px_fit_results.iloc[0].params[1]
            st.write(f"Time = {round(x1,6)}(DateSerial) + {round(const,3)}")
            st.write(f"R-squared = {round(a,3)}")
            col1,col2=st.columns(2)
            with col1:
                date = st.date_input("Select date for WR prediction:", datetime(2024, 8, 15),format="DD/MM/YYYY")
                date_formatted=date.strftime('%d/%m/%Y')
                
            with col2:
                serial = date - datetime(1899, 12, 30).date()
    
                st.write(f"If a world record was achieved on {date_formatted}, this trend predicts it would be a time of {round(x1*serial.days +const,3)} seconds.")




























    if race_type=="Men's Team Pursuit":
        
        c1,c2=st.columns([1,3])
        with c1:
            @st.cache_data
            def get_data_from_excel():
                df = pd.read_excel(
                    io='pages/WR_progressions/Men_TP.xlsx',
                    engine ='openpyxl',
                    sheet_name='Sheet1',
                    skiprows=0,
                    usecols='A:D',
                    nrows=30
                    )
                #df = df.replace(',','')
                df["Time"]=((pd.to_datetime(df["Time"], format="%H:%M:%S.%f").dt.strftime("%M:%S.%f")).astype(str)).str[1:9]
                # df["Time"]=df["Time"].astype(str)
                # df["Time"]=df["Time"].str[1:9]
                df["Datetime"]=df["Date"]
                df["Date"]=df["Date"].dt.strftime("%d/%m/%Y")
                return df
            df= get_data_from_excel()
            df_master=df
            df_show = df.drop(columns=["DateSerial","Datetime"])
            
            df_show
            
            ##Download buttons
            def convert_to_csv(df_show):
                return df.to_csv(index=False,sep = ",").encode('utf-32')
            csv = convert_to_csv(df_show)
            download1 = st.download_button(
                label="Download Men TP WR data as CSV",
                data=csv,
                file_name='Men_TP_WR_Data.csv',
                mime='text/csv',
                key="buffertt1"
            )
            buffer_tt = io.BytesIO()
            with pd.ExcelWriter(buffer_tt, engine='xlsxwriter') as writer:
                df_show.to_excel(writer, sheet_name='Sheet1', index=False)
                writer.close()
                download2 = st.download_button(
                    label="Download Men TP WR data as Excel",
                    data=buffer_tt,
                    file_name='Men_TP_WR_Data.xlsx',
                    mime='application/vnd.ms-excel',
                    key="buffertt2"
                )
            ##Download buttons complete


        with c2:
            date_range = st.slider(
    "Restrict date range?",
            value = (datetime.strptime(df_master["Date"][0], '%d/%m/%Y'),datetime.strptime(df_master["Date"][len(df_master)-1], '%d/%m/%Y')),
                min_value = datetime.strptime(df_master["Date"][0], '%d/%m/%Y'),
                max_value = datetime.strptime(df_master["Date"][len(df_master)-1], '%d/%m/%Y'),
            format="DD/MM/YY")
            
            time_range = st.slider(
    "Restrict time range?",
            value = (df_master["Seconds"][len(df_master)-1],df_master["Seconds"][0]),
            max_value = df_master["Seconds"][0],
            min_value = df_master["Seconds"][len(df_master)-1])
            
            
            df_mask = df.mask(df["Datetime"] < date_range[0])
            df_mask = df_mask.mask(df_mask["Datetime"] > date_range[1])
            df_mask = df_mask.mask(df_mask["Seconds"] < time_range[0])
            df_mask = df_mask.mask(df_mask["Seconds"] > time_range[1])
            fig = px.scatter(df_mask, x="DateSerial", y = "Seconds", title="World Record Progression",labels={"value":"Splits (seconds)"},trendline="ols",trendline_color_override="red")
            customdata = np.stack((round(df_mask['Seconds'],3), df_mask['Date']), axis=-1)
            hovertemplate = ('Time: %{customdata[0]}<br>' + 
        'Date: %{customdata[1]}<br>' 
        '<extra></extra>')
            fig.update_traces(customdata=customdata, hovertemplate=hovertemplate)
            st.plotly_chart(fig, use_container_width=True)
            a=px.get_trendline_results(fig).px_fit_results.iloc[0].rsquared
            const = px.get_trendline_results(fig).px_fit_results.iloc[0].params[0]
            x1=px.get_trendline_results(fig).px_fit_results.iloc[0].params[1]
            st.write(f"Time = {round(x1,6)}(DateSerial) + {round(const,3)}")
            st.write(f"R-squared = {round(a,3)}")
            col1,col2=st.columns(2)
            with col1:
                date = st.date_input("Select date for WR prediction:", datetime(2024, 8, 15),format="DD/MM/YYYY")
                date_formatted=date.strftime('%d/%m/%Y')
                
            with col2:
                serial = date - datetime(1899, 12, 30).date()
    

                m, s = divmod(x1*serial.days +const, 60)
                h, m = divmod(m, 60)
                m = int(m)
                s=round(s,3)
                if s<10:
                    s="0"+str(s)           
                st.write(f"If a world record was achieved on {date_formatted}, this trend predicts it would be a time of {m}:{s}.")















    if race_type=="Women's Team Pursuit":
        
        c1,c2=st.columns([1,3])
        with c1:
            @st.cache_data
            def get_data_from_excel():
                df = pd.read_excel(
                    io='pages/WR_progressions/Women_TP.xlsx',
                    engine ='openpyxl',
                    sheet_name='Sheet1',
                    skiprows=0,
                    usecols='A:D',
                    nrows=30
                    )
                #df = df.replace(',','')
                df["Time"]=((pd.to_datetime(df["Time"], format="%H:%M:%S.%f").dt.strftime("%M:%S.%f")).astype(str)).str[1:9]
                # df["Time"]=df["Time"].astype(str)
                # df["Time"]=df["Time"].str[1:9]
                df["Datetime"]=df["Date"]
                df["Date"]=df["Date"].dt.strftime("%d/%m/%Y")
                return df
            df= get_data_from_excel()
            df_master=df
            df_show = df.drop(columns=["DateSerial","Datetime"])
            
            df_show
            
            ##Download buttons
            def convert_to_csv(df_show):
                return df.to_csv(index=False,sep = ",").encode('utf-32')
            csv = convert_to_csv(df_show)
            download1 = st.download_button(
                label="Download Women TP WR data as CSV",
                data=csv,
                file_name='Women_TP_WR_Data.csv',
                mime='text/csv',
                key="buffertt1"
            )
            buffer_tt = io.BytesIO()
            with pd.ExcelWriter(buffer_tt, engine='xlsxwriter') as writer:
                df_show.to_excel(writer, sheet_name='Sheet1', index=False)
                writer.close()
                download2 = st.download_button(
                    label="Download Women TP WR data as Excel",
                    data=buffer_tt,
                    file_name='Women_TP_WR_Data.xlsx',
                    mime='application/vnd.ms-excel',
                    key="buffertt2"
                )
            ##Download buttons complete


        with c2:
            date_range = st.slider(
    "Restrict date range?",
            value = (datetime.strptime(df_master["Date"][0], '%d/%m/%Y'),datetime.strptime(df_master["Date"][len(df_master)-1], '%d/%m/%Y')),
                min_value = datetime.strptime(df_master["Date"][0], '%d/%m/%Y'),
                max_value = datetime.strptime(df_master["Date"][len(df_master)-1], '%d/%m/%Y'),
            format="DD/MM/YY")
            
            time_range = st.slider(
    "Restrict time range?",
            value = (df_master["Seconds"][len(df_master)-1],df_master["Seconds"][0]),
            max_value = df_master["Seconds"][0],
            min_value = df_master["Seconds"][len(df_master)-1])
            
            
            df_mask = df.mask(df["Datetime"] < date_range[0])
            df_mask = df_mask.mask(df_mask["Datetime"] > date_range[1])
            df_mask = df_mask.mask(df_mask["Seconds"] < time_range[0])
            df_mask = df_mask.mask(df_mask["Seconds"] > time_range[1])
            fig = px.scatter(df_mask, x="DateSerial", y = "Seconds", title="World Record Progression",labels={"value":"Splits (seconds)"},trendline="ols",trendline_color_override="red")
            customdata = np.stack((round(df_mask['Seconds'],3), df_mask['Date']), axis=-1)
            hovertemplate = ('Time: %{customdata[0]}<br>' + 
        'Date: %{customdata[1]}<br>' 
        '<extra></extra>')
            fig.update_traces(customdata=customdata, hovertemplate=hovertemplate)
            st.plotly_chart(fig, use_container_width=True)
            a=px.get_trendline_results(fig).px_fit_results.iloc[0].rsquared
            const = px.get_trendline_results(fig).px_fit_results.iloc[0].params[0]
            x1=px.get_trendline_results(fig).px_fit_results.iloc[0].params[1]
            st.write(f"Time = {round(x1,6)}(DateSerial) + {round(const,3)}")
            st.write(f"R-squared = {round(a,3)}")
            col1,col2=st.columns(2)
            with col1:
                date = st.date_input("Select date for WR prediction:", datetime(2024, 8, 15),format="DD/MM/YYYY")
                date_formatted=date.strftime('%d/%m/%Y')
                
            with col2:
                serial = date - datetime(1899, 12, 30).date()
                

                m, s = divmod(x1*serial.days +const, 60)
                h, m = divmod(m, 60)
                m = int(m)
                
                s=round(s,3)
                if s<10:
                    s="0"+str(s)
                st.write(f"If a world record was achieved on {date_formatted}, this trend predicts it would be a time of {m}:{s}.")

















    
    if race_type=="Men's Individual Pursuit":
        
        c1,c2=st.columns([1,3])
        with c1:
            @st.cache_data
            def get_data_from_excel():
                df = pd.read_excel(
                    io='pages/WR_progressions/Men_IP.xlsx',
                    engine ='openpyxl',
                    sheet_name='Sheet1',
                    skiprows=0,
                    usecols='A:D',
                    nrows=30
                    )
                #df = df.replace(',','')
                df["Time"]=((pd.to_datetime(df["Time"], format="%H:%M:%S.%f").dt.strftime("%M:%S.%f")).astype(str)).str[1:9]
                # df["Time"]=df["Time"].astype(str)
                # df["Time"]=df["Time"].str[1:9]
                df["Datetime"]=df["Date"]
                df["Date"]=df["Date"].dt.strftime("%d/%m/%Y")
                return df
            df= get_data_from_excel()
            df_master=df
            df_show = df.drop(columns=["DateSerial","Datetime"])
            
            df_show
            
            ##Download buttons
            def convert_to_csv(df_show):
                return df.to_csv(index=False,sep = ",").encode('utf-32')
            csv = convert_to_csv(df_show)
            download1 = st.download_button(
                label="Download Men IP WR data as CSV",
                data=csv,
                file_name='Men_IP_WR_Data.csv',
                mime='text/csv',
                key="buffertt1"
            )
            buffer_tt = io.BytesIO()
            with pd.ExcelWriter(buffer_tt, engine='xlsxwriter') as writer:
                df_show.to_excel(writer, sheet_name='Sheet1', index=False)
                writer.close()
                download2 = st.download_button(
                    label="Download Men IP WR data as Excel",
                    data=buffer_tt,
                    file_name='Men_IP_WR_Data.xlsx',
                    mime='application/vnd.ms-excel',
                    key="buffertt2"
                )
            ##Download buttons complete


        with c2:
            date_range = st.slider(
    "Restrict date range?",
            value = (datetime.strptime(df_master["Date"][0], '%d/%m/%Y'),datetime.strptime(df_master["Date"][len(df_master)-1], '%d/%m/%Y')),
                min_value = datetime.strptime(df_master["Date"][0], '%d/%m/%Y'),
                max_value = datetime.strptime(df_master["Date"][len(df_master)-1], '%d/%m/%Y'),
            format="DD/MM/YY")
            
            time_range = st.slider(
    "Restrict time range?",
            value = (df_master["Seconds"][len(df_master)-1],df_master["Seconds"][0]),
            max_value = df_master["Seconds"][0],
            min_value = df_master["Seconds"][len(df_master)-1])
            
            
            df_mask = df.mask(df["Datetime"] < date_range[0])
            df_mask = df_mask.mask(df_mask["Datetime"] > date_range[1])
            df_mask = df_mask.mask(df_mask["Seconds"] < time_range[0])
            df_mask = df_mask.mask(df_mask["Seconds"] > time_range[1])
            fig = px.scatter(df_mask, x="DateSerial", y = "Seconds", title="World Record Progression",labels={"value":"Splits (seconds)"},trendline="ols",trendline_color_override="red")
            customdata = np.stack((round(df_mask['Seconds'],3), df_mask['Date']), axis=-1)
            hovertemplate = ('Time: %{customdata[0]}<br>' + 
        'Date: %{customdata[1]}<br>' 
        '<extra></extra>')
            fig.update_traces(customdata=customdata, hovertemplate=hovertemplate)
            st.plotly_chart(fig, use_container_width=True)
            a=px.get_trendline_results(fig).px_fit_results.iloc[0].rsquared
            const = px.get_trendline_results(fig).px_fit_results.iloc[0].params[0]
            x1=px.get_trendline_results(fig).px_fit_results.iloc[0].params[1]
            st.write(f"Time = {round(x1,6)}(DateSerial) + {round(const,3)}")
            st.write(f"R-squared = {round(a,3)}")
            col1,col2=st.columns(2)
            with col1:
                date = st.date_input("Select date for WR prediction:", datetime(2024, 8, 15),format="DD/MM/YYYY")
                date_formatted=date.strftime('%d/%m/%Y')
                
            with col2:
                serial = date - datetime(1899, 12, 30).date()
    

                m, s = divmod(x1*serial.days +const, 60)
                h, m = divmod(m, 60)
                m = int(m)
                s=round(s,3)
                if s<10:
                    s="0"+str(s)            
                st.write(f"If a world record was achieved on {date_formatted}, this trend predicts it would be a time of {m}:{s}.")