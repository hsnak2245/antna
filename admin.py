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
    
    # Disastersimport streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import numpy as np
from groq import Groq
import json
import warnings

warnings.filterwarnings('ignore')

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

def generate_disaster_data(groq_client, scenario_prompt):
    """Generate structured disaster alerts data"""
    messages = [
        {"role": "system", "content": """You are a disaster data generator for Qatar's emergency management system. 
        Generate exactly 10 emergency alerts as a JSON array. Each alert must have these exact fields and follow these rules:

        Fields required for each alert:
        {
            "type": "one of [Sandstorm, Heat Wave, Flash Flood, Dust Storm, Strong Winds, Thunderstorm]",
            "severity": "one of [Low, Medium, High]",
            "location": "specific Qatar location like Doha, Al Wakrah, Al Khor, etc.",
            "time": "current time in format YYYY-MM-DD HH:MM",
            "description": "detailed 20-word description of the specific alert"
        }

        Rules:
        - Generate exactly 10 alerts
        - Mix different types and severities
        - Use realistic Qatar locations
        - Make descriptions specific and detailed
        - All alerts should be related to the main scenario
        
        Format the output as a proper JSON array that can be parsed."""},
        {"role": "user", "content": f"Generate 10 structured alerts based on this scenario: {scenario_prompt}"}
    ]
    
    try:
        response = groq_client.chat.completions.create(
            messages=messages,
            model="mixtral-8x7b-32768",
            temperature=0.7,
            max_tokens=1000
        )
        alerts = json.loads(response.choices[0].message.content)
        disasters_df = pd.DataFrame(alerts)
        return disasters_df
    except Exception as e:
        st.error(f"Error generating disaster data: {str(e)}")
        return pd.DataFrame()

def generate_resource_data(groq_client, scenario_prompt):
    """Generate structured facility resource data"""
    messages = [
        {"role": "system", "content": """You are a facility resource manager for Qatar's emergency management system. 
        Generate exactly 10 facility status reports as a JSON array. Each facility must have these exact fields and follow these rules:

        Fields required for each facility:
        {
            "facility": "name of hospital, stadium, or shelter in Qatar",
            "water": "water supply (1000-10000)",
            "food": "food supply (500-5000)",
            "medical": "medical supplies percentage (0-100)",
            "beds": "total bed capacity (100-1000)",
            "current_occupancy": "current occupants (must be less than beds)",
            "last_updated": "current time in format YYYY-MM-DD HH:MM"
        }

        Rules:
        - Generate exactly 10 facilities
        - Include mix of hospitals, stadiums, and shelters
        - Use realistic Qatar facility names
        - Numbers must be within specified ranges
        - Current occupancy must be less than total beds
        - Resource levels should reflect the scenario impact
        
        Format the output as a proper JSON array that can be parsed."""},
        {"role": "user", "content": f"Generate 10 structured facility reports based on this scenario: {scenario_prompt}"}
    ]
    
    try:
        response = groq_client.chat.completions.create(
            messages=messages,
            model="mixtral-8x7b-32768",
            temperature=0.7,
            max_tokens=1000
        )
        resources = json.loads(response.choices[0].message.content)
        resources_df = pd.DataFrame(resources)
        return resources_df
    except Exception as e:
        st.error(f"Error generating resource data: {str(e)}")
        return pd.DataFrame()

def generate_social_updates(groq_client, scenario_prompt):
    """Generate structured social media updates"""
    messages = [
        {"role": "system", "content": """You are a social media feed generator for Qatar's emergency management system. 
        Generate exactly 10 social media updates as a JSON array. Each update must have these exact fields and follow these rules:

        Fields required for each update:
        {
            "source_type": "one of [Official, Healthcare, Emergency, Media, Citizen]",
            "username": "Twitter handle starting with @",
            "message": "the social media update content",
            "location": "specific Qatar location",
            "verified": "boolean true/false",
            "trust_score": "number between 0.0 and 1.0",
            "timestamp": "current time in format YYYY-MM-DD HH:MM",
            "engagement": "number between 100 and 5000"
        }

        Rules:
        - Generate exactly 10 updates
        - Mix different source types
        - Official sources should have higher trust scores
        - Include both verified and unverified accounts
        - Messages should be realistic and specific
        - All updates should relate to the scenario
        
        Format the output as a proper JSON array that can be parsed."""},
        {"role": "user", "content": f"Generate 10 structured social media updates based on this scenario: {scenario_prompt}"}
    ]
    
    try:
        response = groq_client.chat.completions.create(
            messages=messages,
            model="mixtral-8x7b-32768",
            temperature=0.7,
            max_tokens=1000
        )
        updates = json.loads(response.choices[0].message.content)
        updates_df = pd.DataFrame(updates)
        return updates_df
    except Exception as e:
        st.error(f"Error generating social updates: {str(e)}")
        return pd.DataFrame()

def process_scenario(prompt, groq_client):
    """Process scenario and generate all required data"""
    try:
        with st.spinner("Generating disaster alerts..."):
            disasters_df = generate_disaster_data(groq_client, prompt)
            if not disasters_df.empty:
                st.session_state.disasters = disasters_df
                st.success("✅ Disaster alerts generated!")
        
        with st.spinner("Generating resource data..."):
            resources_df = generate_resource_data(groq_client, prompt)
            if not resources_df.empty:
                st.session_state.resources = resources_df
                st.success("✅ Resource data generated!")
        
        with st.spinner("Generating social updates..."):
            updates_df = generate_social_updates(groq_client, prompt)
            if not updates_df.empty:
                st.session_state.updates = updates_df
                st.success("✅ Social updates generated!")
        
        return True, "Scenario data generated successfully!"
    except Exception as e:
        return False, f"Error processing scenario: {str(e)}"

# Initialize session state with empty DataFrames
def init_session_state():
    if 'disasters' not in st.session_state:
        st.session_state.disasters = pd.DataFrame({
            'type': ['No Active Disasters'],
            'severity': ['Low'],
            'location': ['N/A'],
            'time': [datetime.now().strftime('%Y-%m-%d %H:%M')],
            'description': ['No active disasters or emergencies at this time.']
        })
    
    if 'resources' not in st.session_state:
        st.session_state.resources = pd.DataFrame({
            'facility': ['Hamad General Hospital'],
            'water': [5000],
            'food': [2500],
            'medical': [80],
            'beds': [500],
            'current_occupancy': [200],
            'last_updated': [datetime.now().strftime('%Y-%m-%d %H:%M')]
        })
    
    if 'updates' not in st.session_state:
        st.session_state.updates = pd.DataFrame({
            'source_type': ['Official'],
            'username': ['@QatarAlert'],
            'message': ['Systems operational. Monitoring for emergencies.'],
            'location': ['Doha'],
            'verified': [True],
            'trust_score': [1.0],
            'timestamp': [datetime.now().strftime('%Y-%m-%d %H:%M')],
            'engagement': [100]
        })

# Export data function for app.py
def get_simulation_data():
    return {
        'disasters': st.session_state.disasters,
        'resources': st.session_state.resources,
        'updates': st.session_state.updates
    }

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

    # Scenario Generator Tab
    with tab1:
        st.markdown("<h2>💭 Generate Emergency Scenario</h2>", unsafe_allow_html=True)
        
        # Example scenarios dropdown
        example_scenarios = [
            "Select an example or write your own...",
            "A severe sandstorm is approaching Doha with winds exceeding 80km/h. Visibility is dropping rapidly.",
            "A heatwave has hit Qatar with temperatures reaching 50°C, causing widespread power outages.",
            "Heavy rainfall has caused flash flooding in Al Wakrah, with water levels rising rapidly.",
            "Multiple simultaneous dust storms are affecting northern Qatar regions."
        ]
        
        selected_scenario = st.selectbox("Example Scenarios", example_scenarios)
        
        prompt = st.text_area(
            "Describe the emergency scenario",
            value=selected_scenario if selected_scenario != example_scenarios[0] else "",
            placeholder="Describe the emergency scenario in detail...",
            height=150
        )
        
        col1, col2 = st.columns([1, 5])
        with col1:
            if st.button("Generate", type="primary"):
                if prompt and prompt != example_scenarios[0]:
                    success, message = process_scenario(prompt, groq_client)
                    if success:
                        st.balloons()
                else:
                    st.warning("Please enter or select a scenario description")
        
        with col2:
            if st.button("Reset Data"):
                init_session_state()
                st.success("Data reset to initial state")

    # Data Viewer Tab
    with tab2:
        st.markdown("<h2>📊 Current Simulation Data</h2>", unsafe_allow_html=True)
        
        # Disasters DataFrame
        st.markdown("<h3>🚨 Active Disasters</h3>", unsafe_allow_html=True)
        st.dataframe(
            st.session_state.disasters,
            use_container_width=True,
            column_config={
                "type": "Disaster Type",
                "severity": "Severity",
                "location": "Location",
                "time": "Time",
                "description": st.column_config.TextColumn("Description", width="large")
            }
        )
        
        # Resources DataFrame
        st.markdown("<h3>🏥 Resource Levels</h3>", unsafe_allow_html=True)
        st.dataframe(
            st.session_state.resources,
            use_container_width=True,
            column_config={
                "facility": "Facility Name",
                "water": "Water Supply",
                "food": "Food Supply",
                "medical": "Medical Supplies %",
                "beds": "Total Beds",
                "current_occupancy": "Current Occupancy",
                "last_updated": "Last Updated"
            }
        )
        
        # Social Updates DataFrame
        st.markdown("<h3>📱 Social Updates</h3>", unsafe_allow_html=True)
        st.dataframe(
            st.session_state.updates.sort_values('timestamp', ascending=False),
            use_container_width=True,
            column_config={
                "source_type": "Source",
                "username": "Username",
                "message": st.column_config.TextColumn("Message", width="large"),
                "location": "Location",
                "verified": "Verified",
                "trust_score": "Trust Score",
                "timestamp": "Time",
                "engagement": "Engagement"
            }
        )

if __name__ == "__main__":
    main()
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
