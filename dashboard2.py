import streamlit as st
import gspread
from google.oauth2.service_account import Credentials

# --- Authenticate and connect to your new workbook ---
service_account_info = st.secrets["gcp_service_account"]
creds = Credentials.from_service_account_info(service_account_info, scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
])
client = gspread.authorize(creds)
worksheet = client.open("Grades3").worksheet("Sheet1")  # Update sheet name if needed

# --- Sidebar UI ---
st.sidebar.title("Teacher Entry Portal")

teacher_email = st.sidebar.text_input("Your Email")
subject = st.sidebar.text_input("Subject")
role = st.sidebar.selectbox("Role", ["Subject Teacher", "Form Teacher"])

st.sidebar.markdown("---")

# -- Grades input --
student_name = st.sidebar.text_input("Student Name")
grade = st.sidebar.number_input("Grade", min_value=0, max_value=100)
conduct_code = st.sidebar.selectbox("Conduct Code", ["Excellent", "Good", "Average", "Needs Improvement"])  # Update as needed
comment_code = st.sidebar.text_area("Comment")

if st.sidebar.button("Submit Entry"):
    # --- Logic to write to Google Sheets ---
    new_row = [teacher_email, subject, role, student_name, grade, conduct_code, comment_code]
    worksheet.append_row(new_row)
    st.sidebar.success("Entry submitted!")

# You can expand this with dropdowns for students, subjects, etc., by reading the sheet and populating options.
