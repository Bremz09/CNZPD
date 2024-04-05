#!/usr/bin/env python
# coding: utf-8


import pickle
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image
import datetime
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm
import os
import pytz
import streamlit_authenticator as stauth
import math
import time


st.set_page_config(page_title='CNZ Performance Database',
                  page_icon=":bike:",
                  layout="wide")

# --- USER AUTHENTICATION ---

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
    
    st.latex(r'''P = C_{d}A \frac{1}{2}\rho v^3''')
    st.header("Insert initial values")
    c1,c2,c3,c4=st.columns(4)
    with c1:
        options=["P","CdA","rho","v"]
        var1=st.selectbox(options=options,label="Inital value 1:",key="var1")
        if var1=="P":
            value = 450
            label="Power in watts"
            var1_value=st.number_input(label=f"{label}:",value=value,key=f"{var1}")
            P=var1_value
        if var1=="CdA":
            value = 0.1700
            label="CdA in m^2"
            var1_value=st.number_input(label=f"{label}:",value=value,key=f"{var1}")
            CdA=var1_value
        if var1=="rho":
            value = 1.169
            label="Air density in kg/m^3"
            var1_value=st.number_input(label=f"{label}:",value=value,key=f"{var1}")
            rho=var1_value
        if var1=="v":
            value = 15.00
            label="Lap split in seconds"
            var1_value=st.number_input(label=f"{label}:",value=value,key=f"{var1}")
            v=var1_value
        
    with c2:
        options.remove(var1)
        var2=st.selectbox(options=options,label="Inital value 2:",key="var2")
        if var2=="P":
            value = 450
            label="Power in watts"
            var2_value=st.number_input(label=f"{label}:",value=value,key=f"{var2}")
            P=var2_value
        if var2=="CdA":
            value = 0.1700
            label="CdA in m^2"
            var2_value=st.number_input(label=f"{label}:",value=value,key=f"{var2}")
            CdA=var2_value
        if var2=="rho":
            value = 1.169
            label="Air density in kg/m^3"
            var2_value=st.number_input(label=f"{label}:",value=value,key=f"{var2}")
            rho=var2_value
        if var2=="v":
            value = 15.00
            label="Lap split in seconds"
            var2_value=st.number_input(label=f"{label}:",value=value,key=f"{var2}")
            v=var2_value
        
    with c3:
        options.remove(var2)
        var3=st.selectbox(options=options,label="Inital value 3:",key="var3")
        if var3=="P":
            value = 450
            label="Power in watts"
            var3_value=st.number_input(label=f"{label}:",value=value,key=f"{var3}")
            P=var3_value
        if var3=="CdA":
            value = 0.1700
            label="CdA in m^2"
            var3_value=st.number_input(label=f"{label}:",value=value,key=f"{var3}")
            CdA=var3_value
        if var3=="rho":
            value = 1.169
            label="Air density in kg/m^3"
            var3_value=st.number_input(label=f"{label}:",value=value,key=f"{var3}")
            rho=var3_value
        if var3=="v":
            value = 15.00
            label="Lap split in seconds"
            var3_value=st.number_input(label=f"{label}:",value=value,key=f"{var3}")
            v=250/var3_value
        
    with c4:
        options.remove(var3)
        if options[0]=="P":
            var4 = CdA*0.5*rho*(v**3)
            st.latex(r'''P = C_{d}A \rho v^3 = '''+rf'''{var4}'''+r'''\text{ W}''')
        if options[0]=="CdA":
            var4 = round(2*P/(rho*(v**3)),4)
            st.latex(r'''C_{d}A=\frac{2P}{\rho v^3} = '''+rf'''{var4} '''+r'''\text{ }'''+r'''ms^{-1}''')
        if options[0]=="rho":
            var4 = round(2*P/(CdA*(v**3)),4)
            st.latex(r'''\rho=\frac{2P}{C_{d}A v^3} = '''+rf'''{var4}'''+r'''\text{ }'''+r'''kgm^{-3}''')
        if options[0]=="v":
            var4 = round((2*P/(CdA*rho))**(1/3),4)
            st.latex(r'''v=\left( \frac{2P}{C_{d}A\rho}  \right)^{\frac{1}{3}} = '''+rf'''{var4} '''+ r''' \text{ }ms^{-1}''')
            st.latex(r'''\text{Or a lap time of }'''+rf'''{round(250/var4,2)}'''+r'''\text{ seconds}''')