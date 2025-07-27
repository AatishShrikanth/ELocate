import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    # API Keys
    QLOO_API_KEY = os.getenv('QLOO_API_KEY')
    GOOGLE_PLACES_API_KEY = os.getenv('GOOGLE_PLACES_API_KEY')
    OPENWEATHER_API_KEY = os.getenv('OPENWEATHER_API_KEY')
    
    # AWS Configuration
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
    AWS_DEFAULT_REGION = os.getenv('AWS_DEFAULT_REGION', 'us-east-1')
    
    # API Endpoints
    QLOO_BASE_URL = "https://api.qloo.com/v1"
    OPENWEATHER_BASE_URL = "https://api.openweathermap.org/data/2.5"
    GOOGLE_PLACES_BASE_URL = "https://maps.googleapis.com/maps/api/place"
    
    # App Settings
    DEFAULT_RADIUS = 5000  # 5km radius for venue search
    MAX_RECOMMENDATIONS = 20
    
    # Budget Mapping
    BUDGET_MAPPING = {
        "$": 1,
        "$$": 2,
        "$$$": 3,
        "$$$$": 4
    }
    
    # Weather Thresholds
    WEATHER_THRESHOLDS = {
        'rain_threshold': 0.5,  # mm/h
        'temp_cold': 10,        # Celsius
        'temp_hot': 30,         # Celsius
        'wind_strong': 20       # km/h
    }
    
    # Entertainment Categories
    ENTERTAINMENT_CATEGORIES = [
        'restaurants', 'bars', 'movie_theater', 'museum', 'amusement_park',
        'bowling_alley', 'casino', 'night_club', 'shopping_mall', 'spa',
        'tourist_attraction', 'zoo', 'art_gallery', 'library', 'park'
    ]
    
    # AI Assistant Settings
    BEDROCK_MODEL_ID = 'anthropic.claude-3-haiku-20240307-v1:0'
    AI_MAX_TOKENS = 1000
    AI_TEMPERATURE = 0.7
