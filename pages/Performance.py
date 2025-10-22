import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utility_function.initilize_dbconnection import supabase
from utility_function import performance_utility

# Check if user is logged in
if not st.session_state.get('logged_in', False):
    st.warning("Please log in to access this page.")
    st.stop()

st.title("📈 Performance Analytics")
st.write(f"Welcome, {st.session_state.get('fullname')}!")

user_role = st.session_state.get('role')
user_id = st.session_state.get('user_id')

# Create tabs
tabs = st.tabs(["👤 Personal Performance", "👥 Others' Performance", "🌍 Community Leaderboard", "🏆 Category Ratings"])
tab_personal, tab_others, tab_community, tab_category = tabs

# ========================================
# TAB 1: Personal Performance
# ========================================
with tab_personal:
    st.header("👤 My Performance Analytics")
  