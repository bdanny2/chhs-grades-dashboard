# utils/sheets_api.py

import pandas as pd
import gspread
from gspread_dataframe import get_as_dataframe
import streamlit as st

def load_grades_df(sheet_name="Grades3"):
    gc = gspread.service_account_from_dict(st.secrets["gcp_service_account"])
    sh = gc.open(sheet_name)
    worksheet = sh.sheet1
    df = get_as_dataframe(worksheet, evaluate_formulas=True)
    df = df.dropna(how="all")  # remove empty rows
    return df

def append_grade_row(row_dict, sheet_name="Grades3"):
    gc = gspread.service_account_from_dict(st.secrets["gcp_service_account"])
    sh = gc.open(sheet_name)
    worksheet = sh.sheet1
    worksheet.append_row(list(row_dict.values()))
