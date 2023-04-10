#!/usr/bin/env python
# coding: utf-8

import pickle
from pathlib import Path
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image
import streamlit_authenticator as stauth 

st.set_page_config(page_title='CNZ Performance Database',
                  page_icon=":bike:",
                  layout="wide")

# # --- USER AUTHENTICATION ---
# names = ["CNZPD"]
# usernames = ["CNZPD"]

# # load hashed passwords
# with open("hashed_pw.pkl","rb") as file:
#     hashed_passwords = pickle.load(file)

# authenticator = stauth.Authenticate(names, usernames, hashed_passwords,"Cycling_New_Zealand_Performance_Database", "abcdef", cookie_expiry_days=30)

# name, authentication_status, username = authenticator.login("Login", "main")

# if authentication_status == False:
#     st.error("Username/password is incorrect")

# if authentication_status == None:
#     st.warning("Please enter your username and password")

# if authentication_status:

col1, col2, col3 = st.columns(3)

with col1:
    st.write('')

with col2:
    st.image("CNZ.png")
    st.header('Cycling New Zealand Performance Database')
    st.subheader('Event links in the sidebar')

with col3:
    st.write('')





    

