#!/usr/bin/env python
# coding: utf-8


import pickle
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image
import datetime
from datetime import datetime, timedelta, date
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm
import os
import pytz
import streamlit_authenticator as stauth


def filter_top_3_cl2(group):
    if 'CL2' in group['Class'].values:  
        cl2_group = group[group['Class'] == 'CL2']  
        top = cl2_group.groupby('Race', group_keys=False).apply(lambda x: x.nlargest(3, 'Points'))  
        return pd.concat([top, group[group['Class'] != 'CL2']]) 
    return group
def filter_top_3_cl1(group):
    if 'CL1' in group['Class'].values:  # Check if the group contains rows with Class = "CL1"
        cl1_group = group[group['Class'] == 'CL1']  # Filter for rows where Class = "CL1"
        top = cl1_group.groupby('Race', group_keys=False).apply(lambda x: x.nlargest(3, 'Points'))  # Keep top 3
        return pd.concat([top, group[group['Class'] != 'CL1']])  # Add back rows with Class != "CL1"
    return group
def filter_top_6_cl2(group):
    if 'CL2' in group['Class'].values:  
        cl2_group = group[group['Class'] == 'CL2']  
        top = cl2_group.groupby('Race', group_keys=False).apply(lambda x: x.nlargest(6, 'Points'))  
        return pd.concat([top, group[group['Class'] != 'CL2']]) 
    return group
def filter_top_6_cl1(group):
    if 'CL1' in group['Class'].values:  # Check if the group contains rows with Class = "CL1"
        cl1_group = group[group['Class'] == 'CL1']  # Filter for rows where Class = "CL1"
        top = cl1_group.groupby('Race', group_keys=False).apply(lambda x: x.nlargest(6, 'Points'))  # Keep top 3
        return pd.concat([top, group[group['Class'] != 'CL1']])  # Add back rows with Class != "CL1"
    return group
def filter_top_1_NCp(group):
    if 'NCp' in group['Class'].values:  
        NCp_group = group[group['Class'] == 'NCp'] 
        top = NCp_group.groupby('Race', group_keys=False).apply(lambda x: x.nlargest(1, 'Points'))  
        return pd.concat([top, group[group['Class'] != 'NCp']])  
    return group
def filter_top_2_NCp(group):
    if 'NCp' in group['Class'].values:  
        NCp_group = group[group['Class'] == 'NCp'] 
        top = NCp_group.groupby('Race', group_keys=False).apply(lambda x: x.nlargest(2, 'Points'))  
        return pd.concat([top, group[group['Class'] != 'NCp']])  
    return group
def filter_top_2_WCh(group):
    if 'WCh' in group['Class'].values:  
        WCh_group = group[group['Class'] == 'WCh'] 
        top = WCh_group.groupby('Race', group_keys=False).apply(lambda x: x.nlargest(2, 'Points'))  
        return pd.concat([top, group[group['Class'] != 'WCh']])  
    return group
def filter_top_1_WCh(group):
    if 'WCh' in group['Class'].values:  
        WCh_group = group[group['Class'] == 'WCh'] 
        top = WCh_group.groupby('Race', group_keys=False).apply(lambda x: x.nlargest(1, 'Points'))  
        return pd.concat([top, group[group['Class'] != 'WCh']])  
    return group
def filter_top_2_CCh(group):
    if 'CCh' in group['Class'].values:  
        CCh_group = group[group['Class'] == 'CCh'] 
        top = CCh_group.groupby('Race', group_keys=False).apply(lambda x: x.nlargest(2, 'Points'))  
        return pd.concat([top, group[group['Class'] != 'CCh']])  
    return group
def filter_top_1_CCh(group):
    if 'CCh' in group['Class'].values:  
        CCh_group = group[group['Class'] == 'CCh'] 
        top = CCh_group.groupby('Race', group_keys=False).apply(lambda x: x.nlargest(1, 'Points'))  
        return pd.concat([top, group[group['Class'] != 'CCh']])  
    return group
def filter_top_1_NCh(group):
    if 'NCh' in group['Class'].values:  
        NCh_group = group[group['Class'] == 'NCh'] 
        top = NCh_group.groupby('Race', group_keys=False).apply(lambda x: x.nlargest(1, 'Points'))  
        return pd.concat([top, group[group['Class'] != 'NCh']])  
    return group
def filter_top_2_NCh(group):
    if 'NCh' in group['Class'].values:  
        NCh_group = group[group['Class'] == 'NCh'] 
        top = NCh_group.groupby('Race', group_keys=False).apply(lambda x: x.nlargest(2, 'Points'))  
        return pd.concat([top, group[group['Class'] != 'NCh']])  
    return group






st.set_page_config(page_title='CNZ Performance Database',
                  page_icon=":bike:",
                  layout="wide")

# --- USER AUTHENTICATION ---

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
    st.header('Points Tool')

    #update = datetime.date.today()+ pd.DateOffset(hour=12)
    
    def get_data(sheet_name):
        df = pd.read_excel(
            io=f'pages/Rankings/{sheet_name}.xlsx',
            engine ='openpyxl',
            sheet_name=f'{sheet_name}',
            skiprows=0,
            usecols='A:J',
            nrows=3000
            )
        df = df.replace(',','')
        df = df.replace('\*','',regex=True)
        df['Date'] = pd.to_datetime(df['Date']).dt.date
        return df
 

    Events = ["ME Worlds Picture", "WE Worlds Picture","ME Individual","ME Nation", "MS Individual", "MS Nation","MTS","MTP","M Mado Individual","M Mado Nation",
             "WE Individual","WE Nation", "WS Individual", "WS Nation","WTS","WTP","W Mado Individual","W Mado Nation"]

    Event = st.selectbox("Select Event:", Events, key="Event_selector")
    worlds_pic = 0
    if Event == "ME Individual":
        df=get_data("Endurance_Points_Ind_Men")
    elif Event == "ME Nation":
        df=get_data("Endurance_Points_Nat_Men")
        df=df.drop(['UCI_ID', 'Name'], axis=1)
    elif Event == "ME Worlds Picture":
        df_ind=get_data("Endurance_Points_Ind_Men")
        df_nat=get_data("Endurance_Points_Nat_Men")
        df_ind["Points"]=df_ind['Points'].astype(str).astype(int)
        Race = df_ind["Event"].str.split(" - ").str[-2]
        df_ind.insert(5,"Race",Race)
        df_ind["Event"] = df_ind["Event"].str.split(" - ").str[0]
        df_nat["Points"]=df_nat['Points'].astype(str).astype(int)
        Race = df_nat["Event"].str.split(" - ").str[-2]
        df_nat.insert(5,"Race",Race)
        df_nat["Event"] = df_nat["Event"].str.split(" - ").str[0]
        worlds_pic=1
    elif Event == "WE Worlds Picture":
        df_ind=get_data("Endurance_Points_Ind_Women")
        df_nat=get_data("Endurance_Points_Nat_Women")
        df_ind["Points"]=df_ind['Points'].astype(str).astype(int)
        Race = df_ind["Event"].str.split(" - ").str[-2]
        df_ind.insert(5,"Race",Race)
        df_ind["Event"] = df_ind["Event"].str.split(" - ").str[0]
        df_nat["Points"]=df_nat['Points'].astype(str).astype(int)
        Race = df_nat["Event"].str.split(" - ").str[-2]
        df_nat.insert(5,"Race",Race)
        df_nat["Event"] = df_nat["Event"].str.split(" - ").str[0]
        worlds_pic=1
    elif Event == "ME Nation":
        df=get_data("Endurance_Points_Nat_Men")
        df=df.drop(['UCI_ID', 'Name'], axis=1)
    elif Event == "MS Individual":
        df=get_data("Sprint_Points_Ind_Men")
    elif Event == "MS Nation":
        df=get_data("Sprint_Points_Nat_Men")
        df=df.drop(['UCI_ID', 'Name'], axis=1)
    elif Event == "MTS":
        df=get_data("MTS_Points")
        df["Unique"] = df["Name"] + df["Date"].astype(str) + df["Event"] + df["Rank"].astype(str)
        df = df.drop_duplicates(subset=['Unique'])
        df["Points"]=df["Points"].astype(int)*3
        df=df.drop(['Unique'], axis=1)
        df=df.drop(['UCI_ID', 'Name'], axis=1)
    elif Event == "MTP":
        df=get_data("MTP_Points")
       
        df["Unique"] = df["Name"] + df["Date"].astype(str) + df["Event"] + df["Rank"].astype(str)
        df = df.drop_duplicates(subset=['Unique'])
        df["Points"]=df["Points"].astype(int)*4
        df=df.drop(['Unique'], axis=1)
  
    elif Event == "M Mado Individual":
        df=get_data("Mado_Points_Ind_Men")
    elif Event == "M Mado Nation":
        df=get_data("Mado_Points_Nat_Men")
        df=df.drop(['UCI_ID', 'Name'], axis=1)
        
    elif Event == "WE Individual":
        df=get_data("Endurance_Points_Ind_Women")
    elif Event == "WE Nation":
        df=get_data("Endurance_Points_Nat_Women")
        df=df.drop(['UCI_ID', 'Name'], axis=1)
    elif Event == "WS Individual":
        df=get_data("Sprint_Points_Ind_Women")
    elif Event == "WS Nation":
        df=get_data("Sprint_Points_Nat_Women")
        df=df.drop(['UCI_ID', 'Country'], axis=1)
    elif Event == "WTS":
        df=get_data("WTS_Points")
        df=df.drop(['UCI_ID', 'Name'], axis=1)
        df["Unique"] = df["Name"] + df["Date"].astype(str) + df["Event"] + df["Rank"].astype(str)
        df = df.drop_duplicates(subset=['Unique'])
        df["Points"]=df["Points"].astype(int)*3
        df=df.drop(['Unique'], axis=1)

    elif Event == "WTP":
        df=get_data("WTP_Points")
        
        df["Unique"] = df["Name"] + df["Date"].astype(str) + df["Event"] + df["Rank"].astype(str)
        df = df.drop_duplicates(subset=['Unique'])
        df["Points"]=df["Points"].astype(int)*4
        df=df.drop(['Unique'], axis=1)
        df=df.drop(['UCI_ID', 'Name'], axis=1)
    elif Event == "W Mado Individual":
        df=get_data("Mado_Points_Ind_Women")
        df["Points"]=df["Points"].astype(int)*2
    elif Event == "W Mado Nation":
        df=get_data("Mado_Points_Nat_Women")
        df=df.drop(['UCI_ID', 'Name'], axis=1)
    if worlds_pic == 0:
         
        df["Points"]=df['Points'].astype(str).astype(int)
        Race = df["Event"].str.split(" - ").str[-2]
        df.insert(5,"Race",Race)
        df["Event"] = df["Event"].str.split(" - ").str[0]
        st.header("Original data")
        
    
    
    
    
    
    
    
    if Event in ("ME Worlds Picture", "WE Worlds Picture"):
        st.write("Filters one year before September 6th. Takes top 16 Nations from Nation Ranking, then adds the top eight nations from Individual ranking once these 16 nations have been removed from the individual ranking.")
        selected_date = date(2025, 9, 6)
        one_year_before = selected_date - timedelta(days=365)
        df_nat=df_nat.drop(['UCI_ID', 'Country'], axis=1)
        df_nat = df_nat[(df_nat['Date'] >= one_year_before) & (df_nat['Date'] <= selected_date)]
        
        df_nat = df_nat.groupby('Name', group_keys=False).apply(filter_top_1_NCp).reset_index(drop=True)
        df_nat = df_nat.groupby('Name', group_keys=False).apply(filter_top_1_NCh).reset_index(drop=True)
        df_nat = df_nat.groupby('Name', group_keys=False).apply(filter_top_1_CCh).reset_index(drop=True)
        df_nat = df_nat.groupby('Name', group_keys=False).apply(filter_top_1_WCh).reset_index(drop=True)
        df_nat = df_nat.groupby('Name', group_keys=False).apply(filter_top_3_cl2).reset_index(drop=True)
        df_nat = df_nat.groupby('Name', group_keys=False).apply(filter_top_3_cl1).reset_index(drop=True)
        
        proj_points = df_nat.groupby('Name')['Points'].sum().reset_index(name='Proj Points')

        # Rank the Proj Points (higher points get a better rank, i.e., 1 is the best rank)
        proj_points['Proj Rank'] = proj_points['Proj Points'].rank(ascending=False, method='dense').astype(int)

        # Merge the calculated Proj Points and Proj Rank back into the original DataFrame
        df_nat = df_nat.merge(proj_points, on='Name').sort_values(by=['Proj Points'],ascending=False)
        move = df_nat.pop("Proj Points")
        df_nat.insert(1,"Proj_Points", move)
        move = df_nat.pop("Proj Rank")
        df_nat.insert(2,"Proj_Rank", move)
        st.header("Nations ranking")
        df_nat = df_nat.reset_index(drop=True)
        df_nat
        st.header("Projected top 16 Nations:")
        top16 = df_nat.drop_duplicates(subset='Name').head(16)
        top16 =top16.drop(["Date","Class","Race","Event","Rank","Points"], axis=1).reset_index(drop=True)
        top16

        

        st.subheader("Individual ranking top eight with these top 16 nations removed:")
        # Filter the DataFrame
        df_ind = df_ind[(df_ind['Date'] >= one_year_before) & (df_ind['Date'] <= selected_date)]

        # Apply the filtering logic per UCI_ID group
        df_ind = df_ind.groupby('UCI_ID', group_keys=False).apply(filter_top_3_cl2).reset_index(drop=True)
        df_ind = df_ind.groupby('UCI_ID', group_keys=False).apply(filter_top_3_cl1).reset_index(drop=True)
        df_ind = df_ind.groupby('UCI_ID', group_keys=False).apply(filter_top_1_NCp).reset_index(drop=True)

        proj_points = df_ind.groupby('UCI_ID')['Points'].sum().reset_index(name='Proj Points')

        # Rank the Proj Points (higher points get a better rank, i.e., 1 is the best rank)
        proj_points['Proj Rank'] = proj_points['Proj Points'].rank(ascending=False, method='dense').astype(int)

        # Merge the calculated Proj Points and Proj Rank back into the original DataFrame
        df_ind = df_ind.merge(proj_points, on='UCI_ID').sort_values(by=['Proj Points'],ascending=False)
        move = df_ind.pop("Proj Points")
        df_ind.insert(1,"Proj_Points", move)
        move = df_ind.pop("Proj Rank")
        df_ind.insert(2,"Proj_Rank", move)
        top16_names = top16.drop_duplicates(subset='Name').head(16)['Name']

        # Filter df2 to exclude rows with names in top16_names
        df_ind_16_removed = df_ind[~df_ind['Country'].isin(top16_names)]

        athletes = df_ind_16_removed['Name'].drop_duplicates()
        Proj_Points = []
        Proj_Rank = []
        UCI_ID = []
        Country = []
        Current_Points = []
        Current_Rank = []
        OLY_totals = []
        WCh_totals = []
        NCp_totals = []
        CCh_totals = []
        NCh_totals = []
        ChL_totals = []
        ChR_totals = []
        CL1_totals = []
        CL2_totals = []
        totals=[]
        allowed_athletes = []
        classes = ['OLY','WCh','NCp','CCh','NCh','ChL','ChR','CL1','CL2']
        for idx, athlete in enumerate(athletes):

            athlete_results = df_ind_16_removed.loc[(df_ind_16_removed.Name == athlete)]
            Proj_Points.append(df_ind_16_removed.loc[(df_ind_16_removed.Name == athlete)]["Proj_Points"].iloc[0])
            Proj_Rank.append(df_ind_16_removed.loc[(df_ind_16_removed.Name == athlete)]["Proj_Rank"].iloc[0])
    #         UCI_ID.append(filtered_df.loc[(filtered_df.Name == athlete)]["UCI_ID"].iloc[0])
            Country.append(df_ind_16_removed.loc[(df_ind_16_removed.Name == athlete)]["Country"].iloc[0])
            Current_Points.append(df_ind_16_removed.loc[(df_ind_16_removed.Name == athlete)]["Current_Points"].iloc[0])
            Current_Rank.append(df_ind_16_removed.loc[(df_ind_16_removed.Name == athlete)]["Current_Rank"].iloc[0])
            y=athlete_results.groupby('Class')['Points'].sum().reset_index()
            points_by_class = pd.DataFrame(y)

            x = points_by_class.loc[(points_by_class.Class == 'OLY')]["Points"]
            if len(x)>0:
                OLY_totals.append(x.iloc[0])
            else:
                OLY_totals.append(0)
            x = points_by_class.loc[(points_by_class.Class == 'WCh')]["Points"]
            if len(x)>0:
                WCh_totals.append(x.iloc[0])
            else:
                WCh_totals.append(0)
            x = points_by_class.loc[(points_by_class.Class == 'NCp')]["Points"]
            if len(x)>0:
                NCp_totals.append(x.iloc[0])
            else:
                NCp_totals.append(0)
            x = points_by_class.loc[(points_by_class.Class == 'CCh')]["Points"]

            if len(x)>0:
                CCh_totals.append(x.iloc[0])
            else:
                CCh_totals.append(0)
            x = points_by_class.loc[(points_by_class.Class == 'NCh')]["Points"]
            if len(x)>0:    
                NCh_totals.append(x.iloc[0])
            else:
                NCh_totals.append(0)
            x = points_by_class.loc[(points_by_class.Class == 'ChL')]["Points"]
            if len(x)>0:
                ChL_totals.append(x.iloc[0])
            else:
                ChL_totals.append(0)
            x = points_by_class.loc[(points_by_class.Class == 'ChR')]["Points"]
            if len(x)>0:
                ChR_totals.append(x.iloc[0])
            else:
                ChR_totals.append(0)
            x = points_by_class.loc[(points_by_class.Class == 'CL1')]["Points"]
            if len(x)>0:
                CL1_totals.append(x.iloc[0])
            else:
                CL1_totals.append(0)
            x = points_by_class.loc[(points_by_class.Class == 'CL2')]["Points"]
            if len(x)>0:
                CL2_totals.append(x.iloc[0])
            else:
                CL2_totals.append(0)
        d = {'Name': athletes, 'Country': Country, 'Current_Rank': Current_Rank, 'Current_Points': Current_Points, 'Proj_Rank': Proj_Rank, 'Proj_Points': Proj_Points, 'OLY': OLY_totals, 'WCh': WCh_totals, 'NCp': NCp_totals, 'CCh': CCh_totals, 'NCh': NCh_totals, 'ChL': ChL_totals, 'ChR': ChR_totals, 'CL1': CL1_totals, 'CL2': CL2_totals}
        nice_df = pd.DataFrame(d).reset_index(drop=True)
         
        
        nice_df = nice_df.drop_duplicates(subset='Name').head(8)
        nice_df
#         df_ind_16_removed =df_ind_16_removed.drop(["Date","Class","Race","Event","Rank","Points","UCI_ID"], axis=1).reset_index(drop=True)
#         columns = list(df_ind_16_removed.columns)
#         columns.insert(1, columns.pop(3))  # Remove "Country" from 4th spot and insert it at the 2nd spot
#         df_ind_16_removed = df_ind_16_removed[columns]
#         df_ind_16_removed
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    elif Event in ("ME Individual" , "MS Individual" , "M Mado Individual" , "WE Individual" , "WS Individual" , "W Mado Individual"):
        nations = st.multiselect("Select nations to include - default is to include all:",sorted(df["Country"].unique()))
        if len(nations)>0:
            filtered_df = df[df['Country'].isin(nations)]
        else:
            filtered_df=df
        filtered_df
        
        selected_date = st.date_input("Select an end date (6th September is 6 weeks before Worlds)", datetime.now().date())
        
            



        # Calculate the date one year before - There is the 18 month rule (3.3.003) but every nation is having a CC so those points will drop off anyway
        one_year_before = selected_date - timedelta(days=365)

        # Filter the DataFrame
        filtered_df = filtered_df[(filtered_df['Date'] >= one_year_before) & (filtered_df['Date'] <= selected_date)]
        
        # Apply the filtering logic per UCI_ID group
        filtered_df = filtered_df.groupby('UCI_ID', group_keys=False).apply(filter_top_3_cl2).reset_index(drop=True)
        filtered_df = filtered_df.groupby('UCI_ID', group_keys=False).apply(filter_top_3_cl1).reset_index(drop=True)
        filtered_df = filtered_df.groupby('UCI_ID', group_keys=False).apply(filter_top_1_NCp).reset_index(drop=True)
        
        proj_points = filtered_df.groupby('UCI_ID')['Points'].sum().reset_index(name='Proj_Points')
        filtered_df = filtered_df.merge(proj_points, on='UCI_ID').sort_values(by=['Proj_Points'],ascending=False)
        move = filtered_df.pop("Proj_Points")
        filtered_df.insert(1,"Proj_Points", move)

        
        filtered_df['Proj_Rank'] = filtered_df['Proj_Points'].rank(ascending=False, method='dense').astype(int)
        
        # Merge the calculated Proj Points and Proj Rank back into the original DataFrame

        move = filtered_df.pop("Proj_Rank")
        filtered_df.insert(2,"Proj_Rank", move)

        st.subheader("Filtered DataFrame")
        st.write("Filters one year before the chosen date. Takes top three CL1, CL2, and top NCp result only - I don't think any further filtering is required.")
        filtered_df
        st.header("Breakdown")

        athletes = filtered_df['Name'].drop_duplicates()
        Proj_Points = []
        Proj_Rank = []
        UCI_ID = []
        Country = []
        Current_Points = []
        Current_Rank = []
        OLY_totals = []
        WCh_totals = []
        NCp_totals = []
        CCh_totals = []
        NCh_totals = []
        ChL_totals = []
        ChR_totals = []
        CL1_totals = []
        CL2_totals = []
        totals=[]
        allowed_athletes = []
        classes = ['OLY','WCh','NCp','CCh','NCh','ChL','ChR','CL1','CL2']
        for idx, athlete in enumerate(athletes):

            athlete_results = filtered_df.loc[(filtered_df.Name == athlete)]
            Proj_Points.append(filtered_df.loc[(filtered_df.Name == athlete)]["Proj_Points"].iloc[0])
            Proj_Rank.append(filtered_df.loc[(filtered_df.Name == athlete)]["Proj_Rank"].iloc[0])
    #         UCI_ID.append(filtered_df.loc[(filtered_df.Name == athlete)]["UCI_ID"].iloc[0])
            Country.append(filtered_df.loc[(filtered_df.Name == athlete)]["Country"].iloc[0])
            Current_Points.append(filtered_df.loc[(filtered_df.Name == athlete)]["Current_Points"].iloc[0])
            Current_Rank.append(filtered_df.loc[(filtered_df.Name == athlete)]["Current_Rank"].iloc[0])
            y=athlete_results.groupby('Class')['Points'].sum().reset_index()
            points_by_class = pd.DataFrame(y)

            x = points_by_class.loc[(points_by_class.Class == 'OLY')]["Points"]
            if len(x)>0:
                OLY_totals.append(x.iloc[0])
            else:
                OLY_totals.append(0)
            x = points_by_class.loc[(points_by_class.Class == 'WCh')]["Points"]
            if len(x)>0:
                WCh_totals.append(x.iloc[0])
            else:
                WCh_totals.append(0)
            x = points_by_class.loc[(points_by_class.Class == 'NCp')]["Points"]
            if len(x)>0:
                NCp_totals.append(x.iloc[0])
            else:
                NCp_totals.append(0)
            x = points_by_class.loc[(points_by_class.Class == 'CCh')]["Points"]

            if len(x)>0:
                CCh_totals.append(x.iloc[0])
            else:
                CCh_totals.append(0)
            x = points_by_class.loc[(points_by_class.Class == 'NCh')]["Points"]
            if len(x)>0:    
                NCh_totals.append(x.iloc[0])
            else:
                NCh_totals.append(0)
            x = points_by_class.loc[(points_by_class.Class == 'ChL')]["Points"]
            if len(x)>0:
                ChL_totals.append(x.iloc[0])
            else:
                ChL_totals.append(0)
            x = points_by_class.loc[(points_by_class.Class == 'ChR')]["Points"]
            if len(x)>0:
                ChR_totals.append(x.iloc[0])
            else:
                ChR_totals.append(0)
            x = points_by_class.loc[(points_by_class.Class == 'CL1')]["Points"]
            if len(x)>0:
                CL1_totals.append(x.iloc[0])
            else:
                CL1_totals.append(0)
            x = points_by_class.loc[(points_by_class.Class == 'CL2')]["Points"]
            if len(x)>0:
                CL2_totals.append(x.iloc[0])
            else:
                CL2_totals.append(0)
        d = {'Name': athletes, 'Country': Country, 'Current_Rank': Current_Rank, 'Current_Points': Current_Points, 'Proj_Rank': Proj_Rank, 'Proj_Points': Proj_Points, 'OLY': OLY_totals, 'WCh': WCh_totals, 'NCp': NCp_totals, 'CCh': CCh_totals, 'NCh': NCh_totals, 'ChL': ChL_totals, 'ChR': ChR_totals, 'CL1': CL1_totals, 'CL2': CL2_totals}
        nice_df = pd.DataFrame(d).reset_index(drop=True)
        ath_per_nat = st.selectbox("Athletes per Nation (typically 2 for Sprint and Keirin):",("All","1","2"))
        if ath_per_nat == "1":
            nice_df = nice_df.loc[nice_df.groupby('Country')['Proj_Points'].idxmax()]
        elif ath_per_nat == "2":
            nice_df = nice_df.groupby('Country', group_keys=False).apply(lambda x: x.nlargest(2, 'Proj_Points'))
        nice_df['Proj_Rank'] = nice_df['Proj_Points'].rank(ascending=False, method='dense').astype(int)    
        nice_df=nice_df.sort_values(by=['Proj_Rank']).reset_index(drop=True)
        nice_df
        
        


        

        
        
        

    elif Event in ("MTS" , "MTP" , "WTS" , "WTP"):
        nations = st.multiselect("Select nations to include - default is to include all:",sorted(df["Country"].unique()))
        if len(nations)>0:
            filtered_df = df[df['Country'].isin(nations)]
        else:
            filtered_df=df
        filtered_df
        selected_date = st.date_input("Select a date", datetime.now().date())

        # Calculate the date one year before - There is the 18 month rule (3.3.003) but every nation is having a CC so those points will drop off anyway
        one_year_before = selected_date - timedelta(days=365)

        # Filter the DataFrame
        filtered_df = filtered_df[(filtered_df['Date'] >= one_year_before) & (filtered_df['Date'] <= selected_date)]
        
        filtered_df = filtered_df.groupby('Country', group_keys=False).apply(filter_top_1_NCp).reset_index(drop=True)
        filtered_df = filtered_df.groupby('Country', group_keys=False).apply(filter_top_1_NCh).reset_index(drop=True)
        
        proj_points = filtered_df.groupby('Country')['Points'].sum().reset_index(name='Proj Points')

        # Rank the Proj Points (higher points get a better rank, i.e., 1 is the best rank)
        proj_points['Proj Rank'] = proj_points['Proj Points'].rank(ascending=False, method='dense').astype(int)

        # Merge the calculated Proj Points and Proj Rank back into the original DataFrame
        filtered_df = filtered_df.merge(proj_points, on='Country').sort_values(by=['Proj Points'],ascending=False)
        move = filtered_df.pop("Proj Points")
        filtered_df.insert(1,"Proj_Points", move)
        move = filtered_df.pop("Proj Rank")
        filtered_df.insert(2,"Proj_Rank", move)

        st.subheader("Filtered DataFrame")
        st.write("Filters one year before the chosen date. Takes top NCp result - I don't think any further filtering is required.")
        st.write(filtered_df)
        st.header("Breakdown")

        athletes = filtered_df['Country'].drop_duplicates()
        Proj_Points = []
        Proj_Rank = []
        UCI_ID = []
        Country = []
        Current_Points = []
        Current_Rank = []
        OLY_totals = []
        WCh_totals = []
        NCp_totals = []
        CCh_totals = []
        NCh_totals = []
        ChL_totals = []
        ChR_totals = []
        CL1_totals = []
        CL2_totals = []
        totals=[]
        allowed_athletes = []
        classes = ['OLY','WCh','NCp','CCh','NCh','ChL','ChR','CL1','CL2']
        for idx, athlete in enumerate(athletes):

            athlete_results = filtered_df.loc[(filtered_df.Country == athlete)]
            Proj_Points.append(filtered_df.loc[(filtered_df.Country == athlete)]["Proj_Points"].iloc[0])
            Proj_Rank.append(filtered_df.loc[(filtered_df.Country == athlete)]["Proj_Rank"].iloc[0])
            Current_Points.append(filtered_df.loc[(filtered_df.Country == athlete)]["Current_Points"].iloc[0])
            Current_Rank.append(filtered_df.loc[(filtered_df.Country == athlete)]["Current_Rank"].iloc[0])
            y=athlete_results.groupby('Class')['Points'].sum().reset_index()
            points_by_class = pd.DataFrame(y)

            x = points_by_class.loc[(points_by_class.Class == 'OLY')]["Points"]
            if len(x)>0:
                OLY_totals.append(x.iloc[0])
            else:
                OLY_totals.append(0)
            x = points_by_class.loc[(points_by_class.Class == 'WCh')]["Points"]
            if len(x)>0:
                WCh_totals.append(x.iloc[0])
            else:
                WCh_totals.append(0)
            x = points_by_class.loc[(points_by_class.Class == 'NCp')]["Points"]
            if len(x)>0:
                NCp_totals.append(x.iloc[0])
            else:
                NCp_totals.append(0)
            x = points_by_class.loc[(points_by_class.Class == 'CCh')]["Points"]

            if len(x)>0:
                CCh_totals.append(x.iloc[0])
            else:
                CCh_totals.append(0)
            x = points_by_class.loc[(points_by_class.Class == 'NCh')]["Points"]
            if len(x)>0:    
                NCh_totals.append(x.iloc[0])
            else:
                NCh_totals.append(0)
            x = points_by_class.loc[(points_by_class.Class == 'ChL')]["Points"]
            if len(x)>0:
                ChL_totals.append(x.iloc[0])
            else:
                ChL_totals.append(0)
            x = points_by_class.loc[(points_by_class.Class == 'ChR')]["Points"]
            if len(x)>0:
                ChR_totals.append(x.iloc[0])
            else:
                ChR_totals.append(0)
            x = points_by_class.loc[(points_by_class.Class == 'CL1')]["Points"]
            if len(x)>0:
                CL1_totals.append(x.iloc[0])
            else:
                CL1_totals.append(0)
            x = points_by_class.loc[(points_by_class.Class == 'CL2')]["Points"]
            if len(x)>0:
                CL2_totals.append(x.iloc[0])
            else:
                CL2_totals.append(0)
               
        d = {'Country': athletes,  'Current_Rank': Current_Rank, 'Current_Points': Current_Points, 'Proj_Rank': Proj_Rank, 'Proj_Points': Proj_Points, 'OLY': OLY_totals, 'WCh': WCh_totals, 'NCp': NCp_totals, 'CCh': CCh_totals, 'NCh': NCh_totals, 'ChL': ChL_totals, 'ChR': ChR_totals, 'CL1': CL1_totals, 'CL2': CL2_totals}
        nice_df = pd.DataFrame(d).reset_index(drop=True)
        nice_df    

        
        
        
        
        
        
        
        
        
    elif Event in ("MS Nation" , "WS Nation" ):
        selected_date = st.date_input("Select an end date (6th September is 6 weeks before Worlds)", datetime.now().date())
        nations = st.multiselect("Select nations to include - default is to include all:",sorted(df["Country"].unique()))
        if len(nations)>0:
            filtered_df = df[df['Country'].isin(nations)]
        else:
            filtered_df=df
        filtered_df
        # Calculate the date one year before - There is the 18 month rule (3.3.003) but every nation is having a CC so those points will drop off anyway
        one_year_before = selected_date - timedelta(days=365)

        # Filter the DataFrame
        filtered_df = filtered_df[(filtered_df['Date'] >= one_year_before) & (filtered_df['Date'] <= selected_date)]
        
        filtered_df = filtered_df.groupby('Country', group_keys=False).apply(filter_top_2_NCp).reset_index(drop=True)
        filtered_df = filtered_df.groupby('Country', group_keys=False).apply(filter_top_1_NCh).reset_index(drop=True)
        filtered_df = filtered_df.groupby('Country', group_keys=False).apply(filter_top_2_CCh).reset_index(drop=True)
        filtered_df = filtered_df.groupby('Country', group_keys=False).apply(filter_top_2_WCh).reset_index(drop=True)
        filtered_df = filtered_df.groupby('Country', group_keys=False).apply(filter_top_3_cl2).reset_index(drop=True)
        filtered_df = filtered_df.groupby('Country', group_keys=False).apply(filter_top_3_cl1).reset_index(drop=True)
        
        proj_points = filtered_df.groupby('Country')['Points'].sum().reset_index(name='Proj Points')

        # Rank the Proj Points (higher points get a better rank, i.e., 1 is the best rank)
        proj_points['Proj Rank'] = proj_points['Proj Points'].rank(ascending=False, method='dense').astype(int)

        # Merge the calculated Proj Points and Proj Rank back into the original DataFrame
        filtered_df = filtered_df.merge(proj_points, on='Country').sort_values(by=['Proj Points'],ascending=False)
        move = filtered_df.pop("Proj Points")
        filtered_df.insert(1,"Proj_Points", move)
        move = filtered_df.pop("Proj Rank")
        filtered_df.insert(2,"Proj_Rank", move)

        st.subheader("Filtered DataFrame")
        st.write("Filters one year before the chosen date. Takes top 2 results from WCh, NCh and CC, and top 3 results from Cl1 and Cl2.")
        st.write(filtered_df)
        st.header("Breakdown")

        athletes = filtered_df['Country'].drop_duplicates()
        Proj_Points = []
        Proj_Rank = []
        UCI_ID = []
        Country = []
        Current_Points = []
        Current_Rank = []
        OLY_totals = []
        WCh_totals = []
        NCp_totals = []
        CCh_totals = []
        NCh_totals = []
        ChL_totals = []
        ChR_totals = []
        CL1_totals = []
        CL2_totals = []
        totals=[]
        allowed_athletes = []
        classes = ['OLY','WCh','NCp','CCh','NCh','ChL','ChR','CL1','CL2']
        for idx, athlete in enumerate(athletes):

            athlete_results = filtered_df.loc[(filtered_df.Country == athlete)]
            Proj_Points.append(filtered_df.loc[(filtered_df.Country == athlete)]["Proj_Points"].iloc[0])
            Proj_Rank.append(filtered_df.loc[(filtered_df.Country == athlete)]["Proj_Rank"].iloc[0])
    #         UCI_ID.append(filtered_df.loc[(filtered_df.Name == athlete)]["UCI_ID"].iloc[0])
    #         Country.append(filtered_df.loc[(filtered_df.Name == athlete)]["Country"].iloc[0])
            Current_Points.append(filtered_df.loc[(filtered_df.Country == athlete)]["Current_Points"].iloc[0])
            Current_Rank.append(filtered_df.loc[(filtered_df.Country == athlete)]["Current_Rank"].iloc[0])
            y=athlete_results.groupby('Class')['Points'].sum().reset_index()
            points_by_class = pd.DataFrame(y)

            x = points_by_class.loc[(points_by_class.Class == 'OLY')]["Points"]
            if len(x)>0:
                OLY_totals.append(x.iloc[0])
            else:
                OLY_totals.append(0)
            x = points_by_class.loc[(points_by_class.Class == 'WCh')]["Points"]
            if len(x)>0:
                WCh_totals.append(x.iloc[0])
            else:
                WCh_totals.append(0)
            x = points_by_class.loc[(points_by_class.Class == 'NCp')]["Points"]
            if len(x)>0:
                NCp_totals.append(x.iloc[0])
            else:
                NCp_totals.append(0)
            x = points_by_class.loc[(points_by_class.Class == 'CCh')]["Points"]

            if len(x)>0:
                CCh_totals.append(x.iloc[0])
            else:
                CCh_totals.append(0)
            x = points_by_class.loc[(points_by_class.Class == 'NCh')]["Points"]
            if len(x)>0:    
                NCh_totals.append(x.iloc[0])
            else:
                NCh_totals.append(0)
            x = points_by_class.loc[(points_by_class.Class == 'ChL')]["Points"]
            if len(x)>0:
                ChL_totals.append(x.iloc[0])
            else:
                ChL_totals.append(0)
            x = points_by_class.loc[(points_by_class.Class == 'ChR')]["Points"]
            if len(x)>0:
                ChR_totals.append(x.iloc[0])
            else:
                ChR_totals.append(0)
            x = points_by_class.loc[(points_by_class.Class == 'CL1')]["Points"]
            if len(x)>0:
                CL1_totals.append(x.iloc[0])
            else:
                CL1_totals.append(0)
            x = points_by_class.loc[(points_by_class.Class == 'CL2')]["Points"]
            if len(x)>0:
                CL2_totals.append(x.iloc[0])
            else:
                CL2_totals.append(0)

        d = {'Country': athletes,  'Current_Rank': Current_Rank, 'Current_Points': Current_Points, 'Proj_Rank': Proj_Rank, 'Proj_Points': Proj_Points, 'OLY': OLY_totals, 'WCh': WCh_totals, 'NCp': NCp_totals, 'CCh': CCh_totals, 'NCh': NCh_totals, 'ChL': ChL_totals, 'ChR': ChR_totals, 'CL1': CL1_totals, 'CL2': CL2_totals}
        nice_df = pd.DataFrame(d).reset_index(drop=True)
        nice_df    


        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
    elif Event in ("M Mado Nation" , "W Mado Nation" ):
        selected_date = st.date_input("Select an end date (6th September is 6 weeks before Worlds)", datetime.now().date())
        nations = st.multiselect("Select nations to include - default is to include all:",sorted(df["Country"].unique()))
        if len(nations)>0:
            filtered_df = df[df['Country'].isin(nations)]
        else:
            filtered_df=df
        filtered_df
        # Calculate the date one year before - There is the 18 month rule (3.3.003) but every nation is having a CC so those points will drop off anyway
        one_year_before = selected_date - timedelta(days=365)

        # Filter the DataFrame
        filtered_df = filtered_df[(filtered_df['Date'] >= one_year_before) & (filtered_df['Date'] <= selected_date)]
        
        filtered_df = filtered_df.groupby('Country', group_keys=False).apply(filter_top_2_NCp).reset_index(drop=True)
        filtered_df = filtered_df.groupby('Country', group_keys=False).apply(filter_top_2_NCh).reset_index(drop=True)
        filtered_df = filtered_df.groupby('Country', group_keys=False).apply(filter_top_2_CCh).reset_index(drop=True)
        filtered_df = filtered_df.groupby('Country', group_keys=False).apply(filter_top_2_WCh).reset_index(drop=True)
        filtered_df = filtered_df.groupby('Country', group_keys=False).apply(filter_top_6_cl2).reset_index(drop=True)
        filtered_df = filtered_df.groupby('Country', group_keys=False).apply(filter_top_6_cl1).reset_index(drop=True)
        
        proj_points = filtered_df.groupby('Country')['Points'].sum().reset_index(name='Proj Points')

        # Rank the Proj Points (higher points get a better rank, i.e., 1 is the best rank)
        proj_points['Proj Rank'] = proj_points['Proj Points'].rank(ascending=False, method='dense').astype(int)

        # Merge the calculated Proj Points and Proj Rank back into the original DataFrame
        filtered_df = filtered_df.merge(proj_points, on='Country').sort_values(by=['Proj Points'],ascending=False)
        move = filtered_df.pop("Proj Points")
        filtered_df.insert(1,"Proj_Points", move)
        move = filtered_df.pop("Proj Rank")
        filtered_df.insert(2,"Proj_Rank", move)

        st.subheader("Filtered DataFrame")
        st.write("Filters one year before the chosen date. Takes top 2 results from WCh, NCh and CC, and top 3 results from Cl1 and Cl2.")
        st.write(filtered_df)
        st.header("Breakdown")

        athletes = filtered_df['Country'].drop_duplicates()
        Proj_Points = []
        Proj_Rank = []
        UCI_ID = []
        Country = []
        Current_Points = []
        Current_Rank = []
        OLY_totals = []
        WCh_totals = []
        NCp_totals = []
        CCh_totals = []
        NCh_totals = []
        ChL_totals = []
        ChR_totals = []
        CL1_totals = []
        CL2_totals = []
        totals=[]
        allowed_athletes = []
        classes = ['OLY','WCh','NCp','CCh','NCh','ChL','ChR','CL1','CL2']
        for idx, athlete in enumerate(athletes):

            athlete_results = filtered_df.loc[(filtered_df.Country == athlete)]
            Proj_Points.append(filtered_df.loc[(filtered_df.Country == athlete)]["Proj_Points"].iloc[0])
            Proj_Rank.append(filtered_df.loc[(filtered_df.Country == athlete)]["Proj_Rank"].iloc[0])
    #         UCI_ID.append(filtered_df.loc[(filtered_df.Name == athlete)]["UCI_ID"].iloc[0])
    #         Country.append(filtered_df.loc[(filtered_df.Name == athlete)]["Country"].iloc[0])
            Current_Points.append(filtered_df.loc[(filtered_df.Country == athlete)]["Current_Points"].iloc[0])
            Current_Rank.append(filtered_df.loc[(filtered_df.Country == athlete)]["Current_Rank"].iloc[0])
            y=athlete_results.groupby('Class')['Points'].sum().reset_index()
            points_by_class = pd.DataFrame(y)

            x = points_by_class.loc[(points_by_class.Class == 'OLY')]["Points"]
            if len(x)>0:
                OLY_totals.append(x.iloc[0])
            else:
                OLY_totals.append(0)
            x = points_by_class.loc[(points_by_class.Class == 'WCh')]["Points"]
            if len(x)>0:
                WCh_totals.append(x.iloc[0])
            else:
                WCh_totals.append(0)
            x = points_by_class.loc[(points_by_class.Class == 'NCp')]["Points"]
            if len(x)>0:
                NCp_totals.append(x.iloc[0])
            else:
                NCp_totals.append(0)
            x = points_by_class.loc[(points_by_class.Class == 'CCh')]["Points"]

            if len(x)>0:
                CCh_totals.append(x.iloc[0])
            else:
                CCh_totals.append(0)
            x = points_by_class.loc[(points_by_class.Class == 'NCh')]["Points"]
            if len(x)>0:    
                NCh_totals.append(x.iloc[0])
            else:
                NCh_totals.append(0)
            x = points_by_class.loc[(points_by_class.Class == 'ChL')]["Points"]
            if len(x)>0:
                ChL_totals.append(x.iloc[0])
            else:
                ChL_totals.append(0)
            x = points_by_class.loc[(points_by_class.Class == 'ChR')]["Points"]
            if len(x)>0:
                ChR_totals.append(x.iloc[0])
            else:
                ChR_totals.append(0)
            x = points_by_class.loc[(points_by_class.Class == 'CL1')]["Points"]
            if len(x)>0:
                CL1_totals.append(x.iloc[0])
            else:
                CL1_totals.append(0)
            x = points_by_class.loc[(points_by_class.Class == 'CL2')]["Points"]
            if len(x)>0:
                CL2_totals.append(x.iloc[0])
            else:
                CL2_totals.append(0)

        d = {'Country': athletes,  'Current_Rank': Current_Rank, 'Current_Points': Current_Points, 'Proj_Rank': Proj_Rank, 'Proj_Points': Proj_Points, 'OLY': OLY_totals, 'WCh': WCh_totals, 'NCp': NCp_totals, 'CCh': CCh_totals, 'NCh': NCh_totals, 'ChL': ChL_totals, 'ChR': ChR_totals, 'CL1': CL1_totals, 'CL2': CL2_totals}
        nice_df = pd.DataFrame(d).reset_index(drop=True)
        nice_df    

        
        
        
        
        
        
        
    #######    
    elif Event in ("ME Nation" , "WE Nation" ):
        selected_date = st.date_input("Select an end date (6th September is 6 weeks before Worlds)", datetime.now().date())
        nations = st.multiselect("Select nations to include - default is to include all:",sorted(df["Country"].unique()))
        if len(nations)>0:
            filtered_df = df[df['Country'].isin(nations)]
        else:
            filtered_df=df
        filtered_df
        # Calculate the date one year before - There is the 18 month rule (3.3.003) but every nation is having a CC so those points will drop off anyway
        one_year_before = selected_date - timedelta(days=365)

        # Filter the DataFrame
        filtered_df = filtered_df[(filtered_df['Date'] >= one_year_before) & (filtered_df['Date'] <= selected_date)]
        
        filtered_df = filtered_df.groupby('Country', group_keys=False).apply(filter_top_1_NCp).reset_index(drop=True)
        filtered_df = filtered_df.groupby('Country', group_keys=False).apply(filter_top_1_NCh).reset_index(drop=True)
        filtered_df = filtered_df.groupby('Country', group_keys=False).apply(filter_top_1_CCh).reset_index(drop=True)
        filtered_df = filtered_df.groupby('Country', group_keys=False).apply(filter_top_1_WCh).reset_index(drop=True)
        filtered_df = filtered_df.groupby('Country', group_keys=False).apply(filter_top_3_cl2).reset_index(drop=True)
        filtered_df = filtered_df.groupby('Country', group_keys=False).apply(filter_top_3_cl1).reset_index(drop=True)
        
        proj_points = filtered_df.groupby('Country')['Points'].sum().reset_index(name='Proj Points')

        # Rank the Proj Points (higher points get a better rank, i.e., 1 is the best rank)
        proj_points['Proj Rank'] = proj_points['Proj Points'].rank(ascending=False, method='dense').astype(int)

        # Merge the calculated Proj Points and Proj Rank back into the original DataFrame
        filtered_df = filtered_df.merge(proj_points, on='Country').sort_values(by=['Proj Points'],ascending=False)
        move = filtered_df.pop("Proj Points")
        filtered_df.insert(1,"Proj_Points", move)
        move = filtered_df.pop("Proj Rank")
        filtered_df.insert(2,"Proj_Rank", move)

        st.subheader("Filtered DataFrame")
        st.write("Filters one year before the chosen date. Takes top results from WCh, NCh and CC, and top 3 results from Cl1 and Cl2.")
        filtered_df
        st.header("Breakdown")



        athletes = filtered_df['Country'].drop_duplicates()
        Proj_Points = []
        Proj_Rank = []
        UCI_ID = []
        Country = []
        Current_Points = []
        Current_Rank = []
        OLY_totals = []
        WCh_totals = []
        NCp_totals = []
        CCh_totals = []
        NCh_totals = []
        ChL_totals = []
        ChR_totals = []
        CL1_totals = []
        CL2_totals = []
        totals=[]
        allowed_athletes = []
        classes = ['OLY','WCh','NCp','CCh','NCh','ChL','ChR','CL1','CL2']
        for idx, athlete in enumerate(athletes):

            athlete_results = filtered_df.loc[(filtered_df.Country == athlete)]
            Proj_Points.append(filtered_df.loc[(filtered_df.Country == athlete)]["Proj_Points"].iloc[0])
            Proj_Rank.append(filtered_df.loc[(filtered_df.Country == athlete)]["Proj_Rank"].iloc[0])
    #         UCI_ID.append(filtered_df.loc[(filtered_df.Name == athlete)]["UCI_ID"].iloc[0])
    #         Country.append(filtered_df.loc[(filtered_df.Name == athlete)]["Country"].iloc[0])
            Current_Points.append(filtered_df.loc[(filtered_df.Country == athlete)]["Current_Points"].iloc[0])
            Current_Rank.append(filtered_df.loc[(filtered_df.Country == athlete)]["Current_Rank"].iloc[0])
            y=athlete_results.groupby('Class')['Points'].sum().reset_index()
            points_by_class = pd.DataFrame(y)

            x = points_by_class.loc[(points_by_class.Class == 'OLY')]["Points"]
            if len(x)>0:
                OLY_totals.append(x.iloc[0])
            else:
                OLY_totals.append(0)
            x = points_by_class.loc[(points_by_class.Class == 'WCh')]["Points"]
            if len(x)>0:
                WCh_totals.append(x.iloc[0])
            else:
                WCh_totals.append(0)
            x = points_by_class.loc[(points_by_class.Class == 'NCp')]["Points"]
            if len(x)>0:
                NCp_totals.append(x.iloc[0])
            else:
                NCp_totals.append(0)
            x = points_by_class.loc[(points_by_class.Class == 'CCh')]["Points"]

            if len(x)>0:
                CCh_totals.append(x.iloc[0])
            else:
                CCh_totals.append(0)
            x = points_by_class.loc[(points_by_class.Class == 'NCh')]["Points"]
            if len(x)>0:    
                NCh_totals.append(x.iloc[0])
            else:
                NCh_totals.append(0)
            x = points_by_class.loc[(points_by_class.Class == 'ChL')]["Points"]
            if len(x)>0:
                ChL_totals.append(x.iloc[0])
            else:
                ChL_totals.append(0)
            x = points_by_class.loc[(points_by_class.Class == 'ChR')]["Points"]
            if len(x)>0:
                ChR_totals.append(x.iloc[0])
            else:
                ChR_totals.append(0)
            x = points_by_class.loc[(points_by_class.Class == 'CL1')]["Points"]
            if len(x)>0:
                CL1_totals.append(x.iloc[0])
            else:
                CL1_totals.append(0)
            x = points_by_class.loc[(points_by_class.Class == 'CL2')]["Points"]
            if len(x)>0:
                CL2_totals.append(x.iloc[0])
            else:
                CL2_totals.append(0)



        d = {'Country': athletes,  'Current_Rank': Current_Rank, 'Current_Points': Current_Points, 'Proj_Rank': Proj_Rank, 'Proj_Points': Proj_Points, 'OLY': OLY_totals, 'WCh': WCh_totals, 'NCp': NCp_totals, 'CCh': CCh_totals, 'NCh': NCh_totals, 'ChL': ChL_totals, 'ChR': ChR_totals, 'CL1': CL1_totals, 'CL2': CL2_totals}
        nice_df = pd.DataFrame(d).reset_index(drop=True)
        nice_df    

    
    
    
    
    ##############################################Prior to 2025###############################################
    #@st.cache_data

#     def get_MK_points_data_from_excel():
#         df_MK = pd.read_excel(
#             io='pages/Kierin_Points_Men.xlsx',
#             engine ='openpyxl',
#             sheet_name='Kierin_Points_Men',
#             skiprows=0,
#             usecols='A:J',
#             nrows=3000
#             )
#         df_MK = df_MK.replace(',','')
#         df_MK['Date'] = pd.to_datetime(df_MK['Date']).dt.date
#         return df_MK
#     df_MK = get_MK_points_data_from_excel()



#     def get_MS_points_data_from_excel():
#         df_MS = pd.read_excel(
#             io='pages/Sprint_Points_Men.xlsx',
#             engine ='openpyxl',
#             sheet_name='Sprint_Points_Men',
#             skiprows=0,
#             usecols='A:J',
#             nrows=3000
#             )
#         df_MS = df_MS.replace(',','')
#         df_MS['Date'] = pd.to_datetime(df_MS['Date']).dt.date
#         return df_MS
#     df_MS = get_MS_points_data_from_excel()





#     def get_WS_points_data_from_excel():
#         df_WS = pd.read_excel(
#             io='pages/Sprint_Points_Women.xlsx',
#             engine ='openpyxl',
#             sheet_name='Sprint_Points_Women',
#             skiprows=0,
#             usecols='A:J',
#             nrows=3000
#             )
#         df_WS = df_WS.replace(',','')
#         df_WS['Date'] = pd.to_datetime(df_WS['Date']).dt.date
#         return df_WS
#     df_WS = get_WS_points_data_from_excel()




#     def get_WK_points_data_from_excel():
#         df_WK = pd.read_excel(
#             io='pages/Kierin_Points_Women.xlsx',
#             engine ='openpyxl',
#             sheet_name='Kierin_Points_Women',
#             skiprows=0,
#             usecols='A:J',
#             nrows=3000
#             )
#         df_WK = df_WK.replace(',','')
#         df_WK['Date'] = pd.to_datetime(df_WK['Date']).dt.date
#         return df_WK
#     df_WK = get_WK_points_data_from_excel()

#     def get_WTT_points_data_from_excel():
#         df_WTT = pd.read_excel(
#             io='pages/Time_Trial_Points_Women.xlsx',
#             engine ='openpyxl',
#             sheet_name='Time_Trial_Points_Women',
#             skiprows=0,
#             usecols='A:J',
#             nrows=3000
#             )
#         df_WTT = df_WTT.replace(',','')
#         df_WTT['Date'] = pd.to_datetime(df_WTT['Date']).dt.date
#         return df_WTT
#     df_WTT = get_WTT_points_data_from_excel()
    
#     ###This script is in "Daily Scrape"
#     def get_para_points_data_from_excel():
#         df_Para = pd.read_excel(
#             io='pages/Para_Points_All_FINAL.xlsx',
#             engine ='openpyxl',
#             sheet_name='Para_Points_All_FINAL',
#             skiprows=0,
#             usecols='A:L',
#             nrows=5816
#             )
#         df_Para["Points"] = df_Para["Points"].str.replace("*","")
#         df_Para = df_Para.replace(',','')
#         df_Para['Date'] = pd.to_datetime(df_Para['Date']).dt.date
#         df_Para = df_Para.astype({'Points':'int'})
#         df_Para["Event"] = df_Para["Event"] +" "+df_Para["Track_Road"]
#         df_Para["UCI_ID"]=df_Para["UCI_ID"].astype(str)
#         df_Para["Unique1"] = df_Para["Classification"]+" "+df_Para["Track_Road"]+" "+df_Para["Event"] + " "+df_Para["Country"]+ " "+df_Para["Sex"]

#         df_Para["Unique2"] = df_Para["Classification"]+" "+df_Para["Track_Road"]+" "+df_Para["Event"] + " "+df_Para["Country"]+ " "+df_Para["Sex"]+ " "+df_Para["UCI_ID"]
#         return df_Para
#     df_Para = get_para_points_data_from_excel()
    
#     def get_2022_para_points_data_from_excel():
#         df_Para_2022 = pd.read_excel(
#             io='pages/Para_Points_All_2022.xlsx',
#             engine ='openpyxl',
#             sheet_name='Para_Points_All_2022',
#             skiprows=0,
#             usecols='A:L',
#             nrows=5000
#             )
#         df_Para_2022["Points"] = df_Para_2022["Points"].str.replace("*","")
#         df_Para_2022 = df_Para_2022.replace(',','')
#         df_Para_2022['Date'] = pd.to_datetime(df_Para_2022['Date']).dt.date
#         df_Para_2022 = df_Para_2022.astype({'Points':'int'})
#         df_Para_2022["Event"] = df_Para_2022["Event"] +" "+df_Para_2022["Track_Road"]
#         df_Para_2022["UCI_ID"]=df_Para_2022["UCI_ID"].astype(str)
        
#         df_Para_2022["Unique1"] = df_Para_2022["Classification"]+" "+df_Para_2022["Track_Road"]+" "+df_Para_2022["Event"] + " "+df_Para_2022["Country"]
#         df_Para_2022["Unique2"] = df_Para_2022["Classification"]+" "+df_Para_2022["Track_Road"]+" "+df_Para_2022["Event"] + " "+df_Para_2022["Country"]+ " "+df_Para_2022["UCI_ID"]
#         return df_Para_2022
#     df_Para_2022 = get_2022_para_points_data_from_excel()

#     s = os.path.getmtime('pages/Kierin_Points_Women.xlsx')
#     dt_m = datetime.date.fromtimestamp(s)+pd.DateOffset(days=1)
#     s1 = dt_m.strftime("%d/%m/%Y")
#     st.subheader("Last updated on "+ str(s1))
#     Events = ["Men's Sprint","Men's Keirin", "Women's Sprint", "Women's Keirin","Women's 500 Time Trial","Para Team Tracking"]

#     Event = st.selectbox("Select Event:", Events, key="Event_selector")

#     if Event == Events[0]:
#         df=df_MS
#     elif Event == Events[1]:
#         df=df_MK
#     elif Event == Events[2]:
#         df=df_WS
#     elif Event == Events[3]:
#         df=df_WK
#     elif Event == Events[4]:
#         df=df_WTT
#     else:
#         df=df_Para

#     df_orig=df
    
#     if Event == Events[5]:
#         st.header("Filtered Data")
#         import pandas as pd
#         import streamlit as st
#         import streamlit.components.v1 as components
#         from pandas.api.types import (
#         is_categorical_dtype,
#         is_datetime64_any_dtype,
#         is_numeric_dtype,
#         is_object_dtype,
#         )
        
        
#         frames = [df_Para_2022, df_Para]
#         data_22 = st.checkbox("Include data from 2022?")
#         if data_22:
#             df = pd.concat(frames)
        
#         def filter_dataframe(df: pd.DataFrame) -> pd.DataFrame:

#             modify = st.checkbox("Add filters")

#             if not modify:
#                 return df

#             df = df.copy()

#             # Try to convert datetimes into a standard format (datetime, no timezone)
#             for col in df.columns:
#                 if is_object_dtype(df[col]):
#                     try:
#                         df[col] = pd.to_datetime(df[col])
#                     except Exception:
#                         pass

#                 if is_datetime64_any_dtype(df[col]):
#                     df[col] = df[col].dt.tz_localize(None)

#             modification_container = st.container()

#             with modification_container:
#                 to_filter_columns = st.multiselect("Filter dataframe on", df.columns)
#                 for column in to_filter_columns:
#                     left, right = st.columns((1, 20))
#                     # Treat columns with < 10 unique values as categorical
#                     if is_categorical_dtype(df[column]) or df[column].nunique() < 11:
#                         user_cat_input = right.multiselect(
#                             f"Values for {column}",
#                             df[column].unique(),
#                             default=list(df[column].unique()),
#                         )
#                         df = df[df[column].isin(user_cat_input)]
#                     elif is_numeric_dtype(df[column]):
#                         _min = float(df[column].min())
#                         _max = float(df[column].max())
#                         step = (_max - _min) / 100
#                         user_num_input = right.slider(
#                             f"Values for {column}",
#                             min_value=_min,
#                             max_value=_max,
#                             value=(_min, _max),
#                             step=step,
#                         )
#                         df = df[df[column].between(*user_num_input)]
#                     elif is_datetime64_any_dtype(df[column]):
#                         user_date_input = right.date_input(
#                             f"Values for {column}",
#                             value=(
#                                 df[column].min(),
#                                 df[column].max(),
#                             ),
#                         )
#                         if len(user_date_input) == 2:
#                             user_date_input = tuple(map(pd.to_datetime, user_date_input))
#                             start_date, end_date = user_date_input
#                             df = df.loc[df[column].between(start_date, end_date)]
#                     else:
#                         user_text_input = right.text_input(
#                             f"Substring or regex in {column}",
#                         )
#                         if user_text_input:
#                             df = df[df[column].astype(str).str.contains(user_text_input)]

#             return df
#         df_master = df
#         df_filt = filter_dataframe(df)
#         df_filt=df_filt.reset_index(drop=True)
        
#         ##This section is for filtering out anyone except top three in each athlete class
#         df_filt_top_three = pd.DataFrame().reindex_like(df_filt).dropna()
        
#         non_top_three=[] 
#         drops=[]
#         uniques = df_filt["Unique1"].unique()
#         #uniques 
#         for i in range(len(uniques)):
#             #Making a small dataframe with all riders in the same country + sport class at each event
#             df_ath_unq = pd.DataFrame(df_filt.loc[df_filt["Unique1"]==uniques[i]])
#             #Checking if there are more than three athletes per country in this sport class
#             if len(df_ath_unq["UCI_ID"].unique())>3:
                
#                 ids = df_ath_unq["UCI_ID"].unique()
#                 unique2s = df_ath_unq["Unique2"].unique()
                
#                 points_sum=[]
#                 for j in range(len(ids)):
#                     points_sum.append(sum(df_ath_unq.loc[df_ath_unq["UCI_ID"]==ids[j]]["Points"]))
#                 df_top_three=pd.DataFrame(points_sum)
#                 df_top_three["UCI_ID"]=ids
#                 df_top_three["Unique2"]=unique2s
#                 df_top_three=df_top_three.sort_values(by=0,ascending=False).reset_index(drop=True)
                
#                 for k in range(3,len(df_top_three)):
#                     non_top_three.append(df_top_three["Unique2"][k])
                    
                    
#         #I want to remove all rows from df_filt where unique2 is in non_top_three
#         for l in range(len(df_filt)):
#             if df_filt["Unique2"][l] in non_top_three:
#                 drops.append(l)
#         for ind in drops:
#             df_filt=df_filt.drop([ind])
                
            
            

#         ######################################## filtering done ##################            
        
#         df_filt=df_filt.reset_index(drop=True)
#         df_filt
        
# #         df_filt_top_three=df_filt_top_three.reset_index(drop=True)
# #         df_filt_top_three
#         c1,c2,c3,c4=st.columns(4)
#         with c1:
#             st.subheader("Points by Athlete")
#             unq_aths = df_filt["Name"].unique()
#             ath_points=[]
#             for ath in unq_aths:
#                 ath_points.append(sum(df_filt.loc[df_filt["Name"]==ath]["Points"]))
#             df_ath_points = pd.DataFrame(unq_aths)
#             df_ath_points.rename(columns={ df_ath_points.columns[0]: "Name" }, inplace = True)
#             df_ath_points["Points"] = ath_points
            
#             df_ath_points=df_ath_points.sort_values(by="Points",ascending=False)
#             df_ath_points.insert(0, 'Rank', range(1, 1 + len(df_ath_points)))
#             df_ath_points
#         with c2:
#             st.subheader("Points by Nation")
#             unq_nat = df_filt["Country"].unique()
#             nat_points=[]
#             for nat in unq_nat:
#                 nat_points.append(sum(df_filt.loc[df_filt["Country"]==nat]["Points"]))
#             df_nat_points = pd.DataFrame(unq_nat)
#             df_nat_points.rename(columns={ df_nat_points.columns[0]: "Country" }, inplace = True)
#             df_nat_points["Points"] = nat_points
#             df_nat_points=df_nat_points.sort_values(by="Points",ascending=False)
#             df_nat_points.insert(0, 'Rank', range(1, 1 + len(df_nat_points)))
#             df_nat_points
#         with c3:
#             st.subheader("Points by Event")
#             unq_event = df_filt["Event"].unique()
#             event_points=[]
#             for event in unq_event:
#                 event_points.append(sum(df_filt.loc[df_filt["Event"]==event]["Points"]))
#             df_event_points = pd.DataFrame(unq_event)
#             df_event_points.rename(columns={ df_event_points.columns[0]: "Event" }, inplace = True)
#             df_event_points["Points"] = event_points
#             df_event_points=df_event_points.sort_values(by="Points",ascending=False)
#             df_event_points.insert(0, 'Rank', range(1, 1 + len(df_event_points)))
#             df_event_points
#         with c4:
#             st.subheader("Points by Sex")
#             unq_sex = df_filt["Sex"].unique()
#             sex_points=[]
#             for sex in unq_sex:
#                 sex_points.append(sum(df_filt.loc[df_filt["Sex"]==sex]["Points"]))
#             df_sex_points = pd.DataFrame(unq_sex)
#             df_sex_points.rename(columns={ df_sex_points.columns[0]: "Sex" }, inplace = True)
#             df_sex_points["Points"] = sex_points
#             df_sex_points=df_sex_points.sort_values(by="Points",ascending=False)
#             df_sex_points.insert(0, 'Rank', range(1, 1 + len(df_sex_points)))
#             df_sex_points
        
#         c1,c2=st.columns(2)
#         with c1:
#             male_countries = df_filt.loc[df_filt["Sex"]=="Men"].drop_duplicates(subset=['Country']).reset_index(drop=True)
#             df_count_male=pd.DataFrame(male_countries["Country"])
            

#             points_male=[]


#             for idx,countries in enumerate(male_countries["Country"]):
#                 points_male.append(df_filt.loc[(df_filt['Country'] == countries) & (df_filt['Sex'] == "Men")]["Points"].sum())
#             df_count_male["Points"]=points_male
#             total_male=sum(points_male)

#             male_slots=[]


#             for idx,points in enumerate(df_count_male["Points"]):            
#                 male_slots.append(points/(total_male/88))
#             df_count_male["Male_Slots"]=male_slots


#             df_count_male=df_count_male.sort_values("Points",ascending=False).reset_index(drop=True)
#             df_count_male.insert(0, 'Rank', range(1, 1 + len(df_count_male)))
#             st.header("Male Allocation by Country")
#             df_count_male
#             st.write(f'Total number of male points is {total_male}')
#             st.write(f'There are 88 male slots available, so the male factor is {round(total_male/88,2)}.')
#             nzl_male_points=df_count_male.loc[df_count_male["Country"]=="NZL"]["Points"].tolist()[0]
#             st.write(f'NZL has a total of {nzl_male_points} male points') 
#             st.write(f'This gives a total of {round(nzl_male_points/(total_male/88),2)} male slots.')
        
#         with c2:
#             female_countries = df_filt.loc[df_filt["Sex"]=="Women"].drop_duplicates(subset=['Country']).reset_index(drop=True)
#             df_count_female=pd.DataFrame(female_countries["Country"])
            

#             points_female=[]


#             for idx,countries in enumerate(female_countries["Country"]):
#                 points_female.append(df_filt.loc[(df_filt['Country'] == countries) & (df_filt['Sex'] == "Women")]["Points"].sum())
#             df_count_female["Points"]=points_female
#             total_female=sum(points_female)

#             female_slots=[]


#             for idx,points in enumerate(df_count_female["Points"]):            
#                 female_slots.append(points/(total_female/47))
#             df_count_female["female_Slots"]=female_slots


#             df_count_female=df_count_female.sort_values("Points",ascending=False).reset_index(drop=True)
#             df_count_female.insert(0, 'Rank', range(1, 1 + len(df_count_female)))
#             st.header("Female Allocation by Country")
#             df_count_female
#             st.write(f'Total number of female points is {total_female}')
#             st.write(f'There are 47 female slots available, so the female factor is {round(total_female/47,2)}.')
#             nzl_female_points=df_count_female.loc[df_count_female["Country"]=="NZL"]["Points"].tolist()[0]
#             st.write(f'NZL has a total of {nzl_female_points} female points') 
#             st.write(f'This gives a total of {round(nzl_female_points/(total_female/47),2)} female slots.')
    
#     else:


#         #st.subheader("Number of events for inclusion (shouldn't have to change these values)")
#         today = datetime.date.today()
#         default_start = datetime.date(2022, 6, 21)
#         # col_one, col_two, col_three, col_four, col_five = st.columns(5)

#         ### This was when you could change the number of events etc

#         # with col_one:
#         #     WC_events = st.number_input("UCI World Championships", min_value=0, max_value=None, value=1, key="WC")
#         # with col_two:
#         #     NC_events = st.number_input("Nations' Cup", min_value=0, max_value=None, value=1, key="NC")
#         # with col_three:
#         #     CC_events = st.number_input("Continental Championships", min_value=0, max_value=None, value=1, key="CC")
#         # with col_four:
#         #     NCH_events = st.number_input("National Championships", min_value=0, max_value=None, value=1, key="NCH")
#         # with col_five:
#         #     TCLOR_events = st.number_input("Track Champions League Overall Ranking", min_value=0, max_value=None, value=1, key="TCLOR")
#         # col_one, col_two, col_three, col_four,col_five = st.columns(5)
#         # with col_three:
#         #     CTWO_events = st.number_input("Class 2", min_value=0, max_value=None, value=3, key="C2")
#         # with col_one:
#         #     TCLRR_events = st.number_input("Track Champions League Round Ranking", min_value=0, max_value=None, value=5, key="TCLRR")
#         # with col_two:
#         #     CONE_events = st.number_input("Class 1", min_value=0, max_value=None, value=3, key="C1")
#         # with col_four:
#         #     start_date = st.date_input('Period Start', default_start,key="Start date")
#         # with col_five:
#         #     end_date = st.date_input('Period Finish', today,key="End date")
#         # col_one, col_two, col_three, col_four, col_five = st.columns(5)
#         # with col_one:
#         #     max_athletes = st.number_input("Max numbers of athletes from each nation", min_value=0, max_value=None, value=2, key="Max_athletes")

#         ##Hard coded event numbers
#         WC_events=1
#         NC_events=1
#         CC_events=1
#         NCH_events=1
#         TCLOR_events=1
#         CTWO_events=3
#         TCLRR_events=5
#         CONE_events=3
#         start_date = default_start
#         end_date = datetime.date(2023, 6, 23)
#         #max_athletes=2



#         st.write("This sums the best World Champs, Nations Cup, Continental Champs, National Champs, and Overall Champions League points, as well as top three Class 1 and Class 2 points, and top five Champions League Round points, between " + str(start_date) + " and " + str(end_date))

#         col_one, col_two, col_three, col_four = st.columns(4)
#         with col_one:
#             options = ["All athletes","Top two from each Nation"]
#             Max_Ath = st.selectbox("Athletes shown:", options, key="Max Athletes")
#         with col_two:
#             kiwisOnly = ["No","Yes"]
#             JustKiwis = st.selectbox("Show Kiwis Only?:", kiwisOnly, key="kiwis only")

#         if Max_Ath=="Top two from each Nation":
#             max_athletes = 2
#         else:
#             max_athletes = 200


#         df = df[(df['Date'] > start_date) & (df['Date'] < end_date)]
#         athletes = df['Name'].drop_duplicates()
#         countries = []

#         WC_totals = []
#         NC_totals = []
#         CC_totals = []
#         NCH_totals = []
#         TCLRR_totals = []
#         TCLOR_totals = []
#         CONE_totals = []
#         CTWO_totals = []
#         totals=[]
#         allowed_athletes = []

#         for i in range(len(athletes)):
#             y = df.loc[(df.Name == athletes.iloc[i]),'Country'].iloc[0]
#             if countries.count(y)<max_athletes:
#                 allowed_athletes.append(athletes.iloc[i])
#                 countries.append(y)
#                 total=0
#                 x = df.loc[(df.Class == "WCh") &  (df.Name == athletes.iloc[i]),'Points'].astype(int).sort_values(ascending=False)
#                 WC_total = sum(x[:WC_events])
#                 WC_totals.append(WC_total)
#                 total+=WC_total

#                 x = df.loc[(df.Class == "NCp") &  (df.Name == athletes.iloc[i]),'Points'].astype(int).sort_values(ascending=False)
#                 NC_total = sum(x[:NC_events])
#                 NC_totals.append(NC_total)
#                 total+=NC_total

#                 x = df.loc[(df.Class == "CCh") &  (df.Name == athletes.iloc[i]),'Points'].astype(int).sort_values(ascending=False)
#                 CC_total = sum(x[:CC_events])
#                 CC_totals.append(CC_total)
#                 total+=CC_total

#                 x = df.loc[(df.Class == "NCh") &  (df.Name == athletes.iloc[i]),'Points'].astype(int).sort_values(ascending=False)
#                 NCH_total = sum(x[:NCH_events])
#                 NCH_totals.append(NCH_total)
#                 total+=NCH_total

#                 x = df.loc[(df.Class == "ChL") &  (df.Name == athletes.iloc[i]),'Points'].astype(int).sort_values(ascending=False)
#                 TCLOR_total = sum(x[:TCLOR_events])
#                 TCLOR_totals.append(TCLOR_total)
#                 total+=TCLOR_total

#                 x = df.loc[(df.Class == "ChR") &  (df.Name == athletes.iloc[i]),'Points'].astype(int).sort_values(ascending=False)
#                 TCLRR_total = sum(x[:TCLRR_events])
#                 TCLRR_totals.append(TCLRR_total)
#                 total+=TCLRR_total

#                 x = df.loc[(df.Class == "CL1") &  (df.Name == athletes.iloc[i]),'Points'].astype(int).sort_values(ascending=False)
#                 CONE_total = sum(x[:CONE_events])
#                 CONE_totals.append(CONE_total)
#                 total+=CONE_total

#                 x = df.loc[(df.Class == "CL2") &  (df.Name == athletes.iloc[i]),'Points'].astype(int).sort_values(ascending=False)
#                 CTWO_total = sum(x[:CTWO_events])
#                 CTWO_totals.append(CTWO_total)
#                 total+=CTWO_total
#                 totals.append(total)



#         Points = {'Name': allowed_athletes,
#                   'Country': countries,
#                   'Total': totals,
#                   'WCh': WC_totals,
#                   "NCp": NC_totals,
#                   'CCh': CC_totals,
#                   'NCh': NCH_totals,
#                   'ChL': TCLOR_totals,
#                   'ChR': TCLRR_totals,
#                   'CL1': CONE_totals,
#                   'CL2': CTWO_totals,

#                  }

#         df_points=pd.DataFrame(Points).sort_values('Total',ascending=False)
#         Rank = list(range(1,len(allowed_athletes)+1))
#         df_points.insert(loc=0, column='Rank', value=Rank)
#         if JustKiwis == "Yes":
#             df_points = df_points.loc[(df_points.Country == "NZL")]
#         df_points


#         st.subheader("All Results")
#         col_one, col_two = st.columns(2)

#         Classes = df_orig['Class'].drop_duplicates().sort_values()
#         Events = df_orig['Event'].drop_duplicates().sort_values()
#         with col_one:
#             Class = st.multiselect("Select Class(es):", Classes)

#         df_class = df_orig.query(
#             "Class == @Class"
#         )

#         if Class==[]:
#             Events = df_orig['Event'].drop_duplicates().sort_values()
#         else:
#             Events = df_class['Event'].drop_duplicates().sort_values()
#         with col_two:
#             Event = st.multiselect("Select Event(s):", Events)

#         df_event = df_orig.query(
#             "Event == @Event"
#         )

#         df_both = df_orig.query(
#             "Class == @Class & Event == @Event"
#         )

#         if Class==[] and Event==[]:
#             st.dataframe(df_orig)
#         elif Event==[]:
#             st.dataframe(df_class)
#         elif Class==[]:
#             st.dataframe(df_event)
#         else:
#             st.dataframe(df_both)




