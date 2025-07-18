import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd

# --- Authenticate & Load Data ---
service_account_info = st.secrets["gcp_service_account"]
creds = Credentials.from_service_account_info(
    service_account_info,
    scopes=[
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
)
client = gspread.authorize(creds)

SPREADSHEET_NAME = "Grades3"
SHEET_STUDENT = "Sheet2"   # Main grade data
SHEET_TEACHERS = "Sheet7"  # Teacher emails/names/subjects

# --- Load Teacher Roster ---
teacher_ws = client.open(SPREADSHEET_NAME).worksheet(SHEET_TEACHERS)
teacher_data = teacher_ws.get_all_records()
teacher_df = pd.DataFrame(teacher_data)

# --- Sidebar: Teacher Email Validation ---
st.sidebar.title("Teacher Entry Portal")
email = st.sidebar.text_input("Your Email").strip().lower()

# Validate email
matched = teacher_df[teacher_df["email"].str.strip().str.lower() == email]
if len(matched) == 0:
    st.sidebar.error("Email not recognized! Please use your registered email.")
    st.stop()
else:
    teacher_name = matched.iloc[0]["Teacher"]
    st.sidebar.success(f"Welcome, {teacher_name}!")
    # Optional: Let teachers select which subject if they teach multiple
    subjects = matched["Subject"].tolist()  # in case of multiple rows per email
    subject = st.sidebar.selectbox("Select Subject", sorted(set(subjects)))

# --- Load and filter student data ---
student_ws = client.open(SPREADSHEET_NAME).worksheet(SHEET_STUDENT)
student_data = student_ws.get_all_values()
header = student_data[0]
student_df = pd.DataFrame(student_data[1:], columns=header)

# Assume there's a 'Teacher Responsible Email' column for filtering
filtered = student_df[
    (student_df["Teacher Responsible Email"].str.strip().str.lower() == email) &
    (student_df["Subject"] == subject)
]

# Add more sidebar filters (Term, Assessment Type, etc.)
if not filtered.empty:
    term = st.sidebar.selectbox("Term", sorted(filtered["Term"].unique()))
    filtered = filtered[filtered["Term"] == term]
    assessment_type = st.sidebar.selectbox("Assessment Type", sorted(filtered["Assessment Type"].unique()))
    filtered = filtered[filtered["Assessment Type"] == assessment_type]

    st.write(f"Editing as: **{teacher_name}** ({subject}, {term}, {assessment_type})")

    # Inline editable columns
    editable_cols = ["Grade", "Subject Teacher Conduct Code", "Subject Teacher Comment Code"]

    # Show teacher's name in the table (friendly!)
    filtered_view = filtered.copy()
    filtered_view["Teacher"] = teacher_name

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
        for idx in filtered[changed].index:
            row_number = idx + 2  # Header = row 1 in Sheets
            for col in editable_cols:
                col_number = student_df.columns.get_loc(col) + 1
                new_value = edited_df.at[idx, col]
                student_ws.update_cell(row_number, col_number, new_value)
        st.success("Changes saved to Google Sheet!")

else:
    st.info("No assigned students for your filter selection.")

