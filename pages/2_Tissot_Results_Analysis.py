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
    race_types=["Men's Sprint Qualifying","Women's Sprint Qualifying","Men's Sprint","Women's Sprint","Men's Keirin","Women's Keirin","Men's Team Sprint","Women's Team Sprint","Men's Omnium","Women's Omnium","Men's Madison","Women's Madison","Men's 1k Time Trial","Women's 500m Time Trial","Men's Team Pursuit","Women's Team Pursuit","Men's Individual Pursuit","Women's Individual Pursuit"]
    race_type = st.selectbox("Select Event:", race_types, key="Event Selector")
    if race_type=="Men's Sprint Qualifying":
        st.header('Men\'s Sprint Qualifying')




        @st.cache_data
        def get_data_from_excel():
            df = pd.read_excel(
                io='pages/MensRaceResults.xlsm',
                engine ='openpyxl',
                sheet_name='Sprint Qual',
                skiprows=0,
                usecols='A:M',
                nrows=2000
                )
            df = df.replace(',','')
            #df['Date'] = pd.to_datetime(df['Date']).dt.date
            return df
        df= get_data_from_excel()


        def get_dev_data_from_excel():
            df_dev = pd.read_excel(
                io='pages/SprintPerformanceDatabase.xlsx',
                engine ='openpyxl',
                sheet_name='Sprint Qual Men',
                skiprows=0,
                usecols='A:M',
                nrows=3000
                )
            df_dev = df_dev.replace(',','')
            #df_dev['Date'] = pd.to_datetime(df['Date']).dt.date
            return df_dev
        df_dev= get_dev_data_from_excel()
        @st.cache_data
        def convert_to_csv(df):
            return df.to_csv(index=False,sep = ",").encode('utf-32')

        col1, col2, col3, col4 = st.columns(4)
        with col1:

            Devs = ["No","Yes"]
            Dev = st.selectbox("Include Age Grade Competitions?:", Devs, key="Dev_selector")

            if Dev == "Yes":
                df = pd.concat([df,df_dev])
                df=df.sort_values("Date", ascending=False)

        with col2:
            df_orig = df

            year = st.multiselect(
                "Select Year:",
                options=df["Year"].unique(),
                default=df["Year"].unique()[0]
            )    
            if year:
                df = df.query(
                    "Year == @year"
                    )
            else:
                df=df_orig

        with col3:
            location = st.multiselect(
                "Select Location:",
                options=df["Location"].unique(),
                default=df["Location"].unique()[0]
            )

            if location:
                df = df.query(
                    "Location == @location"
                    )
            else:
                df=df_orig


        with col4:
            event = st.multiselect(
                "Select Event Type:",
                options=df["Event"].unique(),
                default=df["Event"].unique()[0]
            )

            if event:
                df = df.query(
                    "Event == @event"
                    )
            else:
                df=df_orig


        st.dataframe(df,use_container_width=True)
        ##Download buttons
        csv = convert_to_csv(df)
        download1 = st.download_button(
            label="Download sprint qualifying data as CSV",
            data=csv,
            file_name='Sprint_Qual_Data.csv',
            mime='text/csv',
            key="buffer1"
        )
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='Sheet1', index=False)
            writer.save()
            download2 = st.download_button(
                label="Download sprint qualifying data as Excel",
                data=buffer,
                file_name='Sprint_Qual_Data.xlsx',
                mime='application/vnd.ms-excel',
                key="buffer2"
            )
        ##Download buttons complete

        st.markdown("---")

        st.title(":bar_chart: Top Ten Performances")

        df_topten = df_orig.sort_values('200m').head(10)

        st.dataframe(df_topten,use_container_width=True)

        ##Download buttons
        csv_tt = convert_to_csv(df_topten)
        download1 = st.download_button(
            label="Download top ten data as CSV",
            data=csv_tt,
            file_name='Sprint_Qual_Data.csv',
            mime='text/csv',
            key="buffertt1"
        )
        buffer_tt = io.BytesIO()
        with pd.ExcelWriter(buffer_tt, engine='xlsxwriter') as writer:
            df_topten.to_excel(writer, sheet_name='Sheet1', index=False)
            writer.save()
            download2 = st.download_button(
                label="Download top ten data as Excel",
                data=buffer_tt,
                file_name='Sprint_Qual_Data.xlsx',
                mime='application/vnd.ms-excel',
                key="buffertt2"
            )
        ##Download buttons complete

        st.markdown("---")

        st.title(":bicyclist: Athlete History")

        athletes = df_orig['Athlete'].drop_duplicates().sort_values()
        athlete = st.multiselect("Select Athlete(s):", athletes)

        df_athleteHistory = df_orig.query(
            "Athlete == @athlete"
        )
        df_athleteHistory=df_athleteHistory.sort_values("Date",ascending=False)
        if len(athlete) !=0:
            st.dataframe(df_athleteHistory,use_container_width=True)
            ##Download buttons
            csv_ah = convert_to_csv(df_athleteHistory)
            download1 = st.download_button(
                label="Download athlete history data as CSV",
                data=csv_ah,
                file_name='Sprint_Qual_Data.csv',
                mime='text/csv',
                key="bufferah1"
            )
            buffer_ah = io.BytesIO()
            with pd.ExcelWriter(buffer_ah, engine='xlsxwriter') as writer:
                df_athleteHistory.to_excel(writer, sheet_name='Sheet1', index=False)
                writer.save()
                download2 = st.download_button(
                    label="Download athlete history data as Excel",
                    data=buffer_ah,
                    file_name='Sprint_Qual_Data.xlsx',
                    mime='application/vnd.ms-excel',
                    key="bufferah2"
                )
            ##Download buttons complete

            #First Figure -- All races

            df_splits_CH = pd.DataFrame()
            df_splits_CH["Marker"] = ["100m","200m"]
            for i in range(len(df_athleteHistory)):
                var = str(i+1)+" " +str(df_athleteHistory["Athlete"].iloc[i]) + " " + str(df_athleteHistory["Year"].iloc[i]) + " " +str(df_athleteHistory["Event"].iloc[i]) + " " +str(df_athleteHistory["Location"].iloc[i])
                df_splits_CH[f"{var}"]=df_athleteHistory.iloc[i][8:10].values
            fig_CH = px.line(df_splits_CH, x="Marker", y = df_splits_CH.columns, title="All Rides",labels={"value":"Splits (seconds)"},markers=True)
            st.plotly_chart(fig_CH, use_container_width=True)

            ##Second Figure -- 200m times by Date
            fig_athlete_history = px.line(df_athleteHistory, x="Date", y = "200m", title = "Times by Date", markers = "True", text = "Location", color="Athlete")
            fig_athlete_history.update_traces(textposition="top right")
            st.plotly_chart(fig_athlete_history,use_container_width=True)
            ##Third Figure -- Rank by Date
            fig_athlete_history = px.line(df_athleteHistory, x="Date", y = "Rank", title = "Rank by Date", markers = "True", color="Athlete")
            fig_athlete_history.update_traces(textposition="top right")
            st.plotly_chart(fig_athlete_history,use_container_width=True)

            ##Fourth Figure -- 200m times by Age
            fig_athlete_history = px.line(df_athleteHistory, x="Age", y = "200m", title = "Times by Age", 
                                          markers = "True", color="Athlete",labels={"200m":"200m (seconds)"})
            fig_athlete_history.update_traces(textposition="top right")
            st.plotly_chart(fig_athlete_history,use_container_width=True)

            ##Fifth Figure -- 100m times by Age    
            fig_athlete_history = px.line(df_athleteHistory, x="Age", y = "100m", title = "100m Times by Age", markers = "True", color="Athlete",labels={"100m":"100m (seconds)"})
            st.plotly_chart(fig_athlete_history,use_container_width=True)

            ##Sixth Figure -- 100-200m times by Age
            fig_athlete_history = px.line(df_athleteHistory, x="Age", y = "100-200m", title = "100-200m Times by Age", markers = "True", color="Athlete",labels={"100-200m":"100-200m (seconds)"})
            st.plotly_chart(fig_athlete_history,use_container_width=True)


        st.markdown("---")

        st.title(":mag_right: Race Analysis Tool")
        uniqueYear = df_orig['Year'].drop_duplicates().sort_values(ascending=False)


        left_column, middle_column, right_column = st.columns(3)
        with left_column:
            an_year = st.selectbox("Select Year:", uniqueYear)

        df_an_year = df_orig.query(
            "Year == @an_year"
        )
        uniqueLocation = df_an_year['Location'].drop_duplicates().sort_values()

        with middle_column:
            an_location = st.selectbox("Select Location:", uniqueLocation)

        df_an_year_location = df_an_year.query(
            "Year == @an_year & Location == @an_location"
        )

        uniqueEvent = df_an_year_location['Event'].drop_duplicates().sort_values()
        with right_column:
            an_event = st.selectbox("Select Event:", uniqueEvent)

        df_an = df_an_year_location.query(
            "Year == @an_year & Location == @an_location & Event == @an_event"
        )

        st.dataframe(df_an,use_container_width=True)



        fig_event = px.line(df_an, y=["100m","200m","Diff"], x = "Athlete",markers="True",labels={"value":"Seconds"})

        st.plotly_chart(fig_event,use_container_width=True)

        
    if race_type=="Women's Sprint Qualifying":
        st.header('Women\'s Sprint Qualifying')




        @st.cache_data
        def get_data_from_excel():
            df = pd.read_excel(
                io='pages/WomensRaceResults.xlsm',
                engine ='openpyxl',
                sheet_name='Sprint Qual',
                skiprows=0,
                usecols='A:M',
                nrows=2000
                )
            df = df.replace(',','')
            #df['Date'] = pd.to_datetime(df['Date']).dt.date
            return df
        df= get_data_from_excel()


        def get_dev_data_from_excel():
            df_dev = pd.read_excel(
                io='pages/SprintPerformanceDatabase.xlsx',
                engine ='openpyxl',
                sheet_name='Sprint Qual Women',
                skiprows=0,
                usecols='A:M',
                nrows=3000
                )
            df_dev = df_dev.replace(',','')
            #df['Date'] = pd.to_datetime(df['Date']).dt.date
            return df_dev
        df_dev= get_dev_data_from_excel()
        @st.cache_data
        def convert_to_csv(df):
            return df.to_csv(index=False,sep = ",").encode('utf-32')

        col1, col2, col3, col4 = st.columns(4)
        with col1:

            Devs = ["No","Yes"]
            Dev = st.selectbox("Include Age Grade Competitions?:", Devs, key="Dev_selector")

            if Dev == "Yes":
                df = pd.concat([df,df_dev])
                df=df.sort_values("Date", ascending=False)

        with col2:
            df_orig = df

            year = st.multiselect(
                "Select Year:",
                options=df["Year"].unique(),
                default=df["Year"].unique()[0]
            )    
            if year:
                df = df.query(
                    "Year == @year"
                    )
            else:
                df=df_orig

        with col3:
            location = st.multiselect(
                "Select Location:",
                options=df["Location"].unique(),
                default=df["Location"].unique()[0]
            )

            if location:
                df = df.query(
                    "Location == @location"
                    )
            else:
                df=df_orig


        with col4:
            event = st.multiselect(
                "Select Event Type:",
                options=df["Event"].unique(),
                default=df["Event"].unique()[0]
            )

            if event:
                df = df.query(
                    "Event == @event"
                    )
            else:
                df=df_orig


        st.dataframe(df,use_container_width=True)
        ##Download buttons
        csv = convert_to_csv(df)
        download1 = st.download_button(
            label="Download sprint qualifying data as CSV",
            data=csv,
            file_name='Sprint_Qual_Data.csv',
            mime='text/csv',
            key="buffer1"
        )
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='Sheet1', index=False)
            writer.save()
            download2 = st.download_button(
                label="Download sprint qualifying data as Excel",
                data=buffer,
                file_name='Sprint_Qual_Data.xlsx',
                mime='application/vnd.ms-excel',
                key="buffer2"
            )
        ##Download buttons complete

        st.markdown("---")

        st.title(":bar_chart: Top Ten Performances")

        df_topten = df_orig.sort_values('200m').head(10)

        st.dataframe(df_topten,use_container_width=True)

        ##Download buttons
        csv_tt = convert_to_csv(df_topten)
        download1 = st.download_button(
            label="Download top ten data as CSV",
            data=csv_tt,
            file_name='Sprint_Qual_Data.csv',
            mime='text/csv',
            key="buffertt1"
        )
        buffer_tt = io.BytesIO()
        with pd.ExcelWriter(buffer_tt, engine='xlsxwriter') as writer:
            df_topten.to_excel(writer, sheet_name='Sheet1', index=False)
            writer.save()
            download2 = st.download_button(
                label="Download top ten data as Excel",
                data=buffer_tt,
                file_name='Sprint_Qual_Data.xlsx',
                mime='application/vnd.ms-excel',
                key="buffertt2"
            )
        ##Download buttons complete

        st.markdown("---")

        st.title(":bicyclist: Athlete History")

        athletes = df_orig['Athlete'].drop_duplicates().sort_values()
        athlete = st.multiselect("Select Athlete(s):", athletes)

        df_athleteHistory = df_orig.query(
            "Athlete == @athlete"
        )
        df_athleteHistory=df_athleteHistory.sort_values("Date",ascending=False)
        if len(athlete) !=0:
            st.dataframe(df_athleteHistory,use_container_width=True)
            ##Download buttons
            csv_ah = convert_to_csv(df_athleteHistory)
            download1 = st.download_button(
                label="Download athlete history data as CSV",
                data=csv_ah,
                file_name='Sprint_Qual_Data.csv',
                mime='text/csv',
                key="bufferah1"
            )
            buffer_ah = io.BytesIO()
            with pd.ExcelWriter(buffer_ah, engine='xlsxwriter') as writer:
                df_athleteHistory.to_excel(writer, sheet_name='Sheet1', index=False)
                writer.save()
                download2 = st.download_button(
                    label="Download athlete history data as Excel",
                    data=buffer_ah,
                    file_name='Sprint_Qual_Data.xlsx',
                    mime='application/vnd.ms-excel',
                    key="bufferah2"
                )
            ##Download buttons complete

            #First Figure -- All races

            df_splits_CH = pd.DataFrame()
            df_splits_CH["Marker"] = ["100m","200m"]
            for i in range(len(df_athleteHistory)):
                var = str(i+1)+" " +str(df_athleteHistory["Athlete"].iloc[i]) + " " + str(df_athleteHistory["Year"].iloc[i]) + " " +str(df_athleteHistory["Event"].iloc[i]) + " " +str(df_athleteHistory["Location"].iloc[i])
                df_splits_CH[f"{var}"]=df_athleteHistory.iloc[i][8:10].values
            fig_CH = px.line(df_splits_CH, x="Marker", y = df_splits_CH.columns, title="All Rides")
            st.plotly_chart(fig_CH, use_container_width=True)

            ##Second Figure -- 200m times by Date
            fig_athlete_history = px.line(df_athleteHistory, x="Date", y = "200m", title = "Times by Date", markers = "True", color="Athlete")
            fig_athlete_history.update_traces(textposition="top right")
            st.plotly_chart(fig_athlete_history,use_container_width=True)
            ##Third Figure -- Rank by Date
            fig_athlete_history = px.line(df_athleteHistory, x="Date", y = "Rank", title = "Rank by Date", markers = "True", color="Athlete")
            fig_athlete_history.update_traces(textposition="top right")
            st.plotly_chart(fig_athlete_history,use_container_width=True)

            ##Fourth Figure -- 200m times by Age
            fig_athlete_history = px.line(df_athleteHistory, x="Age", y = "200m", title = "Times by Age", markers = "True", color="Athlete")
            fig_athlete_history.update_traces(textposition="top right")
            st.plotly_chart(fig_athlete_history,use_container_width=True)

            ##Fifth Figure -- 100m times by Age    
            fig_athlete_history = px.line(df_athleteHistory, x="Age", y = "100m", title = "100m Times by Age", markers = "True", color="Athlete")
            st.plotly_chart(fig_athlete_history,use_container_width=True)

            ##Sixth Figure -- 100-200m times by Age
            fig_athlete_history = px.line(df_athleteHistory, x="Age", y = "100-200m", title = "100-200m Times by Age", markers = "True", color="Athlete")
            st.plotly_chart(fig_athlete_history,use_container_width=True)


        st.markdown("---")

        st.title(":mag_right: Race Analysis Tool")
        uniqueYear = df_orig['Year'].drop_duplicates().sort_values(ascending=False)


        left_column, middle_column, right_column = st.columns(3)
        with left_column:
            an_year = st.selectbox("Select Year:", uniqueYear)

        df_an_year = df_orig.query(
            "Year == @an_year"
        )
        uniqueLocation = df_an_year['Location'].drop_duplicates().sort_values()

        with middle_column:
            an_location = st.selectbox("Select Location:", uniqueLocation)

        df_an_year_location = df_an_year.query(
            "Year == @an_year & Location == @an_location"
        )

        uniqueEvent = df_an_year_location['Event'].drop_duplicates().sort_values()
        with right_column:
            an_event = st.selectbox("Select Event:", uniqueEvent)
        df_an = df_an_year_location.query(
            "Year == @an_year & Location == @an_location & Event == @an_event"
        )

        st.dataframe(df_an,use_container_width=True)



        fig_event = px.line(df_an, y=["100m","200m","Diff"], x = "Athlete",markers=True)

        st.plotly_chart(fig_event,use_container_width=True)



    if race_type=="Men's Sprint":
        st.header('Men\'s Sprint')
        st.subheader('All results')

        @st.cache_data
        def get_data_from_excel():
            df = pd.read_excel(
                io='pages/MensRaceResults.xlsm',
                engine ='openpyxl',
                sheet_name='Sprint',
                skiprows=0,
                usecols='A:S',
                nrows=3000
                )
            df = df.replace(',','')
            df['Date'] = pd.to_datetime(df['Date']).dt.date
            return df
        df= get_data_from_excel()
        df_orig=df



        def get_trueskill_data_from_excel():
            df = pd.read_excel(
                io='pages/MensRaceResults.xlsm',
                engine ='openpyxl',
                sheet_name='Sprint_Trueskill',
                skiprows=0,
                usecols='A:R',
                nrows=3000
                )
            df = df.replace(',','')
            df['Date'] = pd.to_datetime(df['Date']).dt.date
            return df
        df_TS = get_trueskill_data_from_excel()

        df_orig = df_TS

        @st.cache_data
        def convert_to_csv(df):
            return df.to_csv(index=False,sep = ",").encode('utf-32')
        c1,c2,c3=st.columns(3)
        with c1:
            year = st.multiselect(
                "Select Year:",
                options=df["Year"].unique(),
                default=df["Year"].unique()[-1]
            )    
        if year:
            df = df.query(
                "Year == @year"
                )
        else:
            df=df_orig

        with c2:
            location = st.multiselect(
                "Select Location:",
                options=df["Location"].unique(),
                default=df["Location"].unique()[0]
            )

        if location:
            df = df.query(
                "Location == @location"
                )
        else:
            df=df_orig
        with c3:
            event = st.multiselect(
                "Select Event Type:",
                options=df["Event"].unique(),
                default=df["Event"].unique()[0]
            )

        if event:
            df = df.query(
                "Event == @event"
                )
        else:
            df=df_orig


        st.dataframe(df, use_container_width=True)

        ##Download buttons
        csv = convert_to_csv(df)
        download1 = st.download_button(
            label="Download sprint data as CSV",
            data=csv,
            file_name='Sprint_Data.csv',
            mime='text/csv',
            key="buffer1"
        )
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='Sheet1', index=False)
            writer.save()
            download2 = st.download_button(
                label="Download sprint data as Excel",
                data=buffer,
                file_name='Sprint_Data.xlsx',
                mime='application/vnd.ms-excel',
                key="buffer2"
            )
        ##Download buttons complete

        st.markdown("---")

        st.title(":bicyclist: Athlete History")

        athletes = df_orig['Athlete'].drop_duplicates().sort_values()
        athlete = st.multiselect("Select Athlete(s):", athletes)

        df_athleteHistory = df_orig.query(
            "Athlete == @athlete"
        )
        if len(athlete)!=0:
            st.dataframe(df_athleteHistory, use_container_width=True)

            ##Download buttons
            csv_ah = convert_to_csv(df_athleteHistory)
            download1 = st.download_button(
                label="Download sprint data as CSV",
                data=csv_ah,
                file_name='Sprint_Data.csv',
                mime='text/csv',
                key="bufferah1"
            )
            buffer_ah = io.BytesIO()
            with pd.ExcelWriter(buffer_ah, engine='xlsxwriter') as writer:
                df_athleteHistory.to_excel(writer, sheet_name='Sheet1', index=False)
                writer.save()
                download2 = st.download_button(
                    label="Download sprint data as Excel",
                    data=buffer_ah,
                    file_name='Sprint_Data.xlsx',
                    mime='application/vnd.ms-excel',
                    key="bufferah2"
                )
            ##Download buttons complete

            fig_athlete_history = px.line(df_athleteHistory, x="Date", y = ["200m"], title = "Times by Date", markers = "True", text = "Location", color="Athlete")
            fig_athlete_history.update_traces(textposition="top right")

            st.plotly_chart(fig_athlete_history, use_container_width=True)

            fig_athlete_history = px.line(df_athleteHistory, x="Date", y = "Final Rank", title = "Rank by Date", markers = "True", color="Athlete")
            fig_athlete_history.update_traces(textposition="top right")

            st.plotly_chart(fig_athlete_history, use_container_width=True)

            fig_athlete_history = px.line(df_athleteHistory, x="Age", y = ["200m"], title = "Times by Age", markers = "True", color="Athlete")
            fig_athlete_history.update_traces(textposition="top right")

            st.plotly_chart(fig_athlete_history, use_container_width=True)

            fig_athlete_history = px.line(df_athleteHistory, x="Age", y = "Final Rank", title = "Final Rank by Age", markers = "True", color="Athlete")


            st.plotly_chart(fig_athlete_history, use_container_width=True)

            fig_athlete_history = px.line(df_athleteHistory, x="Age", y = "Final_CSE", title = "Conservative Skill Estimate by Age", markers = "True", color="Athlete")


            st.plotly_chart(fig_athlete_history, use_container_width=True)

            fig_athlete_history = px.line(df_athleteHistory, x="Date", y = "Final_CSE", title = "Conservative Skill Estimate by Date", markers = "True", color="Athlete")


            st.plotly_chart(fig_athlete_history, use_container_width=True)


        ###Trueskill Stuff

        st.markdown("---")

        st.title(":brain: Trueskill - Head to Head")

        df_TS = df_TS.drop_duplicates("Athlete",keep="last")
        #athlete_TS = st.multiselect("Select Athlete(s):", latest_TS)
        c1,c2 = st.columns(2)
        with c1:
            ath1 = st.selectbox("Select Athlete 1:", df_TS["Athlete"].sort_values(), key="df_TS")
        with c2:
            ath2 = st.selectbox("Select Athlete 2:", df_TS["Athlete"].sort_values(), key="df_TS_2")

        ind1 = df_TS.index[df_TS['Athlete'] == ath1]
        ind2 = df_TS.index[df_TS['Athlete'] == ath2]
        sig1 = df_TS["Sigma"][ind1].item()
        sig2 = df_TS["Sigma"][ind2].item()
        mu1 = df_TS["Mu"][ind1].item()
        mu2 = df_TS["Mu"][ind2].item()
        name1 = df_TS["Athlete"][ind1].item()
        name2 = df_TS["Athlete"][ind2].item()
        trials=10000
        ### -TESTING




        #x-axis ranges from -3 and 3 with .001 steps
        x = np.arange(0, 50, 0.001)
        if ath1!=ath2:
            #plot normal distribution with mean 0 and standard deviation 1
            plt.plot(x, norm.pdf(x, mu1, sig1), label=df_TS["Athlete"][ind1].iloc[0])
            plt.plot(x, norm.pdf(x, mu2, sig2), label=df_TS["Athlete"][ind2].iloc[0])
            plt.legend()


            s1 = np.random.normal(mu1, sig1, trials)
            s2 = np.random.normal(mu2, sig2, trials)
            s1_wins=0
            for i in range(len(s1)):
                if s1[i]>s2[i]:
                    s1_wins+=1
            s1_win_prob = s1_wins/trials*100
            s2_win_prob=100-s1_win_prob
            left_column, middle_column, right_column = st.columns(3)
            with left_column:

                st.write(name1 + " has mu value " + str(mu1) + " and sigma value " + str(sig1))
                st.write("From " +str(trials) + " trials, " + name1 + " has a " + str(round(s1_win_prob,2))+ "% chance of beating " + name2)

            with middle_column:

                st.pyplot(plt)


            with right_column:

                st.write(name2 + " has mu value " + str(mu2) + " and sigma value " + str(sig2))
                st.write("From " +str(trials) + " trials, " + name2 + " has a " + str(round(s2_win_prob,2))+ "% chance of beating " + name1)




        ###Multi competitor race simulator    




        st.markdown("---")

        st.title(":brain: Trueskill - Race Simulator")

        df_TS_multi = df_TS.drop_duplicates("Athlete",keep="last")
        plt.figure(1)
        aths = st.multiselect("Select Athletes:", df_TS_multi["Athlete"].sort_values(), key="df_TS_multi")
        if len(aths)>1:

            for j in range(len(aths)):
                exec(f'scores{j} = []')
                exec(f'ranks{j} = []')
                ind = df_TS_multi.index[df_TS_multi['Athlete'] == aths[j]]
                sig = df_TS_multi["Sigma"][ind].item()
                mu = df_TS_multi["Mu"][ind].item()
                plt.figure(0)
                plt.plot(x, norm.pdf(x, mu, sig), label=aths[j])

                exec(f'scores{j} = np.random.normal(mu, sig, trials)')

            left_column, middle_column, right_column = st.columns(3)

            with middle_column:
                plt.legend()
                st.pyplot(plt)


            for i in range(trials): 
                scores = []
                for j in range(len(aths)):
                    exec(f'scores.append(scores{j}[i])')
                for k in range(len(aths)):
                    exec(f'ranks{k}.append(sorted(scores,reverse=True).index(scores[k])+1)')

            i=1      

            for i in range(len(aths)):
                exec(f'st.subheader(aths[i]+ " has average rank " + str(round(sum(ranks{i})/len(ranks{i}),2)))')
                for j in range(len(aths)):
                    exec(f'st.write("His likelihood of gaining rank " + str(j+1) + " is "+ str(round(ranks{i}.count(j+1)/len(ranks{i}),3)))')
                st.write("")

                
    if race_type=="Women's Sprint":
        st.header('Women\'s Sprint')
        st.subheader('All results')

        @st.cache_data
        def get_data_from_excel():
            df = pd.read_excel(
                io='pages/WomensRaceResults.xlsm',
                engine ='openpyxl',
                sheet_name='Sprint',
                skiprows=0,
                usecols='A:S',
                nrows=3000
                )
            df = df.replace(',','')
            #df['Date'] = pd.to_datetime(df['Date']).dt.date
            return df
        df= get_data_from_excel()
        df_orig=df

        def get_trueskill_data_from_excel():
            df = pd.read_excel(
                io='pages/WomensRaceResults.xlsm',
                engine ='openpyxl',
                sheet_name='Sprint_Trueskill',
                skiprows=0,
                usecols='A:R',
                nrows=3000
                )
            df = df.replace(',','')
            df['Date'] = pd.to_datetime(df['Date']).dt.date
            return df
        df_TS = get_trueskill_data_from_excel()

        df_orig = df_TS

        @st.cache_data
        def convert_to_csv(df):
            return df.to_csv(index=False,sep = ",").encode('utf-32')
        c1,c2,c3=st.columns(3)
        with c1:
            year = st.multiselect(
                "Select Year:",
                options=df["Year"].unique(),
                default=df["Year"].unique()[0]
            )    
        if year:
            df = df.query(
                "Year == @year"
                )
        else:
            df=df_orig

        with c2:
            location = st.multiselect(
                "Select Location:",
                options=df["Location"].unique(),
                default=df["Location"].unique()[0]
            )

        if location:
            df = df.query(
                "Location == @location"
                )
        else:
            df=df_orig
        with c3:
            event = st.multiselect(
                "Select Event Type:",
                options=df["Event"].unique(),
                default=df["Event"].unique()[0]
            )

        if event:
            df = df.query(
                "Event == @event"
                )
        else:
            df=df_orig


        st.dataframe(df, use_container_width=True)

        ##Download buttons
        csv = convert_to_csv(df)
        download1 = st.download_button(
            label="Download sprint data as CSV",
            data=csv,
            file_name='Sprint_Data.csv',
            mime='text/csv',
            key="buffer1"
        )
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='Sheet1', index=False)
            writer.save()
            download2 = st.download_button(
                label="Download sprint data as Excel",
                data=buffer,
                file_name='Sprint_Data.xlsx',
                mime='application/vnd.ms-excel',
                key="buffer2"
            )
        ##Download buttons complete

        st.markdown("---")

        st.title(":bicyclist: Athlete History")

        athletes = df_orig['Athlete'].drop_duplicates().sort_values()
        athlete = st.multiselect("Select Athlete(s):", athletes)

        df_athleteHistory = df_orig.query(
            "Athlete == @athlete"
        )
        if len(athlete)!=0:
            st.dataframe(df_athleteHistory, use_container_width=True)

            ##Download buttons
            csv_ah = convert_to_csv(df_athleteHistory)
            download1 = st.download_button(
                label="Download sprint data as CSV",
                data=csv_ah,
                file_name='Sprint_Data.csv',
                mime='text/csv',
                key="bufferah1"
            )
            buffer_ah = io.BytesIO()
            with pd.ExcelWriter(buffer_ah, engine='xlsxwriter') as writer:
                df_athleteHistory.to_excel(writer, sheet_name='Sheet1', index=False)
                writer.save()
                download2 = st.download_button(
                    label="Download sprint data as Excel",
                    data=buffer_ah,
                    file_name='Sprint_Data.xlsx',
                    mime='application/vnd.ms-excel',
                    key="bufferah2"
                )
            ##Download buttons complete

            fig_athlete_history = px.line(df_athleteHistory, x="Date", y = ["Time"], title = "Times by Date", markers = "True", text = "Location", color="Athlete")
            fig_athlete_history.update_traces(textposition="top right")

            st.plotly_chart(fig_athlete_history, use_container_width=True)

            fig_athlete_history = px.line(df_athleteHistory, x="Date", y = "Final_Rank", title = "Rank by Date", markers = "True", color="Athlete")
            fig_athlete_history.update_traces(textposition="top right")

            st.plotly_chart(fig_athlete_history, use_container_width=True)

            fig_athlete_history = px.line(df_athleteHistory, x="Age", y = ["Time"], title = "Times by Age", markers = "True", color="Athlete")
            fig_athlete_history.update_traces(textposition="top right")

            st.plotly_chart(fig_athlete_history, use_container_width=True)

            fig_athlete_history = px.line(df_athleteHistory, x="Age", y = "Final_Rank", title = "Final Rank by Age", markers = "True", color="Athlete")


            st.plotly_chart(fig_athlete_history, use_container_width=True)

            fig_athlete_history = px.line(df_athleteHistory, x="Age", y = "Final_CSE", title = "Conservative Skill Estimate by Age", markers = "True", color="Athlete")


            st.plotly_chart(fig_athlete_history, use_container_width=True)

            fig_athlete_history = px.line(df_athleteHistory, x="Date", y = "Final_CSE", title = "Conservative Skill Estimate by Date", markers = "True", color="Athlete")


            st.plotly_chart(fig_athlete_history, use_container_width=True)


        ###Trueskill Stuff

        st.markdown("---")

        st.title(":brain: Trueskill - Head to Head")

        df_TS = df_TS.drop_duplicates("Athlete",keep="last")
        #athlete_TS = st.multiselect("Select Athlete(s):", latest_TS)
        c1,c2 = st.columns(2)
        with c1:
            ath1 = st.selectbox("Select Athlete 1:", df_TS["Athlete"].sort_values(), key="df_TS")
        with c2:
            ath2 = st.selectbox("Select Athlete 2:", df_TS["Athlete"].sort_values(), key="df_TS_2")

        #x-axis ranges from -3 and 3 with .001 steps
        x = np.arange(0, 50, 0.001)
        trials=10000
        if ath1!=ath2:
            ind1 = df_TS.index[df_TS['Athlete'] == ath1]
            ind2 = df_TS.index[df_TS['Athlete'] == ath2]
            sig1 = df_TS["Sigma"][ind1].item()
            sig2 = df_TS["Sigma"][ind2].item()
            mu1 = df_TS["Mu"][ind1].item()
            mu2 = df_TS["Mu"][ind2].item()
            name1 = df_TS["Athlete"][ind1].item()
            name2 = df_TS["Athlete"][ind2].item()

            ### -TESTING






            #plot normal distribution with mean 0 and standard deviation 1
            plt.plot(x, norm.pdf(x, mu1, sig1), label=df_TS["Athlete"][ind1].iloc[0])
            plt.plot(x, norm.pdf(x, mu2, sig2), label=df_TS["Athlete"][ind2].iloc[0])
            plt.legend()


            s1 = np.random.normal(mu1, sig1, trials)
            s2 = np.random.normal(mu2, sig2, trials)
            s1_wins=0
            for i in range(len(s1)):
                if s1[i]>s2[i]:
                    s1_wins+=1
            s1_win_prob = s1_wins/trials*100
            s2_win_prob=100-s1_win_prob
            left_column, middle_column, right_column = st.columns(3)
            with left_column:

                st.write(name1 + " has mu value " + str(mu1) + " and sigma value " + str(sig1))
                st.write("From " +str(trials) + " trials, " + name1 + " has a " + str(round(s1_win_prob,2))+ "% chance of beating " + name2)

            with middle_column:

                st.pyplot(plt)


            with right_column:

                st.write(name2 + " has mu value " + str(mu2) + " and sigma value " + str(sig2))
                st.write("From " +str(trials) + " trials, " + name2 + " has a " + str(round(s2_win_prob,2))+ "% chance of beating " + name1)




        ###Multi competitor race simulator    




        st.markdown("---")

        st.title(":brain: Trueskill - Race Simulator")

        df_TS_multi = df_TS.drop_duplicates("Athlete",keep="last")
        plt.figure(1)
        aths = st.multiselect("Select Athletes:", df_TS_multi["Athlete"].sort_values(), key="df_TS_multi")
        if len(aths)>1:

            for j in range(len(aths)):
                exec(f'scores{j} = []')
                exec(f'ranks{j} = []')
                ind = df_TS_multi.index[df_TS_multi['Athlete'] == aths[j]]
                sig = df_TS_multi["Sigma"][ind].item()
                mu = df_TS_multi["Mu"][ind].item()
                plt.figure(0)
                plt.plot(x, norm.pdf(x, mu, sig), label=aths[j])

                exec(f'scores{j} = np.random.normal(mu, sig, trials)')

            left_column, middle_column, right_column = st.columns(3)

            with middle_column:
                plt.legend()
                st.pyplot(plt)


            for i in range(trials): 
                scores = []
                for j in range(len(aths)):
                    exec(f'scores.append(scores{j}[i])')
                for k in range(len(aths)):
                    exec(f'ranks{k}.append(sorted(scores,reverse=True).index(scores[k])+1)')

            i=1      

            for i in range(len(aths)):
                exec(f'st.subheader(aths[i]+ " has average rank " + str(round(sum(ranks{i})/len(ranks{i}),2)))')
                for j in range(len(aths)):
                    exec(f'st.write("Her likelihood of gaining rank " + str(j+1) + " is "+ str(round(ranks{i}.count(j+1)/len(ranks{i}),3)))')
                st.write("")
                
                
    if race_type=="Men's Keirin":
        st.header('Men\'s Keirin')
        st.subheader('All results')

        @st.cache_data
        def get_data_from_excel():
            df = pd.read_excel(
                io='pages/MensRaceResults.xlsm',
                engine ='openpyxl',
                sheet_name='Keirin_Trueskill',
                skiprows=0,
                usecols='A:Q',
                nrows=5000
                )
            df = df.replace(',','')
            df['Date'] = pd.to_datetime(df['Date']).dt.date
            df=df.drop(["UCI_ID","ExpectedRank","RatingChange"],axis=1)
            return df
        df= get_data_from_excel()


        c1,c2,c3=st.columns(3)
        df_orig = df

        @st.cache_data
        def convert_to_csv(df):
            return df.to_csv(index=False,sep = ",").encode('utf-32')

        with c1:
            year = st.multiselect(
                "Select Year:",
                options=df["Year"].unique(),
                default=df["Year"].unique()[-1]
            )    
        if year:
            df = df.query(
                "Year == @year"
                )
        else:
            df=df_orig

        with c2:
            location = st.multiselect(
                "Select Location:",
                options=df["Location"].unique(),
                default=df["Location"].unique()[-1]
            )

        if location:
            df = df.query(
                "Location == @location"
                )
        else:
            df=df_orig
        with c3:
            event = st.multiselect(
                "Select Event Type:",
                options=df["Event"].unique(),
                default=df["Event"].unique()[0]
            )

        if event:
            df = df.query(
                "Event == @event"
                )
        else:
            df=df_orig


        st.dataframe(df,use_container_width=True)
        ##Download buttons
        csv = convert_to_csv(df)
        download1 = st.download_button(
            label="Download Keirin data as CSV",
            data=csv,
            file_name='Keirin_Data.csv',
            mime='text/csv',
            key="buffer1"
        )
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='Sheet1', index=False)
            writer.save()
            download2 = st.download_button(
                label="Download Keirin data as Excel",
                data=buffer,
                file_name='Keirin_Data.xlsx',
                mime='application/vnd.ms-excel',
                key="buffer2"
            )
        ##Download buttons complete

        st.markdown("---")

        st.title(":bicyclist: Athlete History")

        athletes = df_orig['Athlete'].drop_duplicates().sort_values()
        athlete = st.multiselect("Select Athlete(s):", athletes)

        df_athleteHistory = df_orig.query(
            "Athlete == @athlete"
        )
        if len(athlete)!=0:
            st.dataframe(df_athleteHistory,use_container_width=True)
            ##Download buttons
            csv_ah = convert_to_csv(df_athleteHistory)
            download1 = st.download_button(
                label="Download Keirin data as CSV",
                data=csv_ah,
                file_name='Keirin_Data.csv',
                mime='text/csv',
                key="bufferah1"
            )
            buffer_ah = io.BytesIO()
            with pd.ExcelWriter(buffer_ah, engine='xlsxwriter') as writer:
                df_athleteHistory.to_excel(writer, sheet_name='Sheet1', index=False)
                writer.save()
                download2 = st.download_button(
                    label="Download Keirin data as Excel",
                    data=buffer_ah,
                    file_name='Keirin_Data.xlsx',
                    mime='application/vnd.ms-excel',
                    key="bufferah2"
                )
            ##Download buttons complete

            fig_athlete_history = px.scatter(df_athleteHistory, x="Date", y = ["Rank"], title = "Rank by Date", text = "Location", color="Athlete")
            fig_athlete_history.update_traces(textposition="top right")

            st.plotly_chart(fig_athlete_history,use_container_width=True)

            fig_athlete_history = px.line(df_athleteHistory, x="Date", y = "Final_CSE", title = "Conservative Skill Estimate by Date", markers = "True", color="Athlete")
            fig_athlete_history.update_traces(textposition="top right")

            st.plotly_chart(fig_athlete_history,use_container_width=True)

            fig_athlete_history = px.scatter(df_athleteHistory, x="Age", y = ["Rank"], title = "Rank by Age", color="Athlete")
            fig_athlete_history.update_traces(textposition="top right")

            st.plotly_chart(fig_athlete_history,use_container_width=True)

            fig_athlete_history = px.line(df_athleteHistory, x="Age", y = "Final_CSE", title = "Conservative Skill Estimate by Age", markers = "True", color="Athlete")


            st.plotly_chart(fig_athlete_history,use_container_width=True)





        st.markdown("---")

        st.title(":brain: Trueskill - Head to Head")

        df_TS = df_orig.drop_duplicates("Athlete",keep="last")
        #athlete_TS = st.multiselect("Select Athlete(s):", latest_TS)
        c1,c2=st.columns(2)
        with c1:
            ath1 = st.selectbox("Select Athlete 1:", df_TS["Athlete"].sort_values(), key="df_TS")
        with c2:
            ath2 = st.selectbox("Select Athlete 2:", df_TS["Athlete"].sort_values(), key="df_TS_2")


        ind1 = df_TS.index[df_TS['Athlete'] == ath1]
        ind2 = df_TS.index[df_TS['Athlete'] == ath2]
        sig1 = df_TS["Sigma"][ind1].item()
        sig2 = df_TS["Sigma"][ind2].item()
        mu1 = df_TS["Mu"][ind1].item()
        mu2 = df_TS["Mu"][ind2].item()
        name1 = df_TS["Athlete"][ind1].item()
        name2 = df_TS["Athlete"][ind2].item()
        trials=10000
        ### -TESTING




        #x-axis ranges from -3 and 3 with .001 steps
        x = np.arange(0, 50, 0.001)
        if ath1!=ath2:
            #plot normal distribution with mean 0 and standard deviation 1
            plt.plot(x, norm.pdf(x, mu1, sig1), label=df_TS["Athlete"][ind1].iloc[0])
            plt.plot(x, norm.pdf(x, mu2, sig2), label=df_TS["Athlete"][ind2].iloc[0])
            plt.legend()


            s1 = np.random.normal(mu1, sig1, trials)
            s2 = np.random.normal(mu2, sig2, trials)
            s1_wins=0
            for i in range(len(s1)):
                if s1[i]>s2[i]:
                    s1_wins+=1
            s1_win_prob = s1_wins/trials*100
            s2_win_prob=100-s1_win_prob
            left_column, middle_column, right_column = st.columns(3)
            with left_column:

                st.write(name1 + " has mu value " + str(mu1) + " and sigma value " + str(sig1))
                st.write("From " +str(trials) + " trials, " + name1 + " has a " + str(round(s1_win_prob,2))+ "% chance of beating " + name2)

            with middle_column:

                st.pyplot(plt)


            with right_column:

                st.write(name2 + " has mu value " + str(mu2) + " and sigma value " + str(sig2))
                st.write("From " +str(trials) + " trials, " + name2 + " has a " + str(s2_win_prob)+ "% chance of beating " + name1)




        ###Multi competitor race simulator    




        st.markdown("---")

        st.title(":brain: Trueskill - Race Simulator")

        df_TS_multi = df_orig.drop_duplicates("Athlete",keep="last")
        plt.figure(1)
        aths = st.multiselect("Select Athletes:", df_TS_multi["Athlete"].sort_values(), key="df_TS_multi")
        if len(aths)>1:

            for j in range(len(aths)):
                exec(f'scores{j} = []')
                exec(f'ranks{j} = []')
                ind = df_TS_multi.index[df_TS_multi['Athlete'] == aths[j]]
                sig = df_TS_multi["Sigma"][ind].item()
                mu = df_TS_multi["Mu"][ind].item()
                plt.figure(0)
                plt.plot(x, norm.pdf(x, mu, sig), label=aths[j])

                exec(f'scores{j} = np.random.normal(mu, sig, trials)')

            left_column, middle_column, right_column = st.columns(3)

            with middle_column:
                plt.legend()
                st.pyplot(plt)


            for i in range(trials): 
                scores = []
                for j in range(len(aths)):
                    exec(f'scores.append(scores{j}[i])')
                for k in range(len(aths)):
                    exec(f'ranks{k}.append(sorted(scores,reverse=True).index(scores[k])+1)')

            i=1


            # sum(int(f'ranks{i}[0]')) / len(int(f'ranks{i}[0]'))        

            for i in range(len(aths)):
                exec(f'st.subheader(aths[i]+ " has average rank " + str(round(sum(ranks{i})/len(ranks{i}),2)))')
                for j in range(len(aths)):
                    exec(f'st.write("His likelihood of gaining rank " + str(j+1) + " is "+ str(round(ranks{i}.count(j+1)/len(ranks{i}),3)))')
                st.write("")

    if race_type=="Women's Keirin":
        st.header('Women\'s Keirin')
        st.subheader('All results')

        @st.cache_data
        def get_data_from_excel():
            df = pd.read_excel(
                io='pages/WomensRaceResults.xlsm',
                engine ='openpyxl',
                sheet_name='Keirin_Trueskill',
                skiprows=0,
                usecols='A:Q',
                nrows=5000
                )
            df = df.replace(',','')
            df['Date'] = pd.to_datetime(df['Date']).dt.date
            #df=df.drop(["UCI_ID","ExpectedRank","RatingChange"],axis=1)
            return df
        df= get_data_from_excel()


        c1,c2,c3=st.columns(3)
        df_orig = df

        @st.cache_data
        def convert_to_csv(df):
            return df.to_csv(index=False,sep = ",").encode('utf-32')

        with c1:
            year = st.multiselect(
                "Select Year:",
                options=df["Year"].unique(),
                default=df["Year"].unique()[-1]
            )    
        if year:
            df = df.query(
                "Year == @year"
                )
        else:
            df=df_orig

        with c2:
            location = st.multiselect(
                "Select Location:",
                options=df["Location"].unique(),
                default=df["Location"].unique()[-1]
            )

        if location:
            df = df.query(
                "Location == @location"
                )
        else:
            df=df_orig
        with c3:
            event = st.multiselect(
                "Select Event Type:",
                options=df["Event"].unique(),
                default=df["Event"].unique()[-1]
            )

        if event:
            df = df.query(
                "Event == @event"
                )
        else:
            df=df_orig


        st.dataframe(df,use_container_width=True)
        ##Download buttons
        csv = convert_to_csv(df)
        download1 = st.download_button(
            label="Download Keirin data as CSV",
            data=csv,
            file_name='Keirin_Data.csv',
            mime='text/csv',
            key="buffer1"
        )
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='Sheet1', index=False)
            writer.save()
            download2 = st.download_button(
                label="Download Keirin data as Excel",
                data=buffer,
                file_name='Keirin_Data.xlsx',
                mime='application/vnd.ms-excel',
                key="buffer2"
            )
        ##Download buttons complete

        st.markdown("---")

        st.title(":bicyclist: Athlete History")

        athletes = df_orig['Athlete'].drop_duplicates().sort_values()
        athlete = st.multiselect("Select Athlete(s):", athletes)

        df_athleteHistory = df_orig.query(
            "Athlete == @athlete"
        )
        if len(athlete)!=0:
            st.dataframe(df_athleteHistory,use_container_width=True)
            ##Download buttons
            csv_ah = convert_to_csv(df_athleteHistory)
            download1 = st.download_button(
                label="Download Keirin data as CSV",
                data=csv_ah,
                file_name='Keirin_Data.csv',
                mime='text/csv',
                key="bufferah1"
            )
            buffer_ah = io.BytesIO()
            with pd.ExcelWriter(buffer_ah, engine='xlsxwriter') as writer:
                df_athleteHistory.to_excel(writer, sheet_name='Sheet1', index=False)
                writer.save()
                download2 = st.download_button(
                    label="Download Keirin data as Excel",
                    data=buffer_ah,
                    file_name='Keirin_Data.xlsx',
                    mime='application/vnd.ms-excel',
                    key="bufferah2"
                )
            ##Download buttons complete

            fig_athlete_history = px.scatter(df_athleteHistory, x="Date", y = ["Rank"], title = "Rank by Date", color="Athlete")
            fig_athlete_history.update_traces(textposition="top right")

            st.plotly_chart(fig_athlete_history,use_container_width=True)

            fig_athlete_history = px.line(df_athleteHistory, x="Date", y = "Final CSE", title = "Trueskill by Date", markers = "True", color="Athlete")
            fig_athlete_history.update_traces(textposition="top right")

            st.plotly_chart(fig_athlete_history,use_container_width=True)

            fig_athlete_history = px.scatter(df_athleteHistory, x="Age", y = ["Rank"], title = "Rank by Age", color="Athlete")
            fig_athlete_history.update_traces(textposition="top right")

            st.plotly_chart(fig_athlete_history,use_container_width=True)

            fig_athlete_history = px.line(df_athleteHistory, x="Age", y = "Final CSE", title = "Trueskill by Age", markers = "True", color="Athlete")


            st.plotly_chart(fig_athlete_history,use_container_width=True)





        st.markdown("---")

        st.title(":brain: Trueskill - Head to Head")

        df_TS = df_orig.drop_duplicates("Athlete",keep="last")
        #athlete_TS = st.multiselect("Select Athlete(s):", latest_TS)
        c1,c2=st.columns(2)
        with c1:
            ath1 = st.selectbox("Select Athlete 1:", df_TS["Athlete"].sort_values(), key="df_TS")
        with c2:
            ath2 = st.selectbox("Select Athlete 2:", df_TS["Athlete"].sort_values(), key="df_TS_2")
        trials=10000
        #x-axis ranges from -3 and 3 with .001 steps
        x = np.arange(0, 50, 0.001)
        if ath1!=ath2:

            ind1 = df_TS.index[df_TS['Athlete'] == ath1]
            ind2 = df_TS.index[df_TS['Athlete'] == ath2]
            sig1 = df_TS["Sigma"][ind1].item()
            sig2 = df_TS["Sigma"][ind2].item()
            mu1 = df_TS["Mu"][ind1].item()
            mu2 = df_TS["Mu"][ind2].item()
            name1 = df_TS["Athlete"][ind1].item()
            name2 = df_TS["Athlete"][ind2].item()



            #plot normal distribution with mean 0 and standard deviation 1
            plt.plot(x, norm.pdf(x, mu1, sig1), label=df_TS["Athlete"][ind1].iloc[0])
            plt.plot(x, norm.pdf(x, mu2, sig2), label=df_TS["Athlete"][ind2].iloc[0])
            plt.legend()


            s1 = np.random.normal(mu1, sig1, trials)
            s2 = np.random.normal(mu2, sig2, trials)
            s1_wins=0
            for i in range(len(s1)):
                if s1[i]>s2[i]:
                    s1_wins+=1
            s1_win_prob = s1_wins/trials*100
            s2_win_prob=100-s1_win_prob
            left_column, middle_column, right_column = st.columns(3)
            with left_column:

                st.write(name1 + " has mu value " + str(mu1) + " and sigma value " + str(sig1))
                st.write("From " +str(trials) + " trials, " + name1 + " has a " + str(round(s1_win_prob,2))+ "% chance of beating " + name2)

            with middle_column:

                st.pyplot(plt)


            with right_column:

                st.write(name2 + " has mu value " + str(mu2) + " and sigma value " + str(sig2))
                st.write("From " +str(trials) + " trials, " + name2 + " has a " + str(s2_win_prob)+ "% chance of beating " + name1)




        ###Multi competitor race simulator    




        st.markdown("---")

        st.title(":brain: Trueskill - Race Simulator")

        df_TS_multi = df_orig.drop_duplicates("Athlete",keep="last")
        plt.figure(1)
        aths = st.multiselect("Select Athletes:", df_TS_multi["Athlete"].sort_values(), key="df_TS_multi")
        if len(aths)>1:

            for j in range(len(aths)):
                exec(f'scores{j} = []')
                exec(f'ranks{j} = []')
                ind = df_TS_multi.index[df_TS_multi['Athlete'] == aths[j]]
                sig = df_TS_multi["Sigma"][ind].item()
                mu = df_TS_multi["Mu"][ind].item()
                plt.figure(0)
                plt.plot(x, norm.pdf(x, mu, sig), label=aths[j])

                exec(f'scores{j} = np.random.normal(mu, sig, trials)')

            left_column, middle_column, right_column = st.columns(3)

            with middle_column:
                plt.legend()
                st.pyplot(plt)


            for i in range(trials): 
                scores = []
                for j in range(len(aths)):
                    exec(f'scores.append(scores{j}[i])')
                for k in range(len(aths)):
                    exec(f'ranks{k}.append(sorted(scores,reverse=True).index(scores[k])+1)')

            i=1


            # sum(int(f'ranks{i}[0]')) / len(int(f'ranks{i}[0]'))        

            for i in range(len(aths)):
                exec(f'st.subheader(aths[i]+ " has average rank " + str(round(sum(ranks{i})/len(ranks{i}),2)))')
                for j in range(len(aths)):
                    exec(f'st.write("Her likelihood of gaining rank " + str(j+1) + " is "+ str(round(ranks{i}.count(j+1)/len(ranks{i}),3)))')
                st.write("")
                
                
                
    if race_type=="Men's Team Sprint":
        st.header('Men\'s Team Sprint')
        st.subheader('All results')
        marker = ["125m","250m","375m","500m","625m","750m"]
        @st.cache_data
        def get_data_from_excel():
            df = pd.read_excel(
                io='pages/MensRaceResults.xlsm',
                engine ='openpyxl',
                sheet_name='Team Sprint',
                skiprows=0,
                usecols='A:V',
                nrows=1000
                )
            df = df.replace(',','', regex=True)
            df['Date'] = pd.to_datetime(df['Date']).dt.date
        #     for i in range(len(df)):
        #         df["Date"][i] = df["Date"][i].date()
                #if df["125m"][i] != "NULL":
                    #df["125m"][i] = df["125m"][i].strftime("%M:%S.%f")
            return df
        df= get_data_from_excel()
        @st.cache_data
        def convert_to_csv(df):
            return df.to_csv(index=False,sep = ",").encode('utf-32')
        format_dict = {'Date': '{:%d-%m-%y}', 'Age1': '{0:,.2f}', 'Age2': '{0:,.2f}'}
        df_orig = df
        c1,c2,c3 = st.columns(3)
        with c1:
            year = st.multiselect(
                "Select Year:",
                options=df["Year"].unique(),
                default=df["Year"].unique()[0]
            )    
        if year:
            df = df.query(
                "Year == @year"
                )
        else:
            df=df_orig

        with c2:
            location = st.multiselect(
                "Select Location:",
                options=df["Location"].unique(),
                default=df["Location"].unique()[0]
            )

        if location:
            df = df.query(
                "Location == @location"
                )
        else:
            df=df_orig
        with c3:
            event = st.multiselect(
                "Select Event Type:",
                options=df["Event"].unique(),
                default=df["Event"].unique()[0]
            )

        if event:
            df = df.query(
                "Event == @event"
                )
        else:
            df=df_orig

        st.dataframe(df)
        ##Download buttons
        csv = convert_to_csv(df)
        download1 = st.download_button(
            label="Download Team Sprint data as CSV",
            data=csv,
            file_name='Team_Sprint_Data.csv',
            mime='text/csv',
            key="buffer1"
        )
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='Sheet1', index=False)
            writer.save()
            download2 = st.download_button(
                label="Download Team Sprint data as Excel",
                data=buffer,
                file_name='Team_Sprint_Data.xlsx',
                mime='application/vnd.ms-excel',
                key="buffer2"
            )
        ##Download buttons complete    
        st.markdown("---")

        st.title(":bar_chart: Top Ten Performances")

        df_topten = df_orig.sort_values("Time").head(10)

        st.dataframe(df_topten, use_container_width=True)
        ##Download buttons
        csvtt = convert_to_csv(df_topten)
        download1 = st.download_button(
            label="Download Top Ten data as CSV",
            data=csvtt,
            file_name='Team_Sprint_Data.csv',
            mime='text/csv',
            key="buffertt1"
        )
        buffertt = io.BytesIO()
        with pd.ExcelWriter(buffertt, engine='xlsxwriter') as writer:
            df_topten.to_excel(writer, sheet_name='Sheet1', index=False)
            writer.save()
            download2 = st.download_button(
                label="Download Top Ten data as Excel",
                data=buffertt,
                file_name='Team_Sprint_Data.xlsx',
                mime='application/vnd.ms-excel',
                key="buffertt2"
            )
        ##Download buttons complete  
        df_splits_tt = pd.DataFrame()
        df_splits_tt["Marker"] = ["125m","250m","375m","500m","625m","750m"]
        for i in range(len(df_topten)):
            var = str(i+1)+" "+str(df_topten["Country"].iloc[i]) + " " + str(df_topten["Year"].iloc[i]) + " " +str(df_topten["Location"].iloc[i])+" " +str(df_topten["Event"].iloc[i]) + " " +str(df_topten["Stage"].iloc[i])
            df_splits_tt[f"{var}"]=df_topten.iloc[i][14:20].values


        fig_tt = px.line(df_splits_tt, x="Marker", y = df_splits_tt.columns, title="Top Ten")

        st.plotly_chart(fig_tt, use_container_width=True)

        st.markdown("---")

        st.title(":bicyclist: Country History")

        #FILTERS FOR DATAFRAME

        countries = df_orig['Country'].drop_duplicates().sort_values()
        country = st.multiselect("Select Country:", countries)

        df_countryHistory = df_orig.query(
            "Country == @country"
        )

        if len(country)>0:
            #DATAFRAME
            df_countryHistory = df_countryHistory.sort_values("Date")


            st.dataframe(df_countryHistory)

            #DOWNLOAD BUTTONS
            csv_CH = convert_to_csv(df_countryHistory)
            buffer_ch = io.BytesIO()
            # download button 1 to download dataframe as csv
            downloadCH1 = st.download_button(
                label="Download Country History data as CSV",
                data=csv_CH,
                file_name='Team_Sprint_Country_History_Data.csv',
                mime='text/csv',
                key="DLCH1"
            )

            # download button 2 to download dataframe as xlsx
            with pd.ExcelWriter(buffer_ch, engine='xlsxwriter') as writer:
                # Write each dataframe to a different worksheet.
                df_countryHistory.to_excel(writer, sheet_name='Sheet1', index=False)
                # Close the Pandas Excel writer and output the Excel file to the buffer
                writer.save()

                downloadCH2 = st.download_button(
                    label="Download Country History data as Excel",
                    data=buffer_ch,
                    file_name='Teamp_Sprint_Country_History_Data.xlsx',
                    mime='application/vnd.ms-excel',
                    key="DLCH2"
                )

            ##Download buttons complete


            #FIRST FIGURE -- FINAL TIME PROGRESSION

            fig_country_history = px.line(df_countryHistory, x="Date", y = "Time", title = "Times by Date",text="Location", color="Country",markers=True)
            fig_country_history.update_traces(textposition="top right")

            st.plotly_chart(fig_country_history, use_container_width=True)

            #Second Figure -- Chart with rider names

            df_splits_CH,df_worm_CH = pd.DataFrame(),pd.DataFrame()
            df_splits_CH["Marker"],df_worm_CH["Marker"] = marker,marker
            for i in range(len(df_countryHistory)):
                var = str(i+1)+" " +str(df_countryHistory["Country"].iloc[i]) + " " + str(df_countryHistory["Year"].iloc[i]) + " " +str(df_countryHistory["Event"].iloc[i]) + " " +str(df_countryHistory["Stage"].iloc[i])+ " " +str(df_countryHistory["Rider1"].iloc[i].split(" ")[0])+ " " +str(df_countryHistory["Rider2"].iloc[i].split(" ")[0])+ " " +str(df_countryHistory["Rider3"].iloc[i].split(" ")[0])
                df_splits_CH[f"{var}"]=df_countryHistory.iloc[i][14:20].values
                df_worm_CH[f"{var}"]=df_countryHistory.iloc[i][14:20].values.cumsum()

            show_name=st.selectbox("Show athlete names?",["Yes","No"])
            if show_name=="No":
                for i in range(1,len(df_splits_CH.columns)):
                    df_splits_CH.rename(columns={df_splits_CH.columns[i]: (" ".join(df_splits_CH.columns[i].split(" ")[0:5]))}, inplace=True)
                    df_worm_CH.rename(columns={df_worm_CH.columns[i]: (" ".join(df_worm_CH.columns[i].split(" ")[0:5]))}, inplace=True)
                    #df_splits_CH.columns[i] 

            fig_CH = px.line(df_splits_CH, x="Marker", y = df_splits_CH.columns, title="All Rides")


            st.plotly_chart(fig_CH, use_container_width=True)

            #Third Figure - Worm

            fig_event_CH = px.line(df_worm_CH, x="Marker", y = df_worm_CH.columns, title="The Worm")
            st.plotly_chart(fig_event_CH, use_container_width=True)



            #Fourth Figure - Ranges

            fig_ranges_CH = px.line(df_countryHistory, x=df_splits_CH.columns[1:], y = [125,250,375,500,625,750], title="The Ranges",markers=True)
            st.plotly_chart(fig_ranges_CH, use_container_width=True)





        st.markdown("---")

        st.title(":mag_right: Race Analysis Tool")
        uniqueYear = df_orig['Year'].drop_duplicates().sort_values(ascending=False)


        left_column, middle_column, right_column,c4 = st.columns(4)
        with left_column:
            an_year = st.selectbox("Select Year:", uniqueYear)

        df_an_year = df_orig.query(
            "Year == @an_year"
        )
        uniqueLocation = df_an_year['Location'].drop_duplicates().sort_values()

        with middle_column:
            an_location = st.selectbox("Select Location:", uniqueLocation)

        df_an_year_location = df_an_year.query(
            "Year == @an_year & Location == @an_location"
        )

        uniqueEvent = df_an_year_location['Event'].drop_duplicates().sort_values()
        with right_column:
            an_event = st.selectbox("Select Event:", uniqueEvent)

        df_an_year_location_event = df_an_year_location.query(
            "Year == @an_year & Location == @an_location & Event == @an_event"
        )

        uniqueStage = df_an_year_location_event['Stage'].drop_duplicates().sort_values()
        with c4:
            an_stage = st.selectbox("Select Stage:", uniqueStage)

        df_an = df_an_year_location_event.query(
            "Year == @an_year & Location == @an_location & Event == @an_event & Stage == @an_stage"
        )

        ### Splits dataframe and plot

        df_splits,df_worm = pd.DataFrame(),pd.DataFrame()
        df_splits["Marker"],df_worm["Marker"] = marker,marker
        for i in range(len(df_an)):
            var = str(df_an["Rank"].iloc[i])+" "+str(df_an["Country"].iloc[i])
            df_splits[f"{var}"]=df_an.iloc[i][14:20].values
            df_worm[f"{var}"]=df_an.iloc[i][14:20].values.cumsum()
        st.dataframe(df_an, use_container_width=True)

        fig_event = px.line(df_splits, x="Marker", y = df_splits.columns, title="Splits")
        st.plotly_chart(fig_event, use_container_width=True)

        ### Worm dataframe and plot

        fig_event = px.line(df_worm, x="Marker", y = df_worm.columns, title="The Worm")
        st.plotly_chart(fig_event, use_container_width=True)


        ###Ranges

        fig_event = px.line(df_an, y=[125,250,375,500,625,750], x = df_worm.columns[1:], title="Splits Breakdown", markers=True)
        st.plotly_chart(fig_event, use_container_width=True)



    if race_type=="Women's Team Sprint":
        st.header('Women\'s Team Sprint')
        st.subheader('All results')
        marker = ["125m","250m","375m","500m","625m","750m"]
        @st.cache_data
        def get_data_from_excel():
            df = pd.read_excel(
                io='pages/WomensRaceResults.xlsm',
                engine ='openpyxl',
                sheet_name='Team Sprint',
                skiprows=0,
                usecols='A:V',
                nrows=520
                )
            df = df.replace(',','', regex=True)
            df['Date'] = pd.to_datetime(df['Date']).dt.date
        #     for i in range(len(df)):
        #         df["Date"][i] = df["Date"][i].date()
                #if df["125m"][i] != "NULL":
                    #df["125m"][i] = df["125m"][i].strftime("%M:%S.%f")
            return df
        df= get_data_from_excel()
        @st.cache_data
        def convert_to_csv(df):
            return df.to_csv(index=False,sep = ",").encode('utf-32')
        format_dict = {'Date': '{:%d-%m-%y}', 'Age1': '{0:,.2f}', 'Age2': '{0:,.2f}'}
        df_orig = df
        c1,c2,c3 = st.columns(3)
        with c1:
            year = st.multiselect(
                "Select Year:",
                options=df["Year"].unique(),
                default=df["Year"].unique()[0]
            )    
        if year:
            df = df.query(
                "Year == @year"
                )
        else:
            df=df_orig

        with c2:
            location = st.multiselect(
                "Select Location:",
                options=df["Location"].unique(),
                default=df["Location"].unique()[0]
            )

        if location:
            df = df.query(
                "Location == @location"
                )
        else:
            df=df_orig
        with c3:
            event = st.multiselect(
                "Select Event Type:",
                options=df["Event"].unique(),
                default=df["Event"].unique()[0]
            )

        if event:
            df = df.query(
                "Event == @event"
                )
        else:
            df=df_orig

        st.dataframe(df)
        ##Download buttons
        csv = convert_to_csv(df)
        download1 = st.download_button(
            label="Download Team Sprint data as CSV",
            data=csv,
            file_name='Team_Sprint_Data.csv',
            mime='text/csv',
            key="buffer1"
        )
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='Sheet1', index=False)
            writer.save()
            download2 = st.download_button(
                label="Download Team Sprint data as Excel",
                data=buffer,
                file_name='Team_Sprint_Data.xlsx',
                mime='application/vnd.ms-excel',
                key="buffer2"
            )
        ##Download buttons complete    
        st.markdown("---")

        st.title(":bar_chart: Top Ten Performances")

        df_topten = df_orig.sort_values("Time").head(10)

        st.dataframe(df_topten, use_container_width=True)
        ##Download buttons
        csvtt = convert_to_csv(df_topten)
        download1 = st.download_button(
            label="Download Top Ten data as CSV",
            data=csvtt,
            file_name='Team_Sprint_Data.csv',
            mime='text/csv',
            key="buffertt1"
        )
        buffertt = io.BytesIO()
        with pd.ExcelWriter(buffertt, engine='xlsxwriter') as writer:
            df_topten.to_excel(writer, sheet_name='Sheet1', index=False)
            writer.save()
            download2 = st.download_button(
                label="Download Top Ten data as Excel",
                data=buffertt,
                file_name='Team_Sprint_Data.xlsx',
                mime='application/vnd.ms-excel',
                key="buffertt2"
            )
        ##Download buttons complete  
        df_splits_tt = pd.DataFrame()
        df_splits_tt["Marker"] = ["125m","250m","375m","500m","625m","750m"]
        for i in range(len(df_topten)):
            var = str(i+1)+" "+str(df_topten["Country"].iloc[i]) + " " + str(df_topten["Year"].iloc[i]) + " " +str(df_topten["Location"].iloc[i])+" " +str(df_topten["Event"].iloc[i]) + " " +str(df_topten["Stage"].iloc[i])
            df_splits_tt[f"{var}"]=df_topten.iloc[i][15:21].values


        fig_tt = px.line(df_splits_tt, x="Marker", y = df_splits_tt.columns, title="Top Ten")

        st.plotly_chart(fig_tt, use_container_width=True)

        st.markdown("---")

        st.title(":bicyclist: Country History")

        #FILTERS FOR DATAFRAME

        countries = df_orig['Country'].drop_duplicates().sort_values()
        country = st.multiselect("Select Country:", countries)

        df_countryHistory = df_orig.query(
            "Country == @country"
        )

        if len(country)>0:
            #DATAFRAME
            df_countryHistory = df_countryHistory.sort_values("Date")


            st.dataframe(df_countryHistory)

            #DOWNLOAD BUTTONS
            csv_CH = convert_to_csv(df_countryHistory)
            buffer_ch = io.BytesIO()
            # download button 1 to download dataframe as csv
            downloadCH1 = st.download_button(
                label="Download Country History data as CSV",
                data=csv_CH,
                file_name='Team_Sprint_Country_History_Data.csv',
                mime='text/csv',
                key="DLCH1"
            )

            # download button 2 to download dataframe as xlsx
            with pd.ExcelWriter(buffer_ch, engine='xlsxwriter') as writer:
                # Write each dataframe to a different worksheet.
                df_countryHistory.to_excel(writer, sheet_name='Sheet1', index=False)
                # Close the Pandas Excel writer and output the Excel file to the buffer
                writer.save()

                downloadCH2 = st.download_button(
                    label="Download Country History data as Excel",
                    data=buffer_ch,
                    file_name='Teamp_Sprint_Country_History_Data.xlsx',
                    mime='application/vnd.ms-excel',
                    key="DLCH2"
                )

            ##Download buttons complete


            #FIRST FIGURE -- FINAL TIME PROGRESSION

            fig_country_history = px.line(df_countryHistory, x="Date", y = "Time", title = "Times by Date", color="Country",markers=True)
            fig_country_history.update_traces(textposition="top right")

            st.plotly_chart(fig_country_history, use_container_width=True)

            #Second Figure -- Chart with rider names

            df_splits_CH,df_worm_CH = pd.DataFrame(),pd.DataFrame()
            df_splits_CH["Marker"],df_worm_CH["Marker"] = marker,marker
            for i in range(len(df_countryHistory)):
                var = str(i+1)+" " +str(df_countryHistory["Country"].iloc[i]) + " " + str(df_countryHistory["Year"].iloc[i]) + " " +str(df_countryHistory["Event"].iloc[i]) + " " +str(df_countryHistory["Stage"].iloc[i])+ " " +str(df_countryHistory["Rider1"].iloc[i].split(" ")[0])+ " " +str(df_countryHistory["Rider2"].iloc[i].split(" ")[0])+ " " +str(df_countryHistory["Rider3"].iloc[i].split(" ")[0])
                df_splits_CH[f"{var}"]=df_countryHistory.iloc[i][15:21].values
                df_worm_CH[f"{var}"]=df_countryHistory.iloc[i][15:21].values.cumsum()


            fig_CH = px.line(df_splits_CH, x="Marker", y = df_splits_CH.columns, title="All Rides")


            st.plotly_chart(fig_CH, use_container_width=True)

            #Third Figure - Worm

            fig_event_CH = px.line(df_worm_CH, x="Marker", y = df_worm_CH.columns, title="The Worm")
            st.plotly_chart(fig_event_CH, use_container_width=True)



            #Fourth Figure - Ranges

            fig_ranges_CH = px.line(df_countryHistory, x=df_splits_CH.columns[1:], y = [125,250,375,500,625,750], title="The Ranges",markers=True)
            st.plotly_chart(fig_ranges_CH, use_container_width=True)





        st.markdown("---")

        st.title(":mag_right: Race Analysis Tool")
        uniqueYear = df_orig['Year'].drop_duplicates().sort_values(ascending=False)


        left_column, middle_column, right_column,c4 = st.columns(4)
        with left_column:
            an_year = st.selectbox("Select Year:", uniqueYear)

        df_an_year = df_orig.query(
            "Year == @an_year"
        )
        uniqueLocation = df_an_year['Location'].drop_duplicates().sort_values()

        with middle_column:
            an_location = st.selectbox("Select Location:", uniqueLocation)

        df_an_year_location = df_an_year.query(
            "Year == @an_year & Location == @an_location"
        )

        uniqueEvent = df_an_year_location['Event'].drop_duplicates().sort_values()
        with right_column:
            an_event = st.selectbox("Select Event:", uniqueEvent)

        df_an_year_location_event = df_an_year_location.query(
            "Year == @an_year & Location == @an_location & Event == @an_event"
        )

        uniqueStage = df_an_year_location_event['Stage'].drop_duplicates().sort_values()
        with c4:
            an_stage = st.selectbox("Select Stage:", uniqueStage)

        df_an = df_an_year_location_event.query(
            "Year == @an_year & Location == @an_location & Event == @an_event & Stage == @an_stage"
        )

        ### Splits dataframe and plot

        df_splits,df_worm = pd.DataFrame(),pd.DataFrame()
        df_splits["Marker"],df_worm["Marker"] = marker,marker
        for i in range(len(df_an)):
            var = str(df_an["Rank"].iloc[i])+" "+str(df_an["Country"].iloc[i])
            df_splits[f"{var}"]=df_an.iloc[i][15:21].values
            df_worm[f"{var}"]=df_an.iloc[i][15:21].values.cumsum()
        st.dataframe(df_an, use_container_width=True)

        fig_event = px.line(df_splits, x="Marker", y = df_splits.columns, title="Splits")
        st.plotly_chart(fig_event, use_container_width=True)

        ### Worm dataframe and plot

        fig_event = px.line(df_worm, x="Marker", y = df_worm.columns, title="The Worm")
        st.plotly_chart(fig_event, use_container_width=True)


        ###Ranges

        fig_event = px.line(df_an, y=[125,250,375,500,625,750], x = df_worm.columns[1:], title="The Ranges", markers=True)
        st.plotly_chart(fig_event, use_container_width=True)

    if race_type=="Men's Omnium":
        st.header('Men\'s Omnium')
        st.subheader('All results')

        @st.cache_data
        def get_points_data_from_excel():
            df_points = pd.read_excel(
                io='pages/MensRaceResults.xlsm',
                engine ='openpyxl',
                sheet_name='OM-Points',
                skiprows=0,
                usecols='A:AA',
                nrows=3000
                )
            df_points = df_points.replace(',','')
            df_points.Age = round(df_points.Age,2)
            return df_points
        df_points= get_points_data_from_excel()
        @st.cache_data
        def get_scracth_data_from_excel():
            df_scratch = pd.read_excel(
                io='pages/MensRaceResults.xlsm',
                engine ='openpyxl',
                sheet_name='OM-Scratch',
                skiprows=0,
                usecols='A:J',
                nrows=3000
                )
            df_scratch = df_scratch.replace(',','')
            df_scratch.Age = round(df_scratch.Age,2)
            return df_scratch
        df_scratch= get_scracth_data_from_excel()
        @st.cache_data
        def get_tempo_data_from_excel():
            df_tempo = pd.read_excel(
                io='pages/MensRaceResults.xlsm',
                engine ='openpyxl',
                sheet_name='OM-Tempo',
                skiprows=0,
                usecols='A:AW',
                nrows=3000
                )
            df_tempo = df_tempo.replace(',','')
            return df_tempo
        df_tempo= get_tempo_data_from_excel()
        @st.cache_data
        def get_elimination_data_from_excel():
            df_elim = pd.read_excel(
                io='pages/MensRaceResults.xlsm',
                engine ='openpyxl',
                sheet_name='OM-Elimination',
                skiprows=0,
                usecols='A:J',
                nrows=3000
                )
            df_elim = df_elim.replace(',','')
            df_elim.Age = round(df_elim.Age,2)
            return df_elim
        df_elim= get_elimination_data_from_excel()
        @st.cache_data
        def convert_to_csv(df):
            return df.to_csv(index=False,sep = ",").encode('utf-32')
        df_scratch_orig = df_scratch
        df_elim_orig = df_elim
        df_tempo_orig = df_tempo
        df_points_orig = df_points

        c1,c2,c3=st.columns(3)
        with c1:
            year = st.multiselect(
                "Select Year:",
                options=df_points["Year"].unique(),
                default=df_points["Year"].unique()[0]
            )    
        if year:
            df_points = df_points.query(
                "Year == @year"
                )
            df_scratch = df_scratch.query(
                "Year == @year"
                )
            df_elim = df_elim.query(
                "Year == @year"
                )
            df_tempo = df_tempo.query(
                "Year == @year"
                )
        else:
            df_points=df_points_orig
            df_scratch=df_scratch_orig
            df_tempo=df_tempo_orig
            df_elim=df_elim_orig

        with c2:
            location = st.multiselect(
                "Select Location:",
                options=df_points["Location"].unique(),
                default=df_points["Location"].unique()[0]
            )

        if location:
            df_points = df_points.query(
                "Location == @location"
                )
            df_scratch = df_scratch.query(
                "Location == @location"
                )
            df_elim = df_elim.query(
                "Location == @location"
                )
            df_tempo = df_tempo.query(
                "Location == @location"
                )
        else:
            df_points=df_points_orig
            df_scratch=df_scratch_orig
            df_tempo=df_tempo_orig
            df_elim=df_elim_orig
        with c3:
            event = st.multiselect(
                "Select Event Type:",
                options=df_points["Event"].unique(),
                default=df_points["Event"].unique()[0]
            )

        if event:
            df_points = df_points.query(
                "Event == @event"
                )
            df_scratch = df_scratch.query(
                "Event == @event"
                )
            df_elim = df_elim.query(
                "Event == @event"
                )
            df_tempo = df_tempo.query(
                "Event == @event"
                )
        else:
            df_points=df_points_orig
            df_scratch=df_scratch_orig
            df_tempo=df_tempo_orig
            df_elim=df_elim_orig

        st.subheader('Summary & Points Race')

        ##Defining colouring functions for dataframes
        format_dict = {'Scratch':'{0:,.0f}', 'Date': '{:%d-%m-%y}', 'Age': '{0:,.2f}', 'Avg Speed': '{0:,.3f}'}
        def color_points(val):
            if val == 5:
                background_color = 'darkgoldenrod'    
                return 'background-color: %s' % background_color
            elif val == 3:
                background_color = 'Silver'    
                return 'background-color: %s' % background_color 
            elif val == 2:
                background_color = 'Coral'    
                return 'background-color: %s' % background_color
            elif val == 1:
                background_color = 'darkcyan'    
                return 'background-color: %s' % background_color 
            else:
                background_color = ''    
                return 'background-color: %s' % background_color  
        def color_points_10(val):
            if val == 10:
                background_color = 'darkgoldenrod'    
                return 'background-color: %s' % background_color
            elif val == 6:
                background_color = 'Silver'    
                return 'background-color: %s' % background_color 
            elif val == 4:
                background_color = 'Coral'    
                return 'background-color: %s' % background_color
            elif val == 2:
                background_color = 'darkcyan'    
                return 'background-color: %s' % background_color 
            else:
                background_color = ''    
                return 'background-color: %s' % background_color  
        def color_plus_laps(val):
            if val >19:
                background_color = 'green'    
                return 'background-color: %s' % background_color
            else:
                background_color = ''    
                return 'background-color: %s' % background_color    
        def color_minus_laps(val):
            if val > 19:
                background_color = 'red'    
                return 'background-color: %s' % background_color
            else:
                background_color = ''    
                return 'background-color: %s' % background_color    
        def tempo_color_wins(val):
            background_color = 'yellow' if val == 1 else ""
            return 'background-color: %s' % background_color
        ##Displaying all dataframes, some styled
        df_points_styled = (df_points
                            .style
                            .applymap(color_points, subset=pd.IndexSlice[:, ["Sprint 1","Sprint 2","Sprint 3","Sprint 4","Sprint 5","Sprint 6","Sprint 7","Sprint 8","Sprint 9"]])
                            .applymap(color_points_10, subset=pd.IndexSlice[:, ["Sprint 10"]])
                            .applymap(color_plus_laps, subset=pd.IndexSlice[:, ["Lap +"]])
                            .applymap(color_minus_laps, subset=pd.IndexSlice[:, ["Lap -"]])
                            .format(format_dict))
        st.dataframe(df_points_styled,use_container_width=True)
        ##Download buttons
        csv_points = convert_to_csv(df_points)
        download1 = st.download_button(
            label="Download Omnium Summary as CSV",
            data=csv_points,
            file_name='Ommnium_Summary_Data.csv',
            mime='text/csv',
            key="OmSum1"
        )
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            df_points.to_excel(writer, sheet_name='Sheet1', index=False)
            writer.save()
            download2 = st.download_button(
                label="Download Ommnium Summary as Excel",
                data=buffer,
                file_name='Ommnium_Summary_Data.xlsx',
                mime='application/vnd.ms-excel',
            key="OmSum2"
            )
        ##Download buttons complete

        st.subheader('Scratch Race')
        st.dataframe(df_scratch.style.format(format_dict),use_container_width=True)
        ##Download buttons
        csv_scratch = convert_to_csv(df_scratch)
        download1 = st.download_button(
            label="Download Omnium Scratch Data as CSV",
            data=csv_scratch,
            file_name='Ommnium_Scratch_Data.csv',
            mime='text/csv',
            key="OmSc1"
        )
        buffer_scratch = io.BytesIO()
        with pd.ExcelWriter(buffer_scratch, engine='xlsxwriter') as writer:
            df_scratch.to_excel(writer, sheet_name='Sheet1', index=False)
            writer.save()
            download2 = st.download_button(
                label="Download Ommnium Scratch Data as Excel",
                data=buffer_scratch,
                file_name='Ommnium_Scratch_Data.xlsx',
                mime='application/vnd.ms-excel',
            key="OmSc2"
            )
        ##Download buttons complete
        st.subheader('Tempo Race')
        df_tempo_styled = (df_tempo
                           .style
                           .format(format_dict)
                           .applymap(tempo_color_wins, subset=pd.IndexSlice[:, [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36]]
                          )
                           .applymap(color_plus_laps, subset=pd.IndexSlice[:, ["P.Laps"]]
                          )
                           .applymap(color_minus_laps, subset=pd.IndexSlice[:, ["M.Laps"]]
                          )
                          )
        st.dataframe(df_tempo_styled,use_container_width=True)
        ##Download buttons
        csv_tempo = convert_to_csv(df_tempo)
        download1 = st.download_button(
            label="Download Omnium Tempo Data as CSV",
            data=csv_tempo,
            file_name='Ommnium_Tempo_Data.csv',
            mime='text/csv',
            key="OmTem1"
        )
        buffer_Tempo = io.BytesIO()
        with pd.ExcelWriter(buffer_Tempo, engine='xlsxwriter') as writer:
            df_tempo.to_excel(writer, sheet_name='Sheet1', index=False)
            writer.save()
            download2 = st.download_button(
                label="Download Ommnium Tempo Data as Excel",
                data=buffer_Tempo,
                file_name='Ommnium_Tempo_Data.xlsx',
                mime='application/vnd.ms-excel',
            key="OmTem2"
            )
        ##Download buttons complete
        st.subheader('Elimination Race')
        st.dataframe(df_elim.style.format(format_dict),use_container_width=True)
        ##Download buttons
        csv_elim = convert_to_csv(df_elim)
        download1 = st.download_button(
            label="Download Omnium Elim Data as CSV",
            data=csv_elim,
            file_name='Ommnium_Elim_Data.csv',
            mime='text/csv',
            key="OmEl1"
        )
        buffer_Elim = io.BytesIO()
        with pd.ExcelWriter(buffer_Elim, engine='xlsxwriter') as writer:
            df_elim.to_excel(writer, sheet_name='Sheet1', index=False)
            writer.save()
            download2 = st.download_button(
                label="Download Ommnium Elim Data as Excel",
                data=buffer_Elim,
                file_name='Ommnium_Elim_Data.xlsx',
                mime='application/vnd.ms-excel',
            key="OmEl2"
            )
        ##Download buttons complete

        st.markdown("---")

        st.title(":bicyclist: Rider History")

        names = df_points_orig['Name'].drop_duplicates().sort_values()
        name = st.multiselect("Select Rider(s):", names)

        df_countryHistory = df_points_orig.query(
            "Name == @name"
        )
        df_tempo_hist = df_tempo_orig.query(
            "Name == @name"
        )
        if len(name)>0:
            ## Sorting and displaying rider history plots
            df_countryHistory = df_countryHistory.sort_values("Date",ascending=False)
            df_countryHistory_styled = (df_countryHistory
                                         .style
                                         .applymap(color_points, subset=pd.IndexSlice[:, ["Sprint 1","Sprint 2","Sprint 3","Sprint 4","Sprint 5","Sprint 6","Sprint 7","Sprint 8","Sprint 9"]])
                                         .format(format_dict)
                                         .applymap(color_points_10, subset=pd.IndexSlice[:, ["Sprint 10"]])
                                         .applymap(color_plus_laps, subset=pd.IndexSlice[:, ["Lap +"]])
                                         .applymap(color_minus_laps, subset=pd.IndexSlice[:, ["Lap -"]])
                             )

            st.dataframe(df_countryHistory_styled)
            ##Download buttons
            csv_ah = convert_to_csv(df_countryHistory)
            download1 = st.download_button(
                label="Download Omnium Athlete History Data as CSV",
                data=csv_ah,
                file_name='Ommnium_Athlete_History.csv',
                mime='text/csv',
                key="Omah1"
            )
            buffer_ah = io.BytesIO()
            with pd.ExcelWriter(buffer_ah, engine='xlsxwriter') as writer:
                df_countryHistory.to_excel(writer, sheet_name='Sheet1', index=False)
                writer.save()
                download2 = st.download_button(
                    label="Download Omnium Athlete History Data as Excel",
                    data=buffer_ah,
                    file_name='Ommnium_Athlete_History.xlsx',
                    mime='application/vnd.ms-excel',
                key="Omah2"
                )
            ##Download buttons complete

            df_countryHistory_short = df_countryHistory[(df_countryHistory.Rank != "DSQ") & (df_countryHistory.Rank != "DNF")&(df_countryHistory.Final != "DSQ") & (df_countryHistory.Final != "DNF")]
            #st.dataframe(df_countryHistory_short)


            ##Overall Scoring Summary

            df_summ=df_countryHistory_short.drop(["Age",'Time','Avg Speed','Lap +','Lap -',"Sprint 1","Sprint 2","Sprint 3","Sprint 4","Sprint 5","Sprint 6","Sprint 7","Sprint 8","Sprint 9","Sprint 10"],axis=1)
            df_summ.insert(9, 'Points', df_summ["Final"]-df_summ["Sub Total"])
            df_summ_trans = pd.DataFrame()
            df_summ_trans["Race"] = ["Scratch","Tempo","Elimination","Points"]
            df_ch_Trans = pd.DataFrame()
            df_ch_Trans["Sprint"] = ["Sprint 1","Sprint 2","Sprint 3","Sprint 4","Sprint 5","Sprint 6","Sprint 7","Sprint 8","Sprint 9","Sprint 10"]
            for i in range(len(df_summ)):
                var = str(i+1)+" "+str(df_summ["Name"].iloc[i])+" " +str(df_summ["Location"].iloc[i])+" " +str(df_summ["Event"].iloc[i])+" " +str(df_summ["Year"].iloc[i])
                df_summ_trans[f"{var}"]=df_summ.iloc[i][7:11].values
                df_ch_Trans[f"{var}"]=df_countryHistory_short.iloc[i][12:22].values

            fig_event_mean = px.line(df_summ_trans, x="Race", y = df_summ_trans.columns[1:], title="Overall Scoring", markers=True)
            st.plotly_chart(fig_event_mean,use_container_width=True)

            ##Points race scoring
            fig_event = px.line(df_ch_Trans, x="Sprint", y = df_ch_Trans.columns, title="Points Race Scoring", markers=True)
            st.plotly_chart(fig_event,use_container_width=True)

            #Totals by Date
            fig_country_history = px.line(df_countryHistory, x="Date", y = "Final", title = "Totals by Date", markers = "True", text = "Location", color="Name")
            fig_country_history.update_traces(textposition="top right")
            st.plotly_chart(fig_country_history,use_container_width=True)

            ##Scratch totals by date
            fig_country_history = px.line(df_countryHistory, x="Date", y = "Scratch", title = "Scratch by Date", markers = "True", text = "Location", color="Name")
            fig_country_history.update_traces(textposition="top right")
            st.plotly_chart(fig_country_history,use_container_width=True)

            ##Tempo totals by date
            fig_country_history = px.line(df_countryHistory, x="Date", y = "Tempo", title = "Tempo by Date", markers = "True", text = "Location", color="Name")
            fig_country_history.update_traces(textposition="top right")
            st.plotly_chart(fig_country_history,use_container_width=True)

            ##Tempo distribution by date
            df_tempo_hist = df_tempo_hist[(df_tempo_hist.Rank != "DSQ") & (df_points_orig.Rank != "DNF")]
            df_tempo_hist = df_tempo_hist.sort_values("Date",ascending=False)
            df_tempo_hist_styled = df_tempo_hist.style.applymap(tempo_color_wins, subset=pd.IndexSlice[:, [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36]])                   .applymap(color_plus_laps, subset=pd.IndexSlice[:, ["P.Laps"]]
                          ).applymap(color_minus_laps, subset=pd.IndexSlice[:, ["M.Laps"]]
                          )
            st.dataframe(df_tempo_hist_styled)

            df_tempo_trans = pd.DataFrame()
            df_tempo_trans["Sprint"] = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36]
            for i in range(len(df_tempo_hist)):
                var =str(df_tempo_hist["Name"].iloc[i])+" "+str(df_tempo_hist["Location"].iloc[i])+" "+str(df_tempo_hist["Event"].iloc[i])+" "+str(df_tempo_hist["Year"].iloc[i])
                df_tempo_trans[f"{var}"]=df_tempo_hist.iloc[i][8:44].values

            fig_event = px.line(df_tempo_trans, x="Sprint", y = df_tempo_trans.columns, title="Tempo Distribution by date", markers=True)
            st.plotly_chart(fig_event,use_container_width=True)

            ##Elimination totals by date
            fig_country_history = px.line(df_countryHistory, x="Date", y = "Elimination", title = "Elimination by Date", markers = "True", text = "Location", color="Name")
            fig_country_history.update_traces(textposition="top right")
            st.plotly_chart(fig_country_history,use_container_width=True)

            ## Ranks by Date 
            fig_country_history = px.line(df_countryHistory, x="Date", y = "Rank", title = "Rank by Date", markers = "True", color="Name")
            st.plotly_chart(fig_country_history,use_container_width=True)




        st.markdown("---")

        st.title(":mag_right: Race Analysis Tool")
        uniqueYear = df_points_orig['Year'].drop_duplicates().sort_values(ascending=False)


        left_column, middle_column, right_column = st.columns(3)
        with left_column:
            an_year = st.selectbox("Select Year:", uniqueYear)

        df_an_year = df_points_orig.query(
            "Year == @an_year"
        )
        uniqueLocation = df_an_year['Location'].drop_duplicates().sort_values()

        with middle_column:
            an_location = st.selectbox("Select Location:", uniqueLocation)

        df_an_year_location = df_an_year.query(
            "Year == @an_year & Location == @an_location"
        )

        uniqueEvent = df_an_year_location['Event'].drop_duplicates().sort_values()
        with right_column:
            an_event = st.selectbox("Select Event:", uniqueEvent)

        df_an = df_an_year_location.query(
            "Year == @an_year & Location == @an_location & Event == @an_event"
        )


        df_an_styled = (df_an
                            .style
                            .applymap(color_points, subset=pd.IndexSlice[:, ["Sprint 1","Sprint 2","Sprint 3","Sprint 4","Sprint 5","Sprint 6","Sprint 7","Sprint 8","Sprint 9"]])
                            .applymap(color_points_10, subset=pd.IndexSlice[:, ["Sprint 10"]])
                            .applymap(color_plus_laps, subset=pd.IndexSlice[:, ["Lap +"]])
                            .applymap(color_minus_laps, subset=pd.IndexSlice[:, ["Lap -"]])
                            .format(format_dict))
        st.dataframe(df_an_styled)

        df_summary = df_an.drop(["Year","Age",'Time','Avg Speed','Lap +','Lap -',"Sprint 1","Sprint 2","Sprint 3","Sprint 4","Sprint 5","Sprint 6","Sprint 7","Sprint 8","Sprint 9","Sprint 10","Country","Event","Date","Year","Location"],axis=1)
        df_summary = df_summary[(df_summary.Rank != "DSQ") & (df_summary.Rank != "DNF")&(df_summary.Final != "DSQ") & (df_summary.Final != "DNF")]
        df_summary.insert(5, 'Points', df_summary["Final"]-df_summary["Sub Total"])

        df_summary = df_summary.drop(["Sub Total"],axis=1)
        #st.dataframe(df_summary)


        df_summary_transpose = pd.DataFrame()
        df_summary_transpose["Race"] = ["Scratch","Tempo","Elimination","Points"]
        for i in range(len(df_summary)):
            var = str(df_summary["Name"].iloc[i])
            df_summary_transpose[f"{var}"]=df_summary.iloc[i][2:6].values
            
            
        #Use this to add a discrete color scale to line graphs            
#         n_colors=len(df_an)
#         colors = px.colors.sample_colorscale("hsv", [n/(n_colors -1) for n in range(n_colors)])
#         ,color_discrete_sequence=colors -- add this to the end of px.line
        fig_event_mean = px.line(df_summary_transpose, x="Race", y = df_summary_transpose.columns[1:], title="Omnium Summary", markers=True)
        st.plotly_chart(fig_event_mean,use_container_width=True)

        df_summary = df_summary[(df_summary.Rank != "DSQ") & (df_summary.Rank != "DNF")]
        df_summary_worm = pd.DataFrame()
        df_summary_worm["Race"] = ["Scratch","Tempo","Elimination","Points"]
        for i in range(len(df_summary)):
            var = str(df_summary["Name"].iloc[i])
            df_summary_worm[f"{var}"]=df_summary.iloc[i][2:6].values.cumsum()


        fig_worm = px.line(df_summary_worm, x="Race", y = df_summary_worm.columns, title="Omnium Worm")
        st.plotly_chart(fig_worm,use_container_width=True)

        ### Splits dataframe and plot

        df_splits = pd.DataFrame()
        df_splits["Marker"] = ["Sprint 1","Sprint 2","Sprint 3","Sprint 4","Sprint 5","Sprint 6","Sprint 7","Sprint 8","Sprint 9","Sprint 10"]
        for i in range(len(df_an)):
            var = str(df_an["Name"].iloc[i])
            df_splits[f"{var}"]=df_an.iloc[i][12:22].values


        fig_event = px.line(df_splits, x="Marker", y = df_splits.columns, title="Points Race Sprint Points", markers=True)

        st.plotly_chart(fig_event,use_container_width=True)

        ### Worm 

        df_worm = pd.DataFrame()
        df_worm["Marker"] = ["Sprint 1","Sprint 2","Sprint 3","Sprint 4","Sprint 5","Sprint 6","Sprint 7","Sprint 8","Sprint 9","Sprint 10"]
        for i in range(len(df_an)):
            var = str(df_an["Name"].iloc[i])
            df_worm[f"{var}"]=df_an.iloc[i][12:22].values.cumsum()

        fig_worm = px.line(df_worm, x="Marker", y = df_worm.columns, title="Points Race Worm")
        st.plotly_chart(fig_worm,use_container_width=True)

        ##Tempo Distribution

        df_tempo_an = df_tempo_orig.query(
            "Year == @an_year & Location == @an_location & Event == @an_event"
        )

        df_tempo_an_trans = pd.DataFrame()
        df_tempo_an_trans["Sprint"] = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36]
        for i in range(len(df_tempo_an)):
            var =str(df_tempo_an["Name"].iloc[i])
            df_tempo_an_trans[f"{var}"]=df_tempo_an.iloc[i][8:44].values

        fig_event = px.line(df_tempo_an_trans, x="Sprint", y = df_tempo_an_trans.columns, title="Tempo Distribution", markers=True)
        st.plotly_chart(fig_event,use_container_width=True)

        ###The Ranges


        fig_event = px.line(df_an, y=["Sprint 1","Sprint 2","Sprint 3","Sprint 4","Sprint 5","Sprint 6","Sprint 7","Sprint 8","Sprint 9","Sprint 10"], x = "Name", title="The Ranges", markers=True)
        #fig_event.update_layout(legend_title="legend")
        st.plotly_chart(fig_event,use_container_width=True)


        ##
        st.markdown("---")
        st.header("Points by Position")
        df_points_orig = df_points_orig.replace(["DNS","REL","DNF","DSQ"], np.nan) 
        df_points_orig = df_points_orig.dropna() 
        df_points_by_pos=df_points_orig.groupby("Rank", as_index=False).mean()
        df_points_by_pos=df_points_by_pos.drop(columns=["Year","Age","Avg Speed"])
        df_points_by_pos
        st.markdown("---")
        st.header("Dataset Averages")

        df_mean_points = df_points_orig.groupby('Name', as_index=False).mean()
        df_mean_tempo = df_tempo_orig.groupby('Name', as_index=False).mean()
        df_mean_points=df_mean_points.drop(['Year','Age','Scratch','Lap +','Lap -','Avg Speed'],axis=1)
        df_mean_total = df_points_orig[(df_points_orig.Final != "DSQ") & (df_points_orig.Final != "DNF")]







        riders_avg= st.multiselect(
                "Select Rider(s):",
                options=df_points_orig['Name'].drop_duplicates().sort_values(),
                key="rider averages",
                #default=df_points_orig['Name'].drop_duplicates().sort_values()[0]
            )    
        if len(riders_avg) !=0:
            df_mean_points=df_mean_points[(df_mean_points.Name.isin(riders_avg))]
            df_mean_tempo=df_mean_tempo[(df_mean_tempo.Name.isin(riders_avg))]
            df_mean_total=df_mean_total[(df_mean_total.Name.isin(riders_avg))]
            df_mean_total.Final = pd.to_numeric(df_mean_total.Final)
            df_mean_total.Tempo = pd.to_numeric(df_mean_total.Tempo)
            df_mean_total.Elimination = pd.to_numeric(df_mean_total.Elimination)
            df_mean_total["Sub Total"] = pd.to_numeric(df_mean_total["Sub Total"])
            df_mean_total["Points"] = df_mean_total["Final"]-df_mean_total["Sub Total"]
            df_mean_total=df_mean_total.drop(["Year","Age",'Time','Avg Speed','Lap +','Lap -',"Sprint 1","Sprint 2","Sprint 3","Sprint 4","Sprint 5","Sprint 6","Sprint 7","Sprint 8","Sprint 9","Sprint 10","Sub Total","Final"],axis=1)
            df_mean_total = df_mean_total.groupby('Name', as_index=False).mean()



            df_mean_points_transpose = pd.DataFrame()
            df_mean_points_transpose["Marker"] = ["Sprint 1","Sprint 2","Sprint 3","Sprint 4","Sprint 5","Sprint 6","Sprint 7","Sprint 8","Sprint 9","Sprint 10"]
            df_mean_tempo_transpose = pd.DataFrame()
            df_mean_tempo_transpose["Marker"] = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36]
            df_mean_total_transpose = pd.DataFrame()
            df_mean_total_transpose["Marker"] = ["Scratch","Tempo","Elimination","Points"]
            for i in range(len(df_mean_points)):
                var = str(df_mean_points["Name"].iloc[i])
                df_mean_points_transpose[f"{var}"]=df_mean_points.iloc[i][1:12].values
                df_mean_total_transpose[f"{var}"]=df_mean_total.iloc[i][1:5].values
                df_mean_tempo_transpose[f"{var}"]=df_mean_tempo.iloc[i][3:39].values

            ##Points scoring average plot
            fig_point_mean = px.line(df_mean_points_transpose, x="Marker", y = df_mean_points_transpose.columns[1:], title="Points Scoring Average", markers=True)
            st.plotly_chart(fig_point_mean,use_container_width=True)

            ##Tempo scoring average plot

            fig_tempo_mean = px.line(df_mean_tempo_transpose, x="Marker", y = df_mean_tempo_transpose.columns[1:], title="Tempo Scoring Average", markers=True)
            st.plotly_chart(fig_tempo_mean,use_container_width=True)



            ##Overall Averages plot
            fig_overall_mean = px.line(df_mean_total_transpose, x="Marker", y = df_mean_total_transpose.columns[1:], title="Overall Averages", markers=True)
            st.plotly_chart(fig_overall_mean,use_container_width=True)

            
    if race_type=="Women's Omnium":
        st.header('Women\'s Omnium')
        st.subheader('All results')

        @st.cache_data
        def get_points_data_from_excel():
            df_points = pd.read_excel(
                io='pages/WomensRaceResults.xlsm',
                engine ='openpyxl',
                sheet_name='OM-Points',
                skiprows=0,
                usecols='A:AA',
                nrows=3000
                )
            df_points = df_points.replace(',','')
            df_points.Age = round(df_points.Age,2)
            df_points = df_points.replace(["REL","DNF","DNS"], np.nan) 
            df_points = df_points.dropna() 
            return df_points
        df_points= get_points_data_from_excel()
        @st.cache_data
        def get_scracth_data_from_excel():
            df_scratch = pd.read_excel(
                io='pages/WomensRaceResults.xlsm',
                engine ='openpyxl',
                sheet_name='OM-Scratch',
                skiprows=0,
                usecols='A:J',
                nrows=3000
                )
            df_scratch = df_scratch.replace(',','')
            df_scratch.Age = round(df_scratch.Age,2)
            return df_scratch
        df_scratch= get_scracth_data_from_excel()
        @st.cache_data
        def get_tempo_data_from_excel():
            df_tempo = pd.read_excel(
                io='pages/WomensRaceResults.xlsm',
                engine ='openpyxl',
                sheet_name='OM-Tempo',
                skiprows=0,
                usecols='A:AW',
                nrows=3000
                )
            df_tempo = df_tempo.replace(',','')
            return df_tempo
        df_tempo= get_tempo_data_from_excel()
        @st.cache_data
        def get_elimination_data_from_excel():
            df_elim = pd.read_excel(
                io='pages/WomensRaceResults.xlsm',
                engine ='openpyxl',
                sheet_name='OM-Elimination',
                skiprows=0,
                usecols='A:J',
                nrows=3000
                )
            df_elim = df_elim.replace(',','')
            df_elim.Age = round(df_elim.Age,2)
            return df_elim
        df_elim= get_elimination_data_from_excel()
        @st.cache_data
        def convert_to_csv(df):
            return df.to_csv(index=False,sep = ",").encode('utf-32')
        df_scratch_orig = df_scratch
        df_elim_orig = df_elim
        df_tempo_orig = df_tempo
        df_points_orig = df_points

        c1,c2,c3=st.columns(3)
        with c1:
            year = st.multiselect(
                "Select Year:",
                options=df_points["Year"].unique(),
                default=df_points["Year"].unique()[0]
            )    
        if year:
            df_points = df_points.query(
                "Year == @year"
                )
            df_scratch = df_scratch.query(
                "Year == @year"
                )
            df_elim = df_elim.query(
                "Year == @year"
                )
            df_tempo = df_tempo.query(
                "Year == @year"
                )
        else:
            df_points=df_points_orig
            df_scratch=df_scratch_orig
            df_tempo=df_tempo_orig
            df_elim=df_elim_orig

        with c2:
            location = st.multiselect(
                "Select Location:",
                options=df_points["Location"].unique(),
                default=df_points["Location"].unique()[0]
            )

        if location:
            df_points = df_points.query(
                "Location == @location"
                )
            df_scratch = df_scratch.query(
                "Location == @location"
                )
            df_elim = df_elim.query(
                "Location == @location"
                )
            df_tempo = df_tempo.query(
                "Location == @location"
                )
        else:
            df_points=df_points_orig
            df_scratch=df_scratch_orig
            df_tempo=df_tempo_orig
            df_elim=df_elim_orig
        with c3:
            event = st.multiselect(
                "Select Event Type:",
                options=df_points["Event"].unique(),
                default=df_points["Event"].unique()[0]
            )

        if event:
            df_points = df_points.query(
                "Event == @event"
                )
            df_scratch = df_scratch.query(
                "Event == @event"
                )
            df_elim = df_elim.query(
                "Event == @event"
                )
            df_tempo = df_tempo.query(
                "Event == @event"
                )
        else:
            df_points=df_points_orig
            df_scratch=df_scratch_orig
            df_tempo=df_tempo_orig
            df_elim=df_elim_orig

        st.subheader('Summary & Points Race')

        ##Defining colouring functions for dataframes
        format_dict = {'Scratch':'{0:,.0f}', 'Date': '{:%d-%m-%y}', 'Age': '{0:,.2f}', 'Sub Total': '{0:,.0f}', 'Avg Speed': '{0:,.3f}'}
        def color_points(val):
            if val == 5:
                background_color = 'darkgoldenrod'    
                return 'background-color: %s' % background_color
            elif val == 3:
                background_color = 'Silver'    
                return 'background-color: %s' % background_color 
            elif val == 2:
                background_color = 'Coral'    
                return 'background-color: %s' % background_color
            elif val == 1:
                background_color = 'darkcyan'    
                return 'background-color: %s' % background_color 
            else:
                background_color = ''    
                return 'background-color: %s' % background_color  
        def color_points_10(val):
            if val == 10:
                background_color = 'darkgoldenrod'    
                return 'background-color: %s' % background_color
            elif val == 6:
                background_color = 'Silver'    
                return 'background-color: %s' % background_color 
            elif val == 4:
                background_color = 'Coral'    
                return 'background-color: %s' % background_color
            elif val == 2:
                background_color = 'darkcyan'    
                return 'background-color: %s' % background_color 
            else:
                background_color = ''    
                return 'background-color: %s' % background_color  
        def color_plus_laps(val):
            if val >19:
                background_color = 'green'    
                return 'background-color: %s' % background_color
            else:
                background_color = ''    
                return 'background-color: %s' % background_color    
        def color_minus_laps(val):
            if val > 19:
                background_color = 'red'    
                return 'background-color: %s' % background_color
            else:
                background_color = ''    
                return 'background-color: %s' % background_color    
        def tempo_color_wins(val):
            background_color = 'yellow' if val == 1 else ""
            return 'background-color: %s' % background_color
        ##Displaying all dataframes, some styled
        df_points_styled = (df_points
                            .style
                            .applymap(color_points, subset=pd.IndexSlice[:, ["Sprint 1","Sprint 2","Sprint 3","Sprint 4","Sprint 5","Sprint 6","Sprint 7"]])
                            .applymap(color_points_10, subset=pd.IndexSlice[:, ["Sprint 8"]])
                            .applymap(color_plus_laps, subset=pd.IndexSlice[:, ["Lap +"]])
                            .applymap(color_minus_laps, subset=pd.IndexSlice[:, ["Lap -"]])
                            .format(format_dict))
        st.dataframe(df_points_styled,use_container_width=True)
        ##Download buttons
        csv_points = convert_to_csv(df_points)
        download1 = st.download_button(
            label="Download Omnium Summary as CSV",
            data=csv_points,
            file_name='Ommnium_Summary_Data.csv',
            mime='text/csv',
            key="OmSum1"
        )
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            df_points.to_excel(writer, sheet_name='Sheet1', index=False)
            writer.save()
            download2 = st.download_button(
                label="Download Ommnium Summary as Excel",
                data=buffer,
                file_name='Ommnium_Summary_Data.xlsx',
                mime='application/vnd.ms-excel',
            key="OmSum2"
            )
        ##Download buttons complete

        st.subheader('Scratch Race')
        st.dataframe(df_scratch.style.format(format_dict),use_container_width=True)
        ##Download buttons
        csv_scratch = convert_to_csv(df_scratch)
        download1 = st.download_button(
            label="Download Omnium Scratch Data as CSV",
            data=csv_scratch,
            file_name='Ommnium_Scratch_Data.csv',
            mime='text/csv',
            key="OmSc1"
        )
        buffer_scratch = io.BytesIO()
        with pd.ExcelWriter(buffer_scratch, engine='xlsxwriter') as writer:
            df_scratch.to_excel(writer, sheet_name='Sheet1', index=False)
            writer.save()
            download2 = st.download_button(
                label="Download Ommnium Scratch Data as Excel",
                data=buffer_scratch,
                file_name='Ommnium_Scratch_Data.xlsx',
                mime='application/vnd.ms-excel',
            key="OmSc2"
            )
        ##Download buttons complete
        st.subheader('Tempo Race')
        df_tempo_styled = (df_tempo
                           .style
                           .format(format_dict)
                           .applymap(tempo_color_wins, subset=pd.IndexSlice[:, [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26]]
                          )
                           .applymap(color_plus_laps, subset=pd.IndexSlice[:, ["P.Laps"]]
                          )
                           .applymap(color_minus_laps, subset=pd.IndexSlice[:, ["M.Laps"]]
                          )
                          )
        st.dataframe(df_tempo_styled,use_container_width=True)
        ##Download buttons
        csv_tempo = convert_to_csv(df_tempo)
        download1 = st.download_button(
            label="Download Omnium Tempo Data as CSV",
            data=csv_tempo,
            file_name='Ommnium_Tempo_Data.csv',
            mime='text/csv',
            key="OmTem1"
        )
        buffer_Tempo = io.BytesIO()
        with pd.ExcelWriter(buffer_Tempo, engine='xlsxwriter') as writer:
            df_tempo.to_excel(writer, sheet_name='Sheet1', index=False)
            writer.save()
            download2 = st.download_button(
                label="Download Ommnium Tempo Data as Excel",
                data=buffer_Tempo,
                file_name='Ommnium_Tempo_Data.xlsx',
                mime='application/vnd.ms-excel',
            key="OmTem2"
            )
        ##Download buttons complete
        st.subheader('Elimination Race')
        st.dataframe(df_elim.style.format(format_dict),use_container_width=True)
        ##Download buttons
        csv_elim = convert_to_csv(df_elim)
        download1 = st.download_button(
            label="Download Omnium Elim Data as CSV",
            data=csv_elim,
            file_name='Ommnium_Elim_Data.csv',
            mime='text/csv',
            key="OmEl1"
        )
        buffer_Elim = io.BytesIO()
        with pd.ExcelWriter(buffer_Elim, engine='xlsxwriter') as writer:
            df_elim.to_excel(writer, sheet_name='Sheet1', index=False)
            writer.save()
            download2 = st.download_button(
                label="Download Ommnium Elim Data as Excel",
                data=buffer_Elim,
                file_name='Ommnium_Elim_Data.xlsx',
                mime='application/vnd.ms-excel',
            key="OmEl2"
            )
        ##Download buttons complete

        st.markdown("---")

        st.title(":bicyclist: Rider History")

        names = df_points_orig['Name'].drop_duplicates().sort_values()
        name = st.multiselect("Select Rider(s):", names)

        df_countryHistory = df_points_orig.query(
            "Name == @name"
        )
        df_tempo_hist = df_tempo_orig.query(
            "Name == @name"
        )
        if len(name)>0:
            ## Sorting and displaying rider history plots
            df_countryHistory = df_countryHistory.sort_values("Date",ascending=False)
            df_countryHistory_styled = (df_countryHistory
                                         .style
                                         .applymap(color_points, subset=pd.IndexSlice[:, ["Sprint 1","Sprint 2","Sprint 3","Sprint 4","Sprint 5","Sprint 6","Sprint 7"]])
                                         .format(format_dict)
                                         .applymap(color_points_10, subset=pd.IndexSlice[:, ["Sprint 8"]])
                                         .applymap(color_plus_laps, subset=pd.IndexSlice[:, ["Lap +"]])
                                         .applymap(color_minus_laps, subset=pd.IndexSlice[:, ["Lap -"]])
                             )

            st.dataframe(df_countryHistory_styled)
            ##Download buttons
            csv_ah = convert_to_csv(df_countryHistory)
            download1 = st.download_button(
                label="Download Omnium Athlete History Data as CSV",
                data=csv_ah,
                file_name='Ommnium_Athlete_History.csv',
                mime='text/csv',
                key="Omah1"
            )
            buffer_ah = io.BytesIO()
            with pd.ExcelWriter(buffer_ah, engine='xlsxwriter') as writer:
                df_countryHistory.to_excel(writer, sheet_name='Sheet1', index=False)
                writer.save()
                download2 = st.download_button(
                    label="Download Omnium Athlete History Data as Excel",
                    data=buffer_ah,
                    file_name='Ommnium_Athlete_History.xlsx',
                    mime='application/vnd.ms-excel',
                key="Omah2"
                )
            ##Download buttons complete

            df_countryHistory_short = df_countryHistory[(df_countryHistory.Rank != "DSQ") & (df_countryHistory.Rank != "DNF")&(df_countryHistory.Final != "DSQ") & (df_countryHistory.Final != "DNF")]
            #st.dataframe(df_countryHistory_short)


            ##Overall Scoring Summary

            df_summ=df_countryHistory_short.drop(["Age",'Time','Avg Speed','Lap +','Lap -',"Sprint 1","Sprint 2","Sprint 3","Sprint 4","Sprint 5","Sprint 6","Sprint 7","Sprint 8"],axis=1)
            df_summ.insert(10, 'Points', df_summ["Final"]-df_summ["Sub Total"])
            df_summ_trans = pd.DataFrame()
            df_summ_trans["Race"] = ["Scratch","Tempo","Elimination","Points"]
            df_ch_Trans = pd.DataFrame()
            df_ch_Trans["Sprint"] = ["Sprint 1","Sprint 2","Sprint 3","Sprint 4","Sprint 5","Sprint 6","Sprint 7","Sprint 8"]
            for i in range(len(df_summ)):
                var = str(i+1)+" "+str(df_summ["Name"].iloc[i])+" " +str(df_summ["Location"].iloc[i])+" " +str(df_summ["Event"].iloc[i])+" " +str(df_summ["Year"].iloc[i])
                df_summ_trans[f"{var}"]=df_summ.iloc[i][7:11].values
                df_ch_Trans[f"{var}"]=df_countryHistory_short.iloc[i][12:20].values
            
            fig_event_mean = px.line(df_summ_trans, x="Race", y = df_summ_trans.columns[1:], title="Overall Scoring", markers=True)
            st.plotly_chart(fig_event_mean,use_container_width=True)

            ##Points race scoring
            fig_event = px.line(df_ch_Trans, x="Sprint", y = df_ch_Trans.columns, title="Points Race Scoring", markers=True)
            st.plotly_chart(fig_event,use_container_width=True)

            #Totals by Date
            fig_country_history = px.line(df_countryHistory, x="Date", y = "Final", title = "Totals by Date", markers = "True", color="Name")
            fig_country_history.update_traces(textposition="top right")
            st.plotly_chart(fig_country_history,use_container_width=True)

            ##Scratch totals by date
            fig_country_history = px.line(df_countryHistory, x="Date", y = "Scratch", title = "Scratch by Date", markers = "True", text = "Location", color="Name")
            fig_country_history.update_traces(textposition="top right")
            st.plotly_chart(fig_country_history,use_container_width=True)

            ##Tempo totals by date
            fig_country_history = px.line(df_countryHistory, x="Date", y = "Tempo", title = "Tempo by Date", markers = "True", text = "Location", color="Name")
            fig_country_history.update_traces(textposition="top right")
            st.plotly_chart(fig_country_history,use_container_width=True)

            ##Tempo distribution by date
            df_tempo_hist = df_tempo_hist[(df_tempo_hist.Rank != "DSQ") & (df_points_orig.Rank != "DNF")]
            df_tempo_hist = df_tempo_hist.sort_values("Date",ascending=False)
            df_tempo_hist_styled = df_tempo_hist.style.applymap(tempo_color_wins, subset=pd.IndexSlice[:, [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26]])                   .applymap(color_plus_laps, subset=pd.IndexSlice[:, ["P.Laps"]]
                          ).applymap(color_minus_laps, subset=pd.IndexSlice[:, ["M.Laps"]]
                          )
            

            df_tempo_trans = pd.DataFrame()
            df_tempo_trans["Sprint"] = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26]
            for i in range(len(df_tempo_hist)):
                var =str(df_tempo_hist["Name"].iloc[i])+" "+str(df_tempo_hist["Location"].iloc[i])+" "+str(df_tempo_hist["Event"].iloc[i])+" "+str(df_tempo_hist["Year"].iloc[i])
                df_tempo_trans[f"{var}"]=df_tempo_hist.iloc[i][8:34].values

            fig_event = px.line(df_tempo_trans, x="Sprint", y = df_tempo_trans.columns, title="Tempo Distribution by Date", markers=True)
            st.plotly_chart(fig_event,use_container_width=True)

            ##Elimination totals by date
            fig_country_history = px.line(df_countryHistory, x="Date", y = "Elimination", title = "Elimination by Date", markers = "True", text = "Location", color="Name")
            fig_country_history.update_traces(textposition="top right")
            st.plotly_chart(fig_country_history,use_container_width=True)

            ## Ranks by Date 
            fig_country_history = px.line(df_countryHistory, x="Date", y = "Rank", title = "Rank by Date", markers = "True", color="Name")
            st.plotly_chart(fig_country_history,use_container_width=True)




        st.markdown("---")

        st.title(":mag_right: Race Analysis Tool")
        uniqueYear = df_points_orig['Year'].drop_duplicates().sort_values(ascending=False)


        left_column, middle_column, right_column = st.columns(3)
        with left_column:
            an_year = st.selectbox("Select Year:", uniqueYear)

        df_an_year = df_points_orig.query(
            "Year == @an_year"
        )
        uniqueLocation = df_an_year['Location'].drop_duplicates().sort_values()

        with middle_column:
            an_location = st.selectbox("Select Location:", uniqueLocation)

        df_an_year_location = df_an_year.query(
            "Year == @an_year & Location == @an_location"
        )

        uniqueEvent = df_an_year_location['Event'].drop_duplicates().sort_values()
        with right_column:
            an_event = st.selectbox("Select Event:", uniqueEvent)

        df_an = df_an_year_location.query(
            "Year == @an_year & Location == @an_location & Event == @an_event"
        )


        df_an_styled = (df_an
                            .style
                            .applymap(color_points, subset=pd.IndexSlice[:, ["Sprint 1","Sprint 2","Sprint 3","Sprint 4","Sprint 5","Sprint 6","Sprint 7"]])
                            .applymap(color_points_10, subset=pd.IndexSlice[:, ["Sprint 8"]])
                            .applymap(color_plus_laps, subset=pd.IndexSlice[:, ["Lap +"]])
                            .applymap(color_minus_laps, subset=pd.IndexSlice[:, ["Lap -"]])
                            .format(format_dict))
        st.dataframe(df_an_styled)

        df_summary = df_an.drop(["Year","Age",'Time','Avg Speed','Lap +','Lap -',"Sprint 1","Sprint 2","Sprint 3","Sprint 4","Sprint 5","Sprint 6","Sprint 7","Sprint 8","Nat","Event","Date","Year","Location"],axis=1)
        df_summary = df_summary[(df_summary.Rank != "DSQ") & (df_summary.Rank != "DNF")&(df_summary.Final != "DSQ") & (df_summary.Final != "DNF")]
        df_summary.insert(5, 'Points', df_summary["Final"]-df_summary["Sub Total"])

        df_summary = df_summary.drop(["Sub Total"],axis=1)
        #st.dataframe(df_summary)


        df_summary_transpose = pd.DataFrame()
        df_summary_transpose["Race"] = ["Scratch","Tempo","Elimination","Points"]
        for i in range(len(df_summary)):
            var = str(df_summary["Name"].iloc[i])
            df_summary_transpose[f"{var}"]=df_summary.iloc[i][2:6].values

        fig_event_mean = px.line(df_summary_transpose, x="Race", y = df_summary_transpose.columns[1:], title="Omnium Summary", markers=True)
        st.plotly_chart(fig_event_mean,use_container_width=True)

        df_summary = df_summary[(df_summary.Rank != "DSQ") & (df_summary.Rank != "DNF")]
        df_summary_worm = pd.DataFrame()
        df_summary_worm["Race"] = ["Scratch","Tempo","Elimination","Points"]
        for i in range(len(df_summary)):
            var = str(df_summary["Name"].iloc[i])
            df_summary_worm[f"{var}"]=df_summary.iloc[i][2:6].values.cumsum()


        fig_worm = px.line(df_summary_worm, x="Race", y = df_summary_worm.columns, title="Omnium Worm")
        st.plotly_chart(fig_worm,use_container_width=True)

        ### Splits dataframe and plot

        df_splits = pd.DataFrame()
        df_splits["Marker"] = ["Sprint 1","Sprint 2","Sprint 3","Sprint 4","Sprint 5","Sprint 6","Sprint 7","Sprint 8"]
        for i in range(len(df_an)):
            var = str(df_an["Name"].iloc[i])
            df_splits[f"{var}"]=df_an.iloc[i][12:20].values


        fig_event = px.line(df_splits, x="Marker", y = df_splits.columns, title="Points Race Sprint Points", markers=True)

        st.plotly_chart(fig_event,use_container_width=True)

        ### Worm 

        df_worm = pd.DataFrame()
        df_worm["Marker"] = ["Sprint 1","Sprint 2","Sprint 3","Sprint 4","Sprint 5","Sprint 6","Sprint 7","Sprint 8"]
        for i in range(len(df_an)):
            var = str(df_an["Name"].iloc[i])
            df_worm[f"{var}"]=df_an.iloc[i][12:20].values.cumsum()

        fig_worm = px.line(df_worm, x="Marker", y = df_worm.columns, title="Points Race Worm")
        st.plotly_chart(fig_worm,use_container_width=True)

        ##Tempo Distribution

        df_tempo_an = df_tempo_orig.query(
            "Year == @an_year & Location == @an_location & Event == @an_event"
        )

        df_tempo_an_trans = pd.DataFrame()
        df_tempo_an_trans["Sprint"] = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26]
        for i in range(len(df_tempo_an)):
            var =str(df_tempo_an["Name"].iloc[i])
            df_tempo_an_trans[f"{var}"]=df_tempo_an.iloc[i][8:34].values

        fig_event = px.line(df_tempo_an_trans, x="Sprint", y = df_tempo_an_trans.columns, title="Tempo Distribution", markers=True)
        st.plotly_chart(fig_event,use_container_width=True)

        ###The Ranges


        fig_event = px.line(df_an, y=["Sprint 1","Sprint 2","Sprint 3","Sprint 4","Sprint 5","Sprint 6","Sprint 7","Sprint 8"], x = "Name", title="Points race Ranges", markers=True)
        #fig_event.update_layout(legend_title="legend")
        st.plotly_chart(fig_event,use_container_width=True)


        ##
        st.markdown("---")
        st.header("Dataset Averages")

        df_mean_points = df_points_orig.groupby('Name', as_index=False).mean()
        df_mean_tempo = df_tempo_orig.groupby('Name', as_index=False).mean()
        df_mean_points=df_mean_points.drop(['Year','Age','Lap +','Lap -','Avg Speed'],axis=1)
        df_mean_total = df_points_orig[(df_points_orig.Final != "DSQ") & (df_points_orig.Final != "DNF")]







        riders_avg= st.multiselect(
                "Select Rider(s):",
                options=df_points_orig['Name'].drop_duplicates().sort_values(),
                key="rider averages",
                #default=df_points_orig['Name'].drop_duplicates().sort_values()[0]
            )    
        if len(riders_avg) !=0:
            df_mean_points=df_mean_points[(df_mean_points.Name.isin(riders_avg))]
            df_mean_tempo=df_mean_tempo[(df_mean_tempo.Name.isin(riders_avg))]
            df_mean_total=df_mean_total[(df_mean_total.Name.isin(riders_avg))]
            df_mean_total.Final = pd.to_numeric(df_mean_total.Final)
            df_mean_total.Tempo = pd.to_numeric(df_mean_total.Tempo)
            df_mean_total.Elimination = pd.to_numeric(df_mean_total.Elimination)
            df_mean_total.Scratch = pd.to_numeric(df_mean_total.Scratch)
            df_mean_total["Sub Total"] = pd.to_numeric(df_mean_total["Sub Total"])
            df_mean_total["Points"] = df_mean_total["Final"]-df_mean_total["Sub Total"]
            df_mean_total=df_mean_total.drop(["Year","Age",'Time','Avg Speed','Lap +','Lap -',"Sprint 1","Sprint 2","Sprint 3","Sprint 4","Sprint 5","Sprint 6","Sprint 7","Sprint 8","Sub Total","Final"],axis=1)
            df_mean_total = df_mean_total.groupby('Name', as_index=False).mean()



            df_mean_points_transpose = pd.DataFrame()
            df_mean_points_transpose["Marker"] = ["Sprint 1","Sprint 2","Sprint 3","Sprint 4","Sprint 5","Sprint 6","Sprint 7","Sprint 8"]
            df_mean_tempo_transpose = pd.DataFrame()
            df_mean_tempo_transpose["Marker"] = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26]
            df_mean_total_transpose = pd.DataFrame()
            df_mean_total_transpose["Marker"] = ["Scratch","Tempo","Elimination","Points"]

            for i in range(len(df_mean_points)):
                var = str(df_mean_points["Name"].iloc[i])
                df_mean_points_transpose[f"{var}"]=df_mean_points.iloc[i][2:10].values
                df_mean_total_transpose[f"{var}"]=df_mean_total.iloc[i][1:5].values
                df_mean_tempo_transpose[f"{var}"]=df_mean_tempo.iloc[i][3:29].values

            ##Points scoring average plot
            fig_point_mean = px.line(df_mean_points_transpose, x="Marker", y = df_mean_points_transpose.columns[1:], title="Points Scoring Average", markers=True)
            st.plotly_chart(fig_point_mean,use_container_width=True)

            ##Tempo scoring average plot

            fig_tempo_mean = px.line(df_mean_tempo_transpose, x="Marker", y = df_mean_tempo_transpose.columns[1:], title="Tempo Scoring Average", markers=True)
            st.plotly_chart(fig_tempo_mean,use_container_width=True)



            ##Overall Averages plot
            fig_overall_mean = px.line(df_mean_total_transpose, x="Marker", y = df_mean_total_transpose.columns[1:], title="Overall Averages", markers=True)
            st.plotly_chart(fig_overall_mean,use_container_width=True)
            
    if race_type=="Men's Madison":
        st.header('Men\'s Madison')
        st.subheader('All results')
        all_sprints=["Sprint 1","Sprint 2","Sprint 3","Sprint 4","Sprint 5","Sprint 6","Sprint 7","Sprint 8","Sprint 9","Sprint 10","Sprint 11","Sprint 12","Sprint 13","Sprint 14","Sprint 15","Sprint 16","Sprint 17","Sprint 18","Sprint 19","Sprint 20"]
        @st.cache_data
        def get_data_from_excel():
            df = pd.read_excel(
                io='pages/MensRaceResults.xlsm',
                engine ='openpyxl',
                sheet_name='Madison',
                skiprows=0,
                usecols='A:AK',
                nrows=2000
                )
            df = df.replace(',','')
            return df
        df= get_data_from_excel()
        @st.cache_data
        def convert_to_csv(df):
            return df.to_csv(index=False,sep = ",").encode('utf-32')
        format_dict = { 'Date': '{:%d-%m-%y}', 'Age1': '{0:,.2f}', 'Age2': '{0:,.2f}', 'Avg Speed': '{0:,.3f}'}
        def color_points(val):
            if val == 5:
                background_color = 'darkgoldenrod'    
                return 'background-color: %s' % background_color
            elif val == 3:
                background_color = 'Silver'    
                return 'background-color: %s' % background_color 
            elif val == 2:
                background_color = 'Coral'    
                return 'background-color: %s' % background_color
            elif val == 1:
                background_color = 'darkcyan'    
                return 'background-color: %s' % background_color 
            else:
                background_color = ''    
                return 'background-color: %s' % background_color  
        def color_points_10(val):
            if val == 10:
                background_color = 'darkgoldenrod'    
                return 'background-color: %s' % background_color
            elif val == 6:
                background_color = 'Silver'    
                return 'background-color: %s' % background_color 
            elif val == 4:
                background_color = 'Coral'    
                return 'background-color: %s' % background_color
            elif val == 2:
                background_color = 'darkcyan'    
                return 'background-color: %s' % background_color 
            else:
                background_color = ''    
                return 'background-color: %s' % background_color
        def color_plus_laps(val):
            if val >19:
                background_color = 'green'    
                return 'background-color: %s' % background_color
            else:
                background_color = ''    
                return 'background-color: %s' % background_color 
        def color_minus_laps(val):
            if val > 19:
                background_color = 'red'    
                return 'background-color: %s' % background_color
            else:
                background_color = ''    
                return 'background-color: %s' % background_color 

        c1,c2,c3=st.columns(3)
        with c1:
            df_orig = df

            year = st.multiselect(
                "Select Year:",
                options=df["Year"].unique(),
                default=df["Year"].unique()[0]
            )    
        if year:
            df = df.query(
                "Year == @year"
                )
        else:
            df=df_orig

        with c2:
            location = st.multiselect(
                "Select Location:",
                options=df["Location"].unique(),
                default=df["Location"].unique()[0]
            )

        if location:
            df = df.query(
                "Location == @location"
                )
        else:
            df=df_orig
        with c3:
            event = st.multiselect(
                "Select Event Type:",
                options=df["Event"].unique(),
                default=df["Event"].unique()[0]
            )

        if event:
            df = df.query(
                "Event == @event"
                )
        else:
            df=df_orig

        df_styled = (df
                            .style
                            .applymap(color_points, subset=pd.IndexSlice[:, ["Sprint 1","Sprint 2","Sprint 3","Sprint 4","Sprint 5","Sprint 6","Sprint 7","Sprint 8","Sprint 9","Sprint 10","Sprint 11","Sprint 12","Sprint 13","Sprint 14","Sprint 15","Sprint 16","Sprint 17","Sprint 18","Sprint 19"]])
                            .applymap(color_points_10, subset=pd.IndexSlice[:, ["Sprint 20"]])
                            .applymap(color_plus_laps, subset=pd.IndexSlice[:, ["P.Laps"]])
                            .applymap(color_minus_laps, subset=pd.IndexSlice[:, ["M.Laps"]])
                            .format(format_dict))
        st.dataframe(df_styled,use_container_width=True)
        ##Download buttons
        csv = convert_to_csv(df)
        download1 = st.download_button(
            label="Download Madison Data as CSV",
            data=csv,
            file_name='Madison_Data.csv',
            mime='text/csv',
            key="mad1"
        )
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='Sheet1', index=False)
            writer.save()
            download2 = st.download_button(
                label="Download Madison Data as Excel",
                data=buffer,
                file_name='Madison_Data.xlsx',
                mime='application/vnd.ms-excel',
            key="mad2"
            )
        ##Download buttons complete
        st.markdown("---")

        st.title(":bicyclist: Event History")

        countries = df_orig['Country'].drop_duplicates().sort_values()
        country = st.multiselect("Select Country(s):", countries)
        if len(country)>0:
            df_countryHistory = df_orig.query(
                "Country == @country"
            )

            ## Totals by Date -- DB and plot
            df_countryHistory = df_countryHistory.sort_values("Date", ascending=False)
            df_countryHistory_styled = (df_countryHistory
                                .style
                                .applymap(color_points, subset=pd.IndexSlice[:, ["Sprint 1","Sprint 2","Sprint 3","Sprint 4","Sprint 5","Sprint 6","Sprint 7","Sprint 8","Sprint 9","Sprint 10","Sprint 11","Sprint 12","Sprint 13","Sprint 14","Sprint 15","Sprint 16","Sprint 17","Sprint 18","Sprint 19"]])
                                .applymap(color_points_10, subset=pd.IndexSlice[:, ["Sprint 20"]])
                                .applymap(color_plus_laps, subset=pd.IndexSlice[:, ["P.Laps"]])
                                .applymap(color_minus_laps, subset=pd.IndexSlice[:, ["M.Laps"]])
                                .format(format_dict))
            st.dataframe(df_countryHistory_styled,use_container_width=True)
            ##Download buttons
            csv_ch = convert_to_csv(df_countryHistory)
            download1 = st.download_button(
                label="Download Country History as CSV",
                data=csv_ch,
                file_name='Madison_Country_History.csv',
                mime='text/csv',
                key="madch1"
            )
            buffer_ch = io.BytesIO()
            with pd.ExcelWriter(buffer_ch, engine='xlsxwriter') as writer:
                df_countryHistory.to_excel(writer, sheet_name='Sheet1', index=False)
                writer.save()
                download2 = st.download_button(
                    label="Download Country History as Excel",
                    data=buffer_ch,
                    file_name='Madison_Country_History.xlsx',
                    mime='application/vnd.ms-excel',
                key="madch2"
                )
            ##Download buttons complete
            fig_country_history = px.line(df_countryHistory, x="Date", y = "Total", title = "Totals by Date", markers = "True", color="Country")
            fig_country_history.update_traces(textposition="top right")

            st.plotly_chart(fig_country_history,use_container_width=True)


            ##All races summary
            df_ch_trans,df_ch_worm = pd.DataFrame(),pd.DataFrame()
            df_ch_trans["Sprints"],df_ch_worm["Sprints"] = all_sprints,all_sprints

            for i in range(len(df_countryHistory)):
                var = str(i+1)+" "+str(df_countryHistory["Country"].iloc[i])+" "+str(df_countryHistory["Location"].iloc[i])+" " +str(df_countryHistory["Event"].iloc[i])+" "+str(df_countryHistory["Stage"].iloc[i])+" " +str(df_countryHistory["Year"].iloc[i])
                df_ch_trans[f"{var}"]=df_countryHistory.iloc[i][12:32].values
                df_ch_worm[f"{var}"]=df_countryHistory.iloc[i][12:32].values.cumsum()

            fig_event_mean = px.line(df_ch_trans, x="Sprints", y = df_ch_trans.columns[1:], title="All races Summary", markers=True)
            st.plotly_chart(fig_event_mean,use_container_width=True)

            ##All races Worm
            fig_worm = px.line(df_ch_worm, x="Sprints", y = df_ch_worm.columns, title="The Worm", markers=True)
            st.plotly_chart(fig_worm,use_container_width=True)

            ##The Ranges
            fig_ranges = px.line(df_countryHistory, x=df_ch_worm.columns[1:], y = ["Sprint 1","Sprint 2","Sprint 3","Sprint 4","Sprint 5","Sprint 6","Sprint 7","Sprint 8","Sprint 9","Sprint 10","Sprint 11","Sprint 12","Sprint 13","Sprint 14","Sprint 15","Sprint 16","Sprint 17","Sprint 18","Sprint 19","Sprint 20"], title="The Ranges")

            st.plotly_chart(fig_ranges,use_container_width=True)

            ## Ranks by Date -- DB and plot
            fig_country_history = px.line(df_countryHistory, x="Date", y = "Rank", title = "Rank by Date", markers=True, color="Country")
            #fig_country_history.update_traces(textposition="top right")

            st.plotly_chart(fig_country_history,use_container_width=True)

            ## Laps taken by date -- DB and plot
            fig_country_history = px.line(df_countryHistory, x="Date", y = "P.Laps", title = "Laps Taken by Date", markers = "True", color="Country")
            st.plotly_chart(fig_country_history,use_container_width=True)

            ## Laps lost by date -- DB and plot
            fig_country_history = px.line(df_countryHistory, x="Date", y = "M.Laps", title = "Laps Lost by Date", markers = "True", color="Country")
            st.plotly_chart(fig_country_history,use_container_width=True)




        st.markdown("---")

        st.title(":mag_right: Race Analysis Tool")
        uniqueYear = df_orig['Year'].drop_duplicates().sort_values(ascending=False)


        left_column, middle_column, right_column = st.columns(3)
        with left_column:
            an_year = st.selectbox("Select Year:", uniqueYear)

        df_an_year = df_orig.query(
            "Year == @an_year"
        )
        uniqueLocation = df_an_year['Location'].drop_duplicates().sort_values()

        with middle_column:
            an_location = st.selectbox("Select Location:", uniqueLocation)

        df_an_year_location = df_an_year.query(
            "Year == @an_year & Location == @an_location"
        )

        uniqueEvent = df_an_year_location['Event'].drop_duplicates().sort_values()
        with right_column:
            an_event = st.selectbox("Select Event:", uniqueEvent)

        df_an = df_an_year_location.query(
            "Year == @an_year & Location == @an_location & Event == @an_event"
        )

        st.dataframe(df_an,use_container_width=True)

        ### Splits dataframe and plot

        df_splits = pd.DataFrame()
        df_splits["Marker"] = ["Sprint 1","Sprint 2","Sprint 3","Sprint 4","Sprint 5","Sprint 6","Sprint 7","Sprint 8","Sprint 9","Sprint 10","Sprint 11","Sprint 12","Sprint 13","Sprint 14","Sprint 15","Sprint 16","Sprint 17","Sprint 18","Sprint 19","Sprint 20"]
        for i in range(len(df_an)):
            var = str(df_an["Country"].iloc[i])
            df_splits[f"{var}"]=df_an.iloc[i][12:32].values



        fig_event = px.line(df_splits, x="Marker", y = df_splits.columns, title="Splits", markers=True)

        st.plotly_chart(fig_event,use_container_width=True)

        ### Worm dataframe and plot
        st.write("Running Time")
        df_worm = pd.DataFrame()
        df_worm["Marker"] = ["Sprint 1","Sprint 2","Sprint 3","Sprint 4","Sprint 5","Sprint 6","Sprint 7","Sprint 8","Sprint 9","Sprint 10","Sprint 11","Sprint 12","Sprint 13","Sprint 14","Sprint 15","Sprint 16","Sprint 17","Sprint 18","Sprint 19","Sprint 20"]
        for i in range(len(df_an)):
            var = str(df_an["Country"].iloc[i])
            df_worm[f"{var}"]=df_an.iloc[i][12:32].values.cumsum()


        fig_worm = px.line(df_worm, x="Marker", y = df_worm.columns, title="The Worm")

        st.plotly_chart(fig_worm,use_container_width=True)


        ###Markers Dataframe and plot

        fig_event = px.line(df_an, y=["Sprint 1","Sprint 2","Sprint 3","Sprint 4","Sprint 5","Sprint 6","Sprint 7","Sprint 8","Sprint 9","Sprint 10","Sprint 11","Sprint 12","Sprint 13","Sprint 14","Sprint 15","Sprint 16","Sprint 17","Sprint 18","Sprint 19","Sprint 20"], x = "Country", title="The Ranges", markers=True)
        #fig_event.update_layout(legend_title="legend")
        st.plotly_chart(fig_event,use_container_width=True)

        ##
        st.markdown("---")
        st.header(":chart: Historical Averages")
        df_mean = df_orig.groupby('Country', as_index=False).mean()

        st.write("Points Average")
        df_splits_mean = pd.DataFrame()
        df_splits_mean["Marker"] = ["Sprint 1","Sprint 2","Sprint 3","Sprint 4","Sprint 5","Sprint 6","Sprint 7","Sprint 8","Sprint 9","Sprint 10","Sprint 11","Sprint 12","Sprint 13","Sprint 14","Sprint 15","Sprint 16","Sprint 17","Sprint 18","Sprint 19","Sprint 20"]
        for i in range(len(df_mean)):
            var = str(df_mean["Country"].iloc[i])
            df_splits_mean[f"{var}"]=df_mean.iloc[i][4:24].values

        st.dataframe(df_splits_mean,use_container_width=True)

        fig_event_mean = px.line(df_splits_mean, x="Marker", y = df_splits.columns, title="Points Scoring Average", markers=True)

        st.plotly_chart(fig_event_mean,use_container_width=True)
        df_mean_total = df_orig[df_orig.Total != "DNF"]
        df_mean_total = df_mean_total.groupby('Country', as_index=False)["Total"].mean()


        fig_total_mean = px.bar(df_mean_total, x="Country", y = "Total", title="Total Scoring Average")
        st.plotly_chart(fig_total_mean,use_container_width=True)
        
    if race_type=="Women's Madison":
        st.header('Women\'s Madison')
        st.subheader('All results')
        all_sprints=["Sprint 1","Sprint 2","Sprint 3","Sprint 4","Sprint 5","Sprint 6","Sprint 7","Sprint 8","Sprint 9","Sprint 10","Sprint 11","Sprint 12"]
        @st.cache_data
        def get_data_from_excel():
            df = pd.read_excel(
                io='pages/WomensRaceResults.xlsm',
                engine ='openpyxl',
                sheet_name='Madison',
                skiprows=0,
                usecols='A:AA',
                nrows=2000
                )
            df = df.replace(',','')
            return df
        df= get_data_from_excel()
        @st.cache_data
        def convert_to_csv(df):
            return df.to_csv(index=False,sep = ",").encode('utf-32')
        format_dict = { 'Date': '{:%d-%m-%y}', 'Age1': '{0:,.2f}', 'Age2': '{0:,.2f}', 'Avg Speed': '{0:,.3f}'}
        def color_points(val):
            if val == 5:
                background_color = 'darkgoldenrod'    
                return 'background-color: %s' % background_color
            elif val == 3:
                background_color = 'Silver'    
                return 'background-color: %s' % background_color 
            elif val == 2:
                background_color = 'Coral'    
                return 'background-color: %s' % background_color
            elif val == 1:
                background_color = 'darkcyan'    
                return 'background-color: %s' % background_color 
            else:
                background_color = ''    
                return 'background-color: %s' % background_color  
        def color_points_10(val):
            if val == 10:
                background_color = 'darkgoldenrod'    
                return 'background-color: %s' % background_color
            elif val == 6:
                background_color = 'Silver'    
                return 'background-color: %s' % background_color 
            elif val == 4:
                background_color = 'Coral'    
                return 'background-color: %s' % background_color
            elif val == 2:
                background_color = 'darkcyan'    
                return 'background-color: %s' % background_color 
            else:
                background_color = ''    
                return 'background-color: %s' % background_color
        def color_plus_laps(val):
            if val >19:
                background_color = 'green'    
                return 'background-color: %s' % background_color
            else:
                background_color = ''    
                return 'background-color: %s' % background_color 
        def color_minus_laps(val):
            if val > 19:
                background_color = 'red'    
                return 'background-color: %s' % background_color
            else:
                background_color = ''    
                return 'background-color: %s' % background_color 

        c1,c2,c3=st.columns(3)
        with c1:
            df_orig = df

            year = st.multiselect(
                "Select Year:",
                options=df["Year"].unique(),
                default=df["Year"].unique()[0]
            )    
        if year:
            df = df.query(
                "Year == @year"
                )
        else:
            df=df_orig

        with c2:
            location = st.multiselect(
                "Select Location:",
                options=df["Location"].unique(),
                default=df["Location"].unique()[0]
            )

        if location:
            df = df.query(
                "Location == @location"
                )
        else:
            df=df_orig
        with c3:
            event = st.multiselect(
                "Select Event Type:",
                options=df["Event"].unique(),
                default=df["Event"].unique()[0]
            )

        if event:
            df = df.query(
                "Event == @event"
                )
        else:
            df=df_orig

        df_styled = (df
                            .style
                            .applymap(color_points, subset=pd.IndexSlice[:, ["Sprint 1","Sprint 2","Sprint 3","Sprint 4","Sprint 5","Sprint 6","Sprint 7","Sprint 8","Sprint 9","Sprint 10","Sprint 11"]])
                            .applymap(color_points_10, subset=pd.IndexSlice[:, ["Sprint 12"]])
                            .applymap(color_plus_laps, subset=pd.IndexSlice[:, ["P.Laps"]])
                            .applymap(color_minus_laps, subset=pd.IndexSlice[:, ["M.Laps"]])
                            .format(format_dict))
        st.dataframe(df_styled,use_container_width=True)
        ##Download buttons
        csv = convert_to_csv(df)
        download1 = st.download_button(
            label="Download Madison Data as CSV",
            data=csv,
            file_name='Madison_Data.csv',
            mime='text/csv',
            key="mad1"
        )
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='Sheet1', index=False)
            writer.save()
            download2 = st.download_button(
                label="Download Madison Data as Excel",
                data=buffer,
                file_name='Madison_Data.xlsx',
                mime='application/vnd.ms-excel',
            key="mad2"
            )
        ##Download buttons complete
        st.markdown("---")

        st.title(":bicyclist: Event History")

        countries = df_orig['Country'].drop_duplicates().sort_values()
        country = st.multiselect("Select Country(s):", countries)
        if len(country)>0:
            df_countryHistory = df_orig.query(
                "Country == @country"
            )

            ## Totals by Date -- DB and plot
            df_countryHistory = df_countryHistory.sort_values("Date", ascending=False)
            df_countryHistory_styled = (df_countryHistory
                                .style
                                .applymap(color_points, subset=pd.IndexSlice[:, ["Sprint 1","Sprint 2","Sprint 3","Sprint 4","Sprint 5","Sprint 6","Sprint 7","Sprint 8","Sprint 9","Sprint 10","Sprint 11"]])
                                .applymap(color_points_10, subset=pd.IndexSlice[:, ["Sprint 12"]])
                                .applymap(color_plus_laps, subset=pd.IndexSlice[:, ["P.Laps"]])
                                .applymap(color_minus_laps, subset=pd.IndexSlice[:, ["M.Laps"]])
                                .format(format_dict))
            st.dataframe(df_countryHistory_styled,use_container_width=True)
            ##Download buttons
            csv_ch = convert_to_csv(df_countryHistory)
            download1 = st.download_button(
                label="Download Country History as CSV",
                data=csv_ch,
                file_name='Madison_Country_History.csv',
                mime='text/csv',
                key="madch1"
            )
            buffer_ch = io.BytesIO()
            with pd.ExcelWriter(buffer_ch, engine='xlsxwriter') as writer:
                df_countryHistory.to_excel(writer, sheet_name='Sheet1', index=False)
                writer.save()
                download2 = st.download_button(
                    label="Download Country History as Excel",
                    data=buffer_ch,
                    file_name='Madison_Country_History.xlsx',
                    mime='application/vnd.ms-excel',
                key="madch2"
                )
            ##Download buttons complete
            fig_country_history = px.line(df_countryHistory, x="Date", y = "Total", title = "Totals by Date", markers = "True", color="Country")
            fig_country_history.update_traces(textposition="top right")

            st.plotly_chart(fig_country_history,use_container_width=True)


            ##All races summary
            df_ch_trans,df_ch_worm = pd.DataFrame(),pd.DataFrame()
            df_ch_trans["Sprints"],df_ch_worm["Sprints"] = all_sprints,all_sprints

            for i in range(len(df_countryHistory)):
                var = str(i+1)+" "+str(df_countryHistory["Country"].iloc[i])+" "+str(df_countryHistory["Location"].iloc[i])+" " +str(df_countryHistory["Event"].iloc[i])+" "+str(df_countryHistory["Stage"].iloc[i])+" " +str(df_countryHistory["Year"].iloc[i])
                df_ch_trans[f"{var}"]=df_countryHistory.iloc[i][10:22].values
                df_ch_worm[f"{var}"]=df_countryHistory.iloc[i][10:22].values.cumsum()

            fig_event_mean = px.line(df_ch_trans, x="Sprints", y = df_ch_trans.columns[1:], title="All races Summary", markers=True)
            st.plotly_chart(fig_event_mean,use_container_width=True)

            ##All races Worm
            fig_worm = px.line(df_ch_worm, x="Sprints", y = df_ch_worm.columns, title="The Worm", markers=True)
            st.plotly_chart(fig_worm,use_container_width=True)

            ##The Ranges
            fig_ranges = px.line(df_countryHistory, x=df_ch_worm.columns[1:], y = ["Sprint 1","Sprint 2","Sprint 3","Sprint 4","Sprint 5","Sprint 6","Sprint 7","Sprint 8","Sprint 9","Sprint 10","Sprint 11","Sprint 12"], title="The Ranges", markers=True)

            st.plotly_chart(fig_ranges,use_container_width=True)

            ## Ranks by Date -- DB and plot
            fig_country_history = px.line(df_countryHistory, x="Date", y = "Rank", title = "Rank by Date", markers = "True", color="Country")
            #fig_country_history.update_traces(textposition="top right")

            st.plotly_chart(fig_country_history,use_container_width=True)

            ## Laps taken by date -- DB and plot
            fig_country_history = px.line(df_countryHistory, x="Date", y = "P.Laps", title = "Laps Taken by Date", markers = "True", color="Country")
            st.plotly_chart(fig_country_history,use_container_width=True)

            ## Laps lost by date -- DB and plot
            fig_country_history = px.line(df_countryHistory, x="Date", y = "M.Laps", title = "Laps Lost by Date", markers = "True", color="Country")
            st.plotly_chart(fig_country_history,use_container_width=True)




        st.markdown("---")

        st.title(":mag_right: Race Analysis Tool")
        uniqueYear = df_orig['Year'].drop_duplicates().sort_values(ascending=False)


        left_column, middle_column, right_column = st.columns(3)
        with left_column:
            an_year = st.selectbox("Select Year:", uniqueYear)

        df_an_year = df_orig.query(
            "Year == @an_year"
        )
        uniqueLocation = df_an_year['Location'].drop_duplicates().sort_values()

        with middle_column:
            an_location = st.selectbox("Select Location:", uniqueLocation)

        df_an_year_location = df_an_year.query(
            "Year == @an_year & Location == @an_location"
        )

        uniqueEvent = df_an_year_location['Event'].drop_duplicates().sort_values()
        with right_column:
            an_event = st.selectbox("Select Event:", uniqueEvent)

        df_an = df_an_year_location.query(
            "Year == @an_year & Location == @an_location & Event == @an_event"
        )

        st.dataframe(df_an,use_container_width=True)

        ### Splits dataframe and plot

        df_splits = pd.DataFrame()
        df_splits["Marker"] = ["Sprint 1","Sprint 2","Sprint 3","Sprint 4","Sprint 5","Sprint 6","Sprint 7","Sprint 8","Sprint 9","Sprint 10","Sprint 11","Sprint 12"]
        for i in range(len(df_an)):
            var = str(df_an["Country"].iloc[i])
            df_splits[f"{var}"]=df_an.iloc[i][10:22].values



        fig_event = px.line(df_splits, x="Marker", y = df_splits.columns, title="Splits", markers=True)

        st.plotly_chart(fig_event,use_container_width=True)

        ### Worm dataframe and plot
        st.write("Running Time")
        df_worm = pd.DataFrame()
        df_worm["Marker"] = ["Sprint 1","Sprint 2","Sprint 3","Sprint 4","Sprint 5","Sprint 6","Sprint 7","Sprint 8","Sprint 9","Sprint 10","Sprint 11","Sprint 12"]
        for i in range(len(df_an)):
            var = str(df_an["Country"].iloc[i])
            df_worm[f"{var}"]=df_an.iloc[i][10:22].values.cumsum()


        fig_worm = px.line(df_worm, x="Marker", y = df_worm.columns, title="The Worm")

        st.plotly_chart(fig_worm,use_container_width=True)


        ###Markers Dataframe and plot

        fig_event = px.line(df_an, y=["Sprint 1","Sprint 2","Sprint 3","Sprint 4","Sprint 5","Sprint 6","Sprint 7","Sprint 8","Sprint 9","Sprint 10","Sprint 11","Sprint 12"], x = "Country", title="The Ranges", markers=True)
        #fig_event.update_layout(legend_title="legend")
        st.plotly_chart(fig_event,use_container_width=True)

        ##
        st.markdown("---")
        st.header(":chart: Historical Averages")
        df_mean = df_orig.groupby('Country', as_index=False).mean()

        st.write("Points Average")
        df_splits_mean = pd.DataFrame()
        df_splits_mean["Marker"] = ["Sprint 1","Sprint 2","Sprint 3","Sprint 4","Sprint 5","Sprint 6","Sprint 7","Sprint 8","Sprint 9","Sprint 10","Sprint 11","Sprint 12"]
        for i in range(len(df_mean)):
            var = str(df_mean["Country"].iloc[i])
            df_splits_mean[f"{var}"]=df_mean.iloc[i][2:14].values

        st.dataframe(df_splits_mean,use_container_width=True)

        fig_event_mean = px.line(df_splits_mean, x="Marker", y = df_splits.columns, title="Points Scoring Average", markers=True)

        st.plotly_chart(fig_event_mean,use_container_width=True)
        df_mean_total = df_orig[df_orig.Total != "DNF"]
        df_mean_total = df_mean_total.groupby('Country', as_index=False)["Total"].mean()


        fig_total_mean = px.bar(df_mean_total, x="Country", y = "Total", title="Total Scoring Average")
        st.plotly_chart(fig_total_mean,use_container_width=True)
        
        
    if race_type=="Men's 1k Time Trial":
        st.header('Men\'s 1k Time Trial')
        st.subheader('All results')
        marker=["125m","250m","375m","500m","625m","750m","875m","1000m"]
        @st.cache_data
        def get_data_from_excel():
            df = pd.read_excel(
                io='pages/MensRaceResults.xlsm',
                engine ='openpyxl',
                sheet_name='1k TT',
                skiprows=0,
                usecols='A:S',
                nrows=1000
                )
            df = df.replace(',','')
            return df
        df= get_data_from_excel()
        @st.cache_data
        def convert_to_csv(df):
            return df.to_csv(index=False,sep = ",").encode('utf-32')
        c1,c2,c3=st.columns(3)
        df_orig = df
        with c1:
            year = st.multiselect(
                "Select Year:",
                options=df["Year"].unique(),
                default=df["Year"].unique()[0]
            )    
        if year:
            df = df.query(
                "Year == @year"
                )
        else:
            df=df_orig


        with c2:
            location = st.multiselect(
                "Select Location:",
                options=df["Location"].unique(),
                default=df["Location"].unique()[0]
            )

        if location:
            df = df.query(
                "Location == @location"
                )
        else:
            df=df_orig
        with c3:
            event = st.multiselect(
                "Select Event Type:",
                options=df["Event"].unique(),
                default=df["Event"].unique()[0]
            )

        if event:
            df = df.query(
                "Event == @event"
                )
        else:
            df=df_orig


        st.dataframe(df,use_container_width=True)
        ##Download buttons
        csv = convert_to_csv(df)
        download1 = st.download_button(
            label="Download Time Trial Data as CSV",
            data=csv,
            file_name='TT_Data.csv',
            mime='text/csv',
            key="tt1"
        )
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='Sheet1', index=False)
            writer.save()
            download2 = st.download_button(
                label="Download Time Trial Data as Excel",
                data=buffer,
                file_name='TT_Data.xlsx',
                mime='application/vnd.ms-excel',
            key="tt2"
            )
        ##Download buttons complete
        st.markdown("---")

        st.title(":bar_chart: Top Ten Performances")

        df_topten = df_orig.sort_values('Time').head(10)

        st.dataframe(df_topten,use_container_width=True)

        ##Download buttons
        csvtt = convert_to_csv(df_topten)
        download1 = st.download_button(
            label="Download Top Ten Data as CSV",
            data=csvtt,
            file_name='TT_Data.csv',
            mime='text/csv',
            key="tttt1"
        )
        buffertt = io.BytesIO()
        with pd.ExcelWriter(buffertt, engine='xlsxwriter') as writer:
            df_topten.to_excel(writer, sheet_name='Sheet1', index=False)
            writer.save()
            download2 = st.download_button(
                label="Download Top Ten Data as Excel",
                data=buffertt,
                file_name='TT_Data.xlsx',
                mime='application/vnd.ms-excel',
            key="tttt2"
            )
        ##Download buttons complete

        df_splits_tt = pd.DataFrame()
        df_splits_tt["Marker"] = marker
        for i in range(len(df_topten)):
            var = str(i+1)+" "+str(df_topten["Country"].iloc[i]) + " " + str(df_topten["Year"].iloc[i]) + " " +str(df_topten["Location"].iloc[i])+" " +str(df_topten["Event"].iloc[i]) + " " +str(df_topten["Stage"].iloc[i])
            df_splits_tt[f"{var}"]=df_topten.iloc[i][9:17].values


        fig_tt = px.line(df_splits_tt, x="Marker", y = df_splits_tt.columns, title="Top Ten")

        st.plotly_chart(fig_tt, use_container_width=True)

        st.markdown("---")

        st.title(":bicyclist: Athlete History")

        athletes = df_orig['Athlete'].drop_duplicates().sort_values()
        athlete = st.multiselect("Select Athlete(s):", athletes)
        if len(athlete)>0:
            df_athleteHistory = df_orig.query(
                "Athlete == @athlete"
            )

            st.dataframe(df_athleteHistory,use_container_width=True)
            ##Download buttons
            csvah = convert_to_csv(df_athleteHistory)
            download1 = st.download_button(
                label="Download Athlete History as CSV",
                data=csvah,
                file_name='Athlete_History_Data.csv',
                mime='text/csv',
                key="ttah1"
            )
            bufferah = io.BytesIO()
            with pd.ExcelWriter(bufferah, engine='xlsxwriter') as writer:
                df_athleteHistory.to_excel(writer, sheet_name='Sheet1', index=False)
                writer.save()
                download2 = st.download_button(
                    label="Download Athlete History as Excel",
                    data=bufferah,
                    file_name='Athlete_History_Data.xlsx',
                    mime='application/vnd.ms-excel',
                key="ttah2"
                )
            ##Download buttons complete

            df_athleteHistory_sh = df_athleteHistory[(df_athleteHistory.Rank != "DSQ") & (df_athleteHistory.Rank != "DNF")]
            ##First Figure -- All Races
            df_ah_Trans,df_ch_worm = pd.DataFrame(),pd.DataFrame()
            df_ah_Trans["Distance"],df_ch_worm["Distance"] = marker,marker
            for i in range(len(df_athleteHistory_sh)):
                var =str(i+1)+" "+str(df_athleteHistory_sh["Athlete"].iloc[i])+" "+str(df_athleteHistory_sh["Location"].iloc[i])+" "+str(df_athleteHistory_sh["Event"].iloc[i])+" "+str(df_athleteHistory_sh["Stage"].iloc[i])+" "+str(df_athleteHistory_sh["Year"].iloc[i])
                df_ah_Trans[f"{var}"]=df_athleteHistory_sh.iloc[i][9:17].values
                df_ch_worm[f"{var}"]=df_athleteHistory_sh.iloc[i][9:17].values.cumsum()

            fig_event = px.line(df_ah_Trans, x="Distance", y = df_ah_Trans.columns, title="All races", markers=True)
            st.plotly_chart(fig_event,use_container_width=True)
            ##Second Figure -- The Worm

            fig_event_CH = px.line(df_ch_worm, x="Distance", y = df_ch_worm.columns, title="The Worm")
            st.plotly_chart(fig_event_CH, use_container_width=True)

            #Third Figure -- Ranges
            fig_ranges_CH = px.line(df_athleteHistory, x=df_ch_worm.columns[1:], y = marker, title="The Ranges",markers=True)
            st.plotly_chart(fig_ranges_CH, use_container_width=True)

            fig_athlete_history = px.line(df_athleteHistory, x="Date", y = "Time", title = "Times by Date", markers = "True", text = "Location", color="Athlete")
            fig_athlete_history.update_traces(textposition="top right")

            st.plotly_chart(fig_athlete_history,use_container_width=True)

            fig_athlete_history = px.line(df_athleteHistory, x="Date", y = "Rank", title = "Rank by Date", markers = "True", color="Athlete")
            fig_athlete_history.update_traces(textposition="top right")

            st.plotly_chart(fig_athlete_history,use_container_width=True)

            fig_athlete_history = px.line(df_athleteHistory, x="Age", y = "Time", title = "Times by Age", markers = "True", color="Athlete")
            fig_athlete_history.update_traces(textposition="top right")

            st.plotly_chart(fig_athlete_history,use_container_width=True)

            df_athleteHistory["Half"] = df_athleteHistory["125m"]+df_athleteHistory["250m"]+df_athleteHistory["375m"]+df_athleteHistory["500m"]

            fig_athlete_history = px.line(df_athleteHistory, x="Age", y = "Half", title = "500m Times by Age", markers = "True", color="Athlete")


            st.plotly_chart(fig_athlete_history,use_container_width=True)




        st.markdown("---")

        st.title(":mag_right: Race Analysis Tool")
        uniqueYear = df_orig['Year'].drop_duplicates().sort_values(ascending=False)


        left_column, middle_column, right_column,c4 = st.columns(4)
        with left_column:
            an_year = st.selectbox("Select Year:", uniqueYear)

        df_an_year = df_orig.query(
            "Year == @an_year"
        )
        uniqueLocation = df_an_year['Location'].drop_duplicates().sort_values()

        with middle_column:
            an_location = st.selectbox("Select Location:", uniqueLocation)

        df_an_year_location = df_an_year.query(
            "Year == @an_year & Location == @an_location"
        )

        uniqueEvent = df_an_year_location['Event'].drop_duplicates().sort_values()
        with right_column:
            an_event = st.selectbox("Select Event:", uniqueEvent)

        df_an_year_location_event = df_an_year_location.query(
            "Year == @an_year & Location == @an_location & Event == @an_event"
        )

        uniqueStage = df_an_year_location_event['Stage'].drop_duplicates().sort_values()


        with c4:
            an_stage = st.selectbox("Select Stage:", uniqueStage)

        df_an = df_an_year_location_event.query(
            "Year == @an_year & Location == @an_location & Event == @an_event & Stage == @an_stage"
        )

        st.dataframe(df_an,use_container_width=True)
        df_splits = pd.DataFrame()
        df_splits["Marker"] = ["125m","250m","375m","500m","625m","750m","875m","1000m"]
        for i in range(len(df_an)):
            var = str(df_an["Athlete"].iloc[i])
            df_splits[f"{var}"]=df_an.iloc[i][9:17].values

        fig_event = px.line(df_splits, x="Marker", y = df_splits.columns, markers=True, title="Splits")

        st.plotly_chart(fig_event, use_container_width=True)    

        ### Worm dataframe and plot
        # st.write("Running Time")
        df_worm = pd.DataFrame()
        df_worm["Marker"] = ["125m","250m","375m","500m","625m","750m","875m","1000m"]

        for i in range(len(df_an)):
            var = str(df_an["Athlete"].iloc[i])
            df_worm[f"{var}"]=df_an.iloc[i][9:17].values.cumsum()



        fig_event = px.line(df_worm, x="Marker", y = df_worm.columns, markers=True,title="The Worm")

        st.plotly_chart(fig_event,use_container_width=True)




        fig_event = px.line(df_an, y=["125m","250m","375m","500m","625m","750m","875m","1000m"], x = "Athlete", markers=True,title="The Ranges")

        st.plotly_chart(fig_event,use_container_width=True)
        
        
    if race_type=="Women's 500m Time Trial":
        st.header('Women\'s 500m Time Trial')
        st.subheader('All results')
        marker=["125m","250m","375m","500m"]
        @st.cache_data
        def get_data_from_excel():
            df = pd.read_excel(
                io='pages/WomensRaceResults.xlsm',
                engine ='openpyxl',
                sheet_name='500m Time Trial',
                skiprows=0,
                usecols='A:O',
                nrows=2000
                )
            df = df.replace(',','')
            return df
        df= get_data_from_excel()
        @st.cache_data
        def convert_to_csv(df):
            return df.to_csv(index=False,sep = ",").encode('utf-32')
        c1,c2,c3=st.columns(3)
        df_orig = df
        with c1:
            year = st.multiselect(
                "Select Year:",
                options=df["Year"].unique(),
                default=df["Year"].unique()[0]
            )    
        if year:
            df = df.query(
                "Year == @year"
                )
        else:
            df=df_orig


        with c2:
            location = st.multiselect(
                "Select Location:",
                options=df["Location"].unique(),
                default=df["Location"].unique()[0]
            )

        if location:
            df = df.query(
                "Location == @location"
                )
        else:
            df=df_orig
        with c3:
            event = st.multiselect(
                "Select Event Type:",
                options=df["Event"].unique(),
                default=df["Event"].unique()[0]
            )

        if event:
            df = df.query(
                "Event == @event"
                )
        else:
            df=df_orig


        st.dataframe(df,use_container_width=True)
        ##Download buttons
        csv = convert_to_csv(df)
        download1 = st.download_button(
            label="Download Time Trial Data as CSV",
            data=csv,
            file_name='TT_Data.csv',
            mime='text/csv',
            key="tt1"
        )
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='Sheet1', index=False)
            writer.save()
            download2 = st.download_button(
                label="Download Time Trial Data as Excel",
                data=buffer,
                file_name='TT_Data.xlsx',
                mime='application/vnd.ms-excel',
            key="tt2"
            )
        ##Download buttons complete
        st.markdown("---")

        st.title(":bar_chart: Top Ten Performances")

        df_topten = df_orig.sort_values('Time').head(10)

        st.dataframe(df_topten,use_container_width=True)

        ##Download buttons
        csvtt = convert_to_csv(df_topten)
        download1 = st.download_button(
            label="Download Top Ten Data as CSV",
            data=csvtt,
            file_name='TT_Data.csv',
            mime='text/csv',
            key="tttt1"
        )
        buffertt = io.BytesIO()
        with pd.ExcelWriter(buffertt, engine='xlsxwriter') as writer:
            df_topten.to_excel(writer, sheet_name='Sheet1', index=False)
            writer.save()
            download2 = st.download_button(
                label="Download Top Ten Data as Excel",
                data=buffertt,
                file_name='TT_Data.xlsx',
                mime='application/vnd.ms-excel',
            key="tttt2"
            )
        ##Download buttons complete

        df_splits_tt = pd.DataFrame()
        df_splits_tt["Marker"] = marker
        for i in range(len(df_topten)):
            var = str(i+1)+" "+str(df_topten["Athlete"].iloc[i]) + " " + str(df_topten["Year"].iloc[i]) + " " +str(df_topten["Location"].iloc[i])+" " +str(df_topten["Event"].iloc[i]) + " " +str(df_topten["Stage"].iloc[i])
            df_splits_tt[f"{var}"]=df_topten.iloc[i][10:14].values


        fig_tt = px.line(df_splits_tt, x="Marker", y = df_splits_tt.columns, title="Top Ten", markers=True)

        st.plotly_chart(fig_tt, use_container_width=True)

        st.markdown("---")

        st.title(":bicyclist: Athlete History")

        athletes = df_orig['Athlete'].drop_duplicates().sort_values()
        athlete = st.multiselect("Select Athlete(s):", athletes)
        if len(athlete)>0:
            df_athleteHistory = df_orig.query(
                "Athlete == @athlete"
            )

            st.dataframe(df_athleteHistory,use_container_width=True)
            ##Download buttons
            csvah = convert_to_csv(df_athleteHistory)
            download1 = st.download_button(
                label="Download Athlete History as CSV",
                data=csvah,
                file_name='Athlete_History_Data.csv',
                mime='text/csv',
                key="ttah1"
            )
            bufferah = io.BytesIO()
            with pd.ExcelWriter(bufferah, engine='xlsxwriter') as writer:
                df_athleteHistory.to_excel(writer, sheet_name='Sheet1', index=False)
                writer.save()
                download2 = st.download_button(
                    label="Download Athlete History as Excel",
                    data=bufferah,
                    file_name='Athlete_History_Data.xlsx',
                    mime='application/vnd.ms-excel',
                key="ttah2"
                )
            ##Download buttons complete

            df_athleteHistory_sh = df_athleteHistory[(df_athleteHistory.Rank != "DSQ") & (df_athleteHistory.Rank != "DNF")]
            ##First Figure -- All Races
            df_ah_Trans,df_ch_worm = pd.DataFrame(),pd.DataFrame()
            df_ah_Trans["Distance"],df_ch_worm["Distance"] = marker,marker
            for i in range(len(df_athleteHistory_sh)):
                var =str(i+1)+" "+str(df_athleteHistory_sh["Athlete"].iloc[i])+" "+str(df_athleteHistory_sh["Location"].iloc[i])+" "+str(df_athleteHistory_sh["Event"].iloc[i])+" "+str(df_athleteHistory_sh["Stage"].iloc[i])+" "+str(df_athleteHistory_sh["Year"].iloc[i])
                df_ah_Trans[f"{var}"]=df_athleteHistory_sh.iloc[i][10:14].values
                df_ch_worm[f"{var}"]=df_athleteHistory_sh.iloc[i][10:14].values.cumsum()

            fig_event = px.line(df_ah_Trans, x="Distance", y = df_ah_Trans.columns, title="All races", markers=True)
            st.plotly_chart(fig_event,use_container_width=True)
            ##Second Figure -- The Worm

            fig_event_CH = px.line(df_ch_worm, x="Distance", y = df_ch_worm.columns, title="The Worm", markers=True)
            st.plotly_chart(fig_event_CH, use_container_width=True)

            #Third Figure -- Ranges
            fig_ranges_CH = px.line(df_athleteHistory, x=df_ch_worm.columns[1:], y = marker, title="The Ranges",markers=True)
            st.plotly_chart(fig_ranges_CH, use_container_width=True)

            fig_athlete_history = px.line(df_athleteHistory, x="Date", y = "Time", title = "Times by Date", markers = "True", text = "Location", color="Athlete")
            fig_athlete_history.update_traces(textposition="top right")

            st.plotly_chart(fig_athlete_history,use_container_width=True)

            fig_athlete_history = px.line(df_athleteHistory, x="Date", y = "Rank", title = "Rank by Date", markers = "True", color="Athlete")
            fig_athlete_history.update_traces(textposition="top right")

            st.plotly_chart(fig_athlete_history,use_container_width=True)

            fig_athlete_history = px.line(df_athleteHistory, x="Age", y = "Time", title = "Times by Age", markers = "True", color="Athlete")
            fig_athlete_history.update_traces(textposition="top right")

            st.plotly_chart(fig_athlete_history,use_container_width=True)

            df_athleteHistory["Half"] = df_athleteHistory["125m"]+df_athleteHistory["250m"]

            fig_athlete_history = px.line(df_athleteHistory, x="Age", y = "Half", title = "250m Times by Age", markers = "True", color="Athlete")


            st.plotly_chart(fig_athlete_history,use_container_width=True)




        st.markdown("---")

        st.title(":mag_right: Race Analysis Tool")
        uniqueYear = df_orig['Year'].drop_duplicates().sort_values(ascending=False)


        left_column, middle_column, right_column,c4 = st.columns(4)
        with left_column:
            an_year = st.selectbox("Select Year:", uniqueYear)

        df_an_year = df_orig.query(
            "Year == @an_year"
        )
        uniqueLocation = df_an_year['Location'].drop_duplicates().sort_values()

        with middle_column:
            an_location = st.selectbox("Select Location:", uniqueLocation)

        df_an_year_location = df_an_year.query(
            "Year == @an_year & Location == @an_location"
        )

        uniqueEvent = df_an_year_location['Event'].drop_duplicates().sort_values()
        with right_column:
            an_event = st.selectbox("Select Event:", uniqueEvent)

        df_an_year_location_event = df_an_year_location.query(
            "Year == @an_year & Location == @an_location & Event == @an_event"
        )

        uniqueStage = df_an_year_location_event['Stage'].drop_duplicates().sort_values()


        with c4:
            an_stage = st.selectbox("Select Stage:", uniqueStage)

        df_an = df_an_year_location_event.query(
            "Year == @an_year & Location == @an_location & Event == @an_event & Stage == @an_stage"
        )

        st.dataframe(df_an,use_container_width=True)
        df_splits = pd.DataFrame()
        df_splits["Marker"] = ["125m","250m","375m","500m"]
        for i in range(len(df_an)):
            var = str(df_an["Athlete"].iloc[i])
            df_splits[f"{var}"]=df_an.iloc[i][10:14].values

        fig_event = px.line(df_splits, x="Marker", y = df_splits.columns, title="Splits", markers=True)

        st.plotly_chart(fig_event, use_container_width=True)    

        ### Worm dataframe and plot
        # st.write("Running Time")
        df_worm = pd.DataFrame()
        df_worm["Marker"] = ["125m","250m","375m","500m"]

        for i in range(len(df_an)):
            var = str(df_an["Athlete"].iloc[i])
            df_worm[f"{var}"]=df_an.iloc[i][10:14].values.cumsum()



        fig_event = px.line(df_worm, x="Marker", y = df_worm.columns, title="The Worm", markers=True)

        st.plotly_chart(fig_event,use_container_width=True)




        fig_event = px.line(df_an, y=["125m","250m","375m","500m"], x = "Athlete", title="The Ranges", markers=True)

        st.plotly_chart(fig_event,use_container_width=True)

        
        
    if race_type=="Men's Team Pursuit":
        st.header('Men\'s Team Pursuit')
        st.subheader('All results')

        marker = ["125m","250m","375m","500m","625m","750m","875m","1000m","1125m","1250m","1375m","1500m","1625m","1750m","1875m","2000m","2125m","2250m","2375m","2500m","2625m","2750m","2875m","3000m","3125m","3250m","3375m","3500m","3625m","3750m","3875m","4000m"]

        format_dict = {'Date': '{:%d-%m-%y}', 'Age1': '{0:,.2f}', 'Age2': '{0:,.2f}'}
        @st.cache_data
        def get_data_from_excel():
            df = pd.read_excel(
                io='pages/MensRaceResults.xlsm',
                engine ='openpyxl',
                sheet_name='Team Pursuit',
                skiprows=0,
                usecols='A:BC',
                nrows=2000
                )
            df = df.replace(',','', regex=True)
            df.Age1=round(df.Age1,2)
            df.Age2=round(df.Age2,2)
            df.Age3=round(df.Age3,2)
            df.Age4=round(df.Age4,2)
            df["Avg Speed"]=round(df["Avg Speed"],3)


            for i in range(len(df)):
                df["Date"][i] = df["Date"][i].date()

            return df
        df= get_data_from_excel()

        df_orig = df
        c1,c2,c3=st.columns(3)
        with c1:
            year = st.multiselect(
                "Select Year:",
                options=df["Year"].unique(),
                default=df["Year"].unique()[0]
            )    
        if year:
            df = df.query(
                "Year == @year"
                )
        else:
            df=df_orig

        with c2:
            location = st.multiselect(
                "Select Location:",
                options=df["Location"].unique(),
                default=df["Location"].unique()[0]
            )

        if location:
            df = df.query(
                "Location == @location"
                )
        else:
            df=df_orig
        with c3:
            event = st.multiselect(
                "Select Event Type:",
                options=df["Event"].unique(),
                default=df["Event"].unique()[0]
            )

        if event:
            df = df.query(
                "Event == @event"
                )
        else:
            df=df_orig


        st.dataframe(df)



        ##Download buttons
        @st.cache_data
        def convert_to_csv(df):
            return df.to_csv(index=False,sep = ",").encode('utf-32')
        csv = convert_to_csv(df)
        download1 = st.download_button(
            label="Download TP data as CSV",
            data=csv,
            file_name='CNZ_Data.csv',
            mime='text/csv'
        )
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='Sheet1', index=False)
            writer.save()
            download2 = st.download_button(
                label="Download TP data as Excel",
                data=buffer,
                file_name='CNZ_Data.xlsx',
                mime='application/vnd.ms-excel'
            )
        ##Download buttons complete




        st.markdown("---")

        st.title(":bar_chart: Top Ten Performances")

        df_topten = df_orig.sort_values("Time").head(10)

        st.dataframe(df_topten,use_container_width=True)


        #DOWNLOAD BUTTONS
        csv_tt = convert_to_csv(df_topten)
        buffer_tt = io.BytesIO()
        # download button 1 to download dataframe as csv
        downloadtt1 = st.download_button(
            label="Download Top Ten data as CSV",
            data=csv_tt,
            file_name='CNZ_Data.csv',
            mime='text/csv',
            key="DLTT1"
        )

        # download button 2 to download dataframe as xlsx
        with pd.ExcelWriter(buffer_tt, engine='xlsxwriter') as writer:
            # Write each dataframe to a different worksheet.
            df_topten.to_excel(writer, sheet_name='Sheet1', index=False)
            # Close the Pandas Excel writer and output the Excel file to the buffer
            writer.save()

            downloadtt2 = st.download_button(
                label="Download Top Ten data as Excel",
                data=buffer_tt,
                file_name='CNZ_TT_Data.xlsx',
                mime='application/vnd.ms-excel',
                key="DLTT2"
            )

        ##Download buttons complete


        df_splits_tt = pd.DataFrame()
        df_splits_tt["Marker"] = marker
        for i in range(len(df_topten)):
            var = str(i+1)+" " +str(df_topten["Country"].iloc[i]) + " " + str(df_topten["Year"].iloc[i]) + " " +str(df_topten["Location"].iloc[i])+" " +str(df_topten["Event"].iloc[i]) + " " +str(df_topten["Stage"].iloc[i])
            df_splits_tt[f"{var}"]=df_topten.iloc[i][22:54].values


        fig_tt = px.line(df_splits_tt, x="Marker", y = df_splits_tt.columns, title="Top Ten",labels={
                     "value": "Half lap splits (Seconds)"
                    
                 })

        st.plotly_chart(fig_tt, use_container_width=True)

        st.markdown("---")

        st.title(":bicyclist: Country History")

        #FILTERS FOR DATAFRAME

        countries = df_orig['Country'].drop_duplicates().sort_values()
        country = st.multiselect("Select Country:", countries)

        df_countryHistory = df_orig.query(
            "Country == @country"
        )
        if len(country)>0:
            df_countryHistory = df_countryHistory.sort_values("Date")
            df_countryHistory.insert(54,'Final Time',df_countryHistory.iloc[:,22:54].sum(axis=1))
            df_countryHistory=df_countryHistory.reset_index(drop=True)
            st.dataframe(df_countryHistory)

            #DOWNLOAD BUTTONS
            csv_CH = convert_to_csv(df_countryHistory)
            buffer_ch = io.BytesIO()
            # download button 1 to download dataframe as csv
            downloadCH1 = st.download_button(
                label="Download Country History data as CSV",
                data=csv_CH,
                file_name='CNZ_Country_History_Data.csv',
                mime='text/csv',
                key="DLCH1"
            )

            # download button 2 to download dataframe as xlsx
            with pd.ExcelWriter(buffer_ch, engine='xlsxwriter') as writer:
                # Write each dataframe to a different worksheet.
                df_countryHistory.to_excel(writer, sheet_name='Sheet1', index=False)
                # Close the Pandas Excel writer and output the Excel file to the buffer
                writer.save()

                downloadCH2 = st.download_button(
                    label="Download Country History data as Excel",
                    data=buffer_ch,
                    file_name='CNZ_Country_History_Data.xlsx',
                    mime='application/vnd.ms-excel',
                    key="DLCH2"
                )

            ##Download buttons complete


            #FIRST FIGURE -- FINAL TIME PROGRESSION
            df_countryHistoryNN = df_countryHistory.loc[df_countryHistory['Time'].notnull()]
            fig_country_history = px.line(df_countryHistoryNN, x="Date", y = "Final Time", title = "Times by Date",color="Country",markers=True)
            fig_country_history.update_traces(textposition="top right")
            st.plotly_chart(fig_country_history, use_container_width=True)

            #Second Figure -- Splits


            df_splits_CH = pd.DataFrame()
            df_splits_CH["Marker"] = marker
            df_worm_CH = pd.DataFrame()
            df_worm_CH["Marker"] = marker
            for i in range(len(df_countryHistory)):
                var = str(i+1)+" "+str(df_countryHistory["Country"].iloc[i])+" "+str(df_countryHistory["Location"].iloc[i]) + " " + str(df_countryHistory["Year"].iloc[i]) + " " +str(df_countryHistory["Event"].iloc[i]) + " " +str(df_countryHistory["Stage"].iloc[i])
                df_splits_CH[f"{var}"]=df_countryHistory.iloc[i][22:54].values
                df_worm_CH[f"{var}"]=df_countryHistory.iloc[i][22:54].values.cumsum()


            fig_CH = px.line(df_splits_CH, x="Marker", y = df_splits_CH.columns, title="Splits",labels={
                     "value": "Running Time (Seconds)"
                    
                 })
            st.plotly_chart(fig_CH, use_container_width=True)

            #Third Figure - Worm

            fig_event_CH = px.line(df_worm_CH, x="Marker", y = df_worm_CH.columns, title="The Worm",labels={
                     "value": "Half lap splits (Seconds)"
                    
                 })
            st.plotly_chart(fig_event_CH, use_container_width=True)

            #Fourth Figure - Ranges
            fig_ranges_CH = px.line(df_countryHistory, x=df_splits_CH.columns[1:], y = marker, title="The Ranges",markers=True,labels={
                     "value": "Seconds"
                    
                 })
            st.plotly_chart(fig_ranges_CH, use_container_width=True)



        #Race Analaysis Tool
        st.markdown("---")

        st.title(":mag_right: Race Analysis Tool")
        uniqueYear = df_orig['Year'].drop_duplicates().sort_values(ascending=False)


        left_column, middle_column, right_column,fourth_column = st.columns(4)
        with left_column:
            an_year = st.selectbox("Select Year:", uniqueYear)

        df_an_year = df_orig.query(
            "Year == @an_year"
        )
        uniqueLocation = df_an_year['Location'].drop_duplicates().sort_values()

        with middle_column:
            an_location = st.selectbox("Select Location:", uniqueLocation)

        df_an_year_location = df_an_year.query(
            "Year == @an_year & Location == @an_location"
        )

        uniqueEvent = df_an_year_location['Event'].drop_duplicates().sort_values()
        with right_column:
            an_event = st.selectbox("Select Event:", uniqueEvent)

        df_an_year_location_event = df_an_year_location.query(
            "Year == @an_year & Location == @an_location & Event == @an_event"
        )
        with fourth_column:
            uniqueStage = df_an_year_location_event['Stage'].drop_duplicates().sort_values()
            an_stage = st.selectbox("Select Stage:", uniqueStage)

            df_an = df_an_year_location_event.query(
                "Year == @an_year & Location == @an_location & Event == @an_event & Stage == @an_stage"
            )
        st.dataframe(df_an)

        ### Splits dataframe and plot
        df_splits,df_worm = pd.DataFrame(),pd.DataFrame()
        df_splits["Marker"],df_worm["Marker"] = marker,marker
        for i in range(len(df_an)):
            var = str(df_an["Rank"].iloc[i])+" "+str(df_an["Country"].iloc[i])
            df_splits[f"{var}"]=df_an.iloc[i][22:54].values
            df_worm[f"{var}"]=df_an.iloc[i][22:54].values.cumsum()
        fig_event = px.line(df_splits, x="Marker", y = df_splits.columns, markers=True,title="Splits",labels={
                     "value": "Half lap splits (Seconds)"
                    
                 })
        st.plotly_chart(fig_event, use_container_width=True)

        ### The Worm
        fig_event = px.line(df_worm, x="Marker", y = df_worm.columns, title="The Worm",labels={
                     "value": "Running Time (Seconds)"
                    
                 })
        st.plotly_chart(fig_event, use_container_width=True)
        ## use this is you want to color specific lines --> color_discrete_sequence=['red','gray','blue','yellow','white','white','white','white','white','white','white','white','white','white','white','white','white']
        
        
        
        ###The Ranges
        fig_event = px.line(df_an, y=marker, x = "Country", title="The Ranges", labels={
                     "value": "Seconds"
                    
                 },
                            markers=True)
        st.plotly_chart(fig_event, use_container_width=True)

        
    if race_type=="Women's Team Pursuit":
        st.subheader("Women's Team Pursuit")
        st.subheader('All results')

        marker = ["125m","250m","375m","500m","625m","750m","875m","1000m","1125m","1250m","1375m","1500m","1625m","1750m","1875m","2000m","2125m","2250m","2375m","2500m","2625m","2750m","2875m","3000m","3125m","3250m","3375m","3500m","3625m","3750m","3875m","4000m"]

        format_dict = {'Date': '{:%d-%m-%y}', 'Age1': '{0:,.2f}', 'Age2': '{0:,.2f}'}
        @st.cache_data
        def get_data_from_excel():
            df = pd.read_excel(
                io='pages/WomensRaceResults.xlsm',
                engine ='openpyxl',
                sheet_name='Team Pursuit',
                skiprows=0,
                usecols='A:BC',
                nrows=2000
                )
            df = df.replace(',','', regex=True)
            df.Age1=round(df.Age1,2)
            df.Age2=round(df.Age2,2)
            df.Age3=round(df.Age3,2)
            df.Age4=round(df.Age4,2)
            df["Avg Speed"]=round(df["Avg Speed"],3)


            for i in range(len(df)):
                df["Date"][i] = df["Date"][i].date()

            return df
        df= get_data_from_excel()

        df_orig = df
        c1,c2,c3=st.columns(3)
        with c1:
            year = st.multiselect(
                "Select Year:",
                options=df["Year"].unique(),
                default=df["Year"].unique()[0]
            )    
        if year:
            df = df.query(
                "Year == @year"
                )
        else:
            df=df_orig

        with c2:
            location = st.multiselect(
                "Select Location:",
                options=df["Location"].unique(),
                default=df["Location"].unique()[0]
            )

        if location:
            df = df.query(
                "Location == @location"
                )
        else:
            df=df_orig
        with c3:
            event = st.multiselect(
                "Select Event Type:",
                options=df["Event"].unique(),
                default=df["Event"].unique()[0]
            )

        if event:
            df = df.query(
                "Event == @event"
                )
        else:
            df=df_orig


        st.dataframe(df)



        ##Download buttons
        @st.cache_data
        def convert_to_csv(df):
            return df.to_csv(index=False,sep = ",").encode('utf-32')
        csv = convert_to_csv(df)
        download1 = st.download_button(
            label="Download TP data as CSV",
            data=csv,
            file_name='CNZ_Data.csv',
            mime='text/csv'
        )
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='Sheet1', index=False)
            writer.save()
            download2 = st.download_button(
                label="Download TP data as Excel",
                data=buffer,
                file_name='CNZ_Data.xlsx',
                mime='application/vnd.ms-excel'
            )
        ##Download buttons complete




        st.markdown("---")

        st.title(":bar_chart: Top Ten Performances")

        df_topten = df_orig.sort_values("Time").head(10)

        st.dataframe(df_topten,use_container_width=True)


        #DOWNLOAD BUTTONS
        csv_tt = convert_to_csv(df_topten)
        buffer_tt = io.BytesIO()
        # download button 1 to download dataframe as csv
        downloadtt1 = st.download_button(
            label="Download Top Ten data as CSV",
            data=csv_tt,
            file_name='CNZ_Data.csv',
            mime='text/csv',
            key="DLTT1"
        )

        # download button 2 to download dataframe as xlsx
        with pd.ExcelWriter(buffer_tt, engine='xlsxwriter') as writer:
            # Write each dataframe to a different worksheet.
            df_topten.to_excel(writer, sheet_name='Sheet1', index=False)
            # Close the Pandas Excel writer and output the Excel file to the buffer
            writer.save()

            downloadtt2 = st.download_button(
                label="Download Top Ten data as Excel",
                data=buffer_tt,
                file_name='CNZ_TT_Data.xlsx',
                mime='application/vnd.ms-excel',
                key="DLTT2"
            )

        ##Download buttons complete


        df_splits_tt = pd.DataFrame()
        df_splits_tt["Marker"] = marker
        for i in range(len(df_topten)):
            var = str(i+1)+ " " +str(df_topten["Country"].iloc[i]) + " " + str(df_topten["Year"].iloc[i]) + " " +str(df_topten["Location"].iloc[i])+" " +str(df_topten["Event"].iloc[i]) + " " +str(df_topten["Stage"].iloc[i])
            df_splits_tt[f"{var}"]=df_topten.iloc[i][22:54].values


        fig_tt = px.line(df_splits_tt, x="Marker", y = df_splits_tt.columns, title="Top Ten")

        st.plotly_chart(fig_tt, use_container_width=True)

        st.markdown("---")

        st.title(":bicyclist: Country History")

        #FILTERS FOR DATAFRAME

        countries = df_orig['Country'].drop_duplicates().sort_values()
        country = st.multiselect("Select Country:", countries)

        df_countryHistory = df_orig.query(
            "Country == @country"
        )
        if len(country)>0:
#             df_countryHistory = df_countryHistory.sort_values("Date")
#             df_countryHistory.insert(49,'Final Time',df_countryHistory.iloc[:,16:48].sum(axis=1))
#             df_countryHistory=df_countryHistory.reset_index(drop=True)
            st.dataframe(df_countryHistory)

            #DOWNLOAD BUTTONS
            csv_CH = convert_to_csv(df_countryHistory)
            buffer_ch = io.BytesIO()
            # download button 1 to download dataframe as csv
            downloadCH1 = st.download_button(
                label="Download Country History data as CSV",
                data=csv_CH,
                file_name='CNZ_Country_History_Data.csv',
                mime='text/csv',
                key="DLCH1"
            )

            # download button 2 to download dataframe as xlsx
            with pd.ExcelWriter(buffer_ch, engine='xlsxwriter') as writer:
                # Write each dataframe to a different worksheet.
                df_countryHistory.to_excel(writer, sheet_name='Sheet1', index=False)
                # Close the Pandas Excel writer and output the Excel file to the buffer
                writer.save()

                downloadCH2 = st.download_button(
                    label="Download Country History data as Excel",
                    data=buffer_ch,
                    file_name='CNZ_Country_History_Data.xlsx',
                    mime='application/vnd.ms-excel',
                    key="DLCH2"
                )

            ##Download buttons complete


            #FIRST FIGURE -- FINAL TIME PROGRESSION

            fig_country_history = px.line(df_countryHistory, x="Date", y = "Time", title = "Times by Date",color="Country",markers=True)
            fig_country_history.update_traces(textposition="top right")
            st.plotly_chart(fig_country_history, use_container_width=True)

            #Second Figure -- Splits


            df_splits_CH = pd.DataFrame()
            df_splits_CH["Marker"] = marker
            df_worm_CH = pd.DataFrame()
            df_worm_CH["Marker"] = marker
            for i in range(len(df_countryHistory)):
                var = str(i+1)+" "+str(df_countryHistory["Country"].iloc[i])+" "+str(df_countryHistory["Location"].iloc[i]) + " " + str(df_countryHistory["Year"].iloc[i]) + " " +str(df_countryHistory["Event"].iloc[i]) + " " +str(df_countryHistory["Stage"].iloc[i])
                df_splits_CH[f"{var}"]=df_countryHistory.iloc[i][22:54].values
                df_worm_CH[f"{var}"]=df_countryHistory.iloc[i][22:54].values.cumsum()


            fig_CH = px.line(df_splits_CH, x="Marker", y = df_splits_CH.columns, title="Splits")
            st.plotly_chart(fig_CH, use_container_width=True)

            #Third Figure - Worm

            fig_event_CH = px.line(df_worm_CH, x="Marker", y = df_worm_CH.columns, title="The Worm")
            st.plotly_chart(fig_event_CH, use_container_width=True)

            #Fourth Figure - Ranges
            fig_ranges_CH = px.line(df_countryHistory, x=df_splits_CH.columns[1:], y = marker, title="The Ranges",markers=True)
            st.plotly_chart(fig_ranges_CH, use_container_width=True)


        #Race Analaysis Tool
        st.markdown("---")

        st.title(":mag_right: Race Analysis Tool")
        uniqueYear = df_orig['Year'].drop_duplicates().sort_values(ascending=False)


        left_column, middle_column, right_column,fourth_column = st.columns(4)
        with left_column:
            an_year = st.selectbox("Select Year:", uniqueYear)

        df_an_year = df_orig.query(
            "Year == @an_year"
        )
        uniqueLocation = df_an_year['Location'].drop_duplicates().sort_values()

        with middle_column:
            an_location = st.selectbox("Select Location:", uniqueLocation)

        df_an_year_location = df_an_year.query(
            "Year == @an_year & Location == @an_location"
        )

        uniqueEvent = df_an_year_location['Event'].drop_duplicates().sort_values()
        with right_column:
            an_event = st.selectbox("Select Event:", uniqueEvent)

        df_an_year_location_event = df_an_year_location.query(
            "Year == @an_year & Location == @an_location & Event == @an_event"
        )
        with fourth_column:
            uniqueStage = df_an_year_location_event['Stage'].drop_duplicates().sort_values()
            an_stage = st.selectbox("Select Stage:", uniqueStage)

            df_an = df_an_year_location_event.query(
                "Year == @an_year & Location == @an_location & Event == @an_event & Stage == @an_stage"
            )
        st.dataframe(df_an)

        ### Splits dataframe and plot
        df_splits,df_worm = pd.DataFrame(),pd.DataFrame()
        df_splits["Marker"],df_worm["Marker"] = marker,marker
        # df_worm = pd.DataFrame()
        # df_worm["Marker"] = marker
        for i in range(len(df_an)):
            var = str(df_an["Rank"].iloc[i])+" "+str(df_an["Country"].iloc[i])
            df_splits[f"{var}"]=df_an.iloc[i][22:54].values
            df_worm[f"{var}"]=df_an.iloc[i][22:54].values.cumsum()
        fig_event = px.line(df_splits, x="Marker", y = df_splits.columns, title="Splits")
        st.plotly_chart(fig_event, use_container_width=True)

        ### The Worm
        fig_event = px.line(df_worm, x="Marker", y = df_worm.columns, title="The Worm")
        st.plotly_chart(fig_event, use_container_width=True)


        ###The Ranges
        fig_event = px.line(df_an, y=marker, x = df_splits.columns[1:], title="The Ranges", markers=True)
        st.plotly_chart(fig_event, use_container_width=True)

        
        
    if race_type=="Men's Individual Pursuit":
        st.header('Men\'s Individual Pursuit')
        st.subheader('All results')
        marker = ["125m","250m","375m","500m","625m","750m","875m","1000m","1125m","1250m","1375m","1500m","1625m","1750m","1875m","2000m","2125m","2250m","2375m","2500m","2625m","2750m","2875m","3000m","3125m","3250m","3375m","3500m","3625m","3750m","3875m","4000m"]
        markerx = [125,250,375,500,625,750,875,1000,1125,1250,1375,1500,1625,1750,1875,2000,2125,2250,2375,2500,2625,2750,2875,3000,3125,3250,3375,3500,3625,3750,3875,4000]
        @st.cache_data
        def get_data_from_excel():
            df = pd.read_excel(
                io='pages/MensRaceResults.xlsm',
                engine ='openpyxl',
                sheet_name='Individual Pursuit',
                skiprows=0,
                usecols='A:AQ',
                nrows=2500
                )
            df = df.replace(',','', regex=True)
            for i in range(len(df)):
                df["Date"][i] = df["Date"][i].date()
                #if df["125m"][i] != "NULL":
                    #df["125m"][i] = df["125m"][i].strftime("%M:%S.%f")
            return df
        df= get_data_from_excel()
        @st.cache_data
        def convert_to_csv(df):
            return df.to_csv(index=False,sep = ",").encode('utf-32')
        df_orig = df
        c1,c2,c3=st.columns(3)
        with c1:
            year = st.multiselect(
                "Select Year:",
                options=df["Year"].unique(),
                default=df["Year"].unique()[0]
            )    
        if year:
            df = df.query(
                "Year == @year"
                )
        else:
            df=df_orig

        with c2:
            location = st.multiselect(
                "Select Location:",
                options=df["Location"].unique(),
                default=df["Location"].unique()[0]
            )

        if location:
            df = df.query(
                "Location == @location"
                )
        else:
            df=df_orig
        with c3:
            event = st.multiselect(
                "Select Event Type:",
                options=df["Event"].unique(),
                default=df["Event"].unique()[0]
            )

        if event:
            df = df.query(
                "Event == @event"
                )
        else:
            df=df_orig


        st.dataframe(df,use_container_width=True)
        #DOWNLOAD BUTTONS
        csv = convert_to_csv(df)
        buffer = io.BytesIO()
        download1 = st.download_button(
            label="Download IP data as CSV",
            data=csv,
            file_name='IP_Data.csv',
            mime='text/csv',
            key="IP1"
        )
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='Sheet1', index=False)
            writer.save()
            download2 = st.download_button(
                label="Download IP data as Excel",
                data=buffer,
                file_name='IP_Data.xlsx',
                mime='application/vnd.ms-excel',
                key="IP2"
            )

        ##Download buttons complete
        st.markdown("---")

        st.title(":bar_chart: Top Ten Performances")

        df_topten = df_orig.sort_values("Time").head(10)

        st.dataframe(df_topten)
        #DOWNLOAD BUTTONS
        csvtt = convert_to_csv(df_topten)
        buffertt = io.BytesIO()
        download1 = st.download_button(
            label="Download Top Ten as CSV",
            data=csvtt,
            file_name='IP_Top_Ten_Data.csv',
            mime='text/csv',
            key="IPtt1"
        )
        with pd.ExcelWriter(buffertt, engine='xlsxwriter') as writer:
            df_topten.to_excel(writer, sheet_name='Sheet1', index=False)
            writer.save()
            download2 = st.download_button(
                label="Download Top Ten as Excel",
                data=buffertt,
                file_name='IP_Top_Ten_Data.xlsx',
                mime='application/vnd.ms-excel',
                key="IPtt2"
            )

        ##Download buttons complete
        st.markdown("---")

        st.title(":bicyclist: Athlete History")

        #FILTERS FOR DATAFRAME

        athletes = df_orig['Athlete'].drop_duplicates().sort_values()
        athlete = st.multiselect("Select Athlete(s):", athletes)

        df_athleteHistory = df_orig.query(
            "Athlete == @athlete"
        )

        if len(athlete)>0:
            st.dataframe(df_athleteHistory,use_container_width=True)
            #DOWNLOAD BUTTONS
            csvah = convert_to_csv(df_athleteHistory)
            buffertt = io.BytesIO()
            download1 = st.download_button(
                label="Download Athlete History as CSV",
                data=csvah,
                file_name='IP_Athlete_History_Data.csv',
                mime='text/csv',
                key="IPah1"
            )
            with pd.ExcelWriter(buffertt, engine='xlsxwriter') as writer:
                df_athleteHistory.to_excel(writer, sheet_name='Sheet1', index=False)
                writer.save()
                download2 = st.download_button(
                    label="Download Athlete History as Excel",
                    data=buffertt,
                    file_name='IP_Athlete_History_Data.xlsx',
                    mime='application/vnd.ms-excel',
                    key="IPah2"
                )
            ##Download buttons complete

            df_splits_CH = pd.DataFrame()
            df_splits_CH["Marker"] = marker
            df_worm_CH = pd.DataFrame()
            df_worm_CH["Marker"] = marker
            for i in range(len(df_athleteHistory)):
                var = str(i+1)+" "+str(df_athleteHistory["Athlete"].iloc[i])+" "+str(df_athleteHistory["Location"].iloc[i]) + " " + str(df_athleteHistory["Year"].iloc[i]) + " " +str(df_athleteHistory["Event"].iloc[i]) + " " +str(df_athleteHistory["Stage"].iloc[i])
                df_splits_CH[f"{var}"]=df_athleteHistory.iloc[i][9:41].values
                df_worm_CH[f"{var}"]=df_athleteHistory.iloc[i][9:41].values.cumsum()


            fig_CH = px.line(df_splits_CH, x="Marker", y = df_splits_CH.columns, title="Splits")
            st.plotly_chart(fig_CH, use_container_width=True)

            #Third Figure - Worm

            fig_event_CH = px.line(df_worm_CH, x="Marker", y = df_worm_CH.columns, title="The Worm")
            st.plotly_chart(fig_event_CH, use_container_width=True)

            #Fourth Figure - Ranges
            fig_ranges_CH = px.line(df_athleteHistory, x=df_splits_CH.columns[1:], y = markerx, title="The Ranges",markers=True)
            st.plotly_chart(fig_ranges_CH, use_container_width=True)


            #FIRST FIGURE -- FINAL TIME PROGRESSION

            fig_athlete_history = px.line(df_athleteHistory, x="Date", y = "Time", title = "Times by Date", markers = "True", color="Athlete")
            fig_athlete_history.update_traces(textposition="top right")

            st.plotly_chart(fig_athlete_history,use_container_width=True)

            ### Time by Age

            fig_athlete_history = px.line(df_athleteHistory, x="Age", y = "Time", title = "Times by Age", markers = "True", color="Athlete")
            fig_athlete_history.update_traces(textposition="top right")

            st.plotly_chart(fig_athlete_history,use_container_width=True)




        st.markdown("---")

        st.title(":mag_right: Race Analysis Tool")
        uniqueYear = df_orig['Year'].drop_duplicates().sort_values(ascending=False)


        left_column, middle_column, right_column,col4 = st.columns(4)
        with left_column:
            an_year = st.selectbox("Select Year:", uniqueYear)

        df_an_year = df_orig.query(
            "Year == @an_year"
        )
        uniqueLocation = df_an_year['Location'].drop_duplicates().sort_values()

        with middle_column:
            an_location = st.selectbox("Select Location:", uniqueLocation)

        df_an_year_location = df_an_year.query(
            "Year == @an_year & Location == @an_location"
        )

        uniqueEvent = df_an_year_location['Event'].drop_duplicates().sort_values()
        with right_column:
            an_event = st.selectbox("Select Event:", uniqueEvent)

        df_an_year_location_event = df_an_year_location.query(
            "Year == @an_year & Location == @an_location & Event == @an_event"
        )


        with col4:

            uniqueStage = df_an_year_location_event['Stage'].drop_duplicates().sort_values()
            an_stage = st.selectbox("Select Stage:", uniqueStage)

        df_an = df_an_year_location_event.query(
            "Year == @an_year & Location == @an_location & Event == @an_event & Stage == @an_stage"
        )



        ### Splits dataframe and plot
        st.dataframe(df_an)
        df_splits,df_worm = pd.DataFrame(),pd.DataFrame()
        df_splits["Marker"],df_worm["Marker"] = marker,marker
        for i in range(len(df_an)):
            var = str(df_an["Rank"].iloc[i])+ " "+ str(df_an["Athlete"].iloc[i])
            df_splits[f"{var}"]=df_an.iloc[i][9:41].values
            df_worm[f"{var}"]=df_an.iloc[i][9:41].values.cumsum()

        fig_event = px.line(df_splits, x="Marker", y = df_splits.columns, title="Splits")

        st.plotly_chart(fig_event,use_container_width=True)

        ### Worm dataframe and plot
        # st.write("Running Time")
        # df_worm = pd.DataFrame()
        # df_worm["Marker"] = ["125m","250m","375m","500m","625m","750m","875m","1000m","1125m","1250m","1375m","1500m","1625m","1750m","1875m","2000m","2125m","2250m","2375m","2500m","2625m","2750m","2875m","3000m","3125m","3250m","3375m","3500m","3625m","3750m","3875m","4000m"]
        # for i in range(len(df_an)):
        #     var = str(df_an["Athlete"].iloc[i])
        #     df_worm[f"{var}"]=df_an.iloc[i][9:41].values.cumsum()



        fig_event = px.line(df_worm, x="Marker", y = df_worm.columns, title="The Worm")

        st.plotly_chart(fig_event,use_container_width=True)

        fig_event = px.line(df_an, y=[125,250,375,500,625,750,875,1000,1125,1250,1375,1500,1625,1750,1875,2000,2125,2250,2375,2500,2625,2750,2875,3000,3125,3250,3375,3500,3625,3750,3875,4000], x = "Athlete", title="The Ranges", markers=True)

        st.plotly_chart(fig_event,use_container_width=True)

    
    
    if race_type=="Women's Individual Pursuit":
        st.header('Women\'s Individual Pursuit')
        st.subheader('All results')
        marker = ["125m","250m","375m","500m","625m","750m","875m","1000m","1125m","1250m","1375m","1500m","1625m","1750m","1875m","2000m","2125m","2250m","2375m","2500m","2625m","2750m","2875m","3000m"]
        markerx = [125,250,375,500,625,750,875,1000,1125,1250,1375,1500,1625,1750,1875,2000,2125,2250,2375,2500,2625,2750,2875,3000]
        @st.cache_data
        def get_data_from_excel():
            df = pd.read_excel(
                io='pages/WomensRaceResults.xlsm',
                engine ='openpyxl',
                sheet_name='Individual Pursuit',
                skiprows=0,
                usecols='A:AQ',
                nrows=2500
                )
            df = df.replace(',','', regex=True)

            for i in range(len(df)):
                df["Date"][i] = df["Date"][i].date()
                if isinstance(df["Time"][i], datetime.time):
                    df["Time"][i]=df['Time'][i].strftime("%M:%S.%f")[:len(df['Time'][i].strftime("%M:%S.%f"))-3]

            return df
        df= get_data_from_excel()
        @st.cache_data
        def convert_to_csv(df):
            return df.to_csv(index=False,sep = ",").encode('utf-32')
        df_orig = df
        c1,c2,c3=st.columns(3)
        with c1:
            year = st.multiselect(
                "Select Year:",
                options=df["Year"].unique(),
                default=df["Year"].unique()[0]
            )    
        if year:
            df = df.query(
                "Year == @year"
                )
        else:
            df=df_orig

        with c2:
            location = st.multiselect(
                "Select Location:",
                options=df["Location"].unique(),
                default=df["Location"].unique()[0]
            )

        if location:
            df = df.query(
                "Location == @location"
                )
        else:
            df=df_orig
        with c3:
            event = st.multiselect(
                "Select Event Type:",
                options=df["Event"].unique(),
                default=df["Event"].unique()[0]
            )

        if event:
            df = df.query(
                "Event == @event"
                )
        else:
            df=df_orig


        st.dataframe(df,use_container_width=True)

        #DOWNLOAD BUTTONS
        csv = convert_to_csv(df)
        buffer = io.BytesIO()
        download1 = st.download_button(
            label="Download IP data as CSV",
            data=csv,
            file_name='IP_Data.csv',
            mime='text/csv',
            key="IP1"
        )
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='Sheet1', index=False)
            writer.save()
            download2 = st.download_button(
                label="Download IP data as Excel",
                data=buffer,
                file_name='IP_Data.xlsx',
                mime='application/vnd.ms-excel',
                key="IP2"
            )

        ##Download buttons complete
        st.markdown("---")

        st.title(":bar_chart: Top Ten Performances")

        df_topten = df_orig.sort_values("Time").head(10)

        st.dataframe(df_topten)
        #DOWNLOAD BUTTONS
        csvtt = convert_to_csv(df_topten)
        buffertt = io.BytesIO()
        download1 = st.download_button(
            label="Download Top Ten as CSV",
            data=csvtt,
            file_name='IP_Top_Ten_Data.csv',
            mime='text/csv',
            key="IPtt1"
        )
        with pd.ExcelWriter(buffertt, engine='xlsxwriter') as writer:
            df_topten.to_excel(writer, sheet_name='Sheet1', index=False)
            writer.save()
            download2 = st.download_button(
                label="Download Top Ten as Excel",
                data=buffertt,
                file_name='IP_Top_Ten_Data.xlsx',
                mime='application/vnd.ms-excel',
                key="IPtt2"
            )

        ##Download buttons complete

        df_splits_tt = pd.DataFrame()
        df_splits_tt["Marker"] = marker
        for i in range(len(df_topten)):
            var = str(i+1)+" "+str(df_topten["Country"].iloc[i]) + " " + str(df_topten["Year"].iloc[i]) + " " +str(df_topten["Location"].iloc[i])+" " +str(df_topten["Event"].iloc[i]) + " " +str(df_topten["Stage"].iloc[i])
            df_splits_tt[f"{var}"]=df_topten.iloc[i][10:34].values


        fig_tt = px.line(df_splits_tt, x="Marker", y = df_splits_tt.columns, title="Top Ten",markers=False)

        st.plotly_chart(fig_tt, use_container_width=True)
        st.markdown("---")

        st.title(":bicyclist: Athlete History")

        #FILTERS FOR DATAFRAME

        athletes = df_orig['Athlete'].drop_duplicates().sort_values()
        athlete = st.multiselect("Select Athlete(s):", athletes)

        df_athleteHistory = df_orig.query(
            "Athlete == @athlete"
        )

        if len(athlete)>0:
            st.dataframe(df_athleteHistory,use_container_width=True)
            df_athleteHistory['Time']= pd.to_datetime(df_athleteHistory['Time'])

            #DOWNLOAD BUTTONS
            csvah = convert_to_csv(df_athleteHistory)
            buffertt = io.BytesIO()
            download1 = st.download_button(
                label="Download Athlete History as CSV",
                data=csvah,
                file_name='IP_Athlete_History_Data.csv',
                mime='text/csv',
                key="IPah1"
            )
            with pd.ExcelWriter(buffertt, engine='xlsxwriter') as writer:
                df_athleteHistory.to_excel(writer, sheet_name='Sheet1', index=False)
                writer.save()
                download2 = st.download_button(
                    label="Download Athlete History as Excel",
                    data=buffertt,
                    file_name='IP_Athlete_History_Data.xlsx',
                    mime='application/vnd.ms-excel',
                    key="IPah2"
                )
            ##Download buttons complete

            df_splits_CH = pd.DataFrame()
            df_splits_CH["Marker"] = marker
            df_worm_CH = pd.DataFrame()
            df_worm_CH["Marker"] = marker
            for i in range(len(df_athleteHistory)):
                var = str(i+1)+" "+str(df_athleteHistory["Athlete"].iloc[i])+" "+str(df_athleteHistory["Location"].iloc[i]) + " " + str(df_athleteHistory["Year"].iloc[i]) + " " +str(df_athleteHistory["Event"].iloc[i]) + " " +str(df_athleteHistory["Stage"].iloc[i])
                df_splits_CH[f"{var}"]=df_athleteHistory.iloc[i][10:34].values
                df_worm_CH[f"{var}"]=df_athleteHistory.iloc[i][10:34].values.cumsum()


            fig_CH = px.line(df_splits_CH, x="Marker", y = df_splits_CH.columns, title="Splits")
            st.plotly_chart(fig_CH, use_container_width=True)

            #Third Figure - Worm

            fig_event_CH = px.line(df_worm_CH, x="Marker", y = df_worm_CH.columns, title="The Worm")
            st.plotly_chart(fig_event_CH, use_container_width=True)

            #Fourth Figure - Ranges
            fig_ranges_CH = px.line(df_athleteHistory, x=df_splits_CH.columns[1:], y = markerx, title="The Ranges",markers=True)
            st.plotly_chart(fig_ranges_CH, use_container_width=True)


            #FIRST FIGURE -- FINAL TIME PROGRESSION

            fig_athlete_history = px.line(df_athleteHistory, x="Date", y = "Time", title = "Times by Date", markers = "True", color="Athlete")
            fig_athlete_history.update_layout(yaxis_tickformat="%H:%M")
            fig_athlete_history.update_traces(textposition="top right")

            st.plotly_chart(fig_athlete_history,use_container_width=True)

            ### Time by Age

            fig_athlete_history = px.line(df_athleteHistory, x="Age", y = "Time", title = "Times by Age", markers = "True", color="Athlete")
            fig_athlete_history.update_layout(yaxis_tickformat="%H:%M")
            fig_athlete_history.update_traces(textposition="top right")

            st.plotly_chart(fig_athlete_history,use_container_width=True)




        st.markdown("---")

        st.title(":mag_right: Race Analysis Tool")
        uniqueYear = df_orig['Year'].drop_duplicates().sort_values(ascending=False)


        left_column, middle_column, right_column,col4 = st.columns(4)
        with left_column:
            an_year = st.selectbox("Select Year:", uniqueYear)

        df_an_year = df_orig.query(
            "Year == @an_year"
        )
        uniqueLocation = df_an_year['Location'].drop_duplicates().sort_values()

        with middle_column:
            an_location = st.selectbox("Select Location:", uniqueLocation)

        df_an_year_location = df_an_year.query(
            "Year == @an_year & Location == @an_location"
        )

        uniqueEvent = df_an_year_location['Event'].drop_duplicates().sort_values()
        with right_column:
            an_event = st.selectbox("Select Event:", uniqueEvent)

        df_an_year_location_event = df_an_year_location.query(
            "Year == @an_year & Location == @an_location & Event == @an_event"
        )


        with col4:

            uniqueStage = df_an_year_location_event['Stage'].drop_duplicates().sort_values()
            an_stage = st.selectbox("Select Stage:", uniqueStage)

        df_an = df_an_year_location_event.query(
            "Year == @an_year & Location == @an_location & Event == @an_event & Stage == @an_stage"
        )



        ### Splits dataframe and plot
        st.dataframe(df_an)
        df_splits,df_worm = pd.DataFrame(),pd.DataFrame()
        df_splits["Marker"],df_worm["Marker"] = marker,marker
        for i in range(len(df_an)):
            var = str(int(df_an["Rank"].iloc[i]))+ " "+ str(df_an["Athlete"].iloc[i])
            df_splits[f"{var}"]=df_an.iloc[i][10:34].values
            df_worm[f"{var}"]=df_an.iloc[i][10:34].values.cumsum()

        fig_event = px.line(df_splits, x="Marker", y = df_splits.columns, title="Splits")

        st.plotly_chart(fig_event,use_container_width=True)

        ### Worm dataframe and plot
        # st.write("Running Time")
        # df_worm = pd.DataFrame()
        # df_worm["Marker"] = ["125m","250m","375m","500m","625m","750m","875m","1000m","1125m","1250m","1375m","1500m","1625m","1750m","1875m","2000m","2125m","2250m","2375m","2500m","2625m","2750m","2875m","3000m","3125m","3250m","3375m","3500m","3625m","3750m","3875m","4000m"]
        # for i in range(len(df_an)):
        #     var = str(df_an["Athlete"].iloc[i])
        #     df_worm[f"{var}"]=df_an.iloc[i][9:41].values.cumsum()



        fig_event = px.line(df_worm, x="Marker", y = df_worm.columns, title="The Worm")

        st.plotly_chart(fig_event,use_container_width=True)

        fig_event = px.line(df_an, y=[125,250,375,500,625,750,875,1000,1125,1250,1375,1500,1625,1750,1875,2000,2125,2250,2375,2500,2625,2750,2875,3000], x = "Athlete", title="The Ranges", markers=True)

        st.plotly_chart(fig_event,use_container_width=True)
