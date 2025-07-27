import streamlit as st
from typing import Dict, List, Tuple
import folium
from streamlit_folium import st_folium
from utils.helpers import format_rating, format_price_level
from utils.location_mapper import LocationMapper

class MapVisualization:
    def __init__(self):
        self.default_location = [37.7749, -122.4194]  # San Francisco
    
    def _get_location_coordinates(self, location):
        """Convert location input to coordinates for mapping"""
        if not location:
            return None
            
        # If already a dict with lat/lng, return as list
        if isinstance(location, dict) and 'lat' in location and 'lng' in location:
            return [location['lat'], location['lng']]
        
        # If string, use LocationMapper to get coordinates
        if isinstance(location, str):
            coords = LocationMapper.get_coordinates(location)
            if coords:
                return [coords['lat'], coords['lng']]
        
        return None
    
    def create_recommendations_map(self, 
                                 recommendations: List[Dict], 
                                 user_location = None) -> folium.Map:
        """Create a map with venue recommendations"""
        try:
            # Determine map center
            user_coords = self._get_location_coordinates(user_location)
            if user_coords:
                center = user_coords
            elif recommendations and self._has_valid_location(recommendations[0]):
                first_venue = recommendations[0]
                location = first_venue['geometry']['location']
                center = [location['lat'], location['lng']]
            else:
                center = self.default_location
            
            # Create map
            m = folium.Map(
                location=center,
                zoom_start=13,
                tiles='OpenStreetMap'
            )
            
            # Add user location marker if available
            if user_coords:
                folium.Marker(
                    user_coords,
                    popup="Your Location",
                    tooltip="You are here",
                    icon=folium.Icon(color='blue', icon='user', prefix='fa')
                ).add_to(m)
            
            # Add venue markers
            for i, venue in enumerate(recommendations):
                if self._has_valid_location(venue):
                    self._add_venue_marker(m, venue, i)
            
            return m
            
        except Exception as e:
            st.error(f"Error creating map: {str(e)}")
            return None
    
    def _has_valid_location(self, venue: Dict) -> bool:
        """Check if venue has valid location data"""
        geometry = venue.get('geometry', {})
        location = geometry.get('location', {})
        return 'lat' in location and 'lng' in location
    
    def _add_venue_marker(self, map_obj: folium.Map, venue: Dict, index: int):
        """Add a venue marker to the map"""
        try:
            location = venue['geometry']['location']
            
            # Create popup content
            popup_content = self._create_popup_content(venue, index)
            
            # Determine marker color based on rating
            rating = venue.get('google_rating', venue.get('rating', 0))
            marker_color = self._get_marker_color(rating)
            
            # Create marker
            folium.Marker(
                [location['lat'], location['lng']],
                popup=folium.Popup(popup_content, max_width=350),
                tooltip=venue.get('name', f'Venue {index + 1}'),
                icon=folium.Icon(
                    color=marker_color,
                    icon='star',
                    prefix='fa'
                )
            ).add_to(map_obj)
            
        except Exception as e:
            print(f"Error adding marker for venue {venue.get('name', 'Unknown')}: {str(e)}")
    
    def _create_popup_content(self, venue: Dict, index: int) -> str:
        """Create HTML content for venue popup"""
        name = venue.get('name', f'Venue {index + 1}')
        rating = venue.get('google_rating', venue.get('rating'))
        price_level = venue.get('price_level')
        address = venue.get('address', venue.get('vicinity', 'Address not available'))
        phone = venue.get('phone', '')
        website = venue.get('website', '')
        
        # Format rating and price
        rating_display = format_rating(rating) if rating else "No rating available"
        price_display = format_price_level(price_level)
        
        # Build popup HTML
        popup_html = f"""
        <div style="width: 300px; font-family: Arial, sans-serif;">
            <h4 style="margin: 0 0 10px 0; color: #333; font-size: 16px;">{name}</h4>
            
            <div style="margin-bottom: 8px;">
                <strong>Rating:</strong> {rating_display}
            </div>
            
            <div style="margin-bottom: 8px;">
                <strong>Price:</strong> {price_display}
            </div>
            
            <div style="margin-bottom: 8px;">
                <strong>Address:</strong><br>
                <span style="font-size: 12px; color: #666;">{address}</span>
            </div>
        """
        
        if phone:
            popup_html += f"""
            <div style="margin-bottom: 8px;">
                <strong>Phone:</strong> <a href="tel:{phone}">{phone}</a>
            </div>
            """
        
        if website:
            popup_html += f"""
            <div style="margin-bottom: 8px;">
                <strong>Website:</strong> <a href="{website}" target="_blank">Visit Website</a>
            </div>
            """
        
        # Add distance if available
        if venue.get('distance'):
            popup_html += f"""
            <div style="margin-bottom: 8px;">
                <strong>Distance:</strong> {venue['distance']:.1f} km
            </div>
            """
        
        popup_html += "</div>"
        
        return popup_html
    
    def _get_marker_color(self, rating: float) -> str:
        """Get marker color based on rating"""
        if rating is None:
            return 'gray'
        elif rating >= 4.5:
            return 'green'
        elif rating >= 4.0:
            return 'lightgreen'
        elif rating >= 3.5:
            return 'orange'
        elif rating >= 3.0:
            return 'red'
        else:
            return 'darkred'
    
    def show_interactive_map(self, recommendations: List[Dict], user_location = None):
        """Display interactive map in Streamlit"""
        try:
            if not recommendations:
                st.warning("No venues to display on map")
                return
            
            # Create map
            map_obj = self.create_recommendations_map(recommendations, user_location)
            
            if map_obj:
                st.subheader("🗺️ Venue Locations")
                
                # Show map legend
                self._show_map_legend()
                
                # Display map
                map_data = st_folium(
                    map_obj,
                    width=700,
                    height=500,
                    returned_objects=["last_object_clicked"]
                )
                
                # Handle map interactions
                if map_data['last_object_clicked']:
                    self._handle_map_click(map_data['last_object_clicked'], recommendations)
            
        except ImportError:
            st.error("Map functionality requires 'folium' and 'streamlit-folium' packages. Please install them.")
        except Exception as e:
            st.error(f"Error displaying map: {str(e)}")
    
    def _show_map_legend(self):
        """Show map legend"""
        with st.expander("Map Legend"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Marker Colors (by rating):**")
                st.write("🟢 Green: 4.5+ stars")
                st.write("🟡 Light Green: 4.0-4.4 stars")
                st.write("🟠 Orange: 3.5-3.9 stars")
            
            with col2:
                st.write("**Symbols:**")
                st.write("🔵 Blue User: Your location")
                st.write("⭐ Star: Venue location")
                st.write("🔴 Red: 3.0-3.4 stars")
                st.write("⚫ Dark Red: Below 3.0 stars")
    
    def _handle_map_click(self, clicked_data: Dict, recommendations: List[Dict]):
        """Handle map marker clicks"""
        try:
            if clicked_data and 'tooltip' in clicked_data:
                venue_name = clicked_data['tooltip']
                
                # Find the clicked venue
                clicked_venue = None
                for venue in recommendations:
                    if venue.get('name') == venue_name:
                        clicked_venue = venue
                        break
                
                if clicked_venue:
                    st.info(f"Selected: {venue_name}")
                    
                    # Show quick venue details
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        rating = clicked_venue.get('google_rating', clicked_venue.get('rating'))
                        if rating:
                            st.metric("Rating", f"{rating:.1f} ⭐")
                        
                        price_level = clicked_venue.get('price_level')
                        if price_level:
                            st.metric("Price", format_price_level(price_level))
                    
                    with col2:
                        if clicked_venue.get('phone'):
                            st.write(f"📞 {clicked_venue['phone']}")
                        
                        if clicked_venue.get('website'):
                            st.markdown(f"[🌐 Website]({clicked_venue['website']})")
                
        except Exception as e:
            print(f"Error handling map click: {str(e)}")
    
    def create_heatmap(self, venues: List[Dict], user_location = None) -> folium.Map:
        """Create a heatmap of venue density"""
        try:
            from folium.plugins import HeatMap
            
            # Determine map center
            user_coords = self._get_location_coordinates(user_location)
            if user_coords:
                center = user_coords
            else:
                center = self.default_location
            
            # Create map
            m = folium.Map(location=center, zoom_start=12)
            
            # Prepare heatmap data
            heat_data = []
            for venue in venues:
                if self._has_valid_location(venue):
                    location = venue['geometry']['location']
                    # Use rating as weight (higher rating = more heat)
                    weight = venue.get('google_rating', venue.get('rating', 3.0))
                    heat_data.append([location['lat'], location['lng'], weight])
            
            # Add heatmap layer
            if heat_data:
                HeatMap(heat_data, radius=15, blur=10, max_zoom=1).add_to(m)
            
            return m
            
        except ImportError:
            st.error("Heatmap requires folium plugins. Please install folium with all plugins.")
            return None
        except Exception as e:
            st.error(f"Error creating heatmap: {str(e)}")
            return None
    
    def show_venue_clusters(self, recommendations: List[Dict], user_location = None):
        """Show venues grouped by clusters"""
        try:
            from folium.plugins import MarkerCluster
            
            # Determine map center
            user_coords = self._get_location_coordinates(user_location)
            if user_coords:
                center = user_coords
            else:
                center = self.default_location
            
            # Create map
            m = folium.Map(location=center, zoom_start=12)
            
            # Create marker cluster
            marker_cluster = MarkerCluster().add_to(m)
            
            # Add user location
            if user_coords:
                folium.Marker(
                    user_coords,
                    popup="Your Location",
                    icon=folium.Icon(color='blue', icon='user', prefix='fa')
                ).add_to(m)
            
            # Add clustered venue markers
            for i, venue in enumerate(recommendations):
                if self._has_valid_location(venue):
                    location = venue['geometry']['location']
                    popup_content = self._create_popup_content(venue, i)
                    
                    folium.Marker(
                        [location['lat'], location['lng']],
                        popup=folium.Popup(popup_content, max_width=350),
                        tooltip=venue.get('name', f'Venue {i + 1}')
                    ).add_to(marker_cluster)
            
            # Display map
            st.subheader("🗺️ Clustered Venue View")
            st_folium(m, width=700, height=500)
            
        except ImportError:
            st.error("Clustering requires folium plugins.")
        except Exception as e:
            st.error(f"Error creating clustered map: {str(e)}")
