import streamlit as st
import pandas as pd
import logging
from typing import Dict, List
from services.weather_service import WeatherService
from utils.data_manager import DataManager
from utils.helpers import (
    format_rating, format_price_level, get_time_of_day, 
    get_day_context, filter_venues_by_budget, create_venue_card_html
)

# Set up debug logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RecommendationEngine:
    def __init__(self, qloo_service=None):
        logger.info("🎯 Initializing Recommendation Engine with Qloo-only service")
        self.qloo_service = qloo_service  # Use passed Qloo service
        self.weather_service = WeatherService()
        self.data_manager = DataManager()
        logger.info("✅ Recommendation Engine initialized")
    
    def show_recommendation_filters(self) -> Dict:
        """Display recommendation filters"""
        st.subheader("🎛️ Customize Your Recommendations")
        
        col1, col2 = st.columns(2)
        
        with col1:
            category_filter = st.selectbox(
                "Category",
                ["All", "Restaurants", "Bars", "Entertainment", "Culture", "Shopping", "Outdoor"],
                help="Filter by venue category"
            )
        
        with col2:
            time_filter = st.selectbox(
                "Time Context",
                ["Current Time", "Morning", "Afternoon", "Evening", "Night"]
            )
        
        # Advanced filters in expander
        with st.expander("Advanced Filters"):
            col1, col2 = st.columns(2)
            
            with col1:
                weather_aware = st.checkbox(
                    "Weather-Aware Recommendations",
                    value=True,
                    help="Consider current weather for indoor/outdoor suggestions"
                )
            
            with col2:
                min_rating = st.slider(
                    "Minimum Rating",
                    min_value=0.0,
                    max_value=5.0,
                    value=3.0,
                    step=0.5,
                    help="Minimum venue rating"
                )
                
                max_results = st.slider(
                    "Number of Results",
                    min_value=5,
                    max_value=50,
                    value=20,
                    help="Maximum number of recommendations"
                )
        
        return {
            'budget': 'Any',  # Default budget to Any since we removed the filter
            'category': category_filter,
            'distance': 5,  # Default distance since we removed the filter
            'time_context': time_filter if time_filter != "Current Time" else get_time_of_day(),
            'weather_aware': weather_aware,
            'min_rating': min_rating,
            'max_results': max_results
        }
    
    def get_recommendations(self, user_id: str, location: Dict, filters: Dict) -> List[Dict]:
        """Get recommendations using Qloo-only service"""
        logger.info("🎯 Getting recommendations from Qloo-only service")
        logger.info(f"👤 User ID: {user_id}")
        logger.info(f"📍 Location: {location}")
        logger.info(f"🔍 Filters: {filters}")
        
        try:
            st.info("🔍 Searching for recommendations from Qloo API...")
            
            if not self.qloo_service:
                logger.error("❌ No Qloo service available")
                st.error("❌ Qloo service not available")
                return []
            
            # Use Qloo-only service
            recommendations = self.qloo_service.get_recommendations(user_id, location, filters)
            
            logger.info(f"✅ Retrieved {len(recommendations)} recommendations from Qloo API")
            
            if not recommendations:
                st.warning("❌ No recommendations found from Qloo API. Check the logs for detailed API responses.")
                logger.warning("⚠️ No recommendations returned from Qloo API")
                return []
            
            # Log sample recommendations
            for i, rec in enumerate(recommendations[:3], 1):
                logger.debug(f"📋 Recommendation {i}: {rec.get('name')} (Score: {rec.get('recommendation_score', 0):.2f})")
            
            st.success(f"✅ Found {len(recommendations)} recommendations from Qloo API!")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"❌ Error getting recommendations: {str(e)}")
            st.error(f"❌ Error getting recommendations: {str(e)}")
            return []
            return self._get_fallback_recommendations(location, filters)
    
    def _enrich_recommendations(self, recommendations: List[Dict]) -> List[Dict]:
        """Enrich recommendations with additional details"""
        enriched = []
        
        for rec in recommendations:
            try:
                # Get detailed place information if we have a place_id
                place_id = rec.get('place_id')
                if place_id:
                    details = self.places_service.get_place_details(place_id)
                    if details:
                        # Merge the details
                        enriched_rec = {
                            **rec,
                            'address': details.get('formatted_address', rec.get('vicinity', '')),
                            'phone': details.get('formatted_phone_number'),
                            'website': details.get('website'),
                            'opening_hours': details.get('opening_hours', {}).get('weekday_text', []),
                            'google_rating': details.get('rating', rec.get('rating')),
                            'google_reviews': len(details.get('reviews', [])),
                            'photos': details.get('photos', rec.get('photos', []))
                        }
                        enriched.append(enriched_rec)
                    else:
                        enriched.append(rec)
                else:
                    enriched.append(rec)
                    
            except Exception as e:
                print(f"Error enriching recommendation: {str(e)}")
                enriched.append(rec)
        
        return enriched
    
    def _get_fallback_recommendations(self, location: Dict, filters: Dict) -> List[Dict]:
        """Fallback recommendations using direct Google Places search"""
        try:
            st.info("🔄 Using fallback recommendation method...")
            
            # Simple category-based search
            category = filters.get('category', 'All')
            if category == 'All':
                search_type = 'restaurant'
            else:
                type_mapping = {
                    'Restaurants': 'restaurant',
                    'Bars': 'bar',
                    'Entertainment': 'movie_theater',
                    'Culture': 'museum',
                    'Shopping': 'shopping_mall',
                    'Outdoor': 'park'
                }
                search_type = type_mapping.get(category, 'restaurant')
            
            # Search for places
            places = self.places_service.search_nearby_places(
                location, search_type, filters.get('distance', 5) * 1000
            )
            
            # Format as recommendations
            recommendations = []
            for place in places[:filters.get('max_results', 20)]:
                rec = {
                    'id': place.get('place_id', ''),
                    'name': place.get('name', 'Unknown Venue'),
                    'rating': place.get('rating'),
                    'price_level': place.get('price_level'),
                    'types': place.get('types', []),
                    'vicinity': place.get('vicinity', ''),
                    'geometry': place.get('geometry', {}),
                    'photos': place.get('photos', []),
                    'place_id': place.get('place_id'),
                    'source': 'fallback'
                }
                recommendations.append(rec)
            
            return recommendations
            
        except Exception as e:
            st.error(f"Fallback recommendations failed: {str(e)}")
            return []
    
    def show_recommendations(self, recommendations: List[Dict], user_id: str):
        """Display recommendations with rating interface"""
        if not recommendations:
            st.warning("No recommendations found. Try adjusting your filters.")
            return
        
        st.subheader(f"🎯 Found {len(recommendations)} Recommendations")
        
        # Show recommendation sources
        sources = {}
        for rec in recommendations:
            source = rec.get('source', 'unknown')
            sources[source] = sources.get(source, 0) + 1
        
        if len(sources) > 1:
            source_info = ", ".join([f"{count} from {source}" for source, count in sources.items()])
            st.info(f"📊 Recommendations: {source_info}")
        
        # Display mode selector
        display_mode = st.radio(
            "Display Mode",
            ["List", "Map"],
            horizontal=True
        )
        
        if display_mode == "List":
            self._show_list_view(recommendations, user_id)
        else:
            self._show_map_view(recommendations)
    
    
    def _show_list_view(self, recommendations: List[Dict], user_id: str):
        """Show recommendations in list view"""
        # Create DataFrame for display
        display_data = []
        for venue in recommendations:
            display_data.append({
                'Name': venue.get('name', 'Unknown'),
                'Rating': venue.get('google_rating', venue.get('rating', 'N/A')),
                'Phone': venue.get('phone', 'Not available'),
                'Website': venue.get('website', 'Not available'),
                'Address': venue.get('address', venue.get('vicinity', 'N/A')),
                'Source': venue.get('source', 'unknown')
            })
        
        df = pd.DataFrame(display_data)
        st.dataframe(df, use_container_width=True)
        
        # Quick rating interface
        st.subheader("Quick Rating")
        selected_venue = st.selectbox("Select venue to rate:", [v['name'] for v in recommendations])
        
        col1, col2 = st.columns(2)
        with col1:
            quick_rating = st.slider("Rating", 1, 5, 3)
        with col2:
            if st.button("Submit Quick Rating"):
                venue_idx = next(i for i, v in enumerate(recommendations) if v['name'] == selected_venue)
                venue = recommendations[venue_idx]
                venue_id = venue.get('place_id', venue.get('id', venue.get('name')))
                
                if self.data_manager.add_user_feedback(user_id, venue_id, quick_rating):
                    st.success("Rating saved!")
                    self._update_recommendation_feedback(user_id, venue, quick_rating)
                else:
                    st.error("Failed to save rating")
    
    def _show_map_view(self, recommendations: List[Dict]):
        """Show recommendations on map"""
        try:
            from components.map_view import MapVisualization
            map_viz = MapVisualization()
            map_viz.show_interactive_map(recommendations)
            
        except ImportError:
            st.error("Map view requires folium and streamlit-folium. Please install them.")
        except Exception as e:
            st.error(f"Error displaying map: {str(e)}")
    
    def _update_recommendation_feedback(self, user_id: str, venue: Dict, rating: int):
        """Update recommendation system with user feedback"""
        try:
            # This would typically update the ML model or recommendation weights
            # For now, we just store it in the user's feedback history
            pass
        except Exception as e:
            print(f"Error updating recommendation feedback: {str(e)}")
    
    def show_weather_context(self, location):
        """Show current weather context - handles both string locations and coordinate dicts"""
        try:
            from utils.location_mapper import LocationMapper
            
            # Convert location to coordinates if needed
            coordinates = LocationMapper.get_coordinates(location)
            if not coordinates:
                st.warning(f"Weather data not available for location: {LocationMapper.get_city_name(location)}")
                return
            
            city_name = LocationMapper.get_city_name(location)
            st.write(f"📍 Weather for: **{city_name}**")
            
            weather_data = self.weather_service.get_current_weather(coordinates['lat'], coordinates['lng'])
            if weather_data:
                weather_analysis = self.weather_service.analyze_weather_for_recommendations(weather_data)
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    temp = weather_data['main']['temp']
                    st.metric("Temperature", f"{temp:.1f}°C")
                
                with col2:
                    condition = weather_data['weather'][0]['main']
                    st.metric("Condition", condition)
                
                with col3:
                    if weather_analysis['indoor_preferred']:
                        st.metric("Recommendation", "Indoor venues preferred")
                    else:
                        st.metric("Recommendation", "Great for outdoor activities")
                
                if weather_analysis['weather_context'] != 'unknown':
                    st.info(f"Current weather: {weather_analysis['weather_context']}")
                    
        except Exception as e:
            st.warning("Unable to fetch weather data")
            print(f"Weather error: {str(e)}")
    
    def show_recommendation_tips(self):
        """Show tips for getting better recommendations"""
        with st.expander("💡 Tips for Better Recommendations"):
            st.markdown("""
            **To get better recommendations:**
            
            1. **Complete your profile** - Add interests and past venues you enjoyed
            2. **Rate venues** - Your ratings help improve future suggestions
            3. **Use filters** - Adjust budget, distance, and category filters
            4. **Enable weather awareness** - Get indoor/outdoor suggestions based on weather
            5. **Try different categories** - Explore various types of venues
            6. **Adjust distance** - Increase radius to find more options
            
            **If you're not seeing results:**
            - Try increasing the distance filter
            - Lower the minimum rating threshold
            - Select "All" for category to see more variety
            - Check your internet connection
            """)
