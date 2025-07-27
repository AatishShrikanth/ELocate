import streamlit as st
import hashlib
from datetime import datetime, time
from typing import Dict, List, Tuple
import requests

def generate_user_id(name: str, email: str = "") -> str:
    """Generate a unique user ID based on name and email"""
    unique_string = f"{name.lower()}_{email.lower()}_{datetime.now().date()}"
    return hashlib.md5(unique_string.encode()).hexdigest()[:12]

def get_time_of_day() -> str:
    """Get current time context"""
    current_time = datetime.now().time()
    
    if time(6, 0) <= current_time < time(12, 0):
        return "morning"
    elif time(12, 0) <= current_time < time(17, 0):
        return "afternoon"
    elif time(17, 0) <= current_time < time(21, 0):
        return "evening"
    else:
        return "night"

def get_day_context() -> str:
    """Get day context (weekday/weekend)"""
    today = datetime.now().weekday()
    return "weekend" if today >= 5 else "weekday"

def format_price_level(price_level: int) -> str:
    """Convert price level to dollar signs"""
    if price_level is None:
        return "Price not available"
    
    price_map = {1: "$", 2: "$$", 3: "$$$", 4: "$$$$"}
    return price_map.get(price_level, "Unknown")

def format_rating(rating: float) -> str:
    """Format rating with stars"""
    if rating is None:
        return "No rating"
    
    stars = "⭐" * int(rating)
    return f"{stars} ({rating:.1f})"

def get_user_location() -> Tuple[float, float]:
    """Get user's current location (placeholder - in real app would use geolocation)"""
    # Default to San Francisco coordinates
    # In a real app, you'd use browser geolocation or IP-based location
    return 37.7749, -122.4194

def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
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

def filter_venues_by_budget(venues: List[Dict], budget_filter: str) -> List[Dict]:
    """Filter venues by budget"""
    if budget_filter == "Any":
        return venues
    
    budget_mapping = {"$": 1, "$$": 2, "$$$": 3, "$$$$": 4}
    max_price_level = budget_mapping.get(budget_filter, 4)
    
    filtered = []
    for venue in venues:
        venue_price = venue.get('price_level')
        if venue_price is None or venue_price <= max_price_level:
            filtered.append(venue)
    
    return filtered

def get_venue_image_url(venue: Dict) -> str:
    """Get venue image URL from photos"""
    photos = venue.get('photos', [])
    if photos and len(photos) > 0:
        photo_ref = photos[0].get('photo_reference')
        if photo_ref:
            from config.settings import Config
            return f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photoreference={photo_ref}&key={Config.GOOGLE_PLACES_API_KEY}"
    
    # Return placeholder image if no photo available
    return "https://via.placeholder.com/400x300?text=No+Image+Available"

def create_venue_card_html(venue: Dict) -> str:
    """Create HTML for venue card display"""
    name = venue.get('name', 'Unknown Venue')
    rating = venue.get('google_rating', venue.get('rating'))
    price_level = venue.get('price_level')
    address = venue.get('address', 'Address not available')
    image_url = get_venue_image_url(venue)
    
    rating_display = format_rating(rating) if rating else "No rating"
    price_display = format_price_level(price_level)
    
    return f"""
    <div style="border: 1px solid #ddd; border-radius: 10px; padding: 15px; margin: 10px 0; background-color: white;">
        <img src="{image_url}" style="width: 100%; height: 200px; object-fit: cover; border-radius: 5px;" />
        <h3 style="margin: 10px 0 5px 0; color: #333;">{name}</h3>
        <p style="margin: 5px 0; color: #666;"><strong>Rating:</strong> {rating_display}</p>
        <p style="margin: 5px 0; color: #666;"><strong>Price:</strong> {price_display}</p>
        <p style="margin: 5px 0; color: #666; font-size: 0.9em;">{address}</p>
    </div>
    """

def validate_api_keys() -> Dict[str, bool]:
    """Validate that all required API keys are present"""
    from config.settings import Config
    
    return {
        'qloo': bool(Config.QLOO_API_KEY),
        'google_places': bool(Config.GOOGLE_PLACES_API_KEY),
        'openweather': bool(Config.OPENWEATHER_API_KEY)
    }

def show_api_key_status():
    """Display API key status in Streamlit"""
    api_status = validate_api_keys()
    
    st.sidebar.subheader("API Status")
    for service, status in api_status.items():
        status_icon = "✅" if status else "❌"
        st.sidebar.write(f"{status_icon} {service.replace('_', ' ').title()}")
    
    if not all(api_status.values()):
        st.sidebar.warning("Some API keys are missing. Check your .env file.")

def safe_get_nested(data: Dict, keys: List[str], default=None):
    """Safely get nested dictionary values"""
    for key in keys:
        if isinstance(data, dict) and key in data:
            data = data[key]
        else:
            return default
    return data
