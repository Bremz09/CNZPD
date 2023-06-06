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

    st.header("View/compare efforts from master file")

    # own_master=st.file_uploader("Select master file")
    # if own_master:
    #     df_master = pd.read_excel(own_master)
    #     df_master

    #     selections = st.multiselect(
    #     "Select past effort(s):",
    #     options=df_master["Title"].unique()
    #     )   
    # else:
    df_master = pd.read_excel(f'pages/TP_Master.xlsx')
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
                r1 = [1]
                r2 = [2]
                r3 = [3]
                r4 = [4]
                r1WS = [0.971]
                r2WS = [0.612]
                r3WS = [0.495]
                r4WS = [0.459]
                no_riders=4
                drag_feel = [0,0.971,0.612,0.495,0.459]
                for j in range(1,len(df_small)):
                    
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
                df_small["Rider1"]=r1
                df_small["Rider2"]=r2
                df_small["Rider3"]=r3
                df_small["Rider4"]=r4
                df_small["Rider1WS"]=r1WS*df_small["Del_Speed"]
                df_small["Rider2WS"]=r2WS*df_small["Del_Speed"]
                df_small["Rider3WS"]=r3WS*df_small["Del_Speed"]
                df_small["Rider4WS"]=r4WS*df_small["Del_Speed"]
                
                #df = df_small.drop(columns=["Rider1","Rider2","Rider3","Rider4","Action"])
                df_small
            with col_2:
                average = df_small.Split.iloc[4:].mean()
                fig = px.bar(df_temp, x='Distance', y='Avg_Speed',color=df_temp.Front,hover_data=[df_temp.Split, df_temp.Avg_Speed,df_temp.Del_Speed])
                fig.add_trace(go.Scatter(x=df_temp['Distance'][1:], y=df_temp['Del_Speed'][1:],mode='markers',name="Delivery Speed"))
                fig.update_layout(
                title={
                    'text': df_temp.Title.iloc[0],
                    'y':0.9,
                    'x':0.5,
                    'xanchor': 'center',
                    'yanchor': 'top',
                    'font':dict(size=25)})
                fig.add_hline(y=62.5*3.6/average, line_dash="dash",line_color="white",annotation_text="Avg after first lap = " +str(round(average*4,2)))
                st.plotly_chart(fig, use_container_width=True)
            c1,c2=st.columns(2)
            with c1:
                
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
                df_summ["Wind_Score"] = wind_scores
                df_summ
                
              
            if Videos == "Yes":
                with c2:
                    if pd.isnull(df_temp["Video"].iloc[0]):
                        st.header("No video available")
                    else:
                        video_name = df_temp["Video"].iloc[0]
                        st.header(df_temp["Title"].iloc[0])
                        #if os.path.isfile(f'pages\\Videos\\{video_name}.mp4'):
                        #video_file = open(f'pages\\Videos\\{video_name}.mp4', 'rb')
                        #video_file = open(f'pages\\Videos\\{video_name}.mp4', 'rb')
                        #video_bytes = video_file.read()
                        st.video(f"{video_name}")
            st.markdown("---")



        col_one, col_two, col_three, col_four = st.columns(4)
        with col_one:
            show_names = ["No","Yes"]
            Names = st.selectbox("Show Athlete Names?", show_names, key="Show_Names")
            df_combine["Initial"]=df_combine["Front"].str.replace('[^A-Z]', '')
        if Names == "Yes":
            fig_tt = px.line(df_combine, x="Distance", y = "Split", title="Comparison",color="Title",text="Initial",markers="Front")
            fig_tt.update_traces(textposition='top center')
        else:
            fig_tt = px.line(df_combine, x="Distance", y = "Split", title="Comparison",color="Title",markers="Front")

        st.plotly_chart(fig_tt, use_container_width=True)

        if len(selections) ==2:

            df_zero = df_combine
            df_zero = df_zero.reset_index(drop=True)
            length = df_zero.Title.value_counts()[selections[0]]
            for j in range(length,len(selections)*length):
                df_zero.Split[j]=df_zero.Split[j]-df_zero.Split[j-length]
                df_zero.Split[j-length]=0



            if Names == "Yes":
                fig_zero = px.line(df_zero, x="Distance", y = "Split", title="Zero",color="Title",text="Initial",markers="Front")
                fig_zero.update_traces(textposition='top center')
            else:
                fig_zero = px.line(df_zero, x="Distance", y = "Split", title="Zero",color="Title",markers="Front")
            st.plotly_chart(fig_zero, use_container_width=True)
            if Names=="Yes":
                fig_worm = px.line(df_zero, x="Distance", y = "Time", title="Worm",color="Title",text="Initial",markers="Front")
                fig_worm.update_traces(textposition='top center')
            if Names=="No":
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
        df = pd.read_csv(uploaded_file)
        df=df.sort_values("Start time", ascending=True)
        col_one, col_two, col_three = st.columns(3)
        with col_one:
            rider1 = st.text_input("Select Rider 1:")
            rider2 = st.text_input("Select Rider 2:")
            rider3 = st.text_input("Select Rider 3:")
            rider4 = st.text_input("Select Rider 4:")

        front=[rider1]
        splits=[0]
        del_speeds=[]
        speeds=[0]
        r=0
        df["Time"] = df["Start time"] - df["Start time"].iloc[0]
        markers = len(df)
        df["Distance"] = np.linspace(0, 62.5*(markers-1), num=markers)
        df=df.reset_index(drop=True)
        df.drop(['Timeline','Duration','Instance number','Ungrouped','Notes','Flags'],
      axis='columns', inplace=True)

        #df = df.dropna(axis=0, subset=['Time'])

        with col_two:
            offset = st.number_input("Offset:", min_value=0.00, max_value=None,value=0.08)
            schedule = round(st.number_input("Schedule:", min_value=0.00, max_value=None,value=14.3),2)
            Title = st.text_input("Plot Title:")


        with col_three:
            num_riders=4
            dropped=''
            for i in range(len(df)-1):
                splits.append(round(df.Time[i+1]-df.Time[i],3))
                speeds.append(round((df.Distance[i+1]-df.Distance[i])*3.6/splits[i+1],2))
    #             st.write(str(i+1) + ' current rider is ' + eval(f'rider{r%num_riders+1}'))
    #             st.write(dropped + ' has been dropped')
    #             st.write("Next is " + eval(f'rider{r%num_riders+2}'))
                skip=1
                if dropped == eval(f'rider{r%num_riders+1}'):

                    st.write("next rider is " + eval(f'rider{r%num_riders+1}'))
                    r+=1
                    st.write("lets instead use " + eval(f'rider{r%num_riders+1}'))
                    skip=0
                if df["Row"][i]=="No Change" or df["Row"][i]=="Start/Finish":
                    front.append(eval(f'rider{r%num_riders +1}'))
                    del_speeds.append(speeds[i])
                elif df["Row"][i]=="Change":
                    r+=skip            
                    front.append(eval(f'rider{r%num_riders+1}'))
                    del_speeds.append(round(speeds[i]*splits[i]/(splits[i]-offset),2))                
                elif df["Row"][i]=="Drop":
                    dropped = eval(f'rider{r%num_riders+1}')
                    st.write(str(i) + " " +dropped + " has been dropped")
                    r+=1
                    front.append(eval(f'rider{r%num_riders+1}'))
                    del_speeds.append(round(speeds[i]*splits[i]/(splits[i]-offset),2))

            del_speeds.append(speeds[len(speeds)-1])
    #         for j in range(len(df)):
    #             if df.Change[j]=="n":
    #                 del_speeds.append(speeds[j])
    #             else:
    #                 del_speeds.append(speeds[j]*splits[j]/(splits[j]-offset))
            df["Del_Speed"]=del_speeds
            df["Avg_Speed"]=speeds
            df["Split"]=splits
            df["Front"]=front
            df.drop('Start time',
      axis='columns', inplace=True)
            df.rename(columns = {'Row':'Action'}, inplace = True)
            df.drop(index=df.index[0], axis=0, inplace=True)
            #df = df.dropna(axis=0, subset=['Time'])
            st.write(df)


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
                file_name='TP_Master.csv',
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
                    file_name='TP_Master.xlsx',
                    mime='application/vnd.ms-excel'
                )






