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

st.header("All Data")

# own_master=st.file_uploader("Select master file")
# if own_master:
#     df_master = pd.read_excel(own_master)
#     df_master

#     selections = st.multiselect(
#     "Select past effort(s):",
#     options=df_master["Title"].unique()
#     )   
# else:
df_master = pd.read_excel(f'pages/Environmental_Data/Uni_t_data_master.xlsx')
# @st.cache_data
# def get_time():
#     today = datetime.now()
#     return today
# today = get_time()
# time = st.slider(
#     "Start Date",
#     value=(datetime(2023, 1, 17, 9, 30),today),
#     format="DD/MM/YYYY - hh:mm")


##Gross start/end date getting stuff

end = df_master["Time"][len(df_master)-1]
date_time = end.strftime("%Y/%m/%d, %H:%M:%S")
splits = date_time.split('/')
day=splits[2].split(',')[0]

##Adding Air Density
c0=0.99999683
c1 = -0.90826951e-2
c2 = 0.78736169e-4
c3 = -0.61117958e-6
c4 = 0.43884187e-8
c5 = -0.29883885e-10
c6 = 0.21874425e-12
c7 = -0.17892321e-14
c8 = 0.11112018e-16
c9 = -0.30994571e-19
df_master["Temperature(K)"] = df_master["Temperature(C)"]+273.15
df_master["p(T)"] = c0 + df_master["Temperature(C)"]*(c1 + df_master["Temperature(C)"]*(c2 + df_master["Temperature(C)"]*(c3 + df_master["Temperature(C)"]*(c4 + df_master["Temperature(C)"]*(c5 + df_master["Temperature(C)"]*(c6 + df_master["Temperature(C)"]*(c7 + df_master["Temperature(C)"]*(c8 + df_master["Temperature(C)"]*(c9)))))))))
df_master["Es(T)"] = 6.1078/(pow(df_master["p(T)"],8))
df_master["Pwvp(Pa)"] = df_master["Relative_Humidity(%)"]*df_master["Es(T)"]

df_master["Air_Density(kg/m^3)"] = (df_master["Pwvp(Pa)"])/(461.495*(df_master["Temperature(K)"])) + ((df_master["Pressure(hPa)"]*100) - df_master["Pwvp(Pa)"])/(287.05*(df_master["Temperature(K)"]))

col1,col2 = st.columns(2)
with col1:
    start = st.date_input(
        "Select Start Date:",
        datetime.date(2023, 5, 17),
        key="start")
with col2:
    finish = st.date_input(
        "Select End Date:",
        datetime.date(int(splits[0]),int(splits[1]),int(day)))
    
start=pd.to_datetime(start)
end=pd.to_datetime(end)
mask = (df_master['Time'] > start) & (df_master['Time'] <= end)
df = df_master.loc[mask]
df
##Download buttons
@st.cache_data
def convert_to_csv(df):
    return df.to_csv(index=False,sep = ",").encode('utf-32')
csv = convert_to_csv(df)
download1 = st.download_button(
    label="Download All Environmental data as CSV",
    data=csv,
    file_name='Enviro_Data.csv',
    mime='text/csv'
)
buffer = io.BytesIO()
with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
    df.to_excel(writer, sheet_name='Sheet1', index=False)
    writer.save()
    download2 = st.download_button(
        label="Download Environmental data as Excel",
        data=buffer,
        file_name='Enviro_Data.xlsx',
        mime='application/vnd.ms-excel'
    )
##Download buttons complete

fig = px.scatter(df, x="Time", y = "Temperature(C)", title="Temperature")
st.plotly_chart(fig, use_container_width=True)

fig = px.scatter(df, x="Time", y = "Relative_Humidity(%)", title="Relative Humidity (%)")
st.plotly_chart(fig, use_container_width=True)

fig = px.scatter(df, x="Time", y = "Pressure(hPa)", title="Pressure (hPa)")
st.plotly_chart(fig, use_container_width=True)

fig = px.scatter(df, x="Time", y = "Air_Density(kg/m^3)", title="Air Density (kg/m^3)")
st.plotly_chart(fig, use_container_width=True)
