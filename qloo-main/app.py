import streamlit as st
import os
import logging
from typing import Dict, Tuple

# Set up debug logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import components
from components.user_profile import UserProfileManager
from components.recommendations import RecommendationEngine
from components.map_view import MapVisualization
from services.qloo_only_recommendation_service import QlooOnlyRecommendationService
from utils.helpers import show_api_key_status, get_user_location
from config.settings import Config

logger.info("🎯 Starting Entertainment Recommender with Qloo-Only Data")

# Page configuration
st.set_page_config(
    page_title="Entertainment Recommender",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 0.5rem 0;
    }
    
    .venue-card {
        border: 1px solid #ddd;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        background-color: white;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .sidebar .sidebar-content {
        background-color: #f8f9fa;
    }
    
    .stButton > button {
        width: 100%;
        border-radius: 20px;
        border: none;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    .stSelectbox > div > div {
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

class EntertainmentRecommenderApp:
    def __init__(self):
        logger.info("🎯 Initializing Entertainment Recommender App")
        self.profile_manager = UserProfileManager()
        self.qloo_service = QlooOnlyRecommendationService()  # Use Qloo-only service
        self.recommendation_engine = RecommendationEngine(self.qloo_service)
        self.map_viz = MapVisualization()
        
        # Initialize session state
        if 'user_location' not in st.session_state:
            st.session_state.user_location = None
        if 'current_recommendations' not in st.session_state:
            st.session_state.current_recommendations = []
        
        logger.info("✅ Entertainment Recommender App initialized with Qloo-only data")
    
    def run(self):
        """Main application runner"""
        # Header
        st.markdown("""
        <div class="main-header">
            <h1>🎯 Entertainment Recommender</h1>
            <p>Discover personalized entertainment venues powered by Qloo's Taste AI™</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Sidebar
        self.show_sidebar()
        
        # Main content
        self.show_main_content()
    
    def show_sidebar(self):
        """Display sidebar with navigation and settings"""
        with st.sidebar:
            st.title("🎛️ Control Panel")
            
            # API Status
            show_api_key_status()
            
            st.divider()
            
            # Navigation
            current_page = st.session_state.get('current_page', '🏠 Home')
            page = st.selectbox(
                "Navigate to:",
                ["🏠 Home", "👤 Profile", "🗂️ Profile Management", "🎯 Recommendations", "🗺️ Map View", "📊 Analytics", "🧪 Debug"],
                index=["🏠 Home", "👤 Profile", "🗂️ Profile Management", "🎯 Recommendations", "🗺️ Map View", "📊 Analytics", "🧪 Debug"].index(current_page) if current_page in ["🏠 Home", "👤 Profile", "🗂️ Profile Management", "🎯 Recommendations", "🗺️ Map View", "📊 Analytics", "🧪 Debug"] else 0
            )
            
            # Update current page only if selectbox changed
            if page != current_page:
                st.session_state.current_page = page
            
            st.divider()
            
            # Location Settings
            st.subheader("📍 Location")
            
            # Location dropdown instead of coordinates
            location_options = [
                "SanFrancisco",
                "New York", 
                "Los Angeles",
                "Chicago",
                "Miami",
                "Seattle",
                "Boston",
                "Austin",
                "Denver",
                "Portland"
            ]
            
            selected_location = st.selectbox(
                "Select Location:",
                location_options,
                index=0  # SanFrancisco as default
            )
            
            # Store selected location in session state
            st.session_state.user_location = selected_location
            
            st.info(f"🎯 Using Qloo v2/insights API with location: **{selected_location}**")
            
            # Custom location option
            with st.expander("🌍 Custom Location"):
                custom_location = st.text_input(
                    "Enter custom location name:",
                    placeholder="e.g., Las Vegas, Tokyo, London"
                )
                if custom_location:
                    st.session_state.user_location = custom_location
                    st.success(f"✅ Custom location set: {custom_location}")
            
            st.divider()
            
            # Quick Stats
            if 'user_id' in st.session_state:
                self.show_quick_stats()
                
                st.divider()
                
                # Profile Actions
                st.subheader("👤 Profile Actions")
                
                # Show current user
                try:
                    from utils.data_manager import DataManager
                    data_manager = DataManager()
                    current_profile = data_manager.load_user_profile(st.session_state.user_id)
                    if current_profile:
                        st.write(f"**Current User:** {current_profile.get('name', 'Unknown')}")
                except:
                    pass
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("🔄 Switch Profile"):
                        st.session_state.current_page = "🗂️ Profile Management"
                        st.rerun()
                
                with col2:
                    if st.button("🚪 Logout"):
                        # Clear user session
                        if 'user_id' in st.session_state:
                            del st.session_state.user_id
                        if 'current_recommendations' in st.session_state:
                            del st.session_state.current_recommendations
                        st.success("Logged out successfully!")
                        st.rerun()
    
    def show_location_input(self):
        """Show location input interface"""
        st.write("Enter your location:")
        
        col1, col2 = st.columns(2)
        with col1:
            lat = st.number_input("Latitude", value=37.7749, format="%.6f")
        with col2:
            lng = st.number_input("Longitude", value=-122.4194, format="%.6f")
        
        if st.button("Set Location"):
            st.session_state.user_location = {'lat': lat, 'lng': lng}
            st.success(f"Location set to: {lat:.4f}, {lng:.4f}")
    
    def show_quick_stats(self):
        """Show quick user statistics"""
        try:
            from utils.data_manager import DataManager
            data_manager = DataManager()
            stats = data_manager.get_user_statistics(st.session_state.user_id)
            
            st.subheader("📊 Your Stats")
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total Ratings", stats.get('total_ratings', 0))
            with col2:
                avg_rating = stats.get('average_rating', 0)
                st.metric("Avg Rating", f"{avg_rating:.1f}" if avg_rating else "N/A")
            
        except Exception as e:
            st.error(f"Error loading stats: {str(e)}")
    
    def show_main_content(self):
        """Display main content based on current page"""
        page = st.session_state.get('current_page', '🏠 Home')
        
        if page == "🏠 Home":
            self.show_home_page()
        elif page == "👤 Profile":
            self.show_profile_page()
        elif page == "🗂️ Profile Management":
            self.show_profile_management_page()
        elif page == "🎯 Recommendations":
            self.show_recommendations_page()
        elif page == "🗺️ Map View":
            self.show_map_page()
        elif page == "📊 Analytics":
            self.show_analytics_page()
        elif page == "🧪 Debug":
            self.show_debug_page()
    
    def show_home_page(self):
        """Display home page"""
        # Check if user has a profile
        if 'user_id' not in st.session_state:
            st.info("👋 Welcome! Let's start by creating your taste profile.")
            
            # Get or create profile
            user_id = self.profile_manager.get_or_create_profile()
            
            if user_id:
                st.session_state.user_id = user_id
                st.rerun()
        else:
            # Show welcome back message
            self.profile_manager.show_profile_summary(st.session_state.user_id)
            
            st.divider()
            
            # Quick actions
            st.subheader("🚀 Quick Actions")
            
            # Explain what Get Recommendations does
            st.info("""
            **🎯 Get Recommendations** - This will take you to the Recommendations page where you can:
            - Apply filters (budget, category, distance, weather-aware)
            - Get personalized venue suggestions based on your profile
            - View results in cards, list, or map format
            - Rate venues to improve future recommendations
            """)
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("🎯 Get Recommendations", type="primary"):
                    st.session_state.current_page = "🎯 Recommendations"
                    st.rerun()
            
            with col2:
                if st.button("🗺️ View Map"):
                    st.session_state.current_page = "🗺️ Map View"
                    st.rerun()
            
            with col3:
                if st.button("👤 Edit Profile"):
                    st.session_state.current_page = "👤 Profile"
                    st.rerun()
            
            st.divider()
            
            # Show weather context if location is available
            if st.session_state.user_location:
                st.subheader("🌤️ Current Weather Context")
                self.recommendation_engine.show_weather_context(st.session_state.user_location)
            
            # Recent activity or getting started tips
            self.show_getting_started_tips()
    
    def show_profile_page(self):
        """Display profile management page"""
        if 'user_id' not in st.session_state:
            st.warning("Please create a profile first.")
            user_id = self.profile_manager.get_or_create_profile()
            if user_id:
                st.session_state.user_id = user_id
                st.rerun()
        else:
            tab1, tab2 = st.tabs(["View Profile", "Edit Profile"])
            
            with tab1:
                self.profile_manager.show_profile_summary(st.session_state.user_id)
            
            with tab2:
                self.profile_manager.show_profile_editor(st.session_state.user_id)
    
    def show_profile_management_page(self):
        """Display profile management page"""
        st.header("🗂️ Profile Management")
        st.write("Manage all user profiles - view, select, or delete profiles.")
        
        try:
            self.profile_manager.show_profile_management()
        except Exception as e:
            st.error(f"Error loading profile management: {str(e)}")
    
    def show_recommendations_page(self):
        """Display recommendations page with AI assistant"""
        if 'user_id' not in st.session_state:
            st.warning("Please create a profile first to get personalized recommendations.")
            return
        
        if not st.session_state.user_location:
            st.warning("Please set your location in the sidebar to get recommendations.")
            return
        
        st.header("🎯 Personalized Recommendations")
        
        # Create main layout with AI assistant
        main_col, ai_col = st.columns([0.7, 0.3])
        
        with main_col:
            # Show current status
            with st.expander("ℹ️ How Recommendations Work - QLOO API ONLY!"):
                st.write("""
                **🎯 QLOO API ONLY MODE ACTIVE!**
                
                **Current Recommendation System:**
                1. **🎯 Qloo API ONLY**: All data comes directly from Qloo's hackathon API
                2. **🚫 NO DEMO DATA**: Demo data has been completely removed
                3. **🔍 Multiple Methods**: Tries venue search, category search, and entity search
                4. **🌤️ Weather Integration**: Real-time weather-aware filtering (if available)
                5. **🎨 Personalization**: Based on your interests + Qloo category matching
                
                **Debug Information:**
                - ✅ **Authentication**: Tested on service initialization
                - ✅ **API Calls**: All requests/responses logged in detail
                - ✅ **Data Source**: 100% Qloo API data
                - ✅ **Fallback Methods**: Multiple API approaches attempted
                
                **Check the console logs for detailed Qloo API request/response information!**
                """)
            
            # Show filters
            filters = self.recommendation_engine.show_recommendation_filters()
            
            # Get recommendations button
            if st.button("🔍 Get Recommendations", type="primary"):
                with st.spinner("Finding personalized recommendations..."):
                    try:
                        st.write("🔍 **Debug Info:**")
                        st.write(f"- User ID: {st.session_state.user_id}")
                        st.write(f"- Location: {st.session_state.user_location}")
                        st.write(f"- Filters: {filters}")
                        
                        recommendations = self.recommendation_engine.get_recommendations(
                            st.session_state.user_id,
                            st.session_state.user_location,
                            filters
                        )
                        st.session_state.current_recommendations = recommendations
                        
                        if recommendations:
                            st.success(f"✅ Found {len(recommendations)} recommendations!")
                        else:
                            st.warning("No recommendations found. Try adjusting your filters.")
                            
                    except Exception as e:
                        st.error(f"Error getting recommendations: {str(e)}")
                        st.session_state.current_recommendations = []
            
            # Display recommendations
            if st.session_state.current_recommendations:
                self.recommendation_engine.show_recommendations(
                    st.session_state.current_recommendations,
                    st.session_state.user_id
                )
            else:
                st.info("Click '🔍 Get Recommendations' to see personalized venue suggestions!")
        
        with ai_col:
            # AI Assistant
            from components.ai_assistant import render_ai_assistant
            
            # Prepare data for AI assistant
            recommendations_data = None
            user_preferences = None
            
            if st.session_state.current_recommendations:
                recommendations_data = {
                    'venues': st.session_state.current_recommendations,
                    'filters': filters if 'filters' in locals() else {}
                }
            
            # Get user preferences from profile
            try:
                from utils.data_manager import DataManager
                data_manager = DataManager()
                user_profile = data_manager.load_user_profile(st.session_state.user_id)
                if user_profile:
                    user_preferences = {
                        'interests': user_profile.get('interests', []),
                        'dietary_restrictions': user_profile.get('dietary_restrictions', []),
                        'past_venues': user_profile.get('past_venues', [])
                    }
            except Exception as e:
                st.error(f"Error loading user preferences: {str(e)}")
            
            # Render AI assistant
            render_ai_assistant(recommendations_data, user_preferences)
    
    def show_map_page(self):
        """Display map page"""
        st.header("🗺️ Venue Map")
        
        if not st.session_state.current_recommendations:
            st.info("Get some recommendations first to see them on the map!")
            
            if st.button("🎯 Go to Recommendations"):
                st.session_state.current_page = "🎯 Recommendations"
                st.rerun()
        else:
            # Map display options
            map_type = st.selectbox(
                "Map Type:",
                ["Standard View", "Clustered View", "Heatmap"]
            )
            
            if map_type == "Standard View":
                self.map_viz.show_interactive_map(
                    st.session_state.current_recommendations,
                    st.session_state.user_location
                )
            elif map_type == "Clustered View":
                self.map_viz.show_venue_clusters(
                    st.session_state.current_recommendations,
                    st.session_state.user_location
                )
            else:  # Heatmap
                heatmap = self.map_viz.create_heatmap(
                    st.session_state.current_recommendations,
                    st.session_state.user_location
                )
                if heatmap:
                    from streamlit_folium import st_folium
                    st_folium(heatmap, width=700, height=500)
    
    def show_analytics_page(self):
        """Display analytics and insights page"""
        if 'user_id' not in st.session_state:
            st.warning("Please create a profile first to see analytics.")
            return
        
        st.header("📊 Your Taste Analytics")
        
        try:
            from utils.data_manager import DataManager
            import pandas as pd
            import plotly.express as px
            
            data_manager = DataManager()
            
            # Get user data
            profile = data_manager.load_user_profile(st.session_state.user_id)
            feedback_history = data_manager.get_user_feedback_history(st.session_state.user_id)
            stats = data_manager.get_user_statistics(st.session_state.user_id)
            
            if not feedback_history:
                st.info("Start rating venues to see your taste analytics!")
                return
            
            # Overview metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Ratings", stats.get('total_ratings', 0))
            
            with col2:
                avg_rating = stats.get('average_rating', 0)
                st.metric("Average Rating", f"{avg_rating:.1f}" if avg_rating else "N/A")
            
            with col3:
                favorites = stats.get('favorite_venues', [])
                st.metric("Favorite Venues", len(favorites))
            
            with col4:
                last_activity = stats.get('last_activity', '')
                if last_activity:
                    st.metric("Last Activity", last_activity[:10])
            
            st.divider()
            
            # Rating distribution
            if feedback_history:
                df = pd.DataFrame(feedback_history)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("Rating Distribution")
                    rating_counts = df['rating'].value_counts().sort_index()
                    fig = px.bar(
                        x=rating_counts.index,
                        y=rating_counts.values,
                        labels={'x': 'Rating', 'y': 'Count'},
                        title="Your Rating Distribution"
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    st.subheader("Rating Trends")
                    df['timestamp'] = pd.to_datetime(df['timestamp'])
                    df_sorted = df.sort_values('timestamp')
                    
                    fig = px.line(
                        df_sorted,
                        x='timestamp',
                        y='rating',
                        title="Your Rating Trends Over Time"
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
            # Preferences insights
            st.subheader("Your Preferences")
            interests = profile.get('interests', [])
            if interests:
                st.write("**Your Interests:**")
                for interest in interests:
                    st.write(f"• {interest}")
            
            # Favorite venues
            favorites = stats.get('favorite_venues', [])
            if favorites:
                st.subheader("Your Favorite Venues")
                st.write(f"You've rated {len(favorites)} venues with 4+ stars!")
            
        except Exception as e:
            st.error(f"Error loading analytics: {str(e)}")
    
    def show_getting_started_tips(self):
        """Show getting started tips for new users"""
        st.subheader("💡 Getting Started")
        
        tips = [
            "🎯 **Get Recommendations**: Click 'Get Recommendations' to discover venues tailored to your taste",
            "🗺️ **Explore on Map**: View all recommendations on an interactive map",
            "⭐ **Rate Venues**: Rate venues you visit to improve future recommendations",
            "🌤️ **Weather-Aware**: Enable weather-aware recommendations for better suggestions",
            "💰 **Budget Filter**: Use budget filters to find venues in your price range",
            "📊 **Track Progress**: Check your analytics to see your taste evolution"
        ]
        
        for tip in tips:
            st.markdown(tip)

def main():
    """Main application entry point"""
    try:
        app = EntertainmentRecommenderApp()
        app.run()
    except Exception as e:
        st.error(f"Application error: {str(e)}")
        st.info("Please check your configuration and API keys.")

if __name__ == "__main__":
    main()
