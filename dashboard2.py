import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd

# --- Authenticate and connect to your new workbook ---
service_account_info = st.secrets["gcp_service_account"]
creds = Credentials.from_service_account_info(
    service_account_info, 
    scopes=[
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
)
client = gspread.authorize(creds)

# --- Open your spreadsheet ---
SPREADSHEET_NAME = "Grades3"
SHEET_NAME = "Sheet2"

try:
    worksheet = client.open(SPREADSHEET_NAME).worksheet(SHEET_NAME)
    data = worksheet.get_all_values()
    st.success(f"Connected to: {SPREADSHEET_NAME} / {SHEET_NAME}")
except Exception as e:
    st.error(f"Failed to open sheet: {e}")
    data = []

# --- Parse headers and rows for dropdowns ---
if data and len(data) > 1:
    header = data[0]
    rows = data[1:]
    df = pd.DataFrame(rows, columns=header)
    # Get unique lists for dropdowns
    student_names = sorted(list(set(df["Student Name"].dropna())))
    subjects = sorted(list(set(df["Subject"].dropna())))
    assessment_types = sorted(list(set(df["Assessment Type"].dropna())))
else:
    header = []
    df = pd.DataFrame()
    student_names = []
    subjects = []
    assessment_types = []

# --- SIDEBAR: Teacher Entry Portal ---
st.sidebar.title("Teacher Entry Portal")

teacher_email = st.sidebar.text_input("Your Email")
subject = st.sidebar.selectbox("Subject", subjects) if subjects else st.sidebar.text_input("Subject")
role = st.sidebar.selectbox("Role", ["Subject Teacher", "Form Teacher"])
student_name = st.sidebar.selectbox("Student Name", student_names) if student_names else st.sidebar.text_input("Student Name")
assessment_type = st.sidebar.selectbox("Assessment Type", assessment_types) if assessment_types else st.sidebar.text_input("Assessment Type")
grade = st.sidebar.number_input("Grade", min_value=0, max_value=100)
conduct_code = st.sidebar.selectbox("Conduct Code", ["Excellent", "Good", "Average", "Needs Improvement"])
comment_code = st.sidebar.text_area("Comment")

# --- Update the right row, not append ---
if st.sidebar.button("Submit Entry"):
    if not all([teacher_email, subject, student_name, assessment_type]):
        st.sidebar.error("Please fill in all required fields!")
    else:
        # Find the row to update
        data = worksheet.get_all_values()
        header = data[0]
        rows = data[1:]

        col_name = header.index("Student Name")
        col_subject = header.index("Subject")
        col_assessment = header.index("Assessment Type")
        col_grade = header.index("Grade")
        col_conduct = header.index("Subject Teacher Conduct Code")
        col_comment = header.index("Subject Teacher Comment Code")
        col_teacher = header.index("Teacher")
        col_role = header.index("Role") if "Role" in header else None  # Optional

        row_num = None
        for i, row in enumerate(rows, start=2):  # Google Sheets is 1-indexed
            if (
                row[col_name].strip() == student_name.strip() and
                row[col_subject].strip() == subject.strip() and
                row[col_assessment].strip() == assessment_type.strip()
            ):
                row_num = i
                break

        if row_num:
            worksheet.update_cell(row_num, col_teacher + 1, teacher_email)
            if col_role: worksheet.update_cell(row_num, col_role + 1, role)
            worksheet.update_cell(row_num, col_grade + 1, grade)
            worksheet.update_cell(row_num, col_conduct + 1, conduct_code)
            worksheet.update_cell(row_num, col_comment + 1, comment_code)
            st.sidebar.success(f"Updated row for {student_name} / {subject} / {assessment_type}")
        else:
            st.sidebar.error("No matching row found! (Student/Subject/Assessment Type)")
            st.sidebar.info("Make sure the entry already exists. You cannot add a new student here.")

# --- MAIN AREA: Show Sheet2 data ---
st.header("Live Sheet Data: Sheet2")
if not df.empty:
    st.dataframe(df)
else:
    st.info("No data in Sheet2 or unable to read data.")
