import requests
from typing import List, Dict, Optional
from config.settings import Config

class PlacesService:
    def __init__(self):
        self.api_key = Config.GOOGLE_PLACES_API_KEY
        self.base_url = Config.GOOGLE_PLACES_BASE_URL
    
    def search_nearby_places(self, 
                           location: Dict[str, float], 
                           place_type: str = 'restaurant',
                           radius: int = 5000) -> List[Dict]:
        """Search for nearby places using Google Places API"""
        try:
            params = {
                'location': f"{location['lat']},{location['lng']}",
                'radius': radius,
                'type': place_type,
                'key': self.api_key
            }
            
            response = requests.get(
                f"{self.base_url}/nearbysearch/json",
                params=params
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('results', [])
            else:
                print(f"Error searching places: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"Error in search_nearby_places: {str(e)}")
            return []
    
    def get_place_details(self, place_id: str) -> Optional[Dict]:
        """Get detailed information about a specific place"""
        try:
            params = {
                'place_id': place_id,
                'fields': 'name,rating,formatted_phone_number,formatted_address,opening_hours,website,photos,price_level,reviews,geometry',
                'key': self.api_key
            }
            
            response = requests.get(
                f"{self.base_url}/details/json",
                params=params
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('result', {})
            else:
                print(f"Error getting place details: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"Error in get_place_details: {str(e)}")
            return None
    
    def search_places_by_text(self, query: str, location: Dict[str, float] = None) -> List[Dict]:
        """Search places using text query"""
        try:
            params = {
                'query': query,
                'key': self.api_key
            }
            
            if location:
                params['location'] = f"{location['lat']},{location['lng']}"
                params['radius'] = Config.DEFAULT_RADIUS
            
            response = requests.get(
                f"{self.base_url}/textsearch/json",
                params=params
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('results', [])
            else:
                print(f"Error in text search: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"Error in search_places_by_text: {str(e)}")
            return []
    
    def get_place_photo_url(self, photo_reference: str, max_width: int = 400) -> str:
        """Get URL for a place photo"""
        return f"{self.base_url}/photo?maxwidth={max_width}&photoreference={photo_reference}&key={self.api_key}"
    
    def enrich_venue_data(self, venues: List[Dict]) -> List[Dict]:
        """Enrich venue data with Google Places information"""
        enriched_venues = []
        
        for venue in venues:
            try:
                # Search for the venue in Google Places
                search_results = self.search_places_by_text(venue.get('name', ''))
                
                if search_results:
                    place = search_results[0]  # Take the first result
                    
                    # Get detailed information
                    place_details = self.get_place_details(place.get('place_id', ''))
                    
                    if place_details:
                        # Merge Qloo data with Google Places data
                        enriched_venue = {
                            **venue,
                            'google_rating': place_details.get('rating'),
                            'google_reviews': len(place_details.get('reviews', [])),
                            'phone': place_details.get('formatted_phone_number'),
                            'address': place_details.get('formatted_address'),
                            'website': place_details.get('website'),
                            'opening_hours': place_details.get('opening_hours', {}).get('weekday_text', []),
                            'price_level': place_details.get('price_level'),
                            'photos': place_details.get('photos', []),
                            'place_id': place.get('place_id'),
                            'geometry': place_details.get('geometry', {})
                        }
                        
                        enriched_venues.append(enriched_venue)
                    else:
                        enriched_venues.append(venue)
                else:
                    enriched_venues.append(venue)
                    
            except Exception as e:
                print(f"Error enriching venue {venue.get('name', 'Unknown')}: {str(e)}")
                enriched_venues.append(venue)
        
        return enriched_venues
    
    def filter_by_weather(self, venues: List[Dict], weather_analysis: Dict) -> List[Dict]:
        """Filter venues based on weather conditions"""
        if not weather_analysis.get('indoor_preferred'):
            return venues
        
        # Define indoor venue types
        indoor_types = [
            'restaurant', 'bar', 'movie_theater', 'museum', 'shopping_mall',
            'bowling_alley', 'casino', 'night_club', 'spa', 'art_gallery', 'library'
        ]
        
        outdoor_types = [
            'park', 'amusement_park', 'zoo', 'tourist_attraction'
        ]
        
        filtered_venues = []
        for venue in venues:
            venue_types = venue.get('types', [])
            
            # If weather suggests indoor activities, prioritize indoor venues
            if weather_analysis['indoor_preferred']:
                if any(vtype in indoor_types for vtype in venue_types):
                    venue['weather_match'] = True
                    filtered_venues.append(venue)
                elif not any(vtype in outdoor_types for vtype in venue_types):
                    # Include venues that are not explicitly outdoor
                    venue['weather_match'] = False
                    filtered_venues.append(venue)
            else:
                venue['weather_match'] = True
                filtered_venues.append(venue)
        
        return filtered_venues
