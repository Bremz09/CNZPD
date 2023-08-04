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
import os.path



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

name, authentication_status, username = authenticator.login("Login", "main")

if authentication_status == False:
    st.error("Username/password is incorrect")

if authentication_status == None:
    st.warning("Please enter your username and password")

if authentication_status:
    ##This bit is the historical visualiser

   
    racetype = st.selectbox(
        "Select Race Type:",
        options=["Women's TP", "Men's TP", "Mens' Keirin","WTS Starts","Men's IP","Women's IP"]
        ) 
    
    ################################################ Women's Team Pursuit ##########################################################
    
    if racetype == "Women's TP":
        df_master = pd.read_excel(f'pages/video_analysis/TP_Master_Women.xlsx')
        df_master = df_master.sort_values(["Save_Date","Title"], ascending=False)
        df_small = df_master.drop(columns=["Save_Date","Action","Video"])
        df_small
        c1,c2=st.columns(2)
        with c1:
            selections = st.multiselect(
            "Select past effort(s):",
            options=df_master["Title"].unique()
            ) 
        with c2:
            show_vids = ["No","Yes"]
            Videos = st.selectbox("Show Race Videos?", show_vids, key="Show_Vids")


        if len(selections) !=0:
            df_combine = pd.DataFrame()
            for i in range(len(selections)):
                col_1,col_2=st.columns(2)
                with col_1:
                    df_temp = df_master.loc[df_master['Title'] == selections[i]]
                    df_combine = pd.concat([df_combine, df_temp], axis=0)
                    df_small = df_temp.drop(columns=["Save_Date","Video"])
                    df_small=df_small.reset_index(drop="True")
                    r1 = [1]
                    r2 = [2]
                    r3 = [3]
                    r4 = [4]
                    r1WS = [0.971]
                    r2WS = [0.612]
                    r3WS = [0.495]
                    r4WS = [0.459]
                    speed_diff=[df_small["Del_Speed"][0]]

                    no_riders=4
                    drag_feel = [0,0.971,0.612,0.495,0.459]
                    for j in range(1,len(df_small)):
                        speed_diff.append(df_small["Del_Speed"][j]-df_small["Del_Speed"][j-1])
                        if df_small["Action"][j-1] == "Change":
                            r1.append(r1[j-1]-1)
                            r2.append(r2[j-1]-1)
                            r3.append(r3[j-1]-1)
                            r4.append(r4[j-1]-1)
                        elif df_small["Action"][j-1] == "Drop":
                            no_riders = 3
                            drag_feel = [0,0.972,0.617,0.517]
                            r1.append(r1[j-1]-1)
                            r2.append(r2[j-1]-1)
                            r3.append(r3[j-1]-1)
                            r4.append(r4[j-1]-1)
                        else:
                            r1.append(r1[j-1])
                            r2.append(r2[j-1])
                            r3.append(r3[j-1])
                            r4.append(r4[j-1])
                        if r1[j]==0:
                            r1[j]=no_riders
                        if r2[j]==0:
                            r2[j]=no_riders
                        if r3[j]==0:
                            r3[j]=no_riders
                        if r4[j]==0:
                            r4[j]=no_riders
                        r1WS.append(drag_feel[r1[j]])
                        r2WS.append(drag_feel[r2[j]])
                        r3WS.append(drag_feel[r3[j]])
                        r4WS.append(drag_feel[r4[j]])
                    if "Drop" in df_small["Action"].unique():        
                        ind = df_small.index[df_small['Action'] == "Drop"][0]

                        if r1[ind]==1:
                            r1[ind+1:]=[0]*(len(df_small)-ind-1)
                            r1WS[ind+1:]=[0]*(len(df_small)-ind-1)
                        if r2[ind]==1:
                            r2[ind+1:]=[0]*(len(df_small)-ind-1)
                            r2WS[ind+1:]=[0]*(len(df_small)-ind-1)
                        if r3[ind]==1:
                            r3[ind+1:]=[0]*(len(df_small)-ind-1)
                            r3WS[ind+1:]=[0]*(len(df_small)-ind-1)
                        if r4[ind]==1:
                            r4[ind+1:]=[0]*(len(df_small)-ind-1)
                            r4WS[ind+1:]=[0]*(len(df_small)-ind-1)
                    one_turn_1=0
                    two_turn_1=0
                    three_turn_1=0
                    four_turn_1=0
                    one_turn_2=0
                    two_turn_2=0
                    three_turn_2=0
                    four_turn_2=0
                    one_turn_3=0
                    two_turn_3=0
                    three_turn_3=0
                    four_turn_3=0
                    j=0

                    while j<len(df_small) and r1[j] == 1:
                        one_turn_1+=1
                        j+=1
                    while j<len(df_small) and r2[j] == 1:
                        two_turn_1+=1
                        j+=1
                    while j<len(df_small) and r3[j] == 1:
                        three_turn_1+=1
                        j+=1
                    while j<len(df_small) and r4[j] == 1:
                        four_turn_1+=1
                        j+=1
                    while j<len(df_small) and r1[j] == 1:
                        one_turn_2+=1
                        j+=1
                    while j<len(df_small) and r2[j] == 1:
                        two_turn_2+=1
                        j+=1
                    while j<len(df_small) and r3[j] == 1:
                        three_turn_2+=1
                        j+=1
                    while j <len(df_small) and r4[j] == 1:
                        four_turn_2+=1
                        j+=1
                    while j <len(df_small) and r1[j] == 1:
                        one_turn_3+=1
                        j+=1
                    while j <len(df_small) and r2[j] == 1:
                        two_turn_3+=1
                        j+=1
                    while j<len(df_small) and r3[j] == 1:
                        three_turn_3+=1
                        j+=1
                    while j <len(df_small) and r4[j] == 1:
                        four_turn_3+=1
                        j+=1
                    first_turns=[one_turn_1,two_turn_1,three_turn_1,four_turn_1]
                    second_turns=[one_turn_2,two_turn_2,three_turn_2,four_turn_2]
                    third_turns=[one_turn_3,two_turn_3,three_turn_3,four_turn_3]
                    df_small["Rider1"]=r1
                    df_small["Rider2"]=r2
                    df_small["Rider3"]=r3
                    df_small["Rider4"]=r4
                    df_small["Speed_Diff"]=speed_diff
                    df_small["Rider1WS"]=r1WS*(df_small["Del_Speed"]+df_small["Speed_Diff"])
                    df_small["Rider2WS"]=r2WS*(df_small["Del_Speed"]+df_small["Speed_Diff"])
                    df_small["Rider3WS"]=r3WS*(df_small["Del_Speed"]+df_small["Speed_Diff"])
                    df_small["Rider4WS"]=r4WS*(df_small["Del_Speed"]+df_small["Speed_Diff"])


                    df_main = df_small.drop(columns=["Rider1","Rider2","Rider3","Rider4","Action","Speed_Diff","Rider1WS","Rider2WS","Rider3WS","Rider4WS"])
                    df_main
                   
                    
                with col_2:
                    average = df_small.Split.iloc[4:].mean()
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
                    fig.add_hline(y=62.5*3.6/average, line_dash="dash",line_color="yellow",annotation_text="Avg after first lap = " +str(round(average*4,2)))
                    
                    yaxis_min = min(df_temp["Avg_Speed"][1:])-1
                    yaxis_max = max(df_temp["Avg_Speed"])+1
                    fig.update_layout(yaxis_range=[yaxis_min,yaxis_max])
                    st.plotly_chart(fig, use_container_width=True)
                c1,c2=st.columns(2)
                with c1:
                    #st.write("Wind score is a measure of exposure. In each quarter lap split, WS is calculated as WS = Summ [df(delivery_speed + speed_change)]")
                    #st.write("Delivery_speed is the speed assuming no positional change, speed_change is the difference in delivery speeds between intervals, and df is 'drag feel' - the portion of drag felt by a rider in a train, compared to a solo rider.")
                    #st.write("Current values for df are 0.971, 0.612, 0.495, 0.459 for lead, 2nd, 3rd and 4th riders respectively in a 4 person train, and 0.972, 0.617, 0.517 for lead, 2nd and 3rd riders in a 3 person chain.")
                    #st.write("We then sum all values to get the Wind_Score shown below:")
                    unq_riders = df_small["Front"].unique()
                    df_summ=pd.DataFrame(unq_riders)
                    df_summ.columns=["Rider"]
                    df_summ=df_summ.dropna(axis=0)
                    front=[]
                    front.append(len(df_small.loc[df_small['Front'] == df_summ["Rider"][0]]))
                    front.append(len(df_small.loc[df_small['Front'] == df_summ["Rider"][1]]))
                    front.append(len(df_small.loc[df_small['Front'] == df_summ["Rider"][2]]))
                    front.append(len(df_small.loc[df_small['Front'] == df_summ["Rider"][3]]))
                    wind_scores = []
                    df_small['Rider1WS'].fillna(0)
                    wind_scores.append(round(sum(df_small['Rider1WS'].fillna(0),1)))
                    wind_scores.append(round(sum(df_small['Rider2WS'].fillna(0),1)))
                    wind_scores.append(round(sum(df_small['Rider3WS'].fillna(0),1)))
                    wind_scores.append(round(sum(df_small['Rider4WS'].fillna(0),1)))
                    df_summ["Front"]=front
                    df_summ["Turn_1"]=first_turns
                    df_summ["Turn_2"]=second_turns
                    df_summ["Turn_3"]=third_turns
                    df_summ["Wind_Score"] = wind_scores
                    
                    # Calculating Splits based off delivery speeds - 900 is a conversion factor
                    avg_splits=[round(900/(df_small[4:].loc[df_small["Front"] ==unq_riders[0]]["Del_Speed"].mean()),2), round(900/df_small[4:].loc[df_small["Front"] ==unq_riders[1]]["Del_Speed"].mean(),2),round(900/df_small[4:].loc[df_small["Front"] ==unq_riders[2]]["Del_Speed"].mean(),2),round(900/df_small[4:].loc[df_small["Front"] ==unq_riders[3]]["Del_Speed"].mean(),2)]
                    df_summ["Avg_Del_Split"]=avg_splits
                    
                    st.subheader("Rider Info")
                    df_summ
                    
                    
                                 
                    st.subheader("Start Splits")
                    df_start=pd.DataFrame(df_small["Distance"][0:4])
                    df_start["Split"]=df_small["Split"][0:4]
                    df_start["Total"]=df_small["Split"][0:4].cumsum()
                    df_start
                    st.subheader("Kilo Splits")
                    df_kilos=pd.DataFrame(["1k","2k","3k","4k"])
                    df_kilos.columns=["Distance"]
                    kilo_split = [sum(df_small["Split"][0:16]),sum(df_small["Split"][16:32]),sum(df_small["Split"][32:48]),sum(df_small["Split"][48:64])]
                    df_kilos["Split"]=kilo_split
                    df_kilos["Total"]=df_kilos["Split"].cumsum()
                    df_kilos['Total'] = pd.to_datetime(df_kilos['Total'], unit='s').dt.strftime('%M:%S.%f')
                    df_kilos
                if Videos == "Yes":
                    with c2:
                        if pd.isnull(df_temp["Video"].iloc[0]):
                            st.header("No video available")
                        else:
                            video_name = df_temp["Video"].iloc[0]
                            st.header(df_temp["Title"].iloc[0])
           
                            st.video(f"{video_name}")
                st.markdown("---")



            col_one, col_two, col_three, col_four = st.columns(4)
            with col_one:
                show_names = ["No","Yes"]
                Names = st.selectbox("Show Athlete Names?", show_names, key="Show_Names")
                df_combine["Initial"]=df_combine["Front"].str.replace('[^A-Z]', '')
                
            if Names == "Yes":
                fig_tt = px.line(df_combine, x="Distance", y = "Del_Speed", title="Comparison",color="Title",text="Initial",markers="Front")
                fig_tt.update_traces(textposition='top center')
            else:
                fig_tt = px.line(df_combine, x="Distance", y = "Del_Speed", title="Comparison",color="Title",markers="Front")

            st.plotly_chart(fig_tt, use_container_width=True)

#             if len(selections) ==2:

#                 df_zero = df_combine
#                 df_zero = df_zero.reset_index(drop=True)
#                 length = df_zero.Title.value_counts()[selections[0]]
#                 for j in range(length,len(selections)*length):
#                     df_zero.Split[j]=df_zero.Split[j]-df_zero.Split[j-length]
#                     df_zero.Split[j-length]=0



#                 if Names == "Yes":
#                     fig_zero = px.line(df_zero, x="Distance", y = "Split", title="Zero",color="Title",text="Initial",markers="Front")
#                     fig_zero.update_traces(textposition='top center')
#                 else:
#                     fig_zero = px.line(df_zero, x="Distance", y = "Split", title="Zero",color="Title",markers="Front")
#                 st.plotly_chart(fig_zero, use_container_width=True)
#                 if Names=="Yes":
#                     fig_worm = px.line(df_zero, x="Distance", y = "Time", title="Worm",color="Title",text="Initial",markers="Front")
#                     fig_worm.update_traces(textposition='top center')
#                 if Names=="No":
#                     fig_worm = px.line(df_zero, x="Distance", y = "Time", title="Worm",color="Title",markers="Front")

#                 st.plotly_chart(fig_worm, use_container_width=True)

#             elif len(selections) >2:

#                 df_zero = df_combine
#                 df_zero = df_zero.reset_index(drop=True)
#                 length = df_zero.Title.value_counts()[selections[0]]
#                 for j in range(length,len(selections)*length):
#                     df_zero.Split[j]=df_zero.Split[j]-df_zero.Split[j-length]
#                     df_zero.Split[j-length]=0




#                 if Names=="Yes":
#                     fig_worm = px.line(df_zero, x="Distance", y = "Time", title="Worm",color="Title",text="Front",markers="Front")
#                     fig_worm.update_traces(textposition='top center')
#                 if Names=="No":
#                     fig_worm = px.line(df_zero, x="Distance", y = "Time", title="Worm",color="Title",markers="Front")

#                 st.plotly_chart(fig_worm, use_container_width=True)






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
            df = pd.read_csv(uploaded_file)
            df=df.sort_values("Start time", ascending=True)
            col_one, col_two, col_three = st.columns(3)
            with col_one:
                rider1 = st.text_input("Select Rider 1:")
                rider2 = st.text_input("Select Rider 2:")
                rider3 = st.text_input("Select Rider 3:")
                rider4 = st.text_input("Select Rider 4:")
            riders=[rider1,rider2,rider3,rider4]*10
            #riders
            df["Avg_Speed"]=0
            df["Del_Speed"]=0
            df["Split"]=0
            df["Front"]="HOLDER"
            front=[rider1]
            splits=[0]
            del_speeds=[0]
            speeds=[0]
            r=0
            df["Time"] = df["Start time"] - df["Start time"].iloc[0]
            markers = len(df)
            df["Distance"] = np.linspace(0, 62.5*(markers-1), num=markers)
            df=df.reset_index(drop=True)
            df.drop(['Timeline','Duration','Instance number','Ungrouped','Notes','Flags'],
          axis='columns', inplace=True)
            st.write("original df")
            df

            #df = df.dropna(axis=0, subset=['Time'])

            with col_two:
                offset = st.number_input("Offset:", min_value=0.00, max_value=None,value=0.12)
                schedule = round(st.number_input("Schedule:", min_value=0.00, max_value=None,value=14.3),2)
                Title = st.text_input("Plot Title:")


            with col_three:
                num_riders=4
                dropped=''
                #df
                rider_ind=0
                for i in range(1,len(df)):
                    df["Split"][i]=df["Time"][i]-df["Time"][i-1]
                    df["Avg_Speed"][i] = 62.5*3.6/(df["Split"][i])
                    if df["Row"][i] == "Change" or df["Row"][i] == "Drop":
                        df["Del_Speed"][i]=round(df["Avg_Speed"][i]*df["Split"][i]/(df["Split"][i]-offset),2)
                    else:
                        df["Del_Speed"][i]=df["Avg_Speed"][i]
                    if df["Row"][i]=="Drop":
                        df["Front"][i]=riders[rider_ind]
                        dropped=df["Front"][i]
                        rider_ind+=1
                    elif df["Row"][i]=="Change":
                        df["Front"][i]=riders[rider_ind]
                        rider_ind+=1
                        if riders[rider_ind] == dropped:
                            rider_ind+=1
                    else:
                        df["Front"][i]=riders[rider_ind]
                        
                  
                df.drop('Start time',
          axis='columns', inplace=True)
                df.rename(columns = {'Row':'Action'}, inplace = True)
                df.drop(index=df.index[0], axis=0, inplace=True)
                #df = df.dropna(axis=0, subset=['Time'])
                st.write("final df")
                df


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






            #master_path=st.text_input("Add path to master file:",key="prompt")
            if st.button("Append this effort to master",key="upload"):




                df_save=df
                df_save.insert(0, 'Save_Date', datetime.date.today())
                df_save["Save_Date"] = pd.to_datetime(df_save['Save_Date'])
                df_save.insert(0, 'Title', Title)
                df = pd.concat([df_master, df_save], axis=0)
                df

                ##Testing downloader


                # buffer to use for excel writer
                buffer = io.BytesIO()



                @st.cache_data
                def convert_to_csv(df):
                    # IMPORTANT: Cache the conversion to prevent computation on every rerun
                    return df.to_csv(index=False).encode('utf-8')

                csv = convert_to_csv(df)

                # display the dataframe on streamlit app
        #         st.write(df)

                # download button 1 to download dataframe as csv
                download1 = st.download_button(
                    label="Download new Master as CSV",
                    data=csv,
                    file_name='TP_Master_Women.csv',
                    mime='text/csv'
                )

                # download button 2 to download dataframe as xlsx
                with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                    # Write each dataframe to a different worksheet.
                    df.to_excel(writer, sheet_name='Sheet1', index=False)
                    # Close the Pandas Excel writer and output the Excel file to the buffer
                    writer.save()

                    download2 = st.download_button(
                        label="Download new Master as Excel",
                        data=buffer,
                        file_name='TP_Master_Women.xlsx',
                        mime='application/vnd.ms-excel'
                    )  
                    
                    
   ###################################################### Men's Team Pursuit #############################################                 
                    
    if racetype == "Men's TP":
        df_master = pd.read_excel(f'pages/video_analysis/TP_Master_Men.xlsx')
        df_master = df_master.sort_values(["Save_Date","Title"], ascending=False)
        df_small = df_master.drop(columns=["Save_Date","Action","Video"])
        df_small
        c1,c2=st.columns(2)
        with c1:
            selections = st.multiselect(
            "Select past effort(s):",
            options=df_master["Title"].unique()
            ) 
        with c2:
            show_vids = ["No","Yes"]
            Videos = st.selectbox("Show Race Videos?", show_vids, key="Show_Vids")


        if len(selections) !=0:
            df_combine = pd.DataFrame()
            for i in range(len(selections)):
                col_1,col_2=st.columns(2)
                with col_1:
                    df_temp = df_master.loc[df_master['Title'] == selections[i]]
                    df_combine = pd.concat([df_combine, df_temp], axis=0)
                    df_small = df_temp.drop(columns=["Save_Date","Video"])
                    df_small=df_small.reset_index(drop="True")
                    r1 = [1]
                    r2 = [2]
                    r3 = [3]
                    r4 = [4]
                    r1WS = [0.971]
                    r2WS = [0.612]
                    r3WS = [0.495]
                    r4WS = [0.459]
                    speed_diff=[df_small["Del_Speed"][0]]

                    no_riders=4
                    drag_feel = [0,0.971,0.612,0.495,0.459]
                    for j in range(1,len(df_small)):
                        speed_diff.append(df_small["Del_Speed"][j]-df_small["Del_Speed"][j-1])
                        if df_small["Action"][j-1] == "Change":
                            r1.append(r1[j-1]-1)
                            r2.append(r2[j-1]-1)
                            r3.append(r3[j-1]-1)
                            r4.append(r4[j-1]-1)
                        elif df_small["Action"][j-1] == "Drop":
                            no_riders = 3
                            drag_feel = [0,0.972,0.617,0.517]
                            r1.append(r1[j-1]-1)
                            r2.append(r2[j-1]-1)
                            r3.append(r3[j-1]-1)
                            r4.append(r4[j-1]-1)
                        else:
                            r1.append(r1[j-1])
                            r2.append(r2[j-1])
                            r3.append(r3[j-1])
                            r4.append(r4[j-1])
                        if r1[j]==0:
                            r1[j]=no_riders
                        if r2[j]==0:
                            r2[j]=no_riders
                        if r3[j]==0:
                            r3[j]=no_riders
                        if r4[j]==0:
                            r4[j]=no_riders
                        r1WS.append(drag_feel[r1[j]])
                        r2WS.append(drag_feel[r2[j]])
                        r3WS.append(drag_feel[r3[j]])
                        r4WS.append(drag_feel[r4[j]])
                    if "Drop" in df_small["Action"].unique():        
                        ind = df_small.index[df_small['Action'] == "Drop"][0]

                        if r1[ind]==1:
                            r1[ind+1:]=[0]*(len(df_small)-ind-1)
                            r1WS[ind+1:]=[0]*(len(df_small)-ind-1)
                        if r2[ind]==1:
                            r2[ind+1:]=[0]*(len(df_small)-ind-1)
                            r2WS[ind+1:]=[0]*(len(df_small)-ind-1)
                        if r3[ind]==1:
                            r3[ind+1:]=[0]*(len(df_small)-ind-1)
                            r3WS[ind+1:]=[0]*(len(df_small)-ind-1)
                        if r4[ind]==1:
                            r4[ind+1:]=[0]*(len(df_small)-ind-1)
                            r4WS[ind+1:]=[0]*(len(df_small)-ind-1)
                    one_turn_1=0
                    two_turn_1=0
                    three_turn_1=0
                    four_turn_1=0
                    one_turn_2=0
                    two_turn_2=0
                    three_turn_2=0
                    four_turn_2=0
                    one_turn_3=0
                    two_turn_3=0
                    three_turn_3=0
                    four_turn_3=0
                    j=0

                    while j<len(df_small) and r1[j] == 1:
                        one_turn_1+=1
                        j+=1
                    while j<len(df_small) and r2[j] == 1:
                        two_turn_1+=1
                        j+=1
                    while j<len(df_small) and r3[j] == 1:
                        three_turn_1+=1
                        j+=1
                    while j<len(df_small) and r4[j] == 1:
                        four_turn_1+=1
                        j+=1
                    while j<len(df_small) and r1[j] == 1:
                        one_turn_2+=1
                        j+=1
                    while j<len(df_small) and r2[j] == 1:
                        two_turn_2+=1
                        j+=1
                    while j<len(df_small) and r3[j] == 1:
                        three_turn_2+=1
                        j+=1
                    while j <len(df_small) and r4[j] == 1:
                        four_turn_2+=1
                        j+=1
                    while j <len(df_small) and r1[j] == 1:
                        one_turn_3+=1
                        j+=1
                    while j <len(df_small) and r2[j] == 1:
                        two_turn_3+=1
                        j+=1
                    while j<len(df_small) and r3[j] == 1:
                        three_turn_3+=1
                        j+=1
                    while j <len(df_small) and r4[j] == 1:
                        four_turn_3+=1
                        j+=1
                    first_turns=[one_turn_1,two_turn_1,three_turn_1,four_turn_1]
                    second_turns=[one_turn_2,two_turn_2,three_turn_2,four_turn_2]
                    third_turns=[one_turn_3,two_turn_3,three_turn_3,four_turn_3]
                    df_small["Rider1"]=r1
                    df_small["Rider2"]=r2
                    df_small["Rider3"]=r3
                    df_small["Rider4"]=r4
                    df_small["Speed_Diff"]=speed_diff
                    df_small["Rider1WS"]=r1WS*(df_small["Del_Speed"]+df_small["Speed_Diff"])
                    df_small["Rider2WS"]=r2WS*(df_small["Del_Speed"]+df_small["Speed_Diff"])
                    df_small["Rider3WS"]=r3WS*(df_small["Del_Speed"]+df_small["Speed_Diff"])
                    df_small["Rider4WS"]=r4WS*(df_small["Del_Speed"]+df_small["Speed_Diff"])


                    df_main = df_small.drop(columns=["Rider1","Rider2","Rider3","Rider4","Action","Speed_Diff","Rider1WS","Rider2WS","Rider3WS","Rider4WS"])
                    df_main
                   
                    
                with col_2:
                    average = df_small.Split.iloc[4:].mean()
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
                    fig.add_hline(y=62.5*3.6/average, line_dash="dash",line_color="yellow",annotation_text="Avg after first lap = " +str(round(average*4,2)))
                    yaxis_min = min(df_temp["Avg_Speed"][1:])-1
                    yaxis_max = max(df_temp["Avg_Speed"])+1
                    fig.update_layout(yaxis_range=[yaxis_min,yaxis_max])
                    st.plotly_chart(fig, use_container_width=True)
                c1,c2=st.columns(2)
                with c1:
                    #st.write("Wind score is a measure of exposure. In each quarter lap split, WS is calculated as WS = Summ [df(delivery_speed + speed_change)]")
                    #st.write("Delivery_speed is the speed assuming no positional change, speed_change is the difference in delivery speeds between intervals, and df is 'drag feel' - the portion of drag felt by a rider in a train, compared to a solo rider.")
                    #st.write("Current values for df are 0.971, 0.612, 0.495, 0.459 for lead, 2nd, 3rd and 4th riders respectively in a 4 person train, and 0.972, 0.617, 0.517 for lead, 2nd and 3rd riders in a 3 person chain.")
                    #st.write("We then sum all values to get the Wind_Score shown below:")
                    unq_riders = df_small["Front"].unique()
                    df_summ=pd.DataFrame(unq_riders)
                    df_summ.columns=["Rider"]
                    df_summ=df_summ.dropna(axis=0)
                    front=[]
                    front.append(len(df_small.loc[df_small['Front'] == df_summ["Rider"][0]]))
                    front.append(len(df_small.loc[df_small['Front'] == df_summ["Rider"][1]]))
                    front.append(len(df_small.loc[df_small['Front'] == df_summ["Rider"][2]]))
                    front.append(len(df_small.loc[df_small['Front'] == df_summ["Rider"][3]]))
                    wind_scores = []
                    df_small['Rider1WS'].fillna(0)
                    wind_scores.append(round(sum(df_small['Rider1WS'].fillna(0),1)))
                    wind_scores.append(round(sum(df_small['Rider2WS'].fillna(0),1)))
                    wind_scores.append(round(sum(df_small['Rider3WS'].fillna(0),1)))
                    wind_scores.append(round(sum(df_small['Rider4WS'].fillna(0),1)))
                    df_summ["Front"]=front
                    df_summ["Turn_1"]=first_turns
                    df_summ["Turn_2"]=second_turns
                    df_summ["Turn_3"]=third_turns
                    df_summ["Wind_Score"] = wind_scores
                    
                    # Calculating Splits based off delivery speeds - 900 is a conversion factor
                    avg_splits=[round(900/(df_small[4:].loc[df_small["Front"] ==unq_riders[0]]["Del_Speed"].mean()),2), round(900/df_small[4:].loc[df_small["Front"] ==unq_riders[1]]["Del_Speed"].mean(),2),round(900/df_small[4:].loc[df_small["Front"] ==unq_riders[2]]["Del_Speed"].mean(),2),round(900/df_small[4:].loc[df_small["Front"] ==unq_riders[3]]["Del_Speed"].mean(),2)]
                    df_summ["Avg_Del_Split"]=avg_splits
                    
                    
                    speed_var=[df_small[4:].loc[df_small["Front"] ==unq_riders[0]]["Del_Speed"].max()-df_small[4:].loc[df_small["Front"] ==unq_riders[0]]["Del_Speed"].min(),df_small[4:].loc[df_small["Front"] ==unq_riders[1]]["Del_Speed"].max()-df_small[4:].loc[df_small["Front"] ==unq_riders[1]]["Del_Speed"].min(),df_small[4:].loc[df_small["Front"] ==unq_riders[2]]["Del_Speed"].max()-df_small[4:].loc[df_small["Front"] ==unq_riders[2]]["Del_Speed"].min(),df_small[4:].loc[df_small["Front"] ==unq_riders[3]]["Del_Speed"].max()-df_small[4:].loc[df_small["Front"] ==unq_riders[3]]["Del_Speed"].min()]
                    df_summ["Speed_Var"]=speed_var
                    
                    
                    st.subheader("Rider Info")
                    df_summ
                    st.subheader("Start Splits")
                    df_start=pd.DataFrame(df_small["Distance"][0:4])
                    df_start["Split"]=df_small["Split"][0:4]
                    df_start["Total"]=df_small["Split"][0:4].cumsum()
                    df_start
                    st.subheader("Kilo Splits")
                    df_kilos=pd.DataFrame(["1k","2k","3k","4k"])
                    df_kilos.columns=["Distance"]
                    kilo_split = [sum(df_small["Split"][0:16]),sum(df_small["Split"][16:32]),sum(df_small["Split"][32:48]),sum(df_small["Split"][48:64])]
                    df_kilos["Split"]=kilo_split
                    df_kilos["Total"]=df_kilos["Split"].cumsum()
                    df_kilos['Total'] = pd.to_datetime(df_kilos['Total'], unit='s').dt.strftime('%M:%S.%f')
                    df_kilos
                if Videos == "Yes":
                    with c2:
                        if pd.isnull(df_temp["Video"].iloc[0]):
                            st.header("No video available")
                        else:
                            video_name = df_temp["Video"].iloc[0]
                            st.header(df_temp["Title"].iloc[0])
           
                            st.video(f"{video_name}")
                st.markdown("---")



            col_one, col_two, col_three, col_four = st.columns(4)
            with col_one:
                show_names = ["No","Yes"]
                Names = st.selectbox("Show Athlete Names?", show_names, key="Show_Names")
                df_combine["Initial"]=df_combine["Front"].str.replace('[^A-Z]', '')
            
            if Names == "Yes":
                fig_tt = px.line(df_combine, x="Distance", y = "Del_Speed", title="Comparison",color="Title",text="Initial",markers="Front")
                fig_tt.update_traces(textposition='top center')
            else:
                fig_tt = px.line(df_combine, x="Distance", y = "Del_Speed", title="Comparison",color="Title",markers="Front")

            st.plotly_chart(fig_tt, use_container_width=True)
            
            ##This bit needs fixed for variable length df's

#             if len(selections) ==2:

#                 df_zero = df_combine
#                 df_zero = df_zero.reset_index(drop=True)
#                 length = df_zero.Title.value_counts()[selections[0]]
#                 for j in range(length,len(selections)*length):
#                     df_zero.Split[j]=df_zero.Split[j]-df_zero.Split[j-length]
#                     df_zero.Split[j-length]=0

                

#                 if Names == "Yes":
#                     fig_zero = px.line(df_zero, x="Distance", y = "Split", title="Zero",color="Title",text="Initial",markers="Front")
#                     fig_zero.update_traces(textposition='top center')
#                 else:
#                     fig_zero = px.line(df_zero, x="Distance", y = "Split", title="Zero",color="Title",markers="Front")
#                 st.plotly_chart(fig_zero, use_container_width=True)
#                 if Names=="Yes":
#                     fig_worm = px.line(df_zero, x="Distance", y = "Time", title="Worm",color="Title",text="Initial",markers="Front")
#                     fig_worm.update_traces(textposition='top center')
#                 if Names=="No":
#                     fig_worm = px.line(df_zero, x="Distance", y = "Time", title="Worm",color="Title",markers="Front")

#                 st.plotly_chart(fig_worm, use_container_width=True)

#             elif len(selections) >2:

#                 df_zero = df_combine
#                 df_zero = df_zero.reset_index(drop=True)
#                 length = df_zero.Title.value_counts()[selections[0]]
#                 tick=0

                        
                    
                
                
#                 for j in range(length,len(selections)*length):
#                     df_zero.Split[j]=df_zero.Split[j]-df_zero.Split[j-length]
#                     df_zero.Split[j-length]=0


                

#                 if Names=="Yes":
#                     fig_worm = px.line(df_zero, x="Distance", y = "Time", title="Worm",color="Title",text="Front",markers="Front")
#                     fig_worm.update_traces(textposition='top center')
#                 if Names=="No":
#                     fig_worm = px.line(df_zero, x="Distance", y = "Time", title="Worm",color="Title",markers="Front")

#                 st.plotly_chart(fig_worm, use_container_width=True)






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
            df = pd.read_csv(uploaded_file)
            df=df.sort_values("Start time", ascending=True)
            col_one, col_two, col_three = st.columns(3)
            with col_one:
                rider1 = st.text_input("Select Rider 1:")
                rider2 = st.text_input("Select Rider 2:")
                rider3 = st.text_input("Select Rider 3:")
                rider4 = st.text_input("Select Rider 4:")
            riders=[rider1,rider2,rider3,rider4]*10
            #riders
            df["Avg_Speed"]=0
            df["Del_Speed"]=0
            df["Split"]=0
            df["Front"]="HOLDER"
            front=[rider1]
            splits=[0]
            del_speeds=[0]
            speeds=[0]
            r=0
            df["Time"] = df["Start time"] - df["Start time"].iloc[0]
            markers = len(df)
            df["Distance"] = np.linspace(0, 62.5*(markers-1), num=markers)
            df=df.reset_index(drop=True)
            df.drop(['Timeline','Duration','Instance number','Ungrouped','Notes','Flags'],
          axis='columns', inplace=True)
            st.write("original df")
            df

            #df = df.dropna(axis=0, subset=['Time'])

            with col_two:
                offset = st.number_input("Offset:", min_value=0.00, max_value=None,value=0.12)
                schedule = round(st.number_input("Schedule:", min_value=0.00, max_value=None,value=14.3),2)
                Title = st.text_input("Plot Title:")


            with col_three:
                num_riders=4
                dropped=''
                #df
                rider_ind=0
                for i in range(1,len(df)):
                    df["Split"][i]=df["Time"][i]-df["Time"][i-1]
                    df["Avg_Speed"][i] = 62.5*3.6/(df["Split"][i])
                    if df["Row"][i] == "Change" or df["Row"][i] == "Drop":
                        df["Del_Speed"][i]=round(df["Avg_Speed"][i]*df["Split"][i]/(df["Split"][i]-offset),2)
                    else:
                        df["Del_Speed"][i]=df["Avg_Speed"][i]
                    if df["Row"][i]=="Drop":
                        df["Front"][i]=riders[rider_ind]
                        dropped=df["Front"][i]
                        rider_ind+=1
                    elif df["Row"][i]=="Change":
                        df["Front"][i]=riders[rider_ind]
                        rider_ind+=1
                        if riders[rider_ind] == dropped:
                            rider_ind+=1
                    else:
                        df["Front"][i]=riders[rider_ind]
                        
                  
                df.drop('Start time',
          axis='columns', inplace=True)
                df.rename(columns = {'Row':'Action'}, inplace = True)
                df.drop(index=df.index[0], axis=0, inplace=True)
                #df = df.dropna(axis=0, subset=['Time'])
                st.write("hello")
                df


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






            #master_path=st.text_input("Add path to master file:",key="prompt")
            if st.button("Append this effort to master",key="upload"):




                df_save=df
                df_save.insert(0, 'Save_Date', datetime.date.today())
                df_save["Save_Date"] = pd.to_datetime(df_save['Save_Date'])
                df_save.insert(0, 'Title', Title)
                df = pd.concat([df_master, df_save], axis=0)
                df

                ##Testing downloader


                # buffer to use for excel writer
                buffer = io.BytesIO()



                @st.cache_data
                def convert_to_csv(df):
                    # IMPORTANT: Cache the conversion to prevent computation on every rerun
                    return df.to_csv(index=False).encode('utf-8')

                csv = convert_to_csv(df)

                # display the dataframe on streamlit app
        #         st.write(df)

                # download button 1 to download dataframe as csv
                download1 = st.download_button(
                    label="Download new Master as CSV",
                    data=csv,
                    file_name='TP_Master_Men.csv',
                    mime='text/csv'
                )

                # download button 2 to download dataframe as xlsx
                with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                    # Write each dataframe to a different worksheet.
                    df.to_excel(writer, sheet_name='Sheet1', index=False)
                    # Close the Pandas Excel writer and output the Excel file to the buffer
                    writer.save()

                    download2 = st.download_button(
                        label="Download new Master as Excel",
                        data=buffer,
                        file_name='TP_Master_Men.xlsx',
                        mime='application/vnd.ms-excel'
                    )                
                    
    ######################################## Men's Keirin ################################################################                
                    
    elif racetype == "Mens' Keirin":
        df_master = pd.read_csv(f'pages/video_analysis/Mens_Keirin.csv')
        
        #df_small = df_master.drop(columns=["Save_Date","Action","Video"])
        df_select = df_master
        c1,c2,c3,c4 = st.columns(4)
        with c1:
            with c1:
                event = st.selectbox(
                "Select Event(s):",
                options=df_master["Event"].unique()
                ) 
                if event:
                    df_select = df_master.query(
                "Event == @event"
                )
        with c2:
            Round = st.selectbox(
            "Select Round(s):",
            options=df_select["Round"].unique()
            )
            if Round:
                df_select = df_master.query(
            "Round == @Round"
            )
        with c3:
            Heat = st.selectbox(
            "Select Heat(s):",
            options=df_select["Heat"].unique()
            )
            if Heat:
                df_select = df_select.query(
            "Heat == @Heat"
            )
        with c4:
            show_vids = ["No","Yes"]
            Videos = st.selectbox("Show Race Video?", show_vids, key="Show_Vids")
        df_select["Time"]=df_select["Start time"]-df_select["Start time"].iloc[0]
        df_select=df_select.drop(columns=["Start time"])
        #df_select    
        
        
        
        
        df_gaps = pd.DataFrame()
        df_gaps["To Go"] = ["3 Laps","2.5 Laps","2 Laps","1.5 Laps","1 Lap","0.5 Laps","15m"]
        
        for i in range(len(df_select["Name"].unique())):
            var = str(df_select["Name"].unique()[i])
           
            df_gaps[f"{var}"]=df_select.loc[df_select["Name"]==var]["Time"].values
        
        cols = len(df_gaps.columns)
        
        df_splits=pd.DataFrame()
        df_splits["Half"] = [1,2,3,4,5,6]
        for i in range(1,cols):
            x=[]
            for j in range(1,7):
                x.append(df_gaps[df_gaps.columns[i]][j]-df_gaps[df_gaps.columns[i]][j-1])
            df_splits[df_gaps.columns[i]] = x

        for i in range(1,7):
            small = df_gaps.loc[i][1:].min()
            
            for j in range(1,cols):
                df_gaps.loc[i,df_gaps.columns[j]]=df_gaps.loc[i,df_gaps.columns[j]]-small
        st.subheader("Time Gap to Leader") 
        c1,c2=st.columns([1,3])
        with c1:
            df_gaps 

        fig_tt = px.line(df_gaps, x="To Go", y = df_gaps.columns, title="Time Gap to Leader")
        with c2:
            st.plotly_chart(fig_tt, use_container_width=True)
        
        
        ###Splits
        
        
#         df_splits = pd.DataFrame()
#         df_splits["To Go"] = ["3 Laps","2.5 Laps","2 Laps","1.5 Laps","1 Lap","0.5 Laps","15m"]
#         df_splits
        
            
            
            
            
        
        st.subheader("Splits (Pursuit Lines)")
        c1,c2=st.columns([1,3])
        with c1:
            df_splits
        fig_tt = px.line(df_splits, x="Half", y = df_splits.columns, title="Splits")
        with c2:
            st.plotly_chart(fig_tt, use_container_width=True)
        
        if Videos=="Yes":
            video_name=df_select["Video"].iloc[0]
            c1,c2,c3=st.columns([1,2,1])
            with c2:
                st.video(f"{video_name}")
            
        
        st.markdown("---")
        st.header("Rider Analysis")
        df_riders=df_master
        c1,c2=st.columns([5,1])
        with c1:
            riders = st.multiselect(
                "Select rider(s):",
                options=df_master["Name"].unique()
                ) 
        with c2:
            show_vids_2 = ["No","Yes"]
            Videos_2 = st.selectbox("Show Race Video?", show_vids_2, key="Show_Vids_2")
        if riders:
            df_riders = df_master.query(
        "Name == @riders"
        )
        
            df_riders=df_riders.sort_values(by=["Name","Start time"])
            df_riders=df_riders.reset_index(drop=True)
            df_riders["Initials"]=df_riders["Name"].apply(lambda x: ''.join(i[0] for i in x.split()))
            #df_riders

    #         for Name in df_riders["Name"].unique():
    #             for Event in df_riders.loc[df_riders["Name"]==Name]["Event"].unique():
    #                 for Round in df_riders.loc[(df_riders["Name"]==Name)]["Round"].unique():
    #                     for Heat in df_riders.loc[df_riders["Name"]==Name]["Heat"].unique():
    #                         st.write(Name+" "+Event+" "+Round+" "+str(Heat))
            tags=[]

            Name=df_riders["Name"][0]
            Event=df_riders["Event"][0]
            Round=df_riders["Round"][0]
            Heat=df_riders["Heat"][0]

            tags.append(df_riders["Initials"][0]+" "+df_riders["Event"][0]+" "+df_riders["Round"][0]+" H"+str(df_riders["Heat"][0]))
            count=0
            tag_count=0
            start=df_riders["Start time"][0]
            videos=[df_riders["Video"][0]]
            times=[df_riders["Start time"][0]-start]
            df_worm=pd.DataFrame()
            df_worm["To Go"]=["3 Laps","2.5 Laps","2 Laps","1.5 Laps","1 Lap","0.5 Laps","15m"]
            for i in range(1,len(df_riders)):
                if count<6:
                    times.append(df_riders["Start time"][i]-start)
                    count+=1
                else:
                    tags.append(df_riders["Initials"][i]+" "+df_riders["Event"][i]+" "+df_riders["Round"][i]+" H"+str(df_riders["Heat"][i]))

                    df_worm[tags[tag_count]]=times
                    count=0
                    tag_count+=1
                    times=[]
                    start = df_riders["Start time"][i]
                    times.append(df_riders["Start time"][i]-start)
                    videos.append(df_riders["Video"][i])
            df_worm[tags[tag_count]]=times

            df_worm
            
            fig_worm = px.line(df_worm, x="To Go", y = df_worm.columns, title="Worms")

            st.plotly_chart(fig_worm, use_container_width=True)




            df_split=pd.DataFrame()
            df_split["Half"] = [1,2,3,4,5,6]

            for col in df_worm.columns[1:]:
                x=[]
                for i in range(1,7):
                    x.append(df_worm[col][i]-df_worm[col][i-1])
                df_split[col]=x
                    
            df_split
            
            
            fig_splits = px.line(df_split, x="Half", y = df_split.columns, title="Splits")

            st.plotly_chart(fig_splits, use_container_width=True)
            
            if Videos_2=="Yes":
                count=0
                for i in range(len(videos)):
                    c1,c2=st.columns([1,2])
                    with c1:
                        st.subheader(df_riders["Name"][count])
                        st.subheader(df_riders["Event"][count]+" "+df_riders["Round"][count]+" H"+str(df_riders["Heat"][count]))
                        st.subheader("Half Lap Splits")
                        df_split[["Half",df_split.columns[i+1]]]
                        st.subheader("Running Time")
                        df_worm[["To Go",df_worm.columns[i+1]]]
                        count+=7
                        
                    with c2:
                        video_name=videos[i]
                        st.video(f"{video_name}")
                    st.markdown('---')
                            
                        
                    
                        
        


        #####################################   WTS Starts stuff   #############################################################
            
    elif racetype == "WTS Starts":
        df_master = pd.read_excel(f'pages/video_analysis/WTS_starts.xlsx')
        for i in range(len(df_master)):
            df_master["Date"][i] = df_master["Date"][i].date()
        df_small = df_master.drop(columns=["Back","Forward","Green","PL",62.5,125,187.5,250,312.5,375,437.5,500])
        df_small
        c1,c2,c3=st.columns(3)
        
        with c1:
            riders = st.multiselect(
            "Select rider(s):",
            options=df_master["Name"].unique()
            ) 
            if riders:
                df_small = df_small.query(
            "Name == @riders"
            )
        with c2:
            dates = st.multiselect(
            "Select date(s):",
            options=df_small["Date"].unique()
            )
            if dates:
                df_small = df_small.query(
            "Date == @dates"
            )
        with c3:
            show_vids = ["No","Yes"]
            Videos = st.selectbox("Show Race Videos?", show_vids, key="Show_Vids")


        if len(riders) !=0:
            df_combine = pd.DataFrame()
            for i in range(len(riders)):
                col_1,col_2=st.columns(2)
                with col_1:
                    df_temp = df_small.loc[df_master['Name'] == riders[i]]
                    df_combine = pd.concat([df_combine, df_temp], axis=0)
                    
                    #df_small=df_small.reset_index(drop="True")
            df_combine = df_combine.reset_index(drop="True")
            
            df_combine
            
            df_splits = pd.DataFrame()
            df_splits["Mark"] = ["RT","Q1","Q2","Q3","Q4","Q5","Q6","Q7","Q8"]
            for i in range(len(df_combine)):
                var = str(i+1)+" " +str(df_combine["Name"].iloc[i]) + " " + str(df_combine["Date"].iloc[i]) + " Set " +str(df_combine["Set"].iloc[i])+" Rep " +str(df_combine["Rep"].iloc[i]) + " " +str(df_combine["Team/Solo"].iloc[i])
                df_splits[f"{var}"]=df_combine.iloc[i][8:17].values

            
            fig_tt = px.line(df_splits, x="Mark", y = df_splits.columns, title="Reaction Time + Quarter Splits")

            st.plotly_chart(fig_tt, use_container_width=True)
            #c1,c2=st.columns(2)
            
            if Videos == "Yes":
                for i in range(len(df_combine)):
                    if pd.isnull(df_combine["Video"].iloc[i]):
                        pass
                    else:
                        c1,c2=st.columns(2)
                        video_name = df_combine["Video"].iloc[i]
                        with c1:
                            st.header(df_combine["Name"].iloc[i])
                            st.subheader(df_combine["Date"].iloc[i])
                            st.subheader("Set "+str(df_combine["Set"].iloc[i])+ ", Rep " +str(df_combine["Rep"].iloc[i]))
                            st.subheader(df_combine["Team/Solo"].iloc[i])
                            st.subheader("Position "+str(df_combine["Pos"].iloc[i]))
                            st.subheader("Gear "+str(df_combine["Gear"].iloc[i]))
                            st.write("Reaction Time = "+str(round(df_combine["RT"].iloc[i],3)) + " Seconds")
                            st.write("First Quarter in = "+str(round(df_combine["Q1"].iloc[i],3)) + " Seconds, with a Moving Time of "+str(round(df_combine["Q1_MT"].iloc[i],3)) + " Seconds")
                            if pd.isnull(df_combine["Q2"].iloc[i])==False:
                                st.write("Second Quarter in = "+str(round(df_combine["Q2"].iloc[i],3)) + " Seconds, giving a split of "+str(round(df_combine["H1"].iloc[i],3))+" with a Moving Time of "+str(round(df_combine["H1_MT"].iloc[i],3)) + " Seconds")
                            if pd.isnull(df_combine["Q3"].iloc[i])==False:
                                st.write("Third Quarter in = "+str(round(df_combine["Q3"].iloc[i],3)) + " Seconds")
                            if pd.isnull(df_combine["Q4"].iloc[i])==False:
                                st.write("Fourth Quarter in = "+str(round(df_combine["Q4"].iloc[i],3)) + " Seconds, giving a split of "+str(round(df_combine["H2"].iloc[i],3))+" with a Moving Time of "+str(round(df_combine["Lap_MT"].iloc[i],3)) + " Seconds")
                                

                        with c2:
                            st.video(f"{video_name}")
                        st.markdown("---")





###################################################### Men's Individual Pursuit #############################################                 
                    
    if racetype == "Men's IP":
        df_master = pd.read_excel(f'pages/video_analysis/IP_Master_Men.xlsx')
        df_master = df_master.sort_values(["Save_Date","Title"], ascending=False)
        df_small = df_master.drop(columns=["Save_Date","Action","Video"])
        df_small
        c1,c2=st.columns(2)
        with c1:
            selections = st.multiselect(
            "Select past effort(s):",
            options=df_master["Title"].unique()
            ) 
        with c2:
            show_vids = ["No","Yes"]
            Videos = st.selectbox("Show Race Videos?", show_vids, key="Show_Vids")


        if len(selections) !=0:
            df_combine = pd.DataFrame()
            for i in range(len(selections)):
                col_1,col_2=st.columns(2)
                with col_1:
                    df_temp = df_master.loc[df_master['Title'] == selections[i]]
                    df_combine = pd.concat([df_combine, df_temp], axis=0)
                    df_small = df_temp.drop(columns=["Save_Date","Video"])
                    df_small=df_small.reset_index(drop="True")
                  
                       
                        


                    df_main = df_small.drop(columns=["Action"])
                    df_main
                with col_2:
                    average = df_small.Split.iloc[4:].mean()
                    fig = px.bar(df_temp, x='Distance', y='Avg_Speed',hover_data=[df_temp.Split, df_temp.Avg_Speed])
                    
                    fig.update_layout(
                    title={
                        'text': df_temp.Title.iloc[0],
                        'y':0.9,
                        'x':0.5,
                        'xanchor': 'center',
                        'yanchor': 'top',
                        'font':dict(size=25)})
                    fig.add_hline(y=62.5*3.6/average, line_dash="dash",line_color="yellow",annotation_text="Avg after first lap = " +str(round(average*4,2)))
                    yaxis_min = min(df_temp["Avg_Speed"][1:])-1
                    yaxis_max = max(df_temp["Avg_Speed"])+1
                    fig.update_layout(yaxis_range=[yaxis_min,yaxis_max])
                    st.plotly_chart(fig, use_container_width=True)
                c1,c2=st.columns(2)
                with c1:

                    
                    
                    st.subheader("Start Splits")
                    df_start=pd.DataFrame(df_small["Distance"][0:4])
                    df_start["Split"]=df_small["Split"][0:4]
                    df_start["Total"]=df_small["Split"][0:4].cumsum()
                    df_start
                    st.subheader("Kilo Splits")
                    df_kilos=pd.DataFrame(["1k","2k","3k","4k"])
                    df_kilos.columns=["Distance"]
                    kilo_split = [sum(df_small["Split"][0:16]),sum(df_small["Split"][16:32]),sum(df_small["Split"][32:48]),sum(df_small["Split"][48:64])]
                    df_kilos["Split"]=kilo_split
                    df_kilos["Total"]=df_kilos["Split"].cumsum()
                    df_kilos['Total'] = pd.to_datetime(df_kilos['Total'], unit='s').dt.strftime('%M:%S.%f')
                    df_kilos
                if Videos == "Yes":
                    with c2:
                        if pd.isnull(df_temp["Video"].iloc[0]):
                            st.header("No video available")
                        else:
                            video_name = df_temp["Video"].iloc[0]
                            st.header(df_temp["Title"].iloc[0])
   
                            st.video(f"{video_name}")
                st.markdown("---")



            col_one, col_two, col_three, col_four = st.columns(4)
            
            with col_one:
           
                fig_tt = px.line(df_combine, x="Distance", y = "Avg_Speed", title="Comparison",color="Title",markers="Front")
                
            st.plotly_chart(fig_tt, use_container_width=True)

            if len(selections) ==2:

                df_zero = df_combine
                df_zero = df_zero.reset_index(drop=True)
                length = df_zero.Title.value_counts()[selections[0]]
                for j in range(length,len(selections)*length):
                    df_zero.Split[j]=df_zero.Split[j]-df_zero.Split[j-length]
                    df_zero.Split[j-length]=0



                fig_zero = px.line(df_zero, x="Distance", y = "Avg_Speed", title="Zero",color="Title",markers="Front")
                st.plotly_chart(fig_zero, use_container_width=True)
               
                fig_worm = px.line(df_zero, x="Distance", y = "Time", title="Worm",color="Title",markers="Front")

                st.plotly_chart(fig_worm, use_container_width=True)

            elif len(selections) >2:

                df_zero = df_combine
                df_zero = df_zero.reset_index(drop=True)
                length = df_zero.Title.value_counts()[selections[0]]
                for j in range(length,len(selections)*length):
                    df_zero.Split[j]=df_zero.Split[j]-df_zero.Split[j-length]
                    df_zero.Split[j-length]=0




                if Names=="Yes":
                    fig_worm = px.line(df_zero, x="Distance", y = "Time", title="Worm",color="Title",text="Front",markers="Front")
                    fig_worm.update_traces(textposition='top center')
                if Names=="No":
                    fig_worm = px.line(df_zero, x="Distance", y = "Time", title="Worm",color="Title",markers="Front")

                st.plotly_chart(fig_worm, use_container_width=True)






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
            df = pd.read_csv(uploaded_file)
            df=df.sort_values("Start time", ascending=True)
            col_one, col_two, col_three = st.columns(3)
            with col_one:
                rider = st.text_input("Select Rider:")

            
            splits=[0]
            
            speeds=[0]
            r=0
            df["Time"] = df["Start time"] - df["Start time"].iloc[0]
            markers = len(df)
            df["Distance"] = np.linspace(0, 62.5*(markers-1), num=markers)
            df=df.reset_index(drop=True)
            df.drop(['Timeline','Duration','Instance number','Ungrouped','Notes','Flags'],
          axis='columns', inplace=True)

            #df = df.dropna(axis=0, subset=['Time'])

            with col_two:
                offset = st.number_input("Offset:", min_value=0.00, max_value=None,value=0.12)
                schedule = round(st.number_input("Schedule:", min_value=0.00, max_value=None,value=14.3),2)
                Title = st.text_input("Plot Title:")


            with col_three:
                
                for i in range(len(df)-1):
                    splits.append(round(df.Time[i+1]-df.Time[i],3))
                    speeds.append(round((df.Distance[i+1]-df.Distance[i])*3.6/splits[i+1],2))
                    

                df["Avg_Speed"]=speeds
                df["Split"]=splits
                df.drop('Start time',
          axis='columns', inplace=True)
                df.rename(columns = {'Row':'Action'}, inplace = True)
                df.drop(index=df.index[0], axis=0, inplace=True)
                #df = df.dropna(axis=0, subset=['Time'])
                st.write(df)


            fig = px.bar(df, x='Distance', y='Avg_Speed',hover_data=[df.Split, df.Avg_Speed])
   
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






            #master_path=st.text_input("Add path to master file:",key="prompt")
            if st.button("Append this effort to master",key="upload"):




                df_save=df
                df_save.insert(0, 'Save_Date', datetime.date.today())
                df_save["Save_Date"] = pd.to_datetime(df_save['Save_Date'])
                df_save.insert(0, 'Title', Title)
                df = pd.concat([df_master, df_save], axis=0)
                df

                ##Testing downloader


                # buffer to use for excel writer
                buffer = io.BytesIO()



                @st.cache_data
                def convert_to_csv(df):
                    # IMPORTANT: Cache the conversion to prevent computation on every rerun
                    return df.to_csv(index=False).encode('utf-8')

                csv = convert_to_csv(df)

                # display the dataframe on streamlit app
        #         st.write(df)

                # download button 1 to download dataframe as csv
                download1 = st.download_button(
                    label="Download new Master as CSV",
                    data=csv,
                    file_name='IP_Master_Men.csv',
                    mime='text/csv'
                )

                # download button 2 to download dataframe as xlsx
                with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                    # Write each dataframe to a different worksheet.
                    df.to_excel(writer, sheet_name='Sheet1', index=False)
                    # Close the Pandas Excel writer and output the Excel file to the buffer
                    writer.save()

                    download2 = st.download_button(
                        label="Download new Master as Excel",
                        data=buffer,
                        file_name='IP_Master_Men.xlsx',
                        mime='application/vnd.ms-excel'
                    )                
                    

           ###################################################### Women's Individual Pursuit #############################################                 
                    
    if racetype == "Women's IP":
        df_master = pd.read_excel(f'pages/video_analysis/IP_Master_Women.xlsx')
        df_master = df_master.sort_values(["Save_Date","Title"], ascending=False)
        df_small = df_master.drop(columns=["Save_Date","Action","Video"])
        df_small
        c1,c2=st.columns(2)
        with c1:
            selections = st.multiselect(
            "Select past effort(s):",
            options=df_master["Title"].unique()
            ) 
        with c2:
            show_vids = ["No","Yes"]
            Videos = st.selectbox("Show Race Videos?", show_vids, key="Show_Vids")


        if len(selections) !=0:
            df_combine = pd.DataFrame()
            for i in range(len(selections)):
                col_1,col_2=st.columns(2)
                with col_1:
                    df_temp = df_master.loc[df_master['Title'] == selections[i]]
                    df_combine = pd.concat([df_combine, df_temp], axis=0)
                    df_small = df_temp.drop(columns=["Save_Date","Video"])
                    df_small=df_small.reset_index(drop="True")
                  
                       
                        


                    df_main = df_small.drop(columns=["Action"])
                    df_main
                with col_2:
                    average = df_small.Split.iloc[4:].mean()
                    fig = px.bar(df_temp, x='Distance', y='Avg_Speed',hover_data=[df_temp.Split, df_temp.Avg_Speed])
                    
                    fig.update_layout(
                    title={
                        'text': df_temp.Title.iloc[0],
                        'y':0.9,
                        'x':0.5,
                        'xanchor': 'center',
                        'yanchor': 'top',
                        'font':dict(size=25)})
                    fig.add_hline(y=62.5*3.6/average, line_dash="dash",line_color="yellow",annotation_text="Avg after first lap = " +str(round(average*4,2)))
                    yaxis_min = min(df_temp["Avg_Speed"][1:])-1
                    yaxis_max = max(df_temp["Avg_Speed"])+1
                    fig.update_layout(yaxis_range=[yaxis_min,yaxis_max])
                    st.plotly_chart(fig, use_container_width=True)
                c1,c2=st.columns(2)
                with c1:

                    
                    
                    st.subheader("Start Splits")
                    df_start=pd.DataFrame(df_small["Distance"][0:4])
                    df_start["Split"]=df_small["Split"][0:4]
                    df_start["Total"]=df_small["Split"][0:4].cumsum()
                    df_start
                    st.subheader("Kilo Splits")
                    df_kilos=pd.DataFrame(["1k","2k","3k"])
                    df_kilos.columns=["Distance"]
                    kilo_split = [sum(df_small["Split"][0:16]),sum(df_small["Split"][16:32]),sum(df_small["Split"][32:48])]
                    df_kilos["Split"]=kilo_split
                    df_kilos["Total"]=df_kilos["Split"].cumsum()
                    df_kilos['Total'] = pd.to_datetime(df_kilos['Total'], unit='s').dt.strftime('%M:%S.%f')
                    df_kilos
                if Videos == "Yes":
                    with c2:
                        if pd.isnull(df_temp["Video"].iloc[0]):
                            st.header("No video available")
                        else:
                            video_name = df_temp["Video"].iloc[0]
                            st.header(df_temp["Title"].iloc[0])
   
                            st.video(f"{video_name}")
                st.markdown("---")



            col_one, col_two, col_three, col_four = st.columns(4)
            with col_one:
           
                fig_tt = px.line(df_combine, x="Distance", y = "Avg_Speed", title="Comparison",color="Title",markers="Front")

            st.plotly_chart(fig_tt, use_container_width=True)

            if len(selections) ==2:

                df_zero = df_combine
                df_zero = df_zero.reset_index(drop=True)
                length = df_zero.Title.value_counts()[selections[0]]
                for j in range(length,len(selections)*length):
                    df_zero.Split[j]=df_zero.Split[j]-df_zero.Split[j-length]
                    df_zero.Split[j-length]=0



                fig_zero = px.line(df_zero, x="Distance", y = "Split", title="Zero",color="Title",markers="Front")
                st.plotly_chart(fig_zero, use_container_width=True)
               
                fig_worm = px.line(df_zero, x="Distance", y = "Time", title="Worm",color="Title",markers="Front")

                st.plotly_chart(fig_worm, use_container_width=True)

            elif len(selections) >2:

                df_zero = df_combine
                df_zero = df_zero.reset_index(drop=True)
                length = df_zero.Title.value_counts()[selections[0]]
                for j in range(length,len(selections)*length):
                    df_zero.Split[j]=df_zero.Split[j]-df_zero.Split[j-length]
                    df_zero.Split[j-length]=0




                if Names=="Yes":
                    fig_worm = px.line(df_zero, x="Distance", y = "Time", title="Worm",color="Title",text="Front",markers="Front")
                    fig_worm.update_traces(textposition='top center')
                if Names=="No":
                    fig_worm = px.line(df_zero, x="Distance", y = "Time", title="Worm",color="Title",markers="Front")

                st.plotly_chart(fig_worm, use_container_width=True)






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
            df = pd.read_csv(uploaded_file)
            df=df.sort_values("Start time", ascending=True)
            col_one, col_two, col_three = st.columns(3)
            with col_one:
                rider = st.text_input("Select Rider:")

            
            splits=[0]
            
            speeds=[0]
            r=0
            df["Time"] = df["Start time"] - df["Start time"].iloc[0]
            markers = len(df)
            df["Distance"] = np.linspace(0, 62.5*(markers-1), num=markers)
            df=df.reset_index(drop=True)
            df.drop(['Timeline','Duration','Instance number','Ungrouped','Notes','Flags'],
          axis='columns', inplace=True)

            #df = df.dropna(axis=0, subset=['Time'])

            with col_two:
                offset = st.number_input("Offset:", min_value=0.00, max_value=None,value=0.12)
                schedule = round(st.number_input("Schedule:", min_value=0.00, max_value=None,value=14.3),2)
                Title = st.text_input("Plot Title:")


            with col_three:
                
                for i in range(len(df)-1):
                    splits.append(round(df.Time[i+1]-df.Time[i],3))
                    speeds.append(round((df.Distance[i+1]-df.Distance[i])*3.6/splits[i+1],2))
                    

                df["Avg_Speed"]=speeds
                df["Split"]=splits
                df.drop('Start time',
          axis='columns', inplace=True)
                df.rename(columns = {'Row':'Action'}, inplace = True)
                df.drop(index=df.index[0], axis=0, inplace=True)
                #df = df.dropna(axis=0, subset=['Time'])
                st.write(df)


            fig = px.bar(df, x='Distance', y='Avg_Speed',hover_data=[df.Split, df.Avg_Speed])
   
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






            #master_path=st.text_input("Add path to master file:",key="prompt")
            if st.button("Append this effort to master",key="upload"):




                df_save=df
                df_save.insert(0, 'Save_Date', datetime.date.today())
                df_save["Save_Date"] = pd.to_datetime(df_save['Save_Date'])
                df_save.insert(0, 'Title', Title)
                df = pd.concat([df_master, df_save], axis=0)
                df

                ##Testing downloader


                # buffer to use for excel writer
                buffer = io.BytesIO()



                @st.cache_data
                def convert_to_csv(df):
                    # IMPORTANT: Cache the conversion to prevent computation on every rerun
                    return df.to_csv(index=False).encode('utf-8')

                csv = convert_to_csv(df)

                # display the dataframe on streamlit app
        #         st.write(df)

                # download button 1 to download dataframe as csv
                download1 = st.download_button(
                    label="Download new Master as CSV",
                    data=csv,
                    file_name='IP_Master_Women.csv',
                    mime='text/csv'
                )

                # download button 2 to download dataframe as xlsx
                with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                    # Write each dataframe to a different worksheet.
                    df.to_excel(writer, sheet_name='Sheet1', index=False)
                    # Close the Pandas Excel writer and output the Excel file to the buffer
                    writer.save()

                    download2 = st.download_button(
                        label="Download new Master as Excel",
                        data=buffer,
                        file_name='IP_Master_Women.xlsx',
                        mime='application/vnd.ms-excel'
                    )                
                    
