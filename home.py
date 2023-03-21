#!/usr/bin/env python
# coding: utf-8



import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image

st.set_page_config(page_title='CNZ Performance Database',
                  page_icon=":bike:",
                  layout="wide")

col1, col2, col3 = st.columns(3)

with col1:
    st.write('')

with col2:
    st.image("CNZ.png")
    st.header('Cycling New Zealand Performance Database')
    st.subheader('Event links in the sidebar')

with col3:
    st.write('')





    

