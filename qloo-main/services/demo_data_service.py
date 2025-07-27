"""
Demo data service to provide sample recommendations when APIs are not available
"""

import random
from typing import List, Dict

class DemoDataService:
    """Provides demo data for testing when APIs are not available"""
    
    def __init__(self):
        self.demo_venues = [
            {
                'id': 'demo_1',
                'name': 'The French Laundry',
                'rating': 4.8,
                'price_level': 4,
                'types': ['restaurant', 'fine_dining'],
                'vicinity': '6640 Washington St, Yountville, CA',
                'address': '6640 Washington St, Yountville, CA 94599',
                'geometry': {'location': {'lat': 38.4024, 'lng': -122.3631}},
                'photos': [],
                'place_id': 'demo_french_laundry',
                'source': 'demo',
                'recommendation_score': 4.8,
                'phone': '(707) 944-2380',
                'website': 'https://www.thomaskeller.com/tfl',
                'opening_hours': ['Monday: Closed', 'Tuesday: 5:30–9:00 PM', 'Wednesday: 5:30–9:00 PM']
            },
            {
                'id': 'demo_2',
                'name': 'Tartine Bakery',
                'rating': 4.5,
                'price_level': 2,
                'types': ['bakery', 'restaurant'],
                'vicinity': '600 Guerrero St, San Francisco, CA',
                'address': '600 Guerrero St, San Francisco, CA 94110',
                'geometry': {'location': {'lat': 37.7609, 'lng': -122.4242}},
                'photos': [],
                'place_id': 'demo_tartine',
                'source': 'demo',
                'recommendation_score': 4.5,
                'phone': '(415) 487-2600',
                'website': 'https://www.tartinebakery.com',
                'opening_hours': ['Monday: 8:00 AM–3:00 PM', 'Tuesday: 8:00 AM–3:00 PM']
            },
            {
                'id': 'demo_3',
                'name': 'SFMOMA',
                'rating': 4.6,
                'price_level': 3,
                'types': ['museum', 'art_gallery'],
                'vicinity': '151 3rd St, San Francisco, CA',
                'address': '151 3rd St, San Francisco, CA 94103',
                'geometry': {'location': {'lat': 37.7857, 'lng': -122.4011}},
                'photos': [],
                'place_id': 'demo_sfmoma',
                'source': 'demo',
                'recommendation_score': 4.6,
                'phone': '(415) 357-4000',
                'website': 'https://www.sfmoma.org',
                'opening_hours': ['Monday: Closed', 'Tuesday: 10:00 AM–5:00 PM']
            },
            {
                'id': 'demo_4',
                'name': 'Golden Gate Park',
                'rating': 4.7,
                'price_level': None,
                'types': ['park', 'tourist_attraction'],
                'vicinity': 'San Francisco, CA',
                'address': 'Golden Gate Park, San Francisco, CA',
                'geometry': {'location': {'lat': 37.7694, 'lng': -122.4862}},
                'photos': [],
                'place_id': 'demo_ggpark',
                'source': 'demo',
                'recommendation_score': 4.7,
                'phone': None,
                'website': 'https://sfrecpark.org/facilities/facility/details/golden-gate-park-3',
                'opening_hours': ['Open 24 hours']
            },
            {
                'id': 'demo_5',
                'name': 'Blue Bottle Coffee',
                'rating': 4.3,
                'price_level': 2,
                'types': ['cafe', 'coffee_shop'],
                'vicinity': '66 Mint St, San Francisco, CA',
                'address': '66 Mint St, San Francisco, CA 94103',
                'geometry': {'location': {'lat': 37.7820, 'lng': -122.4058}},
                'photos': [],
                'place_id': 'demo_bluebottle',
                'source': 'demo',
                'recommendation_score': 4.3,
                'phone': '(510) 653-3394',
                'website': 'https://bluebottlecoffee.com',
                'opening_hours': ['Monday: 6:00 AM–7:00 PM', 'Tuesday: 6:00 AM–7:00 PM']
            },
            {
                'id': 'demo_6',
                'name': 'The Fillmore',
                'rating': 4.4,
                'price_level': 3,
                'types': ['night_club', 'entertainment'],
                'vicinity': '1805 Geary Blvd, San Francisco, CA',
                'address': '1805 Geary Blvd, San Francisco, CA 94115',
                'geometry': {'location': {'lat': 37.7844, 'lng': -122.4324}},
                'photos': [],
                'place_id': 'demo_fillmore',
                'source': 'demo',
                'recommendation_score': 4.4,
                'phone': '(415) 346-6000',
                'website': 'https://www.thefillmore.com',
                'opening_hours': ['Hours vary by event']
            },
            {
                'id': 'demo_7',
                'name': 'Chinatown',
                'rating': 4.2,
                'price_level': 1,
                'types': ['tourist_attraction', 'neighborhood'],
                'vicinity': 'Grant Ave, San Francisco, CA',
                'address': 'Grant Ave & Bush St, San Francisco, CA 94108',
                'geometry': {'location': {'lat': 37.7941, 'lng': -122.4078}},
                'photos': [],
                'place_id': 'demo_chinatown',
                'source': 'demo',
                'recommendation_score': 4.2,
                'phone': None,
                'website': 'https://www.sanfranciscochinatown.com',
                'opening_hours': ['Open 24 hours']
            },
            {
                'id': 'demo_8',
                'name': 'Alcatraz Island',
                'rating': 4.5,
                'price_level': 3,
                'types': ['tourist_attraction', 'museum'],
                'vicinity': 'San Francisco Bay, CA',
                'address': 'Alcatraz Island, San Francisco, CA 94133',
                'geometry': {'location': {'lat': 37.8267, 'lng': -122.4233}},
                'photos': [],
                'place_id': 'demo_alcatraz',
                'source': 'demo',
                'recommendation_score': 4.5,
                'phone': '(415) 561-4900',
                'website': 'https://www.nps.gov/alca',
                'opening_hours': ['Hours vary by season']
            },
            {
                'id': 'demo_9',
                'name': 'Lombard Street',
                'rating': 4.1,
                'price_level': None,
                'types': ['tourist_attraction', 'scenic_view'],
                'vicinity': 'Lombard St, San Francisco, CA',
                'address': 'Lombard St, San Francisco, CA 94133',
                'geometry': {'location': {'lat': 37.8021, 'lng': -122.4187}},
                'photos': [],
                'place_id': 'demo_lombard',
                'source': 'demo',
                'recommendation_score': 4.1,
                'phone': None,
                'website': None,
                'opening_hours': ['Open 24 hours']
            },
            {
                'id': 'demo_10',
                'name': 'Ferry Building Marketplace',
                'rating': 4.4,
                'price_level': 2,
                'types': ['shopping_mall', 'food_court'],
                'vicinity': '1 Ferry Building, San Francisco, CA',
                'address': '1 Ferry Building, San Francisco, CA 94111',
                'geometry': {'location': {'lat': 37.7955, 'lng': -122.3937}},
                'photos': [],
                'place_id': 'demo_ferry_building',
                'source': 'demo',
                'recommendation_score': 4.4,
                'phone': '(415) 983-8030',
                'website': 'https://www.ferrybuildingmarketplace.com',
                'opening_hours': ['Monday: 10:00 AM–7:00 PM', 'Tuesday: 10:00 AM–7:00 PM']
            }
        ]
    
    def get_demo_recommendations(self, 
                                user_id: str, 
                                location: Dict[str, float],
                                filters: Dict = None) -> List[Dict]:
        """Get demo recommendations based on filters"""
        
        if not filters:
            filters = {}
        
        # Start with all demo venues
        recommendations = self.demo_venues.copy()
        
        # Apply category filter
        category = filters.get('category', 'All')
        if category != 'All':
            category_mapping = {
                'Restaurants': ['restaurant', 'bakery', 'cafe', 'coffee_shop', 'food_court'],
                'Bars': ['bar', 'night_club'],
                'Entertainment': ['night_club', 'entertainment', 'movie_theater'],
                'Culture': ['museum', 'art_gallery', 'tourist_attraction'],
                'Shopping': ['shopping_mall'],
                'Outdoor': ['park', 'scenic_view']
            }
            
            allowed_types = category_mapping.get(category, [])
            if allowed_types:
                recommendations = [
                    r for r in recommendations 
                    if any(t in allowed_types for t in r.get('types', []))
                ]
        
        # Apply budget filter
        budget = filters.get('budget', 'Any')
        if budget != 'Any':
            budget_mapping = {"$": 1, "$$": 2, "$$$": 3, "$$$$": 4}
            max_price_level = budget_mapping.get(budget, 4)
            recommendations = [
                r for r in recommendations 
                if r.get('price_level') is None or r.get('price_level') <= max_price_level
            ]
        
        # Apply rating filter
        min_rating = filters.get('min_rating', 0)
        if min_rating > 0:
            recommendations = [
                r for r in recommendations 
                if r.get('rating', 0) >= min_rating
            ]
        
        # Calculate distances from user location
        for rec in recommendations:
            geometry = rec.get('geometry', {})
            if geometry and 'location' in geometry:
                venue_location = geometry['location']
                distance = self._calculate_distance(
                    location['lat'], location['lng'],
                    venue_location['lat'], venue_location['lng']
                )
                rec['distance'] = distance
        
        # Apply distance filter
        max_distance = filters.get('distance', 25)
        recommendations = [
            r for r in recommendations 
            if r.get('distance', 0) <= max_distance
        ]
        
        # Sort by recommendation score
        recommendations.sort(key=lambda x: x.get('recommendation_score', 0), reverse=True)
        
        # Limit results
        max_results = filters.get('max_results', 20)
        return recommendations[:max_results]
    
    def _calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two points in kilometers"""
        from math import radians, cos, sin, asin, sqrt
        
        # Convert decimal degrees to radians
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        
        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        r = 6371  # Radius of earth in kilometers
        
        return c * r
    
    def get_personalized_demo_recommendations(self, 
                                            user_id: str, 
                                            location: Dict[str, float],
                                            filters: Dict = None) -> List[Dict]:
        """Get personalized demo recommendations based on user profile"""
        
        # Get base recommendations
        recommendations = self.get_demo_recommendations(user_id, location, filters)
        
        # Try to personalize based on user profile
        try:
            from utils.data_manager import DataManager
            data_manager = DataManager()
            user_profile = data_manager.load_user_profile(user_id)
            
            if user_profile:
                interests = user_profile.get('interests', [])
                
                # Boost scores based on interests
                for rec in recommendations:
                    venue_types = rec.get('types', [])
                    
                    # Interest matching boost
                    if 'Fine Dining' in interests and 'restaurant' in venue_types:
                        rec['recommendation_score'] += 0.5
                    if 'Museums' in interests and 'museum' in venue_types:
                        rec['recommendation_score'] += 0.5
                    if 'Coffee Shops' in interests and 'cafe' in venue_types:
                        rec['recommendation_score'] += 0.3
                    if 'Outdoor Activities' in interests and 'park' in venue_types:
                        rec['recommendation_score'] += 0.4
                    if 'Art Galleries' in interests and 'art_gallery' in venue_types:
                        rec['recommendation_score'] += 0.5
                
                # Re-sort by updated scores
                recommendations.sort(key=lambda x: x.get('recommendation_score', 0), reverse=True)
        
        except Exception as e:
            print(f"Error personalizing demo recommendations: {str(e)}")
        
        return recommendations
