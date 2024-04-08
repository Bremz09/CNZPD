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
    
    st.latex(r'''P_{Aero} = C_{d}A \frac{1}{2}\rho v^3''')

    st.header("Insert initial values")
    st.session_state
    

    c1,c2,c3,c4=st.columns(4)
    with c1:
        options=["v","CdA","rho","P"]
        
        var1=st.selectbox(options=options,label="Inital value 1:",key="a")
        if var1=="v":
            value = 16.67
            label="Speed in m/s"
            var1_value=st.number_input(label=f"{label}:",value=value,key=f"e")
            v=var1_value
            ls=250/v
            st.write(f"Lap split of {round(ls,2)} seconds")

        if var1=="CdA":
            value = 0.1700
            label="CdA in m^2"
            var1_value=st.number_input(label=f"{label}:",value=value,key=f"c",step=1e-4,format="%.4f")
            CdA=var1_value
        if var1=="rho":
            value = 1.169
            label="Air density in kg/m^3"
            var1_value=st.number_input(label=f"{label}:",value=value,key=f"d",step=1e-3,format="%.3f")
            rho=var1_value
        if var1=="P":
            value = 460
            label="Power in watts"
            var1_value=st.number_input(label=f"{label}:",value=value,key=f"b")
            P=var1_value

    with c2:
        options.remove(var1)
        var2=st.selectbox(options=options,label="Inital value 2:",key="f")
        if var2=="P":
            value = 460
            label="Power in watts"
            var2_value=st.number_input(label=f"{label}:",value=value,key=f"g")
            P=var2_value
        if var2=="CdA":
            value = 0.1700
            label="CdA in m^2"
            var2_value=st.number_input(label=f"{label}:",value=value,key=f"h",step=1e-4,format="%.4f")
            CdA=var2_value
        if var2=="rho":
            value = 1.169
            label="Air density in kg/m^3"
            var2_value=st.number_input(label=f"{label}:",value=value,key=f"i",step=1e-3,format="%.3f")
            rho=var2_value
        if var2=="v":
            value = 16.67
            label="Speed in m/s"
            var2_value=st.number_input(label=f"{label}:",value=value,key=f"j")
            v=var2_value
            ls=250/v
            st.write(f"Lap split of {round(ls,2)} seconds")
        
    with c3:
        options.remove(var2)
        var3=st.selectbox(options=options,label="Inital value 3:",key="k")
        if var3=="P":
            value = 460
            label="Power in watts"
            var3_value=st.number_input(label=f"{label}:",value=value,key=f"l")
            P=var3_value
        if var3=="CdA":
            value = 0.1700
            label="CdA in m^2"
            var3_value=st.number_input(label=f"{label}:",value=value,key=f"m",step=1e-4,format="%.4f")
            CdA=var3_value
        if var3=="rho":
            value = 1.169
            label="Air density in kg/m^3"
            var3_value=st.number_input(label=f"{label}:",value=value,key=f"n",step=1e-3,format="%.3f")
            rho=var3_value
        if var3=="v":
            value = 16.67
            label="Speed in m/s"
            var3_value=st.number_input(label=f"{label}:",value=value,key=f"o")
            v=var3_value
            ls=250/v
            st.write(f"Lap split of {round(ls,2)} seconds")
        
    with c4:
        options.remove(var3)
        if options[0]=="P":
            var4 = CdA*0.5*rho*(v**3)
            P=var4
            st.latex(r'''P = C_{d}A \frac{1}{2} \rho v^3 = '''+rf'''{round(var4,2)}'''+r'''\text{ W}''')
        if options[0]=="CdA":
            var4 = 2*P/(rho*(v**3))
            CdA=var4
            st.latex(r'''C_{d}A=\frac{2P}{\rho v^3} = '''+rf'''{round(var4,4)} '''+r'''\text{ }'''+r'''ms^{-1}''')
        if options[0]=="rho":
            var4 = 2*P/(CdA*(v**3))
            rho=var4
            st.latex(r'''\rho=\frac{2P}{C_{d}A v^3} = '''+rf'''{round(var4,3)}'''+r'''\text{ }'''+r'''kgm^{-3}''')
        if options[0]=="v":
            var4 = (2*P/(CdA*rho))**(1/3)
            v=var4
            st.latex(r'''v=\left( \frac{2P}{C_{d}A\rho}  \right)^{\frac{1}{3}} = '''+rf'''{round(var4,2)} '''+ r''' \text{ }ms^{-1}''')
            st.latex(r'''\text{Or a lap time of }'''+rf'''{round(250/var4,2)}'''+r'''\text{ seconds}''')
    
    st.header("Final Values")
    c1,c2=st.columns(2)
   
    with c1:
        free_var=st.selectbox(options=["P","CdA","v","rho"],label="Select free variable:",key="p")
    with c2:
        if free_var=="P":
            shift=st.number_input(label=f"Power shift in Watts:",value=0,key=f"free_P")
        if free_var=="CdA":
            shift=st.number_input(label=f"CdA shift in m^2:",value=0.000,key=f"free_CdA",step=1e-4,format="%.4f")
        if free_var=="rho":
            shift=st.number_input(label=f"rho shift in kg/m^3:",value=0.00,key=f"free_rho",step=1e-3,format="%.3f")
        if free_var=="v":
            shift=st.number_input(label=f"Speed in m/s:",value=0.00,key=f"free_v")
    if free_var=="P":
        P_f = P+shift
        st.latex(rf''' P_f = {round(P_f,2)}''')
        c1,c2=st.columns(2)
        CdA_f = P_f*CdA/P
        with c1:
            st.latex(r'''v_{in} = v_{f} \implies C_dA_f = \frac{P_fC_dA_{in}}{P_{in}}''')
            st.latex(rf''' C_dA_f = {round(CdA_f,4)}''')
            st.subheader(f"A shift of {round(CdA_f-CdA,4)} m^2")

        
        with c2:
            v_f = (P_f*(v**3)/P)**(1/3)
            st.latex(r'''C_dA_{in} = C_dA_f \implies v_f = \left(\frac{P_f}{P_{in}v_{in}^3}\right)^{1/3}''')
            st.latex(rf''' v_f = {round(v_f,2)}'''+r'''\text{ }'''r'''ms^{-1}''')
            st.latex(rf''' Lap Split = {round(250/v_f,2)}''' +r'''\text{ s}''')
            
    if free_var=="CdA":
        CdA_f = CdA+shift
        st.latex(rf''' C_dA_f = {round(CdA_f,4)}''')
        c1,c2=st.columns(2)
        P_f = CdA_f*P/CdA
        with c1:
            st.latex(r'''v_{in} = v_{f} \implies P_f = \frac{C_dA_fP_{in}}{C_dA_{in}}''')
            st.latex(rf''' P_f = {round(P_f,2)}''')
            st.subheader(f"A shift of {round(P_f-P,2)} W")
        with c2:
            v_f = (CdA*(v**3)/CdA_f)**(1/3)
            st.latex(r'''P_{in} = P_f \implies v_f = \left(\frac{C_dA_{in}v_{in}^3}{C_dA_f}\right)^{1/3}''')
            st.latex(rf''' v_f = {round(v_f,2)}'''+r'''\text{ }'''r'''ms^{-1}''')
            st.latex(rf''' Lap Split = {round(250/v_f,2)}''' +r'''\text{ s}''')
    if free_var=="v":
        v_f = v+shift

        st.latex(rf''' v_f = {round(v_f,2)}''')
        st.latex(rf''' Lap Split = {round(250/v_f,2)}''')
        c1,c2=st.columns(2)
        P_f = ((v_f)**3)*P/((v)**3)
        with c1:
            st.latex(r'''C_dA_{in} = C_dA_{f} \implies P_f = \frac{v_f^3P_{in}}{v_{in}^3}''')
            st.latex(rf''' P_f = {round(P_f,2)}''')
            st.subheader(f"A shift of {round(P_f-P,2)} W")
        with c2:
            CdA_f = CdA*((v)**3)/((v_f)**3)
            st.latex(r'''P_{in} = P_f \implies C_dA_f = \frac{C_dA_{in}v_{in}^3}{v_f^3}''')
            st.latex(rf''' C_dA_f = {round(CdA_f,4)}'''+r'''\text{ }'''r'''m^{2}''')
            st.subheader(f"A shift of {round(CdA_f-CdA,4)} m^2")
    if free_var=="rho":
        rho_f = rho+shift
        st.latex(rf''' \rho_f = {round(rho_f,3)}''')
        c1,c2=st.columns(2)
        P_f = rho_f*P/rho
        with c1:
            st.latex(r'''v_{in} = v_{f} \implies P_f = \frac{\rho_fP_{in}}{\rho_{in}}''')
            st.latex(rf''' P_f = {round(P_f,2)}''')
            st.subheader(f"A shift of {round(P_f-P,2)} W")
        with c2:
            v_f = (rho*(v**3)/rho_f)**(1/3)
            st.latex(r'''P_{in} = P_f \implies v_f = \left(\frac{\rho_{in}v_{in}^3}{\rho_f}\right)^{1/3}''')
            st.latex(rf''' v_f = {round(v_f,2)}'''+r'''\text{ }'''r'''ms^{-1}''')
            st.latex(rf''' Lap Split = {round(250/v_f,2)}''' +r'''\text{ s}''')
        
    if v_f>v:
        c1,c2,c3=st.columns(3)
        with c2:
            diff_3750 = (3750/v)-(3750/v_f)
            
            st.subheader(f"This is {round(diff_3750,2)} seconds faster over 3750m")
    if v_f<v:
        c1,c2,c3=st.columns(3)
        with c2:
            diff_3750 = (3750/v_f)-(3750/v)
            
            st.subheader(f"This is {round(diff_3750,2)} seconds slower over 3750m")