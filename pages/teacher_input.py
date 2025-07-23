import streamlit as st
import pandas as pd
from utils.sheets_api import load_grades_df, append_grade_row

from utils.layout import apply_common_layout

apply_common_layout(
    page_key="teacher_input",
    title="Teacher Grade Input",
    subtitle="Input and update your subject grades here."
)




# --- Teacher Authentication ---
teacher_email = st.text_input("Enter your teacher email")

if teacher_email:
    st.success(f"Welcome, {teacher_email}!")

    # Load Grades data
    df = load_grades_df()

    # Filter for this teacher's entries
    teacher_df = df[df["Teacher"] == teacher_email]

    if teacher_df.empty:
        st.warning("No records found for this teacher.")
    else:
        # Optional filter UI: Subject + Term
        subjects = sorted(teacher_df["Subject"].dropna().unique())
        terms = sorted(teacher_df["Assessment Period"].dropna().unique())

        selected_subject = st.selectbox("Filter by Subject", ["All"] + subjects)
        selected_term = st.selectbox("Filter by Term", ["All"] + terms)

        filtered_df = teacher_df.copy()
        if selected_subject != "All":
            filtered_df = filtered_df[filtered_df["Subject"] == selected_subject]
        if selected_term != "All":
            filtered_df = filtered_df[filtered_df["Assessment Period"] == selected_term]

        st.subheader("Editable Grade Sheet (Your Classes Only)")

        edited_df = st.data_editor(
            filtered_df.reset_index(drop=True),
            num_rows="dynamic",
            use_container_width=True,
            key="teacher_editable_grades"
        )

        st.caption("⚠ Changes are local only. Save feature coming soon.")
else:
    st.info("Please enter your email to access grade entry.")
