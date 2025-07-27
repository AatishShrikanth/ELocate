import requests
from typing import Dict, Optional
from config.settings import Config

class WeatherService:
    def __init__(self):
        self.api_key = Config.OPENWEATHER_API_KEY
        self.base_url = Config.OPENWEATHER_BASE_URL
    
    def get_current_weather(self, lat: float, lon: float) -> Optional[Dict]:
        """Get current weather for given coordinates"""
        try:
            params = {
                'lat': lat,
                'lon': lon,
                'appid': self.api_key,
                'units': 'metric'  # Celsius
            }
            
            response = requests.get(
                f"{self.base_url}/weather",
                params=params
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error getting weather: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"Error in get_current_weather: {str(e)}")
            return None
    
    def get_weather_forecast(self, lat: float, lon: float, hours: int = 24) -> Optional[Dict]:
        """Get weather forecast for given coordinates"""
        try:
            params = {
                'lat': lat,
                'lon': lon,
                'appid': self.api_key,
                'units': 'metric',
                'cnt': min(hours, 48)  # Max 48 hours for free tier
            }
            
            response = requests.get(
                f"{self.base_url}/forecast",
                params=params
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error getting forecast: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"Error in get_weather_forecast: {str(e)}")
            return None
    
    def analyze_weather_for_recommendations(self, weather_data: Dict) -> Dict:
        """Analyze weather data to provide recommendation context"""
        if not weather_data:
            return {'indoor_preferred': False, 'weather_context': 'unknown'}
        
        try:
            main = weather_data.get('main', {})
            weather = weather_data.get('weather', [{}])[0]
            wind = weather_data.get('wind', {})
            rain = weather_data.get('rain', {})
            
            temp = main.get('temp', 20)
            humidity = main.get('humidity', 50)
            wind_speed = wind.get('speed', 0) * 3.6  # Convert m/s to km/h
            rain_1h = rain.get('1h', 0)
            weather_main = weather.get('main', '').lower()
            
            # Determine if indoor activities are preferred
            indoor_preferred = (
                temp < Config.WEATHER_THRESHOLDS['temp_cold'] or
                temp > Config.WEATHER_THRESHOLDS['temp_hot'] or
                rain_1h > Config.WEATHER_THRESHOLDS['rain_threshold'] or
                wind_speed > Config.WEATHER_THRESHOLDS['wind_strong'] or
                weather_main in ['rain', 'thunderstorm', 'snow']
            )
            
            # Generate weather context
            weather_context = self._generate_weather_context(
                temp, weather_main, rain_1h, wind_speed
            )
            
            return {
                'indoor_preferred': indoor_preferred,
                'weather_context': weather_context,
                'temperature': temp,
                'condition': weather_main,
                'rain': rain_1h > 0,
                'windy': wind_speed > Config.WEATHER_THRESHOLDS['wind_strong']
            }
            
        except Exception as e:
            print(f"Error analyzing weather: {str(e)}")
            return {'indoor_preferred': False, 'weather_context': 'unknown'}
    
    def _generate_weather_context(self, temp: float, condition: str, rain: float, wind: float) -> str:
        """Generate human-readable weather context"""
        contexts = []
        
        if temp < 10:
            contexts.append("cold weather")
        elif temp > 30:
            contexts.append("hot weather")
        elif 20 <= temp <= 25:
            contexts.append("pleasant weather")
        
        if rain > 0:
            contexts.append("rainy conditions")
        elif condition == 'clear':
            contexts.append("clear skies")
        elif condition in ['clouds', 'overcast']:
            contexts.append("cloudy weather")
        
        if wind > 20:
            contexts.append("windy conditions")
        
        if not contexts:
            return "moderate weather conditions"
        
        return ", ".join(contexts)
