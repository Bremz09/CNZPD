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
        
        @st.cache_data
        def get_wr_data_from_excel():
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


        def get_placing_data_from_excel():
            df = pd.read_excel(
                io='pages/WR_progressions/Medals_Men_F200.xlsx',
                engine ='openpyxl',
                sheet_name='Sheet1',
                skiprows=0,
                usecols='A:G',
                nrows=40
                )
            #df = df.replace(',','')


            return df


        c1,c2=st.columns([1,3])
        with c1:
            trend = st.selectbox("WR or Placings trend?:", ["World Record progression","Placing progression"], key="MSP trend type Selector")

            if trend=="World Record progression":
                df= get_wr_data_from_excel()
                df_master=df
                df_show = df
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
                    fig = px.scatter(df_mask, x="DateSerial", y = "Seconds", title="Men's Flying 200m World Record Progression",labels={"value":"Splits (seconds)"},trendline='ols',trendline_color_override="red")
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


                
                
              
            else:
                df = get_placing_data_from_excel()
                df_master=df
                df_show=df
                df_show
                
                ##Download buttons
                def convert_to_csv(df_show):
                    return df.to_csv(index=False,sep = ",").encode('utf-32')
                csv = convert_to_csv(df_show)
                download1 = st.download_button(
                    label="Download Men F200 Placing data as CSV",
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
                        label="Download Men F200 Placing data as Excel",
                        data=buffer_tt,
                        file_name='Men_F200_Data.xlsx',
                        mime='application/vnd.ms-excel',
                        key="buffertt2"
                    )
                ##Download buttons complete
                with c2:
                    date_range = st.slider(
            "Restrict date range?",
                    value = (2000,2023),
                        min_value = 2000,
                        max_value = 2021)
                    
                    time_range = st.slider(
            "Restrict time range?",
                    value = (9.100,11.000),
                        max_value = 11.000,
                        min_value = 9.100)
                    
                    df_mask = df.mask(df["Year"] < date_range[0])
                    df_mask = df_mask.mask(df_mask["Year"] > date_range[1])
                    df_mask = df_mask.mask(df_mask["1st"] < time_range[0])
                    df_mask = df_mask.mask(df_mask["1st"] > time_range[1])
                    df_mask = df_mask.mask(df_mask["2nd"] < time_range[0])
                    df_mask = df_mask.mask(df_mask["2nd"] > time_range[1])
                    df_mask = df_mask.mask(df_mask["3rd"] < time_range[0])
                    df_mask = df_mask.mask(df_mask["3rd"] > time_range[1])
                    df_mask = df_mask.mask(df_mask["16th"] < time_range[0])
                    df_mask = df_mask.mask(df_mask["16th"] > time_range[1])
                    df_mask = df_mask.mask(df_mask["8th"] < time_range[0])
                    df_mask = df_mask.mask(df_mask["8th"] > time_range[1])
                    fig = px.scatter(df_mask, x="Year", y = ["1st","2nd","3rd","8th","16th"], title="Men's Sprint Olympic and World Champs Placings Time Progression",labels={"value":"Seconds"},trendline="ols", color_discrete_sequence=['gold',"silver","darkorange","lightpink","teal"])
                    customdata = np.stack((round(df_mask['1st'],3), round(df_mask['2nd'],3),round(df_mask['3rd'],3), round(df_mask['8th'],3),round(df_mask['16th'],3),df_mask['Year'], df_mask['Competition']),axis=-1)
                    hovertemplate = ('Gold: %{customdata[0]}<br>' + 'Silver: %{customdata[1]}<br>' + 'Bronze: %{customdata[2]}<br>' + '8th: %{customdata[3]}<br>' + '16th: %{customdata[4]}<br>' +
                'Year: %{customdata[5]}<br>' +
                'Competition: %{customdata[6]}<br>'
                '<extra></extra>')
                    fig.update_traces(customdata=customdata, hovertemplate=hovertemplate)
                    
                    st.plotly_chart(fig, use_container_width=True)
                    col1,col2=st.columns(2)
                    with col1:
                        first_a=px.get_trendline_results(fig).px_fit_results.iloc[0].rsquared
                        first_const = px.get_trendline_results(fig).px_fit_results.iloc[0].params[0]
                        first_x1=px.get_trendline_results(fig).px_fit_results.iloc[0].params[1]
                        
                        second_a=px.get_trendline_results(fig).px_fit_results.iloc[1].rsquared
                        second_const = px.get_trendline_results(fig).px_fit_results.iloc[1].params[0]
                        second_x1=px.get_trendline_results(fig).px_fit_results.iloc[1].params[1]
                        
                        third_a=px.get_trendline_results(fig).px_fit_results.iloc[2].rsquared
                        third_const = px.get_trendline_results(fig).px_fit_results.iloc[2].params[0]
                        third_x1=px.get_trendline_results(fig).px_fit_results.iloc[2].params[1]
                        
                        eigth_a=px.get_trendline_results(fig).px_fit_results.iloc[3].rsquared
                        eigth_const = px.get_trendline_results(fig).px_fit_results.iloc[3].params[0]
                        eigth_x1=px.get_trendline_results(fig).px_fit_results.iloc[3].params[1]
                        
                        sixteenth_a=px.get_trendline_results(fig).px_fit_results.iloc[4].rsquared
                        sixteenth_const = px.get_trendline_results(fig).px_fit_results.iloc[4].params[0]
                        sixteenth_x1=px.get_trendline_results(fig).px_fit_results.iloc[4].params[1]
                        
                        st.write(f"1st = {round(first_x1,6)}(Year) + {round(first_const,3)}")
                        st.write(f"R-squared = {round(first_a,3)}")
                        
                        st.write(f"2nd = {round(second_x1,6)}(Year) + {round(second_const,3)}")
                        st.write(f"R-squared = {round(second_a,3)}")
                        
                        st.write(f"3rd = {round(third_x1,6)}(Year) + {round(third_const,3)}")
                        st.write(f"R-squared = {round(third_a,3)}")
                        
                        st.write(f"8th = {round(eigth_x1,6)}(Year) + {round(eigth_const,3)}")
                        st.write(f"R-squared = {round(eigth_a,3)}")
                        
                        st.write(f"16th = {round(sixteenth_x1,6)}(Year) + {round(sixteenth_const,3)}")
                        st.write(f"R-squared = {round(sixteenth_a,3)}")

                    with col2:
                        predict_year = st.selectbox("Select year for medal predictions:", [2024,2028,2032,2036,2040,2044,2048])
                        
                        
                        first_m, first_s = divmod(first_x1*predict_year +first_const, 60)
                        first_h, first_m = divmod(first_m, 60)
                        first_m = int(first_m)
                        first_s=round(first_s,3)
                        if first_s<10:
                            first_s="0"+str(first_s)           
                        st.write(f"This trend predicts a top qualifying time of {first_s} in {predict_year}.")
        

                        second_m, second_s = divmod(second_x1*predict_year +second_const, 60)
                        second_h, second_m = divmod(second_m, 60)
                        second_m = int(second_m)
                        second_s=round(second_s,3)
                        if second_s<10:
                            second_s="0"+str(second_s)           
                        st.write(f"This trend predicts a second qualifying time of {second_s} in {predict_year}.")

                        third_m, third_s = divmod(third_x1*predict_year +third_const, 60)
                        third_h, third_m = divmod(third_m, 60)
                        third_m = int(third_m)
                        third_s=round(third_s,3)
                        if third_s<10:
                            third_s="0"+str(third_s)           
                        st.write(f"This trend predicts a third qualifying time of {third_s} in {predict_year}.")
        
        
            
                        eigth_m, eigth_s = divmod(eigth_x1*predict_year +eigth_const, 60)
                        eigth_h, eigth_m = divmod(eigth_m, 60)
                        eigth_m = int(eigth_m)
                        eigth_s=round(eigth_s,3)
                        if eigth_s<10:
                            eigth_s="0"+str(eigth_s)           
                        st.write(f"This trend predicts a eigth qualifying time of {eigth_s} in {predict_year}.")

                        sixteenth_m, sixteenth_s = divmod(sixteenth_x1*predict_year +sixteenth_const, 60)
                        sixteenth_h, sixteenth_m = divmod(sixteenth_m, 60)
                        sixteenth_m = int(sixteenth_m)
                        sixteenth_s=round(sixteenth_s,3)
                        if sixteenth_s<10:
                            sixteenth_s="0"+str(sixteenth_s)           
                        st.write(f"This trend predicts a sixteenth qualifying time of {sixteenth_s} in {predict_year}.")















    if race_type=="Women's Sprint Qualifying":
        
        @st.cache_data
        def get_wr_data_from_excel():
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


        def get_placing_data_from_excel():
            df = pd.read_excel(
                io='pages/WR_progressions/Medals_Women_F200.xlsx',
                engine ='openpyxl',
                sheet_name='Sheet1',
                skiprows=0,
                usecols='A:G',
                nrows=40
                )
            #df = df.replace(',','')


            return df


        c1,c2=st.columns([1,3])
        with c1:
            trend = st.selectbox("WR or Placings trend?:", ["World Record progression","Placing progression"], key="MSP trend type Selector")

            if trend=="World Record progression":
                df= get_wr_data_from_excel()
                df_master=df
                df_show = df
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
                    fig = px.scatter(df_mask, x="DateSerial", y = "Seconds", title="Men's Flying 200m World Record Progression",labels={"value":"Splits (seconds)"},trendline='ols',trendline_color_override="red")
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


                
                
              
            else:
                df = get_placing_data_from_excel()
                df_master=df
                df_show=df
                df_show
                
                ##Download buttons
                def convert_to_csv(df_show):
                    return df.to_csv(index=False,sep = ",").encode('utf-32')
                csv = convert_to_csv(df_show)
                download1 = st.download_button(
                    label="Download Men F200 Placing data as CSV",
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
                        label="Download Men F200 Placing data as Excel",
                        data=buffer_tt,
                        file_name='Men_F200_Data.xlsx',
                        mime='application/vnd.ms-excel',
                        key="buffertt2"
                    )
                ##Download buttons complete
                with c2:
                    date_range = st.slider(
            "Restrict date range?",
                    value = (2000,2023),
                        min_value = 2000,
                        max_value = 2021)
                    
                    time_range = st.slider(
            "Restrict time range?",
                    value = (10.100,12.200),
                        max_value = 12.200,
                        min_value = 10.100)
                    
                    df_mask = df.mask(df["Year"] < date_range[0])
                    df_mask = df_mask.mask(df_mask["Year"] > date_range[1])
                    df_mask = df_mask.mask(df_mask["1st"] < time_range[0])
                    df_mask = df_mask.mask(df_mask["1st"] > time_range[1])
                    df_mask = df_mask.mask(df_mask["2nd"] < time_range[0])
                    df_mask = df_mask.mask(df_mask["2nd"] > time_range[1])
                    df_mask = df_mask.mask(df_mask["3rd"] < time_range[0])
                    df_mask = df_mask.mask(df_mask["3rd"] > time_range[1])
                    df_mask = df_mask.mask(df_mask["16th"] < time_range[0])
                    df_mask = df_mask.mask(df_mask["16th"] > time_range[1])
                    df_mask = df_mask.mask(df_mask["8th"] < time_range[0])
                    df_mask = df_mask.mask(df_mask["8th"] > time_range[1])
                    fig = px.scatter(df_mask, x="Year", y = ["1st","2nd","3rd","8th","16th"], title="Women's Sprint Olympic and World Champs Placings Time Progression",labels={"value":"Seconds"},trendline="ols", color_discrete_sequence=['gold',"silver","darkorange","lightpink","teal"])
                    customdata = np.stack((round(df_mask['1st'],3), round(df_mask['2nd'],3),round(df_mask['3rd'],3), round(df_mask['8th'],3),round(df_mask['16th'],3),df_mask['Year'], df_mask['Competition']),axis=-1)
                    hovertemplate = ('Gold: %{customdata[0]}<br>' + 'Silver: %{customdata[1]}<br>' + 'Bronze: %{customdata[2]}<br>' + '8th: %{customdata[3]}<br>' + '16th: %{customdata[4]}<br>' +
                'Year: %{customdata[5]}<br>' +
                'Competition: %{customdata[6]}<br>'
                '<extra></extra>')
                    fig.update_traces(customdata=customdata, hovertemplate=hovertemplate)
                    
                    st.plotly_chart(fig, use_container_width=True)
                    col1,col2=st.columns(2)
                    with col1:
                        first_a=px.get_trendline_results(fig).px_fit_results.iloc[0].rsquared
                        first_const = px.get_trendline_results(fig).px_fit_results.iloc[0].params[0]
                        first_x1=px.get_trendline_results(fig).px_fit_results.iloc[0].params[1]
                        
                        second_a=px.get_trendline_results(fig).px_fit_results.iloc[1].rsquared
                        second_const = px.get_trendline_results(fig).px_fit_results.iloc[1].params[0]
                        second_x1=px.get_trendline_results(fig).px_fit_results.iloc[1].params[1]
                        
                        third_a=px.get_trendline_results(fig).px_fit_results.iloc[2].rsquared
                        third_const = px.get_trendline_results(fig).px_fit_results.iloc[2].params[0]
                        third_x1=px.get_trendline_results(fig).px_fit_results.iloc[2].params[1]
                        
                        eigth_a=px.get_trendline_results(fig).px_fit_results.iloc[3].rsquared
                        eigth_const = px.get_trendline_results(fig).px_fit_results.iloc[3].params[0]
                        eigth_x1=px.get_trendline_results(fig).px_fit_results.iloc[3].params[1]
                        
                        sixteenth_a=px.get_trendline_results(fig).px_fit_results.iloc[4].rsquared
                        sixteenth_const = px.get_trendline_results(fig).px_fit_results.iloc[4].params[0]
                        sixteenth_x1=px.get_trendline_results(fig).px_fit_results.iloc[4].params[1]
                        
                        st.write(f"1st = {round(first_x1,6)}(Year) + {round(first_const,3)}")
                        st.write(f"R-squared = {round(first_a,3)}")
                        
                        st.write(f"2nd = {round(second_x1,6)}(Year) + {round(second_const,3)}")
                        st.write(f"R-squared = {round(second_a,3)}")
                        
                        st.write(f"3rd = {round(third_x1,6)}(Year) + {round(third_const,3)}")
                        st.write(f"R-squared = {round(third_a,3)}")
                        
                        st.write(f"8th = {round(eigth_x1,6)}(Year) + {round(eigth_const,3)}")
                        st.write(f"R-squared = {round(eigth_a,3)}")
                        
                        st.write(f"16th = {round(sixteenth_x1,6)}(Year) + {round(sixteenth_const,3)}")
                        st.write(f"R-squared = {round(sixteenth_a,3)}")

                    with col2:
                        predict_year = st.selectbox("Select year for medal predictions:", [2024,2028,2032,2036,2040,2044,2048])
                        
                        
                        first_m, first_s = divmod(first_x1*predict_year +first_const, 60)
                        first_h, first_m = divmod(first_m, 60)
                        first_m = int(first_m)
                        first_s=round(first_s,3)
                        if first_s<10:
                            first_s="0"+str(first_s)           
                        st.write(f"This trend predicts a top qualifying time of {first_s} in {predict_year}.")
        

                        second_m, second_s = divmod(second_x1*predict_year +second_const, 60)
                        second_h, second_m = divmod(second_m, 60)
                        second_m = int(second_m)
                        second_s=round(second_s,3)
                        if second_s<10:
                            second_s="0"+str(second_s)           
                        st.write(f"This trend predicts a second qualifying time of {second_s} in {predict_year}.")

                        third_m, third_s = divmod(third_x1*predict_year +third_const, 60)
                        third_h, third_m = divmod(third_m, 60)
                        third_m = int(third_m)
                        third_s=round(third_s,3)
                        if third_s<10:
                            third_s="0"+str(third_s)           
                        st.write(f"This trend predicts a third qualifying time of {third_s} in {predict_year}.")
        
        
            
                        eigth_m, eigth_s = divmod(eigth_x1*predict_year +eigth_const, 60)
                        eigth_h, eigth_m = divmod(eigth_m, 60)
                        eigth_m = int(eigth_m)
                        eigth_s=round(eigth_s,3)
                        if eigth_s<10:
                            eigth_s="0"+str(eigth_s)           
                        st.write(f"This trend predicts a eigth qualifying time of {eigth_s} in {predict_year}.")

                        sixteenth_m, sixteenth_s = divmod(sixteenth_x1*predict_year +sixteenth_const, 60)
                        sixteenth_h, sixteenth_m = divmod(sixteenth_m, 60)
                        sixteenth_m = int(sixteenth_m)
                        sixteenth_s=round(sixteenth_s,3)
                        if sixteenth_s<10:
                            sixteenth_s="0"+str(sixteenth_s)           
                        st.write(f"This trend predicts a sixteenth qualifying time of {sixteenth_s} in {predict_year}.")

















#     if race_type=="Women's Sprint Qualifying":
        
#         c1,c2=st.columns([1,3])
#         with c1:
#             @st.cache_data
#             def get_data_from_excel():
#                 df = pd.read_excel(
#                     io='pages/WR_progressions/Women_F200.xlsx',
#                     engine ='openpyxl',
#                     sheet_name='Sheet1',
#                     skiprows=0,
#                     usecols='A:D',
#                     nrows=30
#                     )
#                 #df = df.replace(',','')
                
#                 df["Datetime"]=df["Date"]
#                 df["Date"]=df["Date"].dt.strftime("%d/%m/%Y")
#                 return df
#             df= get_data_from_excel()
#             df_master=df
#             df_show = df.drop(columns=["Seconds","DateSerial","Datetime"])
            
#             st.dataframe(df_show)
#             ##Download buttons
#             def convert_to_csv(df_show):
#                 return df.to_csv(index=False,sep = ",").encode('utf-32')
#             csv = convert_to_csv(df_show)
#             download1 = st.download_button(
#                 label="Download Women F200 WR data as CSV",
#                 data=csv,
#                 file_name='Women_F200_Data.csv',
#                 mime='text/csv',
#                 key="buffertt1"
#             )
#             buffer_tt = io.BytesIO()
#             with pd.ExcelWriter(buffer_tt, engine='xlsxwriter') as writer:
#                 df_show.to_excel(writer, sheet_name='Sheet1', index=False)
#                 writer.close()
#                 download2 = st.download_button(
#                     label="Download Women F200 WR data as Excel",
#                     data=buffer_tt,
#                     file_name='Women_F200_Data.xlsx',
#                     mime='application/vnd.ms-excel',
#                     key="buffertt2"
#                 )
#             ##Download buttons complete


#         with c2:
#             date_range = st.slider(
#     "Restrict date range?",
#             value = (datetime.strptime(df_master["Date"][0], '%d/%m/%Y'),datetime.strptime(df_master["Date"][len(df_master)-1], '%d/%m/%Y')),
#                 min_value = datetime.strptime(df_master["Date"][0], '%d/%m/%Y'),
#                 max_value = datetime.strptime(df_master["Date"][len(df_master)-1], '%d/%m/%Y'),
#             format="DD/MM/YY")
            
#             time_range = st.slider(
#     "Restrict time range?",
#             value = (df_master["Time"][len(df_master)-1],df_master["Time"][0]),
#                 max_value = df_master["Time"][0],
#                 min_value = df_master["Time"][len(df_master)-1])
            
            
#             df_mask = df.mask(df["Datetime"] < date_range[0])
#             df_mask = df_mask.mask(df_mask["Datetime"] > date_range[1])
#             df_mask = df_mask.mask(df_mask["Time"] < time_range[0])
#             df_mask = df_mask.mask(df_mask["Time"] > time_range[1])
#             fig = px.scatter(df_mask, x="DateSerial", y = "Seconds", title="Women's Flying 200m World Record Progression",labels={"value":"Splits (seconds)"},trendline="ols",trendline_color_override="red")
#             customdata = np.stack((df_mask['Seconds'], df_mask['Date']), axis=-1)
#             hovertemplate = ('Time: %{customdata[0]}<br>' + 
#         'Date: %{customdata[1]}<br>' 
#         '<extra></extra>')
#             fig.update_traces(customdata=customdata, hovertemplate=hovertemplate)
#             st.plotly_chart(fig, use_container_width=True)
#             a=px.get_trendline_results(fig).px_fit_results.iloc[0].rsquared
#             const = px.get_trendline_results(fig).px_fit_results.iloc[0].params[0]
#             x1=px.get_trendline_results(fig).px_fit_results.iloc[0].params[1]
#             st.write(f"Time = {round(x1,6)}(DateSerial) + {round(const,3)}")
#             st.write(f"R-squared = {round(a,3)}")
#             col1,col2=st.columns(2)
#             with col1:
#                 date = st.date_input("Select date for WR prediction:", datetime(2024, 8, 15),format="DD/MM/YYYY")
#                 date_formatted=date.strftime('%d/%m/%Y')
                
#             with col2:
#                 serial = date - datetime(1899, 12, 30).date()
    
#                 st.write(f"If a world record was achieved on {date_formatted}, this trend predicts it would be a time of {round(x1*serial.days +const,3)} seconds.")






























    if race_type=="Men's Team Sprint":
        @st.cache_data
        def get_wr_data_from_excel():
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

        def get_medal_data_from_excel():
            df = pd.read_excel(
                io='pages/WR_progressions/Medals_Men_TS.xlsx',
                engine ='openpyxl',
                sheet_name='Sheet1',
                skiprows=0,
                usecols='A:D',
                nrows=30
                )
            #df = df.replace(',','')
       

            return df
        
        c1,c2=st.columns([1,3])
        with c1:
            trend = st.selectbox("WR or Medal trend?:", ["World Record progression","Medal progression"], key="trend type Selector")

            if trend=="World Record progression":
                df= get_wr_data_from_excel()
                df_master=df
                df_show = df
                df_show
    
                ##Download buttons
                def convert_to_csv(df_show):
                    return df.to_csv(index=False,sep = ",").encode('utf-32')
                csv = convert_to_csv(df_show)
                download1 = st.download_button(
                    label="Download Men TS data as CSV",
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
                        label="Download Men TS data as Excel",
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
                    fig = px.scatter(df_mask, x="DateSerial", y = "Seconds", title="Men's Team Sprint World Record Progression",labels={"value":"Splits (seconds)"},trendline="ols",trendline_color_override="red")
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
        

            else:
                df= get_medal_data_from_excel()
                df_master=df
                df_show = df
                df_show
    
                ##Download buttons
                def convert_to_csv(df_show):
                    return df.to_csv(index=False,sep = ",").encode('utf-32')
                csv = convert_to_csv(df_show)
                download1 = st.download_button(
                    label="Download Men TS data as CSV",
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
                        label="Download Men TS data as Excel",
                        data=buffer_tt,
                        file_name='Men_TS_Data.xlsx',
                        mime='application/vnd.ms-excel',
                        key="buffertt2"
                    )
                ##Download buttons complete
    
    
                with c2:
                    date_range = st.slider(
            "Restrict date range?",
                    value = (2000,2021),
                        min_value = 2000,
                        max_value = 2021)
                    
                    time_range = st.slider(
            "Restrict time range?",
                    value = (41.369,45.161),
                        max_value = 45.161,
                        min_value = 41.369)
                    
                    df_mask = df.mask(df["Year"] < date_range[0])
                    df_mask = df_mask.mask(df_mask["Year"] > date_range[1])
                    df_mask = df_mask.mask(df_mask["Bronze_Time"] < time_range[0])
                    df_mask = df_mask.mask(df_mask["Bronze_Time"] > time_range[1])
                    df_mask = df_mask.mask(df_mask["Silver_Time"] < time_range[0])
                    df_mask = df_mask.mask(df_mask["Silver_Time"] > time_range[1])
                    df_mask = df_mask.mask(df_mask["Gold_Time"] < time_range[0])
                    df_mask = df_mask.mask(df_mask["Gold_Time"] > time_range[1])
                    fig = px.scatter(df_mask, x="Year", y = ["Bronze_Time","Silver_Time","Gold_Time"], title="Men's Team Sprint Olympic Medal Winning Time Progression",labels={"value":"Seconds"},trendline="ols", color_discrete_sequence=['darkorange',"silver","gold"])
                    customdata = np.stack((round(df_mask['Bronze_Time'],3), round(df_mask['Silver_Time'],3),round(df_mask['Gold_Time'],3),df_mask['Year']), axis=-1)
                    hovertemplate = ('Bronze: %{customdata[0]}<br>' + 'Silver: %{customdata[1]}<br>' + 'Gold: %{customdata[2]}<br>' +
                'Year: %{customdata[3]}<br>' 
                '<extra></extra>')
                    fig.update_traces(customdata=customdata, hovertemplate=hovertemplate)
                    
                    st.plotly_chart(fig, use_container_width=True)
                    col1,col2=st.columns(2)
                    with col1:
                        bronze_a=px.get_trendline_results(fig).px_fit_results.iloc[0].rsquared
                        bronze_const = px.get_trendline_results(fig).px_fit_results.iloc[0].params[0]
                        bronze_x1=px.get_trendline_results(fig).px_fit_results.iloc[0].params[1]
                        silver_a=px.get_trendline_results(fig).px_fit_results.iloc[1].rsquared
                        silver_const = px.get_trendline_results(fig).px_fit_results.iloc[1].params[0]
                        silver_x1=px.get_trendline_results(fig).px_fit_results.iloc[1].params[1]
                        gold_a=px.get_trendline_results(fig).px_fit_results.iloc[2].rsquared
                        gold_const = px.get_trendline_results(fig).px_fit_results.iloc[2].params[0]
                        gold_x1=px.get_trendline_results(fig).px_fit_results.iloc[2].params[1]
                        st.write(f"Bronze time = {round(bronze_x1,6)}(Year) + {round(bronze_const,3)}")
                        st.write(f"R-squared = {round(bronze_a,3)}")
                        st.write(f"Silver time = {round(silver_x1,6)}(Year) + {round(silver_const,3)}")
                        st.write(f"R-squared = {round(silver_a,3)}")
                        st.write(f"Gold time = {round(gold_x1,6)}(Year) + {round(gold_const,3)}")
                        st.write(f"R-squared = {round(gold_a,3)}")
                    with col2:
                        predict_year = st.selectbox("Select year for medal predictions:", [2024,2028,2032,2036,2040,2044,2048])
                        
                        
                    
        
                        bronze_m, bronze_s = divmod(bronze_x1*predict_year +bronze_const, 60)
                        bronze_h, bronze_m = divmod(bronze_m, 60)
                        bronze_m = int(bronze_m)
                        bronze_s=round(bronze_s,3)
                        if bronze_s<10:
                            bronze_s="0"+str(bronze_s)           
                        st.write(f"This trend predicts a Bronze medal winning time of {bronze_s} in {predict_year}.")
                        silver_m, silver_s = divmod(silver_x1*predict_year +silver_const, 60)
                        silver_h, silver_m = divmod(silver_m, 60)
                        silver_m = int(silver_m)
                        silver_s=round(silver_s,3)
                        if silver_s<10:
                            silver_s="0"+str(silver_s)           
                        st.write(f"This trend predicts a Silver medal winning time of {silver_s} in {predict_year}.")
                        gold_m, gold_s = divmod(gold_x1*predict_year +gold_const, 60)
                        gold_h, gold_m = divmod(gold_m, 60)
                        gold_m = int(gold_m)
                        gold_s=round(gold_s,3)
                        if gold_s<10:
                            gold_s="0"+str(gold_s)           
                        st.write(f"This trend predicts a Gold medal winning time of {gold_s} in {predict_year}.")
        
        
        
        




















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
            fig = px.scatter(df_mask, x="DateSerial", y = "Seconds", title="Women's Team Sprint World Record Progression",labels={"value":"Splits (seconds)"},trendline="ols",trendline_color_override="red")
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
        @st.cache_data
        def get_wr_data_from_excel():
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

        def get_medal_data_from_excel():
            df = pd.read_excel(
                io='pages/WR_progressions/Medals_Men_TP.xlsx',
                engine ='openpyxl',
                sheet_name='Sheet1',
                skiprows=0,
                usecols='A:G',
                nrows=30
                )
            #df = df.replace(',','')
       
            df["Bronze_Time"]=((pd.to_datetime(df["Bronze_Time"], format="%H:%M:%S.%f").dt.strftime("%M:%S.%f")).astype(str)).str[1:9]
            df["Silver_Time"]=((pd.to_datetime(df["Silver_Time"], format="%H:%M:%S.%f").dt.strftime("%M:%S.%f")).astype(str)).str[1:9]
            df["Gold_Time"]=((pd.to_datetime(df["Gold_Time"], format="%H:%M:%S.%f").dt.strftime("%M:%S.%f")).astype(str)).str[1:9]
            # df["Time"]=df["Time"].astype(str)
            # df["Time"]=df["Time"].str[1:9]
            # df["Datetime"]=df["Date"]
            # df["Date"]=df["Date"].dt.strftime("%d/%m/%Y")
            return df
    
        c1,c2=st.columns([1,3])
        with c1:
            trend = st.selectbox("WR or Medal trend?:", ["World Record progression","Medal progression"], key="trend type Selector")
            
            if trend=="World Record progression":
                df= get_wr_data_from_excel()
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
                    fig = px.scatter(df_mask, x="DateSerial", y = "Seconds", title="Men's Team Pursuit World Record Progression",labels={"value":"Splits (seconds)"},trendline="ols",trendline_color_override="red")
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
        
        
            
            else:
                df=get_medal_data_from_excel()
                df_master=df
                df_show=df
                # df_show = df.drop(columns=["DateSerial","Datetime"])
                
                df_show
                
                ##Download buttons
                def convert_to_csv(df_show):
                    return df.to_csv(index=False,sep = ",").encode('utf-32')
                csv = convert_to_csv(df_show)
                download1 = st.download_button(
                    label="Download Men TP data as CSV",
                    data=csv,
                    file_name='Men_TP_Data.csv',
                    mime='text/csv',
                    key="buffertt1"
                )
                buffer_tt = io.BytesIO()
                with pd.ExcelWriter(buffer_tt, engine='xlsxwriter') as writer:
                    df_show.to_excel(writer, sheet_name='Sheet1', index=False)
                    writer.close()
                    download2 = st.download_button(
                        label="Download Men TP data as Excel",
                        data=buffer_tt,
                        file_name='Men_TP_Data.xlsx',
                        mime='application/vnd.ms-excel',
                        key="buffertt2"
                    )
                ##Download buttons complete
    
    
                with c2:
                    date_range = st.slider(
            "Restrict date range?",
                    value = (df_master["Year"][0]+1,df_master["Year"][len(df_master)-1]),
                        max_value = df_master["Year"][0]+1,
                        min_value = df_master["Year"][len(df_master)-1])
                    
                    time_range = st.slider(
            "Restrict time range?",
                    value = (222.00,337.01),
                    max_value = 337.01,
                    min_value = 222.00)
                    
                    
                    df_mask = df.mask(df["Year"] < date_range[0])
                    df_mask = df_mask.mask(df_mask["Year"] > date_range[1])
                    df_mask = df_mask.mask(df_mask["Bronze_Seconds"] < time_range[0])
                    df_mask = df_mask.mask(df_mask["Bronze_Seconds"] > time_range[1])
                    df_mask = df_mask.mask(df_mask["Silver_Seconds"] < time_range[0])
                    df_mask = df_mask.mask(df_mask["Silver_Seconds"] > time_range[1])
                    df_mask = df_mask.mask(df_mask["Gold_Seconds"] < time_range[0])
                    df_mask = df_mask.mask(df_mask["Gold_Seconds"] > time_range[1])
                    fig = px.scatter(df_mask, x="Year", y = ["Bronze_Seconds","Silver_Seconds","Gold_Seconds"], title="Men's Team Pursuit Olympic Medal Winning Time Progression",labels={"value":"Seconds"},trendline="ols", color_discrete_sequence=['darkorange',"silver","gold"])
                    customdata = np.stack((round(df_mask['Bronze_Seconds'],3), round(df_mask['Silver_Seconds'],3),round(df_mask['Gold_Seconds'],3),df_mask['Year']), axis=-1)
                    hovertemplate = ('Bronze: %{customdata[0]}<br>' + 'Silver: %{customdata[1]}<br>' + 'Gold: %{customdata[2]}<br>' +
                'Year: %{customdata[3]}<br>' 
                '<extra></extra>')
                    fig.update_traces(customdata=customdata, hovertemplate=hovertemplate)
                    
                    st.plotly_chart(fig, use_container_width=True)
                    col1,col2=st.columns(2)
                    with col1:
                        bronze_a=px.get_trendline_results(fig).px_fit_results.iloc[0].rsquared
                        bronze_const = px.get_trendline_results(fig).px_fit_results.iloc[0].params[0]
                        bronze_x1=px.get_trendline_results(fig).px_fit_results.iloc[0].params[1]
                        silver_a=px.get_trendline_results(fig).px_fit_results.iloc[1].rsquared
                        silver_const = px.get_trendline_results(fig).px_fit_results.iloc[1].params[0]
                        silver_x1=px.get_trendline_results(fig).px_fit_results.iloc[1].params[1]
                        gold_a=px.get_trendline_results(fig).px_fit_results.iloc[2].rsquared
                        gold_const = px.get_trendline_results(fig).px_fit_results.iloc[2].params[0]
                        gold_x1=px.get_trendline_results(fig).px_fit_results.iloc[2].params[1]
                        st.write(f"Bronze time = {round(bronze_x1,6)}(Year) + {round(bronze_const,3)}")
                        st.write(f"R-squared = {round(bronze_a,3)}")
                        st.write(f"Silver time = {round(silver_x1,6)}(Year) + {round(silver_const,3)}")
                        st.write(f"R-squared = {round(silver_a,3)}")
                        st.write(f"Gold time = {round(gold_x1,6)}(Year) + {round(gold_const,3)}")
                        st.write(f"R-squared = {round(gold_a,3)}")
                    with col2:
                        predict_year = st.selectbox("Select year for medal predictions:", [2024,2028,2032,2036,2040,2044,2048])
                        
                        
                    
        
                        bronze_m, bronze_s = divmod(bronze_x1*predict_year +bronze_const, 60)
                        bronze_h, bronze_m = divmod(bronze_m, 60)
                        bronze_m = int(bronze_m)
                        bronze_s=round(bronze_s,3)
                        if bronze_s<10:
                            bronze_s="0"+str(bronze_s)           
                        st.write(f"This trend predicts a Bronze medal winning time of {bronze_m}:{bronze_s} in {predict_year}.")
                        silver_m, silver_s = divmod(silver_x1*predict_year +silver_const, 60)
                        silver_h, silver_m = divmod(silver_m, 60)
                        silver_m = int(silver_m)
                        silver_s=round(silver_s,3)
                        if silver_s<10:
                            silver_s="0"+str(silver_s)           
                        st.write(f"This trend predicts a Silver medal winning time of {silver_m}:{silver_s} in {predict_year}.")
                        gold_m, gold_s = divmod(gold_x1*predict_year +gold_const, 60)
                        gold_h, gold_m = divmod(gold_m, 60)
                        gold_m = int(gold_m)
                        gold_s=round(gold_s,3)
                        if gold_s<10:
                            gold_s="0"+str(gold_s)           
                        st.write(f"This trend predicts a Gold medal winning time of {gold_m}:{gold_s} in {predict_year}.")
        
        
        
    
    
    
    







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
            fig = px.scatter(df_mask, x="DateSerial", y = "Seconds", title="Women's Team Pursuit World Record Progression",labels={"value":"Splits (seconds)"},trendline="ols",trendline_color_override="red")
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