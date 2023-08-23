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


    
    
    
    calcs = ["Power for Speed","Time for Power","CdA at Speed"]
    
    Calc = st.selectbox("Select Calculator:", calcs, key="Calc_selector")
    
    
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

    p_type = ["Bryony Comm Games Qual","Dan Nationals","Editable Power Profile"]
    
    Profile = st.selectbox("Select Power Profile:", p_type, key="Profile_Selector")
    if Profile == "Dan Nationals":
        fig_Dan_power = px.line(df_Dan,x="time_in", y = "Power_true", title="Dan's Actual 2Hz Power Trace")
        #fig.update_xaxes(title="Seconds")
        #fig.update_yaxes(title="Power (W)")
        st.plotly_chart(fig_Dan_power, use_container_width=True)

        fig_Dan_w_speed = px.line(df_Dan,x="time_in", y = "w_speed_true_ms", title="Dan's Actual Speed Trace")
        #fig.update_xaxes(title="Seconds")
        #fig.update_yaxes(title="Power (W)")
        st.plotly_chart(fig_Dan_w_speed, use_container_width=True)

        fig_Dan_w_speed = px.line(df_Dan,x="time_in", y = "Total_Dist", title="Dan's Actual Distance V Time")
        #fig.update_xaxes(title="Seconds")
        #fig.update_yaxes(title="Power (W)")
        st.plotly_chart(fig_Dan_w_speed, use_container_width=True)



        ###Modelling bit
        bike_eff = bike_stiffness*chain_efficiency*bearing_efficiency/(1000000)
        curve_rad = (track_circumference-(4*pl_to_trans))/(2*math.pi)

        delta_S = 0.5
        k_s = 0.0072
        #@st.cache_data
        def initial_accel():
            gear_ratio_f = gear_ratio/27
            f_w = 9.80665*(bike_weight+rider_weight)
            mu_s = 1 + straight_bank_angle*k_s
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
        #power_interp = scipy.interpolate.interp1d(x, y)
        power_interp = scipy.interpolate.interp1d(df_Dan["time_in"], df_Dan["Power_true"])
        interp_true_w_dist = scipy.interpolate.interp1d(df_Dan["time_in"], df_Dan["Total_Dist"])

        df=pd.DataFrame()

        df["Wheel_Dist_in(m)"]= np.linspace(0, 4000-delta_S, num=int(4000/delta_S +1)).round(1)
        df["true_w_dist"] = 0
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
            df["true_w_dist"][i]=interp_true_w_dist(df["Time_in(s)"][i])
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

            #Updating rolling resistance and drag froces, and acceleration 
            df["F_rr"][i]= math.sqrt(f_w**2 + (df["F_c"][i]**2))*math.cos(math.radians(df["Bank_angle(deg)"][i]-df["Lean_angle(deg)"][i]))*mu_rr*(1 + abs(df["Bank_angle(deg)"][i]-df["Lean_angle(deg)"][i])*k_s)

            df["F_d"][i] = 0.5*air_density*cda*(df["Speed_in"][i]**2)

            df["Accel"][i] = ((df["P_out_in"][i]/df["Speed_in"][i]) - df["F_d"][i] - (df["F_rr"][i]*df["RC_wh"][i]/df["RC_cm"][i]))/(bike_weight+rider_weight)

            df["Speed_f"][i]= math.sqrt(df["Speed_in"][i]**2 + 2*df["Accel"][i]*df["delta_S_cm"][i])
            df["Wh_Speed_f"][i]= math.sqrt(df["Wh_Speed_in"][i]**2 + 2*df["Accel"][i]*delta_S)
            df["Speed_av"][i] =(df["Speed_in"][i]+df["Speed_f"][i])/2
            df["Wh_Speed_av"][i] =(df["Wh_Speed_in"][i]+df["Wh_Speed_f"][i])/2
            df["delta_t(s)"][i]= df["delta_S_cm"][i]/df["Speed_av"][i]
            df["run_time"][i] = sum(df["delta_t(s)"][0:i+1])

        st.subheader("Using Dan's Power profile as input to our model")
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

        fig_Dist_comp = px.line(df,x="Time_in(s)", y = ["Wheel_Dist_in(m)","true_w_dist"], title="Dist compare")
        #fig.update_xaxes(title="Seconds")
        #fig.update_yaxes(title="Power (W)")
        st.plotly_chart(fig_Dist_comp, use_container_width=True)

        fig_Dan_power = px.line(df_Dan,x="time_in", y = "Power_true", title="Dan's Power trace from Goldmine (2hz)")
        #fig.update_xaxes(title="Seconds")
        #fig.update_yaxes(title="Power (W)")
        st.plotly_chart(fig_Dan_power, use_container_width=True)


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
        
        
        
        
        
        
        
        
    if Profile == "Editable Power Profile":

        ###Modelling bit
        bike_eff = bike_stiffness*chain_efficiency*bearing_efficiency/(1000000)
        curve_rad = (track_circumference-(4*pl_to_trans))/(2*math.pi)

        delta_S = 0.5
        k_s = 0.0072
        #@st.cache_data
        def initial_accel():
            gear_ratio_f = gear_ratio/27
            f_w = 9.80665*(bike_weight+rider_weight)
            mu_s = 1 + straight_bank_angle*k_s
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

            #Updating rolling resistance and drag froces, and acceleration 
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
        
        
        
        
        
        
        
    if Profile == "Bryony Comm Games Qual":
        fig_Dan_power = px.line(df_B,x="time_in", y = "Power_true", title="B's Actual 2Hz Power Trace")
        #fig.update_xaxes(title="Seconds")
        #fig.update_yaxes(title="Power (W)")
        st.plotly_chart(fig_Dan_power, use_container_width=True)

        

        fig_Dan_w_speed = px.line(df_B,x="time_in", y = "Total_Dist", title="B's Actual Distance V Time")
        #fig.update_xaxes(title="Seconds")
        #fig.update_yaxes(title="Power (W)")
        st.plotly_chart(fig_Dan_w_speed, use_container_width=True)



        ###Modelling bit
        bike_eff = bike_stiffness*chain_efficiency*bearing_efficiency/(1000000)
        curve_rad = (track_circumference-(4*pl_to_trans))/(2*math.pi)

        delta_S = 0.5
        k_s = 0.0072
        #@st.cache_data
        def initial_accel():
            gear_ratio_f = gear_ratio/27
            f_w = 9.80665*(bike_weight+rider_weight)
            mu_s = 1 + straight_bank_angle*k_s
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
        #power_interp = scipy.interpolate.interp1d(x, y)
        power_interp = scipy.interpolate.interp1d(df_B["time_in"], df_B["Power_true"])
        #interp_true_w_dist = scipy.interpolate.interp1d(df_Dan["time_in"], df_Dan["Total_Dist"])

        df=pd.DataFrame()

        df["Wheel_Dist_in(m)"]= np.linspace(0, 3000-delta_S, num=int(3000/delta_S +1)).round(1)
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
            if df["Time_in(s)"][i] >= 196:
                df["P_app_in"][i] = 380
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

            #Updating rolling resistance and drag froces, and acceleration 
            df["F_rr"][i]= math.sqrt(f_w**2 + (df["F_c"][i]**2))*math.cos(math.radians(df["Bank_angle(deg)"][i]-df["Lean_angle(deg)"][i]))*mu_rr*(1 + abs(df["Bank_angle(deg)"][i]-df["Lean_angle(deg)"][i])*k_s)

            df["F_d"][i] = 0.5*air_density*cda*(df["Speed_in"][i]**2)

            df["Accel"][i] = ((df["P_out_in"][i]/df["Speed_in"][i]) - df["F_d"][i] - (df["F_rr"][i]*df["RC_wh"][i]/df["RC_cm"][i]))/(bike_weight+rider_weight)

            df["Speed_f"][i]= math.sqrt(df["Speed_in"][i]**2 + 2*df["Accel"][i]*df["delta_S_cm"][i])
            df["Wh_Speed_f"][i]= math.sqrt(df["Wh_Speed_in"][i]**2 + 2*df["Accel"][i]*delta_S)
            df["Speed_av"][i] =(df["Speed_in"][i]+df["Speed_f"][i])/2
            df["Wh_Speed_av"][i] =(df["Wh_Speed_in"][i]+df["Wh_Speed_f"][i])/2
            df["delta_t(s)"][i]= df["delta_S_cm"][i]/df["Speed_av"][i]
            df["run_time"][i] = sum(df["delta_t(s)"][0:i+1])

        st.subheader("Using B's Power profile as input to our model")
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
        st.write("Actual was 3:19.8")


        ###PLOTS

        fig_Dist_comp = px.line(df,x="Time_in(s)", y = "Wheel_Dist_in(m)", title="Dist Trace")
        #fig.update_xaxes(title="Seconds")
        #fig.update_yaxes(title="Power (W)")
        st.plotly_chart(fig_Dist_comp, use_container_width=True)

        fig_Dan_power = px.line(df_B,x="time_in", y = "Power_true", title="B's Power trace from Goldmine (2hz)")
        #fig.update_xaxes(title="Seconds")
        #fig.update_yaxes(title="Power (W)")
        st.plotly_chart(fig_Dan_power, use_container_width=True)


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