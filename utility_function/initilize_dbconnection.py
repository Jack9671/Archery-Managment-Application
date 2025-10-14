import os
from supabase import create_client, Client
import streamlit as st
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Supabase client
@st.cache_resource
def init_supabase():
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_ANON_KEY")
    
    if not url or not key:
        st.error(f"Missing Supabase environment variables. URL: {url}, Key: {'***' if key else None}")
        st.stop()
    
    return create_client(url, key)

supabase: Client = init_supabase()
