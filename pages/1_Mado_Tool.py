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


##This bit is the historical visualiser

st.header("View/compare efforts from master file")
master_file_mado=st.file_uploader("Select master file")
if master_file_mado:
    df_master = pd.read_excel(master_file_mado)
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
    df = pd.read_excel(uploaded_file)
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
    df.Time = df.Time - df.Time[0]
    #df = df.dropna(axis=0, subset=['Time'])

    with col_two:
        offset = st.number_input("Offset:", min_value=0.00, max_value=None,value=0.08)
        schedule = round(st.number_input("Schedule:", min_value=0.00, max_value=None,value=14.3),2)
        Title = st.text_input("Plot Title:")
        

    with col_three:
        for i in range(len(df)-1):
            splits.append(round(df.Time[i+1]-df.Time[i],3))
            speeds.append(round((df.Distance[i+1]-df.Distance[i])*3.6/splits[i+1],2))
            if df.Change[i]=="n":
                front.append(eval(f'rider{r%4 +1}'))
                del_speeds.append(speeds[i])
            else:
                r+=1
                front.append(eval(f'rider{r%4 +1}'))
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
        
        
        
        
        
#         df_save
#         st.write("Saved to Database")



#         master=xw.Book(f'{master_path}')
#         master_sheets=master.sheets
#         sheet=master_sheets[0]
#         if sheet.range('A1').end('down').row > 1000000:
#             index=2
#         else:
#             index=sheet.range('A1').end('down').row+1
#         for i in range(len(df)):
#             sheet[f'A{index}'].value = df_save.iloc[i][0]
#             sheet[f'B{index}'].value = df_save.iloc[i][1]
#             sheet[f'C{index}'].value = df_save.iloc[i][2]
#             sheet[f'D{index}'].value = df_save.iloc[i][3]
#             sheet[f'E{index}'].value = df_save.iloc[i][4]
#             sheet[f'F{index}'].value = df_save.iloc[i][5]
#             sheet[f'G{index}'].value = df_save.iloc[i][6]
#             sheet[f'H{index}'].value = df_save.iloc[i][7]
#             sheet[f'I{index}'].value = df_save.iloc[i][8]
#             index+=1
#         master.save()
#         master.close()




