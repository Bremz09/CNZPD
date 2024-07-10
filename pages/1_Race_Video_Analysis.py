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
    checkboxid=0
    ##This bit is the historical visualiser
    def filter_dataframe(df: pd.DataFrame) -> pd.DataFrame:

        modify = st.checkbox("Add filters",key=f"filt{checkboxid}")

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


   
    racetype = st.selectbox(
        "Select Race Type:",
        options=["Women's TP", "Men's TP", "Women's Team Sprint","Mens' Keirin","WTS Starts","Men's IP","Women's IP"]
        ) 
    
    ################################################ Women's Team Pursuit ##########################################################
    
    if racetype == "Women's TP":
        df_master = pd.read_excel(f'pages/video_analysis/TP_Master_Women.xlsx')
        df_master = df_master.sort_values(by=["Sort_name","Distance"], ascending=[False,True])
        
        df_small = df_master.drop(columns=["Save_Date","Action","Video","Sort_date","Sort_letter"])
        
        c1,c2,c3=st.columns(3)
        with c1:
            
            ath_filt = st.multiselect(
    'Filter athletes? Leave blank to see all rides',["Ally Wollaston","Bryony Botha","Emily Shearman","Micky Drummond","Nicole Shields","Sami Donnelly"]
    )
            st.markdown("[Jump to Full Summary](#full-summary)", unsafe_allow_html=True)

        #st.write(df_small["Title"].unique())
        with c2:
            if len(ath_filt)>0:
                
                options=[]
                for race in df_small["Title"].unique():
                    for name in ath_filt:
                        #st.write(df_small["Front"].loc[df_small["Title"]==race].unique())
                        if name in df_small["Front"].loc[df_small["Title"]==race].unique() and race not in options:
                            #st.write(df_small["Front"].loc[df_small["Title"]==race])
                            options.append(race)
                selections = st.multiselect(
                "Select past effort(s):",
                options=options,#.sort_values(ascending=False)
                ) 
            else:
                selections = st.multiselect(
                "Select past effort(s):",
                options=df_master["Title"].unique())
                st.write("PTA")
            
                
        with c3:
            show_vids = ["No","Yes"]
            Videos = st.selectbox("Show Race Videos?", show_vids, key="Show_Vids")


        if len(selections) !=0:
            avg_speed_dists=[]
            df_combine = pd.DataFrame()
            for count,event_count in enumerate(selections):
                st.markdown("---")
                col_1,col_2=st.columns(2)
                with col_1:
                    df_temp = df_master.loc[df_master['Title'] == selections[count]]
                    df_combine = pd.concat([df_combine, df_temp], axis=0)
                    df_small = df_temp.drop(columns=["Save_Date","Video","Sort_name","Sort_date","Sort_letter"])
                    df_small=df_small.reset_index(drop="True")
                    r1 = [1]
                    r2 = [2]
                    r3 = [3]
                    r4 = [4]
                    r1WS = [0.971]
                    r2WS = [0.612]
                    r3WS = [0.495]
                    r4WS = [0.459]
                    speed_diff=[df_small["Del_Speed"][0]]

                    no_riders=4
                    drag_feel = [0,0.971,0.612,0.495,0.459]
                    for j in range(1,len(df_small)):
                        speed_diff.append(df_small["Del_Speed"][j]-df_small["Del_Speed"][j-1])
                        if df_small["Action"][j-1] == "Change":
                            r1.append(r1[j-1]-1)
                            r2.append(r2[j-1]-1)
                            r3.append(r3[j-1]-1)
                            r4.append(r4[j-1]-1)
                        elif df_small["Action"][j-1] == "Drop":
                            no_riders = 3
                            drag_feel = [0,0.972,0.617,0.517]
                            r1.append(r1[j-1]-1)
                            r2.append(r2[j-1]-1)
                            r3.append(r3[j-1]-1)
                            r4.append(r4[j-1]-1)
                        else:
                            r1.append(r1[j-1])
                            r2.append(r2[j-1])
                            r3.append(r3[j-1])
                            r4.append(r4[j-1])
                        if r1[j]==0:
                            r1[j]=no_riders
                        if r2[j]==0:
                            r2[j]=no_riders
                        if r3[j]==0:
                            r3[j]=no_riders
                        if r4[j]==0:
                            r4[j]=no_riders
                        r1WS.append(drag_feel[r1[j]])
                        r2WS.append(drag_feel[r2[j]])
                        r3WS.append(drag_feel[r3[j]])
                        r4WS.append(drag_feel[r4[j]])
                    if "Drop" in df_small["Action"].unique():        
                        ind = df_small.index[df_small['Action'] == "Drop"][0]

                        if r1[ind]==1:
                            r1[ind+1:]=[0]*(len(df_small)-ind-1)
                            r1WS[ind+1:]=[0]*(len(df_small)-ind-1)
                        if r2[ind]==1:
                            r2[ind+1:]=[0]*(len(df_small)-ind-1)
                            r2WS[ind+1:]=[0]*(len(df_small)-ind-1)
                        if r3[ind]==1:
                            r3[ind+1:]=[0]*(len(df_small)-ind-1)
                            r3WS[ind+1:]=[0]*(len(df_small)-ind-1)
                        if r4[ind]==1:
                            r4[ind+1:]=[0]*(len(df_small)-ind-1)
                            r4WS[ind+1:]=[0]*(len(df_small)-ind-1)
                    one_turn_1=0
                    two_turn_1=0
                    three_turn_1=0
                    four_turn_1=0
                    one_turn_2=0
                    two_turn_2=0
                    three_turn_2=0
                    four_turn_2=0
                    one_turn_3=0
                    two_turn_3=0
                    three_turn_3=0
                    four_turn_3=0
                    j=0

                    while j<df_small["Time"].count() and r1[j] == 1:
                        one_turn_1+=1
                        j+=1
                    while j<df_small["Time"].count() and r2[j] == 1:
                        two_turn_1+=1
                        j+=1
                    while j<df_small["Time"].count() and r3[j] == 1:
                        three_turn_1+=1
                        j+=1
                    while j<df_small["Time"].count() and r4[j] == 1:
                        four_turn_1+=1
                        j+=1
                    while j<df_small["Time"].count() and r1[j] == 1:
                        one_turn_2+=1
                        j+=1
                    while j<df_small["Time"].count() and r2[j] == 1:
                        two_turn_2+=1
                        j+=1
                    while j<df_small["Time"].count() and r3[j] == 1:
                        three_turn_2+=1
                        j+=1
                    while j <df_small["Time"].count() and r4[j] == 1:
                        four_turn_2+=1
                        j+=1
                    while j <df_small["Time"].count() and r1[j] == 1:
                        one_turn_3+=1
                        j+=1
                    while j <df_small["Time"].count() and r2[j] == 1:
                        two_turn_3+=1
                        j+=1
                    while j<df_small["Time"].count() and r3[j] == 1:
                        three_turn_3+=1
                        j+=1
                    while j <df_small["Time"].count() and r4[j] == 1:
                        four_turn_3+=1
                        j+=1
                    first_turns=[one_turn_1,two_turn_1,three_turn_1,four_turn_1]
                    second_turns=[one_turn_2,two_turn_2,three_turn_2,four_turn_2]
                    third_turns=[one_turn_3,two_turn_3,three_turn_3,four_turn_3]
                    df_small["Rider1"]=r1
                    df_small["Rider2"]=r2
                    df_small["Rider3"]=r3
                    df_small["Rider4"]=r4
                    df_small["Speed_Diff"]=speed_diff
                    df_small["Rider1WS"]=r1WS*(df_small["Del_Speed"]+df_small["Speed_Diff"])
                    df_small["Rider2WS"]=r2WS*(df_small["Del_Speed"]+df_small["Speed_Diff"])
                    df_small["Rider3WS"]=r3WS*(df_small["Del_Speed"]+df_small["Speed_Diff"])
                    df_small["Rider4WS"]=r4WS*(df_small["Del_Speed"]+df_small["Speed_Diff"])


                    df_main = df_small.drop(columns=["Rider1","Rider2","Rider3","Rider4","Action","Speed_Diff","Rider1WS","Rider2WS","Rider3WS","Rider4WS"])
    #                     df_main
                    hl_splits=[]
                    hl_rider =[] 
                    hl_distance=[]
                    hl_del_speed=[]
                    for i in range(2,len(df_main["Split"]),2):
                        hl_splits.append(df_main["Split"][i]+df_main["Split"][i-1])
                        hl_rider.append(df_main["Front"][i])
                        hl_distance.append(df_main["Distance"][i])
                        if df_main["Del_Speed"][i]!=df_main["Avg_Speed"][i]:
                            hl_del_speed.append(df_main["Del_Speed"][i])
                        else:
                            hl_del_speed.append(125*3.6/(df_main["Split"][i]+df_main["Split"][i-1]))
                    df_gm=pd.DataFrame()
                    df_gm["Split"] = hl_splits
                    df_gm["Front"]=hl_rider
                    df_gm["Distance"]=hl_distance
                    df_gm["Avg_Speed"]=125*3.6/df_gm["Split"]
                    df_gm["Del_Speed"]=hl_del_speed
                    lap_splits=[]
                    for i in range(len(df_gm["Split"])):
                        if i % 2==0:
                            lap_splits.append("")
                        else:
                            lap_splits.append(round(df_gm["Split"][i]+df_gm["Split"][i-1],2))
                    df_gm["Lap_Split"]=lap_splits
                    


                with col_2:
                    c1sub,c2sub=st.columns(2)
                    with c1sub:
                        yaxis_min = st.number_input("Y-axis Minimum:", min_value=0.00, max_value=None,value=min(df_temp["Avg_Speed"][1:])-1,key=f"yaxis min{event_count}")
                    with c2sub:
                        yaxis_max = st.number_input("Y-axis Maximum:", min_value=min(df_temp["Avg_Speed"])-1, max_value=None,value=max(df_temp["Avg_Speed"])+1,key=f"yaxis max{event_count}")
                    average = df_small.Split.iloc[4:].mean()
                    fig = px.bar(df_temp, x='Distance', y='Avg_Speed',color=df_temp.Front,hover_data={'Split':':.2f', 'Avg_Speed':':.2f', 'Del_Speed':':.2f'})
                    fig.add_trace(go.Scatter(x=df_temp['Distance'][1:], y=df_temp['Del_Speed'][1:],mode='markers',name="Delivery Speed"))
                    fig.update_layout(
                    title={
                        'text': df_temp.Title.iloc[0],
                        'y':0.9,
                        'x':0.5,
                        'xanchor': 'center',
                        'yanchor': 'top',
                        'font':dict(size=25)})
                    av_speed=3.6*62.5/average
                    
                    
                    av_idx=1
                    below_av = df_small["Del_Speed"][av_idx]
                    above_av=below_av
                    while below_av <av_speed:
                        below_av=df_small["Del_Speed"][av_idx]
                        av_idx+=1
                    above_av=df_small["Del_Speed"][av_idx-1]
                    below_av=df_small["Del_Speed"][av_idx-2]
                    
                    
                    below_av_dist = df_small["Distance"][av_idx-2]
                    
                    if below_av==above_av:
                        av_speed_dist = below_av_dist
                    else:
                        av_speed_dist = below_av_dist + 62.5*(av_speed-below_av)/(above_av-below_av)
                    avg_speed_dists.extend([av_speed_dist for i in range(4)])
                    fig.add_hline(y=62.5*3.6/average, line_dash="dash",line_color="yellow",annotation_text="Avg after first lap = " +str(round(average*4,2)))
                    fig.add_vline(x=round(av_speed_dist,2), line_dash="dash",line_color="yellow",annotation_text=f"Avg speed at {round(av_speed_dist,2)}m")
                    yaxis_min = yaxis_min #min(df_temp["Avg_Speed"][1:])-1
                    yaxis_max = yaxis_max #max(df_temp["Avg_Speed"])+1
                    fig.update_layout(yaxis_range=[yaxis_min,yaxis_max])
                    st.header("Quarter lap split speed trace")
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    #Goldmine style Speed Trace
                    st.header("Goldmine style speed trace")
                    
                    fig_gm = px.bar(df_gm, x='Distance', y='Avg_Speed',text="Lap_Split",color=df_gm.Front,hover_data={'Split':':.2f', 'Avg_Speed':':.2f', 'Del_Speed':':.2f'})
                    
                    fig_gm.add_trace(go.Scatter(x=df_gm['Distance'][1:], y=df_gm['Del_Speed'][1:],mode='markers',name="Delivery Speed"))
                    fig_gm.update_layout(
                    title={
                        'text': df_temp.Title.iloc[0],
                        'y':0.9,
                        'x':0.5,
                        'xanchor': 'center',
                        'yanchor': 'top',
                        'font':dict(size=25)})
                    fig_gm.add_hline(y=62.5*3.6/average, line_dash="dash",line_color="yellow",annotation_text="Avg after first lap = " +str(round(average*4,2)))
                    fig_gm.add_vline(x=round(av_speed_dist,2), line_dash="dash",line_color="yellow",annotation_text=f"Avg speed at {round(av_speed_dist,2)}m")
                    fig_gm.update_layout(yaxis_range=[yaxis_min,yaxis_max])
                    fig_gm.update_traces(textfont_size=24, cliponaxis=False)
                    st.plotly_chart(fig_gm, use_container_width=True)
                    
                    
#                     average = df_small.Split.iloc[4:len(df_small)-1].mean()
#                     fig = px.bar(df_temp, x='Distance', y='Avg_Speed',color=df_temp.Front,hover_data=[df_temp.Split, df_temp.Avg_Speed,df_temp.Del_Speed])
#                     fig.add_trace(go.Scatter(x=df_temp['Distance'][1:], y=df_temp['Del_Speed'][1:],mode='markers',name="Delivery Speed"))
#                     fig.update_layout(
#                     title={
#                         'text': df_temp.Title.iloc[0],
#                         'y':0.9,
#                         'x':0.5,
#                         'xanchor': 'center',
#                         'yanchor': 'top',
#                         'font':dict(size=25)})
#                     fig.add_hline(y=62.5*3.6/average, line_dash="dash",line_color="yellow",annotation_text="Avg after first lap = " +str(round(average*4,2)))
                    
#                     yaxis_min = min(df_temp["Avg_Speed"][1:])-1
#                     yaxis_max = max(df_temp["Avg_Speed"])+1
#                     fig.update_layout(yaxis_range=[yaxis_min,yaxis_max])
#                     st.plotly_chart(fig, use_container_width=True)
                    
#                 c1,c2=st.columns(2)
                with col_1:

                    st.header(df_temp["Title"].iloc[0])
                    df_small
                    unq_riders = df_small["Front"].unique()
                    df_summ=pd.DataFrame(unq_riders)
                    df_summ.columns=["Rider"]
                    df_summ=df_summ.dropna(axis=0)
                    front=[]
                    front.append(len(df_small.loc[df_small['Front'] == df_summ["Rider"][0]]))
                    front.append(len(df_small.loc[df_small['Front'] == df_summ["Rider"][1]]))
                    front.append(len(df_small.loc[df_small['Front'] == df_summ["Rider"][2]]))
                    front.append(len(df_small.loc[df_small['Front'] == df_summ["Rider"][3]]))
                    wind_scores = []
                    df_small['Rider1WS'].fillna(0)
                    wind_scores.append(round(sum(df_small['Rider1WS'].fillna(0),1)))
                    wind_scores.append(round(sum(df_small['Rider2WS'].fillna(0),1)))
                    wind_scores.append(round(sum(df_small['Rider3WS'].fillna(0),1)))
                    wind_scores.append(round(sum(df_small['Rider4WS'].fillna(0),1)))
                    df_summ["Front"]=front
                    df_summ["Turn_1"]=first_turns
                    df_summ["Turn_2"]=second_turns
                    df_summ["Turn_3"]=third_turns
                    df_summ["Wind_Score"] = wind_scores
                    # df_summ["Event_Count"]=count
                    
                    # Calculating Splits based off delivery speeds - 900 is a conversion factor
                    avg_splits=[round(900/(df_small[4:].loc[df_small["Front"] ==unq_riders[0]]["Del_Speed"].mean()),2), round(900/df_small[4:].loc[df_small["Front"] ==unq_riders[1]]["Del_Speed"].mean(),2),round(900/df_small[4:].loc[df_small["Front"] ==unq_riders[2]]["Del_Speed"].mean(),2),round(900/df_small[4:len(df_small)-1].loc[df_small["Front"] ==unq_riders[3]]["Del_Speed"].mean(),2)]
                    df_summ["Avg_Del_Split"]=avg_splits
                    
                    st.subheader("Rider Info")
                    
                    speed_var=[df_small[4:len(df_small)-1].loc[df_small["Front"] ==unq_riders[0]]["Del_Speed"].max()-df_small[4:len(df_small)-1].loc[df_small["Front"] ==unq_riders[0]]["Del_Speed"].min(),df_small[4:len(df_small)-1].loc[df_small["Front"] ==unq_riders[1]]["Del_Speed"].max()-df_small[4:len(df_small)-1].loc[df_small["Front"] ==unq_riders[1]]["Del_Speed"].min(),df_small[4:len(df_small)-1].loc[df_small["Front"] ==unq_riders[2]]["Del_Speed"].max()-df_small[4:len(df_small)-1].loc[df_small["Front"] ==unq_riders[2]]["Del_Speed"].min(),df_small[4:len(df_small)-1].loc[df_small["Front"] ==unq_riders[3]]["Del_Speed"].max()-df_small[4:len(df_small)-1].loc[df_small["Front"] ==unq_riders[3]]["Del_Speed"].min()]
                    df_summ["Speed_Var"]=speed_var
                    st.write("Wind score is a measure of exposure. In each quarter lap split, WS is calculated as WS = Summ [df(delivery_speed + speed_change)]")
                    st.write("Delivery_speed is the speed assuming no positional change, speed_change is the difference in delivery speeds between intervals, and df is 'drag feel' - the portion of drag felt by a rider in a train, compared to a solo rider.")
                    st.write("Current values for df are 0.971, 0.612, 0.495, 0.459 for lead, 2nd, 3rd and 4th riders respectively in a 4 person train, and 0.972, 0.617, 0.517 for lead, 2nd and 3rd riders in a 3 person chain.")
                    st.write("We then sum all values to get the Wind_Score shown below:")

                    df_summ
                    
                                 
                    st.subheader("Start Splits")
                    df_start=pd.DataFrame(df_small["Distance"][0:4])
                    df_start["Split"]=df_small["Split"][0:4]
                    df_start["Total"]=df_small["Split"][0:4].cumsum()
                    df_start
                    
                    
                    st.subheader("Lap Splits")
                    df_laps=pd.DataFrame(["Lap 1","Lap 2","Lap 3","Lap 4","Lap 5","Lap 6","Lap 7","Lap 8","Lap 9","Lap 10","Lap 11","Lap 12","Lap 13","Lap 14","Lap 15","Lap 16",])
                    df_laps.columns=["Distance"]
                    lap_split = [sum(df_small["Split"][0:4]),sum(df_small["Split"][4:8]),sum(df_small["Split"][8:12]),sum(df_small["Split"][12:16]),sum(df_small["Split"][16:20]),sum(df_small["Split"][20:24]),sum(df_small["Split"][24:28]),sum(df_small["Split"][28:32]),sum(df_small["Split"][32:36]),sum(df_small["Split"][36:40]),sum(df_small["Split"][40:44]),sum(df_small["Split"][44:48]),sum(df_small["Split"][48:52]),sum(df_small["Split"][52:56]),sum(df_small["Split"][56:60]),sum(df_small["Split"][60:64])]
                    df_laps["Split"]=lap_split
                    df_laps["Total"]=df_laps["Split"].cumsum()
                    df_laps['Total'] = pd.to_datetime(df_laps['Total'], unit='s').dt.strftime('%M:%S.%f')
                    df_laps['Diff from avg']=(average*4)-df_laps["Split"]
                    
                    laps_done = (df_laps["Split"].gt(12)).sum()
                    consistency = sum(abs(df_laps["Diff from avg"][1:laps_done]))
                    
                    df_laps
                    
                    
                    st.subheader("Kilo Splits")
                    df_kilos=pd.DataFrame(["1k","2k","3k","4k"])
                    df_kilos.columns=["Distance"]
                    kilo_split = [sum(df_small["Split"][0:16]),sum(df_small["Split"][16:32]),sum(df_small["Split"][32:48]),sum(df_small["Split"][48:64])]
                    df_kilos["Split"]=kilo_split
                    df_kilos["Total"]=df_kilos["Split"].cumsum()
                    df_kilos['Total'] = pd.to_datetime(df_kilos['Total'], unit='s').dt.strftime('%M:%S.%f')
                    df_kilos
                    df_summ
                    df_summ_full = df_summ
                    
                    df_summ_full.insert(1,"Event",df_temp["Title"].iloc[0])
                    # df_summ_full = df_summ_full.query(
                    #     "Event == @selections"
                    #     )
                    total_wind=df_summ_full['Wind_Score'].sum()
                    df_summ_full.insert(7,"Wind_Share_%",100*df_summ_full["Wind_Score"]/total_wind)
                    #df_summ_full["Wind_Share_%"]=100*df_summ_full["Wind_Score"]/total_wind
                    df_summ_full["Team_consistency"]=round(consistency,2)
                    df_summ_full.insert(1,"Position",[1,2,3,4])
                    df_summ_full.insert(3,"Time",df_kilos['Total'][3])
                    df_summ_full["62.5"]=round(df_small["Split"][0],3)
                    df_summ_full["125"]=round(df_start["Total"][1],3)
                    df_summ_full["187.5"]=round(df_start["Total"][2],3)
                    df_summ_full["250"]=round(df_start["Total"][3],3)
                    df_summ_full["1k"]=round(df_kilos["Split"][0],3)
                    df_summ_full["2k"]=round(df_kilos["Split"][1],3)
                    df_summ_full["3k"]=round(df_kilos["Split"][2],3)
                    df_summ_full["4k"]=round(df_kilos["Split"][3],3)
                    avg_del_split=df_summ_full['Avg_Del_Split'].mean()
                    df_summ_full.insert(11,"Avg_Del_Split_%",round(100*df_summ_full["Avg_Del_Split"]/avg_del_split,2))
                    df_summ_full["Date"]=df_summ_full["Event"].str[:8]
                    

                # df_start["Split"]=df_small["Split"][0:4]
                #     df_start["Total"]=df_small["Split"][0:4].cumsum()
                with col_2:
                    st.subheader(f"Consistency score is {round(consistency,2)}")
                    st.write("Sum of the absolute difference of lap splits from the average post first lap, pre last quarter (smaller is better).")
                    if Videos == "Yes":
                    
                    
                    
                        if pd.isnull(df_temp["Video"].iloc[0]):
                            st.header("No video available")
                        else:
                            video_name = df_temp["Video"].iloc[0]
                            st.header(df_temp["Title"].iloc[0])
           
                            st.video(f"{video_name}")
                st.markdown("---")
                
                
            
                if count == 0:
                    df_full_summary = pd.DataFrame()
                    df_full_summary=df_summ_full
                else:
                    df_full_summary = pd.concat([df_full_summary, df_summ_full], ignore_index=True)
            # df_full_summary.sort_values("Event_Count",ascending=True)
            st.header("Full Summary")
            df_full_summary["Dist_to_avg_speed"]=avg_speed_dists
            df_full_summary
            buffer = io.BytesIO()



            @st.cache_data
            def convert_to_csv(df_full_summary):
                # IMPORTANT: Cache the conversion to prevent computation on every rerun
                return df_full_summary.to_csv(index=False).encode('utf-8')

            csv = convert_to_csv(df_full_summary)

            # display the dataframe on streamlit app
    #         st.write(df)

            # download button 1 to download dataframe as csv
            download1 = st.download_button(
                label="Download Summary as CSV",
                data=csv,
                file_name='TP_Summary_Women.csv',
                mime='text/csv'
            )

            # download button 2 to download dataframe as xlsx
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                # Write each dataframe to a different worksheet.
                df_full_summary.to_excel(writer, sheet_name='Sheet1', index=False)
                # Close the Pandas Excel writer and output the Excel file to the buffer
                writer.close()

                download2 = st.download_button(
                    label="Download Summary as Excel",
                    data=buffer,
                    file_name='TP_Summary_Women.xlsx',
                    mime='application/vnd.ms-excel'
                ) 
            c1,c2=st.columns(2)
            with c1:
                variable = st.selectbox(
                'Select variable to compare:',
                    df_full_summary.columns[4:]
                )
            with c2:
                show_event = st.selectbox(
                'Show event names?',
                    ["No","Yes"]
                )

            df_full_summary["Date"]=df_full_summary["Event"].str[0:8]
            df_full_summary=df_full_summary.sort_values(by="Date")
            df_full_summary["EventName"]=df_full_summary["Event"].str[9:]
            if show_event == "Yes":
                fig_summary = px.line(df_full_summary, x="Date", color="Rider",y=f'{variable}',markers=True,text="EventName",hover_data=["EventName"])
            else:
                fig_summary = px.line(df_full_summary, x=df_full_summary["Date"], color="Rider",y=f'{variable}',markers=True,hover_data=["EventName"] )
        
            # x_ax=df_full_summary.sort_values("Event_Count",ascending=True)["Event"]
            # fig_summary = px.line(df_full_summary, x="Event_Count", y=f'{variable}',color="Rider",markers=True)
            # # fig_summary.update_xaxes(type='category')
            # fig_summary.update_xaxes(categoryorder='category ascending')
            st.plotly_chart(fig_summary, use_container_width=True)
            st.markdown("---")
                



            col_one, col_two, col_three, col_four = st.columns(4)
            with col_one:
                show_names = ["No","Yes"]
                Names = st.selectbox("Show Athlete Names?", show_names, key="Show_Names")
                df_combine["Initial"]=df_combine["Front"].str.replace('[^A-Z]', '')

            if Names == "Yes":
                fig_tt = px.line(df_combine, x="Distance", y = "Del_Speed", title="Comparison",color="Title",text="Initial",markers="Front")
                fig_tt.update_traces(textposition='top center')
            else:
                fig_tt = px.line(df_combine, x="Distance", y = "Del_Speed", title="Comparison",color="Title",markers="Front")

            st.plotly_chart(fig_tt, use_container_width=True)

#             if len(selections) ==2:

#                 df_zero = df_combine
#                 df_zero = df_zero.reset_index(drop=True)
#                 length = df_zero.Title.value_counts()[selections[0]]
#                 for j in range(length,len(selections)*length):
#                     df_zero.Split[j]=df_zero.Split[j]-df_zero.Split[j-length]
#                     df_zero.Split[j-length]=0



#                 if Names == "Yes":
#                     fig_zero = px.line(df_zero, x="Distance", y = "Split", title="Zero",color="Title",text="Initial",markers="Front")
#                     fig_zero.update_traces(textposition='top center')
#                 else:
#                     fig_zero = px.line(df_zero, x="Distance", y = "Split", title="Zero",color="Title",markers="Front")
#                 st.plotly_chart(fig_zero, use_container_width=True)
#                 if Names=="Yes":
#                     fig_worm = px.line(df_zero, x="Distance", y = "Time", title="Worm",color="Title",text="Initial",markers="Front")
#                     fig_worm.update_traces(textposition='top center')
#                 if Names=="No":
#                     fig_worm = px.line(df_zero, x="Distance", y = "Time", title="Worm",color="Title",markers="Front")

#                 st.plotly_chart(fig_worm, use_container_width=True)

#             elif len(selections) >2:

#                 df_zero = df_combine
#                 df_zero = df_zero.reset_index(drop=True)
#                 length = df_zero.Title.value_counts()[selections[0]]
#                 for j in range(length,len(selections)*length):
#                     df_zero.Split[j]=df_zero.Split[j]-df_zero.Split[j-length]
#                     df_zero.Split[j-length]=0




#                 if Names=="Yes":
#                     fig_worm = px.line(df_zero, x="Distance", y = "Time", title="Worm",color="Title",text="Front",markers="Front")
#                     fig_worm.update_traces(textposition='top center')
#                 if Names=="No":
#                     fig_worm = px.line(df_zero, x="Distance", y = "Time", title="Worm",color="Title",markers="Front")

#                 st.plotly_chart(fig_worm, use_container_width=True)






        st.markdown("---")            
        st.header('View, edit and upload a new effort')

        with open('pages/TP_demo.xlsx', "rb") as template_file:
                template_byte = template_file.read()



        st.download_button(label="Click to Download Template File",
                            data=template_byte,
                            file_name="template.xlsx"
                          )

        uploaded_file = st.file_uploader("Choose a file",key="uploader")

        if uploaded_file is not None:
            st.markdown("---")

            st.header("Editor")
            df_full = pd.read_csv(uploaded_file)
            df_full=df_full.sort_values(by=["Start time"]).reset_index(drop=True)
            df_full.drop(['Timeline','Duration','Instance number','Ungrouped','Notes','Flags'],
          axis='columns', inplace=True)
            df_full
            c1,c2,c3=st.columns(3)
            with c1:
                start=st.number_input("Start Row (inclusive)", value=0)
            with c2:
                end=st.number_input("End Row (inclusive)", value=start+64)+1
            
            
            df=df_full[start:end]
            df=df.sort_values("Start time", ascending=True)
            col_one, col_two, col_three = st.columns(3)
            with col_one:
                rider1 = st.text_input("Select Rider 1:")
                rider2 = st.text_input("Select Rider 2:")
                rider3 = st.text_input("Select Rider 3:")
                rider4 = st.text_input("Select Rider 4:")
            riders=[rider1,rider2,rider3,rider4]*10
            #riders
            df["Avg_Speed"]=0
            df["Del_Speed"]=0
            df["Split"]=0
            df["Front"]="HOLDER"
            front=[rider1]
            splits=[0]
            del_speeds=[0]
            speeds=[0]
            r=0
            df["Time"] = df["Start time"] - df["Start time"].iloc[0]
            markers = len(df)
            df["Distance"] = np.linspace(0, 62.5*(markers-1), num=markers)
            
            df=df.reset_index(drop=True)
            
            

            #df = df.dropna(axis=0, subset=['Time'])

            with col_two:
                offset = st.number_input("Offset:", min_value=0.00, max_value=None,value=0.12)
                schedule = round(st.number_input("Schedule:", min_value=0.00, max_value=None,value=14.3),2)
                Title = st.text_input("Plot Title:")


            with col_three:
                num_riders=4
                dropped=''
                #df
                rider_ind=0
                for i in range(1,len(df)):
                    df["Split"][i]=df["Time"][i]-df["Time"][i-1]
                    df["Avg_Speed"][i] = 62.5*3.6/(df["Split"][i])
                    if df["Row"][i] == "Change" or df["Row"][i] == "Drop":
                        df["Del_Speed"][i]=round(df["Avg_Speed"][i]*df["Split"][i]/(df["Split"][i]-offset),2)
                    else:
                        df["Del_Speed"][i]=df["Avg_Speed"][i]
                    if df["Row"][i]=="Drop":
                        df["Front"][i]=riders[rider_ind]
                        dropped=df["Front"][i]
                        rider_ind+=1
                    elif df["Row"][i]=="Change":
                        df["Front"][i]=riders[rider_ind]
                        rider_ind+=1
                        if riders[rider_ind] == dropped:
                            rider_ind+=1
                    else:
                        df["Front"][i]=riders[rider_ind]
                        
                  
                df.drop('Start time',
          axis='columns', inplace=True)
                df.rename(columns = {'Row':'Action'}, inplace = True)
                df.drop(index=df.index[0], axis=0, inplace=True)
                #df = df.dropna(axis=0, subset=['Time'])
                st.write("final df")
                df


            fig = px.bar(df, x='Distance', y='Avg_Speed',color=df.Front,hover_data=[df.Split, df.Avg_Speed,df.Del_Speed])
            fig.add_trace(go.Scatter(x=df['Distance'][1:], y=df['Del_Speed'][1:],mode='markers',name="Delivery Speed"))
            fig.update_layout(
            title={
                'text': Title,
                'y':0.9,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top',
                'font':dict(size=25)})
            fig.add_hline(y=250*3.6/schedule, line_dash="dash",line_color="white",annotation_text="Schedule = " +str(schedule))
            st.plotly_chart(fig, use_container_width=True)






            #master_path=st.text_input("Add path to master file:",key="prompt")
            if st.button("Append this effort to master",key="upload"):




                df_save=df
                df_save.insert(0, 'Save_Date', datetime.date.today())
                df_save["Save_Date"] = pd.to_datetime(df_save['Save_Date'])
                df_save.insert(0, 'Title', Title)
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
                    file_name='TP_Master_Women.csv',
                    mime='text/csv'
                )

                # download button 2 to download dataframe as xlsx
                with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                    # Write each dataframe to a different worksheet.
                    df.to_excel(writer, sheet_name='Sheet1', index=False)
                    # Close the Pandas Excel writer and output the Excel file to the buffer
                    writer.close()

                    download2 = st.download_button(
                        label="Download new Master as Excel",
                        data=buffer,
                        file_name='TP_Master_Women.xlsx',
                        mime='application/vnd.ms-excel'
                    )  
                    
                    
   ###################################################### Men's Team Pursuit #############################################                 
                    
    if racetype == "Men's TP":
        df_master = pd.read_excel(f'pages/video_analysis/TP_Master_Men.xlsx')
        df_master = df_master.sort_values(by=["Sort_name","Distance"], ascending=[False,True])
        df_small = df_master.drop(columns=["Save_Date","Action","Video","Sort_date","Sort_letter"])
#         df_small
        c1,c2,c3=st.columns(3)
        with c1:
            ath_filt = st.multiselect(
    'Filter athletes? Leave blank to see all rides',["Aaron Gate","Campbell Stewart","Dan Bridgwater","George Jackson","Keegan Hornblow","Nick Kergozou","Tom Sexton"]
    )
            st.markdown("[Jump to Full Summary](#full-summary)", unsafe_allow_html=True)
        with c2:
            if len(ath_filt)>0:
                
                options=[]
                for race in df_small["Title"].unique():
                    for name in ath_filt:
                        #st.write(df_small["Front"].loc[df_small["Title"]==race].unique())
                        if name in df_small["Front"].loc[df_small["Title"]==race].unique():
                            #st.write(df_small["Front"].loc[df_small["Title"]==race])
                            options.append(race)
                selections = st.multiselect(
                "Select past effort(s):",
                options=options  #.sort_values(ascending=False)
                ) 
            else:
                selections = st.multiselect(
                "Select past effort(s):",
                options=df_master["Title"].unique()  #.sort_values(ascending=False)
                ) 
        with c3:
            show_vids = ["No","Yes"]
            Videos = st.selectbox("Show Race Videos?", show_vids, key="Show_Vids")

        st.markdown("---")
        if len(selections) !=0:
            avg_speed_dists=[]
            df_combine = pd.DataFrame()
            for event_count in range(len(selections)):
                col_1,col_2=st.columns(2)
                with col_1:
                    
                    df_temp = df_master.loc[df_master['Title'] == selections[event_count]]
                    st.header(df_temp["Title"].iloc[0])
                    df_combine = pd.concat([df_combine, df_temp], axis=0)
                    df_small = df_temp.drop(columns=["Save_Date","Video","Sort_name","Sort_date","Sort_letter"])
                    df_small=df_small.reset_index(drop="True")
                    r1 = [1]
                    r2 = [2]
                    r3 = [3]
                    r4 = [4]
                    r1WS = [0.971]
                    r2WS = [0.612]
                    r3WS = [0.495]
                    r4WS = [0.459]
                    speed_diff=[df_small["Del_Speed"][0]]

                    no_riders=4
                    drag_feel = [0,0.971,0.612,0.495,0.459]
                    for j in range(1,len(df_small)):
                        speed_diff.append(df_small["Del_Speed"][j]-df_small["Del_Speed"][j-1])
                        if df_small["Action"][j-1] == "Change":
                            r1.append(r1[j-1]-1)
                            r2.append(r2[j-1]-1)
                            r3.append(r3[j-1]-1)
                            r4.append(r4[j-1]-1)
                        elif df_small["Action"][j-1] == "Drop":
                            no_riders = 3
                            drag_feel = [0,0.972,0.617,0.517]
                            r1.append(r1[j-1]-1)
                            r2.append(r2[j-1]-1)
                            r3.append(r3[j-1]-1)
                            r4.append(r4[j-1]-1)
                        else:
                            r1.append(r1[j-1])
                            r2.append(r2[j-1])
                            r3.append(r3[j-1])
                            r4.append(r4[j-1])
                        if r1[j]==0:
                            r1[j]=no_riders
                        if r2[j]==0:
                            r2[j]=no_riders
                        if r3[j]==0:
                            r3[j]=no_riders
                        if r4[j]==0:
                            r4[j]=no_riders
                        r1WS.append(drag_feel[r1[j]])
                        r2WS.append(drag_feel[r2[j]])
                        r3WS.append(drag_feel[r3[j]])
                        r4WS.append(drag_feel[r4[j]])
                    if "Drop" in df_small["Action"].unique():        
                        ind = df_small.index[df_small['Action'] == "Drop"][0]

                        if r1[ind]==1:
                            r1[ind+1:]=[0]*(len(df_small)-ind-1)
                            r1WS[ind+1:]=[0]*(len(df_small)-ind-1)
                        if r2[ind]==1:
                            r2[ind+1:]=[0]*(len(df_small)-ind-1)
                            r2WS[ind+1:]=[0]*(len(df_small)-ind-1)
                        if r3[ind]==1:
                            r3[ind+1:]=[0]*(len(df_small)-ind-1)
                            r3WS[ind+1:]=[0]*(len(df_small)-ind-1)
                        if r4[ind]==1:
                            r4[ind+1:]=[0]*(len(df_small)-ind-1)
                            r4WS[ind+1:]=[0]*(len(df_small)-ind-1)
                    one_turn_1=0
                    two_turn_1=0
                    three_turn_1=0
                    four_turn_1=0
                    one_turn_2=0
                    two_turn_2=0
                    three_turn_2=0
                    four_turn_2=0
                    one_turn_3=0
                    two_turn_3=0
                    three_turn_3=0
                    four_turn_3=0
                    j=0

                    while j<len(df_small) and r1[j] == 1:
                        one_turn_1+=1
                        j+=1
                    while j<len(df_small) and r2[j] == 1:
                        two_turn_1+=1
                        j+=1
                    while j<len(df_small) and r3[j] == 1:
                        three_turn_1+=1
                        j+=1
                    while j<len(df_small) and r4[j] == 1:
                        four_turn_1+=1
                        j+=1
                    while j<len(df_small) and r1[j] == 1:
                        one_turn_2+=1
                        j+=1
                    while j<len(df_small) and r2[j] == 1:
                        two_turn_2+=1
                        j+=1
                    while j<len(df_small) and r3[j] == 1:
                        three_turn_2+=1
                        j+=1
                    while j <len(df_small) and r4[j] == 1:
                        four_turn_2+=1
                        j+=1
                    while j <len(df_small) and r1[j] == 1:
                        one_turn_3+=1
                        j+=1
                    while j <len(df_small) and r2[j] == 1:
                        two_turn_3+=1
                        j+=1
                    while j<len(df_small) and r3[j] == 1:
                        three_turn_3+=1
                        j+=1
                    while j <len(df_small) and r4[j] == 1:
                        four_turn_3+=1
                        j+=1
                    first_turns=[one_turn_1,two_turn_1,three_turn_1,four_turn_1]
                    second_turns=[one_turn_2,two_turn_2,three_turn_2,four_turn_2]
                    third_turns=[one_turn_3,two_turn_3,three_turn_3,four_turn_3]
                    df_small["Rider1"]=r1
                    df_small["Rider2"]=r2
                    df_small["Rider3"]=r3
                    df_small["Rider4"]=r4
                    df_small["Speed_Diff"]=speed_diff
                    df_small["Rider1WS"]=r1WS*(df_small["Del_Speed"]+df_small["Speed_Diff"])
                    df_small["Rider2WS"]=r2WS*(df_small["Del_Speed"]+df_small["Speed_Diff"])
                    df_small["Rider3WS"]=r3WS*(df_small["Del_Speed"]+df_small["Speed_Diff"])
                    df_small["Rider4WS"]=r4WS*(df_small["Del_Speed"]+df_small["Speed_Diff"])

                    df_small
                    df_main = df_small.drop(columns=["Rider1","Rider2","Rider3","Rider4","Action","Speed_Diff","Rider1WS","Rider2WS","Rider3WS","Rider4WS"])
                    
                    
                    hl_splits=[]
                    hl_rider =[] 
                    hl_distance=[]
                    hl_del_speed=[]
                    for i in range(2,len(df_main["Split"]),2):
                        hl_splits.append(df_main["Split"][i]+df_main["Split"][i-1])
                        hl_rider.append(df_main["Front"][i])
                        hl_distance.append(df_main["Distance"][i])
                        if df_main["Del_Speed"][i]!=df_main["Avg_Speed"][i]:
                            hl_del_speed.append(df_main["Del_Speed"][i])
                        else:
                            hl_del_speed.append(125*3.6/(df_main["Split"][i]+df_main["Split"][i-1]))
                    df_gm=pd.DataFrame()
                    df_gm["Split"] = hl_splits
                    df_gm["Front"]=hl_rider
                    df_gm["Distance"]=hl_distance
                    df_gm["Avg_Speed"]=125*3.6/df_gm["Split"]
                    df_gm["Del_Speed"]=hl_del_speed
                    lap_splits=[]
                    for i in range(len(df_gm["Split"])):
                        if i % 2==0:
                            lap_splits.append("")
                        else:
                            lap_splits.append(round(df_gm["Split"][i]+df_gm["Split"][i-1],2))
                    df_gm["Lap_Split"]=lap_splits
    #                     df_gm
                   
                    
                with col_2:
                    c1sub,c2sub=st.columns(2)
                    with c1sub:
                        yaxis_min = st.number_input("Y-axis Minimum:", min_value=0.00, max_value=None,value=min(df_temp["Avg_Speed"][1:])-1)
                    with c2sub:
                        yaxis_max = st.number_input("Y-axis Maximum:", min_value=min(df_temp["Avg_Speed"])-1, max_value=None,value=max(df_temp["Avg_Speed"])+1)
                    average = df_small.Split.iloc[4:].mean()
                    fig = px.bar(df_temp, x='Distance', y='Avg_Speed',color=df_temp.Front,hover_data={'Split':':.2f', 'Avg_Speed':':.2f', 'Del_Speed':':.2f'})
                    fig.add_trace(go.Scatter(x=df_temp['Distance'][1:], y=df_temp['Del_Speed'][1:],mode='markers',name="Delivery Speed"))
                    fig.update_layout(
                    title={
                        'text': df_temp.Title.iloc[0],
                        'y':0.9,
                        'x':0.5,
                        'xanchor': 'center',
                        'yanchor': 'top',
                        'font':dict(size=25)})

                    av_speed=3.6*62.5/average
                    
                    
                    av_idx=1
                    below_av = df_small["Del_Speed"][av_idx]
                    above_av=below_av
                    while below_av <av_speed:
                        below_av=df_small["Del_Speed"][av_idx]
                        av_idx+=1
                    above_av=df_small["Del_Speed"][av_idx-1]
                    below_av=df_small["Del_Speed"][av_idx-2]
                    
                    
                    below_av_dist = df_small["Distance"][av_idx-2]
                    
                    if below_av==above_av:
                        av_speed_dist = below_av_dist
                    else:
                        av_speed_dist = below_av_dist + 62.5*(av_speed-below_av)/(above_av-below_av)
                    avg_speed_dists.extend([av_speed_dist for i in range(4)])
                    fig.add_vline(x=round(av_speed_dist,2), line_dash="dash",line_color="yellow",annotation_text=f"Avg speed at {round(av_speed_dist,2)}m")
                    fig.add_hline(y=62.5*3.6/average, line_dash="dash",line_color="yellow",annotation_text="Avg after first lap = " +str(round(average*4,2)))
                    yaxis_min = yaxis_min #min(df_temp["Avg_Speed"][1:])-1
                    yaxis_max = yaxis_max #max(df_temp["Avg_Speed"])+1
                    fig.update_layout(yaxis_range=[yaxis_min,yaxis_max])
                    st.plotly_chart(fig, use_container_width=True)
                    
                    #Goldmine style Speed Trace
                    st.header("Goldmine style speed trace")
                    
                    fig_gm = px.bar(df_gm, x='Distance', y='Avg_Speed',text="Lap_Split",color=df_gm.Front,hover_data={'Split':':.2f', 'Avg_Speed':':.2f'})
                    
                    fig_gm.add_trace(go.Scatter(x=df_gm['Distance'][1:], y=df_gm['Del_Speed'][1:],mode='markers',name="Delivery Speed"))
                    fig_gm.update_layout(
                    title={
                        'text': df_temp.Title.iloc[0],
                        'y':0.9,
                        'x':0.5,
                        'xanchor': 'center',
                        'yanchor': 'top',
                        'font':dict(size=25)})
                    fig_gm.add_vline(x=round(av_speed_dist,2), line_dash="dash",line_color="yellow",annotation_text=f"Avg speed at {round(av_speed_dist,2)}m")
                    fig_gm.add_hline(y=62.5*3.6/average, line_dash="dash",line_color="yellow",annotation_text="Avg after first lap = " +str(round(average*4,2)))
                    fig_gm.update_layout(yaxis_range=[yaxis_min,yaxis_max])
                    fig_gm.update_traces(textfont_size=24, cliponaxis=False)
                    st.plotly_chart(fig_gm, use_container_width=True)
                c1,c2=st.columns(2)
                with col_1:
                    #st.write("Wind score is a measure of exposure. In each quarter lap split, WS is calculated as WS = Summ [df(delivery_speed + speed_change)]")
                    #st.write("Delivery_speed is the speed assuming no positional change, speed_change is the difference in delivery speeds between intervals, and df is 'drag feel' - the portion of drag felt by a rider in a train, compared to a solo rider.")
                    #st.write("Current values for df are 0.971, 0.612, 0.495, 0.459 for lead, 2nd, 3rd and 4th riders respectively in a 4 person train, and 0.972, 0.617, 0.517 for lead, 2nd and 3rd riders in a 3 person chain.")
                    #st.write("We then sum all values to get the Wind_Score shown below:")
                    
                    unq_riders = df_small["Front"].unique()
                    df_summ=pd.DataFrame(unq_riders)
                    df_summ.columns=["Rider"]
                    df_summ=df_summ.dropna(axis=0)
                    front=[]
                    front.append(len(df_small.loc[df_small['Front'] == df_summ["Rider"][0]]))
                    front.append(len(df_small.loc[df_small['Front'] == df_summ["Rider"][1]]))
                    front.append(len(df_small.loc[df_small['Front'] == df_summ["Rider"][2]]))
                    front.append(len(df_small.loc[df_small['Front'] == df_summ["Rider"][3]]))
                    wind_scores = []
                    df_small['Rider1WS'].fillna(0)
                    wind_scores.append(round(sum(df_small['Rider1WS'].fillna(0),1)))
                    wind_scores.append(round(sum(df_small['Rider2WS'].fillna(0),1)))
                    wind_scores.append(round(sum(df_small['Rider3WS'].fillna(0),1)))
                    wind_scores.append(round(sum(df_small['Rider4WS'].fillna(0),1)))
                    df_summ["Front"]=front
                    df_summ["Turn_1"]=first_turns
                    df_summ["Turn_2"]=second_turns
                    df_summ["Turn_3"]=third_turns
                    df_summ["Wind_Score"] = wind_scores
                    
                    # Calculating Splits based off delivery speeds - 900 is a conversion factor
                    avg_splits=[round(900/(df_small[4:].loc[df_small["Front"] ==unq_riders[0]]["Del_Speed"].mean()),2), round(900/df_small[4:].loc[df_small["Front"] ==unq_riders[1]]["Del_Speed"].mean(),2),round(900/df_small[4:].loc[df_small["Front"] ==unq_riders[2]]["Del_Speed"].mean(),2),round(900/df_small[4:len(df_small)-1].loc[df_small["Front"] ==unq_riders[3]]["Del_Speed"].mean(),2)]
                    df_summ["Avg_Del_Split"]=avg_splits
                    
                    
                    speed_var=[df_small[4:].loc[df_small["Front"] ==unq_riders[0]]["Del_Speed"].max()-df_small[4:len(df_small)-1].loc[df_small["Front"] ==unq_riders[0]]["Del_Speed"].min(),df_small[4:len(df_small)-1].loc[df_small["Front"] ==unq_riders[1]]["Del_Speed"].max()-df_small[4:len(df_small)-1].loc[df_small["Front"] ==unq_riders[1]]["Del_Speed"].min(),df_small[4:len(df_small)-1].loc[df_small["Front"] ==unq_riders[2]]["Del_Speed"].max()-df_small[4:len(df_small)-1].loc[df_small["Front"] ==unq_riders[2]]["Del_Speed"].min(),df_small[4:len(df_small)-1].loc[df_small["Front"] ==unq_riders[3]]["Del_Speed"].max()-df_small[4:len(df_small)-1].loc[df_small["Front"] ==unq_riders[3]]["Del_Speed"].min()]
                    df_summ["Speed_Var"]=speed_var
                    
                    
                    st.subheader("Rider Info")
                    df_summ
                    st.subheader("Start Splits")
                    df_start=pd.DataFrame(df_small["Distance"][0:4])
                    df_start["Split"]=df_small["Split"][0:4]
                    df_start["Total"]=df_small["Split"][0:4].cumsum()
                    df_start
                    
                    st.subheader("Lap Splits")
                    df_laps=pd.DataFrame(["Lap 1","Lap 2","Lap 3","Lap 4","Lap 5","Lap 6","Lap 7","Lap 8","Lap 9","Lap 10","Lap 11","Lap 12","Lap 13","Lap 14","Lap 15","Lap 16",])
                    df_laps.columns=["Distance"]
                    lap_split = [sum(df_small["Split"][0:4]),sum(df_small["Split"][4:8]),sum(df_small["Split"][8:12]),sum(df_small["Split"][12:16]),sum(df_small["Split"][16:20]),sum(df_small["Split"][20:24]),sum(df_small["Split"][24:28]),sum(df_small["Split"][28:32]),sum(df_small["Split"][32:36]),sum(df_small["Split"][36:40]),sum(df_small["Split"][40:44]),sum(df_small["Split"][44:48]),sum(df_small["Split"][48:52]),sum(df_small["Split"][52:56]),sum(df_small["Split"][56:60]),sum(df_small["Split"][60:64])]
                    df_laps["Split"]=lap_split
                    df_laps["Total"]=df_laps["Split"].cumsum()
                    df_laps['Total'] = pd.to_datetime(df_laps['Total'], unit='s').dt.strftime('%M:%S.%f')
                    
                    laps_done = (df_laps["Split"].gt(12)).sum()
                    
                    df_laps['Diff from avg']=(average*4)-df_laps["Split"]
                    consistency = sum(abs(df_laps["Diff from avg"][1:laps_done]))
                    
                    
                    df_laps
                    
                    st.subheader("Kilo Splits")
                    df_kilos=pd.DataFrame(["1k","2k","3k","4k"])
                    df_kilos.columns=["Distance"]
                    kilo_split = [sum(df_small["Split"][0:16]),sum(df_small["Split"][16:32]),sum(df_small["Split"][32:48]),sum(df_small["Split"][48:64])]
                    df_kilos["Split"]=kilo_split
                    df_kilos["Total"]=df_kilos["Split"].cumsum()
                    df_kilos['Total'] = pd.to_datetime(df_kilos['Total'], unit='s').dt.strftime('%M:%S.%f')
                    df_kilos
                    df_summ_full = df_summ
                    df_summ_full.insert(1,"Event",df_temp["Title"].iloc[0])
                    total_wind=df_summ_full['Wind_Score'].sum()
                    df_summ_full.insert(7,"Wind_Share_%",100*df_summ_full["Wind_Score"]/total_wind)
                    #df_summ_full["Wind_Share_%"]=100*df_summ_full["Wind_Score"]/total_wind
                    df_summ_full["Team_consistency"]=round(consistency,2)
                    df_summ_full.insert(1,"Position",[1,2,3,4])
                    df_summ_full.insert(3,"Time",df_kilos['Total'][3])
                    df_summ_full["62.5"]=round(df_small["Split"][0],3)
                    df_summ_full["125"]=round(df_start["Total"][1],3)
                    df_summ_full["187.5"]=round(df_start["Total"][2],3)
                    df_summ_full["250"]=round(df_start["Total"][3],3)
                    df_summ_full["1k"]=round(df_kilos["Split"][0],3)
                    df_summ_full["2k"]=round(df_kilos["Split"][1],3)
                    df_summ_full["3k"]=round(df_kilos["Split"][2],3)
                    df_summ_full["4k"]=round(df_kilos["Split"][3],3)
                    
                    avg_del_split=df_summ_full['Avg_Del_Split'].mean()
                    df_summ_full.insert(11,"Avg_Del_Split_%",round(100*df_summ_full["Avg_Del_Split"]/avg_del_split,2))
                    
                with col_2:
                    st.subheader(f"Consistency score is {round(consistency,2)}")
                    st.write("Sum of the absolute difference of lap splits from the average post first lap, pre last quarter (smaller is better).")
                    if Videos == "Yes":

                        if pd.isnull(df_temp["Video"].iloc[0]):
                            st.header("No video available")
                        else:
                            video_name = df_temp["Video"].iloc[0]
                            st.header(df_temp["Title"].iloc[0])

                            st.video(f"{video_name}")
                st.markdown("---")
                
                
            
                if event_count == 0:
                    df_full_summary = pd.DataFrame()
                    df_full_summary=df_summ_full
                else:
                    df_full_summary = pd.concat([df_full_summary, df_summ_full], ignore_index=True)
            st.header("Full Summary")
            
            df_full_summary["Dist_to_avg_speed"]=avg_speed_dists
            df_full_summary
            
            buffer = io.BytesIO()



            @st.cache_data
            def convert_to_csv(df_full_summary):
                # IMPORTANT: Cache the conversion to prevent computation on every rerun
                return df_full_summary.to_csv(index=False).encode('utf-8')

            csv = convert_to_csv(df_full_summary)

            # display the dataframe on streamlit app
    #         st.write(df)

            # download button 1 to download dataframe as csv
            download1 = st.download_button(
                label="Download Summary as CSV",
                data=csv,
                file_name='TP_Summary_Men.csv',
                mime='text/csv'
            )

            # download button 2 to download dataframe as xlsx
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                # Write each dataframe to a different worksheet.
                df_full_summary.to_excel(writer, sheet_name='Sheet1', index=False)
                # Close the Pandas Excel writer and output the Excel file to the buffer
                writer.close()

                download2 = st.download_button(
                    label="Download Summary as Excel",
                    data=buffer,
                    file_name='TP_Summary_Men.xlsx',
                    mime='application/vnd.ms-excel'
                )  
            c1,c2=st.columns(2)
            with c1:
                variable = st.selectbox(
                'Select variable to compare:',
                    df_full_summary.columns[4:]
                )
            with c2:
                show_event = st.selectbox(
                'Display event name?',
                    ["No","Yes"]
                )   

            # riders=df_full_summary["Rider"].unique()
            # events = df_full_summary["Event"].unique()
            # riders2=[]
            # for idx,event in enumerate(events):
            #     df_temp = df_full_summary.loc[df_full_summary["Event"]==event].reset_index(drop=True)
            #     df_temp
            #     for rider in riders:
            #         for i
            #         if df_temp.Rider.isin([riders]):
            #             riders2.append(rider)
            # riders2
                

            




            ##Horrific code snippet
            
            # df_var_summ=pd.DataFrame()
            # df_event_unq=pd.DataFrame()
            # df_var_summ["Rider"]=df_full_summary["Rider"].unique()
            # df_var_summ = pd.DataFrame(np.repeat(df_var_summ.values, len(df_full_summary["Event"].unique()), axis=0))
            # df_var_summ.rename(columns={ df_var_summ.columns[0]: "Rider" }, inplace = True)
            # events=[]
            # count=0
            # for i in range(len(df_var_summ)):
            #     events.append(df_full_summary["Event"].unique()[count])
            #     count+=1
            #     if count==len(df_full_summary["Event"].unique()):
            #         count=0
            # var_score=[]
            # df_var_summ["Event"]=events
            # df_var_summ
            # for i in range(len(df_var_summ)):
            #     rider = df_var_summ["Rider"][i]
            #     event = df_var_summ["Event"][i]
            #     df_temp=df_full_summary.loc[df_full_summary["Event"]==event]
            #     if rider in df_temp["Rider"].unique():
            #         df_temp
            #         ind = df_temp['Rider'].loc[lambda x: x==True].index
            #         id
            #         var_score.append(df_temp[f'{variable}'][ind])
            #     else:
            #         var_score.append(None)
            # df_var_summ[f"{variable}"]=var_score
            # df_var_summ






            
            df_full_summary["Date"]=df_full_summary["Event"].str[0:8]
            df_full_summary=df_full_summary.sort_values(by="Date")
            df_full_summary["EventName"]=df_full_summary["Event"].str[9:]
            
            
            if show_event == "Yes":
                fig_summary = px.line(df_full_summary, x="Date", color="Rider",y=f'{variable}',markers=True,text="EventName",hover_data=["EventName"])
            else:
                fig_summary = px.line(df_full_summary, x=df_full_summary["Date"], color="Rider",y=f'{variable}',markers=True,hover_data=["EventName"] )
            #for event in df_full_summary["Event"].unique():
        
            # fig_gm.add_trace(go.Scatter(x=df_gm['Distance'][1:], y=df_gm['Del_Speed'][1:],mode='markers',name="Delivery Speed"))
            # fig_gm.update_layout(
            # title={
            #     'text': df_temp.Title.iloc[0],
            #     'y':0.9,
            #     'x':0.5,
            #     'xanchor': 'center',
            #     'yanchor': 'top',
            #     'font':dict(size=25)})
            # fig_gm.add_hline(y=62.5*3.6/average, line_dash="dash",line_color="yellow",annotation_text="Avg after first lap = " +str(round(average*4,2)))
            # fig_gm.update_layout(yaxis_range=[yaxis_min,yaxis_max])
            # fig_gm.update_traces(textfont_size=24, cliponaxis=False)
            
            st.plotly_chart(fig_summary, use_container_width=True)
            st.markdown("---")



            col_one, col_two, col_three, col_four = st.columns(4)
            with col_one:
                show_names = ["No","Yes"]
                Names = st.selectbox("Show Athlete Names?", show_names, key="Show_Names")
                df_combine["Initial"]=df_combine["Front"].str.replace('[^A-Z]', '')
            
            if Names == "Yes":
                fig_tt = px.line(df_combine, x="Distance", y = "Del_Speed", title="Comparison",color="Title",text="Initial",markers="Front")
                fig_tt.update_traces(textposition='top center')
            else:
                fig_tt = px.line(df_combine, x="Distance", y = "Del_Speed", title="Comparison",color="Title",markers="Front")

            st.plotly_chart(fig_tt, use_container_width=True)
            







        st.markdown("---")            
        st.header('View, edit and upload a new effort')

        with open('pages/TP_demo.xlsx', "rb") as template_file:
                template_byte = template_file.read()



        st.download_button(label="Click to Download Template File",
                            data=template_byte,
                            file_name="template.xlsx"
                          )

        uploaded_file = st.file_uploader("Choose a file",key="uploader")

        if uploaded_file is not None:
            st.markdown("---")

            st.header("Editor")
            
            df_full = pd.read_csv(uploaded_file)
            df_full=df_full.sort_values(by=["Start time"]).reset_index(drop=True)
            df_full.drop(['Timeline','Duration','Instance number','Ungrouped','Notes','Flags'],
          axis='columns', inplace=True)
            df_full
            c1,c2,c3=st.columns(3)
            with c1:
                start=st.number_input("Start Row (inclusive)", value=0)
            with c2:
                end=st.number_input("End Row (inclusive)", value=start+64)+1
            
            
            df=df_full[start:end]
            df=df.sort_values("Start time", ascending=True)
            
            col_one, col_two, col_three = st.columns(3)
            with col_one:
                rider1 = st.text_input("Select Rider 1:")
                rider2 = st.text_input("Select Rider 2:")
                rider3 = st.text_input("Select Rider 3:")
                rider4 = st.text_input("Select Rider 4:")
            riders=[rider1,rider2,rider3,rider4]*10
            #riders
            df["Avg_Speed"]=0
            df["Del_Speed"]=0
            df["Split"]=0
            df["Front"]="HOLDER"
            front=[rider1]
            splits=[0]
            del_speeds=[0]
            speeds=[0]
            r=0
            df["Time"] = df["Start time"] - df["Start time"].iloc[0]
            markers = len(df)
            df["Distance"] = np.linspace(0, 62.5*(markers-1), num=markers)
            df=df.reset_index(drop=True)

            st.write("original df")
            df

            #df = df.dropna(axis=0, subset=['Time'])

            with col_two:
                offset = st.number_input("Offset:", min_value=0.00, max_value=None,value=0.12)
                schedule = round(st.number_input("Schedule:", min_value=0.00, max_value=None,value=14.3),2)
                Title = st.text_input("Plot Title:")


            with col_three:
                num_riders=4
                dropped=''
                #df
                rider_ind=0
                for i in range(1,len(df)):
                    df["Split"][i]=df["Time"][i]-df["Time"][i-1]
                    df["Avg_Speed"][i] = 62.5*3.6/(df["Split"][i])
                    if df["Row"][i] == "Change" or df["Row"][i] == "Drop":
                        df["Del_Speed"][i]=round(df["Avg_Speed"][i]*df["Split"][i]/(df["Split"][i]-offset),2)
                    else:
                        df["Del_Speed"][i]=df["Avg_Speed"][i]
                    if df["Row"][i]=="Drop":
                        df["Front"][i]=riders[rider_ind]
                        dropped=df["Front"][i]
                        rider_ind+=1
                    elif df["Row"][i]=="Change":
                        df["Front"][i]=riders[rider_ind]
                        rider_ind+=1
                        if riders[rider_ind] == dropped:
                            rider_ind+=1
                    else:
                        df["Front"][i]=riders[rider_ind]
                        
                  
                df.drop('Start time',
          axis='columns', inplace=True)
                df.rename(columns = {'Row':'Action'}, inplace = True)
                df.drop(index=df.index[0], axis=0, inplace=True)
                #df = df.dropna(axis=0, subset=['Time'])
                
                df


            fig = px.bar(df, x='Distance', y='Avg_Speed',color=df.Front,hover_data=[df.Split, df.Avg_Speed,df.Del_Speed])
            fig.add_trace(go.Scatter(x=df['Distance'][1:], y=df['Del_Speed'][1:],mode='markers',name="Delivery Speed"))
            fig.update_layout(
            title={
                'text': Title,
                'y':0.9,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top',
                'font':dict(size=25)})
            fig.add_hline(y=250*3.6/schedule, line_dash="dash",line_color="white",annotation_text="Schedule = " +str(schedule))
            st.plotly_chart(fig, use_container_width=True)






            #master_path=st.text_input("Add path to master file:",key="prompt")
            if st.button("Append this effort to master",key="upload"):




                df_save=df
                df_save.insert(0, 'Save_Date', datetime.date.today())
                df_save["Save_Date"] = pd.to_datetime(df_save['Save_Date'])
                df_save.insert(0, 'Title', Title)
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
                    file_name='TP_Master_Men.csv',
                    mime='text/csv'
                )

                # download button 2 to download dataframe as xlsx
                with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                    # Write each dataframe to a different worksheet.
                    df.to_excel(writer, sheet_name='Sheet1', index=False)
                    # Close the Pandas Excel writer and output the Excel file to the buffer
                    writer.close()

                    download2 = st.download_button(
                        label="Download new Master as Excel",
                        data=buffer,
                        file_name='TP_Master_Men.xlsx',
                        mime='application/vnd.ms-excel'
                    )                
                    
    ######################################## Men's Keirin ################################################################                
                    
    elif racetype == "Mens' Keirin":
        df_master = pd.read_csv(f'pages/video_analysis/Mens_Keirin.csv')
        
        #df_small = df_master.drop(columns=["Save_Date","Action","Video"])
        df_select = df_master
        c1,c2,c3,c4 = st.columns(4)
        with c1:
            
            event = st.selectbox(
            "Select Event(s):",
            options=df_master["Event"].unique()
            ) 
            if event:
                df_select = df_master.query(
            "Event == @event"
            )
        with c2:
            Round = st.selectbox(
            "Select Round(s):",
            options=df_select["Round"].unique()
            )
            if Round:
                df_select = df_select.query(
            "Round == @Round"
            )
        with c3:
            Heat = st.selectbox(
            "Select Heat(s):",
            options=df_select["Heat"].unique()
            )
            if Heat:
                df_select = df_select.query(
            "Heat == @Heat"
            )
        with c4:
            show_vids = ["No","Yes"]
            Videos = st.selectbox("Show Race Video?", show_vids, key="Show_Vids")
        df_select["Time"]=df_select["Start time"]-df_select["Start time"].iloc[0]
        df_select=df_select.drop(columns=["Start time"])
        #df_select    
        
        
        
        
        df_gaps = pd.DataFrame()
        df_gaps["To Go"] = ["3 Laps","2.5 Laps","2 Laps","1.5 Laps","1 Lap","0.5 Laps","15m"]
        
        for i in range(len(df_select["Name"].unique())):
            var = str(df_select["Name"].unique()[i])
           
            df_gaps[f"{var}"]=df_select.loc[df_select["Name"]==var]["Time"].values
        
        cols = len(df_gaps.columns)
        
        df_splits=pd.DataFrame()
        df_splits["Half"] = [1,2,3,4,5,6]
        for i in range(1,cols):
            x=[]
            for j in range(1,7):
                x.append(df_gaps[df_gaps.columns[i]][j]-df_gaps[df_gaps.columns[i]][j-1])
            df_splits[df_gaps.columns[i]] = x

        for i in range(1,7):
            small = df_gaps.loc[i][1:].min()
            
            for j in range(1,cols):
                df_gaps.loc[i,df_gaps.columns[j]]=df_gaps.loc[i,df_gaps.columns[j]]-small
     

        
        
        st.subheader("Time Gap to Leader") 
        c1,c2=st.columns([1,3])
        with c1:
            df_gaps 

        fig_tt = px.line(df_gaps, x="To Go", y = df_gaps.columns, title="Time Gap to Leader", markers=True,labels={"value":"Seconds"})
        with c2:
            st.plotly_chart(fig_tt, use_container_width=True)
        
        
        ###Splits
        
        
#         df_splits = pd.DataFrame()
#         df_splits["To Go"] = ["3 Laps","2.5 Laps","2 Laps","1.5 Laps","1 Lap","0.5 Laps","15m"]
#         df_splits
        
            
            
            
            
        
        st.subheader("Splits (Pursuit Lines)")
        c1,c2=st.columns([1,3])
        with c1:
            df_splits
            df_times = df_splits.sum(axis=0)
            df_times=pd.DataFrame(df_times, columns=["3 lap time"])
            df_times = df_times[1:]
            st.subheader("3 lap times")
            df_times
        fig_tt = px.line(df_splits, x="Half", y = df_splits.columns, title="Splits",markers=True,labels={"value":"Seconds"})
        with c2:
            st.plotly_chart(fig_tt, use_container_width=True)
        
        
        c1,c2=st.columns(2)
        if Videos=="Yes":
            video_name=df_select["Video"].iloc[0]
            with c2:
                st.video(f"{video_name}")
        with c1:
            
            len(df_select["Draw"].unique())
            
            
            
            
            ## Getting Position at each pursuit line
            s = df_gaps.iloc[:,1:].stack().sort_values(ascending=True).groupby(level=0).cumcount() + 1
            s1 = (s.reset_index(1)
                .set_index(0, append=True)
                .unstack(1)
                .add_prefix("Position ")
                )
            s1.columns = s1.columns.get_level_values(1)
            
            
            df_gaps=df_gaps.join(s1)
            
            num_riders = len(s1.columns)
            
            for j in range(num_riders):
                name=df_select["Name"].unique()[j]
                
                
                
                
                rider_pos=[]
                
                for i in range(len(df_gaps)):
                    n = df_gaps.iloc[:,num_riders+1:].iloc[i]
                    pos=n[n==name].index[0]
                    to_go = df_gaps["To Go"][i]
                    gap = round(df_gaps[name][i],2)
                    rider_pos.append(int(pos.split(' ')[1]))
                df_gaps[f'{name} rank'] = rider_pos
            df_gaps = df_gaps.iloc[:,num_riders+1:]
            df_gaps
            

            
            
        
        st.markdown("---")
        st.header("Rider Analysis")
        df_riders=df_master
        c1,c2=st.columns([5,1])
        with c1:
            athletes = df_master["Name"].drop_duplicates().sort_values()
            riders = st.multiselect(
                "Select rider(s):",
                options= athletes
                ) 
        with c2:
            show_vids_2 = ["No","Yes"]
            Videos_2 = st.selectbox("Show Race Video?", show_vids_2, key="Show_Vids_2")
        if riders:
            df_riders = df_master.query(
        "Name == @riders"
        )
        
            df_riders=df_riders.sort_values(by=["Name","Start time"])
            df_riders=df_riders.reset_index(drop=True)
            df_riders["Initials"]=df_riders["Name"].apply(lambda x: ''.join(i[0] for i in x.split()))
            #df_riders

    #         for Name in df_riders["Name"].unique():
    #             for Event in df_riders.loc[df_riders["Name"]==Name]["Event"].unique():
    #                 for Round in df_riders.loc[(df_riders["Name"]==Name)]["Round"].unique():
    #                     for Heat in df_riders.loc[df_riders["Name"]==Name]["Heat"].unique():
    #                         st.write(Name+" "+Event+" "+Round+" "+str(Heat))
            tags=[]

            Name=df_riders["Name"][0]
            Event=df_riders["Event"][0]
            Round=df_riders["Round"][0]
            Heat=df_riders["Heat"][0]

            tags.append(df_riders["Initials"][0]+" "+df_riders["Event"][0]+" "+df_riders["Round"][0]+" H"+str(df_riders["Heat"][0]))
            count=0
            tag_count=0
            start=df_riders["Start time"][0]
            videos=[df_riders["Video"][0]]
            times=[df_riders["Start time"][0]-start]
            df_worm=pd.DataFrame()
            df_worm["To Go"]=["3 Laps","2.5 Laps","2 Laps","1.5 Laps","1 Lap","0.5 Laps","15m"]
            for i in range(1,len(df_riders)):
                if count<6:
                    times.append(df_riders["Start time"][i]-start)
                    count+=1
                else:
                    tags.append(df_riders["Initials"][i]+" "+df_riders["Event"][i]+" "+df_riders["Round"][i]+" H"+str(df_riders["Heat"][i]))

                    df_worm[tags[tag_count]]=times
                    count=0
                    tag_count+=1
                    times=[]
                    start = df_riders["Start time"][i]
                    times.append(df_riders["Start time"][i]-start)
                    videos.append(df_riders["Video"][i])
            df_worm[tags[tag_count]]=times

            df_worm
            
            fig_worm = px.line(df_worm, x="To Go", y = df_worm.columns, title="Worms",markers=True,labels={"value":"Seconds"})

            st.plotly_chart(fig_worm, use_container_width=True)




            df_split=pd.DataFrame()
            df_split["Half"] = [1,2,3,4,5,6]

            for col in df_worm.columns[1:]:
                x=[]
                for i in range(1,7):
                    x.append(df_worm[col][i]-df_worm[col][i-1])
                df_split[col]=x
                    
            df_split
            
            
            fig_splits = px.line(df_split, x="Half", y = df_split.columns, title="Splits",markers=True,labels={"value":"Seconds"})

            st.plotly_chart(fig_splits, use_container_width=True)
            
            if Videos_2=="Yes":
                count=0
                for i in range(len(videos)):
                    c1,c2=st.columns([1,2])
                    with c1:
                        st.subheader(df_riders["Name"][count])
                        st.subheader(df_riders["Event"][count]+" "+df_riders["Round"][count]+" H"+str(df_riders["Heat"][count]))
                        st.subheader("Half Lap Splits")
                        df_split[["Half",df_split.columns[i+1]]]
                        st.subheader("Running Time")
                        df_worm[["To Go",df_worm.columns[i+1]]]
                        count+=7
                        
                    with c2:
                        video_name=videos[i]
                        st.video(f"{video_name}")
                    st.markdown('---')
                            
                        
                    
                        
        


        #####################################   WTS Starts stuff   #############################################################
            
    elif racetype == "WTS Starts":
        df_master = pd.read_excel(f'pages/video_analysis/WTS_starts.xlsx')
        for i in range(len(df_master)):
            df_master["Date"][i] = df_master["Date"][i].date()
        df_small = df_master.drop(columns=["Back","Forward","Green","PL",62.5,125,187.5,250,312.5,375,437.5,500])
        df_small
        c1,c2,c3=st.columns(3)
        
        with c1:
            riders = st.multiselect(
            "Select rider(s):",
            options=df_master["Name"].unique()
            ) 
            if riders:
                df_small = df_small.query(
            "Name == @riders"
            )
        with c2:
            dates = st.multiselect(
            "Select date(s):",
            options=df_small["Date"].unique()
            )
            if dates:
                df_small = df_small.query(
            "Date == @dates"
            )
        with c3:
            show_vids = ["No","Yes"]
            Videos = st.selectbox("Show Race Videos?", show_vids, key="Show_Vids")


        if len(riders) !=0:
            df_combine = pd.DataFrame()
            for i in range(len(riders)):
                col_1,col_2=st.columns(2)
                with col_1:
                    df_temp = df_small.loc[df_master['Name'] == riders[i]]
                    df_combine = pd.concat([df_combine, df_temp], axis=0)
                    
                    #df_small=df_small.reset_index(drop="True")
            df_combine = df_combine.reset_index(drop="True")
            
            df_combine
            
            df_splits = pd.DataFrame()
            df_splits["Mark"] = ["RT","Q1","Q2","Q3","Q4","Q5","Q6","Q7","Q8"]
            for i in range(len(df_combine)):
                var = str(i+1)+" " +str(df_combine["Name"].iloc[i]) + " " + str(df_combine["Date"].iloc[i]) + " Set " +str(df_combine["Set"].iloc[i])+" Rep " +str(df_combine["Rep"].iloc[i]) + " " +str(df_combine["Team/Solo"].iloc[i])
                df_splits[f"{var}"]=df_combine.iloc[i][8:17].values

            
            fig_tt = px.line(df_splits, x="Mark", y = df_splits.columns, title="Reaction Time + Quarter Splits")

            st.plotly_chart(fig_tt, use_container_width=True)
            #c1,c2=st.columns(2)
            
            if Videos == "Yes":
                for i in range(len(df_combine)):
                    if pd.isnull(df_combine["Video"].iloc[i]):
                        pass
                    else:
                        c1,c2=st.columns(2)
                        video_name = df_combine["Video"].iloc[i]
                        with c1:
                            st.header(df_combine["Name"].iloc[i])
                            st.subheader(df_combine["Date"].iloc[i])
                            st.subheader("Set "+str(df_combine["Set"].iloc[i])+ ", Rep " +str(df_combine["Rep"].iloc[i]))
                            st.subheader(df_combine["Team/Solo"].iloc[i])
                            st.subheader("Position "+str(df_combine["Pos"].iloc[i]))
                            st.subheader("Gear "+str(df_combine["Gear"].iloc[i]))
                            st.write("Reaction Time = "+str(round(df_combine["RT"].iloc[i],3)) + " Seconds")
                            st.write("First Quarter in = "+str(round(df_combine["Q1"].iloc[i],3)) + " Seconds, with a Moving Time of "+str(round(df_combine["Q1_MT"].iloc[i],3)) + " Seconds")
                            if pd.isnull(df_combine["Q2"].iloc[i])==False:
                                st.write("Second Quarter in = "+str(round(df_combine["Q2"].iloc[i],3)) + " Seconds, giving a split of "+str(round(df_combine["H1"].iloc[i],3))+" with a Moving Time of "+str(round(df_combine["H1_MT"].iloc[i],3)) + " Seconds")
                            if pd.isnull(df_combine["Q3"].iloc[i])==False:
                                st.write("Third Quarter in = "+str(round(df_combine["Q3"].iloc[i],3)) + " Seconds")
                            if pd.isnull(df_combine["Q4"].iloc[i])==False:
                                st.write("Fourth Quarter in = "+str(round(df_combine["Q4"].iloc[i],3)) + " Seconds, giving a split of "+str(round(df_combine["H2"].iloc[i],3))+" with a Moving Time of "+str(round(df_combine["Lap_MT"].iloc[i],3)) + " Seconds")
                                

                        with c2:
                            st.video(f"{video_name}")
                        st.markdown("---")





###################################################### Men's Individual Pursuit #############################################                 
                    
    if racetype == "Men's IP":
        df_master = pd.read_excel(f'pages/video_analysis/IP_Master_Men.xlsx')
        df_master = df_master.sort_values(["Save_Date","Title"], ascending=False)
        df_small = df_master.drop(columns=["Save_Date","Action","Video"])
        df_small
        c1,c2=st.columns(2)
        with c1:
            selections = st.multiselect(
            "Select past effort(s):",
            options=df_master["Title"].unique()
            ) 
        with c2:
            show_vids = ["No","Yes"]
            Videos = st.selectbox("Show Race Videos?", show_vids, key="Show_Vids")


        if len(selections) !=0:
            df_combine = pd.DataFrame()
            for i in range(len(selections)):
                col_1,col_2=st.columns(2)
                with col_1:
                    df_temp = df_master.loc[df_master['Title'] == selections[i]]
                    df_combine = pd.concat([df_combine, df_temp], axis=0)
                    df_small = df_temp.drop(columns=["Save_Date","Video"])
                    df_small=df_small.reset_index(drop="True")
                  
                       
                        


                    df_main = df_small.drop(columns=["Action"])
                    df_main
                with col_2:
                    average = df_small.Split.iloc[4:].mean()
                    fig = px.bar(df_temp, x='Distance', y='Avg_Speed',hover_data=[df_temp.Split, df_temp.Avg_Speed])
                    
                    fig.update_layout(
                    title={
                        'text': df_temp.Title.iloc[0],
                        'y':0.9,
                        'x':0.5,
                        'xanchor': 'center',
                        'yanchor': 'top',
                        'font':dict(size=25)})
                    fig.add_hline(y=62.5*3.6/average, line_dash="dash",line_color="yellow",annotation_text="Avg after first lap = " +str(round(average*4,2)))
                    yaxis_min = min(df_temp["Avg_Speed"][1:])-1
                    yaxis_max = max(df_temp["Avg_Speed"])+1
                    fig.update_layout(yaxis_range=[yaxis_min,yaxis_max])
                    st.plotly_chart(fig, use_container_width=True)
                c1,c2=st.columns(2)
                with c1:

                    
                    
                    st.subheader("Start Splits")
                    df_start=pd.DataFrame(df_small["Distance"][0:4])
                    df_start["Split"]=df_small["Split"][0:4]
                    df_start["Total"]=df_small["Split"][0:4].cumsum()
                    df_start
                    
                    st.subheader("Lap Splits")
                    df_laps=pd.DataFrame(["Lap 1","Lap 2","Lap 3","Lap 4","Lap 5","Lap 6","Lap 7","Lap 8","Lap 9","Lap 10","Lap 11","Lap 12","Lap 13","Lap 14","Lap 15","Lap 16",])
                    df_laps.columns=["Distance"]
                    lap_split = [sum(df_small["Split"][0:4]),sum(df_small["Split"][4:8]),sum(df_small["Split"][8:12]),sum(df_small["Split"][12:16]),sum(df_small["Split"][16:20]),sum(df_small["Split"][20:24]),sum(df_small["Split"][24:28]),sum(df_small["Split"][28:32]),sum(df_small["Split"][32:36]),sum(df_small["Split"][36:40]),sum(df_small["Split"][40:44]),sum(df_small["Split"][44:48]),sum(df_small["Split"][48:52]),sum(df_small["Split"][52:56]),sum(df_small["Split"][56:60]),sum(df_small["Split"][60:64])]
                    df_laps["Split"]=lap_split
                    df_laps["Total"]=df_laps["Split"].cumsum()
                    df_laps['Total'] = pd.to_datetime(df_laps['Total'], unit='s').dt.strftime('%M:%S.%f')
                    df_laps
                    
                    st.subheader("Kilo Splits")
                    df_kilos=pd.DataFrame(["1k","2k","3k","4k"])
                    df_kilos.columns=["Distance"]
                    kilo_split = [sum(df_small["Split"][0:16]),sum(df_small["Split"][16:32]),sum(df_small["Split"][32:48]),sum(df_small["Split"][48:64])]
                    df_kilos["Split"]=kilo_split
                    df_kilos["Total"]=df_kilos["Split"].cumsum()
                    df_kilos['Total'] = pd.to_datetime(df_kilos['Total'], unit='s').dt.strftime('%M:%S.%f')
                    df_kilos
                if Videos == "Yes":
                    with c2:
                        if pd.isnull(df_temp["Video"].iloc[0]):
                            st.header("No video available")
                        else:
                            video_name = df_temp["Video"].iloc[0]
                            st.header(df_temp["Title"].iloc[0])
   
                            st.video(f"{video_name}")
                st.markdown("---")



            col_one, col_two, col_three, col_four = st.columns(4)
            
            with col_one:
           
                fig_tt = px.line(df_combine, x="Distance", y = "Avg_Speed", title="Comparison",color="Title",markers="Front")
                
            st.plotly_chart(fig_tt, use_container_width=True)

            if len(selections) ==2:

                df_zero = df_combine
                df_zero = df_zero.reset_index(drop=True)
                length = df_zero.Title.value_counts()[selections[0]]
                for j in range(length,len(selections)*length):
                    df_zero.Split[j]=df_zero.Split[j]-df_zero.Split[j-length]
                    df_zero.Split[j-length]=0



                fig_zero = px.line(df_zero, x="Distance", y = "Avg_Speed", title="Zero",color="Title",markers="Front")
                st.plotly_chart(fig_zero, use_container_width=True)
               
                fig_worm = px.line(df_zero, x="Distance", y = "Time", title="Worm",color="Title",markers="Front")

                st.plotly_chart(fig_worm, use_container_width=True)

            elif len(selections) >2:

                df_zero = df_combine
                df_zero = df_zero.reset_index(drop=True)
                length = df_zero.Title.value_counts()[selections[0]]
                for j in range(length,len(selections)*length):
                    df_zero.Split[j]=df_zero.Split[j]-df_zero.Split[j-length]
                    df_zero.Split[j-length]=0




                if Names=="Yes":
                    fig_worm = px.line(df_zero, x="Distance", y = "Time", title="Worm",color="Title",text="Front",markers="Front")
                    fig_worm.update_traces(textposition='top center')
                if Names=="No":
                    fig_worm = px.line(df_zero, x="Distance", y = "Time", title="Worm",color="Title",markers="Front")

                st.plotly_chart(fig_worm, use_container_width=True)






        st.markdown("---")            
        st.header('View, edit and upload a new effort')

        with open('pages/TP_demo.xlsx', "rb") as template_file:
                template_byte = template_file.read()



        st.download_button(label="Click to Download Template File",
                            data=template_byte,
                            file_name="template.xlsx"
                          )

        uploaded_file = st.file_uploader("Choose a file",key="uploader")

        if uploaded_file is not None:
            st.markdown("---")

            st.header("Editor")
            df_full = pd.read_csv(uploaded_file)
            df_full=df_full.sort_values(by=["Start time"]).reset_index(drop=True)
            df_full.drop(['Timeline','Duration','Instance number','Ungrouped','Notes','Flags','Distance','Effort Type'],
          axis='columns', inplace=True)
            df_full
            c1,c2,c3=st.columns(3)
            with c1:
                start=st.number_input("Start Row (inclusive)", value=0)
            with c2:
                end=st.number_input("End Row (inclusive)", value=start+64)+1
            
            
            df=df_full[start:end]
            df=df.sort_values("Start time", ascending=True)
            col_one, col_two, col_three = st.columns(3)
            with col_one:
                rider = st.text_input("Select Rider:")

            
            splits=[0]
            
            speeds=[0]
            r=0
            df["Time"] = df["Start time"] - df["Start time"].iloc[0]
            markers = len(df)
            df["Distance"] = np.linspace(0, 62.5*(markers-1), num=markers)
            df=df.reset_index(drop=True)
      

            #df = df.dropna(axis=0, subset=['Time'])

            with col_two:
                offset = st.number_input("Offset:", min_value=0.00, max_value=None,value=0.12)
                schedule = round(st.number_input("Schedule:", min_value=0.00, max_value=None,value=14.3),2)
                Title = st.text_input("Plot Title:")


            with col_three:
                
                for i in range(len(df)-1):
                    splits.append(round(df.Time[i+1]-df.Time[i],3))
                    speeds.append(round((df.Distance[i+1]-df.Distance[i])*3.6/splits[i+1],2))
                    

                df["Avg_Speed"]=speeds
                df["Split"]=splits
                df.drop('Start time',
          axis='columns', inplace=True)
                df.rename(columns = {'Row':'Action'}, inplace = True)
                df.drop(index=df.index[0], axis=0, inplace=True)
                #df = df.dropna(axis=0, subset=['Time'])
                st.write(df)


            fig = px.bar(df, x='Distance', y='Avg_Speed',hover_data=[df.Split, df.Avg_Speed])
   
            fig.update_layout(
            title={
                'text': Title,
                'y':0.9,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top',
                'font':dict(size=25)})
            fig.add_hline(y=250*3.6/schedule, line_dash="dash",line_color="white",annotation_text="Schedule = " +str(schedule))
            st.plotly_chart(fig, use_container_width=True)






            #master_path=st.text_input("Add path to master file:",key="prompt")
            if st.button("Append this effort to master",key="upload"):




                df_save=df
                df_save.insert(0, 'Save_Date', datetime.date.today())
                df_save["Save_Date"] = pd.to_datetime(df_save['Save_Date'])
                df_save.insert(0, 'Title', Title)
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
                    file_name='IP_Master_Men.csv',
                    mime='text/csv'
                )

                # download button 2 to download dataframe as xlsx
                with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                    # Write each dataframe to a different worksheet.
                    df.to_excel(writer, sheet_name='Sheet1', index=False)
                    # Close the Pandas Excel writer and output the Excel file to the buffer
                    writer.close()

                    download2 = st.download_button(
                        label="Download new Master as Excel",
                        data=buffer,
                        file_name='IP_Master_Men.xlsx',
                        mime='application/vnd.ms-excel'
                    )                
                    

           ###################################################### Women's Individual Pursuit #############################################                 
                    
    if racetype == "Women's IP":
        df_master = pd.read_excel(f'pages/video_analysis/IP_Master_Women.xlsx')
        df_master = df_master.sort_values(["Save_Date","Title"], ascending=False)
        df_small = df_master.drop(columns=["Save_Date","Action","Video"])
        df_small
        c1,c2=st.columns(2)
        with c1:
            selections = st.multiselect(
            "Select past effort(s):",
            options=df_master["Title"].unique()
            ) 
        with c2:
            show_vids = ["No","Yes"]
            Videos = st.selectbox("Show Race Videos?", show_vids, key="Show_Vids")


        if len(selections) !=0:
            df_combine = pd.DataFrame()
            for i in range(len(selections)):
                col_1,col_2=st.columns(2)
                with col_1:
                    df_temp = df_master.loc[df_master['Title'] == selections[i]]
                    df_combine = pd.concat([df_combine, df_temp], axis=0)
                    df_small = df_temp.drop(columns=["Save_Date","Video"])
                    df_small=df_small.reset_index(drop="True")
                  
                       
                        


                    df_main = df_small.drop(columns=["Action"])
                    df_main
                with col_2:
                    average = df_small.Split.iloc[4:].mean()
                    fig = px.bar(df_temp, x='Distance', y='Avg_Speed',hover_data=[df_temp.Split, df_temp.Avg_Speed])
                    
                    fig.update_layout(
                    title={
                        'text': df_temp.Title.iloc[0],
                        'y':0.9,
                        'x':0.5,
                        'xanchor': 'center',
                        'yanchor': 'top',
                        'font':dict(size=25)})
                    fig.add_hline(y=62.5*3.6/average, line_dash="dash",line_color="yellow",annotation_text="Avg after first lap = " +str(round(average*4,2)))
                    yaxis_min = min(df_temp["Avg_Speed"][1:])-1
                    yaxis_max = max(df_temp["Avg_Speed"])+1
                    fig.update_layout(yaxis_range=[yaxis_min,yaxis_max])
                    st.plotly_chart(fig, use_container_width=True)
                c1,c2=st.columns(2)
                with c1:

                    
                    
                    st.subheader("Start Splits")
                    df_start=pd.DataFrame(df_small["Distance"][0:4])
                    df_start["Split"]=df_small["Split"][0:4]
                    df_start["Total"]=df_small["Split"][0:4].cumsum()
                    df_start
                    
                    st.subheader("Lap Splits")
                    df_laps=pd.DataFrame(["Lap 1","Lap 2","Lap 3","Lap 4","Lap 5","Lap 6","Lap 7","Lap 8","Lap 9","Lap 10","Lap 11","Lap 12","Lap 13","Lap 14","Lap 15","Lap 16",])
                    df_laps.columns=["Distance"]
                    lap_split = [sum(df_small["Split"][0:4]),sum(df_small["Split"][4:8]),sum(df_small["Split"][8:12]),sum(df_small["Split"][12:16]),sum(df_small["Split"][16:20]),sum(df_small["Split"][20:24]),sum(df_small["Split"][24:28]),sum(df_small["Split"][28:32]),sum(df_small["Split"][32:36]),sum(df_small["Split"][36:40]),sum(df_small["Split"][40:44]),sum(df_small["Split"][44:48]),sum(df_small["Split"][48:52]),sum(df_small["Split"][52:56]),sum(df_small["Split"][56:60]),sum(df_small["Split"][60:64])]
                    df_laps["Split"]=lap_split
                    df_laps["Total"]=df_laps["Split"].cumsum()
                    df_laps['Total'] = pd.to_datetime(df_laps['Total'], unit='s').dt.strftime('%M:%S.%f')
                    df_laps
                    
                    st.subheader("Kilo Splits")
                    df_kilos=pd.DataFrame(["1k","2k","3k"])
                    df_kilos.columns=["Distance"]
                    kilo_split = [sum(df_small["Split"][0:16]),sum(df_small["Split"][16:32]),sum(df_small["Split"][32:48])]
                    df_kilos["Split"]=kilo_split
                    df_kilos["Total"]=df_kilos["Split"].cumsum()
                    df_kilos['Total'] = pd.to_datetime(df_kilos['Total'], unit='s').dt.strftime('%M:%S.%f')
                    df_kilos
                if Videos == "Yes":
                    with c2:
                        if pd.isnull(df_temp["Video"].iloc[0]):
                            st.header("No video available")
                        else:
                            video_name = df_temp["Video"].iloc[0]
                            st.header(df_temp["Title"].iloc[0])
   
                            st.video(f"{video_name}")
                st.markdown("---")



            col_one, col_two, col_three, col_four = st.columns(4)
            with col_one:
                
                fig_tt = px.line(df_combine, x="Distance", y = "Avg_Speed", title="Comparison",color="Title",markers="Front")

            st.plotly_chart(fig_tt, use_container_width=True)

            if len(selections) ==2:

                df_zero = df_combine
                df_zero = df_zero.reset_index(drop=True)
                length = df_zero.Title.value_counts()[selections[0]]
                for j in range(length,len(selections)*length):
                    df_zero.Split[j]=df_zero.Split[j]-df_zero.Split[j-length]
                    df_zero.Split[j-length]=0



                fig_zero = px.line(df_zero, x="Distance", y = "Split", title="Zero",color="Title",markers="Front")
                st.plotly_chart(fig_zero, use_container_width=True)
               
                fig_worm = px.line(df_zero, x="Distance", y = "Time", title="Worm",color="Title",markers="Front")

                st.plotly_chart(fig_worm, use_container_width=True)

            elif len(selections) >2:

                df_zero = df_combine
                df_zero = df_zero.reset_index(drop=True)
                length = df_zero.Title.value_counts()[selections[0]]
                for j in range(length,len(selections)*length):
                    df_zero.Split[j]=df_zero.Split[j]-df_zero.Split[j-length]
                    df_zero.Split[j-length]=0




                if Names=="Yes":
                    fig_worm = px.line(df_zero, x="Distance", y = "Time", title="Worm",color="Title",text="Front",markers="Front")
                    fig_worm.update_traces(textposition='top center')
                if Names=="No":
                    fig_worm = px.line(df_zero, x="Distance", y = "Time", title="Worm",color="Title",markers="Front")

                st.plotly_chart(fig_worm, use_container_width=True)






        st.markdown("---")            
        st.header('View, edit and upload a new effort')

        with open('pages/TP_demo.xlsx', "rb") as template_file:
                template_byte = template_file.read()



        st.download_button(label="Click to Download Template File",
                            data=template_byte,
                            file_name="template.xlsx"
                          )

        uploaded_file = st.file_uploader("Choose a file",key="uploader")

        if uploaded_file is not None:
            st.markdown("---")

            st.header("Editor")
            df_full = pd.read_csv(uploaded_file)
            df_full=df_full.sort_values(by=["Start time"]).reset_index(drop=True)
            df_full.drop(['Timeline','Duration','Instance number','Ungrouped','Notes','Flags','Distance','Effort Type'],
          axis='columns', inplace=True)
            df_full
            c1,c2,c3=st.columns(3)
            with c1:
                start=st.number_input("Start Row (inclusive)", value=0)
            with c2:
                end=st.number_input("End Row (inclusive)", value=start+64)+1
            
            
            df=df_full[start:end]
            df=df.sort_values("Start time", ascending=True)
            
            col_one, col_two, col_three = st.columns(3)
            with col_one:
                rider = st.text_input("Select Rider:")

            
            splits=[0]
            
            speeds=[0]
            r=0
            df["Time"] = df["Start time"] - df["Start time"].iloc[0]
            markers = len(df)
            df["Distance"] = np.linspace(0, 62.5*(markers-1), num=markers)
            df=df.reset_index(drop=True)
         

            #df = df.dropna(axis=0, subset=['Time'])

            with col_two:
                offset = st.number_input("Offset:", min_value=0.00, max_value=None,value=0.12)
                schedule = round(st.number_input("Schedule:", min_value=0.00, max_value=None,value=14.3),2)
                Title = st.text_input("Plot Title:")


            with col_three:
                
                for i in range(len(df)-1):
                    splits.append(round(df.Time[i+1]-df.Time[i],3))
                    speeds.append(round((df.Distance[i+1]-df.Distance[i])*3.6/splits[i+1],2))
                    

                df["Avg_Speed"]=speeds
                df["Split"]=splits
                df.drop('Start time',
          axis='columns', inplace=True)
                df.rename(columns = {'Row':'Action'}, inplace = True)
                df.drop(index=df.index[0], axis=0, inplace=True)
                #df = df.dropna(axis=0, subset=['Time'])
                st.write(df)


            fig = px.bar(df, x='Distance', y='Avg_Speed',hover_data=[df.Split, df.Avg_Speed])
   
            fig.update_layout(
            title={
                'text': Title,
                'y':0.9,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top',
                'font':dict(size=25)})
            fig.add_hline(y=250*3.6/schedule, line_dash="dash",line_color="white",annotation_text="Schedule = " +str(schedule))
            st.plotly_chart(fig, use_container_width=True)






            #master_path=st.text_input("Add path to master file:",key="prompt")
            if st.button("Append this effort to master",key="upload"):




                df_save=df
                df_save.insert(0, 'Save_Date', datetime.date.today())
                df_save["Save_Date"] = pd.to_datetime(df_save['Save_Date'])
                df_save.insert(0, 'Title', Title)
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
                    file_name='IP_Master_Women.csv',
                    mime='text/csv'
                )

                # download button 2 to download dataframe as xlsx
                with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                    # Write each dataframe to a different worksheet.
                    df.to_excel(writer, sheet_name='Sheet1', index=False)
                    # Close the Pandas Excel writer and output the Excel file to the buffer
                    writer.close()

                    download2 = st.download_button(
                        label="Download new Master as Excel",
                        data=buffer,
                        file_name='IP_Master_Women.xlsx',
                        mime='application/vnd.ms-excel'
                    )                
                    
    ################################################ Women's Team Sprint ##########################################################
    
    if racetype == "Women's Team Sprint":
        
        st.markdown("---")            
        df_master = pd.read_excel(f'pages/video_analysis/WTS_Master_Women.xlsx')
        #df_master = pd.read_excel("C:\\Users\\SamB\\CNZPD\\pages\\video_analysis\\WTS_Master_Women.xlsx")
        st.header("Race Viewer")
        c1,c2=st.columns(2)
        
        with c1:
            selections = st.multiselect(
            "Select past effort(s):",
            options=df_master["Title"].sort_values(ascending=False).unique()
            ) 
        with c2:
            show_vids = ["No","Yes"]
            Videos = st.selectbox("Show Race Videos?", show_vids, key="Show_Vids")
        if len(selections) !=0:
            st.markdown("[Jump to Full Summary](#summary)", unsafe_allow_html=True)
            df_combine = pd.DataFrame()
            for i in range(len(selections)):
                checkboxid+=1
                df_temp = df_master.loc[df_master['Title'] == selections[i]].reset_index(drop=True)
                
                
                df_table = pd.DataFrame([1,2,3],columns=["Position"])
                df_table.insert(0,"Event",df_temp["Title"][0:3])
                df_table["Rider"]=df_temp["Riders"][0:3]
                df_table["Gear"]=df_temp["Gears"][0:3]
                
                ind1=df_temp.index[df_temp['Row'] == "Rider 1 Forward"].tolist()[0]
                ind2=df_temp.index[df_temp['Row'] == "Rider 2 Forward"].tolist()[0]
                ind3=df_temp.index[df_temp['Row'] == "Rider 3 Forward"].tolist()[0]
                indstart=df_temp.index[df_temp['Row'] == "Start"].tolist()[0]
                start = df_temp["Start time"][indstart]
                react1 = round(df_temp["Start time"][ind1]-start,2)
                react2 = round(df_temp["Start time"][ind2]-start,2)
                react3 = round(df_temp["Start time"][ind3]-start,2)
                
                
                df_table["RT"]=[react1,react2,react3]
                df_table["62.5"]=[df_temp["Start time"][4]-start,df_temp["Start time"][5]-start,df_temp["Start time"][6]-start]
                
                df_table["125"]=[df_temp["Start time"][7]-df_temp["Start time"][4],df_temp["Start time"][8]-df_temp["Start time"][5],df_temp["Start time"][9]-df_temp["Start time"][6]]
                
                df_table["187.5"]=[df_temp["Start time"][10]-df_temp["Start time"][7],df_temp["Start time"][11]-df_temp["Start time"][8],df_temp["Start time"][12]-df_temp["Start time"][9]]
                
                df_table["250"]=[df_temp["Start time"][13]-df_temp["Start time"][10],df_temp["Start time"][14]-df_temp["Start time"][11],df_temp["Start time"][15]-df_temp["Start time"][12]]
                df_table["Lap 1"]=[df_temp["Start time"][13]-start,df_temp["Start time"][14]-start,df_temp["Start time"][15]-start]
                
                
                df_table["Gap 1"]= [0.0,df_table["Lap 1"][1]-df_table["Lap 1"][0],df_table["Lap 1"][2]-df_table["Lap 1"][1]]
                
                df_table["312.5"]=[0,df_temp["Start time"][16]-df_temp["Start time"][14],df_temp["Start time"][17]-df_temp["Start time"][15]]
                
                df_table["375"]=[0,df_temp["Start time"][18]-df_temp["Start time"][16],df_temp["Start time"][19]-df_temp["Start time"][17]]
                
                df_table["437.5"]=[0,df_temp["Start time"][20]-df_temp["Start time"][18],df_temp["Start time"][21]-df_temp["Start time"][19]]
                
                df_table["500"]=[0,df_temp["Start time"][22]-df_temp["Start time"][20],df_temp["Start time"][23]-df_temp["Start time"][21]]
                df_table["Lap 2"]=[0,df_temp["Start time"][22]-df_temp["Start time"][14],df_temp["Start time"][23]-df_temp["Start time"][15]]
                df_table["500m Time"] = [0,df_table["Lap 1"][1]+df_table["Lap 2"][1],df_table["Lap 1"][2]+df_table["Lap 2"][2]]
                df_table["Gap 2"]= [0,0,df_table["Lap 2"][2]-df_table["Lap 2"][1] + df_table["Gap 1"][2]]
                
                df_table["562.5"] = [0,0,df_temp["Start time"][24]-df_temp["Start time"][23]]
                df_table["625"] = [0,0,df_temp["Start time"][25]-df_temp["Start time"][24]]
                df_table["687.5"] = [0,0,df_temp["Start time"][26]-df_temp["Start time"][25]]
                df_table["750"] = [0,0,df_temp["Start time"][27]-df_temp["Start time"][26]]
                
                df_table["Lap 3"] = [0,0,df_temp["Start time"][27]-df_temp["Start time"][23]]
                df_table["1"] = [df_table["Lap 1"][0],0,0]
                df_table["2"] = [0,df_table["Lap 2"][1]+df_table["Gap 1"][1],0]
                df_table["3"] = [0,0,df_table["Lap 3"][2]+df_table["Gap 2"][2]]
                df_table["Time"] = [0,0,df_temp["Start time"][27]-start]
                st.header(selections[i])
                df_table
                
                gap1_2_1 = round(df_table["62.5"][1]-df_table["62.5"][0],2)
                gap1_2_2 = round(df_table["125"][1]-df_table["125"][0] + gap1_2_1,2)
                gap1_2_3 = round(df_table["187.5"][1]-df_table["187.5"][0] + gap1_2_2,2)
                gap1_2_4 = round(df_table["250"][1]-df_table["250"][0] + gap1_2_3,2)
                
                gap2_3_1 = round(df_table["62.5"][2]-df_table["62.5"][1],2)
                gap2_3_2 = round(df_table["125"][2]-df_table["125"][1]+gap2_3_1,2)
                gap2_3_3 = round(df_table["187.5"][2]-df_table["187.5"][1]+gap2_3_2,2)
                gap2_3_4 = round(df_table["250"][2]-df_table["250"][1]+gap2_3_3,2)
                gap2_3_5 = round(df_table["312.5"][2]-df_table["312.5"][1]+gap2_3_4,2)
                gap2_3_6 = round(df_table["375"][2]-df_table["375"][1]+gap2_3_5,2)
                gap2_3_7 = round(df_table["437.5"][2]-df_table["437.5"][1]+gap2_3_6,2)
                gap2_3_8 = round(df_table["500"][2]-df_table["500"][1]+gap2_3_7,2)
                
                gaps1_2=[gap1_2_1,gap1_2_2,gap1_2_3,gap1_2_4,0,0,0,0]
                gaps2_3=[gap2_3_1,gap2_3_2,gap2_3_3,gap2_3_4,gap2_3_5,gap2_3_6,gap2_3_7,gap2_3_8]
                df_gap = pd.DataFrame(gaps1_2)
                df_gap.rename(columns={ df_gap.columns[0]: "Gap1_2" }, inplace = True)
                df_gap["Gap2_3"]=gaps2_3
                
              
            
                f1 = go.Figure(
                data = [
                    go.Scatter(y=gaps1_2[0:4], x=["Q1","Q2","Q3","Q4"], name="Rider 2 to 1"),
                    go.Scatter(x=["Q1","Q2","Q3","Q4","Q5","Q6","Q7","Q8"], y=gaps2_3, name="Rider 3 to 2"),
                ],
                layout = {"xaxis": {"title": "Quarters"}, "yaxis": {"title": "Seconds"}, "title": "Gaps by Quarter"}
                )
                
                st.plotly_chart(f1, use_container_width=True)
                if i==0:
                    df_table_all=df_table
                else:
                    df_table_all=pd.concat([df_table_all,df_table])
                c1,c2=st.columns(2)
                with c2:
                    if Videos == "Yes":
                    
                        if pd.isnull(df_temp["Video"].iloc[0]):
                            st.header("No video available")
                        else:
                            video_name = df_temp["Video"].iloc[0]
                            st.header(df_temp["Title"].iloc[0])

                            st.video(f"{video_name}")
                
                st.markdown("---")
                
                
                teamsplits = [df_table["62.5"][0],df_table["125"][0],df_table["187.5"][0],df_table["250"][0],df_table["312.5"][1]+df_table["Gap 1"][1],df_table["375"][1],df_table["437.5"][1],df_table["500"][1],df_table["562.5"][2]+df_table["Gap 2"][2],df_table["625"][2],df_table["687.5"][2],df_table["750"][2]]
                
                teamspeeds = [round(3.6*62.5/i,2) for i in teamsplits]
                
                df_speeds = pd.DataFrame(teamspeeds)
                
                df_speeds["Title"] = selections[i]
                df_speeds["Marker"] = ["Q1","Q2","Q3","Q4","Q5","Q6","Q7","Q8","Q9","Q10","Q11","Q12"]
                df_speeds["Splits"] = teamsplits
                df_combine = pd.concat([df_combine, df_speeds], axis=0)
                
            st.header("Full Summary", anchor="summary")
            df = df_table_all
            df_filt = filter_dataframe(df)
            df_filt
            
            buffer = io.BytesIO()
            @st.cache_data
            def convert_to_csv(df):
                # IMPORTANT: Cache the conversion to prevent computation on every rerun
                return df.to_csv(index=False).encode('utf-8')

            csv = convert_to_csv(df)

            # download button 1 to download dataframe as csv
            download1 = st.download_button(
                label="Download Summary as CSV",
                data=csv,
                file_name='WTS_summary.csv',
                mime='text/csv'
            )

            # download button 2 to download dataframe as xlsx
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                # Write each dataframe to a different worksheet.
                df_filt.to_excel(writer, sheet_name='Sheet1', index=False)
                # Close the Pandas Excel writer and output the Excel file to the buffer
                writer.close()

                download2 = st.download_button(
                    label="Download Summary as Excel",
                    data=buffer,
                    file_name='WTS_summary.xlsx',
                    mime='application/vnd.ms-excel'
                ) 
            
            df_combine.rename(columns={ df_combine.columns[0]: "Speed (km/h)" }, inplace = True)
            
            fig_comp = px.line(df_combine, x="Marker", y = "Speed (km/h)", title="Average Speed Comparison",color="Title",markers="Splits",labels = {
            "Marker":"Quarter"})

            st.plotly_chart(fig_comp, use_container_width=True)
            
            fig_comp_split = px.line(df_combine, x="Marker", y = "Splits", title="Split Comparison",color="Title",markers="Splits",labels = {
            "Marker":"Quarter"})

            st.plotly_chart(fig_comp_split, use_container_width=True)
        st.markdown('---')
        st.header("Editor")
        with open('pages/TP_demo.xlsx', "rb") as template_file:
                template_byte = template_file.read()



        st.download_button(label="Click to Download Template File",
                            data=template_byte,
                            file_name="template.xlsx"
                          )

        uploaded_file = st.file_uploader("Choose a file",key="uploader")

        if uploaded_file is not None:
            st.markdown("---")

            st.header("Editor")
            st.write("Initial df")
            df_full = pd.read_csv(uploaded_file)
            df_full=df_full.sort_values(by=["Start time"]).reset_index(drop=True)
            df_full.drop(['Timeline','Duration','Instance number','Ungrouped','Notes','Flags'],
          axis='columns', inplace=True)
            
            
            c1,c2,c3=st.columns(3)
            with c1:
                df_full
                start=st.number_input("Start Row (inclusive)", value=0)
            with c2:
                df_check = pd.DataFrame(df_full.iloc[::29, :])
                df_check.drop(["Start time"],axis='columns', inplace=True)
                st.write("Checking we've got everything")
                df_check
                end=st.number_input("End Row (inclusive)", value=start+28)+1
            
            
            df=df_full[start+1:end]
            df=df.sort_values("Start time", ascending=True)
            
            
            with c1:
                rider1 = st.text_input("Select Rider 1:")
                rider2 = st.text_input("Select Rider 2:")
                rider3 = st.text_input("Select Rider 3:")
            
            riders=[rider1,rider2,rider3]
            
            
            
            

            #df = df.dropna(axis=0, subset=['Time'])

            with c2:
                
               
                
                rider1gear = st.text_input("Select Rider 1 gear:")
                rider2gear = st.text_input("Select Rider 2 gear:")
                rider3gear = st.text_input("Select Rider 3 gear:")
                Title = st.text_input("Plot Title:")


            df["Riders"]="NA"
            df["Riders"].iloc[0]=rider1
            df["Riders"].iloc[1]=rider2
            df["Riders"].iloc[2]=rider3
            df["Gears"]=0.0
            df["Title"]=Title
            col = df.pop('Title')
            df.insert(0, col.name, col)
            df["Gears"].iloc[0]=rider1gear
            df["Gears"].iloc[1]=rider2gear
            df["Gears"].iloc[2]=rider3gear
            front=[rider1]
            splits=[0]
            del_speeds=[0]
            speeds=[0]
            r=0
            
   
           
            
            df=df.reset_index(drop=True)
            with c3:
                df
                ind1=df.index[df['Row'] == "Rider 1 Forward"].tolist()[0]
                ind2=df.index[df['Row'] == "Rider 2 Forward"].tolist()[0]
                ind3=df.index[df['Row'] == "Rider 3 Forward"].tolist()[0]
                indstart=df.index[df['Row'] == "Start"].tolist()[0]
                react1 = round(df["Start time"][ind1]-df["Start time"][indstart],2)
                react2 = round(df["Start time"][ind2]-df["Start time"][indstart],2)
                react3 = round(df["Start time"][ind3]-df["Start time"][indstart],2)
                st.write(f'Reaction time for rider 1 is {react1} seconds')
                st.write(f'Reaction time for rider 2 is {react2} seconds')
                st.write(f'Reaction time for rider 3 is {react3} seconds')

            
            #master_path=st.text_input("Add path to master file:",key="prompt")
            if st.button("Append this effort to master",key="upload"):




                df_save=df
                df_save.insert(0, 'Save_Date', datetime.date.today())
                df_save["Save_Date"] = pd.to_datetime(df_save['Save_Date'])
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
                    file_name='WTS_Master_Women.csv',
                    mime='text/csv'
                )

                # download button 2 to download dataframe as xlsx
                with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                    # Write each dataframe to a different worksheet.
                    df.to_excel(writer, sheet_name='Sheet1', index=False)
                    # Close the Pandas Excel writer and output the Excel file to the buffer
                    writer.close()

                    download2 = st.download_button(
                        label="Download new Master as Excel",
                        data=buffer,
                        file_name='WTS_Master_Women.xlsx',
                        mime='application/vnd.ms-excel'
                    )       
            
 