import streamlit as st
from dotenv import load_dotenv


# Load environment variables
load_dotenv()

def main():
    st.set_page_config(page_title="Archery Management System", layout="wide")
    st.title("Welcome to the Archery Management System")
    st.write("The application is used to manage archery tournaments, participants, and scores.")
    st.write("start by signing up or logging in.")

