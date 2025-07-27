import requests
import random
import logging
from typing import List, Dict, Optional
# from services.places_service import PlacesService  # COMMENTED OUT - Google Places disabled
from services.weather_service import WeatherService
from services.demo_data_service import DemoDataService
from services.qloo_service import QlooService
from services.qloo_demo_mapper import QlooDemoMapper
from utils.data_manager import DataManager
from config.settings import Config

# Set up logging
logger = logging.getLogger(__name__)

class RecommendationService:
    """
    Main recommendation service that combines multiple data sources
    Uses Google Places as primary source with intelligent filtering
    """
    
    def __init__(self):
        # self.places_service = PlacesService()  # COMMENTED OUT - Google Places disabled
        self.qloo_service = QlooService()  # Use Qloo API
        self.qloo_mapper = QlooDemoMapper()  # NEW: Qloo-Demo mapper
        self.weather_service = WeatherService()
        self.demo_service = DemoDataService()
        self.data_manager = DataManager()
        self.use_demo_data = False  # Flag to control demo mode
    
    def get_personalized_recommendations(self, 
                                       user_id: str, 
                                       location: Dict[str, float],
                                       filters: Dict = None) -> List[Dict]:
        """Get personalized recommendations using Qloo API + Demo hybrid approach"""
        try:
            if not filters:
                filters = {}
            
            # Get user profile for personalization
            user_profile = self.data_manager.load_user_profile(user_id)
            
            # Get weather context if enabled
            weather_analysis = None
            if filters.get('weather_aware', False):
                weather_data = self.weather_service.get_current_weather(
                    location['lat'], location['lng']
                )
                if weather_data:
                    weather_analysis = self.weather_service.analyze_weather_for_recommendations(weather_data)
            
            # PHASE 1: Get Qloo insights for user's interests and filters
            logger.info("🎯 Phase 1: Getting Qloo AI insights...")
            qloo_insights = {}
            
            try:
                if user_profile:
                    logger.info(f"👤 User Profile Found: {user_profile.get('name', 'Unknown')}")
                    logger.info(f"🎯 User Interests: {user_profile.get('interests', [])}")
                    
                    qloo_insights = self.qloo_service.get_enhanced_recommendations_by_category(
                        user_profile, filters  # Pass full user_profile instead of just preferences
                    )
                    
                    if qloo_insights:
                        total_entities = sum(len(entities) for entities in qloo_insights.values())
                        logger.info(f"✅ Qloo API: Retrieved {total_entities} entities across {len(qloo_insights)} categories")
                        
                        # Show insights summary
                        insights_summary = self.qloo_mapper.get_qloo_insights_summary(qloo_insights)
                        logger.info(f"📊 Qloo Insights: {insights_summary['total_categories']} categories, {insights_summary['total_entities']} entities")
                    else:
                        logger.warning("⚠️ Qloo API: No insights retrieved")
                else:
                    logger.warning("⚠️ No user profile found, using default categories")
                
            except Exception as e:
                logger.error(f"⚠️ Qloo API error (continuing with demo): {str(e)[:100]}...")
            
            # PHASE 2: Get demo venues
            logger.info("📊 Phase 2: Getting demo venue data...")
            demo_venues = self.demo_service.get_demo_recommendations(user_id, location, filters)
            logger.info(f"✅ Demo Data: Retrieved {len(demo_venues)} venues")
            
            # PHASE 3: Enhance demo venues with Qloo insights
            if qloo_insights:
                logger.info("🤖 Phase 3: Enhancing venues with Qloo AI insights...")
                enhanced_venues = self.qloo_mapper.create_qloo_enhanced_recommendations(
                    demo_venues, qloo_insights, user_profile, filters  # Pass full user_profile
                )
                
                # Count enhanced venues
                qloo_enhanced_count = sum(1 for v in enhanced_venues if v.get('qloo_enhanced', False))
                logger.info(f"✅ Qloo Enhancement: {qloo_enhanced_count}/{len(enhanced_venues)} venues enhanced with AI insights")
                
                all_recommendations = enhanced_venues
            else:
                logger.info("📊 Phase 3: Using demo data only (no Qloo insights)")
                all_recommendations = demo_venues
            
            # Apply weather filtering if enabled
            if weather_analysis and filters.get('weather_aware'):
                all_recommendations = self._filter_by_weather(all_recommendations, weather_analysis)
                logger.info(f"🌤️ Weather Filter: {len(all_recommendations)} venues match weather conditions")
            
            # Apply other filters
            filtered_recommendations = self._apply_basic_filters(all_recommendations, filters)
            logger.info(f"🔍 Filters Applied: {len(filtered_recommendations)} venues after filtering")
            
            # Final personalization
            if user_profile:
                filtered_recommendations = self._personalize_ranking(filtered_recommendations, user_profile)
                logger.info("🎨 Personalization: Rankings adjusted based on user profile")
            
            # Limit results
            max_results = filters.get('max_results', 20)
            final_recommendations = filtered_recommendations[:max_results]
            
            logger.info(f"✅ Final Results: Returning {len(final_recommendations)} personalized recommendations")
            
            # Add source information and log final summary
            qloo_enhanced_final = 0
            for rec in final_recommendations:
                if rec.get('qloo_enhanced'):
                    rec['data_source'] = 'Qloo AI + Demo Data'
                    qloo_enhanced_final += 1
                else:
                    rec['data_source'] = 'Demo Data'
            
            logger.info(f"📊 Final Enhancement Status: {qloo_enhanced_final}/{len(final_recommendations)} venues Qloo-enhanced")
            
            return final_recommendations
            
        except Exception as e:
            logger.error(f"❌ Error getting recommendations: {str(e)}")
            logger.error("🔄 Falling back to demo recommendations")
            # Return demo recommendations as final fallback
            return self.demo_service.get_personalized_demo_recommendations(user_id, location, filters)
    
    def _remove_duplicates(self, recommendations: List[Dict]) -> List[Dict]:
        """Remove duplicate venues"""
        seen_ids = set()
        seen_names = set()
        unique_recs = []
        
        for rec in recommendations:
            # Check by ID first
            rec_id = rec.get('place_id') or rec.get('id')
            if rec_id and rec_id in seen_ids:
                continue
            
            # Check by name
            name = rec.get('name', '').lower().strip()
            if name and name in seen_names:
                continue
            
            # Add to unique list
            if rec_id:
                seen_ids.add(rec_id)
            if name:
                seen_names.add(name)
            unique_recs.append(rec)
        
        return unique_recs
    
    def _get_category_recommendations(self, location: Dict, filters: Dict, user_profile: Dict = None) -> List[Dict]:
        """Get recommendations based on selected category"""
        try:
            category = filters.get('category', 'All')
            
            # Map categories to Google Places types
            category_mapping = {
                'Restaurants': ['restaurant', 'meal_takeaway', 'food'],
                'Bars': ['bar', 'night_club', 'liquor_store'],
                'Entertainment': ['movie_theater', 'bowling_alley', 'amusement_park'],
                'Culture': ['museum', 'art_gallery', 'library', 'tourist_attraction'],
                'Shopping': ['shopping_mall', 'store', 'clothing_store'],
                'Outdoor': ['park', 'zoo', 'campground']
            }
            
            recommendations = []
            
            if category == 'All':
                # Get a mix from all categories
                for cat_types in category_mapping.values():
                    for place_type in cat_types[:1]:  # Take first type from each category
                        places = self.places_service.search_nearby_places(
                            location, place_type, filters.get('distance', 5) * 1000
                        )
                        recommendations.extend(places[:3])  # Take top 3 from each
            else:
                # Get specific category
                place_types = category_mapping.get(category, ['restaurant'])
                for place_type in place_types:
                    places = self.places_service.search_nearby_places(
                        location, place_type, filters.get('distance', 5) * 1000
                    )
                    recommendations.extend(places[:5])
            
            return self._format_recommendations(recommendations, 'category')
            
        except Exception as e:
            print(f"Error getting category recommendations: {str(e)}")
            return []
    
    def _get_interest_based_recommendations(self, location: Dict, user_profile: Dict, filters: Dict) -> List[Dict]:
        """Get recommendations based on user interests"""
        try:
            interests = user_profile.get('interests', [])
            recommendations = []
            
            # Map interests to search queries
            interest_mapping = {
                'Fine Dining': 'fine dining restaurant',
                'Casual Dining': 'casual restaurant',
                'Bars & Nightlife': 'bar nightclub',
                'Coffee Shops': 'coffee shop cafe',
                'Museums': 'museum',
                'Art Galleries': 'art gallery',
                'Live Music': 'live music venue',
                'Theater': 'theater',
                'Movies': 'movie theater',
                'Shopping': 'shopping mall',
                'Outdoor Activities': 'park recreation',
                'Sports': 'sports bar gym',
                'Spa & Wellness': 'spa wellness',
                'Cultural Events': 'cultural center'
            }
            
            for interest in interests[:3]:  # Limit to top 3 interests
                query = interest_mapping.get(interest, interest)
                places = self.places_service.search_places_by_text(query, location)
                recommendations.extend(places[:3])
            
            return self._format_recommendations(recommendations, 'interest')
            
        except Exception as e:
            print(f"Error getting interest-based recommendations: {str(e)}")
            return []
    
    def _get_popular_venues(self, location: Dict, filters: Dict) -> List[Dict]:
        """Get popular venues as fallback"""
        try:
            # Search for highly-rated restaurants and attractions
            popular_types = ['restaurant', 'tourist_attraction', 'museum', 'park']
            recommendations = []
            
            for place_type in popular_types:
                places = self.places_service.search_nearby_places(
                    location, place_type, filters.get('distance', 5) * 1000
                )
                # Filter for highly rated places
                highly_rated = [p for p in places if p.get('rating', 0) >= 4.0]
                recommendations.extend(highly_rated[:2])
            
            return self._format_recommendations(recommendations, 'popular')
            
        except Exception as e:
            print(f"Error getting popular venues: {str(e)}")
            return []
    
    def _format_recommendations(self, places: List[Dict], source: str) -> List[Dict]:
        """Format Google Places results into our recommendation format"""
        formatted = []
        
        for place in places:
            try:
                formatted_place = {
                    'id': place.get('place_id', ''),
                    'name': place.get('name', 'Unknown Venue'),
                    'rating': place.get('rating'),
                    'price_level': place.get('price_level'),
                    'types': place.get('types', []),
                    'vicinity': place.get('vicinity', ''),
                    'geometry': place.get('geometry', {}),
                    'photos': place.get('photos', []),
                    'opening_hours': place.get('opening_hours', {}),
                    'place_id': place.get('place_id'),
                    'source': source,
                    'recommendation_score': self._calculate_score(place)
                }
                formatted.append(formatted_place)
            except Exception as e:
                print(f"Error formatting place: {str(e)}")
                continue
        
        return formatted
    
    def _calculate_score(self, place: Dict) -> float:
        """Calculate recommendation score for ranking"""
        score = 0.0
        
        # Rating contribution (0-5 scale)
        rating = place.get('rating', 0)
        score += rating * 0.4
        
        # Review count contribution
        user_ratings_total = place.get('user_ratings_total', 0)
        if user_ratings_total > 100:
            score += 1.0
        elif user_ratings_total > 50:
            score += 0.5
        
        # Price level contribution (prefer mid-range)
        price_level = place.get('price_level')
        if price_level in [2, 3]:  # $$ or $$$
            score += 0.5
        
        return score
    
    def _remove_duplicates(self, recommendations: List[Dict]) -> List[Dict]:
        """Remove duplicate venues"""
        seen_ids = set()
        unique_recs = []
        
        for rec in recommendations:
            place_id = rec.get('place_id') or rec.get('id')
            if place_id and place_id not in seen_ids:
                seen_ids.add(place_id)
                unique_recs.append(rec)
            elif not place_id:
                # If no place_id, check by name
                name = rec.get('name', '').lower()
                if name not in [r.get('name', '').lower() for r in unique_recs]:
                    unique_recs.append(rec)
        
        return unique_recs
    
    def _apply_all_filters(self, recommendations: List[Dict], filters: Dict, 
                          weather_analysis: Dict, location: Dict, user_profile: Dict) -> List[Dict]:
        """Apply all filters to recommendations"""
        filtered = recommendations
        
        # Budget filter
        budget = filters.get('budget', 'Any')
        if budget != 'Any':
            filtered = self._filter_by_budget(filtered, budget)
        
        # Rating filter
        min_rating = filters.get('min_rating', 0)
        if min_rating > 0:
            filtered = [r for r in filtered if (r.get('rating') or 0) >= min_rating]
        
        # Weather filter
        if weather_analysis and filters.get('weather_aware'):
            filtered = self._filter_by_weather(filtered, weather_analysis)
        
        # Distance filter
        max_distance = filters.get('distance', 25)
        filtered = self._filter_by_distance(filtered, location, max_distance)
        
        return filtered
    
    def _filter_by_budget(self, recommendations: List[Dict], budget: str) -> List[Dict]:
        """Filter by budget level"""
        budget_mapping = {"$": 1, "$$": 2, "$$$": 3, "$$$$": 4}
        max_price_level = budget_mapping.get(budget, 4)
        
        return [r for r in recommendations 
                if r.get('price_level') is None or r.get('price_level') <= max_price_level]
    
    def _filter_by_weather(self, recommendations: List[Dict], weather_analysis: Dict) -> List[Dict]:
        """Filter based on weather conditions"""
        if not weather_analysis.get('indoor_preferred'):
            return recommendations
        
        indoor_types = [
            'restaurant', 'bar', 'movie_theater', 'museum', 'shopping_mall',
            'bowling_alley', 'casino', 'night_club', 'spa', 'art_gallery', 'library'
        ]
        
        filtered = []
        for rec in recommendations:
            venue_types = rec.get('types', [])
            if any(vtype in indoor_types for vtype in venue_types):
                rec['weather_match'] = True
                filtered.append(rec)
            elif not any(vtype in ['park', 'zoo', 'amusement_park'] for vtype in venue_types):
                rec['weather_match'] = False
                filtered.append(rec)
        
        return filtered
    
    def _filter_by_distance(self, recommendations: List[Dict], location: Dict, max_distance: float) -> List[Dict]:
        """Filter by distance from user location"""
        from utils.helpers import calculate_distance
        
        filtered = []
        for rec in recommendations:
            geometry = rec.get('geometry', {})
            if geometry and 'location' in geometry:
                venue_location = geometry['location']
                distance = calculate_distance(
                    location['lat'], location['lng'],
                    venue_location['lat'], venue_location['lng']
                )
                if distance <= max_distance:
                    rec['distance'] = distance
                    filtered.append(rec)
            else:
                # Include venues without location data
                filtered.append(rec)
        
        return filtered
    
    def _personalize_ranking(self, recommendations: List[Dict], user_profile: Dict) -> List[Dict]:
        """Personalize ranking based on user profile"""
        try:
            user_interests = user_profile.get('interests', [])
            user_budget = user_profile.get('budget_preference', '$$')
            feedback_history = self.data_manager.get_user_feedback_history(user_profile.get('user_id', ''))
            
            # Calculate personalization scores
            for rec in recommendations:
                personalization_score = 0
                
                # Interest matching
                venue_types = rec.get('types', [])
                interest_match = self._calculate_interest_match(venue_types, user_interests)
                personalization_score += interest_match * 0.3
                
                # Budget preference
                venue_price = rec.get('price_level', 2)
                budget_mapping = {"$": 1, "$$": 2, "$$$": 3, "$$$$": 4}
                preferred_price = budget_mapping.get(user_budget, 2)
                if venue_price == preferred_price:
                    personalization_score += 0.2
                
                # Past feedback influence
                similar_feedback_score = self._calculate_similar_venue_score(rec, feedback_history)
                personalization_score += similar_feedback_score * 0.2
                
                # Update recommendation score
                base_score = rec.get('recommendation_score', 0)
                rec['recommendation_score'] = base_score + personalization_score
            
            # Sort by personalized score
            return sorted(recommendations, key=lambda x: x.get('recommendation_score', 0), reverse=True)
            
        except Exception as e:
            print(f"Error personalizing ranking: {str(e)}")
            return recommendations
    
    def _calculate_interest_match(self, venue_types: List[str], user_interests: List[str]) -> float:
        """Calculate how well venue matches user interests"""
        interest_type_mapping = {
            'Fine Dining': ['restaurant', 'meal_delivery'],
            'Bars & Nightlife': ['bar', 'night_club'],
            'Museums': ['museum'],
            'Art Galleries': ['art_gallery'],
            'Shopping': ['shopping_mall', 'store'],
            'Outdoor Activities': ['park', 'zoo']
        }
        
        match_score = 0
        for interest in user_interests:
            mapped_types = interest_type_mapping.get(interest, [])
            if any(vtype in venue_types for vtype in mapped_types):
                match_score += 1
        
        return min(match_score / len(user_interests) if user_interests else 0, 1.0)
    
    def _calculate_similar_venue_score(self, venue: Dict, feedback_history: List[Dict]) -> float:
        """Calculate score based on similar venues user has rated"""
        if not feedback_history:
            return 0
        
        venue_types = set(venue.get('types', []))
        similar_ratings = []
        
        for feedback in feedback_history:
            # This is simplified - in a real system, you'd have venue type data for past ratings
            similar_ratings.append(feedback['rating'])
        
        if similar_ratings:
            avg_rating = sum(similar_ratings) / len(similar_ratings)
            return (avg_rating - 3) / 2  # Normalize to -1 to 1 scale
        
        return 0
    
    def _apply_basic_filters(self, recommendations: List[Dict], filters: Dict) -> List[Dict]:
        """Apply basic filters to recommendations"""
        filtered = recommendations
        
        # Budget filter
        budget = filters.get('budget', 'Any')
        if budget != 'Any':
            filtered = self._filter_by_budget(filtered, budget)
        
        # Rating filter
        min_rating = filters.get('min_rating', 0)
        if min_rating > 0:
            filtered = [r for r in filtered if (r.get('rating') or 0) >= min_rating]
        
        return filtered
    
    def _filter_by_budget(self, recommendations: List[Dict], budget: str) -> List[Dict]:
        """Filter by budget level"""
        budget_mapping = {"$": 1, "$$": 2, "$$$": 3, "$$$$": 4}
        max_price_level = budget_mapping.get(budget, 4)
        
        return [r for r in recommendations 
                if r.get('price_level') is None or r.get('price_level') <= max_price_level]
    
    def _filter_by_weather(self, recommendations: List[Dict], weather_analysis: Dict) -> List[Dict]:
        """Filter based on weather conditions"""
        if not weather_analysis.get('indoor_preferred'):
            return recommendations
        
        indoor_types = [
            'restaurant', 'bar', 'movie_theater', 'museum', 'shopping_mall',
            'bowling_alley', 'casino', 'night_club', 'spa', 'art_gallery', 'library'
        ]
        
        filtered = []
        for rec in recommendations:
            venue_types = rec.get('types', [])
            if any(vtype in indoor_types for vtype in venue_types):
                rec['weather_match'] = True
                filtered.append(rec)
            elif not any(vtype in ['park', 'zoo', 'amusement_park'] for vtype in venue_types):
                rec['weather_match'] = False
                filtered.append(rec)
        
        return filtered
    
    def _personalize_ranking(self, recommendations: List[Dict], user_profile: Dict) -> List[Dict]:
        """Personalize ranking based on user profile"""
        try:
            user_interests = user_profile.get('interests', [])
            
            # Calculate personalization scores
            for rec in recommendations:
                personalization_score = 0
                
                # Interest matching
                venue_types = rec.get('types', [])
                interest_match = self._calculate_interest_match(venue_types, user_interests)
                personalization_score += interest_match * 0.3
                
                # Update recommendation score
                base_score = rec.get('recommendation_score', rec.get('rating', 0))
                rec['recommendation_score'] = base_score + personalization_score
            
            # Sort by personalized score
            return sorted(recommendations, key=lambda x: x.get('recommendation_score', 0), reverse=True)
            
        except Exception as e:
            print(f"Error personalizing ranking: {str(e)}")
            return recommendations
    
    def _calculate_interest_match(self, venue_types: List[str], user_interests: List[str]) -> float:
        """Calculate how well venue matches user interests"""
        interest_type_mapping = {
            'Fine Dining': ['restaurant', 'meal_delivery'],
            'Bars & Nightlife': ['bar', 'night_club'],
            'Museums': ['museum'],
            'Art Galleries': ['art_gallery'],
            'Shopping': ['shopping_mall', 'store'],
            'Outdoor Activities': ['park', 'zoo']
        }
        
        match_score = 0
        for interest in user_interests:
            mapped_types = interest_type_mapping.get(interest, [])
            if any(vtype in venue_types for vtype in mapped_types):
                match_score += 1
        
        return min(match_score / len(user_interests) if user_interests else 0, 1.0)
