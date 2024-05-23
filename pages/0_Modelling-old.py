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
    st.header('Modelling Tool')

    update = datetime.date.today()+ pd.DateOffset(hour=12)


    
    
    
#     calcs = ["Power for Speed","Time for Power","CdA at Speed"]
    calcs = ["Male Individual Pursuit","Female Team Sprint"]
    Calc = st.selectbox("Select Model:", calcs, key="Calc_selector")
    
    
#     def get_power_profile_from_excel():
#         df_Dan = pd.read_excel(
#             io='pages/Dan_power_profile.xlsx',
#             engine ='openpyxl',
#             sheet_name='Sheet1',
#             skiprows=0,
#             usecols='A:G',
#             nrows=600
#             )
#         #df_MK = df_MK.replace(',','')
#         #df_MK['Date'] = pd.to_datetime(df_MK['Date']).dt.date
#         return df_Dan
#     df_Dan = get_power_profile_from_excel()
    
#     def get_B_power_profile_from_excel():
#         df_B = pd.read_excel(
#             io='pages/B_IP_Comms_22_Qual.xlsx',
#             engine ='openpyxl',
#             sheet_name='B Botha 2Hz',
#             skiprows=0,
#             usecols='A:C',
#             nrows=600
#             )
#         #df_MK = df_MK.replace(',','')
#         #df_MK['Date'] = pd.to_datetime(df_MK['Date']).dt.date
#         return df_B
#     df_B = get_B_power_profile_from_excel()
    if Calc == "Female Team Sprint":
        with st.form("my_form"):
            st.subheader("Position 1 specs")
            c1,c2,c3,c4,c5,c6 =st.columns(6)
            with c1:
                seat_max_RPM_1 = st.number_input("Seated Max RPM:", min_value=0.01, max_value=500.00,value=235.00,key="1_1")
            with c2:
                seat_max_torque_1 = st.number_input("Seated Max Torque:", min_value=0.01, max_value=500.00,value=207.00,key="1_2")
            with c3:
                seat_CdA_1 = st.number_input("Seated CdA:", min_value=0.0001, max_value=2.0000,value=0.2000, step=1e-4, format="%.4f",key="1_3")
            with c4:
                stand_max_RPM_1 = st.number_input("Standing Max RPM:", min_value=0.01, max_value=500.00,value=240.00,key="1_4")
            with c5:
                stand_max_torque_1 = st.number_input("Standing Max Torque:", min_value=0.01, max_value=500.00,value=223.00,key="1_5")
            with c6:
                stand_CdA_1 = st.number_input("Standing CdA:", min_value=0.00, max_value=20.00,value=0.3200, step=1e-4, format="%.4f",key="1_6")
            c1,c2,c3,c4 =st.columns(4)
            with c1:
                total_mass_1 = st.number_input("Total Mass:", min_value=40.0, max_value=150.0,value=84.0, step=0.1, format="%.1f",key="1_7")
            with c2:
                sprocket_1 = st.number_input("Sprocket:", min_value=12, max_value=22,value=15, step=1,key="1_8")
            with c3:
                chainring_1 = st.number_input("Chain Ring:", min_value=40, max_value=100,value=56, step=1,key="1_9")
            with c4:
                seat_height_1 = st.number_input("Seat Height:", min_value=0.50, max_value=2.00,value=1.00,key="1_10")
            st.subheader("Position 2 specs")
            c1,c2,c3,c4,c5,c6 =st.columns(6)
            with c1:
                seat_max_RPM_2 = st.number_input("Seated Max RPM:", min_value=0.01, max_value=500.00,value=260.00,key="2_1")
            with c2:
                seat_max_torque_2 = st.number_input("Seated Max Torque:", min_value=0.01, max_value=500.00,value=250.00,key="2_2")
            with c3:
                seat_CdA_2 = st.number_input("Seated CdA:", min_value=0.0001, max_value=2.0000,value=0.2380, step=1e-4, format="%.4f",key="2_3")
            with c4:
                stand_max_RPM_2 = st.number_input("Standing Max RPM:", min_value=0.01, max_value=500.00,value=260.00,key="2_4")
            with c5:
                stand_max_torque_2 = st.number_input("Standing Max Torque:", min_value=0.01, max_value=500.00,value=350.00,key="2_5")
            with c6:
                stand_CdA_2 = st.number_input("Standing CdA:", min_value=0.00, max_value=20.00,value=0.2975, step=1e-4, format="%.4f",key="2_6")
            c1,c2,c3,c4 =st.columns(4)
            with c1:
                total_mass_2 = st.number_input("Total Mass:", min_value=40.0, max_value=150.0,value=85.0, step=0.1, format="%.1f",key="2_7")
            with c2:
                sprocket_2 = st.number_input("Sprocket:", min_value=12, max_value=22,value=15, step=1,key="2_8")
            with c3:
                chainring_2 = st.number_input("Chain Ring:", min_value=40, max_value=100,value=56, step=1,key="2_9")
            with c4:
                seat_height_2 = st.number_input("Seat Height:", min_value=0.50, max_value=2.00,value=1.00,key="2_10")
            st.subheader("Position 3 specs")
            c1,c2,c3,c4,c5,c6 =st.columns(6)
            with c1:
                seat_max_RPM_3 = st.number_input("Seated Max RPM:", min_value=0.01, max_value=500.00,value=260.00,key="3_1")
            with c2:
                seat_max_torque_3 = st.number_input("Seated Max Torque:", min_value=0.01, max_value=500.00,value=250.00,key="3_2")
            with c3:
                seat_CdA_3 = st.number_input("Seated CdA:", min_value=0.0001, max_value=2.0000,value=0.2380, step=1e-4, format="%.4f",key="3_3")
            with c4:
                stand_max_RPM_3 = st.number_input("Standing Max RPM:", min_value=0.01, max_value=500.00,value=260.00,key="3_4")
            with c5:
                stand_max_torque_3 = st.number_input("Standing Max Torque:", min_value=0.01, max_value=500.00,value=350.00,key="3_5")
            with c6:
                stand_CdA_3 = st.number_input("Standing CdA:", min_value=0.00, max_value=20.00,value=0.2975, step=1e-4, format="%.4f",key="3_6")
            c1,c2,c3,c4 =st.columns(4)
            with c1:
                total_mass_3 = st.number_input("Total Mass:", min_value=40.0, max_value=150.0,value=85.0, step=0.1, format="%.1f",key="3_7")
            with c2:
                sprocket_3 = st.number_input("Sprocket:", min_value=12, max_value=22,value=15, step=1,key="3_8")
            with c3:
                chainring_3 = st.number_input("Chain Ring:", min_value=40, max_value=100,value=56, step=1,key="3_9")
            with c4:
                seat_height_3 = st.number_input("Seat Height:", min_value=0.50, max_value=2.00,value=1.00,key="3_10")
            st.subheader("Global specs")
            c1,c2,c3,c4,c5 =st.columns(5)
            with c1:
                air_Density = st.number_input("Air Density:", min_value=0.001, max_value=3.200,value=1.168,key="4_1")
            with c2:
                dist_at_sit = st.number_input("Distance at sit:", min_value=0.01, max_value=750.0,value=150.00, step=0.1, format="%.1f",key="4_2")
            with c3:
                standing_fatigue_rate = st.number_input("Standing Fatigue Rate (%):", min_value=0.01, max_value=99.99,value=1.20, step=1e-2, format="%.2f",key="4_3")
            with c4:
                seated_fatigue_rate = st.number_input("Seated Fatigue Rate (%):", min_value=0.01, max_value=99.99,value=1.20, step=1e-2, format="%.2f",key="4_4")
            with c5:
                fatigue_onset = st.number_input("Onset of Fatigue (s):", min_value=0.1, max_value=2.0,value=1.0, step=0.1, format="%.1f",key="4_5")
            
            c1,c2,c3,c4,c5 =st.columns(5)
            with c1:
                circumferences = [250,333,500]
                track_circumference = st.selectbox("Track Circumference:", circumferences, key="Track_circumference")
            with c2:
                straight_bank_angle = st.number_input("Straight Bank Angle:", min_value=0.00, max_value=90.00,value=13.00)
            with c4:
                pl_to_trans = st.number_input("Distance from Pursuit Line to Transition:", min_value=0.00, max_value=90.00,value=31.25)
            with c5:
                transition_length = st.number_input("Transition length:", min_value=0.00, max_value=90.00,value=10.00)
            with c3:
                bend_bank_angle = st.number_input("Bend Bank Angle:", min_value=0.00, max_value=90.00,value=46.13)
            submitted = st.form_submit_button("Update Specs")
            
        class Athlete:
            def __init__(self, seat_max_RPM, seat_max_torque, stand_max_RPM, stand_max_torque, stand_CdA, seat_CdA, total_mass, gear, seat_height, max_power,stand_TC_slope, seat_TC_slope):
                self.seat_max_RPM = seat_max_RPM
                self.seat_max_torque = seat_max_torque
                self.stand_max_RPM = stand_max_RPM
                self.stand_max_torque = stand_max_torque
                self.stand_CdA = stand_CdA
                self.seat_CdA = seat_CdA
                self.total_mass = total_mass
                self.gear = gear
                self.seat_height = seat_height
                self.max_power = max_power
                self.stand_TC_slope = stand_TC_slope
                self.seat_TC_slope = seat_TC_slope
                
        p1 = Athlete(seat_max_RPM_1,seat_max_torque_1,stand_max_RPM_1,stand_max_torque_1,stand_CdA_1,seat_CdA_1,total_mass_1,27*chainring_1/sprocket_1, seat_height_1, seat_max_RPM_1*seat_max_torque_1*math.pi/120,-stand_max_torque_1/stand_max_RPM_1,-seat_max_torque_1/seat_max_RPM_1)
        p2 = Athlete(seat_max_RPM_2,seat_max_torque_2,stand_max_RPM_2,stand_max_torque_2,stand_CdA_2,seat_CdA_2,total_mass_2,27*chainring_2/sprocket_2, seat_height_2, seat_max_RPM_2*seat_max_torque_2*math.pi/120,-stand_max_torque_2/stand_max_RPM_2,-seat_max_torque_2/seat_max_RPM_2)
        p3 = Athlete(seat_max_RPM_3,seat_max_torque_3,stand_max_RPM_3,stand_max_torque_3,stand_CdA_3,seat_CdA_3,total_mass_3,27*chainring_3/sprocket_3, seat_height_3, seat_max_RPM_3*seat_max_torque_3*math.pi/120,-stand_max_torque_3/stand_max_RPM_3,-seat_max_torque_3/seat_max_RPM_3)


        wheel_circ=2.096
        ks=0.0072
        mu_rr = 0.0016
        time = 0
        increment=0.1
        efficiency = 0.97
        rad_of_curve = (250 - 4*(pl_to_trans))/(2*math.pi)
        deg_to_rad = math.pi/180
        rad_to_deg = 180/math.pi
        p1.COM_speed = 2    
        p1.COM_dist = 0
        p1.CdA = p1.stand_CdA
        p1.cadence = 0
        p1.torque = stand_max_torque_1
        p1.power_input = p1.cadence*p1.torque*(math.pi/30) # Torque x cadence with a conversion term for cadence and angular velocity??
        p1.power_usable = p1.power_input*efficiency
        p1.acc_fatigue = 0
        p1.bank = straight_bank_angle
        p1.lean = 0 
        p1.camber = abs(p1.bank-p1.lean)
        p1.r_wh = 0 # wheel radius of curvature
        p1.r_cm = 0 #COM radius of curvature
        
        p1.prop_force = 2*math.pi*p1.torque/(2.096*(p1.gear/27)) #from Caddy2015
        #F_prop = torque/(GR*(D/2)) D=diameter, GR= gear ratio
        
        p1.aero_drag = (0.5*air_Density*p1.stand_CdA*p1.COM_speed**2)
        p1.weight_force = 9.81*p1.total_mass
        p1.centripetal_force = 0
        p1.reaction_force = math.sqrt(p1.weight_force**2 + p1.centripetal_force**2)
        p1.normal_force = p1.reaction_force*math.cos(deg_to_rad*p1.camber)
        p1.rr = p1.normal_force*mu_rr*(1+ (p1.camber*ks))
        
        p1.wheel_speed = 0
        p1.wheel_dist = 0
        p1.segment = p1.wheel_dist%125
        p1.accel = (p1.prop_force-(p1.rr+p1.aero_drag))/p1.total_mass

        
        
        def get_bank_lean_camber(segment,lean_initial,v_com,seat_height):
            bend_length = 125 - 2*(pl_to_trans+transition_length)
            r_wh = rad_of_curve
            if (segment < pl_to_trans) or (segment>125-pl_to_trans):
                bank = straight_bank_angle
                r_wh = 1000000
                r_cm = 1000000
            elif segment <= pl_to_trans + transition_length:
                pct_through_trans = (segment-pl_to_trans)/transition_length
                bank = straight_bank_angle + pct_through_trans*(bend_bank_angle-straight_bank_angle)
                
            elif segment<=pl_to_trans + transition_length + bend_length:
                bank = bend_bank_angle
                
            else:
                pct_through_trans = (segment-(pl_to_trans+transition_length+bend_length))/transition_length
                bank = bend_bank_angle + pct_through_trans*(straight_bank_angle-bend_bank_angle)
                
            lean_final = rad_to_deg*math.atan((v_com**2)/(9.81*(r_wh-(seat_height*math.sin(deg_to_rad*lean_initial)))))
            while lean_final-lean_initial>0.1:
                # st.write(lean_initial)
                # st.write(lean_final)
                # st.write("Those are the inital and final lean angles")
                lean_initial = lean_final
                lean_final = rad_to_deg*math.atan((v_com**2)/(9.81*(r_wh-(seat_height*math.sin(deg_to_rad*lean_final)))))
            # st.write(lean_initial)
            # st.write(lean_final)
            # st.write("These angles are close enough")
            if r_wh==rad_of_curve:
                r_cm = r_wh - seat_height*math.sin(deg_to_rad*lean_final)

            camber = bank - lean_final
            
            return bank, r_wh, r_cm, lean_final, camber
        df=pd.DataFrame()
        times = [time]
        COM_speed=[p1.COM_speed]    
        COM_dist=[p1.COM_dist]  
        bank=[p1.bank]  
        r_wh=[p1.r_wh]  
        r_cm=[p1.r_cm]  
        lean=[p1.lean]  
        camber=[p1.camber]  
        wheel_speed=[p1.wheel_speed]  
        wheel_dist=[p1.wheel_dist]  
        cadence=[p1.cadence]  
        torque=[p1.torque]  
        power_input=[p1.power_input]  
        power_usable=[p1.power_usable]  
        prop_force=[p1.prop_force]  
        aero_drag=[p1.aero_drag]  
        weight_force=[p1.weight_force]  
        segment=[p1.segment]  
        centripetal_force=[p1.centripetal_force]  
        reaction_force=[p1.reaction_force]  
        normal_force=[p1.normal_force]  
        rr=[p1.rr]  
        accel=[p1.accel]  
        
        while p1.wheel_dist<dist_at_sit:
            time+=increment
            p1.COM_speed += increment*p1.accel     
            p1.COM_dist += p1.COM_speed*increment
            p1.bank, p1.r_wh, p1.r_cm, p1.lean, p1.camber = get_bank_lean_camber(p1.segment,p1.lean,p1.COM_speed,p1.seat_height)
            p1.wheel_speed = p1.COM_speed*(p1.r_wh/p1.r_cm)
            p1.wheel_dist += p1.wheel_speed*increment
            p1.cadence = 60*p1.wheel_speed/((p1.gear/27)*wheel_circ)
            if time<fatigue_onset:
                p1.torque = p1.stand_max_torque + p1.stand_TC_slope*p1.cadence
            else:
                p1.acc_fatigue += increment*standing_fatigue_rate/100
                p1.torque = p1.stand_max_torque*(1 - p1.acc_fatigue) + (p1.stand_TC_slope*p1.cadence)
            p1.power_input = p1.cadence*p1.torque*(math.pi/30) # Torque x cadence with a conversion term for cadence and angular velocity??
            p1.power_usable = p1.power_input*efficiency
            p1.prop_force = 2*math.pi*p1.torque/(2.096*(p1.gear/27)) #from Caddy2015
            #F_prop = torque/(GR*(D/2)) D=diameter, GR= gear ratio
            p1.aero_drag = (0.5*air_Density*p1.stand_CdA*p1.COM_speed**2)
            p1.weight_force = 9.81*p1.total_mass
            p1.segment = p1.wheel_dist%125
            if (p1.segment< pl_to_trans) or (p1.segment>125-pl_to_trans):
                p1.centripetal_force = 0
            else:
                p1.centripetal_force = (p1.total_mass*p1.COM_speed**2)/p1.r_cm
            p1.reaction_force = math.sqrt(p1.weight_force**2 + p1.centripetal_force**2)
            p1.normal_force = p1.reaction_force*math.cos(deg_to_rad*p1.camber)
            p1.rr = p1.normal_force*mu_rr*(1+ (abs(p1.camber)*ks))
            p1.accel = (p1.prop_force-(p1.rr+p1.aero_drag))/p1.total_mass

            COM_speed.append(p1.COM_speed)    
            COM_dist.append(p1.COM_dist)
            bank.append(p1.bank)
            r_wh.append(p1.r_wh)
            r_cm.append(p1.r_cm)
            lean.append(p1.lean)
            camber.append(p1.camber)
            wheel_speed.append(p1.wheel_speed)
            wheel_dist.append(p1.wheel_dist)
            cadence.append(p1.cadence)
            torque.append(p1.torque)
            power_input.append(p1.power_input)
            power_usable.append(p1.power_usable)
            prop_force.append(p1.prop_force)
            aero_drag.append(p1.aero_drag)
            weight_force.append(p1.weight_force)
            segment.append(p1.segment)
            centripetal_force.append(p1.centripetal_force)
            reaction_force.append(p1.reaction_force)
            normal_force.append(p1.normal_force)
            rr.append(p1.rr)
            accel.append(p1.accel)
            times.append(time)
        p1.CdA = p1.seat_CdA
        while p1.wheel_dist<500:
            time+=increment
            p1.COM_speed += increment*p1.accel     
            p1.COM_dist += p1.COM_speed*increment
            p1.bank, p1.r_wh, p1.r_cm, p1.lean, p1.camber = get_bank_lean_camber(p1.segment,p1.lean,p1.COM_speed,p1.seat_height)
            p1.wheel_speed = p1.COM_speed*(p1.r_wh/p1.r_cm)
            p1.wheel_dist += p1.wheel_speed*increment
            p1.cadence = 60*p1.wheel_speed/((p1.gear/27)*wheel_circ)
            p1.acc_fatigue += increment*seated_fatigue_rate/100
            p1.torque = p1.seat_max_torque*(1 - p1.acc_fatigue) + (p1.seat_TC_slope*p1.cadence)
            p1.power_input = p1.cadence*p1.torque*(math.pi/30) # Torque x cadence with a conversion term for cadence and angular velocity??
            p1.power_usable = p1.power_input*efficiency
            p1.prop_force = 2*math.pi*p1.torque/(2.096*(p1.gear/27)) #from Caddy2015
            #F_prop = torque/(GR*(D/2)) D=diameter, GR= gear ratio
            p1.aero_drag = (0.5*air_Density*p1.stand_CdA*p1.COM_speed**2)
            p1.weight_force = 9.81*p1.total_mass
            p1.segment = p1.wheel_dist%125
            if (p1.segment< pl_to_trans) or (p1.segment>125-pl_to_trans):
                p1.centripetal_force = 0
            else:
                p1.centripetal_force = (p1.total_mass*p1.COM_speed**2)/p1.r_cm
            p1.reaction_force = math.sqrt(p1.weight_force**2 + p1.centripetal_force**2)
            p1.normal_force = p1.reaction_force*math.cos(deg_to_rad*p1.camber)
            p1.rr = p1.normal_force*mu_rr*(1+ (abs(p1.camber)*ks))
            p1.accel = (p1.prop_force-(p1.rr+p1.aero_drag))/p1.total_mass       
    
    
            #Appending

            COM_speed.append(p1.COM_speed)    
            COM_dist.append(p1.COM_dist)
            bank.append(p1.bank)
            r_wh.append(p1.r_wh)
            r_cm.append(p1.r_cm)
            lean.append(p1.lean)
            camber.append(p1.camber)
            wheel_speed.append(p1.wheel_speed)
            wheel_dist.append(p1.wheel_dist)
            cadence.append(p1.cadence)
            torque.append(p1.torque)
            power_input.append(p1.power_input)
            power_usable.append(p1.power_usable)
            prop_force.append(p1.prop_force)
            aero_drag.append(p1.aero_drag)
            weight_force.append(p1.weight_force)
            segment.append(p1.segment)
            centripetal_force.append(p1.centripetal_force)
            reaction_force.append(p1.reaction_force)
            normal_force.append(p1.normal_force)
            rr.append(p1.rr)
            accel.append(p1.accel)
            times.append(time)
        df["Time"]=times
        df["COM_speed"]=COM_speed
        df["COM_dist"]=COM_dist
        df["bank"]=bank
        df["r_wh"]=r_wh
        df["r_cm"]=r_cm
        df["lean"]=lean
        df["camber"]=camber
        df["wheel_speed"]=wheel_speed
        df["wheel_dist"]=wheel_dist
        df["cadence"]=cadence
        df["torque"]=torque
        df["power_input"]=power_input
        
        df["power_usable"]=power_usable
        df["prop_force"]=prop_force
        df["aero_drag"]=aero_drag
        df["weight_force"]=weight_force
        df["segment"]=segment
        df["centripetal_force"]=centripetal_force
        df["reaction_force"]=reaction_force
        df["normal_force"]=normal_force
        df["rr"]=rr
        df["accel"]=accel


        df

        fig = go.Figure()
 
        fig.add_trace(go.Line(x=df["Time"], y=df["power_input"], 
                             name="Power", yaxis='y'))
         
        fig.add_trace(go.Line(x=df["Time"], y=df["wheel_speed"], 
                              name="Wheel speed", yaxis="y2"))
         
        # Create axis objects
        fig.update_layout(xaxis=dict(domain=[0.0, 1.0]),
            #create 1st y axis              
            yaxis=dict(
                title="Power (W)",
                titlefont=dict(color="#1f77b4"),
                tickfont=dict(color="#1f77b4")),
                           
            #create 2nd y axis       
            yaxis2=dict(title="Wheel speed",overlaying="y",
                        side="right",position=1.0))
         
        # title
        fig.update_layout(
            title_text="Power and Wheel speed"
        )
         
        st.plotly_chart(fig, use_container_width=True)

        
        # fig = px.line(df,x="Time", y = "power_input", title="5 Minute Power")
        # fig.update_xaxes(title="Seconds")
        # fig.update_yaxes(title="Power (W)")
        # st.plotly_chart(fig, use_container_width=True)
        





    
    elif Calc == "Male Individual Pursuit":
        
        with st.form("my_form"):
            st.subheader("Bike Specs")
            c1,c2,c3,c4,c5,c6,c7 =st.columns(7)
            with c1:
                bike_stiffness = st.number_input("Bike Stiffness:", min_value=0.00, max_value=100.00,value=99.99)
            with c2:
                chain_efficiency = st.number_input("Chain Efficiency:", min_value=0.00, max_value=100.00,value=99.99)
            with c3:
                bearing_efficiency = st.number_input("Bearing Efficiency:", min_value=0.00, max_value=100.00,value=99.99)
            with c4:
                bike_weight = st.number_input("Bike Weight (kg):", min_value=0.00, max_value=20.00,value=8.00)
            with c5:
                wheel_radius = st.number_input("Wheel Radius (m):", min_value=0.00, max_value=1.00,value=0.33)
            with c6:
                seat_height = st.number_input("Seat Height (m):", min_value=0.00, max_value=2.00,value=0.9)
            with c7:
                gear_ratio = st.number_input("Gear Ratio:", min_value=0.00, max_value=150.00,value=113.4)
            st.subheader("Environment")
            #8 sections of the track, 4 sections where angle increases linearly from straight to bank angle (or vice versa)
            #Maybe add lengths of these sections in
            #Use circumference and bank angles to determine r_m radius of curvature for COM
            c1,c2,c3,c4,c5,c6,c7 =st.columns(7)
            with c1:
                circumferences = [250,333,500]
                track_circumference = st.selectbox("Track Circumference:", circumferences, key="Track_circumference")
            with c2:
                straight_bank_angle = st.number_input("Straight Bank Angle:", min_value=0.00, max_value=90.00,value=13.00)
            with c4:
                pl_to_trans = st.number_input("Distance from Pursuit Line to Transition:", min_value=0.00, max_value=90.00,value=31.25)
            with c5:
                transition_length = st.number_input("Transition length:", min_value=0.00, max_value=90.00,value=10.00)
            with c3:
                bend_bank_angle = st.number_input("Bend Bank Angle:", min_value=0.00, max_value=90.00,value=46.13)
            with c6:
                air_density = st.number_input("Air Density (kg/m^3):", min_value=0.0000, max_value=10.0000,value=1.1620,
            step=1e-4, format="%.4f")
            with c7:
                mu_rr = st.number_input("Rolling Resistance Coefficient:", min_value=0.0000, max_value=0.0050,value=0.0016,
            step=1e-4, format="%.4f")
            st.subheader("Rider Specs")
            c1,c2,c3,c4,c5 =st.columns(5)
            with c1:
                cda = st.number_input("CdA:", min_value=0.0000, max_value=1.0000,value=0.1858,
            step=1e-4, format="%.4f")
            with c2:
                rider_weight = st.number_input("Rider Weight (kit on):", min_value=30.00, max_value=150.00,value=83.00)
            with c3:
                vo2_max = st.number_input("VO2 Max:", min_value=0.00, max_value=100.00,value=80.00)
            with c4:
                co2_def = st.number_input("O2 Deficit:", min_value=0.00, max_value=20.00,value=20.00)
            with c5:
                max_torque = st.number_input("Max Torque (Nm):", min_value=0.00, max_value=1000.00,value=250.00)
            submitted = st.form_submit_button("Update Specs")
            
            
            ###Power profile editor
       
        with st.form("my_2nd_form"):
            st.subheader("5 Minute Power Profile Editor")
            c1, c2 = st.columns([1, 3])
            with c1:
                max_power = st.number_input("Max Power:", min_value=0.00, max_value=3000.00,value=1295.00,
            step=1e-2, format="%.2f")
                max_power_time = st.number_input("Time Max Power is Achieved:", min_value=0.00, max_value=60.00,value=9.50,
            step=1e-2, format="%.2f")
                steady_power = st.number_input("Steady State Power:", min_value=0.00, max_value=800.00,value=465.50,
            step=1e-2, format="%.2f")
                steady_power_time = st.number_input("Time Steady Power is Reached:", min_value=0.00, max_value=60.00,value=31.00,
            step=1e-2, format="%.2f")
    
            with c2:
                
                def power_profile():
                    increment=10
                    x = np.linspace(0, 300, num=300*increment + 1)
                    i = 1
                    y=np.linspace(0, 0, num=300*increment +1)
                    y[0] = 0
                    upslope = max_power/(max_power_time*increment)
                    downslope = (steady_power-max_power)/((steady_power_time-max_power_time)*(increment))
                    while x[i]<300:
                        if x[i] <= max_power_time:
                            y[i]=y[i-1]+upslope
                            i+=1
                        elif x[i]< steady_power_time:
                            y[i]=y[i-1]+downslope
                            i+=1
                        else:
                            y[i]=steady_power
                            i+=1
                    y[i]=steady_power
                    return x,y
                x,y=power_profile()
                fig = px.line(x=x, y = y, title="5 Minute Power")
                fig.update_xaxes(title="Seconds")
                fig.update_yaxes(title="Power (W)")
                st.plotly_chart(fig, use_container_width=True)
            submitted = st.form_submit_button("Update Power Profile")
    
        p_type = ["Editable Power Profile"]
        
        Profile = st.selectbox("Select Power Profile:", p_type, key="Profile_Selector")
    #     if Profile == "Dan Nationals":
    #         fig_Dan_power = px.line(df_Dan,x="time_in", y = "Power_true", title="Dan's Actual 2Hz Power Trace")
    #         #fig.update_xaxes(title="Seconds")
    #         #fig.update_yaxes(title="Power (W)")
    #         st.plotly_chart(fig_Dan_power, use_container_width=True)
    
    #         fig_Dan_w_speed = px.line(df_Dan,x="time_in", y = "w_speed_true_ms", title="Dan's Actual Speed Trace")
    #         #fig.update_xaxes(title="Seconds")
    #         #fig.update_yaxes(title="Power (W)")
    #         st.plotly_chart(fig_Dan_w_speed, use_container_width=True)
    
    #         fig_Dan_w_speed = px.line(df_Dan,x="time_in", y = "Total_Dist", title="Dan's Actual Distance V Time")
    #         #fig.update_xaxes(title="Seconds")
    #         #fig.update_yaxes(title="Power (W)")
    #         st.plotly_chart(fig_Dan_w_speed, use_container_width=True)
    
    
    
    #         ###Modelling bit
    #         bike_eff = bike_stiffness*chain_efficiency*bearing_efficiency/(1000000)
    #         curve_rad = (track_circumference-(4*pl_to_trans))/(2*math.pi)
    
    #         delta_S = 0.5
    #         k_s = 0.0072
    #         #@st.cache_data
    #         def initial_accel():
    #             gear_ratio_f = gear_ratio/27
    #             f_w = 9.80665*(bike_weight+rider_weight)
    #             mu_s = 1 + straight_bank_angle*k_s
    #             f_rr = f_w*mu_rr*mu_s
    #             a_cm = ((max_torque/(gear_ratio_f*wheel_radius)) - f_rr)/(bike_weight+rider_weight)
    #             if a_cm<0:
    #                 a_cm=0
    #             v_cm = math.sqrt(2*a_cm*delta_S)
    #             return a_cm,v_cm,f_w,f_rr
    #         a_cm,v_cm,f_w,f_rr = initial_accel()
    #     #     accel_in=[a_cm]
    #     #     v_cm_in = [0]
    #     #     v_cm_f = [v_cm]
    #     #     v_cm_av = [v_cm/2]
    #     #     delta_t = [delta_S/v_cm_av[0]]
    #     #     run_time = [delta_t]
    
    #             ###Use the (x,y) for the generic power profile editor, otherwise use proper values
    
    #         import scipy.interpolate
    #         #power_interp = scipy.interpolate.interp1d(x, y)
    #         power_interp = scipy.interpolate.interp1d(df_Dan["time_in"], df_Dan["Power_true"])
    #         interp_true_w_dist = scipy.interpolate.interp1d(df_Dan["time_in"], df_Dan["Total_Dist"])
    
    #         df=pd.DataFrame()
    
    #         df["Wheel_Dist_in(m)"]= np.linspace(0, 4000-delta_S, num=int(4000/delta_S +1)).round(1)
    #         df["true_w_dist"] = 0
    #         df["Section_in(m)"] = df["Wheel_Dist_in(m)"]%125.0
    #         df["Time_in(s)"]=0
    #         df["Speed_in"] = 0
    #         df["Wh_Speed_in"] = 0
    #         df["Bank_angle(deg)"] = straight_bank_angle
    #         df["Lean_angle(deg)"]=0 
    #         df["RC_wh"]=1
    #         df["RC_cm"]=1
    #         df["P_app_in"]=0
    #         #df["P_app_f"]=power_interp(delta_t[0])
    #         df["P_out_in"]=df["P_app_in"]*bike_eff
    #         #df["P_out_f"]=df["P_app_f"]*bike_eff
    #         df["F_d"]=0
    #         df["F_c"]=0
    #         df["F_rr"]=f_rr
    #         df["Accel"] = a_cm
    #         df["delta_S_cm"] = delta_S
    #         df["Speed_f"] = v_cm
    #         df["Wh_Speed_f"] = v_cm
    #         df["Speed_av"] = v_cm/2
    #         df["Wh_Speed_av"] = v_cm/2
    #         df["delta_t(s)"] = 2*delta_S/v_cm
    #         df["run_time"]=df["delta_t(s)"].cumsum()
    
    #         for i in range(1,len(df)):
    #             df["Time_in(s)"][i]=df["run_time"][i-1]
    #             df["Speed_in"][i]=df["Speed_f"][i-1]
    #             df["Wh_Speed_in"][i]=df["Wh_Speed_f"][i-1]
    #             df["true_w_dist"][i]=interp_true_w_dist(df["Time_in(s)"][i])
    #             if df["Time_in(s)"][i] >= 290:
    #                 df["P_app_in"][i] = steady_power
    #             else:
    #                 df["P_app_in"][i]=power_interp(df["Time_in(s)"][i])
    
    #             df["P_out_in"][i]=df["P_app_in"][i]*bike_eff
    
    #             #First Transition
    #             if (df["Section_in(m)"][i]>=pl_to_trans and df["Section_in(m)"][i]<=pl_to_trans+transition_length):
    #                 df["Bank_angle(deg)"][i] = straight_bank_angle + ((bend_bank_angle-straight_bank_angle)/(transition_length))*(df["Section_in(m)"][i]-pl_to_trans)
    
    #                 #Updating lean angle by iteration
    #                 alpha = math.radians(df["Lean_angle(deg)"][i-1])
    #                 alpha_1 = math.pi/2
    #                 while abs(alpha-alpha_1)>0.01:  
    #                     alpha=alpha_1
    #                     alpha_1 = math.atan((df["Speed_in"][i]**2)/((curve_rad-(seat_height*math.sin(alpha)))*9.80665))
    #                 df["Lean_angle(deg)"][i] = math.degrees(alpha)
    
    #                 #Updating radius of curvature for COM
    #                 df["RC_wh"][i]= curve_rad 
    #                 df["RC_cm"][i] = curve_rad - (seat_height*math.sin(math.radians(df["Lean_angle(deg)"][i])))
    
    #                 #Updating Centripetal force (only felt in corners)
    #                 df["F_c"][i]=(bike_weight+rider_weight)*(df["Speed_in"][i]**2)/df["RC_cm"][i]
    
    #                 #Updating delta_S for COM
    #                 df["delta_S_cm"][i] = delta_S*df["RC_cm"][i]/df["RC_wh"][i]
    
    #             #Corner
    #             elif (df["Section_in(m)"][i]<=(125-(pl_to_trans+transition_length)) and df["Section_in(m)"][i]>(pl_to_trans+transition_length)):
    #                 df["Bank_angle(deg)"][i] = bend_bank_angle
    
    #                 #Updating lean angle by iteration
    #                 alpha = math.radians(df["Lean_angle(deg)"][i-1])
    #                 alpha_1 = math.pi/2
    #                 while abs(alpha-alpha_1)>0.01:  
    #                     alpha=alpha_1
    #                     alpha_1 = math.atan((df["Speed_in"][i]**2)/((curve_rad-(seat_height*math.sin(alpha)))*9.80665))
    #                 df["Lean_angle(deg)"][i] = math.degrees(alpha)
    
    #                 #Updating radius of curvature for COM
    #                 df["RC_wh"][i]= curve_rad 
    #                 df["RC_cm"][i] = curve_rad - (seat_height*math.sin(math.radians(df["Lean_angle(deg)"][i])))
    
    #                 #Updating Centripetal force (only felt in corners)
    #                 df["F_c"][i]=(bike_weight+rider_weight)*(df["Speed_in"][i]**2)/df["RC_cm"][i]
    
    #                 #Updating delta_S for COM
    #                 df["delta_S_cm"][i] = delta_S*df["RC_cm"][i]/df["RC_wh"][i]
    
    #             #Second Transition
    #             elif (df["Section_in(m)"][i]>(125-(pl_to_trans+transition_length)) and df["Section_in(m)"][i]<=(125-pl_to_trans)):
    #                 df["Bank_angle(deg)"][i] = bend_bank_angle + ((straight_bank_angle-bend_bank_angle)/(transition_length))*(df["Section_in(m)"][i]-(125-pl_to_trans-transition_length))
    
    #                 #Updating lean angle by iteration
    #                 alpha = math.radians(df["Lean_angle(deg)"][i-1])
    #                 alpha_1 = math.pi/2
    #                 while abs(alpha-alpha_1)>0.01:  
    #                     alpha=alpha_1
    #                     alpha_1 = math.atan((df["Speed_in"][i]**2)/((curve_rad-(seat_height*math.sin(alpha)))*9.80665))
    #                 df["Lean_angle(deg)"][i] = math.degrees(alpha)
    
    #                 #Updating radius of curvature for COM
    #                 df["RC_wh"][i]= curve_rad 
    #                 df["RC_cm"][i] = curve_rad - (seat_height*math.sin(math.radians(df["Lean_angle(deg)"][i])))
    
    #                 #Updating Centripetal force (only felt in corners)
    #                 df["F_c"][i]=(bike_weight+rider_weight)*(df["Speed_in"][i]**2)/df["RC_cm"][i]
    
    #                 #Updating delta_S for COM
    #                 df["delta_S_cm"][i] = delta_S*df["RC_cm"][i]/df["RC_wh"][i]
    
    #             #Updating rolling resistance and drag froces, and acceleration 
    #             df["F_rr"][i]= math.sqrt(f_w**2 + (df["F_c"][i]**2))*math.cos(math.radians(df["Bank_angle(deg)"][i]-df["Lean_angle(deg)"][i]))*mu_rr*(1 + abs(df["Bank_angle(deg)"][i]-df["Lean_angle(deg)"][i])*k_s)
    
    #             df["F_d"][i] = 0.5*air_density*cda*(df["Speed_in"][i]**2)
    
    #             df["Accel"][i] = ((df["P_out_in"][i]/df["Speed_in"][i]) - df["F_d"][i] - (df["F_rr"][i]*df["RC_wh"][i]/df["RC_cm"][i]))/(bike_weight+rider_weight)
    
    #             df["Speed_f"][i]= math.sqrt(df["Speed_in"][i]**2 + 2*df["Accel"][i]*df["delta_S_cm"][i])
    #             df["Wh_Speed_f"][i]= math.sqrt(df["Wh_Speed_in"][i]**2 + 2*df["Accel"][i]*delta_S)
    #             df["Speed_av"][i] =(df["Speed_in"][i]+df["Speed_f"][i])/2
    #             df["Wh_Speed_av"][i] =(df["Wh_Speed_in"][i]+df["Wh_Speed_f"][i])/2
    #             df["delta_t(s)"][i]= df["delta_S_cm"][i]/df["Speed_av"][i]
    #             df["run_time"][i] = sum(df["delta_t(s)"][0:i+1])
    
    #         st.subheader("Using Dan's Power profile as input to our model")
    #         df
    #         st.write("Wheel Distance travelled " + str((len(df)-1)*delta_S))
    #         st.write("COM Distance travelled " + str(round(sum(df["delta_S_cm"]),2)))
    #         ind_62_5 = df.index[df["Wheel_Dist_in(m)"]+delta_S==62.5]
    #         ind_125 = df.index[df["Wheel_Dist_in(m)"]+delta_S==125]
    #         ind_187_5 = df.index[df["Wheel_Dist_in(m)"]+delta_S==187.5]
    #         ind_250 = df.index[df["Wheel_Dist_in(m)"]+delta_S==250]
    #         st.write("First quarter in " + str(round(df["run_time"][ind_62_5[0]],2)))
    #         st.write("First half in " + str(round(df["run_time"][ind_125[0]],2)))
    #         st.write("First three quarter in " + str(round(df["run_time"][ind_187_5[0]],2)))
    #         st.write("First lap in " + str(round(df["run_time"][ind_250[0]],2)))
    #         time = str(pd.to_datetime(df["run_time"][len(df)-1],unit="s")).split(" ")[1]
    #         st.write("Final Time " + str(time[3:12]))
    #         st.write("Actual was 4:15.4")
    
    
    #         ###PLOTS
    
    #         fig_Dist_comp = px.line(df,x="Time_in(s)", y = ["Wheel_Dist_in(m)","true_w_dist"], title="Dist compare")
    #         #fig.update_xaxes(title="Seconds")
    #         #fig.update_yaxes(title="Power (W)")
    #         st.plotly_chart(fig_Dist_comp, use_container_width=True)
    
    #         fig_Dan_power = px.line(df_Dan,x="time_in", y = "Power_true", title="Dan's Power trace from Goldmine (2hz)")
    #         #fig.update_xaxes(title="Seconds")
    #         #fig.update_yaxes(title="Power (W)")
    #         st.plotly_chart(fig_Dan_power, use_container_width=True)
    
    
    #         fig_power_in = px.line(df,x="run_time", y = "P_app_in", title="Our power Trace")
    #         #fig.update_xaxes(title="Seconds")
    #         #fig.update_yaxes(title="Power (W)")
    #         st.plotly_chart(fig_power_in, use_container_width=True)
    
    #         fig_speed = px.line(df,x="Wheel_Dist_in(m)", y = "Speed_av", title="Our Speed Trace")
    #         #fig.update_xaxes(title="Seconds")
    #         #fig.update_yaxes(title="Power (W)")
    #         st.plotly_chart(fig_speed, use_container_width=True)
    
    #         fig_speed_time = px.line(df,x="run_time", y = "Speed_av", title="Our COM Speed Trace over Time")
    #         #fig.update_xaxes(title="Seconds")
    #         #fig.update_yaxes(title="Power (W)")
    #         st.plotly_chart(fig_speed_time, use_container_width=True)
    
    #         fig_speed_wh = px.line(df,x="run_time", y = "Wh_Speed_in", title="Our Wheel Speed Trace over Time")
    #         #fig.update_xaxes(title="Seconds")
    #         #fig.update_yaxes(title="Power (W)")
    #         st.plotly_chart(fig_speed_wh, use_container_width=True)
    
    #         fig_speed_in = px.line(df,x="Wheel_Dist_in(m)", y = "Speed_in", title="Our Initial COM Speed Trace")
    #         #fig.update_xaxes(title="Seconds")
    #         #fig.update_yaxes(title="Power (W)")
    #         st.plotly_chart(fig_speed_in, use_container_width=True)
    
    #         fig_dist = px.line(df,y="Wheel_Dist_in(m)", x = "run_time", title="Our Distance V Time")
    #         #fig.update_xaxes(title="Seconds")
    #         #fig.update_yaxes(title="Power (W)")
    #         st.plotly_chart(fig_dist, use_container_width=True)
            
    
            
            
            
            
            
    
       
        ###Modelling bit - most comes from the paper The effects of forward rotation of posture on computer-simulated 4-km track cycling: Implications of Union Cycliste Internationale rule 1.3.013 by Caddy et al
        bike_eff = bike_stiffness*chain_efficiency*bearing_efficiency/(1000000)
        curve_rad = (track_circumference-(4*pl_to_trans))/(2*math.pi)# radius of curvature in the bends - assumes semicircles

        delta_S = 0.5 #distance step
        k_s = 0.0072 #scrubbing constant from Lukes et al - used to describe relationship between bank angle and scrubbing coefficient
        #@st.cache_data
        def initial_accel():
            gear_ratio_f = gear_ratio/27
            f_w = 9.80665*(bike_weight+rider_weight) #weight force
            mu_s = 1 + straight_bank_angle*k_s #scurbbing coefficient 
            f_rr = f_w*mu_rr*mu_s
            a_cm = ((max_torque/(gear_ratio_f*wheel_radius)) - f_rr)/(bike_weight+rider_weight)
            if a_cm<0:
                a_cm=0
            v_cm = math.sqrt(2*a_cm*delta_S)
            return a_cm,v_cm,f_w,f_rr
        a_cm,v_cm,f_w,f_rr = initial_accel()
    #     accel_in=[a_cm]
    #     v_cm_in = [0]
    #     v_cm_f = [v_cm]
    #     v_cm_av = [v_cm/2]
    #     delta_t = [delta_S/v_cm_av[0]]
    #     run_time = [delta_t]

            ###Use the (x,y) for the generic power profile editor, otherwise use proper values

        import scipy.interpolate
        power_interp = scipy.interpolate.interp1d(x, y)
        #power_interp = scipy.interpolate.interp1d(df_Dan["time_in"], df_Dan["Power_true"])
        #interp_true_w_dist = scipy.interpolate.interp1d(df_Dan["time_in"], df_Dan["Total_Dist"])

        df=pd.DataFrame()

        df["Wheel_Dist_in(m)"]= np.linspace(0, 4000-delta_S, num=int(4000/delta_S +1)).round(1)
        #df["true_w_dist"] = 0
        df["Section_in(m)"] = df["Wheel_Dist_in(m)"]%125.0
        df["Time_in(s)"]=0
        df["Speed_in"] = 0
        df["Wh_Speed_in"] = 0
        df["Bank_angle(deg)"] = straight_bank_angle
        df["Lean_angle(deg)"]=0 
        df["RC_wh"]=1
        df["RC_cm"]=1
        df["P_app_in"]=0
        #df["P_app_f"]=power_interp(delta_t[0])
        df["P_out_in"]=df["P_app_in"]*bike_eff
        #df["P_out_f"]=df["P_app_f"]*bike_eff
        df["F_d"]=0
        df["F_c"]=0
        df["F_rr"]=f_rr
        df["Accel"] = a_cm
        df["delta_S_cm"] = delta_S
        df["Speed_f"] = v_cm
        df["Wh_Speed_f"] = v_cm
        df["Speed_av"] = v_cm/2
        df["Wh_Speed_av"] = v_cm/2
        df["delta_t(s)"] = 2*delta_S/v_cm
        df["run_time"]=df["delta_t(s)"].cumsum()

        for i in range(1,len(df)):
            df["Time_in(s)"][i]=df["run_time"][i-1]
            df["Speed_in"][i]=df["Speed_f"][i-1]
            df["Wh_Speed_in"][i]=df["Wh_Speed_f"][i-1]
            #df["true_w_dist"][i]=interp_true_w_dist(df["Time_in(s)"][i])
            if df["Time_in(s)"][i] >= 290:
                df["P_app_in"][i] = steady_power
            else:
                df["P_app_in"][i]=power_interp(df["Time_in(s)"][i])

            df["P_out_in"][i]=df["P_app_in"][i]*bike_eff

            #First Transition
            if (df["Section_in(m)"][i]>=pl_to_trans and df["Section_in(m)"][i]<=pl_to_trans+transition_length):
                df["Bank_angle(deg)"][i] = straight_bank_angle + ((bend_bank_angle-straight_bank_angle)/(transition_length))*(df["Section_in(m)"][i]-pl_to_trans)

                #Updating lean angle by iteration
                alpha = math.radians(df["Lean_angle(deg)"][i-1])
                alpha_1 = math.pi/2
                while abs(alpha-alpha_1)>0.01:  
                    alpha=alpha_1
                    alpha_1 = math.atan((df["Speed_in"][i]**2)/((curve_rad-(seat_height*math.sin(alpha)))*9.80665))
                df["Lean_angle(deg)"][i] = math.degrees(alpha)

                #Updating radius of curvature for COM
                df["RC_wh"][i]= curve_rad 
                df["RC_cm"][i] = curve_rad - (seat_height*math.sin(math.radians(df["Lean_angle(deg)"][i])))

                #Updating Centripetal force (only felt in corners)
                df["F_c"][i]=(bike_weight+rider_weight)*(df["Speed_in"][i]**2)/df["RC_cm"][i]

                #Updating delta_S for COM
                df["delta_S_cm"][i] = delta_S*df["RC_cm"][i]/df["RC_wh"][i]

            #Corner
            elif (df["Section_in(m)"][i]<=(125-(pl_to_trans+transition_length)) and df["Section_in(m)"][i]>(pl_to_trans+transition_length)):
                df["Bank_angle(deg)"][i] = bend_bank_angle

                #Updating lean angle by iteration
                alpha = math.radians(df["Lean_angle(deg)"][i-1])
                alpha_1 = math.pi/2
                while abs(alpha-alpha_1)>0.01:  
                    alpha=alpha_1
                    alpha_1 = math.atan((df["Speed_in"][i]**2)/((curve_rad-(seat_height*math.sin(alpha)))*9.80665))
                df["Lean_angle(deg)"][i] = math.degrees(alpha)

                #Updating radius of curvature for COM
                df["RC_wh"][i]= curve_rad 
                df["RC_cm"][i] = curve_rad - (seat_height*math.sin(math.radians(df["Lean_angle(deg)"][i])))

                #Updating Centripetal force (only felt in corners)
                df["F_c"][i]=(bike_weight+rider_weight)*(df["Speed_in"][i]**2)/df["RC_cm"][i]

                #Updating delta_S for COM
                df["delta_S_cm"][i] = delta_S*df["RC_cm"][i]/df["RC_wh"][i]

            #Second Transition
            elif (df["Section_in(m)"][i]>(125-(pl_to_trans+transition_length)) and df["Section_in(m)"][i]<=(125-pl_to_trans)):
                df["Bank_angle(deg)"][i] = bend_bank_angle + ((straight_bank_angle-bend_bank_angle)/(transition_length))*(df["Section_in(m)"][i]-(125-pl_to_trans-transition_length))

                #Updating lean angle by iteration
                alpha = math.radians(df["Lean_angle(deg)"][i-1])
                alpha_1 = math.pi/2
                while abs(alpha-alpha_1)>0.01:  
                    alpha=alpha_1
                    alpha_1 = math.atan((df["Speed_in"][i]**2)/((curve_rad-(seat_height*math.sin(alpha)))*9.80665))
                df["Lean_angle(deg)"][i] = math.degrees(alpha)

                #Updating radius of curvature for COM
                df["RC_wh"][i]= curve_rad 
                df["RC_cm"][i] = curve_rad - (seat_height*math.sin(math.radians(df["Lean_angle(deg)"][i])))

                #Updating Centripetal force (only felt in corners)
                df["F_c"][i]=(bike_weight+rider_weight)*(df["Speed_in"][i]**2)/df["RC_cm"][i]

                #Updating delta_S for COM
                df["delta_S_cm"][i] = delta_S*df["RC_cm"][i]/df["RC_wh"][i]

            #Updating rolling resistance and drag forces, and acceleration 
            df["F_rr"][i]= math.sqrt(f_w**2 + (df["F_c"][i]**2))*math.cos(math.radians(df["Bank_angle(deg)"][i]-df["Lean_angle(deg)"][i]))*mu_rr*(1 + abs(df["Bank_angle(deg)"][i]-df["Lean_angle(deg)"][i])*k_s)

            df["F_d"][i] = 0.5*air_density*cda*(df["Speed_in"][i]**2)

            df["Accel"][i] = ((df["P_out_in"][i]/df["Speed_in"][i]) - df["F_d"][i] - (df["F_rr"][i]*df["RC_wh"][i]/df["RC_cm"][i]))/(bike_weight+rider_weight)

            df["Speed_f"][i]= math.sqrt(df["Speed_in"][i]**2 + 2*df["Accel"][i]*df["delta_S_cm"][i])
            df["Wh_Speed_f"][i]= math.sqrt(df["Wh_Speed_in"][i]**2 + 2*df["Accel"][i]*delta_S)
            df["Speed_av"][i] =(df["Speed_in"][i]+df["Speed_f"][i])/2
            df["Wh_Speed_av"][i] =(df["Wh_Speed_in"][i]+df["Wh_Speed_f"][i])/2
            df["delta_t(s)"][i]= df["delta_S_cm"][i]/df["Speed_av"][i]
            df["run_time"][i] = sum(df["delta_t(s)"][0:i+1])

        st.subheader("Using Editable Power Profile as input to our model")
        df
        st.write("Wheel Distance travelled " + str((len(df)-1)*delta_S))
        st.write("COM Distance travelled " + str(round(sum(df["delta_S_cm"]),2)))
        ind_62_5 = df.index[df["Wheel_Dist_in(m)"]+delta_S==62.5]
        ind_125 = df.index[df["Wheel_Dist_in(m)"]+delta_S==125]
        ind_187_5 = df.index[df["Wheel_Dist_in(m)"]+delta_S==187.5]
        ind_250 = df.index[df["Wheel_Dist_in(m)"]+delta_S==250]
        st.write("First quarter in " + str(round(df["run_time"][ind_62_5[0]],2)))
        st.write("First half in " + str(round(df["run_time"][ind_125[0]],2)))
        st.write("First three quarter in " + str(round(df["run_time"][ind_187_5[0]],2)))
        st.write("First lap in " + str(round(df["run_time"][ind_250[0]],2)))
        time = str(pd.to_datetime(df["run_time"][len(df)-1],unit="s")).split(" ")[1]
        st.write("Final Time " + str(time[3:12]))
        st.write("Actual was 4:15.4")

   ###PLOTS

        fig_Dist_comp = px.line(df,x="Time_in(s)", y = "Wheel_Dist_in(m)", title="Dist compare")
        #fig.update_xaxes(title="Seconds")
        #fig.update_yaxes(title="Power (W)")
        st.plotly_chart(fig_Dist_comp, use_container_width=True)

        


        fig_power_in = px.line(df,x="run_time", y = "P_app_in", title="Our power Trace")
        #fig.update_xaxes(title="Seconds")
        #fig.update_yaxes(title="Power (W)")
        st.plotly_chart(fig_power_in, use_container_width=True)

        fig_speed = px.line(df,x="Wheel_Dist_in(m)", y = "Speed_av", title="Our Speed Trace")
        #fig.update_xaxes(title="Seconds")
        #fig.update_yaxes(title="Power (W)")
        st.plotly_chart(fig_speed, use_container_width=True)

        fig_speed_time = px.line(df,x="run_time", y = "Speed_av", title="Our COM Speed Trace over Time")
        #fig.update_xaxes(title="Seconds")
        #fig.update_yaxes(title="Power (W)")
        st.plotly_chart(fig_speed_time, use_container_width=True)

        fig_speed_wh = px.line(df,x="run_time", y = "Wh_Speed_in", title="Our Wheel Speed Trace over Time")
        #fig.update_xaxes(title="Seconds")
        #fig.update_yaxes(title="Power (W)")
        st.plotly_chart(fig_speed_wh, use_container_width=True)

        fig_speed_in = px.line(df,x="Wheel_Dist_in(m)", y = "Speed_in", title="Our Initial COM Speed Trace")
        #fig.update_xaxes(title="Seconds")
        #fig.update_yaxes(title="Power (W)")
        st.plotly_chart(fig_speed_in, use_container_width=True)

        fig_dist = px.line(df,y="Wheel_Dist_in(m)", x = "run_time", title="Our Distance V Time")
        #fig.update_xaxes(title="Seconds")
        #fig.update_yaxes(title="Power (W)")
        st.plotly_chart(fig_dist, use_container_width=True)
        
        
        
        
        
        
        
#     if Profile == "Bryony Comm Games Qual":
#         fig_Dan_power = px.line(df_B,x="time_in", y = "Power_true", title="B's Actual 2Hz Power Trace")
#         #fig.update_xaxes(title="Seconds")
#         #fig.update_yaxes(title="Power (W)")
#         st.plotly_chart(fig_Dan_power, use_container_width=True)

        

#         fig_Dan_w_speed = px.line(df_B,x="time_in", y = "Total_Dist", title="B's Actual Distance V Time")
#         #fig.update_xaxes(title="Seconds")
#         #fig.update_yaxes(title="Power (W)")
#         st.plotly_chart(fig_Dan_w_speed, use_container_width=True)



#         ###Modelling bit
#         bike_eff = bike_stiffness*chain_efficiency*bearing_efficiency/(1000000)
#         curve_rad = (track_circumference-(4*pl_to_trans))/(2*math.pi)

#         delta_S = 0.5
#         k_s = 0.0072
#         #@st.cache_data
#         def initial_accel():
#             gear_ratio_f = gear_ratio/27
#             f_w = 9.80665*(bike_weight+rider_weight)
#             mu_s = 1 + straight_bank_angle*k_s
#             f_rr = f_w*mu_rr*mu_s
#             a_cm = ((max_torque/(gear_ratio_f*wheel_radius)) - f_rr)/(bike_weight+rider_weight)
#             if a_cm<0:
#                 a_cm=0
#             v_cm = math.sqrt(2*a_cm*delta_S)
#             return a_cm,v_cm,f_w,f_rr
#         a_cm,v_cm,f_w,f_rr = initial_accel()
#     #     accel_in=[a_cm]
#     #     v_cm_in = [0]
#     #     v_cm_f = [v_cm]
#     #     v_cm_av = [v_cm/2]
#     #     delta_t = [delta_S/v_cm_av[0]]
#     #     run_time = [delta_t]

#             ###Use the (x,y) for the generic power profile editor, otherwise use proper values

#         import scipy.interpolate
#         #power_interp = scipy.interpolate.interp1d(x, y)
#         power_interp = scipy.interpolate.interp1d(df_B["time_in"], df_B["Power_true"])
#         #interp_true_w_dist = scipy.interpolate.interp1d(df_Dan["time_in"], df_Dan["Total_Dist"])

#         df=pd.DataFrame()

#         df["Wheel_Dist_in(m)"]= np.linspace(0, 3000-delta_S, num=int(3000/delta_S +1)).round(1)
#         #df["true_w_dist"] = 0
#         df["Section_in(m)"] = df["Wheel_Dist_in(m)"]%125.0
#         df["Time_in(s)"]=0
#         df["Speed_in"] = 0
#         df["Wh_Speed_in"] = 0
#         df["Bank_angle(deg)"] = straight_bank_angle
#         df["Lean_angle(deg)"]=0 
#         df["RC_wh"]=1
#         df["RC_cm"]=1
#         df["P_app_in"]=0
#         #df["P_app_f"]=power_interp(delta_t[0])
#         df["P_out_in"]=df["P_app_in"]*bike_eff
#         #df["P_out_f"]=df["P_app_f"]*bike_eff
#         df["F_d"]=0
#         df["F_c"]=0
#         df["F_rr"]=f_rr
#         df["Accel"] = a_cm
#         df["delta_S_cm"] = delta_S
#         df["Speed_f"] = v_cm
#         df["Wh_Speed_f"] = v_cm
#         df["Speed_av"] = v_cm/2
#         df["Wh_Speed_av"] = v_cm/2
#         df["delta_t(s)"] = 2*delta_S/v_cm
#         df["run_time"]=df["delta_t(s)"].cumsum()

#         for i in range(1,len(df)):
#             df["Time_in(s)"][i]=df["run_time"][i-1]
#             df["Speed_in"][i]=df["Speed_f"][i-1]
#             df["Wh_Speed_in"][i]=df["Wh_Speed_f"][i-1]
#             #df["true_w_dist"][i]=interp_true_w_dist(df["Time_in(s)"][i])
#             if df["Time_in(s)"][i] >= 196:
#                 df["P_app_in"][i] = 380
#             else:
#                 df["P_app_in"][i]=power_interp(df["Time_in(s)"][i])

#             df["P_out_in"][i]=df["P_app_in"][i]*bike_eff

#             #First Transition
#             if (df["Section_in(m)"][i]>=pl_to_trans and df["Section_in(m)"][i]<=pl_to_trans+transition_length):
#                 df["Bank_angle(deg)"][i] = straight_bank_angle + ((bend_bank_angle-straight_bank_angle)/(transition_length))*(df["Section_in(m)"][i]-pl_to_trans)

#                 #Updating lean angle by iteration
#                 alpha = math.radians(df["Lean_angle(deg)"][i-1])
#                 alpha_1 = math.pi/2
#                 while abs(alpha-alpha_1)>0.01:  
#                     alpha=alpha_1
#                     alpha_1 = math.atan((df["Speed_in"][i]**2)/((curve_rad-(seat_height*math.sin(alpha)))*9.80665))
#                 df["Lean_angle(deg)"][i] = math.degrees(alpha)

#                 #Updating radius of curvature for COM
#                 df["RC_wh"][i]= curve_rad 
#                 df["RC_cm"][i] = curve_rad - (seat_height*math.sin(math.radians(df["Lean_angle(deg)"][i])))

#                 #Updating Centripetal force (only felt in corners)
#                 df["F_c"][i]=(bike_weight+rider_weight)*(df["Speed_in"][i]**2)/df["RC_cm"][i]

#                 #Updating delta_S for COM
#                 df["delta_S_cm"][i] = delta_S*df["RC_cm"][i]/df["RC_wh"][i]

#             #Corner
#             elif (df["Section_in(m)"][i]<=(125-(pl_to_trans+transition_length)) and df["Section_in(m)"][i]>(pl_to_trans+transition_length)):
#                 df["Bank_angle(deg)"][i] = bend_bank_angle

#                 #Updating lean angle by iteration
#                 alpha = math.radians(df["Lean_angle(deg)"][i-1])
#                 alpha_1 = math.pi/2
#                 while abs(alpha-alpha_1)>0.01:  
#                     alpha=alpha_1
#                     alpha_1 = math.atan((df["Speed_in"][i]**2)/((curve_rad-(seat_height*math.sin(alpha)))*9.80665))
#                 df["Lean_angle(deg)"][i] = math.degrees(alpha)

#                 #Updating radius of curvature for COM
#                 df["RC_wh"][i]= curve_rad 
#                 df["RC_cm"][i] = curve_rad - (seat_height*math.sin(math.radians(df["Lean_angle(deg)"][i])))

#                 #Updating Centripetal force (only felt in corners)
#                 df["F_c"][i]=(bike_weight+rider_weight)*(df["Speed_in"][i]**2)/df["RC_cm"][i]

#                 #Updating delta_S for COM
#                 df["delta_S_cm"][i] = delta_S*df["RC_cm"][i]/df["RC_wh"][i]

#             #Second Transition
#             elif (df["Section_in(m)"][i]>(125-(pl_to_trans+transition_length)) and df["Section_in(m)"][i]<=(125-pl_to_trans)):
#                 df["Bank_angle(deg)"][i] = bend_bank_angle + ((straight_bank_angle-bend_bank_angle)/(transition_length))*(df["Section_in(m)"][i]-(125-pl_to_trans-transition_length))

#                 #Updating lean angle by iteration
#                 alpha = math.radians(df["Lean_angle(deg)"][i-1])
#                 alpha_1 = math.pi/2
#                 while abs(alpha-alpha_1)>0.01:  
#                     alpha=alpha_1
#                     alpha_1 = math.atan((df["Speed_in"][i]**2)/((curve_rad-(seat_height*math.sin(alpha)))*9.80665))
#                 df["Lean_angle(deg)"][i] = math.degrees(alpha)

#                 #Updating radius of curvature for COM
#                 df["RC_wh"][i]= curve_rad 
#                 df["RC_cm"][i] = curve_rad - (seat_height*math.sin(math.radians(df["Lean_angle(deg)"][i])))

#                 #Updating Centripetal force (only felt in corners)
#                 df["F_c"][i]=(bike_weight+rider_weight)*(df["Speed_in"][i]**2)/df["RC_cm"][i]

#                 #Updating delta_S for COM
#                 df["delta_S_cm"][i] = delta_S*df["RC_cm"][i]/df["RC_wh"][i]

#             #Updating rolling resistance and drag froces, and acceleration 
#             df["F_rr"][i]= math.sqrt(f_w**2 + (df["F_c"][i]**2))*math.cos(math.radians(df["Bank_angle(deg)"][i]-df["Lean_angle(deg)"][i]))*mu_rr*(1 + abs(df["Bank_angle(deg)"][i]-df["Lean_angle(deg)"][i])*k_s)

#             df["F_d"][i] = 0.5*air_density*cda*(df["Speed_in"][i]**2)

#             df["Accel"][i] = ((df["P_out_in"][i]/df["Speed_in"][i]) - df["F_d"][i] - (df["F_rr"][i]*df["RC_wh"][i]/df["RC_cm"][i]))/(bike_weight+rider_weight)

#             df["Speed_f"][i]= math.sqrt(df["Speed_in"][i]**2 + 2*df["Accel"][i]*df["delta_S_cm"][i])
#             df["Wh_Speed_f"][i]= math.sqrt(df["Wh_Speed_in"][i]**2 + 2*df["Accel"][i]*delta_S)
#             df["Speed_av"][i] =(df["Speed_in"][i]+df["Speed_f"][i])/2
#             df["Wh_Speed_av"][i] =(df["Wh_Speed_in"][i]+df["Wh_Speed_f"][i])/2
#             df["delta_t(s)"][i]= df["delta_S_cm"][i]/df["Speed_av"][i]
#             df["run_time"][i] = sum(df["delta_t(s)"][0:i+1])

#         st.subheader("Using B's Power profile as input to our model")
#         df
#         st.write("Wheel Distance travelled " + str((len(df)-1)*delta_S))
#         st.write("COM Distance travelled " + str(round(sum(df["delta_S_cm"]),2)))
#         ind_62_5 = df.index[df["Wheel_Dist_in(m)"]+delta_S==62.5]
#         ind_125 = df.index[df["Wheel_Dist_in(m)"]+delta_S==125]
#         ind_187_5 = df.index[df["Wheel_Dist_in(m)"]+delta_S==187.5]
#         ind_250 = df.index[df["Wheel_Dist_in(m)"]+delta_S==250]
#         st.write("First quarter in " + str(round(df["run_time"][ind_62_5[0]],2)))
#         st.write("First half in " + str(round(df["run_time"][ind_125[0]],2)))
#         st.write("First three quarter in " + str(round(df["run_time"][ind_187_5[0]],2)))
#         st.write("First lap in " + str(round(df["run_time"][ind_250[0]],2)))
#         time = str(pd.to_datetime(df["run_time"][len(df)-1],unit="s")).split(" ")[1]
#         st.write("Final Time " + str(time[3:12]))
#         st.write("Actual was 3:19.8")


#         ###PLOTS

#         fig_Dist_comp = px.line(df,x="Time_in(s)", y = "Wheel_Dist_in(m)", title="Dist Trace")
#         #fig.update_xaxes(title="Seconds")
#         #fig.update_yaxes(title="Power (W)")
#         st.plotly_chart(fig_Dist_comp, use_container_width=True)

#         fig_Dan_power = px.line(df_B,x="time_in", y = "Power_true", title="B's Power trace from Goldmine (2hz)")
#         #fig.update_xaxes(title="Seconds")
#         #fig.update_yaxes(title="Power (W)")
#         st.plotly_chart(fig_Dan_power, use_container_width=True)


#         fig_power_in = px.line(df,x="run_time", y = "P_app_in", title="Our power Trace")
#         #fig.update_xaxes(title="Seconds")
#         #fig.update_yaxes(title="Power (W)")
#         st.plotly_chart(fig_power_in, use_container_width=True)

#         fig_speed = px.line(df,x="Wheel_Dist_in(m)", y = "Speed_av", title="Our Speed Trace")
#         #fig.update_xaxes(title="Seconds")
#         #fig.update_yaxes(title="Power (W)")
#         st.plotly_chart(fig_speed, use_container_width=True)

#         fig_speed_time = px.line(df,x="run_time", y = "Speed_av", title="Our COM Speed Trace over Time")
#         #fig.update_xaxes(title="Seconds")
#         #fig.update_yaxes(title="Power (W)")
#         st.plotly_chart(fig_speed_time, use_container_width=True)

#         fig_speed_wh = px.line(df,x="run_time", y = "Wh_Speed_in", title="Our Wheel Speed Trace over Time")
#         #fig.update_xaxes(title="Seconds")
#         #fig.update_yaxes(title="Power (W)")
#         st.plotly_chart(fig_speed_wh, use_container_width=True)

#         fig_speed_in = px.line(df,x="Wheel_Dist_in(m)", y = "Speed_in", title="Our Initial COM Speed Trace")
#         #fig.update_xaxes(title="Seconds")
#         #fig.update_yaxes(title="Power (W)")
#         st.plotly_chart(fig_speed_in, use_container_width=True)

#         fig_dist = px.line(df,y="Wheel_Dist_in(m)", x = "run_time", title="Our Distance V Time")
#         #fig.update_xaxes(title="Seconds")
#         #fig.update_yaxes(title="Power (W)")
#         st.plotly_chart(fig_dist, use_container_width=True)