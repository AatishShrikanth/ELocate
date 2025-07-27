"""
Location mapping utility to convert city names to coordinates for weather API
"""

class LocationMapper:
    """Maps city names to coordinates for weather API calls"""
    
    # Predefined coordinates for common cities
    CITY_COORDINATES = {
        "SanFrancisco": {"lat": 37.7749, "lng": -122.4194},
        "San Francisco": {"lat": 37.7749, "lng": -122.4194},  # Keep both for compatibility
        "New York": {"lat": 40.7128, "lng": -74.0060},
        "Los Angeles": {"lat": 34.0522, "lng": -118.2437},
        "Chicago": {"lat": 41.8781, "lng": -87.6298},
        "Miami": {"lat": 25.7617, "lng": -80.1918},
        "Seattle": {"lat": 47.6062, "lng": -122.3321},
        "Boston": {"lat": 42.3601, "lng": -71.0589},
        "Austin": {"lat": 30.2672, "lng": -97.7431},
        "Denver": {"lat": 39.7392, "lng": -104.9903},
        "Portland": {"lat": 45.5152, "lng": -122.6784},
        
        # Additional cities for custom locations
        "Las Vegas": {"lat": 36.1699, "lng": -115.1398},
        "Tokyo": {"lat": 35.6762, "lng": 139.6503},
        "London": {"lat": 51.5074, "lng": -0.1278},
        "Paris": {"lat": 48.8566, "lng": 2.3522},
        "Berlin": {"lat": 52.5200, "lng": 13.4050},
        "Sydney": {"lat": -33.8688, "lng": 151.2093},
        "Toronto": {"lat": 43.6532, "lng": -79.3832},
        "Vancouver": {"lat": 49.2827, "lng": -123.1207},
        "Montreal": {"lat": 45.5017, "lng": -73.5673},
        "Mexico City": {"lat": 19.4326, "lng": -99.1332},
    }
    
    @classmethod
    def get_coordinates(cls, location_input):
        """
        Get coordinates from location input
        
        Args:
            location_input: Can be a string (city name) or dict with lat/lng
            
        Returns:
            Dict with lat/lng coordinates or None if not found
        """
        if not location_input:
            return None
            
        # If already coordinates
        if isinstance(location_input, dict) and 'lat' in location_input and 'lng' in location_input:
            return location_input
            
        # If string, look up in mapping
        if isinstance(location_input, str):
            # Try exact match first
            if location_input in cls.CITY_COORDINATES:
                return cls.CITY_COORDINATES[location_input]
            
            # Try case-insensitive match
            for city, coords in cls.CITY_COORDINATES.items():
                if city.lower() == location_input.lower():
                    return coords
            
            # Try partial match
            for city, coords in cls.CITY_COORDINATES.items():
                if location_input.lower() in city.lower() or city.lower() in location_input.lower():
                    return coords
        
        return None
    
    @classmethod
    def get_city_name(cls, location_input):
        """
        Get city name from location input
        
        Args:
            location_input: Can be a string (city name) or dict with lat/lng
            
        Returns:
            String city name or "Unknown Location"
        """
        if not location_input:
            return "Unknown Location"
            
        # If string, return as is
        if isinstance(location_input, str):
            return location_input
            
        # If coordinates, try to find matching city
        if isinstance(location_input, dict) and 'lat' in location_input and 'lng' in location_input:
            target_lat = location_input['lat']
            target_lng = location_input['lng']
            
            # Find closest city (simple distance calculation)
            min_distance = float('inf')
            closest_city = "Unknown Location"
            
            for city, coords in cls.CITY_COORDINATES.items():
                distance = ((target_lat - coords['lat']) ** 2 + (target_lng - coords['lng']) ** 2) ** 0.5
                if distance < min_distance:
                    min_distance = distance
                    closest_city = city
            
            # If very close (within ~0.1 degrees), return the city name
            if min_distance < 0.1:
                return closest_city
            else:
                return f"Custom Location ({target_lat:.4f}, {target_lng:.4f})"
        
        return "Unknown Location"
    
    @classmethod
    def is_supported_location(cls, location_input):
        """
        Check if location is supported (has coordinates)
        
        Args:
            location_input: Location to check
            
        Returns:
            Boolean indicating if location is supported
        """
        return cls.get_coordinates(location_input) is not None
    
    @classmethod
    def get_supported_cities(cls):
        """
        Get list of all supported city names
        
        Returns:
            List of supported city names
        """
        return list(cls.CITY_COORDINATES.keys())
