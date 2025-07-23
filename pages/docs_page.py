import streamlit as st
from pathlib import Path


from utils.layout import apply_common_layout

apply_common_layout(
    page_key="teacher_input",
    title="Teacher Grade Input",
    subtitle="Input and update your subject grades here."
)



def load_doc(file_name):
    path = Path("docs") / file_name
    return path.read_text() if path.exists() else "❌ File not found."

# Sidebar navigation
st.sidebar.title("📁 Documentation")
doc_map = {
    "Roles & Permissions": "roles.md",
    "Grade Workflows": "workflows.md",
    "Moodle Integration": "integration.md",
    "System Architecture": "architecture.md",
    "Developer Notes": "dev-notes.md"
}

selected_doc = st.sidebar.selectbox("📄 View a document", list(doc_map.keys()))
st.markdown(f"# 📘 {selected_doc}")
st.markdown(load_doc(doc_map[selected_doc]))
