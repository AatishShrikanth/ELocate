"""
Qloo-Only Recommendation Service
Uses ONLY Qloo API data - no demo data fallback
"""

import logging
from typing import List, Dict, Optional
from services.qloo_service import QlooService
from services.weather_service import WeatherService
from utils.data_manager import DataManager
from utils.location_mapper import LocationMapper

# Set up debug logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class QlooOnlyRecommendationService:
    """Recommendation service using ONLY Qloo API data"""
    
    def __init__(self):
        logger.info("🎯 Initializing Qloo-Only Recommendation Service")
        self.qloo_service = QlooService()
        self.weather_service = WeatherService()
        self.data_manager = DataManager()
        logger.info("✅ Qloo-Only Recommendation Service initialized")
    
    def get_recommendations(self, 
                          user_id: str, 
                          location_name: str,  # Changed from location dict to location name
                          filters: Dict = None) -> List[Dict]:
        """Get recommendations using ONLY Qloo API data"""
        logger.info("🎯 QLOO-ONLY RECOMMENDATIONS REQUEST")
        logger.info("=" * 60)
        logger.info(f"👤 User ID: {user_id}")
        logger.info(f"📍 Location: {location_name}")
        logger.info(f"🔍 Filters: {filters}")
        
        try:
            if not filters:
                filters = {}
            
            # Get user profile for personalization
            user_profile = self.data_manager.load_user_profile(user_id)
            if user_profile:
                logger.info(f"👤 User Profile Found: {user_profile.get('name', 'Unknown')}")
                logger.info(f"🎯 User Interests: {user_profile.get('interests', [])}")
            else:
                logger.warning("⚠️ No user profile found")
            
            # Get weather context if enabled
            weather_analysis = None
            if filters.get('weather_aware', False):
                logger.info("🌤️ Weather-aware recommendations enabled")
                
                # Convert location to coordinates for weather API
                coordinates = LocationMapper.get_coordinates(location_name)
                if coordinates:
                    logger.info(f"🌍 Location coordinates: {coordinates['lat']}, {coordinates['lng']}")
                    
                    weather_data = self.weather_service.get_current_weather(
                        coordinates['lat'], 
                        coordinates['lng']
                    )
                    
                    if weather_data:
                        weather_analysis = self.weather_service.analyze_weather_for_recommendations(weather_data)
                        logger.info(f"🌤️ Weather analysis: {weather_analysis}")
                    else:
                        logger.warning("⚠️ Failed to get weather data")
                else:
                    logger.warning(f"⚠️ No coordinates found for location: {location_name}")
                    logger.info("💡 Weather integration disabled - location not supported")
            
            # METHOD 1: Try to get venue recommendations directly from Qloo v2/insights
            logger.info("🎯 METHOD 1: Direct venue recommendations from Qloo v2/insights API")
            venue_recommendations = self.qloo_service.get_venue_recommendations(location_name, filters)
            
            if venue_recommendations:
                logger.info(f"✅ METHOD 1 SUCCESS: Got {len(venue_recommendations)} venues from Qloo API")
                return self._process_recommendations(venue_recommendations, filters, weather_analysis, user_profile)
            
            # METHOD 2: Get category-based entities and try to find venue data
            logger.info("🎯 METHOD 2: Category-based entity search")
            category_recommendations = self._get_category_based_venues(user_profile, location_name, filters)
            
            if category_recommendations:
                logger.info(f"✅ METHOD 2 SUCCESS: Got {len(category_recommendations)} venues from categories")
                return self._process_recommendations(category_recommendations, filters, weather_analysis, user_profile)
            
            # METHOD 3: Search-based approach
            logger.info("🎯 METHOD 3: Search-based venue discovery")
            search_recommendations = self._get_search_based_venues(location_name, filters)
            
            if search_recommendations:
                logger.info(f"✅ METHOD 3 SUCCESS: Got {len(search_recommendations)} venues from search")
                return self._process_recommendations(search_recommendations, filters, weather_analysis, user_profile)
            
            # If all methods fail
            logger.error("❌ ALL METHODS FAILED - NO QLOO DATA AVAILABLE")
            logger.error("📋 Unable to retrieve any venue data from Qloo API")
            return []
            
        except Exception as e:
            logger.error(f"❌ Error in Qloo-only recommendations: {str(e)}")
            return []
    
    def _get_category_based_venues(self, user_profile: Dict, location_name: str, filters: Dict) -> List[Dict]:
        """Try to get venues from category-based entity search"""
        logger.info("🔍 Searching for venues using category-based approach")
        
        try:
            # Get category insights
            if user_profile:
                insights = self.qloo_service.get_enhanced_recommendations_by_category(user_profile, filters)
            else:
                # Default categories if no profile
                default_categories = ['restaurant', 'bar', 'entertainment', 'museum']
                insights = self.qloo_service.get_category_insights(default_categories)
            
            if not insights:
                logger.warning("⚠️ No category insights retrieved")
                return []
            
            # Look for entities that might be actual venues (have location data)
            venue_entities = []
            
            for category, entities in insights.items():
                logger.info(f"🔍 Checking {len(entities)} entities in category '{category}'")
                
                for entity in entities:
                    properties = entity.get('properties', {})
                    
                    # Check if entity has venue-like properties
                    has_address = bool(properties.get('address'))
                    has_geocode = bool(properties.get('geocode'))
                    has_phone = bool(properties.get('phone'))
                    has_hours = bool(properties.get('hours'))
                    
                    venue_score = sum([has_address, has_geocode, has_phone, has_hours])
                    
                    if venue_score >= 2:  # At least 2 venue-like properties
                        logger.debug(f"✅ Found venue-like entity: {entity.get('name')} (score: {venue_score})")
                        venue_entities.append(entity)
            
            if venue_entities:
                logger.info(f"✅ Found {len(venue_entities)} venue-like entities")
                return self.qloo_service._format_qloo_venues(venue_entities)
            else:
                logger.warning("⚠️ No venue-like entities found in category results")
                return []
                
        except Exception as e:
            logger.error(f"❌ Error in category-based venue search: {str(e)}")
            return []
    
    def _get_search_based_venues(self, location_name: str, filters: Dict) -> List[Dict]:
        """Try to get venues using search-based approach"""
        logger.info("🔍 Searching for venues using search-based approach")
        
        try:
            # Try different search terms that might return venue data
            search_terms = [
                f'restaurant {location_name}',
                f'venues {location_name}',
                f'places to eat {location_name}',
                f'entertainment {location_name}',
                f'bars {location_name}',
                'restaurant',
                'venues'
            ]
            
            all_venues = []
            
            for term in search_terms:
                logger.debug(f"🔍 Searching for: '{term}'")
                
                results = self.qloo_service.search_entities_by_category(term, limit=10)
                
                if results:
                    # Filter for venue-like results
                    venue_results = []
                    for result in results:
                        properties = result.get('properties', {})
                        if properties.get('address') or properties.get('geocode'):
                            venue_results.append(result)
                    
                    if venue_results:
                        logger.info(f"✅ Found {len(venue_results)} venue results for '{term}'")
                        formatted = self.qloo_service._format_qloo_venues(venue_results)
                        all_venues.extend(formatted)
                        
                        # Stop if we have enough venues
                        if len(all_venues) >= 10:
                            break
            
            # Remove duplicates
            unique_venues = self._remove_duplicates(all_venues)
            
            if unique_venues:
                logger.info(f"✅ Search-based approach found {len(unique_venues)} unique venues")
                return unique_venues
            else:
                logger.warning("⚠️ Search-based approach found no venues")
                return []
                
        except Exception as e:
            logger.error(f"❌ Error in search-based venue discovery: {str(e)}")
            return []
    
    def _process_recommendations(self, venues: List[Dict], filters: Dict, weather_analysis: Dict, user_profile: Dict) -> List[Dict]:
        """Process and filter Qloo venue recommendations"""
        logger.info(f"🔄 Processing {len(venues)} Qloo recommendations")
        
        processed_venues = venues.copy()
        
        # Apply budget filter
        budget = filters.get('budget', 'Any')
        if budget != 'Any':
            processed_venues = self._filter_by_budget(processed_venues, budget)
            logger.info(f"💰 Budget filter ({budget}): {len(processed_venues)} venues remaining")
        
        # Apply rating filter
        min_rating = filters.get('min_rating', 0)
        if min_rating > 0:
            processed_venues = [v for v in processed_venues if (v.get('rating') or 0) >= min_rating]
            logger.info(f"⭐ Rating filter (>={min_rating}): {len(processed_venues)} venues remaining")
        
        # Apply weather filter
        if weather_analysis and filters.get('weather_aware'):
            processed_venues = self._filter_by_weather(processed_venues, weather_analysis)
            logger.info(f"🌤️ Weather filter: {len(processed_venues)} venues remaining")
        
        # Apply personalization
        if user_profile:
            processed_venues = self._personalize_ranking(processed_venues, user_profile)
            logger.info("🎨 Personalization applied")
        
        # Limit results
        max_results = filters.get('max_results', 20)
        final_venues = processed_venues[:max_results]
        
        logger.info(f"✅ Final processed recommendations: {len(final_venues)} venues")
        
        # Log final venue details
        for i, venue in enumerate(final_venues[:5], 1):  # Log first 5
            logger.debug(f"📋 Venue {i}: {venue.get('name')} (Score: {venue.get('recommendation_score', 0):.2f})")
        
        return final_venues
    
    def _filter_by_budget(self, venues: List[Dict], budget: str) -> List[Dict]:
        """Filter venues by budget"""
        budget_mapping = {"$": 1, "$$": 2, "$$$": 3, "$$$$": 4}
        max_price_level = budget_mapping.get(budget, 4)
        
        return [v for v in venues 
                if v.get('price_level') is None or v.get('price_level') <= max_price_level]
    
    def _filter_by_weather(self, venues: List[Dict], weather_analysis: Dict) -> List[Dict]:
        """Filter venues based on weather conditions - adapted for Qloo data"""
        if not weather_analysis.get('indoor_preferred'):
            return venues
        
        # Indoor venue indicators for Qloo data
        indoor_keywords = [
            'restaurant', 'bar', 'museum', 'theater', 'hotel', 'shopping', 'mall',
            'casino', 'spa', 'gallery', 'library', 'cafe', 'coffee', 'dining',
            'indoor', 'inside', 'covered', 'entertainment', 'club', 'lounge'
        ]
        
        outdoor_keywords = [
            'park', 'garden', 'outdoor', 'beach', 'trail', 'hiking', 'camping',
            'zoo', 'playground', 'sports field', 'stadium', 'golf', 'tennis court'
        ]
        
        filtered = []
        for venue in venues:
            venue_name = venue.get('name', '').lower()
            venue_description = venue.get('description', '').lower()
            venue_categories = [str(c).lower() for c in venue.get('categories', [])]
            venue_address = venue.get('address', '').lower()
            
            # Check if venue is likely indoor based on multiple signals
            indoor_signals = 0
            outdoor_signals = 0
            
            # Check name
            for keyword in indoor_keywords:
                if keyword in venue_name:
                    indoor_signals += 2
            for keyword in outdoor_keywords:
                if keyword in venue_name:
                    outdoor_signals += 2
            
            # Check description
            for keyword in indoor_keywords:
                if keyword in venue_description:
                    indoor_signals += 1
            for keyword in outdoor_keywords:
                if keyword in venue_description:
                    outdoor_signals += 1
            
            # Check categories
            for category in venue_categories:
                for keyword in indoor_keywords:
                    if keyword in category:
                        indoor_signals += 1
                for keyword in outdoor_keywords:
                    if keyword in category:
                        outdoor_signals += 1
            
            # Special cases based on venue names
            if any(word in venue_name for word in ['museum', 'hotel', 'theater', 'restaurant', 'bar', 'cafe']):
                indoor_signals += 3
            elif any(word in venue_name for word in ['park', 'garden', 'zoo', 'bridge']):
                outdoor_signals += 3
            
            # Default assumption: if no clear signals, assume indoor for weather protection
            is_indoor = indoor_signals >= outdoor_signals or (indoor_signals == 0 and outdoor_signals == 0)
            
            if is_indoor:
                venue['weather_match'] = True
                venue['indoor_reason'] = f"Indoor signals: {indoor_signals}, Outdoor signals: {outdoor_signals}"
                filtered.append(venue)
        
        return filtered
    
    def _personalize_ranking(self, venues: List[Dict], user_profile: Dict) -> List[Dict]:
        """Personalize venue ranking based on user profile"""
        user_interests = user_profile.get('interests', [])
        
        if not user_interests:
            return venues
        
        # Interest matching boost
        for venue in venues:
            base_score = venue.get('recommendation_score', 0)
            
            # Check if venue matches user interests
            venue_name = venue.get('name', '').lower()
            venue_categories = venue.get('categories', [])
            
            interest_boost = 0
            for interest in user_interests:
                interest_lower = interest.lower()
                
                if (interest_lower in venue_name or 
                    any(interest_lower in str(cat).lower() for cat in venue_categories)):
                    interest_boost += 0.5
            
            venue['recommendation_score'] = base_score + interest_boost
        
        # Sort by personalized score
        return sorted(venues, key=lambda x: x.get('recommendation_score', 0), reverse=True)
    
    def _remove_duplicates(self, venues: List[Dict]) -> List[Dict]:
        """Remove duplicate venues"""
        seen_ids = set()
        seen_names = set()
        unique_venues = []
        
        for venue in venues:
            venue_id = venue.get('qloo_entity_id') or venue.get('id')
            venue_name = venue.get('name', '').lower().strip()
            
            if venue_id and venue_id in seen_ids:
                continue
            if venue_name and venue_name in seen_names:
                continue
            
            if venue_id:
                seen_ids.add(venue_id)
            if venue_name:
                seen_names.add(venue_name)
            
            unique_venues.append(venue)
        
        return unique_venues
