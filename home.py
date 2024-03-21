#!/usr/bin/env python
# coding: utf-8


from pathlib import Path
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image
 

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

name, authentication_status, username = authenticator.login('Login', "main")
#name, authentication_status, username = authenticator.fields{'Form name':'Login', 'Username':'Username', 'Password':'Password', 'Login':'Login'}

if authentication_status == False:
    st.error("Username/password is incorrect")

if authentication_status == None:
    st.warning("Please enter your username and password")

if authentication_status:

    authenticator.logout("Logout", "main")

    col1, col2, col3 = st.columns(3)

    with col2:
        st.image("CNZ.png")


    st.markdown("<h1 style='text-align: center; color: white;'>Performance Database</h1>", unsafe_allow_html=True)

    st.markdown("<h2 style='text-align: center; color: Silver;'>Event links in left sidebar</h2>", unsafe_allow_html=True)

    st.markdown("<h4 style='text-align: center; color: Silver;'>Please send any ideas or bug reports to sam.bremer@hpsnz.org.nz</h4>", unsafe_allow_html=True)






