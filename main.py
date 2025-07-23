# main.py

import streamlit as st

from utils.layout import apply_common_layout

apply_common_layout(
    page_key="teacher_input",
    title="CHHS Grading System",
    subtitle=""
)


st.set_page_config(
    page_title="CHHS Grades Portal",
    page_icon="🎓",
    layout="wide"
)

# --- Load school logo from assets folder ---
st.sidebar.image("assets/logo-chhs.png", width=120)

# --- Welcome Screen ---
st.title("🏫 Clement Howell High School Grades Portal")
st.markdown("""
Welcome to the **CHHS Student Grades System**.  
Use the sidebar to navigate between dashboards:
- 📊 Student Grades
- 🧑‍🏫 Teacher Entry
- 🛠️ Admin Tools
- 📘 Documentation

This system integrates **Google Sheets** and **Moodle** to provide a seamless grading experience for all stakeholders: **Teachers, Admins, Students, and Parents**.
""")

st.markdown("---")

st.info("👈 Use the sidebar to get started!", icon="✨")

