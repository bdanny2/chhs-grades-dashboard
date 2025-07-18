import streamlit as st
import gspread
import pandas as pd
from google.oauth2.service_account import Credentials

# --- Google Sheets Auth ---
service_account_info = st.secrets["gcp_service_account"]
creds = Credentials.from_service_account_info(
    service_account_info, 
    scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
)
client = gspread.authorize(creds)

# --- Sheet Names ---
TEACHERS_SHEET = "Sheet7"
STUDENTS_SHEET = "Sheet2"
SPREADSHEET = "Grades3"

# --- Load Teacher Data ---
teacher_ws = client.open(SPREADSHEET).worksheet(TEACHERS_SHEET)
teacher_data = teacher_ws.get_all_records()
teacher_df = pd.DataFrame(teacher_data)

# --- Sidebar: Teacher Login ---
st.sidebar.title("Teacher Login & Filter")
teacher_email = st.sidebar.text_input("Enter your email")

if teacher_email:
    # Find teacher(s) info
    assigned = teacher_df[teacher_df['email'].str.strip().str.lower() == teacher_email.strip().lower()]
    if assigned.empty:
        st.sidebar.error("No teacher found for that email.")
        st.stop()

    st.sidebar.success(f"Welcome, {assigned.iloc[0]['Teacher']}!")

    # Get list of assigned subjects & classes
    subjects = assigned['Subject'].iloc[0].split(',') if ',' in assigned['Subject'].iloc[0] else [assigned['Subject'].iloc[0]]
    role = assigned['Role'].iloc[0]
    st.sidebar.write(f"Your Role: {role}")
    subject_choice = st.sidebar.selectbox("Select Subject", subjects)

    # Optionally handle multiple classes per teacher if included
    class_list = []
    if 'Class' in assigned.columns:
        class_list = assigned['Class'].iloc[0].split(',') if 'Class' in assigned and isinstance(assigned['Class'].iloc[0], str) else []
    class_choice = st.sidebar.selectbox("Select Class", class_list) if class_list else None

    # --- Load Student Data ---
    student_ws = client.open(SPREADSHEET).worksheet(STUDENTS_SHEET)
    student_data = student_ws.get_all_records()
    student_df = pd.DataFrame(student_data)

    # --- Filter student data for this teacher/subject/class ---
    # Make sure your Sheet2 has columns: Student Name, Subject, Teacher Responsible, Class, etc.
    filt = (
        (student_df['Subject'].str.strip().str.lower() == subject_choice.strip().lower()) &
        (student_df['Teacher Responsible'].str.strip().str.lower() == assigned.iloc[0]['Teacher'].strip().lower())
    )
    if class_choice:
        filt = filt & (student_df['Class'].str.strip().str.lower() == class_choice.strip().lower())
    
    filtered_students = student_df[filt]

    st.header(f"Students for {subject_choice}{' - ' + class_choice if class_choice else ''}")
    st.dataframe(filtered_students)

    # --- Grade Entry ---
    st.subheader("Enter/Update Grade")
    if not filtered_students.empty:
        student_names = filtered_students['Student Name'].tolist()
        student_sel = st.selectbox("Select Student", student_names)
        grade = st.number_input("Grade", min_value=0, max_value=100, step=1)
        conduct_code = st.selectbox("Conduct Code", ["Excellent", "Good", "Average", "Needs Improvement"])
        comment_code = st.text_area("Comment")

        if st.button("Submit Grade"):
            # Find the row to update in Sheet2
            idx = student_df[
                (student_df['Student Name'] == student_sel) &
                (student_df['Subject'] == subject_choice) &
                (student_df['Teacher Responsible'] == assigned.iloc[0]['Teacher'])
            ].index

            if not idx.empty:
                # Sheet2 row numbers are 1-based (with header), so add +2 (header + zero-indexed)
                sheet2_row = idx[0] + 2
                # Update grade, conduct, comment columns (adjust column letters as needed!)
                # Example: Grade=H, Conduct=I, Comment=J (check your sheet layout)
                student_ws.update_acell(f'H{sheet2_row}', str(grade))
                student_ws.update_acell(f'I{sheet2_row}', conduct_code)
                student_ws.update_acell(f'J{sheet2_row}', comment_code)
                st.success("Grade updated!")
            else:
                st.error("Student not found for this subject/teacher.")

else:
    st.info("Please enter your email to begin.")

