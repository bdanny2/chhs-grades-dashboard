# utils/layout.py

import streamlit as st

def apply_common_layout(page_key: str, title: str, subtitle: str):
    st.set_page_config(page_title=title, layout="wide")

    # Sidebar styling with logo and active highlight
    with st.sidebar:
        st.markdown(
            """
            <style>
            [data-testid="stSidebar"] {
                background-color: #fff9dc;
            }
            .active-link {
                background-color: #f0ead6;
                border-radius: 8px;
                padding: 0.3rem;
                font-weight: bold;
            }
            </style>
            """, unsafe_allow_html=True
        )
        
        st.image("assets/logo-chhs.png", width=100)

        st.markdown("### Navigation")
        st.markdown("---")

        pages = {
            "main": "Main",
            "admin_dashboard": "Admin Dashboard",
            "docs_page": "Docs Page",
            "moodle_sync": "Moodle Sync",
            "parent_portal": "Parent Portal",
            "student_view": "Student View",
            "teacher_input": "Teacher Input",
            "teacher_page": "Teacher Page"
        }

        for key, name in pages.items():
            css_class = "active-link" if key == page_key else ""
            st.markdown(
                f"<div class='{css_class}'>• <a href='/{key}'>{name}</a></div>",
                unsafe_allow_html=True
            )

    # Top header
    st.markdown(
        f"""
        <div style="background-color: #f8ddb0; padding: 1rem 2rem; border-radius: 0 0 10px 10px;">
            <h1 style="color: #333;">🟢 {title}</h1>
            <p style="font-size: 1.1rem; color: #444;">{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True
    )
