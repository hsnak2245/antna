import pandas as pd
from datetime import datetime, timedelta

def generate_data():
    # Alerts data
    alerts_data = {
        'type': ['Sandstorm', 'Heat Wave', 'Flash Flood', 'Dust Storm', 'Strong Winds'],
        'severity': ['High', 'High', 'Medium', 'Medium', 'Low'],
        'location': ['Al Wakrah', 'Doha', 'Al Khor', 'Al Rayyan', 'Lusail'],
        'time': [
            (datetime.now() - timedelta(minutes=x*30)).strftime('%Y-%m-%d %H:%M')
            for x in range(5)
        ],
        'description': [
            'Severe sandstorm approaching with reduced visibility',
            'Extreme temperatures expected to reach 48°C',
            'Heavy rainfall may cause local flooding',
            'Moderate dust storm affecting visibility',
            'Strong winds expected up to 40km/h'
        ]
    }
    alerts_df = pd.DataFrame(alerts_data)

    # Shelters data
    shelters_data = {
        'name': [
            'Lusail Sports Arena', 'Al Thumama Stadium', 'Education City Stadium',
            'Al Bayt Stadium Complex', 'Khalifa International Stadium'
        ],
        'capacity': [800, 600, 500, 1000, 700],
        'current': [234, 156, 123, 445, 289],
        'lat': [25.430560, 25.230844, 25.311667, 25.652222, 25.263889],
        'lon': [51.488970, 51.532197, 51.424722, 51.487778, 51.448333],
        'type': ['Primary', 'Secondary', 'Primary', 'Primary', 'Secondary'],
        'contact': [f'+974-4000-{x}111' for x in range(1, 6)]
    }
    shelters_df = pd.DataFrame(shelters_data)

    # Resources data
    resources_data = pd.DataFrame({
        'location': shelters_data['name'],
        'water_supply': [1000, 800, 600, 1200, 900],
        'food_supply': [800, 600, 500, 1000, 700],
        'medical_kits': [50, 40, 30, 60, 45],
        'generators': [10, 8, 6, 12, 9],
        'beds': [500, 400, 300, 600, 450],
        'last_updated': [datetime.now().strftime('%Y-%m-%d %H:%M')] * 5
    })
    resources_df = pd.DataFrame(resources_data)

    # Social updates data
    social_updates_data = {
        'timestamp': [(datetime.now() - timedelta(minutes=x*15)).strftime('%Y-%m-%dT%H:%M:%S') for x in range(10)],
        'source': ['Twitter'] * 10,
        'account_type': ['Official', 'Citizen', 'Emergency', 'Official', 'Healthcare',
                        'Citizen', 'Official', 'Emergency', 'Official', 'Media'],
        'username': ['@QatarWeather', '@QatarResident1', '@QatarRedCrescent', 
                    '@QatarMOI', '@HamadMedical', '@DohaResident', '@QatarMet',
                    '@CivilDefenceQA', '@MunicipalityQA', '@QatarNews'],
        'message': [
            'Severe sandstorm warning for Al Wakrah region. Visibility reduced to 500m.',
            'Heavy sand in Al Wakrah area. Roads barely visible.',
            'Emergency teams deployed to Al Wakrah. Shelter available.',
            'Traffic diverted on Al Wakrah Road due to poor visibility.',
            'Al Wakrah Hospital ready to receive emergency cases.',
            'Temperature hitting 47°C in Doha. Multiple cases of heat exhaustion.',
            'Extreme heat warning: Temperature to reach 48°C in Doha.',
            'Flash flood warning for Al Khor. Emergency teams on high alert.',
            'Storm drains being cleared in Al Khor to prevent flooding.',
            'Live updates: Multiple weather-related incidents across Qatar.'
        ],
        'location': ['Al Wakrah']*4 + ['Doha']*3 + ['Al Khor']*2 + ['Qatar'],
        'trust_score': [0.95, 0.68, 0.98, 0.97, 0.96, 0.65, 0.99, 0.97, 0.94, 0.93],
        'verified': [True, False, True, True, True, False, True, True, True, True],
        'engagement': [1205, 342, 892, 1567, 723, 445, 2341, 1123, 567, 1892],
        'emergency_type': ['Sandstorm']*4 + ['Heat Wave']*3 + ['Flood']*2 + ['Multiple']
    }
    social_updates_df = pd.DataFrame(social_updates_data)

    return alerts_df, shelters_df, resources_df, social_updates_df