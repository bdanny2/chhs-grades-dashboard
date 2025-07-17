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

# --- SIDEBAR: Teacher Entry Portal ---
st.sidebar.title("Teacher Entry Portal")

teacher_email = st.sidebar.text_input("Your Email")
subject = st.sidebar.text_input("Subject")
role = st.sidebar.selectbox("Role", ["Subject Teacher", "Form Teacher"])

st.sidebar.markdown("---")

student_name = st.sidebar.text_input("Student Name")
grade = st.sidebar.number_input("Grade", min_value=0, max_value=100)
conduct_code = st.sidebar.selectbox("Conduct Code", ["Excellent", "Good", "Average", "Needs Improvement"])
comment_code = st.sidebar.text_area("Comment")

#if st.sidebar.button("Submit Entry"):
#    new_row = [teacher_email, subject, role, student_name, str(grade), conduct_code, comment_code]
#    worksheet.append_row(new_row)
#    st.sidebar.success("Entry submitted! (Check the main area for updates)")

if st.sidebar.button("Submit Entry"):
    new_row = [teacher_email, subject, role, student_name, grade, conduct_code, comment_code]
    try:
        st.write("About to write this row:", new_row)
        worksheet.append_row(new_row)
        st.sidebar.success("Entry submitted!")
        st.write("Submitted:", new_row)
    except Exception as e:
        st.sidebar.error(f"Error submitting entry: {e}")
        st.write("ERROR:", e)


# --- MAIN AREA: Show Sheet2 data ---
st.header("Live Sheet Data: Sheet2")

if data and len(data) > 1:
    header = data[0]
    clean_rows = [row for row in data[1:] if len(row) == len(header)]
    df = pd.DataFrame(clean_rows, columns=header)
    st.dataframe(df)
else:
    st.info("No data in Sheet2 or unable to read data.")

