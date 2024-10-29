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
    race_types=["Men's Sprint Qualifying","Women's Sprint Qualifying","Men's Team Sprint","Women's Team Sprint","Men's Team Pursuit","Women's Team Pursuit","Men's Individual Pursuit","Women's Individual Pursuit","Junior Men's Sprint Qualifying","Junior Women's Sprint Qualifying","Junior Men's Team Sprint","Junior Women's Team Sprint","Junior Men's Team Pursuit","Junior Women's Team Pursuit","Junior Men's Individual Pursuit","Junior Women's Individual Pursuit","Junior Men's Kilo","Junior Women's 500TT"]
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
            trend = st.selectbox("WR or Placings trend?:", ["World Record progression","Placing progression - raw times","Placing progression - % of win time"], key="MSP trend type Selector")
            

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


                
                
              
            elif trend=="Placing progression - raw times":
                df = get_placing_data_from_excel()
                df_master=df
                df_show=df
                comp = st.selectbox("Which competitions?", ["OLY and WCH","Just OLY", "Just WCH"], key="MSP comp type Selector")
                if comp == "Just OLY":
                        df_show=df_show.loc[df_show["Competition"]=="OLY"]
                elif comp == "Just WCH":
                        df_show=df_show.loc[df_show["Competition"]=="WCH"]
                df=df_show
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
                    value = (2000,2024),
                        min_value = 2000,
                        max_value = 2021)
                    
                    time_range = st.slider(
            "Restrict time range?",
                    value = (9.088,11.000),
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

                        
                        
            elif trend=="Placing progression - % of win time":
                df = get_placing_data_from_excel()
                df_master=df
                
                df["2nd %"]=df["2nd"]/df["1st"]
                df["3rd %"]=df["3rd"]/df["1st"]
                df["8th %"]=df["8th"]/df["1st"]
                df["16th %"]=df["16th"]/df["1st"]
                df_show=df
                comp = st.selectbox("Which competitions?", ["OLY and WCH","Just OLY", "Just WCH"], key="MSP comp type Selector")
                if comp == "Just OLY":
                        df_show=df_show.loc[df_show["Competition"]=="OLY"]
                elif comp == "Just WCH":
                        df_show=df_show.loc[df_show["Competition"]=="WCH"]
                df=df_show
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
                    value = (2000,2024),
                        min_value = 2000,
                        max_value = 2021)
                    
                    time_range = st.slider(
            "Restrict time range?",
                    value = (9.088,11.000),
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
                    
                    
                    fig_diffs = px.scatter(df_mask, x="Year", y = ["2nd %","3rd %","8th %","16th %"], title="% of winning time for minor placings",labels={"value":"% of win time"},trendline="ols", color_discrete_sequence=["silver","darkorange","lightpink","teal"])
                    customdata = np.stack((round(df_mask['2nd %'],3),round(df_mask['3rd %'],3), round(df_mask['8th %'],3),round(df_mask['16th %'],3),df_mask['Year'], df_mask['Competition']),axis=-1)
                    hovertemplate = ('Silver %: %{customdata[0]}<br>' + 'Bronze %: %{customdata[1]}<br>' + '8th %: %{customdata[2]}<br>' + '16th %: %{customdata[3]}<br>' +
                'Year: %{customdata[4]}<br>' +
                'Competition: %{customdata[5]}<br>'
                '<extra></extra>')
                    fig_diffs.update_traces(customdata=customdata, hovertemplate=hovertemplate)
                    
                    st.plotly_chart(fig_diffs, use_container_width=True)
                    col1,col2=st.columns(2)
                    with col1:
                        first_a=px.get_trendline_results(fig).px_fit_results.iloc[0].rsquared
                        first_const = px.get_trendline_results(fig).px_fit_results.iloc[0].params[0]
                        first_x1=px.get_trendline_results(fig).px_fit_results.iloc[0].params[1]
                        
                        second_a=px.get_trendline_results(fig_diffs).px_fit_results.iloc[0].rsquared
                        second_const = px.get_trendline_results(fig_diffs).px_fit_results.iloc[0].params[0]
                        second_x1=px.get_trendline_results(fig_diffs).px_fit_results.iloc[0].params[1]
                        
                        third_a=px.get_trendline_results(fig_diffs).px_fit_results.iloc[1].rsquared
                        third_const = px.get_trendline_results(fig_diffs).px_fit_results.iloc[1].params[0]
                        third_x1=px.get_trendline_results(fig_diffs).px_fit_results.iloc[1].params[1]
                        
                        eigth_a=px.get_trendline_results(fig_diffs).px_fit_results.iloc[2].rsquared
                        eigth_const = px.get_trendline_results(fig_diffs).px_fit_results.iloc[2].params[0]
                        eigth_x1=px.get_trendline_results(fig_diffs).px_fit_results.iloc[2].params[1]
                        
                        sixteenth_a=px.get_trendline_results(fig_diffs).px_fit_results.iloc[3].rsquared
                        sixteenth_const = px.get_trendline_results(fig_diffs).px_fit_results.iloc[3].params[0]
                        sixteenth_x1=px.get_trendline_results(fig_diffs).px_fit_results.iloc[3].params[1]
                        
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
                        second_s=round(second_s*float(first_s),3)
                        if second_s<10:
                            second_s="0"+str(second_s)           
                        st.write(f"This trend predicts a second qualifying time of {second_s} in {predict_year}.")

                        third_m, third_s = divmod(third_x1*predict_year +third_const, 60)
                        third_h, third_m = divmod(third_m, 60)
                        third_m = int(third_m)
                        third_s=round(third_s*float(first_s),3)
                        if third_s<10:
                            third_s="0"+str(third_s)           
                        st.write(f"This trend predicts a third qualifying time of {third_s} in {predict_year}.")
        
        
            
                        eigth_m, eigth_s = divmod(eigth_x1*predict_year +eigth_const, 60)
                        eigth_h, eigth_m = divmod(eigth_m, 60)
                        eigth_m = int(eigth_m)
                        eigth_s=round(eigth_s*float(first_s),3)
                        if eigth_s<10:
                            eigth_s="0"+str(eigth_s)           
                        st.write(f"This trend predicts a eigth qualifying time of {eigth_s} in {predict_year}.")

                        sixteenth_m, sixteenth_s = divmod(sixteenth_x1*predict_year +sixteenth_const, 60)
                        sixteenth_h, sixteenth_m = divmod(sixteenth_m, 60)
                        sixteenth_m = int(sixteenth_m)
                        sixteenth_s=round(sixteenth_s*float(first_s),3)
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
            trend = st.selectbox("WR or Placings trend?:", ["World Record progression","Placing progression - raw time","Placing progression - % of win time"], key="WSP trend type Selector")

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


                
                
              
            elif trend=="Placing progression - raw time":
                df = get_placing_data_from_excel()
                df_master=df
                df_show=df
                comp = st.selectbox("Which competitions?", ["OLY and WCH","Just OLY", "Just WCH"], key="MSP comp type Selector")
                if comp == "Just OLY":
                        df_show=df_show.loc[df_show["Competition"]=="OLY"]
                elif comp == "Just WCH":
                        df_show=df_show.loc[df_show["Competition"]=="WCH"]
                df=df_show
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
                    value = (2000,2024),
                        min_value = 2000,
                        max_value = 2024)
                    
                    time_range = st.slider(
            "Restrict time range?",
                    value = (10.029,12.200),
                        max_value = 12.200,
                        min_value = 10.029)
                    
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







            elif trend=="Placing progression - % of win time":
                df = get_placing_data_from_excel()
                df_master=df
                df["2nd %"]=df["2nd"]/df["1st"]
                df["3rd %"]=df["3rd"]/df["1st"]
                df["8th %"]=df["8th"]/df["1st"]
                df["16th %"]=df["16th"]/df["1st"]
                df_show=df
                comp = st.selectbox("Which competitions?", ["OLY and WCH","Just OLY", "Just WCH"], key="MSP comp type Selector")
                if comp == "Just OLY":
                        df_show=df_show.loc[df_show["Competition"]=="OLY"]
                elif comp == "Just WCH":
                        df_show=df_show.loc[df_show["Competition"]=="WCH"]
                df=df_show
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
                    value = (2000,2024),
                        min_value = 2000,
                        max_value = 2024)
                    
                    time_range = st.slider(
            "Restrict time range?",
                    value = (10.029,12.200),
                        max_value = 12.200,
                        min_value = 10.029)
                    
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
                    
                    
                    fig_diffs = px.scatter(df_mask, x="Year", y = ["2nd %","3rd %","8th %","16th %"], title="% of winning time for minor placings",labels={"value":"% of win time"},trendline="ols", color_discrete_sequence=["silver","darkorange","lightpink","teal"])
                    customdata = np.stack((round(df_mask['2nd %'],3),round(df_mask['3rd %'],3), round(df_mask['8th %'],3),round(df_mask['16th %'],3),df_mask['Year'], df_mask['Competition']),axis=-1)
                    hovertemplate = ('Silver %: %{customdata[0]}<br>' + 'Bronze %: %{customdata[1]}<br>' + '8th %: %{customdata[2]}<br>' + '16th %: %{customdata[3]}<br>' +
                'Year: %{customdata[4]}<br>' +
                'Competition: %{customdata[5]}<br>'
                '<extra></extra>')
                    fig_diffs.update_traces(customdata=customdata, hovertemplate=hovertemplate)
                    
                    st.plotly_chart(fig_diffs, use_container_width=True)
                    col1,col2=st.columns(2)
                    with col1:
                        first_a=px.get_trendline_results(fig).px_fit_results.iloc[0].rsquared
                        first_const = px.get_trendline_results(fig).px_fit_results.iloc[0].params[0]
                        first_x1=px.get_trendline_results(fig).px_fit_results.iloc[0].params[1]
                        
                        second_a=px.get_trendline_results(fig_diffs).px_fit_results.iloc[0].rsquared
                        second_const = px.get_trendline_results(fig_diffs).px_fit_results.iloc[0].params[0]
                        second_x1=px.get_trendline_results(fig_diffs).px_fit_results.iloc[0].params[1]
                        
                        third_a=px.get_trendline_results(fig_diffs).px_fit_results.iloc[1].rsquared
                        third_const = px.get_trendline_results(fig_diffs).px_fit_results.iloc[1].params[0]
                        third_x1=px.get_trendline_results(fig_diffs).px_fit_results.iloc[1].params[1]
                        
                        eigth_a=px.get_trendline_results(fig_diffs).px_fit_results.iloc[2].rsquared
                        eigth_const = px.get_trendline_results(fig_diffs).px_fit_results.iloc[2].params[0]
                        eigth_x1=px.get_trendline_results(fig_diffs).px_fit_results.iloc[2].params[1]
                        
                        sixteenth_a=px.get_trendline_results(fig_diffs).px_fit_results.iloc[3].rsquared
                        sixteenth_const = px.get_trendline_results(fig_diffs).px_fit_results.iloc[3].params[0]
                        sixteenth_x1=px.get_trendline_results(fig_diffs).px_fit_results.iloc[3].params[1]
                        
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
                        second_s=round(second_s*float(first_s),3)
                        if second_s<10:
                            second_s="0"+str(second_s)           
                        st.write(f"This trend predicts a second qualifying time of {second_s} in {predict_year}.")

                        third_m, third_s = divmod(third_x1*predict_year +third_const, 60)
                        third_h, third_m = divmod(third_m, 60)
                        third_m = int(third_m)
                        third_s=round(third_s*float(first_s),3)
                        if third_s<10:
                            third_s="0"+str(third_s)           
                        st.write(f"This trend predicts a third qualifying time of {third_s} in {predict_year}.")
        
        
            
                        eigth_m, eigth_s = divmod(eigth_x1*predict_year +eigth_const, 60)
                        eigth_h, eigth_m = divmod(eigth_m, 60)
                        eigth_m = int(eigth_m)
                        eigth_s=round(eigth_s*float(first_s),3)
                        if eigth_s<10:
                            eigth_s="0"+str(eigth_s)           
                        st.write(f"This trend predicts a eigth qualifying time of {eigth_s} in {predict_year}.")

                        sixteenth_m, sixteenth_s = divmod(sixteenth_x1*predict_year +sixteenth_const, 60)
                        sixteenth_h, sixteenth_m = divmod(sixteenth_m, 60)
                        sixteenth_m = int(sixteenth_m)
                        sixteenth_s=round(sixteenth_s*float(first_s),3)
                        if sixteenth_s<10:
                            sixteenth_s="0"+str(sixteenth_s)           
                        st.write(f"This trend predicts a sixteenth qualifying time of {sixteenth_s} in {predict_year}.")















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
                usecols='A:F',
                nrows=30
                )
            #df = df.replace(',','')
       

            return df
        
        c1,c2=st.columns([1,3])
        with c1:
            trend = st.selectbox("WR or Medal trend?:", ["World Record progression","Medal progression - raw time","Medal progression - % of win time"], key="MTS trend type Selector")

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
        

            elif trend=="Medal progression - raw time":
                df= get_medal_data_from_excel()
                df_master=df
                df_show = df
                comp = st.selectbox("Which competitions?", ["OLY and WCH","Just OLY", "Just WCH"], key="MSP comp type Selector")
                if comp == "Just OLY":
                        df_show=df_show.loc[df_show["Competition"]=="OLY"]
                elif comp == "Just WCH":
                        df_show=df_show.loc[df_show["Competition"]=="WCH"]
                df=df_show
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
                    value = (2000,2024),
                        min_value = 2000,
                        max_value = 2023)
                    
                    time_range = st.slider(
            "Restrict time range?",
                    value = (41.279,45.161),
                        max_value = 45.161,
                        min_value = 41.279)
                    
                    df_mask = df.mask(df["Year"] < date_range[0])
                    df_mask = df_mask.mask(df_mask["Year"] > date_range[1])
                    df_mask = df_mask.mask(df_mask["3rd"] < time_range[0])
                    df_mask = df_mask.mask(df_mask["3rd"] > time_range[1])
                    df_mask = df_mask.mask(df_mask["2nd"] < time_range[0])
                    df_mask = df_mask.mask(df_mask["2nd"] > time_range[1])
                    df_mask = df_mask.mask(df_mask["1st"] < time_range[0])
                    df_mask = df_mask.mask(df_mask["1st"] > time_range[1])
                    df_mask = df_mask.mask(df_mask["8th"] < time_range[0])
                    df_mask = df_mask.mask(df_mask["8th"] > time_range[1])
                    fig = px.scatter(df_mask, x="Year", y = ["1st","2nd","3rd","8th"], title="Men's Team Sprint Olympic and World Champs Qualifying Time Progression",labels={"value":"Seconds"},trendline="ols", color_discrete_sequence=['gold',"silver","darkorange","lightgreen"])
                    customdata = np.stack((round(df_mask['1st'],3), round(df_mask['2nd'],3),round(df_mask['3rd'],3),round(df_mask['8th'],3),df_mask['Year'], df_mask['Competition']),axis=-1)
                    hovertemplate = ('1st: %{customdata[0]}<br>' + '2nd: %{customdata[1]}<br>' + '3rd: %{customdata[2]}<br>' + '4th: %{customdata[3]}<br>'+
                'Year: %{customdata[4]}<br>' +
                'Comp: %{customdata[5]}<br>'
                '<extra></extra>')
                    fig.update_traces(customdata=customdata, hovertemplate=hovertemplate)
                    
                    st.plotly_chart(fig, use_container_width=True)
                    col1,col2=st.columns(2)
                    with col1:
                        third_a=px.get_trendline_results(fig).px_fit_results.iloc[2].rsquared
                        third_const = px.get_trendline_results(fig).px_fit_results.iloc[2].params[0]
                        third_x1=px.get_trendline_results(fig).px_fit_results.iloc[2].params[1]
                        second_a=px.get_trendline_results(fig).px_fit_results.iloc[1].rsquared
                        second_const = px.get_trendline_results(fig).px_fit_results.iloc[1].params[0]
                        second_x1=px.get_trendline_results(fig).px_fit_results.iloc[1].params[1]
                        first_a=px.get_trendline_results(fig).px_fit_results.iloc[0].rsquared
                        first_const = px.get_trendline_results(fig).px_fit_results.iloc[0].params[0]
                        first_x1=px.get_trendline_results(fig).px_fit_results.iloc[0].params[1]
                        eigth_a=px.get_trendline_results(fig).px_fit_results.iloc[3].rsquared
                        eigth_const = px.get_trendline_results(fig).px_fit_results.iloc[3].params[0]
                        eigth_x1=px.get_trendline_results(fig).px_fit_results.iloc[3].params[1]


                        st.write(f"Top qual = {round(first_x1,6)}(Year) + {round(first_const,3)}")
                        st.write(f"R-squared = {round(first_a,3)}")
                        st.write(f"2nd qual = {round(second_x1,6)}(Year) + {round(second_const,3)}")
                        st.write(f"R-squared = {round(second_a,3)}")
                        st.write(f"3rd qual = {round(third_x1,6)}(Year) + {round(third_const,3)}")
                        st.write(f"R-squared = {round(third_a,3)}")
                        st.write(f"8th qual = {round(eigth_x1,6)}(Year) + {round(eigth_const,3)}")
                        st.write(f"R-squared = {round(eigth_a,3)}")                        
                    with col2:
                        predict_year = st.selectbox("Select year for qualifying predictions:", [2024,2028,2032,2036,2040,2044,2048])
                        
                        
                    
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
                        st.write(f"This trend predicts a 2nd qualifying time of {second_s} in {predict_year}.")

                        third_m, third_s = divmod(third_x1*predict_year +third_const, 60)
                        third_h, third_m = divmod(third_m, 60)
                        third_m = int(third_m)
                        third_s=round(third_s,3)
                        if third_s<10:
                            third_s="0"+str(third_s)           
                        st.write(f"This trend predicts a 3rd qualifying time of {third_s} in {predict_year}.")   
                    
                        eigth_m, eigth_s = divmod(eigth_x1*predict_year +eigth_const, 60)
                        eigth_h, eigth_m = divmod(eigth_m, 60)
                        eigth_m = int(eigth_m)
                        eigth_s=round(eigth_s,3)
                        if eigth_s<10:
                            eigth_s="0"+str(eigth_s)           
                        st.write(f"This trend predicts an 8th qualifying time of {eigth_s} in {predict_year}.") 
        
        
        
        
        
            elif trend=="Medal progression - % of win time":
                df= get_medal_data_from_excel()
                df_master=df
                df["2nd %"]=df["2nd"]/df["1st"]
                df["3rd %"]=df["3rd"]/df["1st"]
                df["8th %"]=df["8th"]/df["1st"]
                df_show = df
                comp = st.selectbox("Which competitions?", ["OLY and WCH","Just OLY", "Just WCH"], key="MSP comp type Selector")
                if comp == "Just OLY":
                        df_show=df_show.loc[df_show["Competition"]=="OLY"]
                elif comp == "Just WCH":
                        df_show=df_show.loc[df_show["Competition"]=="WCH"]
                df=df_show
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
                    value = (2000,2024),
                        min_value = 2000,
                        max_value = 2023)
                    
                    time_range = st.slider(
            "Restrict time range?",
                    value = (41.279,45.161),
                        max_value = 45.161,
                        min_value = 41.279)
                    
                    df_mask = df.mask(df["Year"] < date_range[0])
                    df_mask = df_mask.mask(df_mask["Year"] > date_range[1])
                    df_mask = df_mask.mask(df_mask["3rd"] < time_range[0])
                    df_mask = df_mask.mask(df_mask["3rd"] > time_range[1])
                    df_mask = df_mask.mask(df_mask["2nd"] < time_range[0])
                    df_mask = df_mask.mask(df_mask["2nd"] > time_range[1])
                    df_mask = df_mask.mask(df_mask["1st"] < time_range[0])
                    df_mask = df_mask.mask(df_mask["1st"] > time_range[1])
                    df_mask = df_mask.mask(df_mask["8th"] < time_range[0])
                    df_mask = df_mask.mask(df_mask["8th"] > time_range[1])
                    fig = px.scatter(df_mask, x="Year", y = ["1st","2nd","3rd","8th"], title="Men's Team Sprint Olympic and World Champs Qualifying Time Progression",labels={"value":"Seconds"},trendline="ols", color_discrete_sequence=['gold',"silver","darkorange","lightgreen"])
                    customdata = np.stack((round(df_mask['1st'],3), round(df_mask['2nd'],3),round(df_mask['3rd'],3),round(df_mask['8th'],3),df_mask['Year'], df_mask['Competition']),axis=-1)
                    hovertemplate = ('1st: %{customdata[0]}<br>' + '2nd: %{customdata[1]}<br>' + '3rd: %{customdata[2]}<br>' + '4th: %{customdata[3]}<br>'+
                'Year: %{customdata[4]}<br>' +
                'Comp: %{customdata[5]}<br>'
                '<extra></extra>')
                    fig.update_traces(customdata=customdata, hovertemplate=hovertemplate)
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    fig_diffs = px.scatter(df_mask, x="Year", y = ["2nd %","3rd %","8th %"], title="% of winning time",labels={"value":"Seconds"},trendline="ols", color_discrete_sequence=["silver","darkorange","lightgreen"])
                    customdata = np.stack((round(df_mask['2nd %'],3),round(df_mask['3rd %'],3),round(df_mask['8th %'],3),df_mask['Year'], df_mask['Competition']),axis=-1)
                    hovertemplate = ('2nd %: %{customdata[0]}<br>' + '3rd %: %{customdata[1]}<br>' + '8th %: %{customdata[2]}<br>'+
                'Year: %{customdata[3]}<br>' +
                'Comp: %{customdata[4]}<br>'
                '<extra></extra>')
                    fig_diffs.update_traces(customdata=customdata, hovertemplate=hovertemplate)
                    
                    st.plotly_chart(fig_diffs, use_container_width=True)
                    col1,col2=st.columns(2)
                    with col1:
                        first_a=px.get_trendline_results(fig).px_fit_results.iloc[0].rsquared
                        first_const = px.get_trendline_results(fig).px_fit_results.iloc[0].params[0]
                        first_x1=px.get_trendline_results(fig).px_fit_results.iloc[0].params[1]
                        second_a=px.get_trendline_results(fig_diffs).px_fit_results.iloc[0].rsquared
                        second_const = px.get_trendline_results(fig_diffs).px_fit_results.iloc[0].params[0]
                        second_x1=px.get_trendline_results(fig_diffs).px_fit_results.iloc[0].params[1]                        
                        third_a=px.get_trendline_results(fig_diffs).px_fit_results.iloc[1].rsquared
                        third_const = px.get_trendline_results(fig_diffs).px_fit_results.iloc[1].params[0]
                        third_x1=px.get_trendline_results(fig_diffs).px_fit_results.iloc[1].params[1]
                        eigth_a=px.get_trendline_results(fig_diffs).px_fit_results.iloc[2].rsquared
                        eigth_const = px.get_trendline_results(fig_diffs).px_fit_results.iloc[2].params[0]
                        eigth_x1=px.get_trendline_results(fig_diffs).px_fit_results.iloc[2].params[1]


                        st.write(f"Top qual = {round(first_x1,6)}(Year) + {round(first_const,3)}")
                        st.write(f"R-squared = {round(first_a,3)}")
                        st.write(f"2nd qual = {round(second_x1,6)}(Year) + {round(second_const,3)}")
                        st.write(f"R-squared = {round(second_a,3)}")
                        st.write(f"3rd qual = {round(third_x1,6)}(Year) + {round(third_const,3)}")
                        st.write(f"R-squared = {round(third_a,3)}")
                        st.write(f"8th qual = {round(eigth_x1,6)}(Year) + {round(eigth_const,3)}")
                        st.write(f"R-squared = {round(eigth_a,3)}")                        
                    with col2:
                        predict_year = st.selectbox("Select year for qualifying predictions:", [2024,2028,2032,2036,2040,2044,2048])
                        
                        
                    
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
                        second_s=round(second_s*first_s,3)
                        if second_s<10:
                            second_s="0"+str(second_s)           
                        st.write(f"This trend predicts a 2nd qualifying time of {second_s} in {predict_year}.")

                        third_m, third_s = divmod(third_x1*predict_year +third_const, 60)
                        third_h, third_m = divmod(third_m, 60)
                        third_m = int(third_m)
                        third_s=round(third_s*first_s,3)
                        if third_s<10:
                            third_s="0"+str(third_s)           
                        st.write(f"This trend predicts a 3rd qualifying time of {third_s} in {predict_year}.")   
                    
                        eigth_m, eigth_s = divmod(eigth_x1*predict_year +eigth_const, 60)
                        eigth_h, eigth_m = divmod(eigth_m, 60)
                        eigth_m = int(eigth_m)
                        eigth_s=round(eigth_s*first_s,3)
                        if eigth_s<10:
                            eigth_s="0"+str(eigth_s)           
                        st.write(f"This trend predicts an 8th qualifying time of {eigth_s} in {predict_year}.") 

        
    if race_type=="Women's Team Sprint":
            @st.cache_data
            def get_wr_data_from_excel():
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

            def get_medal_data_from_excel():
                df = pd.read_excel(
                    io='pages/WR_progressions/Medals_Women_TS.xlsx',
                    engine ='openpyxl',
                    sheet_name='Sheet1',
                    skiprows=0,
                    usecols='A:F',
                    nrows=30
                    )
                #df = df.replace(',','')


                return df

            c1,c2=st.columns([1,3])
            with c1:
                trend = st.selectbox("WR or Medal trend?:", ["World Record progression","Medal progression - raw time","Medal progression - % of win time"], key="trend type Selector")

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
                        label="Download Women TS data as CSV",
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
                            label="Download Women TS data as Excel",
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


                elif trend=="Medal progression - raw time":
                    df= get_medal_data_from_excel()
                    df_master=df
                    df_show = df
                    comp = st.selectbox("Which competitions?", ["OLY and WCH","Just OLY", "Just WCH"], key="MSP comp type Selector")
                    if comp == "Just OLY":
                            df_show=df_show.loc[df_show["Competition"]=="OLY"]
                    elif comp == "Just WCH":
                            df_show=df_show.loc[df_show["Competition"]=="WCH"]
                    df=df_show
                    df_show

                    ##Download buttons
                    def convert_to_csv(df_show):
                        return df.to_csv(index=False,sep = ",").encode('utf-32')
                    csv = convert_to_csv(df_show)
                    download1 = st.download_button(
                        label="Download Women TS data as CSV",
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
                            label="Download Women TS data as Excel",
                            data=buffer_tt,
                            file_name='Women_TS_Data.xlsx',
                            mime='application/vnd.ms-excel',
                            key="buffertt2"
                        )
                    ##Download buttons complete


                    with c2:
                        date_range = st.slider(
                "Restrict date range?",
                        value = (2021,2024),
                            min_value = 2021,
                            max_value = 2023)

                        time_range = st.slider(
                "Restrict time range?",
                        value = (45.472,55.653),
                            max_value = 55.653,
                            min_value = 45.472)

                        df_mask = df.mask(df["Year"] < date_range[0])
                        df_mask = df_mask.mask(df_mask["Year"] > date_range[1])
                        df_mask = df_mask.mask(df_mask["3rd"] < time_range[0])
                        df_mask = df_mask.mask(df_mask["3rd"] > time_range[1])
                        df_mask = df_mask.mask(df_mask["2nd"] < time_range[0])
                        df_mask = df_mask.mask(df_mask["2nd"] > time_range[1])
                        df_mask = df_mask.mask(df_mask["1st"] < time_range[0])
                        df_mask = df_mask.mask(df_mask["1st"] > time_range[1])
                        df_mask = df_mask.mask(df_mask["8th"] < time_range[0])
                        df_mask = df_mask.mask(df_mask["8th"] > time_range[1])
                        fig = px.scatter(df_mask, x="Year", y = ["1st","2nd","3rd","8th"], title="Women's Team Sprint Olympic and World Champs Qualifying Time Progression",labels={"value":"Seconds"},trendline="ols", color_discrete_sequence=['gold',"silver","darkorange","lightgreen"])
                        customdata = np.stack((round(df_mask['1st'],3), round(df_mask['2nd'],3),round(df_mask['3rd'],3),round(df_mask['8th'],3),df_mask['Year'], df_mask['Competition']),axis=-1)
                        hovertemplate = ('1st: %{customdata[0]}<br>' + '2nd: %{customdata[1]}<br>' + '3rd: %{customdata[2]}<br>' + '4th: %{customdata[3]}<br>'+
                    'Year: %{customdata[4]}<br>' +
                    'Comp: %{customdata[5]}<br>'
                    '<extra></extra>')
                        fig.update_traces(customdata=customdata, hovertemplate=hovertemplate)

                        st.plotly_chart(fig, use_container_width=True)
                        col1,col2=st.columns(2)
                        with col1:
                            third_a=px.get_trendline_results(fig).px_fit_results.iloc[2].rsquared
                            third_const = px.get_trendline_results(fig).px_fit_results.iloc[2].params[0]
                            third_x1=px.get_trendline_results(fig).px_fit_results.iloc[2].params[1]
                            second_a=px.get_trendline_results(fig).px_fit_results.iloc[1].rsquared
                            second_const = px.get_trendline_results(fig).px_fit_results.iloc[1].params[0]
                            second_x1=px.get_trendline_results(fig).px_fit_results.iloc[1].params[1]
                            first_a=px.get_trendline_results(fig).px_fit_results.iloc[0].rsquared
                            first_const = px.get_trendline_results(fig).px_fit_results.iloc[0].params[0]
                            first_x1=px.get_trendline_results(fig).px_fit_results.iloc[0].params[1]
                            eigth_a=px.get_trendline_results(fig).px_fit_results.iloc[3].rsquared
                            eigth_const = px.get_trendline_results(fig).px_fit_results.iloc[3].params[0]
                            eigth_x1=px.get_trendline_results(fig).px_fit_results.iloc[3].params[1]


                            st.write(f"Top qual = {round(first_x1,6)}(Year) + {round(first_const,3)}")
                            st.write(f"R-squared = {round(first_a,3)}")
                            st.write(f"2nd qual = {round(second_x1,6)}(Year) + {round(second_const,3)}")
                            st.write(f"R-squared = {round(second_a,3)}")
                            st.write(f"3rd qual = {round(third_x1,6)}(Year) + {round(third_const,3)}")
                            st.write(f"R-squared = {round(third_a,3)}")
                            st.write(f"8th qual = {round(eigth_x1,6)}(Year) + {round(eigth_const,3)}")
                            st.write(f"R-squared = {round(eigth_a,3)}")                        
                        with col2:
                            predict_year = st.selectbox("Select year for qualifying predictions:", [2024,2028,2032,2036,2040,2044,2048])



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
                            st.write(f"This trend predicts a 2nd qualifying time of {second_s} in {predict_year}.")

                            third_m, third_s = divmod(third_x1*predict_year +third_const, 60)
                            third_h, third_m = divmod(third_m, 60)
                            third_m = int(third_m)
                            third_s=round(third_s,3)
                            if third_s<10:
                                third_s="0"+str(third_s)           
                            st.write(f"This trend predicts a 3rd qualifying time of {third_s} in {predict_year}.")   

                            eigth_m, eigth_s = divmod(eigth_x1*predict_year +eigth_const, 60)
                            eigth_h, eigth_m = divmod(eigth_m, 60)
                            eigth_m = int(eigth_m)
                            eigth_s=round(eigth_s,3)
                            if eigth_s<10:
                                eigth_s="0"+str(eigth_s)           
                            st.write(f"This trend predicts an 8th qualifying time of {eigth_s} in {predict_year}.") 





                elif trend=="Medal progression - % of win time":
                    df= get_medal_data_from_excel()
                    df_master=df
                    df["2nd %"]=df["2nd"]/df["1st"]
                    df["3rd %"]=df["3rd"]/df["1st"]
                    df["8th %"]=df["8th"]/df["1st"]
                    df_show = df
                    comp = st.selectbox("Which competitions?", ["OLY and WCH","Just OLY", "Just WCH"], key="MSP comp type Selector")
                    if comp == "Just OLY":
                            df_show=df_show.loc[df_show["Competition"]=="OLY"]
                    elif comp == "Just WCH":
                            df_show=df_show.loc[df_show["Competition"]=="WCH"]
                    df=df_show
                    df_show

                    ##Download buttons
                    def convert_to_csv(df_show):
                        return df.to_csv(index=False,sep = ",").encode('utf-32')
                    csv = convert_to_csv(df_show)
                    download1 = st.download_button(
                        label="Download Women TS data as CSV",
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
                            label="Download Women TS data as Excel",
                            data=buffer_tt,
                            file_name='Women_TS_Data.xlsx',
                            mime='application/vnd.ms-excel',
                            key="buffertt2"
                        )
                    ##Download buttons complete


                    with c2:
                        date_range = st.slider(
                "Restrict date range?",
                        value = (2021,2024),
                            min_value = 2021,
                            max_value = 2023)

                        time_range = st.slider(
                "Restrict time range?",
                        value = (45.472,55.653),
                            max_value = 55.653,
                            min_value = 45.472)

                        df_mask = df.mask(df["Year"] < date_range[0])
                        df_mask = df_mask.mask(df_mask["Year"] > date_range[1])
                        df_mask = df_mask.mask(df_mask["3rd"] < time_range[0])
                        df_mask = df_mask.mask(df_mask["3rd"] > time_range[1])
                        df_mask = df_mask.mask(df_mask["2nd"] < time_range[0])
                        df_mask = df_mask.mask(df_mask["2nd"] > time_range[1])
                        df_mask = df_mask.mask(df_mask["1st"] < time_range[0])
                        df_mask = df_mask.mask(df_mask["1st"] > time_range[1])
                        df_mask = df_mask.mask(df_mask["8th"] < time_range[0])
                        df_mask = df_mask.mask(df_mask["8th"] > time_range[1])
                        fig = px.scatter(df_mask, x="Year", y = ["1st","2nd","3rd","8th"], title="Women's Team Sprint Olympic and World Champs Qualifying Time Progression",labels={"value":"Seconds"},trendline="ols", color_discrete_sequence=['gold',"silver","darkorange","lightgreen"])
                        customdata = np.stack((round(df_mask['1st'],3), round(df_mask['2nd'],3),round(df_mask['3rd'],3),round(df_mask['8th'],3),df_mask['Year'], df_mask['Competition']),axis=-1)
                        hovertemplate = ('1st: %{customdata[0]}<br>' + '2nd: %{customdata[1]}<br>' + '3rd: %{customdata[2]}<br>' + '4th: %{customdata[3]}<br>'+
                    'Year: %{customdata[4]}<br>' +
                    'Comp: %{customdata[5]}<br>'
                    '<extra></extra>')
                        fig.update_traces(customdata=customdata, hovertemplate=hovertemplate)

                        st.plotly_chart(fig, use_container_width=True)
                        
                        
                        fig_diffs = px.scatter(df_mask, x="Year", y = ["2nd %","3rd %","8th %"], title="% of winning time",labels={"value":"% of win time"},trendline="ols", color_discrete_sequence=["silver","darkorange","lightgreen"])
                        customdata = np.stack((round(df_mask['2nd %'],3),round(df_mask['3rd %'],3),round(df_mask['8th %'],3),df_mask['Year'], df_mask['Competition']),axis=-1)
                        hovertemplate = ('2nd %: %{customdata[0]}<br>' + '3rd %: %{customdata[1]}<br>' + '8th %: %{customdata[2]}<br>'+
                    'Year: %{customdata[3]}<br>' +
                    'Comp: %{customdata[4]}<br>'
                    '<extra></extra>')
                        fig_diffs.update_traces(customdata=customdata, hovertemplate=hovertemplate)

                        st.plotly_chart(fig_diffs, use_container_width=True)
                        col1,col2=st.columns(2)
                        with col1:
                            first_a=px.get_trendline_results(fig).px_fit_results.iloc[0].rsquared
                            first_const = px.get_trendline_results(fig).px_fit_results.iloc[0].params[0]
                            first_x1=px.get_trendline_results(fig).px_fit_results.iloc[0].params[1]
                            second_a=px.get_trendline_results(fig_diffs).px_fit_results.iloc[0].rsquared
                            second_const = px.get_trendline_results(fig_diffs).px_fit_results.iloc[0].params[0]
                            second_x1=px.get_trendline_results(fig_diffs).px_fit_results.iloc[0].params[1]                        
                            third_a=px.get_trendline_results(fig_diffs).px_fit_results.iloc[1].rsquared
                            third_const = px.get_trendline_results(fig_diffs).px_fit_results.iloc[1].params[0]
                            third_x1=px.get_trendline_results(fig_diffs).px_fit_results.iloc[1].params[1]
                            eigth_a=px.get_trendline_results(fig_diffs).px_fit_results.iloc[2].rsquared
                            eigth_const = px.get_trendline_results(fig_diffs).px_fit_results.iloc[2].params[0]
                            eigth_x1=px.get_trendline_results(fig_diffs).px_fit_results.iloc[2].params[1]


                            st.write(f"Top qual = {round(first_x1,6)}(Year) + {round(first_const,3)}")
                            st.write(f"R-squared = {round(first_a,3)}")
                            st.write(f"2nd qual = {round(second_x1,6)}(Year) + {round(second_const,3)}")
                            st.write(f"R-squared = {round(second_a,3)}")
                            st.write(f"3rd qual = {round(third_x1,6)}(Year) + {round(third_const,3)}")
                            st.write(f"R-squared = {round(third_a,3)}")
                            st.write(f"8th qual = {round(eigth_x1,6)}(Year) + {round(eigth_const,3)}")
                            st.write(f"R-squared = {round(eigth_a,3)}")                        
                        with col2:
                            predict_year = st.selectbox("Select year for qualifying predictions:", [2024,2028,2032,2036,2040,2044,2048])



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
                            second_s=round(second_s*first_s,3)
                            if second_s<10:
                                second_s="0"+str(second_s)           
                            st.write(f"This trend predicts a 2nd qualifying time of {second_s} in {predict_year}.")

                            third_m, third_s = divmod(third_x1*predict_year +third_const, 60)
                            third_h, third_m = divmod(third_m, 60)
                            third_m = int(third_m)
                            third_s=round(third_s*first_s,3)
                            if third_s<10:
                                third_s="0"+str(third_s)           
                            st.write(f"This trend predicts a 3rd qualifying time of {third_s} in {predict_year}.")   

                            eigth_m, eigth_s = divmod(eigth_x1*predict_year +eigth_const, 60)
                            eigth_h, eigth_m = divmod(eigth_m, 60)
                            eigth_m = int(eigth_m)
                            eigth_s=round(eigth_s*first_s,3)
                            if eigth_s<10:
                                eigth_s="0"+str(eigth_s)           
                            st.write(f"This trend predicts an 8th qualifying time of {eigth_s} in {predict_year}.") 














    if race_type=="Men's Team Pursuit":
        @st.cache_data
        def get_wr_data_from_excel():
            df = pd.read_excel(
                io='pages/WR_progressions/Men_TP.xlsx',
                engine ='openpyxl',
                sheet_name='Sheet1',
                skiprows=0,
                usecols='A:D',
                nrows=100
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
                usecols='A:Q',
                nrows=100
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
                medal_or_qual = st.selectbox("Medal or Qual times:", ["Qual times","Medal times","Fastest time"], key="medal_or_qual_MTP")
                oly_or_wch = st.selectbox("Select competitions:", ["OLY and WCH","OLY only","WCH only"], key="mtp_comps")
                df=get_medal_data_from_excel()
                df_master=df
                if oly_or_wch == "OLY only":
                    df = df.loc[df["Event"]=="OLY"]
                elif oly_or_wch == "WCH only":
                    df = df.loc[df["Event"]=="WCH"]

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
    
                if medal_or_qual=="Medal times":
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
                        fig = px.scatter(df_mask, x="Year", y = ["Bronze_Seconds","Silver_Seconds","Gold_Seconds"], title="Men's Team Pursuit  Medal Winning Time Progression",labels={"value":"Seconds"},trendline="ols", color_discrete_sequence=['darkorange',"silver","gold"])
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
                            
                            #ERRORS
                            df_mask["Gold_Error"]=abs(df_mask["Gold_Seconds"]-((df_mask["Year"]*gold_x1) +gold_const))
                            df_mask["Silver_Error"]=abs(df_mask["Silver_Seconds"]-((df_mask["Year"]*silver_x1) +silver_const))
                            df_mask["Bronze_Error"]=abs(df_mask["Bronze_Seconds"]-((df_mask["Year"]*bronze_x1) +bronze_const))

                            gold_std=round(df_mask['Gold_Error'].std(),2)
                            silver_std=round(df_mask['Silver_Error'].std(),2)
                            bronze_std=round(df_mask['Bronze_Error'].std(),2)
        
                            st.write(f"Gold time = {round(gold_x1,6)}(Year) + {round(gold_const,3)}")
                            st.write(f"One standard deviation of the absolute errors is {gold_std} seconds")
                            st.write(f"R-squared = {round(gold_a,3)}")
                            st.write(f"Silver time = {round(silver_x1,6)}(Year) + {round(silver_const,3)}")
                            st.write(f"One standard deviation of the absolute errors is {silver_std} seconds")
                            st.write(f"R-squared = {round(silver_a,3)}")
                            st.write(f"Bronze time = {round(bronze_x1,6)}(Year) + {round(bronze_const,3)}")
                            st.write(f"One standard deviation of the absolute errors is {bronze_std} seconds")
                            st.write(f"R-squared = {round(bronze_a,3)}")
                        with col2:
                            if oly_or_wch == "OLY only":
                                predict_year = st.selectbox("Select year for fastest time prediction:", [2024,2028,2032,2036,2040,2044,2048])
                                
                            else:
                                predict_year = st.number_input("Select year for fastest time prediction:",min_value=2020,max_value=3000,value=2024,step=1)




                            bronze_m, bronze_s = divmod(bronze_x1*predict_year +bronze_const, 60)
                            bronze_h, bronze_m = divmod(bronze_m, 60)
                            bronze_m = int(bronze_m)
                            bronze_s=round(bronze_s,3)
                            if bronze_s<10:
                                bronze_s="0"+str(bronze_s)   
                                
                            bronze_m_lower, bronze_s_lower = divmod(bronze_x1*predict_year +bronze_const - 1.15*bronze_std, 60)
                            bronze_h_lower, bronze_m_lower = divmod(bronze_m_lower, 60)
                            bronze_m_lower = int(bronze_m_lower)
                            bronze_s_lower=round(bronze_s_lower,3)
                            if bronze_s_lower<10:
                                bronze_s_lower="0"+str(bronze_s_lower)  
                                
                            bronze_m_higher, bronze_s_higher = divmod(bronze_x1*predict_year +bronze_const +1.15*bronze_std, 60)
                            bronze_h_higher, bronze_m_higher = divmod(bronze_m_higher, 60)
                            bronze_m_higher = int(bronze_m_higher)
                            bronze_s_higher=round(bronze_s_higher,3)
                            if bronze_s_higher<10:
                                bronze_s_higher="0"+str(bronze_s_higher)  

                            
                            silver_m, silver_s = divmod(silver_x1*predict_year +silver_const, 60)
                            silver_h, silver_m = divmod(silver_m, 60)
                            silver_m = int(silver_m)
                            silver_s=round(silver_s,3)
                            if silver_s<10:
                                silver_s="0"+str(silver_s)   
                                
                            silver_m_lower, silver_s_lower = divmod(silver_x1*predict_year +silver_const - 1.15*silver_std, 60)
                            silver_h_lower, silver_m_lower = divmod(silver_m_lower, 60)
                            silver_m_lower = int(silver_m_lower)
                            silver_s_lower=round(silver_s_lower,3)
                            if silver_s_lower<10:
                                silver_s_lower="0"+str(silver_s_lower)  
                                
                            silver_m_higher, silver_s_higher = divmod(silver_x1*predict_year +silver_const +1.15*silver_std, 60)
                            silver_h_higher, silver_m_higher = divmod(silver_m_higher, 60)
                            silver_m_higher = int(silver_m_higher)
                            silver_s_higher=round(silver_s_higher,3)
                            if silver_s_higher<10:
                                silver_s_higher="0"+str(silver_s_higher)  
                            
                            gold_m, gold_s = divmod(gold_x1*predict_year +gold_const, 60)
                            gold_h, gold_m = divmod(gold_m, 60)
                            gold_m = int(gold_m)
                            gold_s=round(gold_s,3)
                            if gold_s<10:
                                gold_s="0"+str(gold_s)    
                                
                                
                            gold_m_lower, gold_s_lower = divmod(gold_x1*predict_year +gold_const - 1.15*gold_std, 60)
                            gold_h_lower, gold_m_lower = divmod(gold_m_lower, 60)
                            gold_m_lower = int(gold_m_lower)
                            gold_s_lower=round(gold_s_lower,3)
                            if gold_s_lower<10:
                                gold_s_lower="0"+str(gold_s_lower)  
                                
                            gold_m_higher, gold_s_higher = divmod(gold_x1*predict_year +gold_const +1.15*gold_std, 60)
                            gold_h_higher, gold_m_higher = divmod(gold_m_higher, 60)
                            gold_m_higher = int(gold_m_higher)
                            gold_s_higher=round(gold_s_higher,3)
                            if gold_s_higher<10:
                                gold_s_higher="0"+str(gold_s_higher)                                  
                                

                            st.write(f"This trend predicts a Gold medal winning time of {gold_m}:{gold_s} in {predict_year}.")
                            st.write(f"We can be 75% confident the time will be between {gold_m_lower}:{gold_s_lower} and {gold_m_higher}:{gold_s_higher}")
                            
                            st.write(f"This trend predicts a Silver medal winning time of {silver_m}:{silver_s} in {predict_year}.")
                            st.write(f"We can be 75% confident the time will be between {silver_m_lower}:{silver_s_lower} and {silver_m_higher}:{silver_s_higher}")
                            st.write(f"This trend predicts a Bronze medal winning time of {bronze_m}:{bronze_s} in {predict_year}.")
                            st.write(f"We can be 75% confident the time will be between {bronze_m_lower}:{bronze_s_lower} and {bronze_m_higher}:{bronze_s_higher}")
                elif medal_or_qual=="Qual times":
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
                        df_mask = df_mask.mask(df_mask["Q3_seconds"] < time_range[0])
                        df_mask = df_mask.mask(df_mask["Q3_seconds"] > time_range[1])
                        df_mask = df_mask.mask(df_mask["Q2_seconds"] < time_range[0])
                        df_mask = df_mask.mask(df_mask["Q2_seconds"] > time_range[1])
                        df_mask = df_mask.mask(df_mask["Q1_seconds"] < time_range[0])
                        df_mask = df_mask.mask(df_mask["Q1_seconds"] > time_range[1])
                        fig = px.scatter(df_mask, x="Year", y = ["Q3_seconds","Q2_seconds","Q1_seconds"], title="Men's Team Pursuit Qualifying Time Progression",labels={"value":"Seconds"},trendline="ols", color_discrete_sequence=['darkorange',"silver","gold"])
                        customdata = np.stack((round(df_mask['Q3_seconds'],3), round(df_mask['Q2_seconds'],3),round(df_mask['Q1_seconds'],3),df_mask['Year']), axis=-1)
                        hovertemplate = ('Q3: %{customdata[0]}<br>' + 'Q2: %{customdata[1]}<br>' + 'Q1: %{customdata[2]}<br>' +
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
                            
                            #ERRORS
                            df_mask["Q1_Error"]=abs(df_mask["Q1_seconds"]-((df_mask["Year"]*gold_x1) +gold_const))
                            df_mask["Q2_Error"]=abs(df_mask["Q2_seconds"]-((df_mask["Year"]*silver_x1) +silver_const))
                            df_mask["Q3_Error"]=abs(df_mask["Q3_seconds"]-((df_mask["Year"]*bronze_x1) +bronze_const))
                            
                            q1_std=round(df_mask['Q1_Error'].std(),2)
                            q2_std=round(df_mask['Q2_Error'].std(),2)
                            q3_std=round(df_mask['Q3_Error'].std(),2)
                            
                            
                            st.write(f"Q1 time = {round(gold_x1,6)}(Year) + {round(gold_const,3)}")
                            st.write(f"One standard deviation of the absolute errors is {q1_std} seconds")
                            st.write(f"R-squared = {round(gold_a,3)}")
                            st.write(f"Q2 time = {round(silver_x1,6)}(Year) + {round(silver_const,3)}")
                            st.write(f"One standard deviation of the absolute errors is {q2_std} seconds")
                            st.write(f"R-squared = {round(silver_a,3)}")
                            st.write(f"Q3 time = {round(bronze_x1,6)}(Year) + {round(bronze_const,3)}")
                            st.write(f"One standard deviation of the absolute errors is {q3_std} seconds")
                            st.write(f"R-squared = {round(bronze_a,3)}")
                        with col2:
                            if oly_or_wch == "OLY only":
                                predict_year = st.selectbox("Select year for fastest time prediction:", [2024,2028,2032,2036,2040,2044,2048])
                                
                            else:
                                predict_year = st.number_input("Select year for fastest time prediction:",min_value=2020,max_value=3000,value=2024,step=1)




                            bronze_m, bronze_s = divmod(bronze_x1*predict_year +bronze_const, 60)
                            bronze_h, bronze_m = divmod(bronze_m, 60)
                            bronze_m = int(bronze_m)
                            bronze_s=round(bronze_s,3)
                            if bronze_s<10:
                                bronze_s="0"+str(bronze_s)   
                                
                            bronze_m_lower, bronze_s_lower = divmod(bronze_x1*predict_year +bronze_const - 2*q3_std, 60)
                            bronze_h_lower, bronze_m_lower = divmod(bronze_m_lower, 60)
                            bronze_m_lower = int(bronze_m_lower)
                            bronze_s_lower=round(bronze_s_lower,3)
                            if bronze_s_lower<10:
                                bronze_s_lower="0"+str(bronze_s_lower)  
                                
                            bronze_m_higher, bronze_s_higher = divmod(bronze_x1*predict_year +bronze_const +2*q3_std, 60)
                            bronze_h_higher, bronze_m_higher = divmod(bronze_m_higher, 60)
                            bronze_m_higher = int(bronze_m_higher)
                            bronze_s_higher=round(bronze_s_higher,3)
                            if bronze_s_higher<10:
                                bronze_s_higher="0"+str(bronze_s_higher)  

                            
                            silver_m, silver_s = divmod(silver_x1*predict_year +silver_const, 60)
                            silver_h, silver_m = divmod(silver_m, 60)
                            silver_m = int(silver_m)
                            silver_s=round(silver_s,3)
                            if silver_s<10:
                                silver_s="0"+str(silver_s)   
                                
                            silver_m_lower, silver_s_lower = divmod(silver_x1*predict_year +silver_const - 2*q2_std, 60)
                            silver_h_lower, silver_m_lower = divmod(silver_m_lower, 60)
                            silver_m_lower = int(silver_m_lower)
                            silver_s_lower=round(silver_s_lower,3)
                            if silver_s_lower<10:
                                silver_s_lower="0"+str(silver_s_lower)  
                                
                            silver_m_higher, silver_s_higher = divmod(silver_x1*predict_year +silver_const +2*q2_std, 60)
                            silver_h_higher, silver_m_higher = divmod(silver_m_higher, 60)
                            silver_m_higher = int(silver_m_higher)
                            silver_s_higher=round(silver_s_higher,3)
                            if silver_s_higher<10:
                                silver_s_higher="0"+str(silver_s_higher)  
                            
                            gold_m, gold_s = divmod(gold_x1*predict_year +gold_const, 60)
                            gold_h, gold_m = divmod(gold_m, 60)
                            gold_m = int(gold_m)
                            gold_s=round(gold_s,3)
                            if gold_s<10:
                                gold_s="0"+str(gold_s)    
                                
                                
                            gold_m_lower, gold_s_lower = divmod(gold_x1*predict_year +gold_const - 2*q1_std, 60)
                            gold_h_lower, gold_m_lower = divmod(gold_m_lower, 60)
                            gold_m_lower = int(gold_m_lower)
                            gold_s_lower=round(gold_s_lower,3)
                            if gold_s_lower<10:
                                gold_s_lower="0"+str(gold_s_lower)  
                                
                            gold_m_higher, gold_s_higher = divmod(gold_x1*predict_year +gold_const +2*q1_std, 60)
                            gold_h_higher, gold_m_higher = divmod(gold_m_higher, 60)
                            gold_m_higher = int(gold_m_higher)
                            gold_s_higher=round(gold_s_higher,3)
                            if gold_s_higher<10:
                                gold_s_higher="0"+str(gold_s_higher)                                  
                                

                            st.write(f"This trend predicts a Q1 time of {gold_m}:{gold_s} in {predict_year}.")
                            st.write(f"We can be 95% confident the time will be between {gold_m_lower}:{gold_s_lower} and {gold_m_higher}:{gold_s_higher}")
                            
                            st.write(f"This trend predicts a Q2 time of {silver_m}:{silver_s} in {predict_year}.")
                            st.write(f"We can be 95% confident the time will be between {silver_m_lower}:{silver_s_lower} and {silver_m_higher}:{silver_s_higher}")
                            st.write(f"This trend predicts a Q3 time of {bronze_m}:{bronze_s} in {predict_year}.")
                            st.write(f"We can be 95% confident the time will be between {bronze_m_lower}:{bronze_s_lower} and {bronze_m_higher}:{bronze_s_higher}")         


                    
                elif medal_or_qual=="Fastest time":
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
                        df_mask = df_mask.mask(df_mask["Fastest_seconds"] < time_range[0])
                        df_mask = df_mask.mask(df_mask["Fastest_seconds"] > time_range[1])

                        fig = px.scatter(df_mask, x="Year", y = ["Fastest_seconds"], title="Men's Team Pursuit Competition Fastest Time Progression",labels={"value":"Seconds"},trendline="ols", color_discrete_sequence=["gold"])
                        customdata = np.stack((round(df_mask['Fastest_seconds'],3),df_mask['Year']), axis=-1)
                        hovertemplate = ('Fastest: %{customdata[0]}<br>' +
                    'Year: %{customdata[1]}<br>' 
                    '<extra></extra>')
                        fig.update_traces(customdata=customdata, hovertemplate=hovertemplate)

                        st.plotly_chart(fig, use_container_width=True)
                        col1,col2=st.columns(2)
                        with col1:
                            fastest_a=px.get_trendline_results(fig).px_fit_results.iloc[0].rsquared
                            fastest_const = px.get_trendline_results(fig).px_fit_results.iloc[0].params[0]
                            fastest_x1=px.get_trendline_results(fig).px_fit_results.iloc[0].params[1]
                            
                            #ERRORS
                            df_mask["Fastest_Error"]=abs(df_mask["Fastest_seconds"]-((df_mask["Year"]*fastest_x1) +fastest_const))

                            
                            fastest_std=round(df_mask['Fastest_Error'].std(),2)

                            
                            st.write(f"Q3 time = {round(fastest_x1,6)}(Year) + {round(fastest_const,3)}")
                            st.write(f"One standard deviation of the absolute errors is {fastest_std} seconds")
                            st.write(f"R-squared = {round(fastest_a,3)}")

                        with col2:
                            if oly_or_wch == "OLY only":
                                predict_year = st.selectbox("Select year for fastest time prediction:", [2024,2028,2032,2036,2040,2044,2048])
                                
                            else:
                                predict_year = st.number_input("Select year for fastest time prediction:",min_value=2020,max_value=3000,value=2024,step=1)
                                




                            fastest_m, fastest_s = divmod(fastest_x1*predict_year +fastest_const, 60)
                            fastest_h, fastest_m = divmod(fastest_m, 60)
                            fastest_m = int(fastest_m)
                            fastest_s=round(fastest_s,3)
                            if fastest_s<10:
                                fastest_s="0"+str(fastest_s)           
                            
                            
                            fastest_m_lower, fastest_s_lower = divmod(fastest_x1*predict_year +fastest_const - 2*fastest_std, 60)
                            fastest_h_lower, fastest_m_lower = divmod(fastest_m_lower, 60)
                            fastest_m_lower = int(fastest_m_lower)
                            fastest_s_lower=round(fastest_s_lower,3)
                            if fastest_s_lower<10:
                                fastest_s_lower="0"+str(fastest_s_lower)  
                                
                            fastest_m_higher, fastest_s_higher = divmod(fastest_x1*predict_year +fastest_const +2*fastest_std, 60)
                            fastest_h_higher, fastest_m_higher = divmod(fastest_m_higher, 60)
                            fastest_m_higher = int(fastest_m_higher)
                            fastest_s_higher=round(fastest_s_higher,3)
                            if fastest_s_higher<10:
                                fastest_s_higher="0"+str(fastest_s_higher)     

                            st.write(f"This trend predicts a fastest time of {fastest_m}:{fastest_s} in {predict_year}.")
                            st.write(f"We can be 95% confident the time will be between {fastest_m_lower}:{fastest_s_lower} and {fastest_m_higher}:{fastest_s_higher}")




    if race_type=="Women's Team Pursuit":
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
        
        c1,c2=st.columns([1,3])

        with c1:
            trend = st.selectbox("WR or Medal trend?:", ["World Record progression","Medal progression"], key="trend type Selector")
            
        if trend=="World Record progression":
            
            df= get_data_from_excel()
            df_master=df
            df_show = df.drop(columns=["DateSerial","Datetime"])
            with c1:
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


        else:
            @st.cache_data
            def get_placing_data_from_excel():
                df = pd.read_excel(
                    io='pages/WR_progressions/Medals_Women_TP.xlsx',
                    engine ='openpyxl',
                    sheet_name='Sheet1',
                    skiprows=0,
                    usecols='A:L',
                    nrows=40
                    )
                #df = df.replace(',','')


                return df


            c1,c2=st.columns([1,3])
            with c1:
    #             trend = st.selectbox("WR or Placings trend?:", ["World Record progression","Placing progression"], key="MSP trend type Selector")

                #if trend=="World Record progression":

                df = get_placing_data_from_excel()
                df_master=df
                df_show=df
                comp = st.selectbox("Which competitions?", ["OLY and WCH","Just OLY", "Just WCH"], key="MSP comp type Selector")
                if comp == "Just OLY":
                        df_show=df_show.loc[df_show["Competition"]=="OLY"]
                elif comp == "Just WCH":
                        df_show=df_show.loc[df_show["Competition"]=="WCH"]
                df=df_show
                df_show

                ##Download buttons
                def convert_to_csv(df_show):
                    return df.to_csv(index=False,sep = ",").encode('utf-32')
                csv = convert_to_csv(df_show)
                download1 = st.download_button(
                    label="Download Women IP Placing data as CSV",
                    data=csv,
                    file_name='Women_IP_Data.csv',
                    mime='text/csv',
                    key="buffertt1"
                )
                buffer_tt = io.BytesIO()
                with pd.ExcelWriter(buffer_tt, engine='xlsxwriter') as writer:
                    df_show.to_excel(writer, sheet_name='Sheet1', index=False)
                    writer.close()
                    download2 = st.download_button(
                        label="Download Women IP Placing data as Excel",
                        data=buffer_tt,
                        file_name='Women_IP_Data.xlsx',
                        mime='application/vnd.ms-excel',
                        key="buffertt2"
                    )
                ##Download buttons complete
            with c2:
                date_range = st.slider(
        "Restrict date range?",
                value = (2000,2025),
                    min_value = 2000,
                    max_value = 2025)

                time_range = st.slider(
        "Restrict time range?",
                value = (243.000,284.000),
                    max_value = 284.000,
                    min_value = 243.000)

                df_mask = df.mask(df["Year"] < date_range[0])
                df_mask = df_mask.mask(df_mask["Year"] > date_range[1])
                df_mask = df_mask.mask(df_mask["1st_seconds"] < time_range[0])
                df_mask = df_mask.mask(df_mask["1st_seconds"] > time_range[1])
                df_mask = df_mask.mask(df_mask["2nd_seconds"] < time_range[0])
                df_mask = df_mask.mask(df_mask["2nd_seconds"] > time_range[1])
                df_mask = df_mask.mask(df_mask["3rd_seconds"] < time_range[0])
                df_mask = df_mask.mask(df_mask["3rd_seconds"] > time_range[1])

                df_mask = df_mask.mask(df_mask["8th_seconds"] < time_range[0])
                df_mask = df_mask.mask(df_mask["8th_seconds"] > time_range[1])
                fig = px.scatter(df_mask, x="Year", y = ["1st_seconds","2nd_seconds","3rd_seconds","8th_seconds"], title="Women's TP World Champs & Olympics Qualifying Time Progression",labels={"value":"Seconds"},trendline="ols", color_discrete_sequence=['gold',"silver","darkorange","lightpink","teal"])
                customdata = np.stack((round(df_mask['1st_seconds'],3), round(df_mask['2nd_seconds'],3),round(df_mask['3rd_seconds'],3), round(df_mask['8th_seconds'],3),df_mask['Year'], df_mask['Competition']),axis=-1)
                hovertemplate = ('Gold: %{customdata[0]}<br>' + 'Silver: %{customdata[1]}<br>' + 'Bronze: %{customdata[2]}<br>' + '8th: %{customdata[3]}<br>' +
            'Year: %{customdata[4]}<br>' +
            'Competition: %{customdata[5]}<br>'
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



                    st.write(f"1st = {round(first_x1,6)}(Year) + {round(first_const,3)}")
                    st.write(f"R-squared = {round(first_a,3)}")

                    st.write(f"2nd = {round(second_x1,6)}(Year) + {round(second_const,3)}")
                    st.write(f"R-squared = {round(second_a,3)}")

                    st.write(f"3rd = {round(third_x1,6)}(Year) + {round(third_const,3)}")
                    st.write(f"R-squared = {round(third_a,3)}")

                    st.write(f"8th = {round(eigth_x1,6)}(Year) + {round(eigth_const,3)}")
                    st.write(f"R-squared = {round(eigth_a,3)}")


                with col2:
                    predict_year = st.number_input("Select year for fastest time prediction:",min_value=2020,max_value=3000,value=2024,step=1)


                    first_m, first_s = divmod(first_x1*predict_year +first_const, 60)
                    first_h, first_m = divmod(first_m, 60)
                    first_m = int(first_m)
                    first_s=round(first_s,3)
                    if first_s<10:
                        first_s="0"+str(first_s)           
                    st.write(f"This trend predicts a top qualifying time of {first_m}:{first_s} in {predict_year}.")


                    second_m, second_s = divmod(second_x1*predict_year +second_const, 60)
                    second_h, second_m = divmod(second_m, 60)
                    second_m = int(second_m)
                    second_s=round(second_s,3)
                    if second_s<10:
                        second_s="0"+str(second_s)           
                    st.write(f"This trend predicts a second qualifying time of {second_m}:{second_s} in {predict_year}.")

                    third_m, third_s = divmod(third_x1*predict_year +third_const, 60)
                    third_h, third_m = divmod(third_m, 60)
                    third_m = int(third_m)
                    third_s=round(third_s,3)
                    if third_s<10:
                        third_s="0"+str(third_s)           
                    st.write(f"This trend predicts a third qualifying time of {third_m}:{third_s} in {predict_year}.")



                    eigth_m, eigth_s = divmod(eigth_x1*predict_year +eigth_const, 60)
                    eigth_h, eigth_m = divmod(eigth_m, 60)
                    eigth_m = int(eigth_m)
                    eigth_s=round(eigth_s,3)
                    if eigth_s<10:
                        eigth_s="0"+str(eigth_s)           
                    st.write(f"This trend predicts a eigth qualifying time of {eigth_m}:{eigth_s} in {predict_year}.")






















    
    if race_type=="Men's Individual Pursuit":
        
        c1,c2=st.columns([1,3])
        with c1:
            trend = st.selectbox("WR or Placings trend?:", ["World Record progression","Placing progression"], key="MSP trend type Selector")

        if trend=="World Record progression":
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
            with c1:
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


        else:    
            @st.cache_data
            def get_placing_data_from_excel():
                df = pd.read_excel(
                    io='pages/WR_progressions/Medals_Men_IP.xlsx',
                    engine ='openpyxl',
                    sheet_name='Sheet1',
                    skiprows=0,
                    usecols='A:L',
                    nrows=40
                    )
                #df = df.replace(',','')


                return df


#                 c1,co2=st.columns([1,3])
            with c1:


                df = get_placing_data_from_excel()
                df_master=df
                df_show=df
                df_show

                ##Download buttons
                def convert_to_csv(df_show):
                    return df.to_csv(index=False,sep = ",").encode('utf-32')
                csv = convert_to_csv(df_show)
                download1 = st.download_button(
                    label="Download Men IP Placing data as CSV",
                    data=csv,
                    file_name='Men_IP_Data.csv',
                    mime='text/csv',
                    key="buffertt1"
                )
                buffer_tt = io.BytesIO()
                with pd.ExcelWriter(buffer_tt, engine='xlsxwriter') as writer:
                    df_show.to_excel(writer, sheet_name='Sheet1', index=False)
                    writer.close()
                    download2 = st.download_button(
                        label="Download Men IP Placing data as Excel",
                        data=buffer_tt,
                        file_name='Men_IP_Data.xlsx',
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
                value = (240.000,283.000),
                    max_value = 283.000,
                    min_value = 240.000)

                df_mask = df.mask(df["Year"] < date_range[0])
                df_mask = df_mask.mask(df_mask["Year"] > date_range[1])
                df_mask = df_mask.mask(df_mask["1st_seconds"] < time_range[0])
                df_mask = df_mask.mask(df_mask["1st_seconds"] > time_range[1])
                df_mask = df_mask.mask(df_mask["2nd_seconds"] < time_range[0])
                df_mask = df_mask.mask(df_mask["2nd_seconds"] > time_range[1])
                df_mask = df_mask.mask(df_mask["3rd_seconds"] < time_range[0])
                df_mask = df_mask.mask(df_mask["3rd_seconds"] > time_range[1])
                df_mask = df_mask.mask(df_mask["16th_seconds"] < time_range[0])
                df_mask = df_mask.mask(df_mask["16th_seconds"] > time_range[1])
                df_mask = df_mask.mask(df_mask["8th_seconds"] < time_range[0])
                df_mask = df_mask.mask(df_mask["8th_seconds"] > time_range[1])
                fig = px.scatter(df_mask, x="Year", y = ["1st_seconds","2nd_seconds","3rd_seconds","8th_seconds","16th_seconds"], title="Men's IP World Champs Placings Time Progression",labels={"value":"Seconds"},trendline="ols", color_discrete_sequence=['gold',"silver","darkorange","lightpink","teal"])
                customdata = np.stack((round(df_mask['1st_seconds'],3), round(df_mask['2nd_seconds'],3),round(df_mask['3rd_seconds'],3), round(df_mask['8th_seconds'],3),round(df_mask['16th_seconds'],3),df_mask['Year'], df_mask['Competition']),axis=-1)
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
                    st.write(f"This trend predicts a top qualifying time of {first_m}:{first_s} in {predict_year}.")


                    second_m, second_s = divmod(second_x1*predict_year +second_const, 60)
                    second_h, second_m = divmod(second_m, 60)
                    second_m = int(second_m)
                    second_s=round(second_s,3)
                    if second_s<10:
                        second_s="0"+str(second_s)           
                    st.write(f"This trend predicts a second qualifying time of {second_m}:{second_s} in {predict_year}.")

                    third_m, third_s = divmod(third_x1*predict_year +third_const, 60)
                    third_h, third_m = divmod(third_m, 60)
                    third_m = int(third_m)
                    third_s=round(third_s,3)
                    if third_s<10:
                        third_s="0"+str(third_s)           
                    st.write(f"This trend predicts a third qualifying time of {third_m}:{third_s} in {predict_year}.")



                    eigth_m, eigth_s = divmod(eigth_x1*predict_year +eigth_const, 60)
                    eigth_h, eigth_m = divmod(eigth_m, 60)
                    eigth_m = int(eigth_m)
                    eigth_s=round(eigth_s,3)
                    if eigth_s<10:
                        eigth_s="0"+str(eigth_s)           
                    st.write(f"This trend predicts a eigth qualifying time of {eigth_m}:{eigth_s} in {predict_year}.")

                    sixteenth_m, sixteenth_s = divmod(sixteenth_x1*predict_year +sixteenth_const, 60)
                    sixteenth_h, sixteenth_m = divmod(sixteenth_m, 60)
                    sixteenth_m = int(sixteenth_m)
                    sixteenth_s=round(sixteenth_s,3)
                    if sixteenth_s<10:
                        sixteenth_s="0"+str(sixteenth_s)           
                    st.write(f"This trend predicts a sixteenth qualifying time of {sixteenth_m}:{sixteenth_s} in {predict_year}.")







    if race_type=="Women's Individual Pursuit":
        
        
        @st.cache_data
        def get_placing_data_from_excel():
            df = pd.read_excel(
                io='pages/WR_progressions/Medals_Women_IP.xlsx',
                engine ='openpyxl',
                sheet_name='Sheet1',
                skiprows=0,
                usecols='A:L',
                nrows=40
                )
            #df = df.replace(',','')


            return df


        c1,c2=st.columns([1,3])
        with c1:
#             trend = st.selectbox("WR or Placings trend?:", ["World Record progression","Placing progression"], key="MSP trend type Selector")

            #if trend=="World Record progression":

            df = get_placing_data_from_excel()
            df_master=df
            df_show=df
            df_show

            ##Download buttons
            def convert_to_csv(df_show):
                return df.to_csv(index=False,sep = ",").encode('utf-32')
            csv = convert_to_csv(df_show)
            download1 = st.download_button(
                label="Download Women IP Placing data as CSV",
                data=csv,
                file_name='Women_IP_Data.csv',
                mime='text/csv',
                key="buffertt1"
            )
            buffer_tt = io.BytesIO()
            with pd.ExcelWriter(buffer_tt, engine='xlsxwriter') as writer:
                df_show.to_excel(writer, sheet_name='Sheet1', index=False)
                writer.close()
                download2 = st.download_button(
                    label="Download Women IP Placing data as Excel",
                    data=buffer_tt,
                    file_name='Women_IP_Data.xlsx',
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
            value = (196.000,250.000),
                max_value = 250.000,
                min_value = 196.000)

            df_mask = df.mask(df["Year"] < date_range[0])
            df_mask = df_mask.mask(df_mask["Year"] > date_range[1])
            df_mask = df_mask.mask(df_mask["1st_seconds"] < time_range[0])
            df_mask = df_mask.mask(df_mask["1st_seconds"] > time_range[1])
            df_mask = df_mask.mask(df_mask["2nd_seconds"] < time_range[0])
            df_mask = df_mask.mask(df_mask["2nd_seconds"] > time_range[1])
            df_mask = df_mask.mask(df_mask["3rd_seconds"] < time_range[0])
            df_mask = df_mask.mask(df_mask["3rd_seconds"] > time_range[1])
            df_mask = df_mask.mask(df_mask["16th_seconds"] < time_range[0])
            df_mask = df_mask.mask(df_mask["16th_seconds"] > time_range[1])
            df_mask = df_mask.mask(df_mask["8th_seconds"] < time_range[0])
            df_mask = df_mask.mask(df_mask["8th_seconds"] > time_range[1])
            fig = px.scatter(df_mask, x="Year", y = ["1st_seconds","2nd_seconds","3rd_seconds","8th_seconds","16th_seconds"], title="Women's IP World Champs Placings Time Progression",labels={"value":"Seconds"},trendline="ols", color_discrete_sequence=['gold',"silver","darkorange","lightpink","teal"])
            customdata = np.stack((round(df_mask['1st_seconds'],3), round(df_mask['2nd_seconds'],3),round(df_mask['3rd_seconds'],3), round(df_mask['8th_seconds'],3),round(df_mask['16th_seconds'],3),df_mask['Year'], df_mask['Competition']),axis=-1)
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
                st.write(f"This trend predicts a top qualifying time of {first_m}:{first_s} in {predict_year}.")


                second_m, second_s = divmod(second_x1*predict_year +second_const, 60)
                second_h, second_m = divmod(second_m, 60)
                second_m = int(second_m)
                second_s=round(second_s,3)
                if second_s<10:
                    second_s="0"+str(second_s)           
                st.write(f"This trend predicts a second qualifying time of {second_m}:{second_s} in {predict_year}.")

                third_m, third_s = divmod(third_x1*predict_year +third_const, 60)
                third_h, third_m = divmod(third_m, 60)
                third_m = int(third_m)
                third_s=round(third_s,3)
                if third_s<10:
                    third_s="0"+str(third_s)           
                st.write(f"This trend predicts a third qualifying time of {third_m}:{third_s} in {predict_year}.")



                eigth_m, eigth_s = divmod(eigth_x1*predict_year +eigth_const, 60)
                eigth_h, eigth_m = divmod(eigth_m, 60)
                eigth_m = int(eigth_m)
                eigth_s=round(eigth_s,3)
                if eigth_s<10:
                    eigth_s="0"+str(eigth_s)           
                st.write(f"This trend predicts a eigth qualifying time of {eigth_m}:{eigth_s} in {predict_year}.")

                sixteenth_m, sixteenth_s = divmod(sixteenth_x1*predict_year +sixteenth_const, 60)
                sixteenth_h, sixteenth_m = divmod(sixteenth_m, 60)
                sixteenth_m = int(sixteenth_m)
                sixteenth_s=round(sixteenth_s,3)
                if sixteenth_s<10:
                    sixteenth_s="0"+str(sixteenth_s)           
                st.write(f"This trend predicts a sixteenth qualifying time of {sixteenth_m}:{sixteenth_s} in {predict_year}.")




                
                
                
                
                
                
                
                
########################################################Juniors#############################################################


    if race_type=="Junior Men's Sprint Qualifying":
        
        @st.cache_data
        def get_placing_data_from_excel():
            df = pd.read_excel(
                io='pages/WR_progressions/Junior_Progression.xlsx',
                engine ='openpyxl',
                sheet_name='M SP Q',
                skiprows=0,
                usecols='A:F',
                nrows=300
                )
            #df = df.replace(',','')


            return df




        c1,c2=st.columns([1,3])
        with c1:

            


            df= get_placing_data_from_excel()
            df_master=df
            df_show = df
            df_show=df_show.loc[(df_show["Rank"]==1) | (df_show["Rank"]==2) |(df_show["Rank"]==3) | (df_show["Rank"]==4) |(df_show["Rank"]==5) | (df_show["Rank"]==6) |(df_show["Rank"]==8) | (df_show["Rank"]==16)].reset_index(drop=True)
            df_show
                
                


        with c2:
            date_range = st.slider(
    "Restrict date range?",
            value = (df_show["Year"].min(),df_show["Year"].max()),
                min_value = df_show["Year"].min(),
                max_value = df_show["Year"].max())
            

            time_range = st.slider(
    "Restrict time range?",
            value = (df_show["Time"].min(),df_show["Time"].max()),
                min_value = df_show["Time"].min(),
                max_value = df_show["Time"].max())

            df_mask = df_show.mask(df_show["Year"] < date_range[0])
            df_mask = df_mask.mask(df_mask["Year"] > date_range[1])
            df_mask = df_mask.mask(df_mask["Time"] < time_range[0])
            df_mask = df_mask.mask(df_mask["Time"] > time_range[1])
            df_mask=df_mask.dropna()
            
            
            df_flat = df_mask.pivot(index='Year', columns='Rank')
            df_flat = df_flat['Time']
            
            df_flat['Year'] = df_flat.index
            df_flat=df_flat.rename(columns={1: "1st", 2: "2nd", 3: "3rd", 4: "4th", 5: "5th", 6: "6th", 8: "8th", 16: "16th"})
            
            

            fig = px.scatter(df_flat, x="Year", y = ["1st","2nd","3rd","4th","5th","6th","8th","16th"], title="Junior Men's Flying 200m World Champs Placing Progression",trendline="ols", color_discrete_sequence=['gold',"silver","darkorange","lightpink","teal","mediumvioletred","mediumaquamarine","olive"])
            customdata = np.stack((df_flat['1st'], df_flat['2nd'], df_flat['3rd'],df_flat['4th'],df_flat['5th'],df_flat['6th'],df_flat['8th'],df_flat['16th'],df_flat['Year']), axis=-1)
            hovertemplate = ('1st: %{customdata[0]}<br>' + '2nd: %{customdata[1]}<br>' +'3rd: %{customdata[2]}<br>' +'4th: %{customdata[3]}<br>' +'5th: %{customdata[4]}<br>' +'6th: %{customdata[5]}<br>' +'8th: %{customdata[6]}<br>' +'16th: %{customdata[7]}<br>' +
        'Date: %{customdata[8]}<br>' 
        '<extra></extra>')
            fig.update_traces(customdata=customdata, hovertemplate=hovertemplate)
            st.plotly_chart(fig, use_container_width=True)
            first_a=px.get_trendline_results(fig).px_fit_results.iloc[0].rsquared
            first_const = px.get_trendline_results(fig).px_fit_results.iloc[0].params[0]
            first_x1=px.get_trendline_results(fig).px_fit_results.iloc[0].params[1]

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
            
            fourth_a=px.get_trendline_results(fig).px_fit_results.iloc[3].rsquared
            fourth_const = px.get_trendline_results(fig).px_fit_results.iloc[3].params[0]
            fourth_x1=px.get_trendline_results(fig).px_fit_results.iloc[3].params[1]

            fifth_a=px.get_trendline_results(fig).px_fit_results.iloc[4].rsquared
            fifth_const = px.get_trendline_results(fig).px_fit_results.iloc[4].params[0]
            fifth_x1=px.get_trendline_results(fig).px_fit_results.iloc[4].params[1]

            sixth_a=px.get_trendline_results(fig).px_fit_results.iloc[5].rsquared
            sixth_const = px.get_trendline_results(fig).px_fit_results.iloc[5].params[0]
            sixth_x1=px.get_trendline_results(fig).px_fit_results.iloc[5].params[1]

            eigth_a=px.get_trendline_results(fig).px_fit_results.iloc[6].rsquared
            eigth_const = px.get_trendline_results(fig).px_fit_results.iloc[6].params[0]
            eigth_x1=px.get_trendline_results(fig).px_fit_results.iloc[6].params[1]

            sixteenth_a=px.get_trendline_results(fig).px_fit_results.iloc[7].rsquared
            sixteenth_const = px.get_trendline_results(fig).px_fit_results.iloc[7].params[0]
            sixteenth_x1=px.get_trendline_results(fig).px_fit_results.iloc[7].params[1]
            c1,c2=st.columns(2)
            with c1:
                st.write(f"1st = {round(first_x1,6)}(Year) + {round(first_const,3)}")
                st.write(f"R-squared = {round(first_a,3)}")

                st.write(f"2nd = {round(second_x1,6)}(Year) + {round(second_const,3)}")
                st.write(f"R-squared = {round(second_a,3)}")

                st.write(f"3rd = {round(third_x1,6)}(Year) + {round(third_const,3)}")
                st.write(f"R-squared = {round(third_a,3)}")

                st.write(f"4th = {round(fourth_x1,6)}(Year) + {round(fourth_const,3)}")
                st.write(f"R-squared = {round(fourth_a,3)}")
            with c2:
                st.write(f"5th = {round(fifth_x1,6)}(Year) + {round(fifth_const,3)}")
                st.write(f"R-squared = {round(fifth_a,3)}")

                st.write(f"6th = {round(sixth_x1,6)}(Year) + {round(sixth_const,3)}")
                st.write(f"R-squared = {round(sixth_a,3)}")

                st.write(f"8th = {round(eigth_x1,6)}(Year) + {round(eigth_const,3)}")
                st.write(f"R-squared = {round(eigth_a,3)}")

                st.write(f"16th = {round(sixteenth_x1,6)}(Year) + {round(sixteenth_const,3)}")
                st.write(f"R-squared = {round(sixteenth_a,3)}")

        with col2:
            predict_year = st.number_input("Select year for fastest time prediction:",min_value=2020,max_value=3000,value=2024,step=1)


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


            fourth_m, fourth_s = divmod(fourth_x1*predict_year +fourth_const, 60)
            fourth_h, fourth_m = divmod(fourth_m, 60)
            fourth_m = int(fourth_m)
            fourth_s=round(fourth_s,3)
            if fourth_s<10:
                fourth_s="0"+str(fourth_s)           
            st.write(f"This trend predicts a fourth qualifying time of {fourth_s} in {predict_year}.")


            fifth_m, fifth_s = divmod(fifth_x1*predict_year +fifth_const, 60)
            fifth_h, fifth_m = divmod(fifth_m, 60)
            fifth_m = int(fifth_m)
            fifth_s=round(fifth_s,3)
            if fifth_s<10:
                fifth_s="0"+str(fifth_s)           
            st.write(f"This trend predicts a fifth qualifying time of {fifth_s} in {predict_year}.")

            sixth_m, sixth_s = divmod(sixth_x1*predict_year +sixth_const, 60)
            sixth_h, sixth_m = divmod(sixth_m, 60)
            sixth_m = int(sixth_m)
            sixth_s=round(sixth_s,3)
            if sixth_s<10:
                sixth_s="0"+str(sixth_s)           
            st.write(f"This trend predicts a sixth qualifying time of {sixth_s} in {predict_year}.")

            eigth_m, eigth_s = divmod(eigth_x1*predict_year +eigth_const, 60)
            eigth_h, eigth_m = divmod(eigth_m, 60)
            eigth_m = int(eigth_m)
            eigth_s=round(eigth_s,3)
            if eigth_s<10:
                eigth_s="0"+str(eigth_s)           
            st.write(f"This trend predicts an eigth qualifying time of {eigth_s} in {predict_year}.")

            sixteenth_m, sixteenth_s = divmod(sixteenth_x1*predict_year +sixteenth_const, 60)
            sixteenth_h, sixteenth_m = divmod(sixteenth_m, 60)
            sixteenth_m = int(sixteenth_m)
            sixteenth_s=round(sixteenth_s,3)
            if sixteenth_s<10:
                sixteenth_s="0"+str(sixteenth_s)           
            st.write(f"This trend predicts a sixteenth qualifying time of {sixteenth_s} in {predict_year}.")





    if race_type=="Junior Women's Sprint Qualifying":
        
        @st.cache_data
        def get_placing_data_from_excel():
            df = pd.read_excel(
                io='pages/WR_progressions/Junior_Progression.xlsx',
                engine ='openpyxl',
                sheet_name='W SP Q',
                skiprows=0,
                usecols='A:F',
                nrows=300
                )
            #df = df.replace(',','')


            return df




        c1,c2=st.columns([1,3])
        with c1:

            


            df= get_placing_data_from_excel()
            df_master=df
            df_show = df
            df_show=df_show.loc[(df_show["Rank"]==1) | (df_show["Rank"]==2) |(df_show["Rank"]==3) | (df_show["Rank"]==4) |(df_show["Rank"]==5) | (df_show["Rank"]==6) |(df_show["Rank"]==8) | (df_show["Rank"]==16)].reset_index(drop=True)
            df_show
                
                


        with c2:
            date_range = st.slider(
    "Restrict date range?",
            value = (df_show["Year"].min(),df_show["Year"].max()),
                min_value = df_show["Year"].min(),
                max_value = df_show["Year"].max())
            

            time_range = st.slider(
    "Restrict time range?",
            value = (df_show["Time"].min(),df_show["Time"].max()),
                min_value = df_show["Time"].min(),
                max_value = df_show["Time"].max())

            df_mask = df_show.mask(df_show["Year"] < date_range[0])
            df_mask = df_mask.mask(df_mask["Year"] > date_range[1])
            df_mask = df_mask.mask(df_mask["Time"] < time_range[0])
            df_mask = df_mask.mask(df_mask["Time"] > time_range[1])
            df_mask=df_mask.dropna()
            df_flat = df_mask.pivot(index='Year', columns='Rank')

            df_flat = df_flat[ 'Time']
            df_flat['Year'] = df_flat.index
            df_flat=df_flat.rename(columns={1: "1st", 2: "2nd", 3: "3rd", 4: "4th", 5: "5th", 6: "6th", 8: "8th", 16: "16th"})
            
            

            fig = px.scatter(df_flat, x="Year", y = ["1st","2nd","3rd","4th","5th","6th","8th","16th"], title="Junior Women's Flying 200m World Champs Placing Progression",trendline="ols", color_discrete_sequence=['gold',"silver","darkorange","lightpink","teal","mediumvioletred","mediumaquamarine","olive"])
            customdata = np.stack((df_flat['1st'], df_flat['2nd'], df_flat['3rd'],df_flat['4th'],df_flat['5th'],df_flat['6th'],df_flat['8th'],df_flat['16th'],df_flat['Year']), axis=-1)
            hovertemplate = ('1st: %{customdata[0]}<br>' + '2nd: %{customdata[1]}<br>' +'3rd: %{customdata[2]}<br>' +'4th: %{customdata[3]}<br>' +'5th: %{customdata[4]}<br>' +'6th: %{customdata[5]}<br>' +'8th: %{customdata[6]}<br>' +'16th: %{customdata[7]}<br>' +
        'Date: %{customdata[8]}<br>' 
        '<extra></extra>')
            fig.update_traces(customdata=customdata, hovertemplate=hovertemplate)
            st.plotly_chart(fig, use_container_width=True)
            first_a=px.get_trendline_results(fig).px_fit_results.iloc[0].rsquared
            first_const = px.get_trendline_results(fig).px_fit_results.iloc[0].params[0]
            first_x1=px.get_trendline_results(fig).px_fit_results.iloc[0].params[1]

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
            
            fourth_a=px.get_trendline_results(fig).px_fit_results.iloc[3].rsquared
            fourth_const = px.get_trendline_results(fig).px_fit_results.iloc[3].params[0]
            fourth_x1=px.get_trendline_results(fig).px_fit_results.iloc[3].params[1]

            fifth_a=px.get_trendline_results(fig).px_fit_results.iloc[4].rsquared
            fifth_const = px.get_trendline_results(fig).px_fit_results.iloc[4].params[0]
            fifth_x1=px.get_trendline_results(fig).px_fit_results.iloc[4].params[1]

            sixth_a=px.get_trendline_results(fig).px_fit_results.iloc[5].rsquared
            sixth_const = px.get_trendline_results(fig).px_fit_results.iloc[5].params[0]
            sixth_x1=px.get_trendline_results(fig).px_fit_results.iloc[5].params[1]

            eigth_a=px.get_trendline_results(fig).px_fit_results.iloc[6].rsquared
            eigth_const = px.get_trendline_results(fig).px_fit_results.iloc[6].params[0]
            eigth_x1=px.get_trendline_results(fig).px_fit_results.iloc[6].params[1]

            sixteenth_a=px.get_trendline_results(fig).px_fit_results.iloc[7].rsquared
            sixteenth_const = px.get_trendline_results(fig).px_fit_results.iloc[7].params[0]
            sixteenth_x1=px.get_trendline_results(fig).px_fit_results.iloc[7].params[1]
            c1,c2=st.columns(2)
            with c1:
                st.write(f"1st = {round(first_x1,6)}(Year) + {round(first_const,3)}")
                st.write(f"R-squared = {round(first_a,3)}")

                st.write(f"2nd = {round(second_x1,6)}(Year) + {round(second_const,3)}")
                st.write(f"R-squared = {round(second_a,3)}")

                st.write(f"3rd = {round(third_x1,6)}(Year) + {round(third_const,3)}")
                st.write(f"R-squared = {round(third_a,3)}")

                st.write(f"4th = {round(fourth_x1,6)}(Year) + {round(fourth_const,3)}")
                st.write(f"R-squared = {round(fourth_a,3)}")
            with c2:
                st.write(f"5th = {round(fifth_x1,6)}(Year) + {round(fifth_const,3)}")
                st.write(f"R-squared = {round(fifth_a,3)}")

                st.write(f"6th = {round(sixth_x1,6)}(Year) + {round(sixth_const,3)}")
                st.write(f"R-squared = {round(sixth_a,3)}")

                st.write(f"8th = {round(eigth_x1,6)}(Year) + {round(eigth_const,3)}")
                st.write(f"R-squared = {round(eigth_a,3)}")

                st.write(f"16th = {round(sixteenth_x1,6)}(Year) + {round(sixteenth_const,3)}")
                st.write(f"R-squared = {round(sixteenth_a,3)}")

        with col2:
            predict_year = st.number_input("Select year for fastest time prediction:",min_value=2020,max_value=3000,value=2024,step=1)


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


            fourth_m, fourth_s = divmod(fourth_x1*predict_year +fourth_const, 60)
            fourth_h, fourth_m = divmod(fourth_m, 60)
            fourth_m = int(fourth_m)
            fourth_s=round(fourth_s,3)
            if fourth_s<10:
                fourth_s="0"+str(fourth_s)           
            st.write(f"This trend predicts a fourth qualifying time of {fourth_s} in {predict_year}.")


            fifth_m, fifth_s = divmod(fifth_x1*predict_year +fifth_const, 60)
            fifth_h, fifth_m = divmod(fifth_m, 60)
            fifth_m = int(fifth_m)
            fifth_s=round(fifth_s,3)
            if fifth_s<10:
                fifth_s="0"+str(fifth_s)           
            st.write(f"This trend predicts a fifth qualifying time of {fifth_s} in {predict_year}.")

            sixth_m, sixth_s = divmod(sixth_x1*predict_year +sixth_const, 60)
            sixth_h, sixth_m = divmod(sixth_m, 60)
            sixth_m = int(sixth_m)
            sixth_s=round(sixth_s,3)
            if sixth_s<10:
                sixth_s="0"+str(sixth_s)           
            st.write(f"This trend predicts a sixth qualifying time of {sixth_s} in {predict_year}.")

            eigth_m, eigth_s = divmod(eigth_x1*predict_year +eigth_const, 60)
            eigth_h, eigth_m = divmod(eigth_m, 60)
            eigth_m = int(eigth_m)
            eigth_s=round(eigth_s,3)
            if eigth_s<10:
                eigth_s="0"+str(eigth_s)           
            st.write(f"This trend predicts an eigth qualifying time of {eigth_s} in {predict_year}.")

            sixteenth_m, sixteenth_s = divmod(sixteenth_x1*predict_year +sixteenth_const, 60)
            sixteenth_h, sixteenth_m = divmod(sixteenth_m, 60)
            sixteenth_m = int(sixteenth_m)
            sixteenth_s=round(sixteenth_s,3)
            if sixteenth_s<10:
                sixteenth_s="0"+str(sixteenth_s)           
            st.write(f"This trend predicts a sixteenth qualifying time of {sixteenth_s} in {predict_year}.")



            
    if race_type=="Junior Men's Team Sprint":
        
        @st.cache_data
        def get_placing_data_from_excel():
            df = pd.read_excel(
                io='pages/WR_progressions/Junior_Progression.xlsx',
                engine ='openpyxl',
                sheet_name='M TS',
                skiprows=0,
                usecols='A:F',
                nrows=150
                )
            #df = df.replace(',','')


            return df




        c1,c2=st.columns([1,3])
        with c1:

            


            df= get_placing_data_from_excel()
            df_master=df
            df_show = df
            df_show=df_show.loc[(df_show["Rank"]==1) | (df_show["Rank"]==2) |(df_show["Rank"]==3) | (df_show["Rank"]==4) |(df_show["Rank"]==5) | (df_show["Rank"]==6) |(df_show["Rank"]==8)].reset_index(drop=True)
            df_show
                
                


        with c2:
            date_range = st.slider(
    "Restrict date range?",
            value = (df_show["Year"].min(),df_show["Year"].max()),
                min_value = df_show["Year"].min(),
                max_value = df_show["Year"].max())
            

            time_range = st.slider(
    "Restrict time range?",
            value = (df_show["Time"].min(),df_show["Time"].max()),
                min_value = df_show["Time"].min(),
                max_value = df_show["Time"].max())

            df_mask = df_show.mask(df_show["Year"] < date_range[0])
            df_mask = df_mask.mask(df_mask["Year"] > date_range[1])
            df_mask = df_mask.mask(df_mask["Time"] < time_range[0])
            df_mask = df_mask.mask(df_mask["Time"] > time_range[1])
            df_mask=df_mask.dropna()
            df_flat = df_mask.pivot(index='Year', columns='Rank')

            df_flat = df_flat[ 'Time']
            df_flat['Year'] = df_flat.index
            df_flat=df_flat.rename(columns={1: "1st", 2: "2nd", 3: "3rd", 4: "4th", 5: "5th", 6: "6th", 8: "8th"})
            
            

            fig = px.scatter(df_flat, x="Year", y = ["1st","2nd","3rd","4th","5th","6th","8th"], title="Junior Men's Team Sprint World Champs Placing Progression",trendline="ols", color_discrete_sequence=['gold',"silver","darkorange","lightpink","teal","mediumvioletred","mediumaquamarine","olive"])
            customdata = np.stack((df_flat['1st'], df_flat['2nd'], df_flat['3rd'],df_flat['4th'],df_flat['5th'],df_flat['6th'],df_flat['8th'],df_flat['Year']), axis=-1)
            hovertemplate = ('1st: %{customdata[0]}<br>' + '2nd: %{customdata[1]}<br>' +'3rd: %{customdata[2]}<br>' +'4th: %{customdata[3]}<br>' +'5th: %{customdata[4]}<br>' +'6th: %{customdata[5]}<br>' +'8th: %{customdata[6]}<br>' +
        'Date: %{customdata[7]}<br>' 
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
            
            fourth_a=px.get_trendline_results(fig).px_fit_results.iloc[3].rsquared
            fourth_const = px.get_trendline_results(fig).px_fit_results.iloc[3].params[0]
            fourth_x1=px.get_trendline_results(fig).px_fit_results.iloc[3].params[1]

            fifth_a=px.get_trendline_results(fig).px_fit_results.iloc[4].rsquared
            fifth_const = px.get_trendline_results(fig).px_fit_results.iloc[4].params[0]
            fifth_x1=px.get_trendline_results(fig).px_fit_results.iloc[4].params[1]

            sixth_a=px.get_trendline_results(fig).px_fit_results.iloc[5].rsquared
            sixth_const = px.get_trendline_results(fig).px_fit_results.iloc[5].params[0]
            sixth_x1=px.get_trendline_results(fig).px_fit_results.iloc[5].params[1]

            eigth_a=px.get_trendline_results(fig).px_fit_results.iloc[6].rsquared
            eigth_const = px.get_trendline_results(fig).px_fit_results.iloc[6].params[0]
            eigth_x1=px.get_trendline_results(fig).px_fit_results.iloc[6].params[1]

            c1,c2=st.columns(2)
            with c1:
                st.write(f"1st = {round(first_x1,6)}(Year) + {round(first_const,3)}")
                st.write(f"R-squared = {round(first_a,3)}")

                st.write(f"2nd = {round(second_x1,6)}(Year) + {round(second_const,3)}")
                st.write(f"R-squared = {round(second_a,3)}")

                st.write(f"3rd = {round(third_x1,6)}(Year) + {round(third_const,3)}")
                st.write(f"R-squared = {round(third_a,3)}")

                st.write(f"4th = {round(fourth_x1,6)}(Year) + {round(fourth_const,3)}")
                st.write(f"R-squared = {round(fourth_a,3)}")
            with c2:
                st.write(f"5th = {round(fifth_x1,6)}(Year) + {round(fifth_const,3)}")
                st.write(f"R-squared = {round(fifth_a,3)}")

                st.write(f"6th = {round(sixth_x1,6)}(Year) + {round(sixth_const,3)}")
                st.write(f"R-squared = {round(sixth_a,3)}")

                st.write(f"8th = {round(eigth_x1,6)}(Year) + {round(eigth_const,3)}")
                st.write(f"R-squared = {round(eigth_a,3)}")


        with col2:
            predict_year = st.number_input("Select year for fastest time prediction:",min_value=2020,max_value=3000,value=2024,step=1)


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


            fourth_m, fourth_s = divmod(fourth_x1*predict_year +fourth_const, 60)
            fourth_h, fourth_m = divmod(fourth_m, 60)
            fourth_m = int(fourth_m)
            fourth_s=round(fourth_s,3)
            if fourth_s<10:
                fourth_s="0"+str(fourth_s)           
            st.write(f"This trend predicts a fourth qualifying time of {fourth_s} in {predict_year}.")


            fifth_m, fifth_s = divmod(fifth_x1*predict_year +fifth_const, 60)
            fifth_h, fifth_m = divmod(fifth_m, 60)
            fifth_m = int(fifth_m)
            fifth_s=round(fifth_s,3)
            if fifth_s<10:
                fifth_s="0"+str(fifth_s)           
            st.write(f"This trend predicts a fifth qualifying time of {fifth_s} in {predict_year}.")

            sixth_m, sixth_s = divmod(sixth_x1*predict_year +sixth_const, 60)
            sixth_h, sixth_m = divmod(sixth_m, 60)
            sixth_m = int(sixth_m)
            sixth_s=round(sixth_s,3)
            if sixth_s<10:
                sixth_s="0"+str(sixth_s)           
            st.write(f"This trend predicts a sixth qualifying time of {sixth_s} in {predict_year}.")

            eigth_m, eigth_s = divmod(eigth_x1*predict_year +eigth_const, 60)
            eigth_h, eigth_m = divmod(eigth_m, 60)
            eigth_m = int(eigth_m)
            eigth_s=round(eigth_s,3)
            if eigth_s<10:
                eigth_s="0"+str(eigth_s)           
            st.write(f"This trend predicts an eigth qualifying time of {eigth_s} in {predict_year}.")


    if race_type=="Junior Women's Team Sprint":
        
        @st.cache_data
        def get_placing_data_from_excel():
            df = pd.read_excel(
                io='pages/WR_progressions/Junior_Progression.xlsx',
                engine ='openpyxl',
                sheet_name='W TS',
                skiprows=0,
                usecols='A:F',
                nrows=150
                )
            #df = df.replace(',','')


            return df




        c1,c2=st.columns([1,3])
        with c1:

            


            df= get_placing_data_from_excel()
            df_master=df
            df_show = df
            df_show=df_show.loc[(df_show["Rank"]==1) | (df_show["Rank"]==2) |(df_show["Rank"]==3) | (df_show["Rank"]==4) |(df_show["Rank"]==5) | (df_show["Rank"]==6) ].reset_index(drop=True)
            df_show
                
                


        with c2:
            date_range = st.slider(
    "Restrict date range?",
            value = (df_show["Year"].min(),df_show["Year"].max()),
                min_value = df_show["Year"].min(),
                max_value = df_show["Year"].max())
            

            time_range = st.slider(
    "Restrict time range?",
            value = (df_show["Time"].min(),df_show["Time"].max()),
                min_value = df_show["Time"].min(),
                max_value = df_show["Time"].max())

            df_mask = df_show.mask(df_show["Year"] < date_range[0])
            df_mask = df_mask.mask(df_mask["Year"] > date_range[1])
            df_mask = df_mask.mask(df_mask["Time"] < time_range[0])
            df_mask = df_mask.mask(df_mask["Time"] > time_range[1])
            df_mask=df_mask.dropna()
            df_flat = df_mask.pivot(index='Year', columns='Rank')

            df_flat = df_flat[ 'Time']
            df_flat['Year'] = df_flat.index
            df_flat=df_flat.rename(columns={1: "1st", 2: "2nd", 3: "3rd", 4: "4th", 5: "5th", 6: "6th"})
            
            

            fig = px.scatter(df_flat, x="Year", y = ["1st","2nd","3rd","4th","5th","6th"], title="Junior Women's Team Sprint World Champs Placing Progression",trendline="ols", color_discrete_sequence=['gold',"silver","darkorange","lightpink","teal","mediumvioletred","mediumaquamarine","olive"])
            customdata = np.stack((df_flat['1st'], df_flat['2nd'], df_flat['3rd'],df_flat['4th'],df_flat['5th'],df_flat['6th'],df_flat['Year']), axis=-1)
            hovertemplate = ('1st: %{customdata[0]}<br>' + '2nd: %{customdata[1]}<br>' +'3rd: %{customdata[2]}<br>' +'4th: %{customdata[3]}<br>' +'5th: %{customdata[4]}<br>' +'6th: %{customdata[5]}<br>'  +
        'Date: %{customdata[6]}<br>' 
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
            
            fourth_a=px.get_trendline_results(fig).px_fit_results.iloc[3].rsquared
            fourth_const = px.get_trendline_results(fig).px_fit_results.iloc[3].params[0]
            fourth_x1=px.get_trendline_results(fig).px_fit_results.iloc[3].params[1]

            fifth_a=px.get_trendline_results(fig).px_fit_results.iloc[4].rsquared
            fifth_const = px.get_trendline_results(fig).px_fit_results.iloc[4].params[0]
            fifth_x1=px.get_trendline_results(fig).px_fit_results.iloc[4].params[1]

            sixth_a=px.get_trendline_results(fig).px_fit_results.iloc[5].rsquared
            sixth_const = px.get_trendline_results(fig).px_fit_results.iloc[5].params[0]
            sixth_x1=px.get_trendline_results(fig).px_fit_results.iloc[5].params[1]



            c1,c2=st.columns(2)
            with c1:
                st.write(f"1st = {round(first_x1,6)}(Year) + {round(first_const,3)}")
                st.write(f"R-squared = {round(first_a,3)}")

                st.write(f"2nd = {round(second_x1,6)}(Year) + {round(second_const,3)}")
                st.write(f"R-squared = {round(second_a,3)}")

                st.write(f"3rd = {round(third_x1,6)}(Year) + {round(third_const,3)}")
                st.write(f"R-squared = {round(third_a,3)}")
            with c2:
                st.write(f"4th = {round(fourth_x1,6)}(Year) + {round(fourth_const,3)}")
                st.write(f"R-squared = {round(fourth_a,3)}")
            
                st.write(f"5th = {round(fifth_x1,6)}(Year) + {round(fifth_const,3)}")
                st.write(f"R-squared = {round(fifth_a,3)}")

                st.write(f"6th = {round(sixth_x1,6)}(Year) + {round(sixth_const,3)}")
                st.write(f"R-squared = {round(sixth_a,3)}")




        with col2:
            predict_year = st.number_input("Select year for fastest time prediction:",min_value=2020,max_value=3000,value=2024,step=1)


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


            fourth_m, fourth_s = divmod(fourth_x1*predict_year +fourth_const, 60)
            fourth_h, fourth_m = divmod(fourth_m, 60)
            fourth_m = int(fourth_m)
            fourth_s=round(fourth_s,3)
            if fourth_s<10:
                fourth_s="0"+str(fourth_s)           
            st.write(f"This trend predicts a fourth qualifying time of {fourth_s} in {predict_year}.")


            fifth_m, fifth_s = divmod(fifth_x1*predict_year +fifth_const, 60)
            fifth_h, fifth_m = divmod(fifth_m, 60)
            fifth_m = int(fifth_m)
            fifth_s=round(fifth_s,3)
            if fifth_s<10:
                fifth_s="0"+str(fifth_s)           
            st.write(f"This trend predicts a fifth qualifying time of {fifth_s} in {predict_year}.")

            sixth_m, sixth_s = divmod(sixth_x1*predict_year +sixth_const, 60)
            sixth_h, sixth_m = divmod(sixth_m, 60)
            sixth_m = int(sixth_m)
            sixth_s=round(sixth_s,3)
            if sixth_s<10:
                sixth_s="0"+str(sixth_s)           
            st.write(f"This trend predicts a sixth qualifying time of {sixth_s} in {predict_year}.")

            
            
            
            
            
    if race_type=="Junior Men's Team Pursuit":
        
        @st.cache_data
        def get_placing_data_from_excel():
            df = pd.read_excel(
                io='pages/WR_progressions/Junior_Progression.xlsx',
                engine ='openpyxl',
                sheet_name='M TP',
                skiprows=0,
                usecols='A:G',
                nrows=300
                )
            #df = df.replace(',','')


            return df




        c1,c2=st.columns([1,3])
        with c1:

            


            df= get_placing_data_from_excel()
            df_master=df
            df_show = df
            df_show=df_show.loc[(df_show["Rank"]==1) | (df_show["Rank"]==2) |(df_show["Rank"]==3) | (df_show["Rank"]==4) |(df_show["Rank"]==5) | (df_show["Rank"]==6) |(df_show["Rank"]==8) | (df_show["Rank"]==16)].reset_index(drop=True)
            df_show
                
                


        with c2:
            date_range = st.slider(
    "Restrict date range?",
            value = (df_show["Year"].min(),df_show["Year"].max()),
                min_value = df_show["Year"].min(),
                max_value = df_show["Year"].max())
            

            time_range = st.slider(
    "Restrict time range?",
            value = (df_show["Seconds"].min(),df_show["Seconds"].max()),
                min_value = df_show["Seconds"].min(),
                max_value = df_show["Seconds"].max())

            df_mask = df_show.mask(df_show["Year"] < date_range[0])
            df_mask = df_mask.mask(df_mask["Year"] > date_range[1])
            df_mask = df_mask.mask(df_mask["Seconds"] < time_range[0])
            df_mask = df_mask.mask(df_mask["Seconds"] > time_range[1])
            df_mask=df_mask.dropna()
            
            
            df_flat = df_mask.pivot(index='Year', columns='Rank')
            df_flat = df_flat['Seconds']
            
            df_flat['Year'] = df_flat.index
            df_flat=df_flat.rename(columns={1: "1st", 2: "2nd", 3: "3rd", 4: "4th", 5: "5th", 6: "6th", 8: "8th", 16: "16th"})
            
            

            fig = px.scatter(df_flat, x="Year", y = ["1st","2nd","3rd","4th","5th","6th","8th","16th"], title="Junior Men's Team Pursuit World Champs Placing Progression",trendline="ols", color_discrete_sequence=['gold',"silver","darkorange","lightpink","teal","mediumvioletred","mediumaquamarine","olive"])
            customdata = np.stack((df_flat['1st'], df_flat['2nd'], df_flat['3rd'],df_flat['4th'],df_flat['5th'],df_flat['6th'],df_flat['8th'],df_flat['16th'],df_flat['Year']), axis=-1)
            hovertemplate = ('1st: %{customdata[0]}<br>' + '2nd: %{customdata[1]}<br>' +'3rd: %{customdata[2]}<br>' +'4th: %{customdata[3]}<br>' +'5th: %{customdata[4]}<br>' +'6th: %{customdata[5]}<br>' +'8th: %{customdata[6]}<br>' +'16th: %{customdata[7]}<br>' +
        'Date: %{customdata[8]}<br>' 
        '<extra></extra>')
            fig.update_traces(customdata=customdata, hovertemplate=hovertemplate)
            st.plotly_chart(fig, use_container_width=True)
            first_a=px.get_trendline_results(fig).px_fit_results.iloc[0].rsquared
            first_const = px.get_trendline_results(fig).px_fit_results.iloc[0].params[0]
            first_x1=px.get_trendline_results(fig).px_fit_results.iloc[0].params[1]

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
            
            fourth_a=px.get_trendline_results(fig).px_fit_results.iloc[3].rsquared
            fourth_const = px.get_trendline_results(fig).px_fit_results.iloc[3].params[0]
            fourth_x1=px.get_trendline_results(fig).px_fit_results.iloc[3].params[1]

            fifth_a=px.get_trendline_results(fig).px_fit_results.iloc[4].rsquared
            fifth_const = px.get_trendline_results(fig).px_fit_results.iloc[4].params[0]
            fifth_x1=px.get_trendline_results(fig).px_fit_results.iloc[4].params[1]

            sixth_a=px.get_trendline_results(fig).px_fit_results.iloc[5].rsquared
            sixth_const = px.get_trendline_results(fig).px_fit_results.iloc[5].params[0]
            sixth_x1=px.get_trendline_results(fig).px_fit_results.iloc[5].params[1]

            eigth_a=px.get_trendline_results(fig).px_fit_results.iloc[6].rsquared
            eigth_const = px.get_trendline_results(fig).px_fit_results.iloc[6].params[0]
            eigth_x1=px.get_trendline_results(fig).px_fit_results.iloc[6].params[1]

            sixteenth_a=px.get_trendline_results(fig).px_fit_results.iloc[7].rsquared
            sixteenth_const = px.get_trendline_results(fig).px_fit_results.iloc[7].params[0]
            sixteenth_x1=px.get_trendline_results(fig).px_fit_results.iloc[7].params[1]
            c1,c2=st.columns(2)
            with c1:
                st.write(f"1st = {round(first_x1,6)}(Year) + {round(first_const,3)}")
                st.write(f"R-squared = {round(first_a,3)}")

                st.write(f"2nd = {round(second_x1,6)}(Year) + {round(second_const,3)}")
                st.write(f"R-squared = {round(second_a,3)}")

                st.write(f"3rd = {round(third_x1,6)}(Year) + {round(third_const,3)}")
                st.write(f"R-squared = {round(third_a,3)}")

                st.write(f"4th = {round(fourth_x1,6)}(Year) + {round(fourth_const,3)}")
                st.write(f"R-squared = {round(fourth_a,3)}")
            with c2:
                st.write(f"5th = {round(fifth_x1,6)}(Year) + {round(fifth_const,3)}")
                st.write(f"R-squared = {round(fifth_a,3)}")

                st.write(f"6th = {round(sixth_x1,6)}(Year) + {round(sixth_const,3)}")
                st.write(f"R-squared = {round(sixth_a,3)}")

                st.write(f"8th = {round(eigth_x1,6)}(Year) + {round(eigth_const,3)}")
                st.write(f"R-squared = {round(eigth_a,3)}")

                st.write(f"16th = {round(sixteenth_x1,6)}(Year) + {round(sixteenth_const,3)}")
                st.write(f"R-squared = {round(sixteenth_a,3)}")

        with col2:
            predict_year = st.number_input("Select year for fastest time prediction:",min_value=2020,max_value=3000,value=2024,step=1)


            first_m, first_s = divmod(first_x1*predict_year +first_const, 60)
            first_h, first_m = divmod(first_m, 60)
            first_m = int(first_m)
            first_s=round(first_s,3)
            if first_s<10:
                first_s="0"+str(first_s)           
            st.write(f"This trend predicts a top qualifying time of {first_m}:{first_s} in {predict_year}.")


            second_m, second_s = divmod(second_x1*predict_year +second_const, 60)
            second_h, second_m = divmod(second_m, 60)
            second_m = int(second_m)
            second_s=round(second_s,3)
            if second_s<10:
                second_s="0"+str(second_s)           
            st.write(f"This trend predicts a second qualifying time of {second_m}:{second_s} in {predict_year}.")

            third_m, third_s = divmod(third_x1*predict_year +third_const, 60)
            third_h, third_m = divmod(third_m, 60)
            third_m = int(third_m)
            third_s=round(third_s,3)
            if third_s<10:
                third_s="0"+str(third_s)           
            st.write(f"This trend predicts a third qualifying time of {third_m}:{third_s} in {predict_year}.")


            fourth_m, fourth_s = divmod(fourth_x1*predict_year +fourth_const, 60)
            fourth_h, fourth_m = divmod(fourth_m, 60)
            fourth_m = int(fourth_m)
            fourth_s=round(fourth_s,3)
            if fourth_s<10:
                fourth_s="0"+str(fourth_s)           
            st.write(f"This trend predicts a fourth qualifying time of {fourth_m}:{fourth_s} in {predict_year}.")


            fifth_m, fifth_s = divmod(fifth_x1*predict_year +fifth_const, 60)
            fifth_h, fifth_m = divmod(fifth_m, 60)
            fifth_m = int(fifth_m)
            fifth_s=round(fifth_s,3)
            if fifth_s<10:
                fifth_s="0"+str(fifth_s)           
            st.write(f"This trend predicts a fifth qualifying time of {fifth_m}:{fifth_s} in {predict_year}.")

            sixth_m, sixth_s = divmod(sixth_x1*predict_year +sixth_const, 60)
            sixth_h, sixth_m = divmod(sixth_m, 60)
            sixth_m = int(sixth_m)
            sixth_s=round(sixth_s,3)
            if sixth_s<10:
                sixth_s="0"+str(sixth_s)           
            st.write(f"This trend predicts a sixth qualifying time of {sixth_m}:{sixth_s} in {predict_year}.")

            eigth_m, eigth_s = divmod(eigth_x1*predict_year +eigth_const, 60)
            eigth_h, eigth_m = divmod(eigth_m, 60)
            eigth_m = int(eigth_m)
            eigth_s=round(eigth_s,3)
            if eigth_s<10:
                eigth_s="0"+str(eigth_s)           
            st.write(f"This trend predicts an eigth qualifying time of {eigth_m}:{eigth_s} in {predict_year}.")

            sixteenth_m, sixteenth_s = divmod(sixteenth_x1*predict_year +sixteenth_const, 60)
            sixteenth_h, sixteenth_m = divmod(sixteenth_m, 60)
            sixteenth_m = int(sixteenth_m)
            sixteenth_s=round(sixteenth_s,3)
            if sixteenth_s<10:
                sixteenth_s="0"+str(sixteenth_s)           
            st.write(f"This trend predicts a sixteenth qualifying time of {sixteenth_m}:{sixteenth_s} in {predict_year}.")
            
            
            
            
    if race_type=="Junior Women's Team Pursuit":
        
        @st.cache_data
        def get_placing_data_from_excel():
            df = pd.read_excel(
                io='pages/WR_progressions/Junior_Progression.xlsx',
                engine ='openpyxl',
                sheet_name='W TP',
                skiprows=0,
                usecols='A:G',
                nrows=300
                )
            #df = df.replace(',','')


            return df




        c1,c2=st.columns([1,3])
        with c1:

            


            df= get_placing_data_from_excel()
            df_master=df
            df_show = df
            df_show=df_show.loc[(df_show["Rank"]==1) | (df_show["Rank"]==2) |(df_show["Rank"]==3) | (df_show["Rank"]==4) |(df_show["Rank"]==5) | (df_show["Rank"]==6) |(df_show["Rank"]==8) ].reset_index(drop=True)
            df_show
                
                


        with c2:
            date_range = st.slider(
    "Restrict date range?",
            value = (df_show["Year"].min(),df_show["Year"].max()),
                min_value = df_show["Year"].min(),
                max_value = df_show["Year"].max())
            

            time_range = st.slider(
    "Restrict time range?",
            value = (df_show["Seconds"].min(),df_show["Seconds"].max()),
                min_value = df_show["Seconds"].min(),
                max_value = df_show["Seconds"].max())

            df_mask = df_show.mask(df_show["Year"] < date_range[0])
            df_mask = df_mask.mask(df_mask["Year"] > date_range[1])
            df_mask = df_mask.mask(df_mask["Seconds"] < time_range[0])
            df_mask = df_mask.mask(df_mask["Seconds"] > time_range[1])
            df_mask=df_mask.dropna()
            
            
            df_flat = df_mask.pivot(index='Year', columns='Rank')
            df_flat = df_flat['Seconds']
            
            df_flat['Year'] = df_flat.index
            df_flat=df_flat.rename(columns={1: "1st", 2: "2nd", 3: "3rd", 4: "4th", 5: "5th", 6: "6th", 8: "8th", 16: "16th"})
            
            

            fig = px.scatter(df_flat, x="Year", y = ["1st","2nd","3rd","4th","5th","6th","8th"], title="Junior Women's Team Pursuit World Champs Placing Progression",trendline="ols", color_discrete_sequence=['gold',"silver","darkorange","lightpink","teal","mediumvioletred","mediumaquamarine","olive"])
            customdata = np.stack((df_flat['1st'], df_flat['2nd'], df_flat['3rd'],df_flat['4th'],df_flat['5th'],df_flat['6th'],df_flat['8th'],df_flat['Year']), axis=-1)
            hovertemplate = ('1st: %{customdata[0]}<br>' + '2nd: %{customdata[1]}<br>' +'3rd: %{customdata[2]}<br>' +'4th: %{customdata[3]}<br>' +'5th: %{customdata[4]}<br>' +'6th: %{customdata[5]}<br>' +'8th: %{customdata[6]}<br>'  +
        'Date: %{customdata[7]}<br>' 
        '<extra></extra>')
            fig.update_traces(customdata=customdata, hovertemplate=hovertemplate)
            st.plotly_chart(fig, use_container_width=True)
            first_a=px.get_trendline_results(fig).px_fit_results.iloc[0].rsquared
            first_const = px.get_trendline_results(fig).px_fit_results.iloc[0].params[0]
            first_x1=px.get_trendline_results(fig).px_fit_results.iloc[0].params[1]

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
            
            fourth_a=px.get_trendline_results(fig).px_fit_results.iloc[3].rsquared
            fourth_const = px.get_trendline_results(fig).px_fit_results.iloc[3].params[0]
            fourth_x1=px.get_trendline_results(fig).px_fit_results.iloc[3].params[1]

            fifth_a=px.get_trendline_results(fig).px_fit_results.iloc[4].rsquared
            fifth_const = px.get_trendline_results(fig).px_fit_results.iloc[4].params[0]
            fifth_x1=px.get_trendline_results(fig).px_fit_results.iloc[4].params[1]

            sixth_a=px.get_trendline_results(fig).px_fit_results.iloc[5].rsquared
            sixth_const = px.get_trendline_results(fig).px_fit_results.iloc[5].params[0]
            sixth_x1=px.get_trendline_results(fig).px_fit_results.iloc[5].params[1]

            eigth_a=px.get_trendline_results(fig).px_fit_results.iloc[6].rsquared
            eigth_const = px.get_trendline_results(fig).px_fit_results.iloc[6].params[0]
            eigth_x1=px.get_trendline_results(fig).px_fit_results.iloc[6].params[1]

            c1,c2=st.columns(2)
            with c1:
                st.write(f"1st = {round(first_x1,6)}(Year) + {round(first_const,3)}")
                st.write(f"R-squared = {round(first_a,3)}")

                st.write(f"2nd = {round(second_x1,6)}(Year) + {round(second_const,3)}")
                st.write(f"R-squared = {round(second_a,3)}")

                st.write(f"3rd = {round(third_x1,6)}(Year) + {round(third_const,3)}")
                st.write(f"R-squared = {round(third_a,3)}")

                st.write(f"4th = {round(fourth_x1,6)}(Year) + {round(fourth_const,3)}")
                st.write(f"R-squared = {round(fourth_a,3)}")
            with c2:
                st.write(f"5th = {round(fifth_x1,6)}(Year) + {round(fifth_const,3)}")
                st.write(f"R-squared = {round(fifth_a,3)}")

                st.write(f"6th = {round(sixth_x1,6)}(Year) + {round(sixth_const,3)}")
                st.write(f"R-squared = {round(sixth_a,3)}")

                st.write(f"8th = {round(eigth_x1,6)}(Year) + {round(eigth_const,3)}")
                st.write(f"R-squared = {round(eigth_a,3)}")


        with col2:
            predict_year = st.number_input("Select year for fastest time prediction:",min_value=2020,max_value=3000,value=2024,step=1)


            first_m, first_s = divmod(first_x1*predict_year +first_const, 60)
            first_h, first_m = divmod(first_m, 60)
            first_m = int(first_m)
            first_s=round(first_s,3)
            if first_s<10:
                first_s="0"+str(first_s)           
            st.write(f"This trend predicts a top qualifying time of {first_m}:{first_s} in {predict_year}.")


            second_m, second_s = divmod(second_x1*predict_year +second_const, 60)
            second_h, second_m = divmod(second_m, 60)
            second_m = int(second_m)
            second_s=round(second_s,3)
            if second_s<10:
                second_s="0"+str(second_s)           
            st.write(f"This trend predicts a second qualifying time of {second_m}:{second_s} in {predict_year}.")

            third_m, third_s = divmod(third_x1*predict_year +third_const, 60)
            third_h, third_m = divmod(third_m, 60)
            third_m = int(third_m)
            third_s=round(third_s,3)
            if third_s<10:
                third_s="0"+str(third_s)           
            st.write(f"This trend predicts a third qualifying time of {third_m}:{third_s} in {predict_year}.")


            fourth_m, fourth_s = divmod(fourth_x1*predict_year +fourth_const, 60)
            fourth_h, fourth_m = divmod(fourth_m, 60)
            fourth_m = int(fourth_m)
            fourth_s=round(fourth_s,3)
            if fourth_s<10:
                fourth_s="0"+str(fourth_s)           
            st.write(f"This trend predicts a fourth qualifying time of {fourth_m}:{fourth_s} in {predict_year}.")


            fifth_m, fifth_s = divmod(fifth_x1*predict_year +fifth_const, 60)
            fifth_h, fifth_m = divmod(fifth_m, 60)
            fifth_m = int(fifth_m)
            fifth_s=round(fifth_s,3)
            if fifth_s<10:
                fifth_s="0"+str(fifth_s)           
            st.write(f"This trend predicts a fifth qualifying time of {fifth_m}:{fifth_s} in {predict_year}.")

            sixth_m, sixth_s = divmod(sixth_x1*predict_year +sixth_const, 60)
            sixth_h, sixth_m = divmod(sixth_m, 60)
            sixth_m = int(sixth_m)
            sixth_s=round(sixth_s,3)
            if sixth_s<10:
                sixth_s="0"+str(sixth_s)           
            st.write(f"This trend predicts a sixth qualifying time of {sixth_m}:{sixth_s} in {predict_year}.")

            eigth_m, eigth_s = divmod(eigth_x1*predict_year +eigth_const, 60)
            eigth_h, eigth_m = divmod(eigth_m, 60)
            eigth_m = int(eigth_m)
            eigth_s=round(eigth_s,3)
            if eigth_s<10:
                eigth_s="0"+str(eigth_s)           
            st.write(f"This trend predicts an eigth qualifying time of {eigth_m}:{eigth_s} in {predict_year}.")


            
            
            
            
    if race_type=="Junior Men's Individual Pursuit":
        
        @st.cache_data
        def get_placing_data_from_excel():
            df = pd.read_excel(
                io='pages/WR_progressions/Junior_Progression.xlsx',
                engine ='openpyxl',
                sheet_name='M IP',
                skiprows=0,
                usecols='A:G',
                nrows=500
                )
            #df = df.replace(',','')


            return df




        c1,c2=st.columns([1,3])
        with c1:

            


            df= get_placing_data_from_excel()
            df_master=df
            df_show = df
            df_show=df_show.loc[(df_show["Rank"]==1) | (df_show["Rank"]==2) |(df_show["Rank"]==3) | (df_show["Rank"]==4) |(df_show["Rank"]==5) | (df_show["Rank"]==6) |(df_show["Rank"]==8) | (df_show["Rank"]==16)].reset_index(drop=True)
            df_show
                
                


        with c2:
            date_range = st.slider(
    "Restrict date range?",
            value = (df_show["Year"].min(),df_show["Year"].max()),
                min_value = df_show["Year"].min(),
                max_value = df_show["Year"].max())
            

            time_range = st.slider(
    "Restrict time range?",
            value = (df_show["Seconds"].min(),df_show["Seconds"].max()),
                min_value = df_show["Seconds"].min(),
                max_value = df_show["Seconds"].max())

            df_mask = df_show.mask(df_show["Year"] < date_range[0])
            df_mask = df_mask.mask(df_mask["Year"] > date_range[1])
            df_mask = df_mask.mask(df_mask["Seconds"] < time_range[0])
            df_mask = df_mask.mask(df_mask["Seconds"] > time_range[1])
            df_mask=df_mask.dropna()
            
            
            df_flat = df_mask.pivot(index='Year', columns='Rank')
            df_flat = df_flat['Seconds']
            
            df_flat['Year'] = df_flat.index
            df_flat=df_flat.rename(columns={1: "1st", 2: "2nd", 3: "3rd", 4: "4th", 5: "5th", 6: "6th", 8: "8th", 16: "16th"})
            
            

            fig = px.scatter(df_flat, x="Year", y = ["1st","2nd","3rd","4th","5th","6th","8th","16th"], title="Junior Men's Individual Pursuit World Champs Placing Progression",trendline="ols", color_discrete_sequence=['gold',"silver","darkorange","lightpink","teal","mediumvioletred","mediumaquamarine","olive"])
            customdata = np.stack((df_flat['1st'], df_flat['2nd'], df_flat['3rd'],df_flat['4th'],df_flat['5th'],df_flat['6th'],df_flat['8th'],df_flat['16th'],df_flat['Year']), axis=-1)
            hovertemplate = ('1st: %{customdata[0]}<br>' + '2nd: %{customdata[1]}<br>' +'3rd: %{customdata[2]}<br>' +'4th: %{customdata[3]}<br>' +'5th: %{customdata[4]}<br>' +'6th: %{customdata[5]}<br>' +'8th: %{customdata[6]}<br>' +'16th: %{customdata[7]}<br>' +
        'Date: %{customdata[8]}<br>' 
        '<extra></extra>')
            fig.update_traces(customdata=customdata, hovertemplate=hovertemplate)
            st.plotly_chart(fig, use_container_width=True)
            first_a=px.get_trendline_results(fig).px_fit_results.iloc[0].rsquared
            first_const = px.get_trendline_results(fig).px_fit_results.iloc[0].params[0]
            first_x1=px.get_trendline_results(fig).px_fit_results.iloc[0].params[1]

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
            
            fourth_a=px.get_trendline_results(fig).px_fit_results.iloc[3].rsquared
            fourth_const = px.get_trendline_results(fig).px_fit_results.iloc[3].params[0]
            fourth_x1=px.get_trendline_results(fig).px_fit_results.iloc[3].params[1]

            fifth_a=px.get_trendline_results(fig).px_fit_results.iloc[4].rsquared
            fifth_const = px.get_trendline_results(fig).px_fit_results.iloc[4].params[0]
            fifth_x1=px.get_trendline_results(fig).px_fit_results.iloc[4].params[1]

            sixth_a=px.get_trendline_results(fig).px_fit_results.iloc[5].rsquared
            sixth_const = px.get_trendline_results(fig).px_fit_results.iloc[5].params[0]
            sixth_x1=px.get_trendline_results(fig).px_fit_results.iloc[5].params[1]

            eigth_a=px.get_trendline_results(fig).px_fit_results.iloc[6].rsquared
            eigth_const = px.get_trendline_results(fig).px_fit_results.iloc[6].params[0]
            eigth_x1=px.get_trendline_results(fig).px_fit_results.iloc[6].params[1]

            sixteenth_a=px.get_trendline_results(fig).px_fit_results.iloc[7].rsquared
            sixteenth_const = px.get_trendline_results(fig).px_fit_results.iloc[7].params[0]
            sixteenth_x1=px.get_trendline_results(fig).px_fit_results.iloc[7].params[1]
            c1,c2=st.columns(2)
            with c1:
                st.write(f"1st = {round(first_x1,6)}(Year) + {round(first_const,3)}")
                st.write(f"R-squared = {round(first_a,3)}")

                st.write(f"2nd = {round(second_x1,6)}(Year) + {round(second_const,3)}")
                st.write(f"R-squared = {round(second_a,3)}")

                st.write(f"3rd = {round(third_x1,6)}(Year) + {round(third_const,3)}")
                st.write(f"R-squared = {round(third_a,3)}")

                st.write(f"4th = {round(fourth_x1,6)}(Year) + {round(fourth_const,3)}")
                st.write(f"R-squared = {round(fourth_a,3)}")
            with c2:
                st.write(f"5th = {round(fifth_x1,6)}(Year) + {round(fifth_const,3)}")
                st.write(f"R-squared = {round(fifth_a,3)}")

                st.write(f"6th = {round(sixth_x1,6)}(Year) + {round(sixth_const,3)}")
                st.write(f"R-squared = {round(sixth_a,3)}")

                st.write(f"8th = {round(eigth_x1,6)}(Year) + {round(eigth_const,3)}")
                st.write(f"R-squared = {round(eigth_a,3)}")

                st.write(f"16th = {round(sixteenth_x1,6)}(Year) + {round(sixteenth_const,3)}")
                st.write(f"R-squared = {round(sixteenth_a,3)}")

        with col2:
            predict_year = st.number_input("Select year for fastest time prediction:",min_value=2020,max_value=3000,value=2024,step=1)


            first_m, first_s = divmod(first_x1*predict_year +first_const, 60)
            first_h, first_m = divmod(first_m, 60)
            first_m = int(first_m)
            first_s=round(first_s,3)
            if first_s<10:
                first_s="0"+str(first_s)           
            st.write(f"This trend predicts a top qualifying time of {first_m}:{first_s} in {predict_year}.")


            second_m, second_s = divmod(second_x1*predict_year +second_const, 60)
            second_h, second_m = divmod(second_m, 60)
            second_m = int(second_m)
            second_s=round(second_s,3)
            if second_s<10:
                second_s="0"+str(second_s)           
            st.write(f"This trend predicts a second qualifying time of {second_m}:{second_s} in {predict_year}.")

            third_m, third_s = divmod(third_x1*predict_year +third_const, 60)
            third_h, third_m = divmod(third_m, 60)
            third_m = int(third_m)
            third_s=round(third_s,3)
            if third_s<10:
                third_s="0"+str(third_s)           
            st.write(f"This trend predicts a third qualifying time of {third_m}:{third_s} in {predict_year}.")


            fourth_m, fourth_s = divmod(fourth_x1*predict_year +fourth_const, 60)
            fourth_h, fourth_m = divmod(fourth_m, 60)
            fourth_m = int(fourth_m)
            fourth_s=round(fourth_s,3)
            if fourth_s<10:
                fourth_s="0"+str(fourth_s)           
            st.write(f"This trend predicts a fourth qualifying time of {fourth_m}:{fourth_s} in {predict_year}.")


            fifth_m, fifth_s = divmod(fifth_x1*predict_year +fifth_const, 60)
            fifth_h, fifth_m = divmod(fifth_m, 60)
            fifth_m = int(fifth_m)
            fifth_s=round(fifth_s,3)
            if fifth_s<10:
                fifth_s="0"+str(fifth_s)           
            st.write(f"This trend predicts a fifth qualifying time of {fifth_m}:{fifth_s} in {predict_year}.")

            sixth_m, sixth_s = divmod(sixth_x1*predict_year +sixth_const, 60)
            sixth_h, sixth_m = divmod(sixth_m, 60)
            sixth_m = int(sixth_m)
            sixth_s=round(sixth_s,3)
            if sixth_s<10:
                sixth_s="0"+str(sixth_s)           
            st.write(f"This trend predicts a sixth qualifying time of {sixth_m}:{sixth_s} in {predict_year}.")

            eigth_m, eigth_s = divmod(eigth_x1*predict_year +eigth_const, 60)
            eigth_h, eigth_m = divmod(eigth_m, 60)
            eigth_m = int(eigth_m)
            eigth_s=round(eigth_s,3)
            if eigth_s<10:
                eigth_s="0"+str(eigth_s)           
            st.write(f"This trend predicts an eigth qualifying time of {eigth_m}:{eigth_s} in {predict_year}.")

            sixteenth_m, sixteenth_s = divmod(sixteenth_x1*predict_year +sixteenth_const, 60)
            sixteenth_h, sixteenth_m = divmod(sixteenth_m, 60)
            sixteenth_m = int(sixteenth_m)
            sixteenth_s=round(sixteenth_s,3)
            if sixteenth_s<10:
                sixteenth_s="0"+str(sixteenth_s)           
            st.write(f"This trend predicts a sixteenth qualifying time of {sixteenth_m}:{sixteenth_s} in {predict_year}.")   
            
            
            
            
            
            
    if race_type=="Junior Women's Individual Pursuit":
        
        @st.cache_data
        def get_placing_data_from_excel():
            df = pd.read_excel(
                io='pages/WR_progressions/Junior_Progression.xlsx',
                engine ='openpyxl',
                sheet_name='W IP',
                skiprows=0,
                usecols='A:G',
                nrows=400
                )
            #df = df.replace(',','')


            return df




        c1,c2=st.columns([1,3])
        with c1:

            


            df= get_placing_data_from_excel()
            df_master=df
            df_show = df
            df_show=df_show.loc[(df_show["Rank"]==1) | (df_show["Rank"]==2) |(df_show["Rank"]==3) | (df_show["Rank"]==4) |(df_show["Rank"]==5) | (df_show["Rank"]==6) |(df_show["Rank"]==8) | (df_show["Rank"]==16)].reset_index(drop=True)
            df_show
                
                


        with c2:
            date_range = st.slider(
    "Restrict date range?",
            value = (df_show["Year"].min(),df_show["Year"].max()),
                min_value = df_show["Year"].min(),
                max_value = df_show["Year"].max())
            

            time_range = st.slider(
    "Restrict time range?",
            value = (df_show["Seconds"].min(),df_show["Seconds"].max()),
                min_value = df_show["Seconds"].min(),
                max_value = df_show["Seconds"].max())

            df_mask = df_show.mask(df_show["Year"] < date_range[0])
            df_mask = df_mask.mask(df_mask["Year"] > date_range[1])
            df_mask = df_mask.mask(df_mask["Seconds"] < time_range[0])
            df_mask = df_mask.mask(df_mask["Seconds"] > time_range[1])
            df_mask=df_mask.dropna()
            
            
            df_flat = df_mask.pivot(index='Year', columns='Rank')
            df_flat = df_flat['Seconds']
            
            df_flat['Year'] = df_flat.index
            df_flat=df_flat.rename(columns={1: "1st", 2: "2nd", 3: "3rd", 4: "4th", 5: "5th", 6: "6th", 8: "8th", 16: "16th"})
            
            

            fig = px.scatter(df_flat, x="Year", y = ["1st","2nd","3rd","4th","5th","6th","8th","16th"], title="Junior Women's Individual Pursuit World Champs Placing Progression",trendline="ols", color_discrete_sequence=['gold',"silver","darkorange","lightpink","teal","mediumvioletred","mediumaquamarine","olive"])
            customdata = np.stack((df_flat['1st'], df_flat['2nd'], df_flat['3rd'],df_flat['4th'],df_flat['5th'],df_flat['6th'],df_flat['8th'],df_flat['16th'],df_flat['Year']), axis=-1)
            hovertemplate = ('1st: %{customdata[0]}<br>' + '2nd: %{customdata[1]}<br>' +'3rd: %{customdata[2]}<br>' +'4th: %{customdata[3]}<br>' +'5th: %{customdata[4]}<br>' +'6th: %{customdata[5]}<br>' +'8th: %{customdata[6]}<br>' +'16th: %{customdata[7]}<br>' +
        'Date: %{customdata[8]}<br>' 
        '<extra></extra>')
            fig.update_traces(customdata=customdata, hovertemplate=hovertemplate)
            st.plotly_chart(fig, use_container_width=True)
            first_a=px.get_trendline_results(fig).px_fit_results.iloc[0].rsquared
            first_const = px.get_trendline_results(fig).px_fit_results.iloc[0].params[0]
            first_x1=px.get_trendline_results(fig).px_fit_results.iloc[0].params[1]

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
            
            fourth_a=px.get_trendline_results(fig).px_fit_results.iloc[3].rsquared
            fourth_const = px.get_trendline_results(fig).px_fit_results.iloc[3].params[0]
            fourth_x1=px.get_trendline_results(fig).px_fit_results.iloc[3].params[1]

            fifth_a=px.get_trendline_results(fig).px_fit_results.iloc[4].rsquared
            fifth_const = px.get_trendline_results(fig).px_fit_results.iloc[4].params[0]
            fifth_x1=px.get_trendline_results(fig).px_fit_results.iloc[4].params[1]

            sixth_a=px.get_trendline_results(fig).px_fit_results.iloc[5].rsquared
            sixth_const = px.get_trendline_results(fig).px_fit_results.iloc[5].params[0]
            sixth_x1=px.get_trendline_results(fig).px_fit_results.iloc[5].params[1]

            eigth_a=px.get_trendline_results(fig).px_fit_results.iloc[6].rsquared
            eigth_const = px.get_trendline_results(fig).px_fit_results.iloc[6].params[0]
            eigth_x1=px.get_trendline_results(fig).px_fit_results.iloc[6].params[1]

            sixteenth_a=px.get_trendline_results(fig).px_fit_results.iloc[7].rsquared
            sixteenth_const = px.get_trendline_results(fig).px_fit_results.iloc[7].params[0]
            sixteenth_x1=px.get_trendline_results(fig).px_fit_results.iloc[7].params[1]
            c1,c2=st.columns(2)
            with c1:
                st.write(f"1st = {round(first_x1,6)}(Year) + {round(first_const,3)}")
                st.write(f"R-squared = {round(first_a,3)}")

                st.write(f"2nd = {round(second_x1,6)}(Year) + {round(second_const,3)}")
                st.write(f"R-squared = {round(second_a,3)}")

                st.write(f"3rd = {round(third_x1,6)}(Year) + {round(third_const,3)}")
                st.write(f"R-squared = {round(third_a,3)}")

                st.write(f"4th = {round(fourth_x1,6)}(Year) + {round(fourth_const,3)}")
                st.write(f"R-squared = {round(fourth_a,3)}")
            with c2:
                st.write(f"5th = {round(fifth_x1,6)}(Year) + {round(fifth_const,3)}")
                st.write(f"R-squared = {round(fifth_a,3)}")

                st.write(f"6th = {round(sixth_x1,6)}(Year) + {round(sixth_const,3)}")
                st.write(f"R-squared = {round(sixth_a,3)}")

                st.write(f"8th = {round(eigth_x1,6)}(Year) + {round(eigth_const,3)}")
                st.write(f"R-squared = {round(eigth_a,3)}")

                st.write(f"16th = {round(sixteenth_x1,6)}(Year) + {round(sixteenth_const,3)}")
                st.write(f"R-squared = {round(sixteenth_a,3)}")

        with col2:
            predict_year = st.number_input("Select year for fastest time prediction:",min_value=2020,max_value=3000,value=2024,step=1)


            first_m, first_s = divmod(first_x1*predict_year +first_const, 60)
            first_h, first_m = divmod(first_m, 60)
            first_m = int(first_m)
            first_s=round(first_s,3)
            if first_s<10:
                first_s="0"+str(first_s)           
            st.write(f"This trend predicts a top qualifying time of {first_m}:{first_s} in {predict_year}.")


            second_m, second_s = divmod(second_x1*predict_year +second_const, 60)
            second_h, second_m = divmod(second_m, 60)
            second_m = int(second_m)
            second_s=round(second_s,3)
            if second_s<10:
                second_s="0"+str(second_s)           
            st.write(f"This trend predicts a second qualifying time of {second_m}:{second_s} in {predict_year}.")

            third_m, third_s = divmod(third_x1*predict_year +third_const, 60)
            third_h, third_m = divmod(third_m, 60)
            third_m = int(third_m)
            third_s=round(third_s,3)
            if third_s<10:
                third_s="0"+str(third_s)           
            st.write(f"This trend predicts a third qualifying time of {third_m}:{third_s} in {predict_year}.")


            fourth_m, fourth_s = divmod(fourth_x1*predict_year +fourth_const, 60)
            fourth_h, fourth_m = divmod(fourth_m, 60)
            fourth_m = int(fourth_m)
            fourth_s=round(fourth_s,3)
            if fourth_s<10:
                fourth_s="0"+str(fourth_s)           
            st.write(f"This trend predicts a fourth qualifying time of {fourth_m}:{fourth_s} in {predict_year}.")


            fifth_m, fifth_s = divmod(fifth_x1*predict_year +fifth_const, 60)
            fifth_h, fifth_m = divmod(fifth_m, 60)
            fifth_m = int(fifth_m)
            fifth_s=round(fifth_s,3)
            if fifth_s<10:
                fifth_s="0"+str(fifth_s)           
            st.write(f"This trend predicts a fifth qualifying time of {fifth_m}:{fifth_s} in {predict_year}.")

            sixth_m, sixth_s = divmod(sixth_x1*predict_year +sixth_const, 60)
            sixth_h, sixth_m = divmod(sixth_m, 60)
            sixth_m = int(sixth_m)
            sixth_s=round(sixth_s,3)
            if sixth_s<10:
                sixth_s="0"+str(sixth_s)           
            st.write(f"This trend predicts a sixth qualifying time of {sixth_m}:{sixth_s} in {predict_year}.")

            eigth_m, eigth_s = divmod(eigth_x1*predict_year +eigth_const, 60)
            eigth_h, eigth_m = divmod(eigth_m, 60)
            eigth_m = int(eigth_m)
            eigth_s=round(eigth_s,3)
            if eigth_s<10:
                eigth_s="0"+str(eigth_s)           
            st.write(f"This trend predicts an eigth qualifying time of {eigth_m}:{eigth_s} in {predict_year}.")

            sixteenth_m, sixteenth_s = divmod(sixteenth_x1*predict_year +sixteenth_const, 60)
            sixteenth_h, sixteenth_m = divmod(sixteenth_m, 60)
            sixteenth_m = int(sixteenth_m)
            sixteenth_s=round(sixteenth_s,3)
            if sixteenth_s<10:
                sixteenth_s="0"+str(sixteenth_s)           
            st.write(f"This trend predicts a sixteenth qualifying time of {sixteenth_m}:{sixteenth_s} in {predict_year}.")  
            
            
            
            
    if race_type=="Junior Men's Kilo":
        
        @st.cache_data
        def get_placing_data_from_excel():
            df = pd.read_excel(
                io='pages/WR_progressions/Junior_Progression.xlsx',
                engine ='openpyxl',
                sheet_name='M Kilo',
                skiprows=0,
                usecols='A:G',
                nrows=700
                )
            #df = df.replace(',','')


            return df




        c1,c2=st.columns([1,3])
        with c1:

            


            df= get_placing_data_from_excel()
            df_master=df
            df_show = df
            df_show=df_show.loc[(df_show["Rank"]==1) | (df_show["Rank"]==2) |(df_show["Rank"]==3) | (df_show["Rank"]==4) |(df_show["Rank"]==5) | (df_show["Rank"]==6) |(df_show["Rank"]==8) | (df_show["Rank"]==16)].reset_index(drop=True)
            df_show
                
                


        with c2:
            date_range = st.slider(
    "Restrict date range?",
            value = (df_show["Year"].min(),df_show["Year"].max()),
                min_value = df_show["Year"].min(),
                max_value = df_show["Year"].max())
            

            time_range = st.slider(
    "Restrict time range?",
            value = (df_show["Seconds"].min(),df_show["Seconds"].max()),
                min_value = df_show["Seconds"].min(),
                max_value = df_show["Seconds"].max())

            df_mask = df_show.mask(df_show["Year"] < date_range[0])
            df_mask = df_mask.mask(df_mask["Year"] > date_range[1])
            df_mask = df_mask.mask(df_mask["Seconds"] < time_range[0])
            df_mask = df_mask.mask(df_mask["Seconds"] > time_range[1])
            df_mask=df_mask.dropna()
            
            
            df_flat = df_mask.pivot(index='Year', columns='Rank')
            df_flat = df_flat['Seconds']
            
            df_flat['Year'] = df_flat.index
            df_flat=df_flat.rename(columns={1: "1st", 2: "2nd", 3: "3rd", 4: "4th", 5: "5th", 6: "6th", 8: "8th", 16: "16th"})
            
            

            fig = px.scatter(df_flat, x="Year", y = ["1st","2nd","3rd","4th","5th","6th","8th","16th"], title="Junior Men's Kilo World Champs Placing Progression",trendline="ols", color_discrete_sequence=['gold',"silver","darkorange","lightpink","teal","mediumvioletred","mediumaquamarine","olive"])
            customdata = np.stack((df_flat['1st'], df_flat['2nd'], df_flat['3rd'],df_flat['4th'],df_flat['5th'],df_flat['6th'],df_flat['8th'],df_flat['16th'],df_flat['Year']), axis=-1)
            hovertemplate = ('1st: %{customdata[0]}<br>' + '2nd: %{customdata[1]}<br>' +'3rd: %{customdata[2]}<br>' +'4th: %{customdata[3]}<br>' +'5th: %{customdata[4]}<br>' +'6th: %{customdata[5]}<br>' +'8th: %{customdata[6]}<br>' +'16th: %{customdata[7]}<br>' +
        'Date: %{customdata[8]}<br>' 
        '<extra></extra>')
            fig.update_traces(customdata=customdata, hovertemplate=hovertemplate)
            st.plotly_chart(fig, use_container_width=True)
            first_a=px.get_trendline_results(fig).px_fit_results.iloc[0].rsquared
            first_const = px.get_trendline_results(fig).px_fit_results.iloc[0].params[0]
            first_x1=px.get_trendline_results(fig).px_fit_results.iloc[0].params[1]

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
            
            fourth_a=px.get_trendline_results(fig).px_fit_results.iloc[3].rsquared
            fourth_const = px.get_trendline_results(fig).px_fit_results.iloc[3].params[0]
            fourth_x1=px.get_trendline_results(fig).px_fit_results.iloc[3].params[1]

            fifth_a=px.get_trendline_results(fig).px_fit_results.iloc[4].rsquared
            fifth_const = px.get_trendline_results(fig).px_fit_results.iloc[4].params[0]
            fifth_x1=px.get_trendline_results(fig).px_fit_results.iloc[4].params[1]

            sixth_a=px.get_trendline_results(fig).px_fit_results.iloc[5].rsquared
            sixth_const = px.get_trendline_results(fig).px_fit_results.iloc[5].params[0]
            sixth_x1=px.get_trendline_results(fig).px_fit_results.iloc[5].params[1]

            eigth_a=px.get_trendline_results(fig).px_fit_results.iloc[6].rsquared
            eigth_const = px.get_trendline_results(fig).px_fit_results.iloc[6].params[0]
            eigth_x1=px.get_trendline_results(fig).px_fit_results.iloc[6].params[1]

            sixteenth_a=px.get_trendline_results(fig).px_fit_results.iloc[7].rsquared
            sixteenth_const = px.get_trendline_results(fig).px_fit_results.iloc[7].params[0]
            sixteenth_x1=px.get_trendline_results(fig).px_fit_results.iloc[7].params[1]
            c1,c2=st.columns(2)
            with c1:
                st.write(f"1st = {round(first_x1,6)}(Year) + {round(first_const,3)}")
                st.write(f"R-squared = {round(first_a,3)}")

                st.write(f"2nd = {round(second_x1,6)}(Year) + {round(second_const,3)}")
                st.write(f"R-squared = {round(second_a,3)}")

                st.write(f"3rd = {round(third_x1,6)}(Year) + {round(third_const,3)}")
                st.write(f"R-squared = {round(third_a,3)}")

                st.write(f"4th = {round(fourth_x1,6)}(Year) + {round(fourth_const,3)}")
                st.write(f"R-squared = {round(fourth_a,3)}")
            with c2:
                st.write(f"5th = {round(fifth_x1,6)}(Year) + {round(fifth_const,3)}")
                st.write(f"R-squared = {round(fifth_a,3)}")

                st.write(f"6th = {round(sixth_x1,6)}(Year) + {round(sixth_const,3)}")
                st.write(f"R-squared = {round(sixth_a,3)}")

                st.write(f"8th = {round(eigth_x1,6)}(Year) + {round(eigth_const,3)}")
                st.write(f"R-squared = {round(eigth_a,3)}")

                st.write(f"16th = {round(sixteenth_x1,6)}(Year) + {round(sixteenth_const,3)}")
                st.write(f"R-squared = {round(sixteenth_a,3)}")

        with col2:
            predict_year = st.number_input("Select year for fastest time prediction:",min_value=2020,max_value=3000,value=2024,step=1)


            first_m, first_s = divmod(first_x1*predict_year +first_const, 60)
            first_h, first_m = divmod(first_m, 60)
            first_m = int(first_m)
            first_s=round(first_s,3)
            if first_s<10:
                first_s="0"+str(first_s)           
            st.write(f"This trend predicts a top qualifying time of {first_m}:{first_s} in {predict_year}.")


            second_m, second_s = divmod(second_x1*predict_year +second_const, 60)
            second_h, second_m = divmod(second_m, 60)
            second_m = int(second_m)
            second_s=round(second_s,3)
            if second_s<10:
                second_s="0"+str(second_s)           
            st.write(f"This trend predicts a second qualifying time of {second_m}:{second_s} in {predict_year}.")

            third_m, third_s = divmod(third_x1*predict_year +third_const, 60)
            third_h, third_m = divmod(third_m, 60)
            third_m = int(third_m)
            third_s=round(third_s,3)
            if third_s<10:
                third_s="0"+str(third_s)           
            st.write(f"This trend predicts a third qualifying time of {third_m}:{third_s} in {predict_year}.")


            fourth_m, fourth_s = divmod(fourth_x1*predict_year +fourth_const, 60)
            fourth_h, fourth_m = divmod(fourth_m, 60)
            fourth_m = int(fourth_m)
            fourth_s=round(fourth_s,3)
            if fourth_s<10:
                fourth_s="0"+str(fourth_s)           
            st.write(f"This trend predicts a fourth qualifying time of {fourth_m}:{fourth_s} in {predict_year}.")


            fifth_m, fifth_s = divmod(fifth_x1*predict_year +fifth_const, 60)
            fifth_h, fifth_m = divmod(fifth_m, 60)
            fifth_m = int(fifth_m)
            fifth_s=round(fifth_s,3)
            if fifth_s<10:
                fifth_s="0"+str(fifth_s)           
            st.write(f"This trend predicts a fifth qualifying time of {fifth_m}:{fifth_s} in {predict_year}.")

            sixth_m, sixth_s = divmod(sixth_x1*predict_year +sixth_const, 60)
            sixth_h, sixth_m = divmod(sixth_m, 60)
            sixth_m = int(sixth_m)
            sixth_s=round(sixth_s,3)
            if sixth_s<10:
                sixth_s="0"+str(sixth_s)           
            st.write(f"This trend predicts a sixth qualifying time of {sixth_m}:{sixth_s} in {predict_year}.")

            eigth_m, eigth_s = divmod(eigth_x1*predict_year +eigth_const, 60)
            eigth_h, eigth_m = divmod(eigth_m, 60)
            eigth_m = int(eigth_m)
            eigth_s=round(eigth_s,3)
            if eigth_s<10:
                eigth_s="0"+str(eigth_s)           
            st.write(f"This trend predicts an eigth qualifying time of {eigth_m}:{eigth_s} in {predict_year}.")

            sixteenth_m, sixteenth_s = divmod(sixteenth_x1*predict_year +sixteenth_const, 60)
            sixteenth_h, sixteenth_m = divmod(sixteenth_m, 60)
            sixteenth_m = int(sixteenth_m)
            sixteenth_s=round(sixteenth_s,3)
            if sixteenth_s<10:
                sixteenth_s="0"+str(sixteenth_s)           
            st.write(f"This trend predicts a sixteenth qualifying time of {sixteenth_m}:{sixteenth_s} in {predict_year}.")  
            
            
            
            
    if race_type=="Junior Women's 500TT":
        
        @st.cache_data
        def get_placing_data_from_excel():
            df = pd.read_excel(
                io='pages/WR_progressions/Junior_Progression.xlsx',
                engine ='openpyxl',
                sheet_name='W 500TT',
                skiprows=0,
                usecols='A:F',
                nrows=500
                )
            #df = df.replace(',','')


            return df




        c1,c2=st.columns([1,3])
        with c1:

            


            df= get_placing_data_from_excel()
            df_master=df
            df_show = df
            df_show=df_show.loc[(df_show["Rank"]==1) | (df_show["Rank"]==2) |(df_show["Rank"]==3) | (df_show["Rank"]==4) |(df_show["Rank"]==5) | (df_show["Rank"]==6) |(df_show["Rank"]==8) | (df_show["Rank"]==16)].reset_index(drop=True)
            df_show
                
                


        with c2:
            date_range = st.slider(
    "Restrict date range?",
            value = (df_show["Year"].min(),df_show["Year"].max()),
                min_value = df_show["Year"].min(),
                max_value = df_show["Year"].max())
            

            time_range = st.slider(
    "Restrict time range?",
            value = (df_show["Time"].min(),df_show["Time"].max()),
                min_value = df_show["Time"].min(),
                max_value = df_show["Time"].max())

            df_mask = df_show.mask(df_show["Year"] < date_range[0])
            df_mask = df_mask.mask(df_mask["Year"] > date_range[1])
            df_mask = df_mask.mask(df_mask["Time"] < time_range[0])
            df_mask = df_mask.mask(df_mask["Time"] > time_range[1])
            df_mask=df_mask.dropna()
            
            
            df_flat = df_mask.pivot(index='Year', columns='Rank')
            df_flat = df_flat['Time']
            
            df_flat['Year'] = df_flat.index
            df_flat=df_flat.rename(columns={1: "1st", 2: "2nd", 3: "3rd", 4: "4th", 5: "5th", 6: "6th", 8: "8th", 16: "16th"})
            
            

            fig = px.scatter(df_flat, x="Year", y = ["1st","2nd","3rd","4th","5th","6th","8th","16th"], title="Junior Women's 500TT World Champs Placing Progression",trendline="ols", color_discrete_sequence=['gold',"silver","darkorange","lightpink","teal","mediumvioletred","mediumaquamarine","olive"])
            customdata = np.stack((df_flat['1st'], df_flat['2nd'], df_flat['3rd'],df_flat['4th'],df_flat['5th'],df_flat['6th'],df_flat['8th'],df_flat['16th'],df_flat['Year']), axis=-1)
            hovertemplate = ('1st: %{customdata[0]}<br>' + '2nd: %{customdata[1]}<br>' +'3rd: %{customdata[2]}<br>' +'4th: %{customdata[3]}<br>' +'5th: %{customdata[4]}<br>' +'6th: %{customdata[5]}<br>' +'8th: %{customdata[6]}<br>' +'16th: %{customdata[7]}<br>' +
        'Date: %{customdata[8]}<br>' 
        '<extra></extra>')
            fig.update_traces(customdata=customdata, hovertemplate=hovertemplate)
            st.plotly_chart(fig, use_container_width=True)
            first_a=px.get_trendline_results(fig).px_fit_results.iloc[0].rsquared
            first_const = px.get_trendline_results(fig).px_fit_results.iloc[0].params[0]
            first_x1=px.get_trendline_results(fig).px_fit_results.iloc[0].params[1]

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
            
            fourth_a=px.get_trendline_results(fig).px_fit_results.iloc[3].rsquared
            fourth_const = px.get_trendline_results(fig).px_fit_results.iloc[3].params[0]
            fourth_x1=px.get_trendline_results(fig).px_fit_results.iloc[3].params[1]

            fifth_a=px.get_trendline_results(fig).px_fit_results.iloc[4].rsquared
            fifth_const = px.get_trendline_results(fig).px_fit_results.iloc[4].params[0]
            fifth_x1=px.get_trendline_results(fig).px_fit_results.iloc[4].params[1]

            sixth_a=px.get_trendline_results(fig).px_fit_results.iloc[5].rsquared
            sixth_const = px.get_trendline_results(fig).px_fit_results.iloc[5].params[0]
            sixth_x1=px.get_trendline_results(fig).px_fit_results.iloc[5].params[1]

            eigth_a=px.get_trendline_results(fig).px_fit_results.iloc[6].rsquared
            eigth_const = px.get_trendline_results(fig).px_fit_results.iloc[6].params[0]
            eigth_x1=px.get_trendline_results(fig).px_fit_results.iloc[6].params[1]

            sixteenth_a=px.get_trendline_results(fig).px_fit_results.iloc[7].rsquared
            sixteenth_const = px.get_trendline_results(fig).px_fit_results.iloc[7].params[0]
            sixteenth_x1=px.get_trendline_results(fig).px_fit_results.iloc[7].params[1]
            c1,c2=st.columns(2)
            with c1:
                st.write(f"1st = {round(first_x1,6)}(Year) + {round(first_const,3)}")
                st.write(f"R-squared = {round(first_a,3)}")

                st.write(f"2nd = {round(second_x1,6)}(Year) + {round(second_const,3)}")
                st.write(f"R-squared = {round(second_a,3)}")

                st.write(f"3rd = {round(third_x1,6)}(Year) + {round(third_const,3)}")
                st.write(f"R-squared = {round(third_a,3)}")

                st.write(f"4th = {round(fourth_x1,6)}(Year) + {round(fourth_const,3)}")
                st.write(f"R-squared = {round(fourth_a,3)}")
            with c2:
                st.write(f"5th = {round(fifth_x1,6)}(Year) + {round(fifth_const,3)}")
                st.write(f"R-squared = {round(fifth_a,3)}")

                st.write(f"6th = {round(sixth_x1,6)}(Year) + {round(sixth_const,3)}")
                st.write(f"R-squared = {round(sixth_a,3)}")

                st.write(f"8th = {round(eigth_x1,6)}(Year) + {round(eigth_const,3)}")
                st.write(f"R-squared = {round(eigth_a,3)}")

                st.write(f"16th = {round(sixteenth_x1,6)}(Year) + {round(sixteenth_const,3)}")
                st.write(f"R-squared = {round(sixteenth_a,3)}")

        with col2:
            predict_year = st.number_input("Select year for fastest time prediction:",min_value=2020,max_value=3000,value=2024,step=1)


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


            fourth_m, fourth_s = divmod(fourth_x1*predict_year +fourth_const, 60)
            fourth_h, fourth_m = divmod(fourth_m, 60)
            fourth_m = int(fourth_m)
            fourth_s=round(fourth_s,3)
            if fourth_s<10:
                fourth_s="0"+str(fourth_s)           
            st.write(f"This trend predicts a fourth qualifying time of {fourth_s} in {predict_year}.")


            fifth_m, fifth_s = divmod(fifth_x1*predict_year +fifth_const, 60)
            fifth_h, fifth_m = divmod(fifth_m, 60)
            fifth_m = int(fifth_m)
            fifth_s=round(fifth_s,3)
            if fifth_s<10:
                fifth_s="0"+str(fifth_s)           
            st.write(f"This trend predicts a fifth qualifying time of {fifth_s} in {predict_year}.")

            sixth_m, sixth_s = divmod(sixth_x1*predict_year +sixth_const, 60)
            sixth_h, sixth_m = divmod(sixth_m, 60)
            sixth_m = int(sixth_m)
            sixth_s=round(sixth_s,3)
            if sixth_s<10:
                sixth_s="0"+str(sixth_s)           
            st.write(f"This trend predicts a sixth qualifying time of {sixth_s} in {predict_year}.")

            eigth_m, eigth_s = divmod(eigth_x1*predict_year +eigth_const, 60)
            eigth_h, eigth_m = divmod(eigth_m, 60)
            eigth_m = int(eigth_m)
            eigth_s=round(eigth_s,3)
            if eigth_s<10:
                eigth_s="0"+str(eigth_s)           
            st.write(f"This trend predicts an eigth qualifying time of {eigth_s} in {predict_year}.")

            sixteenth_m, sixteenth_s = divmod(sixteenth_x1*predict_year +sixteenth_const, 60)
            sixteenth_h, sixteenth_m = divmod(sixteenth_m, 60)
            sixteenth_m = int(sixteenth_m)
            sixteenth_s=round(sixteenth_s,3)
            if sixteenth_s<10:
                sixteenth_s="0"+str(sixteenth_s)           
            st.write(f"This trend predicts a sixteenth qualifying time of {sixteenth_s} in {predict_year}.") 