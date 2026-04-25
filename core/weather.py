import requests
import os
from datetime import datetime
from typing import Dict, List

class WeatherService:
    def __init__(self):
        self.noaa_api_key = os.getenv('NOAA_API_KEY')
        self.openweather_api_key = os.getenv('OPENWEATHER_API_KEY')
        self.update_interval = int(os.getenv('UPDATE_INTERVAL', 300))
        
    def get_current_weather(self, location: str) -> Dict:
        """Get current weather data for a location"""
        coordinates = self._get_coordinates(location)
        
        # Try OpenWeather API first
        weather_data = self._fetch_openweather(coordinates)
        
        if not weather_data:
            # Fallback to NOAA API
            weather_data = self._fetch_noaa(coordinates)
        
        return {
            'location': {
                'name': location.title(),
                'coordinates': coordinates,
                'country': self._get_country(location),
                'timezone': self._get_timezone(location)
            },
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'temperature': weather_data.get('temperature', 0),
            'humidity': weather_data.get('humidity', 0),
            'wind_speed': weather_data.get('wind_speed', 0),
            'solar_radiation': weather_data.get('solar_radiation', 0),
            'uv_index': weather_data.get('uv_index', 0),
            'cloud_cover': weather_data.get('cloud_cover', 0),
            'pressure': weather_data.get('pressure', 0)
        }
    
    def get_forecast(self, location: str, hours: int) -> List[Dict]:
        """Get weather forecast for a location"""
        coordinates = self._get_coordinates(location)
        
        forecast_data = self._fetch_openweather_forecast(coordinates, hours)
        
        hourly_forecast = []
        for hour in forecast_data:
            hourly_forecast.append({
                'time': hour['time'],
                'temperature': hour['temperature'],
                'humidity': hour['humidity'],
                'wind_speed': hour['wind_speed'],
                'solar_radiation': hour.get('solar_radiation', 0),
                'uv_index': hour.get('uv_index', 0),
                'cloud_cover': hour.get('cloud_cover', 0),
                'timestamp': hour['time']
            })
        
        return hourly_forecast
    
    def _get_coordinates(self, location: str) -> Dict:
        """Get coordinates for a location"""
        location_coords = {
            'mecca': {'lat': 21.4225, 'lng': 39.8262},
            'medina': {'lat': 24.4672, 'lng': 39.6147},
            'riyadh': {'lat': 24.7136, 'lng': 46.6753},
            'jeddah': {'lat': 21.5433, 'lng': 39.1728},
            'dammam': {'lat': 26.4244, 'lng': 50.1036},
            'dubai': {'lat': 25.2048, 'lng': 55.2708},
            'abu_dhabi': {'lat': 24.4539, 'lng': 54.3773},
            'doha': {'lat': 25.2854, 'lng': 51.5310},
            'kuwait_city': {'lat': 29.3759, 'lng': 47.9774},
            'manama': {'lat': 26.0667, 'lng': 50.5577}
        }
        
        return location_coords.get(location.lower(), {'lat': 0, 'lng': 0})
    
    def _get_country(self, location: str) -> str:
        """Get country code for a location"""
        location_countries = {
            'mecca': 'SA', 'medina': 'SA', 'riyadh': 'SA', 'jeddah': 'SA', 'dammam': 'SA',
            'dubai': 'AE', 'abu_dhabi': 'AE',
            'doha': 'QA',
            'kuwait_city': 'KW',
            'manama': 'BH'
        }
        return location_countries.get(location.lower(), 'SA')
    
    def _get_timezone(self, location: str) -> str:
        """Get timezone for a location"""
        location_timezones = {
            'mecca': 'Asia/Riyadh', 'medina': 'Asia/Riyadh', 'riyadh': 'Asia/Riyadh',
            'jeddah': 'Asia/Riyadh', 'dammam': 'Asia/Riyadh',
            'dubai': 'Asia/Dubai', 'abu_dhabi': 'Asia/Dubai',
            'doha': 'Asia/Qatar',
            'kuwait_city': 'Asia/Kuwait',
            'manama': 'Asia/Bahrain'
        }
        return location_timezones.get(location.lower(), 'Asia/Riyadh')
    
    def _fetch_openweather(self, coordinates: Dict) -> Dict:
        """Fetch weather data from OpenWeather API"""
        if not self.openweather_api_key:
            return {}
        
        url = f"https://api.openweathermap.org/data/2.5/weather"
        params = {
            'lat': coordinates['lat'],
            'lon': coordinates['lng'],
            'appid': self.openweather_api_key,
            'units': 'metric'
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            return {
                'temperature': data['main']['temp'],
                'humidity': data['main']['humidity'],
                'wind_speed': data['wind']['speed'],
                'pressure': data['main']['pressure'],
                'cloud_cover': data['clouds']['all'],
                'uv_index': 0,  # Requires separate UV API call
                'solar_radiation': data.get('solar_radiation', 0)
            }
        except Exception as e:
            print(f"Error fetching OpenWeather data: {e}")
            return {}
    
    def _fetch_openweather_forecast(self, coordinates: Dict, hours: int) -> List[Dict]:
        """Fetch forecast data from OpenWeather API"""
        if not self.openweather_api_key:
            return []
        
        url = f"https://api.openweathermap.org/data/2.5/forecast"
        params = {
            'lat': coordinates['lat'],
            'lon': coordinates['lng'],
            'appid': self.openweather_api_key,
            'units': 'metric'
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            forecast = []
            for item in data['list'][:hours]:
                forecast.append({
                    'time': item['dt_txt'],
                    'temperature': item['main']['temp'],
                    'humidity': item['main']['humidity'],
                    'wind_speed': item['wind']['speed'],
                    'cloud_cover': item['clouds']['all'],
                    'uv_index': 0,
                    'solar_radiation': item.get('solar_radiation', 0)
                })
            
            return forecast
        except Exception as e:
            print(f"Error fetching forecast data: {e}")
            return []
    
    def _fetch_noaa(self, coordinates: Dict) -> Dict:
        """Fetch weather data from NOAA API"""
        if not self.noaa_api_key:
            return {}
        
        url = f"https://www.ncdc.noaa.gov/cdo-web/api/v2/data"
        params = {
            'datasetid': 'GHCND',
            'locationid': f'POINT({coordinates["lng"]},{coordinates["lat"]})',
            'startdate': datetime.utcnow().strftime('%Y-%m-%d'),
            'enddate': datetime.utcnow().strftime('%Y-%m-%d'),
            'limit': 1
        }
        
        headers = {'token': self.noaa_api_key}
        
        try:
            response = requests.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get('results'):
                result = data['results'][0]
                return {
                    'temperature': result.get('value', 0) / 10.0,  # Convert to Celsius
                    'humidity': 50,  # NOAA doesn't provide humidity in basic dataset
                    'wind_speed': 0,
                    'pressure': 1013,
                    'cloud_cover': 0,
                    'uv_index': 0,
                    'solar_radiation': 0
                }
        except Exception as e:
            print(f"Error fetching NOAA data: {e}")
        
        return {}
