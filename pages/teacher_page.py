import streamlit as st
import pandas as pd
from datetime import datetime


from utils.layout import apply_common_layout

apply_common_layout(
    page_key="teacher_input",
    title="Teacher Grade Input",
    subtitle="Input and update your subject grades here."
)


# Load master data
grades_file = "Grades3.xlsx"
df = pd.read_excel(grades_file)
teacher_list = sorted(df["Subject Teacher"].dropna().unique())
subjects_list = sorted(df["Subject"].dropna().unique())
terms = sorted(df["Assessment Period"].dropna().unique())

# --- Grade Entry Form ---
st.image('logo-chhs.png', width=100)
st.title("Teacher Grade Entry Portal")

with st.form("grade_entry_form", clear_on_submit=True):
    teacher = st.selectbox("Teacher Name", ["Select..."] + teacher_list)
    # Only show subjects that this teacher teaches
    if teacher != "Select...":
        teacher_subjects = df[df["Subject Teacher"] == teacher]["Subject"].dropna().unique()
    else:
        teacher_subjects = []
    subject = st.selectbox("Subject", ["Select..."] + list(teacher_subjects))
    term = st.selectbox("Term/Period", terms)
    
    # Students filtered by subject/teacher/term (adjust as needed)
    eligible_students = df[
        (df["Subject Teacher"] == teacher) & 
        (df["Subject"] == subject) & 
        (df["Assessment Period"] == term)
    ]["NAME"].unique()
    
    student = st.selectbox("Student Name", eligible_students)
    assessment_type = st.selectbox("Assessment Type", ["Marksheet 1", "Marksheet 2", "Exam"])
    grade = st.number_input("Grade (0-100)", min_value=0, max_value=100)
    comments = st.text_area("Comments (optional)")
    submit = st.form_submit_button("Submit Grade")
    
    if submit:
        new_row = {
            "NAME": student,
            "Subject": subject,
            "Subject Teacher": teacher,
            "Assessment Type": assessment_type,
            "Grade": grade,
            "Assessment Period": term,
            "Date Submitted": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Comments": comments
        }
        # Append to DataFrame
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        # Write back to Excel (CAREFUL: this will overwrite!)
        df.to_excel(grades_file, index=False)
        st.success(f"Grade for {student} in {subject} ({assessment_type}) submitted!")

        # Optional: show last 5 submissions for this teacher
        st.subheader("Your Recent Submissions")
        recent = df[
            (df["Subject Teacher"] == teacher)
        ].sort_values("Date Submitted", ascending=False).head(5)
        st.dataframe(recent)

