# app.py
import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from datetime import datetime, timedelta
from groq import Groq
import numpy as np
from audio_recorder_streamlit import audio_recorder
import tempfile
import os
import warnings
import openrouteservice
from data import generate_data
import geocoder
warnings.filterwarnings('ignore')


# Page config must be the first Streamlit command
st.set_page_config(
    page_title="ANTNA",
    page_icon="🐜",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': "ANTNA - Crisis Management System 🐜"
    }
)

# Near the top of your app.py, after the imports
def load_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
load_css('styles.css')

# Define affected locations in Turkey
turkey_eq_locations = {
    "Gaziantep City Center": [37.0662, 37.3833],
    "Kahramanmaraş City Center": [37.5753, 36.9228],
    "Antakya City Center (Hatay)": [36.2025, 36.1603],
    "Adıyaman City Center": [37.7648, 38.2786],
    "Malatya City Center": [38.3552, 38.3095],
    "Iskenderun Port Area": [36.5817, 36.1650],
    "Nurdağı District (Gaziantep)": [37.1683, 36.7367],
    "Hatay Airport": [36.3622, 36.2822],
    "Adana Relief Coordination Center": [37.0017, 35.3289],
    "Osmaniye Temporary Shelter Camp": [37.0742, 36.2468],
    "Gaziantep Castle Area": [37.0658, 37.3833],
    "Kahramanmaraş Sütçü İmam University": [37.8010, 36.9250],
    "Hatay Medical Center": [36.5200, 36.3850],
    "Malatya Battalgazi District": [38.4000, 38.3667],
    "Adıyaman Fault Line Zone": [37.8500, 38.2833]
}

# Initialize keys
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
ORS_API_KEY = st.secrets["ORS_API_KEY"]
ors_client = openrouteservice.Client(key=ORS_API_KEY)  # Initialize ORS client
groq_client = Groq(api_key=GROQ_API_KEY)

# Get all dataframes
alerts_df, shelters_df, resources_df, social_updates_df = generate_data()

def find_nearest_shelter(shelters_df, user_location):
    """
    Find the nearest shelter to the user's location based on query type.
    """
    # Simulate finding the nearest shelter by calculating distances
    shelters_df["distance"] = shelters_df.apply(
        lambda row: np.sqrt((row["lat"] - user_location[0])**2 + (row["lon"] - user_location[1])**2),
        axis=1
    )
    nearest_shelter = shelters_df.loc[shelters_df["distance"].idxmin()]
    return nearest_shelter

# Voice transcription function
def process_voice_input(audio_bytes):
    if not audio_bytes:
        return None
    
    with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_audio:
        try:
            temp_audio.write(audio_bytes)
            temp_audio_path = temp_audio.name
            
            with open(temp_audio_path, 'rb') as audio_file:
                response = groq_client.audio.transcriptions.create(
                    file=audio_file,
                    model="whisper-large-v3"
                )
            return response.text
        except Exception as e:
            st.error(f"Transcription error: {str(e)}")
            return None
        finally:
            try:
                os.remove(temp_audio_path)
            except:
                pass

# RAG simulation
def process_query_with_rag(query, social_updates_df):
    try:
        relevant_updates = social_updates_df[
            social_updates_df['message'].str.contains('|'.join(query.split()), case=False, na=False)
        ]
        
        context = "\n".join(relevant_updates['message'].tolist())
        
        messages = [
            {"role": "system", "content": """You are ANTNA, an AI assistant for emergency management in turkey earthquake. 
             Provide clear, accurate information based on available data and social media updates."""},
            {"role": "user", "content": f"Context from verified social media:\n{context}\n\nUser Question: {query}"}
        ]
        
        try:
            response = groq_client.chat.completions.create(
                messages=messages,
                model="mixtral-8x7b-32768",
                temperature=0.7,
                max_tokens=500,
                top_p=0.9
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"AI processing error: {str(e)}"
            
    except Exception as e:
        return f"Error processing query: {str(e)}"

def main():
    alerts_df, shelters_df, resources_df, social_updates_df = generate_data()

  
        
    st.markdown("""
            <div class="title-block">
                <h1><center>ANTNA</center></h1>
            </div>
        """, unsafe_allow_html=True)

    # Main tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Home", "⚠️ Alerts", "🏥 Centers", "📱 Updates", "✅ Prep"])
    
    
    with tab1:
        user_query = st.text_input('',placeholder= "Ask ANTNA")
        if user_query:
            with st.spinner("Processing..."):
                
                response = process_query_with_rag(user_query, social_updates_df)
                
                # Display the AI response
                st.markdown("""
                    <div class="ai-response">
                        <strong>ANTNA:</strong><br>{response}
                    </div>
                """, unsafe_allow_html=True)
        # Display essential information in a compact grid
        col1, col2, col3 = st.columns(3)
            
        with col1:
            # Nearest Shelter Card
            g = geocoder.ip('me')
            user_location = [g.latlng[0], g.latlng[1]] if g.latlng else [37.0662, 37.3833]
            nearest_shelter = find_nearest_shelter(shelters_df, user_location)
            
            st.markdown(f"""
            <div class="info-card">
                <div class="card-header">
                    <span class="status-indicator status-active"></span>
                    🏥 Nearest Shelter
                </div>
                <div class="card-content">
                    <strong>{nearest_shelter['name']}</strong>
                    <p style="margin: 10px 0;">
                        <i class="fas fa-map-marker-alt"></i> Distance: {nearest_shelter['distance']:.2f} km
                    </p>
                    <div style="font-size: 0.8rem; color: #666;">
                        Updated {time.strftime('%H:%M')}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            # Latest Alert Card
            latest_alert = alerts_df.iloc[0]
            alert_status = "danger" if latest_alert['type'].lower() == 'emergency' else "warning"
            
            st.markdown(f"""
            <div class="info-card">
                <div class="card-header">
                    <span class="status-indicator status-{alert_status}"></span>
                    ⚠️ Latest Alert
                </div>
                <div class="card-content">
                    <strong>{latest_alert['type']} Alert</strong>
                    <p style="margin: 10px 0;">
                        <i class="fas fa-location-dot"></i> {latest_alert['location']}
                    </p>
                    <div style="font-size: 0.8rem; color: #666;">
                        Issued {time.strftime('%H:%M')}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            # Recent Update Card
            recent_update = social_updates_df.iloc[0]
            
            st.markdown(f"""
            <div class="info-card">
                <div class="card-header">
                    <span class="status-indicator status-active"></span>
                    📱 Recent Update
                </div>
                <div class="card-content">
                    <strong>{recent_update['username']}</strong>
                    <p style="margin: 10px 0;">
                        {recent_update['message'][:100]}{'...' if len(recent_update['message']) > 100 else ''}
                    </p>
                    <div style="font-size: 0.8rem; color: #666;">
                        Posted {time.strftime('%H:%M')}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    with tab2:
        st.markdown("<h3>⚠️ Active Alerts</h3>", unsafe_allow_html=True)
        for _, alert in alerts_df.iterrows():
            severity_color = {
                "High": "🔴", 
                "Medium": "🟡",
                "Low": "🟢"
            }.get(alert["severity"], "⚪")
            
            st.markdown(f"""
                <div class="alert-box">
                    <h4>{severity_color} {alert['type']} Alert</h4>
                    <p>📍 <b>Location:</b> {alert['location']}</p>
                    <p>🕒 <b>Time:</b> {alert['time']}</p>
                    <p>⚠️ <b>Severity:</b> {alert['severity']}</p>
                    <p>ℹ️ <b>Details:</b> {alert['description']}</p>
                </div>
            """, unsafe_allow_html=True)
    
    # Centers Tab
    # Centers Tab
    with tab3:
        st.markdown("<h2>🏥 Critical Locations</h2>", unsafe_allow_html=True)
        
        # Get the data
        _, shelters_df, resources_df, _ = generate_data()
        
        # Define common locations in Doha
    # Define affected locations in Turkey
        turkey_eq_locations = {
            "Gaziantep City Center": [37.0662, 37.3833],
            "Kahramanmaraş City Center": [37.5753, 36.9228],
            "Antakya City Center (Hatay)": [36.2025, 36.1603],
            "Adıyaman City Center": [37.7648, 38.2786],
            "Malatya City Center": [38.3552, 38.3095],
            "Iskenderun Port Area": [36.5817, 36.1650],
            "Nurdağı District (Gaziantep)": [37.1683, 36.7367],
            "Hatay Airport": [36.3622, 36.2822],
            "Adana Relief Coordination Center": [37.0017, 35.3289],
            "Osmaniye Temporary Shelter Camp": [37.0742, 36.2468],
            "Gaziantep Castle Area": [37.0658, 37.3833],
            "Kahramanmaraş Sütçü İmam University": [37.8010, 36.9250],
            "Hatay Medical Center": [36.5200, 36.3850],
            "Malatya Battalgazi District": [38.4000, 38.3667],
            "Adıyaman Fault Line Zone": [37.8500, 38.2833]
        }
        # Create subtabs
        list_tab, map_tab = st.tabs(["📋 List View", "🗺️ Map View"])
        
        # List View Tab
        with list_tab:
            for idx, location in shelters_df.iterrows():
                resources = resources_df[resources_df['location'] == location['name']].iloc[0]
                occupancy = (location['current'] / location['capacity']) * 100
                st.markdown(f"""
                    <div class="stats-box">
                    <h3>{location['name']}</h3>
                    <p>🏥 Type: {location['type']}</p>
                    <p>📞 Contact: {location['contact']}</p>
                    <p>👥 Occupancy: {location['current']}/{location['capacity']} 
                    ({occupancy:.1f}%)</p>
                    <p>💧 Water: {resources['water_supply']} units</p>
                    <p>🍲 Food: {resources['food_supply']} units</p>
                    <p>🏥 Medical: {resources['medical_kits']} kits</p>
                    <p>🕒 Updated: {resources['last_updated']}</p>
                    </div>
                """, unsafe_allow_html=True)
        
        # Map View Tab
        with map_tab:
            # Location Details Block (Top)
            st.markdown("<div class='location-details-container'>", unsafe_allow_html=True)
            
            # Type filter, location selector, current location, and route toggle
            col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
            
            with col1:
                location_type = st.selectbox(
                    "Filter by type",
                    options=['All'] + list(shelters_df['type'].unique()),
                    key='map_type_filter'
                )
            
            filtered_df = shelters_df if location_type == 'All' else shelters_df[shelters_df['type'] == location_type]
            
            with col2:
                selected_location = st.selectbox(
                    "Select facility",
                    options=filtered_df['name'].tolist(),
                    key='map_location_select'
                )
            
            with col3:
                current_location = st.selectbox(
                    "Your location",
                    options=list(turkey_eq_locations.keys()),
                    key='current_location_select'
                )
                
            with col4:
                show_route = st.checkbox("Show route", value=False)
            
            # Get selected location details
            location_info = shelters_df[shelters_df['name'] == selected_location].iloc[0]
            resources_info = resources_df[resources_df['location'] == selected_location].iloc[0]
            
            # Display compact location details with status
            occupancy_percentage = (location_info['current'] / location_info['capacity']) * 100
            status_class = (
                "status-active" if occupancy_percentage < 60 
                else "status-busy" if occupancy_percentage < 90 
                else "status-full"
            )
            
            st.markdown(f"""
                <div class="stats-box {status_class}">
                    <div style="display: flex; justify-content: space-between; align-items: top;">
                        <div style="flex: 2;">
                            <h3>{location_info['name']}</h3>
                            <p>🏥 Type: {location_info['type']} | 📞 {location_info['contact']}</p>
                            <p>👥 Occupancy: {location_info['current']}/{location_info['capacity']} 
                            ({occupancy_percentage:.1f}%)</p>
                            <p>💧 Water: {resources_info['water_supply']} units | 
                            🍲 Food: {resources_info['food_supply']} units | 
                            🏥 Medical: {resources_info['medical_kits']} kits</p>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            # Map Block (Bottom)
            m = folium.Map(
                location=turkey_eq_locations[current_location],  # Center map on selected current location
                zoom_start=12,
                tiles="cartodbpositron"
            )
            
            # Add markers for all locations
            for idx, location in filtered_df.iterrows():
                color = {
                    'Primary': 'red',
                    'Secondary': 'blue'
                }.get(location['type'], 'gray')
                
                occupancy = (location['current'] / location['capacity']) * 100
                resources = resources_df[resources_df['location'] == location['name']].iloc[0]
                
                popup_content = f"""
                    <div style="width: 200px">
                        <h4>{location['name']}</h4>
                        <p><b>Type:</b> {location['type']}</p>
                        <p><b>Contact:</b> {location['contact']}</p>
                        <p><b>Occupancy:</b> {occupancy:.1f}%</p>
                        <p><b>Resources:</b></p>
                        <ul>
                            <li>Water: {resources['water_supply']} units</li>
                            <li>Food: {resources['food_supply']} units</li>
                            <li>Medical: {resources['medical_kits']} kits</li>
                        </ul>
                    </div>
                """
                
                marker = folium.Marker(
                    location=[location['lat'], location['lon']],
                    popup=folium.Popup(popup_content, max_width=300),
                    icon=folium.Icon(color=color, icon='info-sign'),
                )
                marker.add_to(m)
            
            # Add routing if requested
            if show_route:
                try:
                    # Get coordinates for selected current location
                    user_location = turkey_eq_locations[current_location]
                    
                    # Add user location marker
                    folium.Marker(
                        location=user_location,
                        popup=f"Your Location ({current_location})",
                        icon=folium.Icon(color='green', icon='info-sign')
                    ).add_to(m)

                    # Calculate route using OpenRouteService
                    coordinates = [
                        [user_location[1], user_location[0]],  # Current location (lon, lat)
                        [location_info['lon'], location_info['lat']]  # Destination (lon, lat)
                    ]
                    
                    route = ors_client.directions(
                        coordinates=coordinates,
                        profile='driving-car',
                        format='geojson'
                    )

                    # Extract and convert route coordinates
                    route_coords = [[coord[1], coord[0]] for coord in route['features'][0]['geometry']['coordinates']]
                    
                    # Add route to map
                    folium.PolyLine(
                        locations=route_coords,
                        weight=4,
                        color='green',
                        opacity=0.8,
                        tooltip='Route to Location'
                    ).add_to(m)

                    # Fit map bounds to show route
                    m.fit_bounds([user_location, [location_info['lat'], location_info['lon']]])
                    
                    # Show route details
                    duration_minutes = route['features'][0]['properties']['segments'][0]['duration'] / 60
                    distance_km = route['features'][0]['properties']['segments'][0]['distance'] / 1000
                    
                    st.markdown(f"""
                        <div class="route-info">
                            <h4>🚗 Route Information:</h4>
                            <p>📍 From: {current_location}</p>
                            <p>🎯 To: {location_info['name']}</p>
                            <p>⏱️ Estimated Time: {duration_minutes:.1f} minutes</p>
                            <p>📏 Distance: {distance_km:.1f} km</p>
                        </div>
                    """, unsafe_allow_html=True)
                    
                except Exception as e:
                    st.error(f"Error calculating route: {str(e)}")
            
            # Display the map
            st_folium(m, height=500)

    # Inside Tab 3 (Social Updates)
    with tab4:
        st.markdown("<h2>📱 Live Updates</h2>", unsafe_allow_html=True)
        
        col1, col2 = st.columns([2,3])
        with col1:
            min_trust_score = st.slider("Trust Score Filter", 0.0, 1.0, 0.7, 0.1)
        with col2:
            account_types = st.multiselect(
                "Source Filter",
                options=social_updates_df['account_type'].unique(),
                default=social_updates_df['account_type'].unique()
            )
        
        # Filter updates
        filtered_updates = social_updates_df[
            (social_updates_df['trust_score'] >= min_trust_score) &
            (social_updates_df['account_type'].isin(account_types))
        ].sort_values(['timestamp', 'trust_score'], ascending=[False, False])
        
        # Display updates
        for _, update in filtered_updates.iterrows():
            # Determine trust class and verification status
            trust_class = {
                True: "trust-high" if update['trust_score'] >= 0.9 else "trust-medium",
                False: "trust-low"
            }[update['trust_score'] >= 0.7]
            
            verification_badge = "verified" if update['verified'] else "unverified"
            
            # Select badge color based on account type and verification
            badge_color = {
                'Official': '#00ff9d',
                'Healthcare': '#00ff9d',
                'Emergency': '#00ff9d',
                'Media': '#ffbe0b',
                'Citizen': '#888888'
            }.get(update['account_type'], '#888888')
            
            st.markdown(f"""
                <div class='social-update {trust_class}'>
                    <div class="update-header">
                        <div class="account-info">
                            <strong style="color: {badge_color}">{update['account_type']}</strong>
                            <span class="username">{update['username']}</span>
                            <span class="badge {verification_badge}">
                                {' ✓' if update['verified'] else '✕'}
                            </span>
                        </div>
                    </div>
                    <div class="update-content">
                        {update['message']}
                    </div>
                    <div class="update-meta">
                        <span class="meta-item">📍 {update['location']}</span>
                        <span class="meta-separator">|</span>
                        <span class="meta-item">💯 Trust: {update['trust_score']:.2f}</span>
                        <span class="meta-separator">|</span>
                        <span class="meta-item">👥 {update['engagement']}</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)


    
    # Preparation Tab
    with tab5:
        st.markdown("<h2>✅ Emergency Preparedness</h2>", unsafe_allow_html=True)
        
        # Checklist in a clean container
        st.markdown("<h3>📋 Essential Items</h3>", unsafe_allow_html=True)
        
        # Initialize checklist items
        checklist_data = {
            "Item": [
                "Water (5L per person per day)",
                "Non-perishable food",
                "First aid kit",
                "Portable fan/cooling devices",
                "Dust masks",
                "Emergency contact list",
                "Portable radio",
                "Power bank",
                "Important documents in waterproof container",
                "Sand/dust protection for electronics"
            ],
            "Checked": [False] * 10
        }
        
        checklist_df = pd.DataFrame(checklist_data)
        
        # Display checklist items dynamically
        for index, row in checklist_df.iterrows():
            checklist_df.at[index, "Checked"] = st.checkbox(row["Item"], value=row["Checked"])
        
        # Readiness Score with visual indicator
        readiness = checklist_df["Checked"].mean() * 100
        st.markdown("<h3>🎯 Readiness Score</h3>", unsafe_allow_html=True)
        st.progress(readiness / 100)
        st.markdown(f"""
            <div class="stats-box" style="text-align: center;">
                <h2 style="color: {'#00ff9d' if readiness > 70 else '#ffbe0b' if readiness > 40 else '#ff006e'};">
                    {readiness:.1f}%
                </h2>
                <p>Preparedness Level</p>
            </div>
        """, unsafe_allow_html=True)

        # Emergency Contacts
        st.markdown("<h3>☎️ Emergency Contacts</h3>", unsafe_allow_html=True)
        st.markdown("""
            <div class="stats-box">
                <p>🚔 <b>Police:</b> 999</p>
                <p>🚑 <b>Ambulance:</b> 999</p>
                <p>🚒 <b>Civil Defence:</b> 999</p>
                <p>🏥 <b>Hamad Hospital:</b> 4439 5777</p>
                <p>⚡ <b>Kahramaa (Utilities):</b> 991</p>
            </div>
        """, unsafe_allow_html=True)
        
        # Quick Tips
        with st.expander("📖 Quick Emergency Guidelines"):
            st.markdown("""
                <div class="stats-box">
                    <h4>Before Emergency:</h4>
                    - Keep important documents in a waterproof container<br>
                    - Maintain emergency supplies<br>
                    - Learn evacuation routes<br><br>
                    
                    <h4>During Emergency:</h4>
                    - Stay informed through official channels<br>
                    - Follow evacuation orders immediately<br>
                    - Help others if safe to do so<br><br>
                    
                    <h4>After Emergency:</h4>
                    - Check on family and neighbors<br>
                    - Document any damage<br>
                    - Follow official recovery guidance
                </div>
            """, unsafe_allow_html=True)
        


if __name__ == "__main__":
    main()
