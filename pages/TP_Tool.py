#!/usr/bin/env python
# coding: utf-8



import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image
import numpy as np
from io import StringIO



st.set_page_config(page_title='CNZ Performance Database',
                  page_icon=":bike:",
                  layout="wide")
st.header('Pursuit Visualiser')
st.subheader('All results')



riders=["GATE Aaron","BRIDGEWATER Dan","SEXTON Tom", "GOUGH Regan", "STEWART Campbell", "JACKSON George"]
riders.sort()
uploaded_file = st.file_uploader("Choose a file")



if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)
    col_one, col_two, col_three = st.columns(3)

    with col_one:
        rider1 = st.selectbox("Select Rider 1:", riders)
        rider2 = st.selectbox("Select Rider 2:", riders)
        rider3 = st.selectbox("Select Rider 3:", riders)
        rider4 = st.selectbox("Select Rider 4:", riders)

    front=[rider1]
    splits=[0]
    del_speeds=[]
    speeds=[0]
    r=0



    with col_two:
        offset = st.number_input("Input offset:")

    with col_three:
        for i in range(len(df)-1):
            splits.append(df.Time[i+1]-df.Time[i])
            speeds.append((df.Distance[i+1]-df.Distance[i])*3.6/splits[i+1])
            if df.Change[i]=="n":
                front.append(eval(f'rider{r%4 +1}'))
                del_speeds.append(speeds[i])
            else:
                r+=1
                front.append(eval(f'rider{r%4 +1}'))
                del_speeds.append(speeds[i]*splits[i]/(splits[i]-offset))
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
        
    fig = px.bar(df, x='Distance', y='Avg_Speed',color="Front")
    st.plotly_chart(fig, use_container_width=True)
