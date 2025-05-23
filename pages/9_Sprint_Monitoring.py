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
        return df
    @st.cache_data
    def get_track_training_data_from_excel():
        df = pd.read_excel(
            io='pages/Sprint Monitoring/Training Data - Track Sprint.xlsx',
            engine ='openpyxl',
            sheet_name='Metrics',
            skiprows=0,
            usecols='A:BV',
            nrows=13000
            )
        return df
    data_types=["Athlete Dashboards","Gym Monitoring","Track Monitoring"]
    data_type = st.selectbox("Select Data:", data_types, key="Data Selector")

    if data_type=="Athlete Dashboards":
        athletes=["Rebecca Petch", "Shaane Fulton", "Ellesse Andrews", "Olivia King", "Sam Dakin"]
        athlete = st.selectbox("Select Athlete:", athletes, key="Athlete Selector")

        df_gym_master =get_gym_data_from_excel()
        df_gym_master = df_gym_master.loc[df_gym_master["Last Name"] == athlete.split(" ")[1]].sort_values("Completed Date", ascending=False).reset_index(drop=True)
        df_gym_master["Completed Date"] = pd.to_datetime(df_gym_master["Completed Date"]).dt.date
        df_gym_master=df_gym_master.drop(columns=["User ID","External ID","Workout ID","Exercise Type","Assigned Date"])
        # df_gym_master["Name"]=df_gym_master["First Name"].astype(str)+" "+df_gym_master["Last Name"].astype(str)
        

        df_track_master =get_track_training_data_from_excel()
        df_track_master = df_track_master.loc[df_track_master["Rider"] == athlete.split(" ")[0][0] +" "+athlete.split(" ")[1]].sort_values("Date", ascending=False).reset_index(drop=True)
        df_track_master["Date"] = pd.to_datetime(df_track_master["Date"]).dt.date
        df_track_master["GearInches"] = df_track_master["GearInches"].round(2)
        df_track_master["Lead"] = df_track_master["Lead"].fillna("None")


        

        if athlete == "Rebecca Petch":
            
            
            # Convert 'Completed Date' to datetime
            df_gym_master['Completed Date'] = pd.to_datetime(df_gym_master['Completed Date'])
            df_track_master['Date'] = pd.to_datetime(df_track_master['Date'])
            # Create a new column for the start of the week (Monday)
            df_gym_master['WeekStart'] = df_gym_master['Completed Date'] - pd.to_timedelta(df_gym_master['Completed Date'].dt.weekday, unit='d')

            # Group by 'WeekStart' and calculate weekly totals
            df_gym_master['weekly_totals'] = df_gym_master.groupby('WeekStart')['Volume Load'].transform('sum')

            # Create a new column for the start of the month
            df_gym_master['MonthStart'] = df_gym_master['Completed Date'].dt.to_period('M').dt.start_time

            # Group by 'MonthStart' and calculate monthly totals
            df_gym_master['monthly_totals'] = df_gym_master.groupby('MonthStart')['Volume Load'].transform('sum')

            
            # Create a new column for the year and quarter
            df_gym_master['Year-Quarter'] = df_gym_master['Completed Date'].dt.to_period('Q').astype(str)
            df_track_master['Year-Quarter'] = df_track_master['Date'].dt.to_period('Q').astype(str)

            # Optional: drop 'WeekStart' and 'MonthStart' if not needed
            df_gym_master.drop(columns=['WeekStart', 'MonthStart'], inplace=True)

            # Reset index if needed
            df_gym_master.reset_index(drop=True, inplace=True)

            
            # Group by 'Year-Quarter' and calculate total volume load for each quarter
            quarterly_volume_load = df_gym_master.groupby('Year-Quarter')['Volume Load'].sum().reset_index()

            # Plotly Express bar chart
            fig = px.bar(quarterly_volume_load, x='Year-Quarter', y='Volume Load', title='Total Gym Volume Load by Quarter')

            # Display the chart in Streamlit
            st.plotly_chart(fig)

            
            quarterly_work = df_track_master.groupby('Year-Quarter')['TotalWorkDoneOverall'].sum().reset_index()
            fig_quarterly_work = px.bar(quarterly_work, x='Year-Quarter', y='TotalWorkDoneOverall', title='Total Track Work Done by Quarter')
            st.plotly_chart(fig_quarterly_work,use_container_width=True)

            daily_work = df_track_master.groupby('Date')['TotalWorkDoneOverall'].sum().reset_index()
            fig_daily_work = px.bar(daily_work, x='Date', y='TotalWorkDoneOverall', title='Total Track Work Done by Day')
            st.plotly_chart(fig_daily_work,use_container_width=True)

            
            merged_df = pd.merge(quarterly_volume_load, quarterly_work, on='Year-Quarter', how='outer')
            merged_df.rename(columns={'Volume Load': 'Gym Volume Load', 'TotalWorkDoneOverall': 'Track Work Done'}, inplace=True)
            

            
            fig = px.bar(
            merged_df,
            x='Year-Quarter',
            y=['Gym Volume Load', 'Track Work Done'],
            title='Gym Volume and Track Work',
            labels={'value': 'Volume', 'variable': 'Category'},
            )

            # Show the chart in Streamlit
            st.plotly_chart(fig)



       


####################### Hip Thrust #############################################################

            # Filter the DataFrame
            df_hip_thrust = df_gym_master[df_gym_master["Exercise Name"] == "Hip Thrust"]

            # Create the figure
            fig_hip_thrust = go.Figure()

            # Add Volume Load to primary y-axis
            fig_hip_thrust.add_trace(go.Scatter(
                x=df_hip_thrust["Completed Date"],
                y=df_hip_thrust["Volume Load"],
                mode='lines+markers',
                name='Volume Load',
                yaxis='y1',
                customdata=df_hip_thrust[["Sets", "Reps/Time"]],
                hovertemplate='<b>Completed Date</b>: %{x}<br><b>Volume Load</b>: %{y}<br><b>Sets</b>: %{customdata[0]}<br><b>Reps/Time</b>: %{customdata[1]}<extra></extra>'
            ))

            # Add Highest Max to secondary y-axis
            fig_hip_thrust.add_trace(go.Scatter(
                x=df_hip_thrust["Completed Date"],
                y=df_hip_thrust["Highest Max"],
                mode='lines+markers',
                name='Highest Max',
                yaxis='y2',
                customdata=df_hip_thrust[["Sets", "Reps/Time"]],
                hovertemplate='<b>Completed Date</b>: %{x}<br><b>Highest Max</b>: %{y}<br><b>Sets</b>: %{customdata[0]}<br><b>Reps/Time</b>: %{customdata[1]}<extra></extra>'
            ))

            # Update layout with dual y-axes
            fig_hip_thrust.update_layout(
                title="Hip thrust highest weight and volume load",
                xaxis=dict(title="Completed Date"),
                yaxis=dict(title="Volume Load"),
                yaxis2=dict(title="Highest Max", overlaying='y', side='right'),
                legend=dict(title='Legend')
            )

            # Display in Streamlit
            st.plotly_chart(fig_hip_thrust, use_container_width=True)


######################## Back Squat ############################################################


            # Filter the DataFrame
            df_squat = df_gym_master[df_gym_master["Exercise Name"].str.contains("Back Squat", case=False, na=False)]
            
            # Create the figure
            fig_squat = go.Figure()

            # Add Volume Load to primary y-axis
            fig_squat.add_trace(go.Scatter(
                x=df_squat["Completed Date"],
                y=df_squat["Volume Load"],
                mode='lines+markers',
                name='Volume Load',
                yaxis='y1',
                customdata=df_squat[["Exercise Name","Sets", "Reps/Time"]],
                hovertemplate='<b>Completed Date</b>: %{x}<br><b>Volume Load</b>: %{y}<br><b>Exercise</b>: %{customdata[0]}<br><b>Sets/Time</b>: %{customdata[1]}<br><b>Reps/Time</b>: %{customdata[2]}<extra></extra>'
            ))

            # Add Highest Max to secondary y-axis
            fig_squat.add_trace(go.Scatter(
                x=df_squat["Completed Date"],
                y=df_squat["Highest Max"],
                mode='lines+markers',
                name='Highest Max',
                yaxis='y2',
                customdata=df_squat[["Exercise Name","Sets", "Reps/Time"]],
                hovertemplate='<b>Completed Date</b>: %{x}<br><b>Volume Load</b>: %{y}<br><b>Exercise</b>: %{customdata[0]}<br><b>Sets/Time</b>: %{customdata[1]}<br><b>Reps/Time</b>: %{customdata[2]}<extra></extra>'
            ))

            # Update layout with dual y-axes
            fig_squat.update_layout(
                title="Squat variations highest weight and volume load",
                xaxis=dict(title="Completed Date"),
                yaxis=dict(title="Volume Load"),
                yaxis2=dict(title="Highest Max", overlaying='y', side='right'),
                legend=dict(title='Legend')
            )

            # Display in Streamlit
            st.plotly_chart(fig_squat, use_container_width=True)


######################## Torque ############################################################

            # Filter the DataFrame
            df_torque = df_track_master[(df_track_master["Distance"] < 66) & (df_track_master["Start"] == "Standing")]

            # Create the figure
            fig_torque = go.Figure()

            # Add Max Full Rev Torque to primary y-axis
            fig_torque.add_trace(go.Scatter(
                x=df_torque["Date"],
                y=df_torque["MaxFullRevTorqueOverall"],
                mode='lines+markers',
                name='Max Full Rev Torque',
                yaxis='y1',
                customdata=df_torque[["Distance", "GearInches"]],
                hovertemplate='<b>Date</b>: %{x}<br><b>Max Full Rev Torque</b>: %{y}<br><b>Distance</b>: %{customdata[0]}<br><b>Gear Inches</b>: %{customdata[1]}<extra></extra>'
            ))

            # Add 0.5s Mean Max Torque to secondary y-axis
            fig_torque.add_trace(go.Scatter(
                x=df_torque["Date"],
                y=df_torque["0.5s Mean Max Torque (Overall)"],
                mode='lines+markers',
                name='0.5s Mean Max Torque',
                yaxis='y2',
                customdata=df_torque[["Distance", "GearInches"]],
                hovertemplate='<b>Date</b>: %{x}<br><b>0.5s Mean Max Torque</b>: %{y}<br><b>Distance</b>: %{customdata[0]}<br><b>Gear Inches</b>: %{customdata[1]}<extra></extra>'
            ))

            # Update layout with dual y-axes
            fig_torque.update_layout(
                title="Max Full Rev Torque & 0.5s Mean Max Torque",
                xaxis=dict(title="Date"),
                yaxis=dict(title="Max Full Rev Torque"),
                yaxis2=dict(title="0.5s Mean Max Torque", overlaying='y', side='right'),
                legend=dict(title='Legend')
            )

            # Display in Streamlit
            st.plotly_chart(fig_torque, use_container_width=True)


######################## CdA ############################################################

            # Filter the DataFrame
            df_cda = df_track_master[(df_track_master["Distance"] > 250) & (df_track_master["Start"] != "Standing")]
            
            # Create the figure
            fig_cda = go.Figure()

            # Add Max Full Rev Torque to primary y-axis
            fig_cda.add_trace(go.Scatter(
                x=df_cda["Date"],
                y=df_cda["CdA"],
                mode='lines+markers',
                name='CdA',
                yaxis='y1',
                customdata=df_cda[["Start", "Structure","Lead","Distance"]],
                hovertemplate='<b>Date</b>: %{x}<br><b>CdA</b>: %{y}<br><b>Start</b>: %{customdata[0]}<br><b>Structure</b>: %{customdata[1]}<br><b>Lead</b>: %{customdata[2]}<br><b>Distance</b>: %{customdata[3]}<extra></extra>'
            ))

            # Add 0.5s Mean Max Torque to secondary y-axis
            fig_cda.add_trace(go.Scatter(
                x=df_cda["Date"],
                y=df_cda["MeanPowerRep"],
                mode='lines+markers',
                name='Mean Power Rep',
                yaxis='y2',
                customdata=df_cda[["Start", "Structure","Lead","Distance"]],
                hovertemplate='<b>Date</b>: %{x}<br><b>Mean Power</b>: %{y}<br><b>Start</b>: %{customdata[0]}<br><b>Structure</b>: %{customdata[1]}<br><b>Lead</b>: %{customdata[2]}<br><b>Distance</b>: %{customdata[3]}<extra></extra>'
            ))

            # Update layout with dual y-axes
            fig_cda.update_layout(
                title="CdA & Average Power",
                xaxis=dict(title="Date"),
                yaxis=dict(title="CdA"),
                yaxis2=dict(title="Power", overlaying='y', side='right'),
                legend=dict(title='Legend')
            )

            # Display in Streamlit
            st.plotly_chart(fig_cda, use_container_width=True)


######################## Cadence ############################################################

            # Filter the DataFrame
            df_cadence = df_track_master[(df_track_master["Distance"] >= 250) & (df_track_master["Start"] != "Standing")]
            
            fig_cadence = px.scatter(df_cadence, x="Date", y = ["CadenceAtMaxFullRevPowerOverall","MaxCadenceOverall","MeanCadenceRep"],
                                   title = "Cadence")
            st.plotly_chart(fig_cadence,use_container_width=True)
            

            df_track_master
            df_gym_master





    if data_type=="Gym Monitoring":
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
        
        
    if data_type=="Track Monitoring":
        df_master =get_track_data_from_excel()
        df_master["Date"] = pd.to_datetime(df_master["Date"]).dt.date
        df_master = df_master.drop(columns=["Month","Week","Time","Standardised Time","Session","Activity","Level","Metrics Available"
                                            ,"LapDistance","GearRatio","KnownMaxPower","StartTime","Version"])
        
        
        

        c1,c2,c3,c4,c5=st.columns(5)
        with c1:
            athlete = st.multiselect("Select Athlete:",df_master["Rider"].sort_values().unique(),key="Athlete Select")
            if len(athlete)>0:
                df=df_master.loc[df_master["Rider"].isin(athlete)]
            else:
                df=df_master
        with c2:
            start = st.multiselect("Select start type:",df["Start"].sort_values().unique(),key="Start Select")
            if len(start)>0:
                df=df.loc[df["Start"].isin(start)]
        with c3:
            structure = st.multiselect("Select structure:",df["Structure"].sort_values().unique(),key="Structure Select")
            if len(structure)>0:
                df=df.loc[df["Structure"].isin(structure)]
        with c4:
            lead = st.multiselect("Select lead type:",df["Lead"].sort_values().unique(),key="Lead Select")
            if len(lead)>0:
                df=df.loc[df["Lead"].isin(lead)]
        with c5:
            distance = st.multiselect("Select distance:",df["Distance"].sort_values().unique(),key="Distance Select")
            if len(distance)>0:
                df=df.loc[df["Distance"].isin(distance)]
            
        df = df.reset_index(drop=True)
        df['GearInches'] = df['GearInches'].round(1)

        df
        cols = df.columns.tolist()
        cols.insert(0,"None")
        c1,c2,c3=st.columns(3)
        with c1:
            xaxis = st.selectbox("Select x-axis:",cols,key="xaxis Select")
        with c2:
            yaxis = st.selectbox("Select y-axis:",cols,key="yaxis Select") 
        with c3:
            group = st.selectbox("Group by:",cols,key="group Select")

        if (xaxis != "None") & (yaxis != "None") & (group == "None"):
            fig_exercise_hist = px.scatter(df, x=f"{xaxis}", y = f"{yaxis}", title = f"{xaxis} & {yaxis}")
            st.plotly_chart(fig_exercise_hist,use_container_width=True)
        elif (xaxis != "None") & (yaxis != "None") & (group != "None"):
            fig_exercise_hist = px.scatter(df, x=f"{xaxis}", y = f"{yaxis}", title = f"{xaxis} & {yaxis}",  color=f"{group}",hover_data=['Distance','GearInches'])
            st.plotly_chart(fig_exercise_hist,use_container_width=True)