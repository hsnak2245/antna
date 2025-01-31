'''# If the query relates to medical supplies, show a map
        if "medical supplies" in query.lower():
            # Simulate user's current location (replace with actual user location if available)
            user_location = [25.3548, 51.1839]  # Example: Doha city center
            
            # Find nearest shelter
            nearest_shelter = find_nearest_shelter(shelters_df, user_location, query_type="medical supplies")
            
            try:
                # Request route from ORS
                coordinates = [
                    (user_location[1], user_location[0]),  # (lon, lat) for user location
                    (nearest_shelter['lon'], nearest_shelter['lat'])  # (lon, lat) for shelter
                ]
                route = ors_client.directions(
                    coordinates=coordinates,
                    profile='driving-car',
                    format='geojson',
                    radiuses=[1000, 1000]  # Increase search radius to 1000 meters
                )
                route_coords = route['features'][0]['geometry']['coordinates']
                
                # Convert coordinates for Folium (lon, lat) -> (lat, lon)
                route_coords = [[coord[1], coord[0]] for coord in route_coords]
            except Exception as e:
                st.error(f"Error fetching route: {e}")
                # Fallback to straight line
                route_coords = [
                    [user_location[0], user_location[1]],
                    [nearest_shelter['lat'], nearest_shelter['lon']]
                ]

            # Generate a map with the route
            m = folium.Map(location=user_location, zoom_start=12)
            
            # Add user location marker
            folium.Marker(
                location=user_location,
                popup="Your Location",
                icon=folium.Icon(color='red', icon='info-sign')
            ).add_to(m)
            
            # Add nearest shelter marker
            folium.Marker(
                location=[nearest_shelter['lat'], nearest_shelter['lon']],
                popup=f"<b>{nearest_shelter['name']}</b>",
                icon=folium.Icon(color='blue', icon='info-sign')
            ).add_to(m)
            
            # Draw the route
            folium.PolyLine(
                locations=route_coords,
                color='green',
                weight=5,
                tooltip="Route to Shelter"
            ).add_to(m)
            
            # Display the map
            st.markdown("<h4>📍 Route to Nearest Shelter with Medical Supplies</h4>", unsafe_allow_html=True)
            st_folium(m, width=600, height=400)
            
            
            
            
            
            
            add a modern ui css for this, just give the added css element for this:

audio_bytes = audio_recorder(
            text="",  # Minimal text
            recording_color="white",
            neutral_color="red"
        )
            '''