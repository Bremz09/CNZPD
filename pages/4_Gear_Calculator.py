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
    st.header("All Data")
    df_master = pd.read_excel(f'pages/Gear_Calculator/Gear_Calculator_Master.xlsx')
    df_master["Competition Date"]=pd.to_datetime(df_master["Competition Date"]).dt.date
    df_master
    
        # buffer to use for excel writer
    buffer = io.BytesIO()
    @st.cache_data
    def convert_to_csv(df_master):
        # IMPORTANT: Cache the conversion to prevent computation on every rerun
        return df_master.to_csv(index=False).encode('utf-8')
    csv = convert_to_csv(df_master)
    # download button 1 to download dataframe as csv
    download1 = st.download_button(
        label="Download All Gear Data as CSV",
        data=csv,
        file_name='All_Gear_Data.csv',
        mime='text/csv'
    )

    # download button 2 to download dataframe as xlsx
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        # Write each dataframe to a different worksheet.
        df_master.to_excel(writer, sheet_name='Sheet1', index=False)
        # Close the Pandas Excel writer and output the Excel file to the buffer
        writer.close()

        download2 = st.download_button(
            label="Download All Gear Data as Excel",
            data=buffer,
            file_name='All_Gear_Data.xlsx',
            mime='application/vnd.ms-excel'
        )  
    
    
    
    ###Filtering Bit -- REALLY GOOD!!
    st.header("Filtered Data")
    import pandas as pd
    import streamlit as st
    import streamlit.components.v1 as components
    from pandas.api.types import (
    is_categorical_dtype,
    is_datetime64_any_dtype,
    is_numeric_dtype,
    is_object_dtype,
    )


    def filter_dataframe(df: pd.DataFrame) -> pd.DataFrame:

        modify = st.checkbox("Add filters")

        if not modify:
            return df

        df = df.copy()

        # Try to convert datetimes into a standard format (datetime, no timezone)
        for col in df.columns:
            if is_object_dtype(df[col]):
                try:
                    df[col] = pd.to_datetime(df[col])
                except Exception:
                    pass

            if is_datetime64_any_dtype(df[col]):
                df[col] = df[col].dt.tz_localize(None)

        modification_container = st.container()

        with modification_container:
            to_filter_columns = st.multiselect("Filter dataframe on", df.columns)
            for column in to_filter_columns:
                left, right = st.columns((1, 20))
                # Treat columns with < 10 unique values as categorical
                if is_categorical_dtype(df[column]) or df[column].nunique() < 10:
                    user_cat_input = right.multiselect(
                        f"Values for {column}",
                        df[column].unique(),
                        default=list(df[column].unique()),
                    )
                    df = df[df[column].isin(user_cat_input)]
                elif is_numeric_dtype(df[column]):
                    _min = float(df[column].min())
                    _max = float(df[column].max())
                    step = (_max - _min) / 100
                    user_num_input = right.slider(
                        f"Values for {column}",
                        min_value=_min,
                        max_value=_max,
                        value=(_min, _max),
                        step=step,
                    )
                    df = df[df[column].between(*user_num_input)]
                elif is_datetime64_any_dtype(df[column]):
                    user_date_input = right.date_input(
                        f"Values for {column}",
                        value=(
                            df[column].min(),
                            df[column].max(),
                        ),
                    )
                    if len(user_date_input) == 2:
                        user_date_input = tuple(map(pd.to_datetime, user_date_input))
                        start_date, end_date = user_date_input
                        df = df.loc[df[column].between(start_date, end_date)]
                else:
                    user_text_input = right.text_input(
                        f"Substring or regex in {column}",
                    )
                    if user_text_input:
                        df = df[df[column].astype(str).str.contains(user_text_input, case=False)]

        return df


        
        
        
        
        
        
        
        

    

    df = df_master
    df_filt = filter_dataframe(df)
    df_filt
    
    
    # buffer to use for excel writer
    buffer = io.BytesIO()
    @st.cache_data
    def convert_to_csv(df_filt):
        # IMPORTANT: Cache the conversion to prevent computation on every rerun
        return df_filt.to_csv(index=False).encode('utf-8')
    csv = convert_to_csv(df_filt)
    # download button 1 to download dataframe as csv
    download1 = st.download_button(
        label="Download Filtered Data as CSV",
        data=csv,
        file_name='Filtered_Gear_Data.csv',
        mime='text/csv'
    )

    # download button 2 to download dataframe as xlsx
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        # Write each dataframe to a different worksheet.
        df_filt.to_excel(writer, sheet_name='Sheet1', index=False)
        # Close the Pandas Excel writer and output the Excel file to the buffer
        writer.close()

        download2 = st.download_button(
            label="Download Filtered Data as Excel",
            data=buffer,
            file_name='Filtered_Gear_Data.xlsx',
            mime='application/vnd.ms-excel'
        )  

    
    
    


    st.header("Gear Calculator")
    st.write("Upload a file to calculate the gear")
    
    uploaded_file = st.file_uploader("Choose a file",key="uploader")

    if uploaded_file is not None:
        st.markdown("---")

        st.header("Editor")
        
        # Check if new file uploaded and reset row inputs
        current_file_name = uploaded_file.name
        if 'last_uploaded_file' not in st.session_state or st.session_state.last_uploaded_file != current_file_name:
            st.session_state.last_uploaded_file = current_file_name
            st.session_state.next_start_row = 1
            st.session_state.next_end_row = 17
            st.session_state.accumulated_batches = pd.DataFrame()  # Clear accumulated batches
            # Also clear the widget states
            if 'start_input' in st.session_state:
                del st.session_state.start_input
            if 'end_input' in st.session_state:
                del st.session_state.end_input
            st.rerun()  # Force rerun to apply the reset values
        
        # Check file type by extension
        file_name = uploaded_file.name.lower()
        df_full = None
        
        if file_name.endswith(('.xlsx', '.xls', '.xlsm')):
            # Handle Excel files
            try:
                df_full = pd.read_excel(uploaded_file, usecols='A:C')
            except Exception as e:
                st.error(f"Unable to read Excel file: {str(e)}")
                st.stop()
        else:
            # Handle CSV files with different encodings
            encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252', 'utf-8-sig']
            for encoding in encodings:
                try:
                    uploaded_file.seek(0)  # Reset file pointer to beginning
                    df_full = pd.read_csv(
                        uploaded_file, 
                        encoding=encoding,
                        on_bad_lines='skip',  # Skip malformed lines
                        engine='python'  # Use Python engine which is more forgiving
                    )
                    break
                except (UnicodeDecodeError, LookupError, Exception):
                    continue
            
            if df_full is None:
                st.error("Unable to read the CSV file. Please check the file encoding and format.")
                st.stop()
        
        # Convert time columns to seconds if they exist
        def convert_time_to_seconds(time_val):
            """Convert time value to total seconds"""
            if pd.isna(time_val):
                return None
            
            # If it's already a numeric value, treat it as decimal day format and convert to seconds
            if isinstance(time_val, (int, float)):
                return round(time_val * 86400, 2)
            
            # Otherwise try to parse as time string (MM:SS or HH:MM:SS)
            time_str = str(time_val).strip()
            parts = time_str.split(':')
            
            try:
                if len(parts) == 2:  # MM:SS format
                    minutes, seconds = map(float, parts)
                    return round(minutes * 60 + seconds, 2)
                elif len(parts) == 3:  # HH:MM:SS format
                    hours, minutes, seconds = map(float, parts)
                    return round(hours * 3600 + minutes * 60 + seconds, 2)
                else:
                    return round(float(time_val) * 86400, 2)  # Try decimal day format
            except (ValueError, AttributeError):
                return None
        
        # Apply conversion to "Position" column if it exists
        if "Position" in df_full.columns:
            df_full["Position"] = df_full["Position"].apply(convert_time_to_seconds)
        
        # Keep original order from Excel
        df_full = df_full.reset_index(drop=True)
        
        # Set default start and end rows
        max_rows = len(df_full)
        st.write(f"Total rows in file: {max_rows}")
        
        # Initialize session state for row tracking (always start at 1, 17)
        if 'next_start_row' not in st.session_state:
            st.session_state.next_start_row = 1
        if 'next_end_row' not in st.session_state:
            st.session_state.next_end_row = 17
        
        col_input1, col_input2 = st.columns(2)
        with col_input1:
            start_row = st.number_input("Start row:", min_value=1, max_value=max_rows, value=min(st.session_state.next_start_row, max_rows), step=1, key="start_input")
        with col_input2:
            end_row = st.number_input("End row:", min_value=1, max_value=max_rows, value=min(st.session_state.next_end_row, max_rows), step=1, key="end_input")
        
        start = start_row - 1  # Convert to 0-based index
        end = end_row
        
        df = df_full[start:end]
        
        # Reset index to start from 1
        df = df.reset_index(drop=True)
        df.index = df.index + 1
        
        st.write("Just include all the relevant info and it'll do the rest")
        
        # Initialize gear variables early
        gear = None
        rps = None
        mps = None
        rev_count = None
        pl_start = None
        pl_finish = None
        rev_start = None
        rev_finish = None
        nearest_gear = None
        coaches_chart = None
        
        # Define possible gears
        round_to=[113.40,103.09,94.50,87.23,81.00,75.60,70.88,66.71,63.00,59.68,56.70,54.00,51.55,49.30,47.25,45.36,116.10,105.55,96.75,89.31,82.93,77.40,72.56,68.29,64.50,61.11,58.05,55.29,52.77,50.48,48.38,46.44,118.80,108.00,99.00,91.38,84.86,79.20,74.25,69.88,66.00,62.53,59.40,56.57,51.65,49.50,47.52,121.50,110.45,101.25,93.46,86.79,75.94,71.47,67.50,63.95,60.75,57.86,55.23,52.83,50.63,48.60,124.20,112.91,103.50,95.54,88.71,82.80,77.63,73.06,69.00,65.37,62.10,59.14,56.45,51.75,49.68,126.90,115.36,105.75,97.62,90.64,84.60,79.31,74.65,70.50,66.79,63.45,60.43,57.68,55.17,52.88,50.76,129.60,117.82,99.69,92.57,86.40,76.24,72.00,68.21,64.80,61.71,58.91,56.35,51.84,132.30,120.27,110.25,101.77,88.20,82.69,77.82,73.50,69.63,66.15,60.14,57.52,55.13,52.92,135.00,122.73,112.50,103.85,96.43,90.00,84.38,79.41,75.00,71.05,64.29,61.36,58.70,56.25,137.70,125.18,114.75,105.92,98.36,91.80,86.06,76.50,72.47,68.85,65.57,62.59,59.87,57.38,55.08,140.40,127.64,117.00,100.29,93.60,87.75,82.59,78.00,73.89,70.20,66.86,63.82,61.04,58.50,56.16,143.10,130.09,119.25,110.08,102.21,95.40,89.44,84.18,79.50,75.32,71.55,68.14,65.05,62.22,59.63,57.24,145.80,132.55,112.15,104.14,97.20,91.13,85.76,76.74,72.90,69.43,66.27,63.39,58.32,148.50,123.75,114.23,106.07,92.81,87.35,82.50,78.16,70.71,64.57,61.88,151.20,137.45,126.00,116.31,100.80,88.94,84.00,79.58,68.73,65.74,60.48,153.90,139.91,128.25,118.38,109.93,102.60,96.19,90.53,85.50,76.95,73.29,69.95,66.91,64.13,61.56,156.60,142.36,130.50,120.46,111.86,104.40,97.88,92.12,87.00,82.42,78.30,74.57,71.18,68.09,65.25,62.64,159.30,144.82,132.75,122.54,113.79,106.20,99.56,93.71,88.50,83.84,79.65,75.86,72.41,69.26,66.38,63.72,162.00,147.27,124.62,115.71,95.29,85.26,77.14,73.64,70.43,164.70,149.73,137.25,126.69,117.64,109.80,102.94,96.88,91.50,86.68,82.35,78.43,74.86,71.61,68.63,65.88,167.40,152.18,139.50,128.77,119.57,111.60,104.63,98.47,93.00,88.11,83.70,79.71,76.09,72.78,69.75,66.96,170.10,154.64,141.75,130.85,106.31,100.06,89.53,85.05,77.32,73.96,68.04,172.80,157.09,144.00,132.92,123.43,115.20,101.65,96.00,90.95,82.29,78.55,75.13,69.12,175.50,159.55,146.25,125.36,109.69,103.24,97.50,92.37,83.57,79.77,76.30,73.13,178.20,137.08,127.29,111.38,104.82,93.79,89.10,77.48,71.28,180.90,164.45,150.75,139.15,129.21,120.60,113.06,106.41,100.50,95.21,90.45,86.14,82.23,78.65,75.38,72.36,183.60,166.91,153.00,141.23,131.14,122.40,102.00,96.63,87.43,83.45,79.83,73.44,186.30,169.36,155.25,143.31,133.07,116.44,109.59,98.05,93.15,84.68,74.52,189.00,171.82,157.50,145.38,118.13,111.18,105.00,99.47,85.91,82.17,78.75,191.70,174.27,159.75,147.46,136.93,127.80,119.81,112.76,106.50,100.89,95.85,91.29,87.14,83.35,79.88,76.68,194.40,176.73,149.54,138.86,114.35,102.32,88.36,84.52,77.76,197.10,179.18,164.25,151.62,140.79,131.40,123.19,115.94,109.50,103.74,98.55,93.86,89.59,85.70,82.13,78.84,199.80,181.64,166.50,153.69,142.71,133.20,124.88,117.53,111.00,105.16,99.90,95.14,90.82,86.87,83.25,79.92,202.50,184.09,168.75,155.77,144.64,126.56,119.12,106.58,92.05,88.04,205.20,186.55,171.00,157.85,146.57,136.80,120.71,114.00,97.71,93.27,89.22,82.08,207.90,173.25,159.92,138.60,129.94,122.29,115.50,109.42,103.95,90.39,86.63,83.16,210.60,191.45,150.43,131.63,123.88,110.84,105.30,95.73,91.57,84.24,213.30,193.91,177.75,164.08,152.36,142.20,133.31,125.47,118.50,112.26,106.65,101.57,96.95,92.74,88.88,85.32,216.00,196.36,180.00,166.15,154.29,127.06,120.00,113.68,102.86,98.18,93.91]
        
        # Calculate gear metrics BEFORE displaying columns
        if "Name" in df.columns and "Position" in df.columns:
            try:
                #This is to find the revs per second
                if df['Name'].str.contains(r'Rev start', na=False, regex=True).any() and df['Name'].str.contains(r'Rev finish', na=False, regex=True).any():
                    rev_start = df.loc[df['Name'].str.contains(r'Rev start', na=False, regex=True)]["Position"].item()
                    rev_finish = df.loc[df['Name'].str.contains(r'Rev finish', na=False, regex=True)]["Position"].item()
                    # Count completed revolutions (Rev (1), Rev (2), etc) plus the final revolution ending at Rev finish
                    rev_count = len(df[df['Name'].str.contains(r'Rev \(\d+\)', na=False, regex=True)]) + 1
                    
                    if rev_count > 0:
                        rps = rev_count/(rev_finish-rev_start)
                
                #This is to find Speed (Pursuit Line)
                if df['Name'].str.contains(r'PL start', na=False, regex=True).any() and df['Name'].str.contains(r'PL finish', na=False, regex=True).any():
                    pl_start=df.loc[df['Name'].str.contains(r'PL start', na=False, regex=True)]["Position"].item()
                    pl_finish=df.loc[df['Name'].str.contains(r'PL finish', na=False, regex=True)]["Position"].item()
                    distance = 125.25  # 125.25 meters between pursuit lines
                    mps = distance/(pl_finish-pl_start)
                    
                    if rps is not None and rps > 0:
                        mpr = mps/rps
                        m_developed = mpr * 1.030819675
                        gear = round(m_developed / (np.pi * 0.0254), 2)
                        nearest_gear = min(round_to, key=lambda x: abs(x - gear))
                        coaches_chart = round(m_developed / 2.096 * 27, 1)
            except Exception as e:
                st.error(f"Error calculating gear: {str(e)}")
        
        col_data, col_gap, col_metrics, col_info = st.columns((2, 0.3, 3.4, 3.3))
        with col_data:
            st.write("**Uploaded Data:**")
            # Calculate height based on number of rows
            table_height = min(35 + len(df) * 35, 800)  # Cap at 800px max
            st.dataframe(df, use_container_width=True, height=table_height)
        with col_gap:
            pass
        with col_metrics:
            st.write("**Calculation Metrics:**")
            if gear is not None:
                # Display calculation metrics in a table
                pl_time = pl_finish - pl_start
                rev_time = rev_finish - rev_start
                mpr = mps/rps
                m_developed = mpr * 1.030819675
                metrics_data = {
                    'Metric': ['Pursuit Line Time', 'Meters Per Second', 'Total Revolutions', 'Rev Time', 'Revolutions Per Second', 'Meters Per Revolution', 'Meters Developed'],
                    'Value': [f"{pl_time:.8f}".rstrip('0').rstrip('.') + 's',
                              f"{mps:.8f}".rstrip('0').rstrip('.'),
                              f"{rev_count}",
                              f"{rev_time:.8f}".rstrip('0').rstrip('.') + 's',
                              f"{rps:.8f}".rstrip('0').rstrip('.'),
                              f"{mpr:.8f}".rstrip('0').rstrip('.'),
                              f"{m_developed:.8f}".rstrip('0').rstrip('.')]
                }
                metrics_df = pd.DataFrame(metrics_data)
                st.dataframe(metrics_df, hide_index=True, use_container_width=False)
                
                st.subheader(f"Calculated gear is {gear}")
                nearest_gear = min(round_to, key=lambda x: abs(x - gear))
                st.subheader(f"Nearest possible gear is {nearest_gear}")
                coaches_chart = round(m_developed / 2.096 * 27, 1)
            else:
                st.info("Upload data and fill in race information to calculate metrics")
                nearest_gear = None
        with col_info:
            st.write("**Race Information:**")
            event = st.selectbox("Event:", options=["Team Sprint","Sprint Qual","Match Sprint","Keirin","Team Pursuit","Madison","Bunch","Individual Pursuit","Om Scratch","Om Tempo","Om Elim","Om Points"])
            
            if event == "Team Pursuit" or event == "Team Sprint":
                
                position = st.selectbox("Position:", options=[1,2,3,4],key="position")
            else:
                position="Null"
            # Get default name from "Name" column if it exists, otherwise use empty string
            name = st.text_input("Rider Name:")
            nation = st.selectbox("Nation:", options=["NZL","AUS","CAN","ESP","FRA","GBR","GER","ITA","JPN","KOR","NED","SUI","USA"],key="nation")
            location = st.selectbox("Event Location:", options=["Perth","Hong Kong","Malaysia","Santiago","Paris","Tokyo","Los Angeles","Rio de Janeiro","Cambridge"],key="location")
            sex = st.selectbox("Sex:", options=["M","F"],key="Sex")
            comp = st.selectbox("Competition:", options=["NC","WCH","OLY","COM"],key="competition")
            Round = st.selectbox("Round:", options=["Q","R1","R2","R3","Rep","F","A Final","B Final"],key="Round")
            comp_date = st.date_input("Competition Date:")
            ##I'm using 2.111 instead of wheel circumference. Seems to work better.
            #wheel_circ = st.number_input("Wheel Circumference:",value=2.096,step=1e-3, format="%.3f")
        
        st.markdown("---")
        
        #master_path=st.text_input("Add path to master file:",key="prompt")
        
        # Format name: Last name first, capitalized
        if name:
            name_parts = name.split()
            if len(name_parts) >= 2:
                formatted_name = name_parts[-1].upper() + " " + " ".join(name_parts[:-1]).title()
            else:
                formatted_name = name.upper()
        else:
            formatted_name = ""
        
        data = [[formatted_name, nation, sex, event, position, comp, location, Round, comp_date, gear, nearest_gear, coaches_chart]]
        df = pd.DataFrame(data, columns=['Name', 'Nation','Sex','Event','Position','Competition','Location','Round','Competition Date','Calculated Gear','Nearest Possible Gear','Coaches Chart'])
        
        st.subheader("Current Batch Data")
        st.dataframe(df, hide_index=True, use_container_width=False)
        
        st.markdown("""
            <style>
            .stButton > button:hover {
                background-color: green !important;
                color: white !important;
                border-color: green !important;
            }
            div.stButton > button {
                display: block;
                margin: 0 auto;
                font-size: 18px;
                padding: 12px 30px;
                height: auto;
            }
            </style>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.subheader("Batch Processing")
        
        # Initialize session state for batch accumulation
        if 'accumulated_batches' not in st.session_state:
            st.session_state.accumulated_batches = pd.DataFrame()
        
        st.markdown("<style>div.stButton > button {width: fit-content; margin-left: 0;}</style>", unsafe_allow_html=True)
        
        if st.button("Save & Continue to Next Batch", key="save_continue"):
            # Accumulate current batch
            st.session_state.accumulated_batches = pd.concat(
                [st.session_state.accumulated_batches, df], 
                ignore_index=True
            )
            
            # Update row numbers for next batch
            row_range = end_row - start_row + 1
            st.session_state.next_start_row = end_row + 1
            st.session_state.next_end_row = min(end_row + row_range, max_rows)
            
            st.success(f"Batch saved! Total rows accumulated: {len(st.session_state.accumulated_batches)}")
            st.rerun()
        
        # Display accumulated batches count
        if len(st.session_state.accumulated_batches) > 0:
            st.info(f"Accumulated data: {len(st.session_state.accumulated_batches)} rows ready to append")
            st.subheader("Saved Batches")
            st.dataframe(st.session_state.accumulated_batches, hide_index=True, use_container_width=False)
        
        st.subheader("Append to Master Data")
        st.write("")  # Add some spacing
        if st.button("Append info to master",key="upload"):
                # Use accumulated batches if available, otherwise use current batch
                if len(st.session_state.accumulated_batches) > 0:
                    df_save = st.session_state.accumulated_batches
                    st.session_state.accumulated_batches = pd.DataFrame()  # Clear accumulated batches
                else:
                    df_save = df
                
                # Calculate range and update session state for next iteration
                row_range = end_row - start_row + 1
                st.session_state.next_start_row = end_row + 1
                st.session_state.next_end_row = min(end_row + row_range, max_rows)
                
                df_combined = pd.concat([df_master, df_save], axis=0)
                # Reset index to keep ascending numbers
                df_combined = df_combined.reset_index(drop=True)
                df_combined.index = df_combined.index + 1
                
                st.success("Data ready to download!")

                ##Testing downloader

                # buffer to use for excel writer
                buffer = io.BytesIO()

                @st.cache_data
                def convert_to_csv(df_combined):
                    # IMPORTANT: Cache the conversion to prevent computation on every rerun
                    return df_combined.to_csv(index=False).encode('utf-8')

                csv = convert_to_csv(df_combined)

                # display the dataframe on streamlit app
                st.subheader("**Updated Master Data:**")
                st.dataframe(df_combined, hide_index=False, use_container_width=True)

                # download button 1 to download dataframe as csv
                download1 = st.download_button(
                    label="Download new Master as CSV",
                    data=csv,
                    file_name='Gear_Calculator_Master.csv',
                    mime='text/csv'
                )

                # download button 2 to download dataframe as xlsx
                with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                    # Write each dataframe to a different worksheet.
                    df_combined.to_excel(writer, sheet_name='Sheet1', index=False)
                    # Close the Pandas Excel writer and output the Excel file to the buffer
                    writer.close()

                    download2 = st.download_button(
                        label="Download new Master as Excel",
                        data=buffer,
                        file_name='Gear_Calculator_Master.xlsx',
                        mime='application/vnd.ms-excel'
                    )  


