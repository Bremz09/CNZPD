#!/usr/bin/env python
# coding: utf-8


import pickle
import pandas as pd
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import math
import time

from sklearn.linear_model import LinearRegression

st.set_page_config(page_title='CNZ Performance Database',
                  page_icon=":bike:",
                  layout="wide")

# --- Helper Functions ---

def process_rider(df, rider_prefix, distance_markers, slope_adjustments, vertical_shifts, color='blue'):
    valid_mask = ~df[[f'{rider_prefix} speed', f'{rider_prefix} distance']].isna().any(axis=1)
    df_valid = df[valid_mask].copy()
    time = df_valid['time'].values
    speed = df_valid[f'{rider_prefix} speed'].values
    distance = df_valid[f'{rider_prefix} distance'].values

    num_segments = len(distance_markers) - 1
    adjusted_speed = np.zeros_like(speed)
    best_fit_lines = []

    for i in range(num_segments):
        start_dist = distance_markers[i]
        end_dist = distance_markers[i + 1]
        segment_mask = (distance >= start_dist) & (distance < end_dist if i < num_segments - 1 else distance <= end_dist)
        segment_indices = np.where(segment_mask)[0]

        if len(segment_indices) == 0:
            continue

        segment_time = time[segment_indices].reshape(-1, 1)
        segment_speed = speed[segment_indices]

        model = LinearRegression()
        model.fit(segment_time, segment_speed)

        residuals = segment_speed - model.predict(segment_time)
        original_slope = model.coef_[0]
        original_intercept = model.intercept_

        # Anchor the first point and adjust slope
        t0 = segment_time[0][0]
        y0 = original_slope * t0 + original_intercept
        adjusted_slope = original_slope + slope_adjustments[i]
        adjusted_intercept = y0 - adjusted_slope * t0

        adjusted_fit = adjusted_slope * segment_time.flatten() + adjusted_intercept
        adjusted_segment_speed = adjusted_fit + residuals + vertical_shifts[i]

        adjusted_speed[segment_indices] = adjusted_segment_speed
        best_fit_lines.append((segment_time.flatten(), adjusted_fit + vertical_shifts[i]))

    crop_mask = distance <= distance_markers[-1]
    adjusted_speed[~crop_mask] = np.nan
    df.loc[valid_mask, f'{rider_prefix} speed adjusted'] = adjusted_speed

    # Plot for live feedback
    fig, ax = plt.subplots(figsize=(22, 6))
    ax.plot(time, speed, label=f'Original {rider_prefix.upper()} Speed', color='gray', alpha=0.6)
    ax.plot(time, adjusted_speed, label=f'Adjusted {rider_prefix.upper()} Speed', color=color)
    for i, (segment_time, fit_values) in enumerate(best_fit_lines):
        ax.plot(segment_time, fit_values, label=f'Segment {i+1} Adjusted Fit', linestyle='--', color='green')
    # Add vertical lines and annotations for each segment end (except the first marker)
    segment_ends = distance_markers[1:]  # skip the 0 marker
    segment_starts = distance_markers[:-1]
    prev_time = None
    for seg_idx, (start_dist, end_dist) in enumerate(zip(segment_starts, segment_ends)):
        # Find the first index where distance >= end_dist
        seg_mask = distance >= end_dist
        if not np.any(seg_mask):
            continue
        idx = np.argmax(seg_mask)
        seg_time = time[idx]
        # Cumulative time at this segment end
        cum_time = seg_time
        # Split time for this segment
        if seg_idx == 0:
            split_time = cum_time
        else:
            split_time = cum_time - prev_time
        prev_time = cum_time
        # Draw vertical line
        ax.axvline(seg_time, color='red', linestyle=':', alpha=0.7)
        # Annotate
        ax.annotate(
            f"{cum_time:.2f}s\nΔ{split_time:.2f}s",
            xy=(seg_time, ax.get_ylim()[1]),
            xytext=(0, -260),
            textcoords='offset points',
            ha='center',
            va='top',
            fontsize=19,
            color='red',
            bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="red", lw=0.5, alpha=0.7)
        )
    ax.set_title(f'Adjusted {rider_prefix.upper()} Speed with Segment Fit Lines and Distance Markers')
    ax.set_xlabel('Time')
    ax.set_ylabel('Speed')
    ax.grid(False)
    plt.tight_layout()
    return fig

def get_bank_r_wh_r_cm_lean(segment,COM,v_com,v_wh):
    pl_to_trans = 21.25
    trans_len = 10
    rad_of_curve = (250 - 4*(pl_to_trans))/(2*math.pi)
    bend_bank = 46.13
    straight_bank = 13
    bend_length = 125 - 2*(pl_to_trans+trans_len)
    if (segment < pl_to_trans) or (segment>125-pl_to_trans): #On either straight
        bank = straight_bank
        r_wh = 2*rad_of_curve
        r_cm = r_wh
    elif segment <= pl_to_trans + trans_len: #Going into the bend
        pct_through_trans = (segment-pl_to_trans)/trans_len
        bank = straight_bank + pct_through_trans*(bend_bank-straight_bank)
        r_wh = 2*rad_of_curve - pct_through_trans*rad_of_curve
    elif segment<=pl_to_trans + trans_len + bend_length: #In the bend
        bank = bend_bank
        r_wh = rad_of_curve
    else: # Exiting the bend
        pct_through_trans = (segment-(pl_to_trans+trans_len+bend_length))/trans_len
        bank = bend_bank + pct_through_trans*(straight_bank-bend_bank)
        r_wh = rad_of_curve + pct_through_trans*rad_of_curve
    asin_arg = (r_wh / COM) * (1 - (v_com / v_wh))
    asin_arg = max(min(asin_arg, 1), -1) # Clamp to [-1, 1]
    lean = math.degrees(math.asin(asin_arg))
    camber = bank - lean
    r_cm = r_wh - math.sin(math.radians(lean))*COM
    return bank, r_wh, r_cm, lean, camber

def fast_smooth_over_revolution(df, value_col, cadence_col, time_col, step=10, pad_seconds=10):
    if len(df) > 1:
        dt = np.median(np.diff(df[time_col]))
    else:
        dt = 0.01
    pad_points = int(pad_seconds / dt)
    pad_values = np.zeros(pad_points)
    pad_cadence = np.ones(pad_points) * 60
    pad_time = np.linspace(df[time_col].iloc[0] - pad_seconds, df[time_col].iloc[0] - dt, pad_points)
    values = np.concatenate([pad_values, df[value_col].values])
    cadence = np.concatenate([pad_cadence, df[cadence_col].values])
    time = np.concatenate([pad_time, df[time_col].values])
    idxs = np.arange(0, len(values), step)
    values_ds = values[idxs]
    cadence_ds = cadence[idxs]
    time_ds = time[idxs]
    smoothed_ds = np.full(len(values_ds), np.nan)
    for j in range(len(values_ds)):
        c = cadence_ds[j]
        if np.isnan(c) or c <= 0:
            continue
        period = 60.0 / c
        t = time_ds[j]
        mask = (time_ds >= t - period/2) & (time_ds <= t + period/2)
        vals = values_ds[mask]
        if len(vals) > 0:
            smoothed_ds[j] = vals.mean()
    smoothed_full = np.interp(np.arange(len(values)), idxs, smoothed_ds, left=np.nan, right=np.nan)
    smoothed_full = smoothed_full[pad_points:]
    return smoothed_full

def downsample_df(df, step=10):
    return df.iloc[::step].reset_index(drop=True)

# --- USER AUTHENTICATION ---

with open("hashed_pw.pkl","rb") as file:
    hashed_passwords = pickle.load(file)

usernames = ['CNZ']
names = ['CNZ']
credentials = {"usernames":{}}
for uname,name,pwd in zip(usernames,names,hashed_passwords):
    user_dict = {"name": name, "password": pwd}
    credentials["usernames"].update({uname: user_dict})

import streamlit_authenticator as stauth
authenticator = stauth.Authenticate(credentials, "CNZPD", "abcdef", cookie_expiry_days=30)
name, authentication_status, username = authenticator.login("Login", "main")

if authentication_status == False:
    st.error("Username/password is incorrect")
if authentication_status == None:
    st.warning("Please enter your username and password")

if authentication_status:
    st.header('Modelling Tool')
    if 'df_orig' not in st.session_state:
        st.session_state['df_orig'] = pd.read_excel("pages/WTS model base.xlsx")
        # st.session_state['df_orig'] = pd.read_excel("C:\\Users\\SamB\\OneDrive - SportNZGroup\\Desktop\\Analysis\\Sprint Modelling\\WTS Q Olympics traces.xlsx")

    # --- Initial Calculations ---
    gear = [103.2, 108, 111.4]
    gear_ratio = [x / 27 for x in gear]
    mass = [63.5+6.8, 85.6+6.8, 81.7+6.8]
    weight = [x * 9.81 for x in mass]
    COM = [0.94, 1.04, 1.01]
    rho = 1.169
    wheel_circ = 2.096
    efficiency = 1
    mu_rr = 0.0021
    ks = 0.0072
    wheel_radius = wheel_circ/(2*math.pi)
    fixed_window_size = 512

    for i in range(1, 4):
        dt = st.session_state['df_orig'][f'p{i} elapsed'].diff().fillna(0)
        st.session_state['df_orig'][f'p{i} distance'] = (st.session_state['df_orig'][f'p{i} speed'] * dt).cumsum().fillna(0)
        dv = st.session_state['df_orig'][f'p{i} COM speed'].diff()
        st.session_state['df_orig'][f'p{i} time'] = dt.cumsum().fillna(0)
        st.session_state['df_orig'][f'p{i} cadence'] = (st.session_state['df_orig'][f'p{i} speed']*60)/(wheel_circ*gear_ratio[i-1])
        st.session_state['df_orig'][f'p{i} prop force'] = 2 * efficiency * math.pi * st.session_state['df_orig'][f'p{i} torque']  / (wheel_circ * gear_ratio[i - 1])
        st.session_state['df_orig'][f'p{i} power'] = ((st.session_state['df_orig'][f'p{i} torque']*st.session_state['df_orig'][f'p{i} speed'])/(wheel_radius*gear_ratio[i-1]))
        st.session_state['df_orig'][f'p{i} accel'] = (dv / dt)
        st.session_state['df_orig'][f'p{i} segment'] = st.session_state['df_orig'][f'p{i} distance'] % 125
        st.session_state['df_orig'][[f'p{i} bank', f'p{i} r_wh', f'p{i} r_cm', f'p{i} lean', f'p{i} camber']] = st.session_state['df_orig'].apply(
            lambda row: get_bank_r_wh_r_cm_lean(
                row[f'p{i} segment'], COM[i - 1], row[f'p{i} COM speed'], row[f'p{i} speed']
            ), axis=1, result_type='expand'
        )
        st.session_state['df_orig'][f'p{i} centripetal'] = (mass[i-1] * (st.session_state['df_orig'][f'p{i} COM speed']**2))/st.session_state['df_orig'][f'p{i} r_cm']
        st.session_state['df_orig'][f'p{i} reaction'] = np.sqrt((weight[i-1]**2) + (st.session_state['df_orig'][f'p{i} centripetal']**2))
        st.session_state['df_orig'][f'p{i} normal'] = st.session_state['df_orig'][f'p{i} reaction']
        st.session_state['df_orig'][f'p{i} rr'] = st.session_state['df_orig'][f'p{i} normal']*mu_rr
        st.session_state['df_orig'][f'p{i} aero'] = 0.5*rho*st.session_state['df_orig'][f'p{i} CdA']*(st.session_state['df_orig'][f'p{i} COM speed']**2)
        st.session_state['df_orig'][f'p{i} potential'] = st.session_state['df_orig'][f'p{i} accel']*mass[i-1] - st.session_state['df_orig'][f'p{i} prop force'] + st.session_state['df_orig'][f'p{i} rr'] + st.session_state['df_orig'][f'p{i} aero']

    # --- Find time points for each rider at every 62.5m (quarter lap) ---
    marker_distance = 62.5
    num_markers = int(np.nanmax([st.session_state['df_orig'][f'p{i} distance'].max() for i in range(1, 4)]) // marker_distance) + 1
    marker_distances = np.arange(marker_distance, marker_distance * (num_markers + 1), marker_distance)

    quarter_lap_times = {}
    for i in range(1, 4):
        distance = st.session_state['df_orig'][f'p{i} distance']
        time = st.session_state['df_orig'][f'p{i} time']
        times_at_markers = []
        for md in marker_distances:
            # Find the first index where distance >= marker
            idxs = np.where(distance >= md)[0]
            if len(idxs) > 0:
                times_at_markers.append(time.iloc[idxs[0]])
            else:
                times_at_markers.append(np.nan)
        quarter_lap_times[f'p{i}'] = times_at_markers



    # --- Define number of segments for each rider ---
    num_segments_dict = {1: 4, 2: 8, 3: 12}

    # --- Plot COM speed for p1, p2, p3 with vertical lines, split annotations, and segment best fit lines ---
    for i, color in zip(range(1, 4), ['blue', 'green', 'red']):
        num_segments = num_segments_dict[i]
        segment_markers = np.linspace(0, marker_distance * num_segments, num_segments + 1)  # <-- Add this line
        fig, ax = plt.subplots(figsize=(20, 4))
        time = st.session_state['df_orig'][f'p{i} time']
        speed = st.session_state['df_orig'][f'p{i} speed']
        distance = st.session_state['df_orig'][f'p{i} distance']
        splits = quarter_lap_times[f'p{i}']

        ax.plot(time, speed, color=color, label='Speed')

        # Store slopes and residuals for each segment
        segment_slopes = []
        segment_residuals = []
        segment_times = []
        segment_indices = []

        # Store original slopes and intercepts for correct adjustment
        segment_orig_slopes = []
        segment_orig_intercepts = []

        # Plot segment best fit lines and store residuals
        for seg_idx in range(num_segments):
            start_dist = segment_markers[seg_idx]
            end_dist = segment_markers[seg_idx + 1]
            seg_mask = (distance >= start_dist) & (distance < end_dist if seg_idx < num_segments - 1 else distance <= end_dist)
            seg_time = time[seg_mask]
            seg_speed = speed[seg_mask]
            seg_idx_arr = np.where(seg_mask)[0]
            # Remove NaNs
            valid = (~np.isnan(seg_time)) & (~np.isnan(seg_speed))
            seg_time = seg_time[valid]
            seg_speed = seg_speed[valid]
            seg_idx_arr = seg_idx_arr[valid]
            # Only fit if at least 2 unique time points
            if len(seg_time) < 2 or np.unique(seg_time).size < 2:
                segment_slopes.append(np.nan)
                segment_residuals.append(np.full_like(seg_time, np.nan))
                segment_times.append(seg_time)
                segment_indices.append(seg_idx_arr)
                segment_orig_slopes.append(np.nan)
                segment_orig_intercepts.append(np.nan)
                continue
            coef = np.polyfit(seg_time, seg_speed, 1)
            fit_line = np.polyval(coef, seg_time)
            ax.plot(seg_time, fit_line, linestyle='--', linewidth=2, label=f'Segment {seg_idx+1} Fit', alpha=0.7)
            segment_slopes.append(coef[0])
            segment_residuals.append(seg_speed - fit_line)
            segment_times.append(seg_time)
            segment_indices.append(seg_idx_arr)
            segment_orig_slopes.append(coef[0])
            segment_orig_intercepts.append(coef[1])

        prev_time = None
        for idx, t in enumerate(splits[:num_segments]):
            if not np.isnan(t):
                ax.axvline(t, color='orange', linestyle='--', alpha=0.7)
                # Calculate split time
                if prev_time is None:
                    split = t
                else:
                    split = t - prev_time
                prev_time = t
                # Annotate above the line
                ax.annotate(
                    f"Q{idx+1}\n{t:.2f}s\nΔ{split:.2f}s",
                    xy=(t, ax.get_ylim()[1]),
                    xytext=(0, -160),
                    textcoords='offset points',
                    ha='center',
                    va='top',
                    fontsize=16,
                    color='black',
                    bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="orange", lw=0.5, alpha=0.7)
                )

        ax.set_title(f'p{i} Speed over Time')
        ax.set_xlabel('Time (s)')
        ax.set_ylabel('Speed (m/s)')
        
        st.pyplot(fig)

        # Display slopes and shifts as number inputs below the plot
        st.markdown(f"**Segment slopes and shifts for p{i}:**")
        slope_inputs = []
        shift_inputs = []
        cols = st.columns(num_segments)
        for idx, col in enumerate(cols):
            slope_value = 0.0  # Default adjustment is 0.0
            shift_value = 0.0  # Default shift is 0.0
            slope_input = col.number_input(
                f"Segment {idx+1} Slope", 
                value=slope_value, 
                key=f"p{i}_slope_{idx+1}", 
                format="%.6f"
            )
            shift_input = col.number_input(
                f"Segment {idx+1} Shift", 
                value=shift_value, 
                key=f"p{i}_shift_{idx+1}", 
                format="%.6f"
            )
            slope_inputs.append(slope_input)
            shift_inputs.append(shift_input)

        # --- Plot adjusted speed using user slope and shift adjustments and original residuals ---
        fig2, ax2 = plt.subplots(figsize=(20, 4))
        adjusted_speed = np.full_like(speed, np.nan)

        # Build adjusted speed for each segment
        for seg_idx in range(num_segments):
            seg_time = segment_times[seg_idx]
            seg_idx_arr = segment_indices[seg_idx]
            orig_slope = segment_orig_slopes[seg_idx]
            orig_intercept = segment_orig_intercepts[seg_idx]
            if len(seg_time) < 2 or np.isnan(orig_slope) or np.isnan(orig_intercept):
                continue
            t0 = seg_time.iloc[0]
            # The adjustment pivots about t0 and adds shift
            slope_adj = slope_inputs[seg_idx]
            shift_adj = shift_inputs[seg_idx]
            fit_line = orig_slope * seg_time + orig_intercept + slope_adj * (seg_time - t0)
            # Add original residuals and shift
            residuals = segment_residuals[seg_idx]
            adjusted_segment_speed = fit_line + residuals + shift_adj
            adjusted_speed[seg_idx_arr] = adjusted_segment_speed
            # All best fit lines in green
            ax2.plot(seg_time, fit_line + shift_adj, linestyle='--', linewidth=2, color='green', label=f'Segment {seg_idx+1} Adjusted Fit' if seg_idx == 0 else None, alpha=0.7)

        # Rider color for original and adjusted speed
        ax2.plot(time, speed, color=color, alpha=0.5, label='Original Speed')
        ax2.plot(time, adjusted_speed, color=color, label='Adjusted Speed')
        st.session_state['df_orig'][f'p{i} speed adjusted'] = adjusted_speed
        # --- Recalculate cumulative times and splits based on adjusted speed ---
        # We'll use the original distance array, and recalculate time by integrating 1/speed over distance
        adjusted_cum_times = []
        adjusted_split_times = []
        segment_end_indices = []
        for seg_idx in range(num_segments):
            # Find the index in distance where the segment ends
            end_dist = segment_markers[seg_idx + 1]
            idxs = np.where(distance >= end_dist)[0]
            if len(idxs) == 0:
                segment_end_indices.append(None)
            else:
                segment_end_indices.append(idxs[0])

        # Calculate cumulative time at each segment end using trapezoidal integration
        last_idx = 0
        last_cum_time = 0.0
        for seg_idx, end_idx in enumerate(segment_end_indices):
            if end_idx is None or end_idx <= last_idx:
                adjusted_cum_times.append(np.nan)
                adjusted_split_times.append(np.nan)
                continue
            # Integrate dt = dx / v over this segment
            seg_dist = distance[last_idx:end_idx+1]
            seg_speed = adjusted_speed[last_idx:end_idx+1]
            # Avoid division by zero or nan
            valid = (~np.isnan(seg_dist)) & (~np.isnan(seg_speed)) & (seg_speed > 0)
            seg_dist = seg_dist[valid]
            seg_speed = seg_speed[valid]
            if len(seg_dist) < 2:
                adjusted_cum_times.append(np.nan)
                adjusted_split_times.append(np.nan)
                last_idx = end_idx
                continue
            dx = np.diff(seg_dist)
            v = (seg_speed[:-1] + seg_speed[1:]) / 2
            dt = dx / v
            seg_time = np.sum(dt)
            last_cum_time += seg_time
            adjusted_cum_times.append(last_cum_time)
            adjusted_split_times.append(seg_time)
            last_idx = end_idx

        # Add vertical lines and annotations for each segment end (except the first marker)
        for seg_idx, end_idx in enumerate(segment_end_indices):
            if end_idx is None or np.isnan(adjusted_cum_times[seg_idx]):
                continue
            seg_time = time[end_idx]
            cum_time = adjusted_cum_times[seg_idx]
            split_time = adjusted_split_times[seg_idx]
            ax2.axvline(seg_time, color='orange', linestyle='--', alpha=0.7)
            ax2.annotate(
                f"Q{seg_idx+1}\n{cum_time:.2f}s\nΔ{split_time:.2f}s",
                xy=(seg_time, ax2.get_ylim()[1]),
                xytext=(0, -160),
                textcoords='offset points',
                ha='center',
                va='top',
                fontsize=16,
                color='black',
                bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="orange", lw=0.5, alpha=0.7)
            )

        ax2.set_title(f'p{i} Adjusted Speed with User Slope/Shift Adjustments and Original Residuals')
        ax2.set_xlabel('Time (s)')
        ax2.set_ylabel('Speed (m/s)')
        ax2.legend()
        st.pyplot(fig2)

    # --- Model calculations using adjusted speed ---
    # --- Model parameter inputs ---
    st.markdown("## Model Parameters")
    gear_new = []
    COM_new = []
    mass_new = []
    col_gear, col_COM, col_mass = st.columns(3)
    for i in range(1, 4):
        gear_val = col_gear.number_input(
            f"Gear (Rider p{i})", value=float(gear[i-1]), key=f"gear_{i}", format="%.2f"
        )
        COM_val = col_COM.number_input(
            f"COM (Rider p{i})", value=float(COM[i-1]), key=f"COM_{i}", format="%.2f"
        )
        mass_val = col_mass.number_input(
            f"Mass (Rider p{i})", value=float(mass[i-1]), key=f"mass_{i}", format="%.2f"
        )
        gear_new.append(gear_val)
        COM_new.append(COM_val)
        mass_new.append(mass_val)
    c1,c2,c3 = st.columns(3)
    with c1:
        CdA_scale = st.number_input("CdA Scale", value=1.0, key="CdA_scale", format="%.3f",step=0.001)
    with c2:
        rho = st.number_input("Air Density (rho)", value=rho, key="rho", format="%.3f",step=0.001)
    with c3:
        model_mu_rr = st.number_input("Rolling Resistance Coefficient (mu_rr)", value=mu_rr, key="model_mu_rr", format="%.4f",step=0.0001)

    # Update model variables
    model_gear = gear_new
    model_gear_ratio = [x / 27 for x in model_gear]
    model_COM = COM_new
    model_mass = mass_new
    model_weight = [x * 9.81 for x in model_mass]
    model_rho = rho

    for i in range(1, 4):
        df = st.session_state['df_orig']
        df[f'p{i} model CdA'] = np.where(
        df[f'p{i} distance'] > 150,
        df[f'p{i} CdA'] * CdA_scale,
        df[f'p{i} CdA']
        )
        df[f'p{i} model speed'] = df[f'p{i} speed adjusted']

        df[f'p{i} model cadence'] = (df[f'p{i} model speed'] * 60) / (wheel_circ * model_gear_ratio[i-1])
        df[f'p{i} model COM speed'] = df[f'p{i} COM speed'] * (df[f'p{i} model speed'] / df[f'p{i} model speed'])
        dd_model = df[f'p{i} distance'].diff().fillna(0)

        # Recalculate time using adjusted speed
        df[f'p{i} model time'] = (dd_model / df[f'p{i} model speed']).cumsum()
        dv_model = df[f'p{i} model COM speed'].diff()
        dt_model = df[f'p{i} model time'].diff()
        df[f'p{i} model accel'] = dv_model / dt_model
        # df[f'p{i} model accel smoothed'] = df[f'p{i} model accel'].rolling(window=fixed_window_size, min_periods=1, center=True).mean()

        # Apply the function row-wise for banking etc.
        df[[f'p{i} model bank', f'p{i} model r_wh', f'p{i} model r_cm', f'p{i} model lean', f'p{i} model camber']] = df.apply(
            lambda row: get_bank_r_wh_r_cm_lean(
                row[f'p{i} segment'], model_COM[i - 1], row[f'p{i} model COM speed'], row[f'p{i} model speed']
            ), axis=1, result_type='expand'
        )
        df[f'p{i} model centripetal'] = (model_mass[i-1] * (df[f'p{i} model COM speed']**2)) / df[f'p{i} model r_cm']
        df[f'p{i} model reaction'] = np.sqrt((model_weight[i-1]**2) + (df[f'p{i} model centripetal']**2))
        df[f'p{i} model normal'] = df[f'p{i} model reaction']
        df[f'p{i} model rr'] = df[f'p{i} model normal'] * model_mu_rr
        df[f'p{i} model aero'] = 0.5 * model_rho * df[f'p{i} model CdA'] * (df[f'p{i} model COM speed']**2)

        df[f'p{i} model torque'] = ((df[f'p{i} model accel'] * model_mass[i-1] + df[f'p{i} model rr'] + df[f'p{i} model aero'] - df[f'p{i} potential']) * (wheel_circ * model_gear_ratio[i-1]) / (2 * efficiency * math.pi)).fillna(0)
        df[f'p{i} model prop force'] = (2 * efficiency * math.pi * df[f'p{i} model torque'] * 27 / (wheel_circ * model_gear[i - 1])).fillna(0)

        df[f'p{i} model power'] = ((df[f'p{i} model torque'] * df[f'p{i} model speed']) / (wheel_radius * model_gear_ratio[i-1])).fillna(0)
        # df[f'p{i} model power smoothed'] = df[f'p{i} model power'].rolling(window=fixed_window_size, min_periods=1, center=True).mean()
    st.write(df)
    # --- Add tables comparing average power for each segment ---
    st.markdown("## Average Power per Segment Comparison")
    final_distances = {1: 250, 2: 500, 3: 750}  # Use these for last segment end index

    for i in range(1, 4):
        df = st.session_state['df_orig']
        num_segments = num_segments_dict[i]
        segment_markers = np.linspace(0, marker_distance * num_segments, num_segments + 1)

        # Prepare lists for each metric
        avg_power_original = []
        avg_power_adjusted = []
        avg_torque_original = []
        avg_torque_adjusted = []
        avg_CdA_original = []
        avg_CdA_adjusted = []
        avg_speed_original = []
        avg_speed_adjusted = []

        # Find start/end indices for each segment
        start_indices = []
        for seg_idx in range(num_segments):
            start_dist = segment_markers[seg_idx]
            idxs = np.where(df[f'p{i} distance'] >= start_dist)[0]
            start_indices.append(idxs[0] if len(idxs) > 0 else None)

        end_indices = []
        for seg_idx in range(num_segments):
            if seg_idx < num_segments - 1:
                next_start = start_indices[seg_idx + 1]
                end_indices.append(next_start - 1 if next_start is not None else None)
            else:
                last_idxs = np.where(df[f'p{i} distance'] >= final_distances[i])[0]
                end_indices.append(last_idxs[0] if len(last_idxs) > 0 else len(df) - 1)

        for seg_idx in range(num_segments):
            start_idx = start_indices[seg_idx]
            end_idx = end_indices[seg_idx]
            if start_idx is None or end_idx is None or end_idx < start_idx:
                seg_power_orig = seg_power_adj = seg_torque_orig = seg_torque_adj = seg_CdA_orig = seg_CdA_adj = seg_speed_orig = seg_speed_adj = np.array([np.nan])
            else:
                seg_power_orig = df[f'p{i} power'].iloc[start_idx:end_idx+1]
                seg_power_adj = df[f'p{i} model power'].iloc[start_idx:end_idx+1]
                seg_torque_orig = df[f'p{i} torque'].iloc[start_idx:end_idx+1]
                seg_torque_adj = df[f'p{i} model torque'].iloc[start_idx:end_idx+1]
                seg_CdA_orig = df[f'p{i} CdA'].iloc[start_idx:end_idx+1]
                seg_CdA_adj = df[f'p{i} model CdA'].iloc[start_idx:end_idx+1]
                seg_speed_orig = df[f'p{i} speed'].iloc[start_idx:end_idx+1]
                seg_speed_adj = df[f'p{i} model speed'].iloc[start_idx:end_idx+1]

            avg_power_original.append(np.nanmean(seg_power_orig))
            avg_power_adjusted.append(np.nanmean(seg_power_adj))
            avg_torque_original.append(np.nanmean(seg_torque_orig))
            avg_torque_adjusted.append(np.nanmean(seg_torque_adj))
            avg_CdA_original.append(np.nanmean(seg_CdA_orig))
            avg_CdA_adjusted.append(np.nanmean(seg_CdA_adj))
            avg_speed_original.append(np.nanmean(seg_speed_orig))
            avg_speed_adjusted.append(np.nanmean(seg_speed_adj))

        # Calculate % shift for each metric
        def pct_shift_row(orig_list, adj_list):
            return [
                "NaN" if np.isnan(orig) or orig == 0 else f"{100 * (adj - orig) / orig:.1f}%"
                for orig, adj in zip(orig_list, adj_list)
            ]

        pct_power = pct_shift_row(avg_power_original, avg_power_adjusted)
        pct_torque = pct_shift_row(avg_torque_original, avg_torque_adjusted)
        pct_CdA = pct_shift_row(avg_CdA_original, avg_CdA_adjusted)
        pct_speed = pct_shift_row(avg_speed_original, avg_speed_adjusted)

        # Build table with segments as columns, rows for each metric
        table_df = pd.DataFrame({
            f"Segment {seg+1}": [
                f"{avg_power_original[seg]:.2f}" if not np.isnan(avg_power_original[seg]) else "NaN",
                f"{avg_power_adjusted[seg]:.2f}" if not np.isnan(avg_power_adjusted[seg]) else "NaN",
                pct_power[seg],
                f"{avg_torque_original[seg]:.2f}" if not np.isnan(avg_torque_original[seg]) else "NaN",
                f"{avg_torque_adjusted[seg]:.2f}" if not np.isnan(avg_torque_adjusted[seg]) else "NaN",
                pct_torque[seg],
                f"{avg_CdA_original[seg]:.4f}" if not np.isnan(avg_CdA_original[seg]) else "NaN",
                f"{avg_CdA_adjusted[seg]:.4f}" if not np.isnan(avg_CdA_adjusted[seg]) else "NaN",
                pct_CdA[seg],
                f"{avg_speed_original[seg]:.2f}" if not np.isnan(avg_speed_original[seg]) else "NaN",
                f"{avg_speed_adjusted[seg]:.2f}" if not np.isnan(avg_speed_adjusted[seg]) else "NaN",
                pct_speed[seg],
            ] for seg in range(num_segments)
        }, index=[
            "Original Power (W)", "Model Power (W)", "% Shift Power",
            "Original Torque (Nm)", "Model Torque (Nm)", "% Shift Torque",
            "Original CdA", "Model CdA", "% Shift CdA",
            "Original Speed (m/s)", "Model Speed (m/s)", "% Shift Speed"
        ])

        st.markdown(f"### Rider p{i}")
        st.dataframe(table_df, use_container_width=True)
 

    # --- Plot original and model power for each rider ---
    st.markdown("## Original vs Model Power Plots")
    for i, color in zip(range(1, 4), ['blue', 'green', 'red']):
        df = st.session_state['df_orig']
        fig, ax = plt.subplots(figsize=(20, 4))
        ax.plot(df[f'p{i} time'], df[f'p{i} power'], label='Original Power', color=color, alpha=0.5)
        ax.plot(df[f'p{i} model time'], df[f'p{i} model power'], label='Model Power', color=color, linestyle='--')
        ax.set_title(f'Rider p{i} Original vs Model Power')
        ax.set_xlabel('Time (s)')
        ax.set_ylabel('Power (W)')
        ax.legend()
        st.pyplot(fig)





