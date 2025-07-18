import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd

# --- PAGE CONFIG & MINIMAL STYLING ---
st.set_page_config(page_title="Grades Entry Portal", layout="wide")
st.markdown("""
    <style>
        body, .stApp { background-color: #f5deb3 !important; }
        section[data-testid="stSidebar"] { background-color: cornsilk !important; }
        .main-title { text-align: center; font-size: 2.5em; font-weight: 500; }
        .subtitle { text-align: center; font-size: 1.3em; margin-bottom: 0.8em; }
        .block-container { padding-top: 1.2em !important; }
    </style>
""", unsafe_allow_html=True)

# --- CONSTANTS ---
SPREADSHEET_NAME = "Grades3"
SHEET_STUDENT = "Sheet2"   # Main grade data
SHEET_TEACHERS = "Sheet7"  # Teacher emails/names/subjects

# --- AUTH & LOAD DATA ---
service_account_info = st.secrets["gcp_service_account"]
creds = Credentials.from_service_account_info(
    service_account_info,
    scopes=[
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
)
client = gspread.authorize(creds)

# Load teachers
teacher_ws = client.open(SPREADSHEET_NAME).worksheet(SHEET_TEACHERS)
teacher_df = pd.DataFrame(teacher_ws.get_all_records())

# --- SIDEBAR: Teacher Login/Validation ---
st.sidebar.image("logo-chhs.png", width=120)
st.sidebar.title("Teacher Entry Portal")
email = st.sidebar.text_input("Your Email").strip().lower()

matched = teacher_df[teacher_df["email"].str.strip().str.lower() == email]
if len(matched) == 0:
    st.sidebar.error("Please enter your registered CHHS email for access.")
    st.stop()
else:
    teacher_name = matched.iloc[0]["Teacher"]
    st.sidebar.success(f"Welcome, {teacher_name}!")
    # If teacher has multiple rows (multiple subjects)
    subjects = matched["Subject"].tolist()
    subject = st.sidebar.selectbox("Select Subject", sorted(set(subjects)))

# --- LOAD AND FILTER STUDENT DATA ---
student_ws = client.open(SPREADSHEET_NAME).worksheet(SHEET_STUDENT)
student_data = student_ws.get_all_values()
header = student_data[0]
student_df = pd.DataFrame(student_data[1:], columns=header)

# Filter for teacher's students, subject
filtered = student_df[
    (student_df["Teacher_Responsible_Email"].str.strip().str.lower() == email) &
    (student_df["Subject"] == subject)
]

# --- Add sidebar filters (Term, Assessment Type) ---
if not filtered.empty:
    term_options = sorted(filtered["Term"].unique())
    term = st.sidebar.selectbox("Term", term_options)
    filtered = filtered[filtered["Term"] == term]

    assessment_options = sorted(filtered["Assessment Type"].unique())
    assessment_type = st.sidebar.selectbox("Assessment Type", assessment_options)
    filtered = filtered[filtered["Assessment Type"] == assessment_type]

    st.header(f"Editing Grades as: {teacher_name} ({subject}, {term}, {assessment_type})")

    # Columns that can be edited
    editable_cols = ["Grade", "Subject Teacher Conduct Code", "Subject Teacher Comment Code"]

    # Show teacher's name (friendly display)
    filtered_view = filtered.copy()
    filtered_view["Teacher"] = teacher_name

    # --- DATA EDITOR FOR GRADE ENTRY ---
    st.markdown("#### 📝 Enter or Edit Grades/Conduct/Comments")
    edited_df = st.data_editor(
        filtered_view,
        num_rows="fixed",
        use_container_width=True,
        column_config={
            "Grade": st.column_config.NumberColumn("Grade", min_value=0, max_value=100),
            "Subject Teacher Conduct Code": st.column_config.SelectboxColumn(
                "Conduct", options=["Excellent", "Good", "Average", "Needs Improvement"]
            ),
            "Subject Teacher Comment Code": st.column_config.TextColumn("Comment")
        },
        disabled=[c for c in filtered_view.columns if c not in editable_cols],
        key="grade_editor"
    )

    if st.button("Save Changes"):
        changed = (filtered[editable_cols] != edited_df[editable_cols]).any(axis=1)
        updated = 0
        for idx in filtered[changed].index:
            row_number = idx + 2  # Header is row 1
            for col in editable_cols:
                col_number = student_df.columns.get_loc(col) + 1
                new_value = edited_df.at[idx, col]
                student_ws.update_cell(row_number, col_number, new_value)
            updated += 1
        if updated:
            st.success(f"Saved {updated} updated row(s) to Google Sheet!")
        else:
            st.info("No changes detected to save.")

else:
    st.info("No assigned students for your filter selection.")

# --- ALWAYS SHOW THE FULL DATA BELOW FOR TRANSPARENCY ---
st.divider()
st.subheader("📋 Full Grades Sheet (Read-only)")
st.dataframe(student_df, use_container_width=True)
