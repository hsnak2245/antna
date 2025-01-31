import pandas as pd
from datetime import datetime, timedelta

def generate_data():
    # Base date for the February 6, 2023 earthquake
    base_date = datetime(2023, 2, 6, 4, 17)  # Actual earthquake time
    
    # Alerts data
    alerts_data = {
        'type': ['Earthquake', 'Aftershock', 'Building Collapse', 'Infrastructure Damage', 'Landslide'],
        'severity': ['High', 'High', 'Medium', 'Medium', 'Low'],
        'location': ['Gaziantep', 'Kahramanmaraş', 'Hatay', 'Adıyaman', 'Malatya'],
        'time': [
            (base_date + timedelta(minutes=x*45)).strftime('%Y-%m-%d %H:%M')
            for x in range(5)
        ],
        'description': [
            'Major earthquake measuring 7.8 magnitude',
            'Powerful 6.7 magnitude aftershock reported',
            'Multiple buildings collapsed in city center',
            'Critical infrastructure damage reported',
            'Landslide risk in mountainous areas'
        ]
    }
    alerts_df = pd.DataFrame(alerts_data)

    # Shelters data
    shelters_data = {
        'name': [
            'Gaziantep Olympic Stadium',
            'Kahramanmaraş University Shelter',
            'Hatay International Convention Center',
            'Adıyaman Sports Complex',
            'Malatya Emergency Shelter'
        ],
        'capacity': [1500, 800, 1200, 600, 900],
        'current': [1345, 623, 987, 450, 782],
        'lat': [37.0662, 37.5753, 36.2025, 37.7648, 38.3552],
        'lon': [37.3833, 36.9228, 36.1603, 38.2786, 38.3095],
        'type': ['Emergency', 'Field Hospital', 'Emergency', 'Temporary', 'Emergency'],
        'contact': [f'+90-342-511-{1000+x}' for x in range(1, 6)]
    }
    shelters_df = pd.DataFrame(shelters_data)

    # Resources data
    resources_data = pd.DataFrame({
        'location': shelters_data['name'],
        'water_supply': [2500, 1800, 2200, 1500, 2000],
        'food_supply': [1800, 1200, 1500, 900, 1300],
        'medical_kits': [200, 150, 180, 100, 170],
        'generators': [25, 18, 22, 15, 20],
        'beds': [1200, 700, 1000, 500, 800],
        'last_updated': [(base_date + timedelta(hours=x)).strftime('%Y-%m-%d %H:%M') for x in range(5)]
    })
    resources_df = pd.DataFrame(resources_data)

    # Social updates data
    social_updates_data = {
        'timestamp': [(base_date + timedelta(minutes=x*20)).strftime('%Y-%m-%dT%H:%M:%S') for x in range(10)],
        'source': ['Twitter', 'Facebook', 'Twitter', 'Website', 'Twitter',
                  'Facebook', 'Twitter', 'Website', 'Twitter', 'Facebook'],
        'account_type': ['Government', 'Citizen', 'NGO', 'Government', 'Healthcare',
                        'Citizen', 'Press', 'NGO', 'Government', 'UN'],
        'username': ['@AFAD', '@HatayResident', '@AKUT', '@RedCrescentTR', '@SaglikBakanligi',
                    '@GaziantepCitizen', '@BBCBreaking', '@UNOCHA', '@Turkiye', '@WHO'],
        'message': [
            'Major earthquake strikes southern Turkey - rescue operations underway',
            'Building collapsed in Antakya! Need urgent help!',
            'AKUT search and rescue teams deployed to Hatay',
            'Emergency hotlines established: 112 and 154',
            'Mobile hospitals being set up in affected regions',
            'No electricity or water in Kahramanmaraş city center',
            'Death toll rises to over 4,000 across Turkey and Syria',
            'International rescue teams arriving at Istanbul Airport',
            'President declares state of emergency in 10 provinces',
            'WHO deploying emergency medical supplies via airlift'
        ],
        'location': ['Turkey']*3 + ['Nationwide', 'Turkey', 'Kahramanmaraş', 
                                  'Turkey', 'Istanbul', 'Turkey', 'Global'],
        'trust_score': [0.98, 0.65, 0.97, 0.99, 0.96, 0.60, 0.95, 0.94, 0.99, 0.97],
        'verified': [True, False, True, True, True, False, True, True, True, True],
        'engagement': [45200, 12450, 28900, 36700, 23400, 8450, 55700, 16700, 48900, 25600],
        'emergency_type': ['Earthquake', 'Collapse', 'Rescue', 'Emergency', 'Medical',
                          'Infrastructure', 'Casualty', 'International Aid', 
                          'Government', 'Medical']
    }
    social_updates_df = pd.DataFrame(social_updates_data)

    return alerts_df, shelters_df, resources_df, social_updates_df