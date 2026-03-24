#!/usr/bin/env python
# coding: utf-8

import pickle, math, datetime
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import streamlit_authenticator as stauth
from statistics import mean

st.set_page_config(page_title='CNZ Performance Database', page_icon=":bike:", layout="wide")

with open("hashed_pw.pkl", "rb") as file:
    hashed_passwords = pickle.load(file)

credentials = {"usernames": {u: {"name": n, "password": p}
               for u, n, p in zip(['CNZ'], ['CNZ'], hashed_passwords)}}
authenticator = stauth.Authenticate(credentials, "CNZPD", "abcdef", cookie_expiry_days=30)
name, authentication_status, username = authenticator.login("Login", "main")

if authentication_status == False:
    st.error("Username/password is incorrect")
if authentication_status == None:
    st.warning("Please enter your username and password")
if authentication_status:
    st.header('Modelling Tool')
    update = datetime.date.today() + pd.DateOffset(hour=12)

    def intp(xval, df, xcol, ycol):
        return np.interp([xval], df[xcol], df[ycol])

    calcs = ["Female Team Sprint", "Male Individual Pursuit"]
    Calc = st.selectbox("Select Model:", calcs, key="Calc_selector")

    if Calc == "Female Team Sprint":
        order = ["Petch, Shaane, Ellesse", "Shaane, Petch, Ellesse"]
        Order = st.selectbox("Select Order:", order, key="Order_selector")

        # Default specs: [seat_RPM, seat_torque, seat_CdA, stand_RPM, stand_torque, stand_CdA, mass, sprocket, chainring, seat_height]
        PETCH   = [235, 207, 0.2050, 240, 223, 0.2563, 71.9, 15, 54, 0.96]
        SHAANE  = [233, 253, 0.2340, 227, 289, 0.2925, 91.8, 15, 62, 1.04]
        ELLESSE = [238, 202, 0.2180, 217, 270, 0.2725, 86.9, 15, 63, 1.01]

        if Order == order[0]:
            rider_names = ["Petch", "Shaane", "Ellesse"]
            rider_defaults = [PETCH, SHAANE, ELLESSE]
        else:
            rider_names = ["Shaane", "Petch", "Ellesse"]
            rider_defaults = [SHAANE, PETCH, ELLESSE]

        def rider_inputs(name, kn, d):
            st.subheader(f"{name} specs")
            c1, c2, c3, c4, c5, c6 = st.columns(6)
            v = [
                c1.number_input("Seated Max RPM:",    min_value=0.01, max_value=500.0,  value=float(d[0]), key=f"{kn}_1"),
                c2.number_input("Seated Max Torque:", min_value=0.01, max_value=500.0,  value=float(d[1]), key=f"{kn}_2"),
                c3.number_input("Seated CdA:",        min_value=0.0001, max_value=2.0,  value=float(d[2]), step=1e-4, format="%.4f", key=f"{kn}_3"),
                c4.number_input("Standing Max RPM:",  min_value=0.01, max_value=500.0,  value=float(d[3]), key=f"{kn}_4"),
                c5.number_input("Standing Max Torque:", min_value=0.01, max_value=500.0, value=float(d[4]), key=f"{kn}_5"),
                c6.number_input("Standing CdA:",      min_value=0.0,  max_value=20.0,   value=float(d[5]), step=1e-4, format="%.4f", key=f"{kn}_6"),
            ]
            c1, c2, c3, c4 = st.columns(4)
            v += [
                c1.number_input("Total Mass:",  min_value=40.0, max_value=150.0, value=float(d[6]), step=0.1, format="%.1f", key=f"{kn}_7"),
                c2.number_input("Sprocket:",    min_value=12,   max_value=22,    value=int(d[7]),   step=1,   key=f"{kn}_8"),
                c3.number_input("Chain Ring:",  min_value=40,   max_value=100,   value=int(d[8]),   step=1,   key=f"{kn}_9"),
                c4.number_input("Seat Height:", min_value=0.50, max_value=2.00,  value=float(d[9]),            key=f"{kn}_10"),
            ]
            return v

        with st.form("my_form"):
            r1 = rider_inputs(rider_names[0], "1", rider_defaults[0])
            r2 = rider_inputs(rider_names[1], "2", rider_defaults[1])
            r3 = rider_inputs(rider_names[2], "3", rider_defaults[2])

            st.subheader("Global specs")
            c1, c2, c3, c4, c5 = st.columns(5)
            air_density           = c1.number_input("Air Density:",             min_value=0.001, max_value=3.2,   value=1.168, step=1e-3, format="%.3f", key="4_1")
            dist_at_sit           = c2.number_input("Distance at sit:",         min_value=0.01,  max_value=750.0, value=150.0, step=0.1,  format="%.1f", key="4_2")
            standing_fatigue_rate = c3.number_input("Standing Fatigue Rate (%):",min_value=0.01, max_value=99.99, value=1.0,   step=1e-2, format="%.2f", key="4_3")
            seated_fatigue_rate   = c4.number_input("Seated Fatigue Rate (%):", min_value=0.01,  max_value=99.99, value=1.0,   step=1e-2, format="%.2f", key="4_4")
            fatigue_onset         = c5.number_input("Onset of Fatigue (s):",    min_value=0.1,   max_value=2.0,   value=1.0,   step=0.1,  format="%.1f", key="4_5")

            c1, c2, c3, c4, c5 = st.columns(5)
            track_circumference = c1.selectbox("Track Circumference:", [250, 333, 500], key="Track_circumference")
            straight_bank_angle = c2.number_input("Straight Bank Angle:",                   min_value=0.0, max_value=90.0, value=13.00)
            bend_bank_angle     = c3.number_input("Bend Bank Angle:",                       min_value=0.0, max_value=90.0, value=46.13)
            pl_to_trans         = c4.number_input("Distance from Pursuit Line to Transition:", min_value=0.0, max_value=90.0, value=31.25)
            transition_length   = c5.number_input("Transition length:",                     min_value=0.0, max_value=90.0, value=10.00)
            submitted = st.form_submit_button("Update Specs")

        (seat_max_RPM_1, seat_max_torque_1, seat_CdA_1, stand_max_RPM_1, stand_max_torque_1, stand_CdA_1, total_mass_1, sprocket_1, chainring_1, seat_height_1) = r1
        (seat_max_RPM_2, seat_max_torque_2, seat_CdA_2, stand_max_RPM_2, stand_max_torque_2, stand_CdA_2, total_mass_2, sprocket_2, chainring_2, seat_height_2) = r2
        (seat_max_RPM_3, seat_max_torque_3, seat_CdA_3, stand_max_RPM_3, stand_max_torque_3, stand_CdA_3, total_mass_3, sprocket_3, chainring_3, seat_height_3) = r3

        # --- Constants ---
        wheel_circ, bike_length = 2.096, 1.7122
        ks, mu_rr, lean_smoothing, increment, efficiency = 0.0072, 0.0016, 1, 0.1, 0.97
        rad_of_curve = (250 - 4 * pl_to_trans) / (2 * math.pi)
        deg_to_rad, rad_to_deg = math.pi / 180, 180 / math.pi

        # --- Athlete class ---
        class Athlete:
            def __init__(self, seat_max_RPM, seat_max_torque, stand_max_RPM, stand_max_torque,
                         stand_CdA, seat_CdA, total_mass, gear, seat_height, max_power,
                         stand_TC_slope, seat_TC_slope):
                self.seat_max_RPM = seat_max_RPM; self.seat_max_torque = seat_max_torque
                self.stand_max_RPM = stand_max_RPM; self.stand_max_torque = stand_max_torque
                self.stand_CdA = stand_CdA; self.seat_CdA = seat_CdA
                self.total_mass = total_mass; self.gear = gear
                self.seat_height = seat_height; self.max_power = max_power
                self.stand_TC_slope = stand_TC_slope; self.seat_TC_slope = seat_TC_slope

            def initialize_state(self, initial_speed, bank_angle, rad_of_curve, air_density, mu_rr, ks, efficiency, bike_length):
                self.time = 0; self.COM_speed = initial_speed; self.COM_dist = 0
                self.CdA = self.stand_CdA; self.cadence = 0; self.torque = self.stand_max_torque
                self.power_input = self.cadence * self.torque * (math.pi / 30)
                self.power_usable = self.power_input * efficiency; self.acc_fatigue = 0
                self.bank = bank_angle; self.lean = 0
                self.camber = abs(self.bank - self.lean)
                self.r_wh = 2 * rad_of_curve; self.r_cm = 2 * rad_of_curve
                self.prop_force = 2 * math.pi * self.torque / (2.096 * (self.gear / 27))
                self.aero_drag = 0.5 * air_density * self.CdA * self.COM_speed ** 2
                self.weight_force = 9.81 * self.total_mass; self.centripetal_force = 0
                self.reaction_force = math.sqrt(self.weight_force ** 2 + self.centripetal_force ** 2)
                self.normal_force = self.reaction_force * math.cos(math.radians(self.camber))
                self.rr = self.normal_force * mu_rr * (1 + (self.camber * ks))
                self.wheel_speed = 0; self.wheel_dist = 0
                self.segment = self.wheel_dist % 125
                self.accel = (self.prop_force - (self.rr + self.aero_drag)) / self.total_mass
                self.air_speed = 0; self.gap = -bike_length

        def make_athlete(rpm_s, tor_s, rpm_st, tor_st, cda_st, cda_s, mass, chain, spr, sh):
            return Athlete(rpm_s, tor_s, rpm_st, tor_st, cda_st, cda_s, mass,
                           27 * chain / spr, sh, rpm_s * tor_s * math.pi / 120,
                           -tor_st / rpm_st, -tor_s / rpm_s)

        p1 = make_athlete(seat_max_RPM_1, seat_max_torque_1, stand_max_RPM_1, stand_max_torque_1, stand_CdA_1, seat_CdA_1, total_mass_1, chainring_1, sprocket_1, seat_height_1)
        p2 = make_athlete(seat_max_RPM_2, seat_max_torque_2, stand_max_RPM_2, stand_max_torque_2, stand_CdA_2, seat_CdA_2, total_mass_2, chainring_2, sprocket_2, seat_height_2)
        p3 = make_athlete(seat_max_RPM_3, seat_max_torque_3, stand_max_RPM_3, stand_max_torque_3, stand_CdA_3, seat_CdA_3, total_mass_3, chainring_3, sprocket_3, seat_height_3)

        for rider, spd in ((p1, 1.8), (p2, 1.6), (p3, 1.6)):
            rider.initialize_state(spd, straight_bank_angle, rad_of_curve, air_density, mu_rr, ks, efficiency, bike_length)

        # --- Track geometry ---
        def get_bank_lean_camber(segment, lean_initial, v_com, seat_height):
            bend_length = 125 - 2 * (pl_to_trans + transition_length)
            r_wh = rad_of_curve
            if (segment < pl_to_trans) or (segment > 125 - pl_to_trans):
                bank = straight_bank_angle
                r_wh = r_cm = 100000
            elif segment <= pl_to_trans + transition_length:
                pct = (segment - pl_to_trans) / transition_length
                bank = straight_bank_angle + pct * (bend_bank_angle - straight_bank_angle)
                r_wh = 2 * rad_of_curve - pct * rad_of_curve
            elif segment <= pl_to_trans + transition_length + bend_length:
                bank = bend_bank_angle
            else:
                pct = (segment - (pl_to_trans + transition_length + bend_length)) / transition_length
                bank = bend_bank_angle + pct * (straight_bank_angle - bend_bank_angle)
                r_wh = rad_of_curve + pct * rad_of_curve
            lean = rad_to_deg * math.atan(v_com ** 2 / (9.81 * (r_wh - seat_height * math.sin(deg_to_rad * lean_initial))))
            while lean - lean_initial > 0.1:
                lean_initial = lean
                lean = rad_to_deg * math.atan(v_com ** 2 / (9.81 * (r_wh - seat_height * math.sin(deg_to_rad * lean))))
            r_cm = r_wh - seat_height * math.sin(deg_to_rad * lean) if r_wh < 2 * rad_of_curve else r_wh
            return bank, r_wh, r_cm, lean, bank - lean

        # --- Simulation helpers ---
        _BASE_FIELDS = ('COM_speed', 'COM_dist', 'bank', 'r_wh', 'r_cm', 'lean', 'camber',
                        'wheel_speed', 'wheel_dist', 'cadence', 'torque', 'power_input',
                        'power_usable', 'prop_force', 'aero_drag', 'weight_force', 'segment',
                        'centripetal_force', 'reaction_force', 'normal_force', 'rr', 'accel')

        def new_data(rider, with_demand=False):
            d = {'time': [rider.time]}
            d.update({k: [getattr(rider, k)] for k in _BASE_FIELDS})
            d['gap'] = [getattr(rider, 'gap', 0)]
            d['air_speed'] = [getattr(rider, 'air_speed', 0)]
            if with_demand:
                d.update({k: [getattr(rider, k, 1 if k == 'dem_sup' else 0)]
                          for k in ('accel_demand', 'rr_demand', 'aero_demand', 'power_demand', 'dem_sup')})
            return d

        def append_state(rider, d, with_demand=False):
            d['time'].append(rider.time)
            for k in _BASE_FIELDS:
                d[k].append(getattr(rider, k))
            d['gap'].append(getattr(rider, 'gap', 0))
            d['air_speed'].append(getattr(rider, 'air_speed', 0))
            if with_demand:
                for k in ('accel_demand', 'rr_demand', 'aero_demand', 'power_demand', 'dem_sup'):
                    d[k].append(getattr(rider, k))

        def update_lean(rider, leans):
            rider.bank, rider.r_wh, rider.r_cm, rider.lean, rider.camber = \
                get_bank_lean_camber(rider.segment, rider.lean, rider.COM_speed, rider.seat_height)
            leans.append(rider.lean)
            if len(leans) > lean_smoothing:
                leans[:] = leans[1:]
            rider.lean = mean(leans)

        def update_kinematics(rider):
            rider.wheel_speed = rider.COM_speed * (rider.r_wh / rider.r_cm)
            rider.wheel_dist += rider.wheel_speed * increment
            rider.cadence = 60 * rider.wheel_speed / ((rider.gear / 27) * wheel_circ)

        def update_forces(rider, cda):
            rider.power_input = rider.cadence * rider.torque * (math.pi / 30)
            rider.power_usable = rider.power_input * efficiency
            rider.prop_force = 2 * math.pi * efficiency * rider.torque / (2.096 * (rider.gear / 27))
            rider.aero_drag = 0.5 * air_density * cda * rider.COM_speed ** 2
            rider.weight_force = 9.81 * rider.total_mass
            rider.segment = rider.wheel_dist % 125
            rider.centripetal_force = (
                0 if (rider.segment < pl_to_trans or rider.segment > 125 - pl_to_trans)
                else (rider.total_mass * rider.COM_speed ** 2) / rider.r_cm
            )
            rider.reaction_force = math.sqrt(rider.weight_force ** 2 + rider.centripetal_force ** 2)
            rider.normal_force = rider.reaction_force * math.cos(deg_to_rad * rider.camber)
            rider.rr = rider.normal_force * mu_rr * (1 + abs(rider.camber) * ks)
            rider.accel = (rider.prop_force - (rider.rr + rider.aero_drag)) / rider.total_mass

        def make_df(d, extra_cols=()):
            cols = ['time'] + list(_BASE_FIELDS) + ['gap', 'air_speed'] + list(extra_cols)
            return pd.DataFrame({c: d[c] for c in cols}).rename(columns={'time': 'Time'})

        # --- P1 simulation ---
        p1d = new_data(p1)
        p1_leans = []
        for is_standing, stop_dist in [(True, dist_at_sit), (False, 250)]:
            if not is_standing:
                p1.CdA = p1.seat_CdA
            while p1.wheel_dist < stop_dist:
                p1.time += increment
                p1.COM_speed += increment * p1.accel
                p1.COM_dist += p1.COM_speed * increment
                update_lean(p1, p1_leans)
                update_kinematics(p1)
                if is_standing:
                    if p1.time < fatigue_onset:
                        p1.torque = p1.stand_max_torque + p1.stand_TC_slope * p1.cadence
                    else:
                        p1.acc_fatigue += increment * standing_fatigue_rate / 100
                        p1.torque = p1.stand_max_torque * (1 - p1.acc_fatigue) + p1.stand_TC_slope * p1.cadence
                    update_forces(p1, p1.stand_CdA)
                else:
                    p1.acc_fatigue += increment * seated_fatigue_rate / 100
                    p1.torque = p1.seat_max_torque * (1 - p1.acc_fatigue) + p1.seat_TC_slope * p1.cadence
                    update_forces(p1, p1.seat_CdA)
                append_state(p1, p1d)
        df_p1 = make_df(p1d)

        # --- P2 simulation ---
        p2d = new_data(p2)
        p2_leans = []
        count = 0
        for is_standing, stop_dist in [(True, dist_at_sit), (False, 500)]:
            if not is_standing:
                p2.CdA = p2.seat_CdA
            while p2.wheel_dist < stop_dist:
                p2.time += increment
                p2.COM_speed += increment * p2.accel
                p2.COM_dist += p2.COM_speed * increment
                update_lean(p2, p2_leans)
                update_kinematics(p2)
                p2.gap = df_p1["wheel_dist"][count] - p2.wheel_dist - bike_length if count < len(df_p1) else 0
                p2.air_speed = p2.COM_speed
                cda = p2.stand_CdA if is_standing else p2.seat_CdA
                if is_standing:
                    if p2.time < fatigue_onset:
                        p2.torque = p2.stand_max_torque + p2.stand_TC_slope * p2.cadence
                    else:
                        p2.acc_fatigue += increment * standing_fatigue_rate / 100
                        p2.torque = p2.stand_max_torque * (1 - p2.acc_fatigue) + p2.stand_TC_slope * p2.cadence
                else:
                    p2.acc_fatigue += increment * seated_fatigue_rate / 100
                    p2.torque = p2.seat_max_torque * (1 - p2.acc_fatigue) + p2.seat_TC_slope * p2.cadence
                update_forces(p2, cda)
                if p2.gap > 0.2:
                    p2.aero_drag *= (100 - (-8.1136 * p2.gap + 50.051)) / 100
                    p2.accel = (p2.prop_force - (p2.rr + p2.aero_drag)) / p2.total_mass
                count += 1
                append_state(p2, p2d)
        df_p2 = make_df(p2d)

        # --- P3 simulation ---
        p3.dem_sup = 1; p3.accel_demand = 0; p3.rr_demand = 0; p3.aero_demand = 0; p3.power_demand = 0
        p3d = new_data(p3, with_demand=True)
        p3_leans = []
        count = 1
        for is_standing, stop_dist in [(True, dist_at_sit), (False, 750)]:
            if not is_standing:
                p3.CdA = p3.seat_CdA
            while p3.wheel_dist < stop_dist:
                if count < len(df_p2):
                    p3.accel_demand = p3.total_mass * df_p2["accel"][count] * df_p2["wheel_speed"][count]
                    p3.rr_demand = p3.rr * df_p2["wheel_speed"][count]
                    p3.aero_demand = 0.5 * air_density * p3.CdA * p3.COM_speed * p3.air_speed ** 2
                    p3.power_demand = p3.accel_demand + p3.rr_demand + p3.aero_demand
                else:
                    p3.accel_demand = p3.rr_demand = p3.aero_demand = p3.power_demand = 0
                p3.time += increment
                p3.COM_speed += increment * p3.accel
                p3.COM_dist += p3.COM_speed * increment
                update_lean(p3, p3_leans)
                update_kinematics(p3)
                p3.gap = df_p2["wheel_dist"][count] - p3.wheel_dist - bike_length if count < len(df_p2) else 0
                p3.air_speed = p3.COM_speed
                cda = p3.stand_CdA if is_standing else p3.seat_CdA
                if is_standing:
                    if p3.time < fatigue_onset:
                        p3.torque = p3.stand_max_torque + p3.stand_TC_slope * p3.cadence
                    else:
                        p3.acc_fatigue += increment * p3.dem_sup * standing_fatigue_rate / 100
                        p3.torque = p3.stand_max_torque * (1 - p3.acc_fatigue) + p3.stand_TC_slope * p3.cadence
                else:
                    p3.acc_fatigue += increment * p3.dem_sup * seated_fatigue_rate / 100
                    p3.torque = p3.seat_max_torque * (1 - p3.acc_fatigue) + p3.seat_TC_slope * p3.cadence
                update_forces(p3, cda)
                p3.dem_sup = p3.power_demand / p3.power_usable if p3.power_usable > p3.power_demand else 1
                if p3.gap > 0.2:
                    p3.aero_drag *= (100 - (-8.1136 * p3.gap + 50.051)) / 100
                    p3.accel = (p3.prop_force - (p3.rr + p3.aero_drag)) / p3.total_mass
                count += 1
                append_state(p3, p3d, with_demand=True)
        df_p3 = make_df(p3d, extra_cols=('accel_demand', 'rr_demand', 'aero_demand', 'power_demand', 'dem_sup'))

        fig_dem_v_supp = px.line(df_p3, x="Time", y=[df_p3["dem_sup"], df_p3["COM_speed"], df_p3["gap"]])
        st.plotly_chart(fig_dem_v_supp, use_container_width=True)

        # --- Summary ---
        st.header("Summary")
        dists_p1 = [62.5, 125, 187.5, 250]
        dists_p2 = dists_p1 + [312.5, 375, 437.5, 500]
        dists_p3 = dists_p2 + [562.5, 625, 687.5, 750]

        def qt(d, df_px):
            return round(intp(d, df_px, 'wheel_dist', 'Time')[0], 3)

        p1_qt = {d: qt(d, df_p1) for d in dists_p1}
        p2_qt = {d: qt(d, df_p2) for d in dists_p2}
        p3_qt = {d: qt(d, df_p3) for d in dists_p3}

        df_time = pd.DataFrame([1, 2, 3], columns=["Time"])
        for d in dists_p1:
            df_time[str(d)] = [p1_qt[d], p2_qt[d], p3_qt[d]]
        for d in [312.5, 375, 437.5, 500]:
            df_time[str(d)] = [0, p2_qt[d], p3_qt[d]]
        for d in [562.5, 625, 687.5, 750]:
            df_time[str(d)] = [0, 0, p3_qt[d]]
        df_time

        df_gap = pd.DataFrame([2, 3], columns=["Time_gap"])
        for d in dists_p1:
            df_gap[str(d)] = [p2_qt[d] - p1_qt[d], p3_qt[d] - p2_qt[d]]
        for d in [312.5, 375, 437.5, 500]:
            df_gap[str(d)] = [0, p3_qt[d] - p2_qt[d]]
        df_gap

        df_dist_gap = pd.DataFrame([2, 3], columns=["Dist_gap"])
        for d in dists_p1:
            df_dist_gap[str(d)] = [round(intp(p1_qt[d], df_p2, 'Time', 'gap')[0], 2),
                                   round(intp(p2_qt[d], df_p3, 'Time', 'gap')[0], 2)]
        for d in [312.5, 375, 437.5, 500]:
            df_dist_gap[str(d)] = [0, round(intp(p2_qt[d], df_p3, 'Time', 'gap')[0], 2)]
        df_dist_gap

        def make_summary_df(field, label):
            df_s = pd.DataFrame([1, 2, 3], columns=[label])
            for d in dists_p1:
                df_s[str(d)] = [round(intp(p1_qt[d], df_p1, 'Time', field)[0], 2),
                                round(intp(p2_qt[d], df_p2, 'Time', field)[0], 2),
                                round(intp(p3_qt[d], df_p3, 'Time', field)[0], 2)]
            for d in [312.5, 375, 437.5, 500]:
                df_s[str(d)] = [0,
                                round(intp(p2_qt[d], df_p2, 'Time', field)[0], 2),
                                round(intp(p3_qt[d], df_p3, 'Time', field)[0], 2)]
            for d in [562.5, 625, 687.5, 750]:
                df_s[str(d)] = [0, 0, round(intp(p3_qt[d], df_p3, 'Time', field)[0], 2)]
            return df_s

        df_cadence = make_summary_df('cadence', 'Cadence')
        df_cadence

        df_wheel_speed = make_summary_df('wheel_speed', 'wheel_speed')
        df_wheel_speed = df_wheel_speed.apply(lambda x: x * 3.6)
        df_wheel_speed["wheel_speed"] = [1, 2, 3]
        st.write("Wheel speed in km/h")
        df_wheel_speed

        # --- Per-rider output ---
        def power_speed_fig(df_px, label):
            fig = go.Figure()
            fig.add_trace(go.Line(x=df_px["Time"], y=df_px["power_usable"], name=f"{label} Power", yaxis='y'))
            fig.add_trace(go.Line(x=df_px["Time"], y=df_px["wheel_speed"], name=f"{label} Wheel speed", yaxis="y2"))
            fig.update_layout(
                xaxis=dict(domain=[0.0, 1.0]),
                yaxis=dict(title="Power (W)", titlefont=dict(color="#1f77b4"), tickfont=dict(color="#1f77b4")),
                yaxis2=dict(title="Wheel speed", overlaying="y", side="right", position=1.0),
                title_text="Power and Wheel speed"
            )
            return fig

        def time_to(dist, df_px):
            row = df_px.iloc[(df_px['wheel_dist'] - dist).abs().argsort()[:2]].reset_index(drop=True)
            return row["Time"][1] + (dist - row["wheel_dist"][1]) / row["wheel_speed"][1]

        st.header("P1 numbers")
        df_p1
        p1_250_time = df_p1["Time"][len(df_p1) - 2] + ((250 - df_p1["wheel_dist"][len(df_p1) - 2]) / df_p1["wheel_speed"][len(df_p1) - 2])
        st.write(f"Time to 250m is {round(p1_250_time, 3)}")
        st.plotly_chart(px.line(df_p1, x="Time", y="lean"), use_container_width=True)
        st.plotly_chart(power_speed_fig(df_p1, "P1"), use_container_width=True)

        st.header("p2 numbers")
        df_p2
        st.write(f"Time to 250m is {round(time_to(250, df_p2), 3)}")
        st.write(f"Time to 500m is {round(time_to(500, df_p2), 3)}")
        st.plotly_chart(power_speed_fig(df_p2, "p2"), use_container_width=True)

        st.header("p3 numbers")
        df_p3
        st.write(f"Time to 250m is {round(time_to(250, df_p3), 3)}")
        st.write(f"Time to 500m is {round(time_to(500, df_p3), 3)}")
        st.write(f"Time to 750m is {round(time_to(750, df_p3), 3)}")

        fig_all = go.Figure()
        for df_px, label in [(df_p1, "p1"), (df_p2, "p2"), (df_p3, "p3")]:
            fig_all.add_trace(go.Line(x=df_px["Time"], y=df_px["power_usable"], name=f"{label} Power", yaxis='y'))
            fig_all.add_trace(go.Line(x=df_px["Time"], y=df_px["wheel_speed"], name=f"{label} Wheel speed", yaxis="y2"))
        fig_all.update_layout(
            xaxis=dict(domain=[0.0, 1.0]),
            yaxis=dict(title="Power (W)", titlefont=dict(color="#1f77b4"), tickfont=dict(color="#1f77b4")),
            yaxis2=dict(title="Wheel speed", overlaying="y", side="right", position=1.0),
            title_text="Power and Wheel speed"
        )
        st.plotly_chart(fig_all, use_container_width=True)

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

        import scipy.intp
        power_interp = scipy.intp.interp1d(x, y)
        #power_interp = scipy.intp.interp1d(df_Dan["time_in"], df_Dan["Power_true"])
        #interp_true_w_dist = scipy.intp.interp1d(df_Dan["time_in"], df_Dan["Total_Dist"])

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
        
        
        
 
