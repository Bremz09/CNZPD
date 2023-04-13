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




st.set_page_config(page_title='CNZ Performance Database',
                  page_icon=":bike:",
                  layout="wide")


# def get_data_from_excel():
#     df_master = pd.read_excel(
#         io='pages/TP_Master.xlsx',
#         engine ='openpyxl',
#         sheet_name='Sheet1',
#         skiprows=0,
#         usecols='A:I',
#         nrows=8000
#         )
#     #df = df.replace(',','', regex=True)
#     #for i in range(len(df)):
#         #df["Date"][i] = df["Date"][i].date()
#         #if df["125m"][i] != "NULL":
#             #df["125m"][i] = df["125m"][i].strftime("%M:%S.%f")
#     return df_master
# df_master= get_data_from_excel()














##This bit is the historical visualiser

st.header("View/compare efforts from master file")
master_file=st.file_uploader("Select master file")
if master_file:
    df_master = pd.read_excel(master_file)
    df_master

    selections = st.multiselect(
    "Select past effort(s):",
    options=df_master["Title"].unique()
    )   




    if len(selections) !=0:
        for i in range(len(selections)):
            col_1,col_2=st.columns(2)
            with col_1:
                df_temp = df_master.loc[df_master['Title'] == selections[i]]
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
    
    
    
    
    
    
    master_path=st.text_input("Add path to master file:",key="prompt")
    if st.button("Save this effort to master",key="upload"):
        
        
  
      
        df_save=df
        df_save.insert(0, 'Save_Date', datetime.date.today())
        df_save.insert(0, 'Title', Title)
        df_save
        st.write("Saved to Database")



        master=xw.Book(f'{master_path}')
        master_sheets=master.sheets
        sheet=master_sheets[0]
        if sheet.range('A1').end('down').row > 1000000:
            index=2
        else:
            index=sheet.range('A1').end('down').row+1
        for i in range(len(df)):
            sheet[f'A{index}'].value = df_save.iloc[i][0]
            sheet[f'B{index}'].value = df_save.iloc[i][1]
            sheet[f'C{index}'].value = df_save.iloc[i][2]
            sheet[f'D{index}'].value = df_save.iloc[i][3]
            sheet[f'E{index}'].value = df_save.iloc[i][4]
            sheet[f'F{index}'].value = df_save.iloc[i][5]
            sheet[f'G{index}'].value = df_save.iloc[i][6]
            sheet[f'H{index}'].value = df_save.iloc[i][7]
            sheet[f'I{index}'].value = df_save.iloc[i][8]
            index+=1
        master.save()
        master.close()




