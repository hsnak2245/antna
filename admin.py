import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import numpy as np
from groq import Groq
import json
import warnings

# Must be the first Streamlit command
st.set_page_config(
    page_title="ANTNA Admin",
    page_icon="🐜",
    layout="wide",
    initial_sidebar_state="expanded",
)

warnings.filterwarnings('ignore')

# Load CSS
def load_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

load_css('styles.css')

# Initialize Groq client
try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
except:
    GROQ_API_KEY = "GROQ_API_KEY"

try:
    groq_client = Groq(api_key=GROQ_API_KEY)
except Exception as e:
    st.error(f"Failed to initialize Groq client: {str(e)}")
    st.stop()

[... rest of your functions remain the same ...]

def main():
    # Initialize session state
    init_session_state()

    st.markdown("""
        <div class="title-block">
            <h1>🐜 ANTNA Admin</h1>
            <p><span class="status-indicator status-active"></span>Crisis Simulation Control</p>
        </div>
    """, unsafe_allow_html=True)

    # Create tabs
    tab1, tab2 = st.tabs(["💭 Scenario Generator", "📊 Current Data"])

    [... rest of main function remains the same ...]

if __name__ == "__main__":
    main()
