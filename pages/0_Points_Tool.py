#!/usr/bin/env python
# coding: utf-8



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



st.set_page_config(page_title='CNZ Performance Database',
                  page_icon=":bike:",
                  layout="wide")
st.header('Points Tool')

update = datetime.date.today()+ pd.DateOffset(hour=12)


#@st.cache_data

def get_MK_points_data_from_excel():
    df_MK = pd.read_excel(
        io='pages/Kierin_Points_Men.xlsx',
        engine ='openpyxl',
        sheet_name='Kierin_Points_Men',
        skiprows=0,
        usecols='A:J',
        nrows=3000
        )
    df_MK = df_MK.replace(',','')
    df_MK['Date'] = pd.to_datetime(df_MK['Date']).dt.date
    return df_MK
df_MK = get_MK_points_data_from_excel()



def get_MS_points_data_from_excel():
    df_MS = pd.read_excel(
        io='pages/Sprint_Points_Men.xlsx',
        engine ='openpyxl',
        sheet_name='Sprint_Points_Men',
        skiprows=0,
        usecols='A:J',
        nrows=3000
        )
    df_MS = df_MS.replace(',','')
    df_MS['Date'] = pd.to_datetime(df_MS['Date']).dt.date
    return df_MS
df_MS = get_MS_points_data_from_excel()





def get_WS_points_data_from_excel():
    df_WS = pd.read_excel(
        io='pages/Sprint_Points_Women.xlsx',
        engine ='openpyxl',
        sheet_name='Sprint_Points_Women',
        skiprows=0,
        usecols='A:J',
        nrows=3000
        )
    df_WS = df_WS.replace(',','')
    df_WS['Date'] = pd.to_datetime(df_WS['Date']).dt.date
    return df_WS
df_WS = get_WS_points_data_from_excel()




def get_WK_points_data_from_excel():
    df_WK = pd.read_excel(
        io='pages/Kierin_Points_Women.xlsx',
        engine ='openpyxl',
        sheet_name='Kierin_Points_Women',
        skiprows=0,
        usecols='A:J',
        nrows=3000
        )
    df_WK = df_WK.replace(',','')
    df_WK['Date'] = pd.to_datetime(df_WK['Date']).dt.date
    return df_WK
df_WK = get_WK_points_data_from_excel()

s = os.path.getmtime('pages/Kierin_Points_Women.xlsx')
dt_m = datetime.date.fromtimestamp(s)+pd.DateOffset(days=1)
s1 = dt_m.strftime("%d/%m/%Y")
st.subheader("Last updated on "+ str(s1))
Events = ["Men's Sprint","Men's Kierin", "Women's Sprint", "Women's Kierin"]

Event = st.selectbox("Select Event:", Events, key="Event_selector")

if Event == Events[0]:
    df=df_MS
elif Event == Events[1]:
    df=df_MK
elif Event == Events[2]:
    df=df_WS
else:
    df=df_WK
    
df_orig=df


#st.subheader("Number of events for inclusion (shouldn't have to change these values)")
today = datetime.date.today()
default_start = datetime.date(2022, 6, 22)
# col_one, col_two, col_three, col_four, col_five = st.columns(5)

### This was when you could change the number of events etc

# with col_one:
#     WC_events = st.number_input("UCI World Championships", min_value=0, max_value=None, value=1, key="WC")
# with col_two:
#     NC_events = st.number_input("Nations' Cup", min_value=0, max_value=None, value=1, key="NC")
# with col_three:
#     CC_events = st.number_input("Continental Championships", min_value=0, max_value=None, value=1, key="CC")
# with col_four:
#     NCH_events = st.number_input("National Championships", min_value=0, max_value=None, value=1, key="NCH")
# with col_five:
#     TCLOR_events = st.number_input("Track Champions League Overall Ranking", min_value=0, max_value=None, value=1, key="TCLOR")
# col_one, col_two, col_three, col_four,col_five = st.columns(5)
# with col_three:
#     CTWO_events = st.number_input("Class 2", min_value=0, max_value=None, value=3, key="C2")
# with col_one:
#     TCLRR_events = st.number_input("Track Champions League Round Ranking", min_value=0, max_value=None, value=5, key="TCLRR")
# with col_two:
#     CONE_events = st.number_input("Class 1", min_value=0, max_value=None, value=3, key="C1")
# with col_four:
#     start_date = st.date_input('Period Start', default_start,key="Start date")
# with col_five:
#     end_date = st.date_input('Period Finish', today,key="End date")
# col_one, col_two, col_three, col_four, col_five = st.columns(5)
# with col_one:
#     max_athletes = st.number_input("Max numbers of athletes from each nation", min_value=0, max_value=None, value=2, key="Max_athletes")

##Hard coded event numbers
WC_events=1
NC_events=1
CC_events=1
NCH_events=1
TCLOR_events=1
CTWO_events=3
TCLRR_events=5
CONE_events=3
start_date = default_start
end_date = datetime.date(2023, 6, 21)
#max_athletes=2



st.write("This sums the best World Champs, Nations Cup, Continental Champs, National Champs, and Overall Champions League points, as well as top three Class 1 and Class 2 points, and top five Champions League Round points, between " + str(start_date) + " and " + str(end_date))

col_one, col_two, col_three, col_four = st.columns(4)
with col_one:
    options = ["All athletes","Top two from each Nation"]
    Max_Ath = st.selectbox("Athletes shown:", options, key="Max Athletes")
with col_two:
    kiwisOnly = ["No","Yes"]
    JustKiwis = st.selectbox("Show Kiwis Only?:", kiwisOnly, key="kiwis only")

if Max_Ath=="Top two from each Nation":
    max_athletes = 2
else:
    max_athletes = 200
    
    
df = df[(df['Date'] > start_date) & (df['Date'] < end_date)]
athletes = df['Name'].drop_duplicates()
countries = []

WC_totals = []
NC_totals = []
CC_totals = []
NCH_totals = []
TCLRR_totals = []
TCLOR_totals = []
CONE_totals = []
CTWO_totals = []
totals=[]
allowed_athletes = []

for i in range(len(athletes)):
    y = df.loc[(df.Name == athletes.iloc[i]),'Country'].iloc[0]
    if countries.count(y)<max_athletes:
        allowed_athletes.append(athletes.iloc[i])
        countries.append(y)
        total=0
        x = df.loc[(df.Class == "WCh") &  (df.Name == athletes.iloc[i]),'Points'].astype(int).sort_values(ascending=False)
        WC_total = sum(x[:WC_events])
        WC_totals.append(WC_total)
        total+=WC_total

        x = df.loc[(df.Class == "NCp") &  (df.Name == athletes.iloc[i]),'Points'].astype(int).sort_values(ascending=False)
        NC_total = sum(x[:NC_events])
        NC_totals.append(NC_total)
        total+=NC_total

        x = df.loc[(df.Class == "CCh") &  (df.Name == athletes.iloc[i]),'Points'].astype(int).sort_values(ascending=False)
        CC_total = sum(x[:CC_events])
        CC_totals.append(CC_total)
        total+=CC_total

        x = df.loc[(df.Class == "NCh") &  (df.Name == athletes.iloc[i]),'Points'].astype(int).sort_values(ascending=False)
        NCH_total = sum(x[:NCH_events])
        NCH_totals.append(NCH_total)
        total+=NCH_total

        x = df.loc[(df.Class == "ChL") &  (df.Name == athletes.iloc[i]),'Points'].astype(int).sort_values(ascending=False)
        TCLOR_total = sum(x[:TCLOR_events])
        TCLOR_totals.append(TCLOR_total)
        total+=TCLOR_total

        x = df.loc[(df.Class == "ChR") &  (df.Name == athletes.iloc[i]),'Points'].astype(int).sort_values(ascending=False)
        TCLRR_total = sum(x[:TCLRR_events])
        TCLRR_totals.append(TCLRR_total)
        total+=TCLRR_total

        x = df.loc[(df.Class == "CL1") &  (df.Name == athletes.iloc[i]),'Points'].astype(int).sort_values(ascending=False)
        CONE_total = sum(x[:CONE_events])
        CONE_totals.append(CONE_total)
        total+=CONE_total

        x = df.loc[(df.Class == "CL2") &  (df.Name == athletes.iloc[i]),'Points'].astype(int).sort_values(ascending=False)
        CTWO_total = sum(x[:CTWO_events])
        CTWO_totals.append(CTWO_total)
        total+=CTWO_total
        totals.append(total)



Points = {'Name': allowed_athletes,
          'Country': countries,
          'Total': totals,
          'WCh': WC_totals,
          "NCp": NC_totals,
          'CCh': CC_totals,
          'NCh': NCH_totals,
          'ChL': TCLOR_totals,
          'ChR': TCLRR_totals,
          'CL1': CONE_totals,
          'CL2': CTWO_totals,
          
         }

df_points=pd.DataFrame(Points).sort_values('Total',ascending=False)
Rank = list(range(1,len(allowed_athletes)+1))
df_points.insert(loc=0, column='Rank', value=Rank)
if JustKiwis == "Yes":
    df_points = df_points.loc[(df_points.Country == "NZL")]
df_points


st.subheader("All Results")
col_one, col_two = st.columns(2)

Classes = df_orig['Class'].drop_duplicates().sort_values()
Events = df_orig['Event'].drop_duplicates().sort_values()
with col_one:
    Class = st.multiselect("Select Class(es):", Classes)

df_class = df_orig.query(
    "Class == @Class"
)

if Class==[]:
    Events = df_orig['Event'].drop_duplicates().sort_values()
else:
    Events = df_class['Event'].drop_duplicates().sort_values()
with col_two:
    Event = st.multiselect("Select Event(s):", Events)
    
df_event = df_orig.query(
    "Event == @Event"
)

df_both = df_orig.query(
    "Class == @Class & Event == @Event"
)

if Class==[] and Event==[]:
    st.dataframe(df_orig)
elif Event==[]:
    st.dataframe(df_class)
elif Class==[]:
    st.dataframe(df_event)
else:
    st.dataframe(df_both)
    




# year = st.multiselect(
#     "Select Year:",
#     options=df["Year"].unique(),
#     default=df["Year"].unique()[0]
# )    
# if year:
#     df = df.query(
#         "Year == @year"
#         )
# else:
#     df=df_orig


# location = st.multiselect(
#     "Select Location:",
#     options=df["Location"].unique(),
#     default=df["Location"].unique()[0]
# )

# if location:
#     df = df.query(
#         "Location == @location"
#         )
# else:
#     df=df_orig

# event = st.multiselect(
#     "Select Event Type:",
#     options=df["Event"].unique(),
#     default=df["Event"].unique()[0]
# )

# if event:
#     df = df.query(
#         "Event == @event"
#         )
# else:
#     df=df_orig

    
# st.dataframe(df)

# st.markdown("---")
    
# st.title(":bicyclist: Athlete History")

# athletes = df_orig['Athlete'].drop_duplicates().sort_values()
# athlete = st.multiselect("Select Athlete(s):", athletes)

# df_athleteHistory = df_orig.query(
#     "Athlete == @athlete"
# )

# st.dataframe(df_athleteHistory)

# fig_athlete_history = px.line(df_athleteHistory, x="Date", y = ["200m R1"], title = "Times by Date", markers = "True", text = "Location", color="Athlete")
# fig_athlete_history.update_traces(textposition="top right")

# st.plotly_chart(fig_athlete_history)

# fig_athlete_history = px.line(df_athleteHistory, x="Date", y = "Final_Rank", title = "Rank by Date", markers = "True", color="Athlete")
# fig_athlete_history.update_traces(textposition="top right")

# st.plotly_chart(fig_athlete_history)

# fig_athlete_history = px.line(df_athleteHistory, x="Age", y = ["200m R1"], title = "R1 Times by Age", markers = "True", color="Athlete")
# fig_athlete_history.update_traces(textposition="top right")

# st.plotly_chart(fig_athlete_history)

# fig_athlete_history = px.line(df_athleteHistory, x="Age", y = "200m R2", title = "R2 Times by Age", markers = "True", color="Athlete")


# st.plotly_chart(fig_athlete_history)

# fig_athlete_history = px.line(df_athleteHistory, x="Age", y = "200m R3", title = "R3 Times by Age", markers = "True", color="Athlete")


# st.plotly_chart(fig_athlete_history)


# # st.markdown("---")
    
# # st.title(":mag_right: Race Analysis Tool")
# # uniqueYear = df_orig['Year'].drop_duplicates().sort_values(ascending=False)


# # left_column, middle_column, right_column = st.columns(3)
# # with left_column:
# #     an_year = st.selectbox("Select Year:", uniqueYear)
    
# # df_an_year = df_orig.query(
# #     "Year == @an_year"
# # )
# # uniqueLocation = df_an_year['Location'].drop_duplicates().sort_values()

# # with middle_column:
# #     an_location = st.selectbox("Select Location:", uniqueLocation)
    
# # df_an_year_location = df_an_year.query(
# #     "Year == @an_year & Location == @an_location"
# # )
    
# # uniqueEvent = df_an_year_location['Event'].drop_duplicates().sort_values()
# # with right_column:
# #     an_event = st.selectbox("Select Event:", uniqueEvent)

# # df_an = df_an_year_location.query(
# #     "Year == @an_year & Location == @an_location & Event == @an_event"
# # )

# # st.dataframe(df_an)

# # df_and=df_an



# # fig_event = px.line(df_an, y=["100m","200m"], x = "Athlete")

# # st.plotly_chart(fig_event)

# #t.write(df_and["100m"])








# st.markdown("---")
    
# st.title(":date: Points Tool")

# dates = df_points['Date'].drop_duplicates().sort_values()

# today = datetime.date.today()
# year_ago = today + datetime.timedelta(days=-365)


# start_date = st.date_input('Period Start:', year_ago)
# end_date = st.date_input('Period Finish:', today)
# df_points_dates = df_points[(df_points['Date'] > start_date) & (df_points['Date'] < end_date)]
# st.write("Number of days: "+str((end_date-start_date).days))

# df_points_dates=df_points_dates.sort_values("Current_Rank")

# st.dataframe(df_points_dates)
# #df_points_topten = df_points.sort_values("Time").head(10)

# names = df_points_dates['Name'].drop_duplicates()


# df_grouped = df_points_dates.groupby(by="Name")["Points"].sum()

# df_grouped = df_grouped.to_frame()
# df_grouped = df_grouped.sort_values(by="Points",ascending=False)
    
# st.header(":moneybag: Top 50")
# df_grouped.insert(0, 'Rank', range(1, 1+len(df_grouped)))
# st.dataframe(df_grouped.head(50))

# ###Trueskill Stuff

# st.markdown("---")
    
# st.title(":brain: Trueskill - Head to Head")

# df_TS = df_TS.drop_duplicates("Athlete",keep="last")
# #athlete_TS = st.multiselect("Select Athlete(s):", latest_TS)

# ath1 = st.selectbox("Select Athlete 1:", df_TS["Athlete"].sort_values(), key="df_TS")
# ath2 = st.selectbox("Select Athlete 2:", df_TS["Athlete"].sort_values(), key="df_TS_2")

# ind1 = df_TS.index[df_TS['Athlete'] == ath1]
# ind2 = df_TS.index[df_TS['Athlete'] == ath2]
# sig1 = df_TS["Sigma"][ind1].item()
# sig2 = df_TS["Sigma"][ind2].item()
# mu1 = df_TS["Mu"][ind1].item()
# mu2 = df_TS["Mu"][ind2].item()
# name1 = df_TS["Athlete"][ind1].item()
# name2 = df_TS["Athlete"][ind2].item()
# trials=10000
# ### -TESTING




# #x-axis ranges from -3 and 3 with .001 steps
# x = np.arange(0, 50, 0.001)

# #plot normal distribution with mean 0 and standard deviation 1
# plt.plot(x, norm.pdf(x, mu1, sig1), label=df_TS["Athlete"][ind1].iloc[0])
# plt.plot(x, norm.pdf(x, mu2, sig2), label=df_TS["Athlete"][ind2].iloc[0])
# plt.legend()


# s1 = np.random.normal(mu1, sig1, trials)
# s2 = np.random.normal(mu2, sig2, trials)
# s1_wins=0
# for i in range(len(s1)):
#     if s1[i]>s2[i]:
#         s1_wins+=1
# s1_win_prob = s1_wins/trials*100
# s2_win_prob=100-s1_win_prob
# left_column, middle_column, right_column = st.columns(3)
# with left_column:

#     st.write(name1 + " has mu value " + str(mu1) + " and sigma value " + str(sig1))
#     st.write("From " +str(trials) + " trials, " + name1 + " has a " + str(round(s1_win_prob,2))+ "% chance of beating " + name2)
    
# with middle_column:

#     st.pyplot(plt)


# with right_column:

#     st.write(name2 + " has mu value " + str(mu2) + " and sigma value " + str(sig2))
#     st.write("From " +str(trials) + " trials, " + name2 + " has a " + str(round(s2_win_prob,2))+ "% chance of beating " + name1)
    
    
    
    
# ###Multi competitor race simulator    
    
    
    

# st.markdown("---")
    
# st.title(":brain: Trueskill - Race Simulator")

# df_TS_multi = df_TS.drop_duplicates("Athlete",keep="last")
# plt.figure(1)
# aths = st.multiselect("Select Athletes:", df_TS_multi["Athlete"].sort_values(), key="df_TS_multi")


# for j in range(len(aths)):
#     exec(f'scores{j} = []')
#     exec(f'ranks{j} = []')
#     ind = df_TS_multi.index[df_TS_multi['Athlete'] == aths[j]]
#     sig = df_TS_multi["Sigma"][ind].item()
#     mu = df_TS_multi["Mu"][ind].item()
#     plt.figure(0)
#     plt.plot(x, norm.pdf(x, mu, sig), label=aths[j])
    
#     exec(f'scores{j} = np.random.normal(mu, sig, trials)')
    
# left_column, middle_column, right_column = st.columns(3)

# with middle_column:
#     plt.legend()
#     st.pyplot(plt)
    
    
# for i in range(trials): 
#     scores = []
#     for j in range(len(aths)):
#         exec(f'scores.append(scores{j}[i])')
#     for k in range(len(aths)):
#         exec(f'ranks{k}.append(sorted(scores,reverse=True).index(scores[k])+1)')

# i=1


# # sum(int(f'ranks{i}[0]')) / len(int(f'ranks{i}[0]'))        
        
# for i in range(len(aths)):
#     exec(f'st.write(aths[i]+ " has average rank " + str(round(sum(ranks{i})/len(ranks{i}),2)))')
#     for j in range(len(aths)):
#         exec(f'st.write("His likelihood of gaining rank " + str(j+1) + " is "+ str(round(ranks{i}.count(j+1)/len(ranks{i}),3)))')
#     st.write("")