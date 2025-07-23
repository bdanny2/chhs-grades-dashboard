import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import gspread
from google.oauth2.service_account import Credentials
from gspread_dataframe import get_as_dataframe

# --- Authenticate and load Google Sheet from Streamlit secrets ---
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]
service_account_info = st.secrets["gcp_service_account"]
creds = Credentials.from_service_account_info(service_account_info, scopes=scope)
client = gspread.authorize(creds)
worksheet = client.open("Grades2").sheet1  # or .worksheet("Sheet1")
df = get_as_dataframe(worksheet, evaluate_formulas=True).dropna(how='all')

# --- Set background color and font sizes ---
st.markdown("""
    <style>
        body, .stApp { background-color: #f5deb3 !important; }
        section[data-testid="stSidebar"] { background-color: corn-silk !important; }
        .main-title {
            text-align: center; 
            font-size: 3em; 
            font-weight: 400; 
            margin-top: 0.5em;
            margin-bottom: 0.1em;
        }
        .subtitle {
            text-align: center;
            font-size: 1.5em;
            margin-bottom: 1em;
        }
        .section-space { margin-top: 3em; }
        .big-legend { font-size: 1.0em; }
        .block-container {
            padding-top: 1.5em !important;
            padding-bottom: 1.5em !important;
            padding-left: 3vw !important;
            padding-right: 3vw !important;
        }
    </style>
""", unsafe_allow_html=True)

# ---- Sidebar content ----
st.sidebar.image("assets/logo-chhs.png", width=120)
st.sidebar.header("Student Selector")
st.sidebar.markdown("**Welcome to the Clement Howell High School Grades Dashboard!**", unsafe_allow_html=True)

# --- Data selectors ---
students = df['NAME'].dropna().unique()
assessment_types = df['Assessment Type'].dropna().unique()

selected_student = st.sidebar.selectbox("Select a student to view grades:", students)
selected_assessment = st.sidebar.selectbox("Select Assessment Type:", assessment_types)

# ---- Main page header ----
st.markdown("<div class='main-title'>🟢 Student Grades Dashboard</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Visualize individual grades by subject.</div>", unsafe_allow_html=True)
st.markdown("<div class='section-space'></div>", unsafe_allow_html=True)

# ---- Filter Data ----
filtered = df[(df['NAME'] == selected_student) & (df['Assessment Type'] == selected_assessment)]
grades = filtered[['Subject', 'Grade']].dropna()
grades.set_index('Subject', inplace=True)
grades = grades['Grade']

def get_color(g):
    if pd.isnull(g): return 'gray'
    if g < 60: return 'red'
    elif g < 70: return '#FFA500'
    elif g < 93: return 'green'
    else: return 'blue'
colors = [get_color(g) for g in grades]

# ---- Bar chart with large fonts ----
fig, ax = plt.subplots(figsize=(36, 20))
bars = ax.bar(grades.index, grades.values, color=colors)
ax.set_title(f"{selected_student}'s Grades ({selected_assessment})", fontsize=50, pad=20)
ax.set_ylabel('Grade', fontsize=44)
ax.set_xlabel('Subject', fontsize=44)
ax.set_ylim(0, 100)
ax.set_yticks(range(0, 101, 10))
plt.xticks(rotation=30, ha='right', fontsize=45)
plt.yticks(fontsize=45)
plt.tight_layout(pad=3.0)

for bar, grade in zip(bars, grades.values):
    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 2,
            f"{grade:.0f}", ha='center', va='bottom', fontsize=37, fontweight='bold')

st.pyplot(fig, use_container_width=True)
st.markdown("<div class='section-space'></div>", unsafe_allow_html=True)

# ---- Styled table ----
def color_grades(val):
    if pd.isnull(val): return ''
    if val < 60: color = 'red'
    elif val < 70: color = '#FFA500'
    elif val < 93: color = 'green'
    else: color = 'blue'
    return f'color: {color}; font-weight:bold; font-size:1.15em;'

styled = (
    filtered[['Subject', 'Grade']]
    .style
    .applymap(color_grades, subset=['Grade'])
    .format({'Grade': '{:.1f}'})
)

st.markdown("<h2 style='font-size:2em; font-weight:400; text-align:center;'>Grade Table</h2>", unsafe_allow_html=True)
st.dataframe(styled, use_container_width=True, hide_index=True)
st.markdown("<div class='section-space'></div>", unsafe_allow_html=True)

# ---- Bigger legend, spaced out ----
st.markdown("""
<div class='big-legend'>
<b>Legend:</b><br>
<span style='color:red; font-size:1.1em;'>Red</span>: <60<br>
<span style='color:#FFA500; font-size:1.1em;'>Orange</span>: 60–69<br>
<span style='color:green; font-size:1.1em;'>Green</span>: 70-92<br>
<span style='color:blue; font-size:1.1em;'>Blue</span>: 93-100
</div>
""", unsafe_allow_html=True)
