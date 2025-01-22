import streamlit as st
import pandas as pd
from datetime import datetime
import numpy as np
from groq import Groq

# Page config
st.set_page_config(
    page_title="ANTNA Admin",
    page_icon="🐜",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Load CSS
def load_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

load_css('styles/styles.css')

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

# Initialize session state
def init_session_state():
    if 'disasters' not in st.session_state:
        st.session_state.disasters = pd.DataFrame({
            'type': ['No Active Disasters'],
            'severity': ['Low'],
            'location': ['N/A'],
            'time': [datetime.now().strftime('%Y-%m-%d %H:%M')],
            'description': ['No active disasters or emergencies at this time.']
        })
    
    if 'shelters' not in st.session_state:
        st.session_state.shelters = pd.DataFrame({
            'name': ['Lusail Sports Arena', 'Al Thumama Stadium', 'Education City Stadium'],
            'capacity': [800, 600, 500],
            'current': [0, 0, 0],
            'lat': [25.430560, 25.230844, 25.311667],
            'lon': [51.488970, 51.532197, 51.424722],
            'type': ['Shelter', 'Shelter', 'Shelter'],
            'contact': ['+974-4000-111', '+974-4000-222', '+974-4000-333']
        })
    
    if 'resources' not in st.session_state:
        st.session_state.resources = pd.DataFrame({
            'location': ['Lusail Sports Arena', 'Al Thumama Stadium', 'Education City Stadium'],
            'water_supply': [1000, 800, 600],
            'food_supply': [800, 600, 500],
            'medical_kits': [50, 40, 30],
            'beds': [500, 400, 300],
            'last_updated': [datetime.now().strftime('%Y-%m-%d %H:%M')] * 3,
            'status': ['Active'] * 3
        })
    
    if 'updates' not in st.session_state:
        st.session_state.updates = pd.DataFrame({
            'timestamp': [datetime.now().strftime('%Y-%m-%d %H:%M')],
            'source': ['Twitter'],
            'account_type': ['Official'],
            'username': ['@QatarAlert'],
            'message': ['Systems operational. Monitoring for emergencies.'],
            'location': ['Doha'],
            'trust_score': [1.0],
            'verified': [True],
            'engagement': [100]
        })

init_session_state()

def process_llm_response(response_text):
    """Process LLM response and update session state with structured data"""
    try:
        # Here you would parse the LLM's response and extract structured data
        # This is a placeholder implementation - the actual implementation would
        # depend on the format of your LLM's response
        
        # Update disasters
        new_disasters = pd.DataFrame({
            'type': [response_text.split('\n')[0]],  # Example parsing
            'severity': ['High'],
            'location': ['Doha'],
            'time': [datetime.now().strftime('%Y-%m-%d %H:%M')],
            'description': [response_text]
        })
        st.session_state.disasters = pd.concat([new_disasters, st.session_state.disasters])
        
        # Generate some example updates based on the scenario
        new_updates = pd.DataFrame({
            'timestamp': [datetime.now().strftime('%Y-%m-%d %H:%M')] * 3,
            'source': ['Twitter'] * 3,
            'account_type': ['Official', 'Emergency', 'Citizen'],
            'username': ['@QatarMet', '@QRCS', '@DohaResident'],
            'message': [
                "Warning: " + response_text.split('\n')[0],
                "Emergency teams deployed to affected areas",
                "Conditions deteriorating in my area"
            ],
            'location': ['Doha'] * 3,
            'trust_score': [0.9, 0.95, 0.7],
            'verified': [True, True, False],
            'engagement': [500, 300, 200]
        })
        st.session_state.updates = pd.concat([new_updates, st.session_state.updates])
        
        # Update shelter occupancy
        st.session_state.shelters['current'] += np.random.randint(50, 200, size=len(st.session_state.shelters))
        st.session_state.shelters['current'] = st.session_state.shelters['current'].clip(0, st.session_state.shelters['capacity'])
        
        # Update resources
        st.session_state.resources['water_supply'] *= 0.8
        st.session_state.resources['food_supply'] *= 0.8
        st.session_state.resources['last_updated'] = datetime.now().strftime('%Y-%m-%d %H:%M')
        
        return True, "Scenario data updated successfully"
    except Exception as e:
        return False, f"Error processing scenario: {str(e)}"

def generate_scenario(prompt):
    """Generate scenario using LLM"""
    try:
        messages = [
            {"role": "system", "content": """You are managing a crisis simulation system in Qatar. 
            Generate a detailed emergency scenario response including disaster details, impacts, 
            and social media reactions. Focus on realistic details and practical impacts."""},
            {"role": "user", "content": prompt}
        ]
        
        response = groq_client.chat.completions.create(
            messages=messages,
            model="mixtral-8x7b-32768",
            temperature=0.7,
            max_tokens=1000
        )
        
        success, message = process_llm_response(response.choices[0].message.content)
        return success, message, response.choices[0].message.content
        
    except Exception as e:
        return False, f"Error generating scenario: {str(e)}", None

# Main interface
st.markdown("""
    <div class="title-block">
        <h1>🐜 ANTNA Admin</h1>
        <p><span class="status-indicator status-active"></span>Crisis Simulation Control</p>
    </div>
""", unsafe_allow_html=True)

# Create tabs
tab1, tab2 = st.tabs(["💭 Scenario Generator", "📊 Current Data"])

# Scenario Generator Tab
with tab1:
    st.markdown("<h2>💭 Generate Emergency Scenario</h2>", unsafe_allow_html=True)
    
    prompt = st.text_area(
        "Describe the emergency scenario",
        placeholder="Example: A severe sandstorm is approaching Doha with winds exceeding 80km/h. Visibility is dropping rapidly...",
        height=150
    )
    
    if st.button("Generate Scenario"):
        if prompt:
            with st.spinner("Processing scenario..."):
                success, message, response = generate_scenario(prompt)
                if success:
                    st.success(message)
                    with st.expander("View LLM Response"):
                        st.write(response)
                else:
                    st.error(message)
        else:
            st.warning("Please enter a scenario description")

# Data Viewer Tab
with tab2:
    st.markdown("<h2>📊 Current Simulation Data</h2>", unsafe_allow_html=True)
    
    # Disasters
    st.markdown("<h3>Active Disasters</h3>", unsafe_allow_html=True)
    st.dataframe(st.session_state.disasters, use_container_width=True)
    
    # Shelters
    st.markdown("<h3>Shelter Status</h3>", unsafe_allow_html=True)
    st.dataframe(st.session_state.shelters, use_container_width=True)
    
    # Resources
    st.markdown("<h3>Resource Levels</h3>", unsafe_allow_html=True)
    st.dataframe(st.session_state.resources, use_container_width=True)
    
    # Social Updates
    st.markdown("<h3>Recent Updates</h3>", unsafe_allow_html=True)
    st.dataframe(
        st.session_state.updates.sort_values('timestamp', ascending=False),
        use_container_width=True
    )

    if st.button("Reset Simulation Data"):
        del st.session_state.disasters
        del st.session_state.shelters
        del st.session_state.resources
        del st.session_state.updates
        init_session_state()
        st.success("Simulation data reset to default values")

# Export data function for app.py to use
def get_simulation_data():
    return {
        'disasters': st.session_state.disasters,
        'shelters': st.session_state.shelters,
        'resources': st.session_state.resources,
        'updates': st.session_state.updates
    }

if __name__ == "__main__":
    st.session_state.setdefault('simulation_active', True)
