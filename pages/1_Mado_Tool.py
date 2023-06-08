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

    df_master = pd.read_csv(f'pages/Jakarta_Mado_W.csv')
    df_master

    selections = st.multiselect(
    "Select past effort(s):",
    options=df_master["Title"].unique()
        )   




    if len(selections) !=0:
        df_combine = pd.DataFrame()
        for i in range(len(selections)):
            col_1,col_2=st.columns(2)
            with col_1:
                df_temp = df_master.loc[df_master['Title'] == selections[i]]
                df_combine = pd.concat([df_combine, df_temp], axis=0)
                df_temp
            with col_2:
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
                #fig.add_hline(y=250*3.6/schedule, line_dash="dash",line_color="white",annotation_text="Schedule = " +str(schedule))
                st.plotly_chart(fig, use_container_width=True)



        fig_tt = px.line(df_combine, x="Distance", y = "Split", title="Comparison",color="Title",markers="Front")

        st.plotly_chart(fig_tt, use_container_width=True)

        if len(selections) >1:

            df_zero = df_combine
            df_zero = df_zero.reset_index(drop=True)
            st.write(len(selections))
            length = df_zero.Title.value_counts()[selections[0]]

            for j in range(length,len(selections)*length):
                df_zero.Split[j]=df_zero.Split[j]-df_zero.Split[j-length]
                df_zero.Split[j-length]=0





            fig_zero = px.line(df_zero, x="Distance", y = "Split", title="Zero",color="Title",markers="Front")

            st.plotly_chart(fig_zero, use_container_width=True)

            fig_worm = px.line(df_zero, x="Distance", y = "Time", title="Worm",color="Title",markers="Front")

            st.plotly_chart(fig_worm, use_container_width=True)
















    ## This is where you upload a new run           

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
        rider0 = st.text_input("Select Rider 1:")
        rider1 = st.text_input("Select Rider 2:")
        col_one, col_two,c3 = st.columns(3)
        
        with col_one:
            

            #down=[rider1]
            splits=[0]
            del_speeds=[]
            speeds=[0]
            r=0
            df.Time = df.Time - df.Time[0]
            down=[]
            #df = df.dropna(axis=0, subset=['Time'])
            down_tick=0
            tick=0
            for i in range(len(df)):
                if df.Action[i] == "Gap":
                    down.append(eval(f'rider{down_tick}'))
                else:
                    tick+=1
                    down_tick=tick%2
                    down.append(eval(f'rider{down_tick}'))
            df["In"]=down
            df
            
        with col_two:
            df_gaps=pd.DataFrame(df.loc[df['Action'] == "Gap"]).reset_index(drop=True)
            df_gaps
            x_gaps = np.linspace(0, len(df_gaps)-1, num=len(df_gaps))
        fig_gaps = px.line(df_gaps, x=x_gaps, y = "Duration", title="Gap behind leader at the end of each lap",markers="In")

        st.plotly_chart(fig_gaps, use_container_width=True)
        with c3:
            df_pos=pd.DataFrame(df.loc[df['Action'] != "Gap"]).reset_index(drop=True)
            df_pos
            x_pos = np.linspace(0, len(df_pos)-1, num=len(df_pos))
        fig_pos = px.line(df_pos, x=x_pos, y = "Action", title="Position at Handover",markers="In")

        st.plotly_chart(fig_pos, use_container_width=True)
            
            
            
            
            
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





  




