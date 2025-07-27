import streamlit as st
from typing import Dict, List
from utils.data_manager import DataManager
from utils.helpers import generate_user_id
from services.qloo_service import QlooService

class UserProfileManager:
    def __init__(self):
        self.data_manager = DataManager()
        self.qloo_service = QlooService()
    
    def show_onboarding_form(self) -> Dict:
        """Display user onboarding form"""
        st.header("🎯 Create Your Taste Profile")
        st.write("Help us understand your preferences to provide personalized recommendations!")
        
        with st.form("user_onboarding"):
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input("Name *", placeholder="Enter your name")
                age = st.selectbox("Age Range", 
                                 ["18-25", "26-35", "36-45", "46-55", "56-65", "65+"])
                location_pref = st.selectbox("Location Preference",
                                           ["Current Location", "Custom Location"])
            
            with col2:
                email = st.text_input("Email (Optional)", placeholder="your@email.com")
                budget_pref = st.selectbox("Typical Budget",
                                         ["$", "$$", "$$$", "$$$$", "Varies"])
                dining_style = st.selectbox("Dining Style",
                                          ["Casual", "Fine Dining", "Fast Food", "Mixed"])
            
            st.subheader("Your Interests")
            interests = st.multiselect(
                "Select your interests (choose multiple):",
                ["Fine Dining", "Casual Dining", "Bars & Nightlife", "Coffee Shops",
                 "Museums", "Art Galleries", "Live Music", "Theater", "Movies",
                 "Shopping", "Outdoor Activities", "Sports", "Fitness", "Spa & Wellness",
                 "Cultural Events", "Food Trucks", "Craft Beer", "Wine Tasting",
                 "Dancing", "Comedy Shows", "Festivals", "Markets"]
            )
            
            st.subheader("Places You've Enjoyed")
            liked_venues = st.text_area(
                "Tell us about some places you've enjoyed (one per line):",
                placeholder="e.g.\nStarbucks\nThe Metropolitan Museum\nCentral Park\nJoe's Pizza"
            )
            
            st.subheader("Dietary Preferences & Restrictions")
            dietary_prefs = st.multiselect(
                "Select any that apply:",
                ["Vegetarian", "Vegan", "Gluten-Free", "Halal", "Kosher", 
                 "Dairy-Free", "Nut-Free", "Low-Carb", "Keto", "None"]
            )
            
            submitted = st.form_submit_button("Create My Profile", type="primary")
            
            if submitted:
                if not name:
                    st.error("Please enter your name to continue.")
                    return None
                
                # Process liked venues
                venue_list = [venue.strip() for venue in liked_venues.split('\n') if venue.strip()]
                
                # Create user profile
                user_id = generate_user_id(name, email)
                
                profile_data = {
                    'user_id': user_id,
                    'name': name,
                    'email': email,
                    'age_range': age,
                    'location_preference': location_pref,
                    'budget_preference': budget_pref,
                    'dining_style': dining_style,
                    'interests': interests,
                    'liked_venues': venue_list,
                    'dietary_preferences': dietary_prefs,
                    'preferences': {
                        'budget': budget_pref,
                        'interests': interests,
                        'liked_venues': venue_list
                    }
                }
                
                # Save profile
                if self.data_manager.save_user_profile(user_id, profile_data):
                    st.success("Profile created successfully!")
                    
                    # Create Qloo taste profile
                    with st.spinner("Creating your personalized taste profile..."):
                        taste_profile = self.qloo_service.create_taste_profile(profile_data['preferences'])
                        
                        if taste_profile:
                            taste_profile_id = taste_profile.get('profile_id', user_id)
                            self.data_manager.update_taste_profile_id(user_id, taste_profile_id)
                            st.success("Taste profile created! Ready for personalized recommendations.")
                        else:
                            st.warning("Profile saved, but taste profile creation failed. You'll still get recommendations!")
                    
                    return profile_data
                else:
                    st.error("Failed to save profile. Please try again.")
                    return None
        
        return None
    
    def show_profile_selector(self) -> str:
        """Show existing profile selector"""
        all_profiles = self.data_manager.load_all_data()
        
        if not all_profiles:
            return None
        
        st.subheader("Select Your Profile")
        
        profile_options = {}
        for user_id, profile in all_profiles.items():
            display_name = f"{profile.get('name', 'Unknown')} ({profile.get('email', 'No email')})"
            profile_options[display_name] = user_id
        
        selected_profile = st.selectbox(
            "Choose an existing profile:",
            ["Create New Profile"] + list(profile_options.keys())
        )
        
        if selected_profile != "Create New Profile":
            return profile_options[selected_profile]
        
        return None
    
    def show_profile_summary(self, user_id: str):
        """Display profile summary"""
        profile = self.data_manager.load_user_profile(user_id)
        if not profile:
            return
        
        st.subheader(f"Welcome back, {profile.get('name', 'User')}! 👋")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Age Range", profile.get('age_range', 'Not specified'))
        
        with col2:
            st.metric("Budget Preference", profile.get('budget_preference', 'Not specified'))
        
        with col3:
            stats = self.data_manager.get_user_statistics(user_id)
            st.metric("Total Ratings", stats.get('total_ratings', 0))
        
        # Show interests
        interests = profile.get('interests', [])
        if interests:
            st.write("**Your Interests:**")
            st.write(", ".join(interests))
        
        # Show recent activity
        if stats.get('last_activity'):
            st.write(f"**Last Activity:** {stats['last_activity'][:10]}")
    
    def show_profile_editor(self, user_id: str):
        """Show profile editing interface"""
        profile = self.data_manager.load_user_profile(user_id)
        if not profile:
            st.error("Profile not found")
            return
        
        st.subheader("Edit Your Profile")
        
        with st.form("edit_profile"):
            # Basic info
            name = st.text_input("Name", value=profile.get('name', ''))
            email = st.text_input("Email", value=profile.get('email', ''))
            budget_pref = st.selectbox("Budget Preference",
                                     ["$", "$$", "$$$", "$$$$", "Varies"],
                                     index=["$", "$$", "$$$", "$$$$", "Varies"].index(
                                         profile.get('budget_preference', 'Varies')))
            
            # Interests
            current_interests = profile.get('interests', [])
            all_interests = ["Fine Dining", "Casual Dining", "Bars & Nightlife", "Coffee Shops",
                           "Museums", "Art Galleries", "Live Music", "Theater", "Movies",
                           "Shopping", "Outdoor Activities", "Sports", "Fitness", "Spa & Wellness",
                           "Cultural Events", "Craft Beer", "Wine Tasting",
                           "Dancing", "Comedy Shows", "Festivals", "Markets"]
            
            interests = st.multiselect("Interests", all_interests, default=current_interests)
            
            # Dietary preferences
            current_dietary = profile.get('dietary_preferences', [])
            dietary_options = ["Vegetarian", "Vegan", "Gluten-Free", "Halal", "Kosher", 
                             "Dairy-Free", "Nut-Free", "Low-Carb", "Keto", "None"]
            dietary_prefs = st.multiselect("Dietary Preferences", dietary_options, default=current_dietary)
            
            if st.form_submit_button("Update Profile"):
                # Update profile
                profile.update({
                    'name': name,
                    'email': email,
                    'budget_preference': budget_pref,
                    'interests': interests,
                    'dietary_preferences': dietary_prefs
                })
                
                # Update preferences for recommendations
                profile['preferences'].update({
                    'budget': budget_pref,
                    'interests': interests
                })
                
                if self.data_manager.save_user_profile(user_id, profile):
                    st.success("Profile updated successfully!")
                    st.rerun()
                else:
                    st.error("Failed to update profile")
    
    def show_profile_management(self):
        """Show profile management interface with delete option"""
        st.subheader("🗂️ Profile Management")
        
        all_profiles = self.data_manager.get_all_user_profiles()
        
        if not all_profiles:
            st.info("No profiles found.")
            return
        
        # Show existing profiles
        st.write("**Existing Profiles:**")
        
        for user_id, profile in all_profiles.items():
            with st.container():
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    name = profile.get('name', 'Unknown User')
                    email = profile.get('email', 'No email')
                    created = profile.get('last_updated', 'Unknown')[:10] if profile.get('last_updated') else 'Unknown'
                    
                    st.write(f"**{name}**")
                    st.caption(f"Email: {email} | Last updated: {created}")
                
                with col2:
                    if st.button("Select", key=f"select_{user_id}"):
                        st.session_state.user_id = user_id
                        st.success(f"Selected profile: {name}")
                        st.rerun()
                
                with col3:
                    if st.button("🗑️ Delete", key=f"delete_{user_id}", type="secondary"):
                        # Show confirmation
                        st.session_state[f'confirm_delete_{user_id}'] = True
                
                # Show delete confirmation if requested
                if st.session_state.get(f'confirm_delete_{user_id}', False):
                    st.warning(f"⚠️ Are you sure you want to delete the profile for **{name}**?")
                    st.write("This action cannot be undone. All ratings and preferences will be lost.")
                    
                    col_yes, col_no = st.columns(2)
                    
                    with col_yes:
                        if st.button("Yes, Delete", key=f"confirm_yes_{user_id}", type="primary"):
                            if self.data_manager.delete_user_profile(user_id):
                                st.success(f"Profile for {name} has been deleted.")
                                
                                # Clear session state if this was the active user
                                if st.session_state.get('user_id') == user_id:
                                    del st.session_state.user_id
                                
                                # Clear confirmation state
                                del st.session_state[f'confirm_delete_{user_id}']
                                st.rerun()
                            else:
                                st.error("Failed to delete profile.")
                    
                    with col_no:
                        if st.button("Cancel", key=f"confirm_no_{user_id}"):
                            del st.session_state[f'confirm_delete_{user_id}']
                            st.rerun()
                
                st.divider()
        
        # Add new profile option
        st.subheader("➕ Create New Profile")
        if st.button("Create New Profile", type="primary"):
            # Clear current user session to force new profile creation
            if 'user_id' in st.session_state:
                del st.session_state.user_id
            st.info("Click 'Home' to create a new profile.")
    
    def show_profile_selector_with_management(self) -> str:
        """Enhanced profile selector with management options"""
        all_profiles = self.data_manager.load_all_data()
        
        if not all_profiles:
            return None
        
        st.subheader("👤 Select Your Profile")
        
        # Profile selection
        profile_options = {}
        for user_id, profile in all_profiles.items():
            display_name = f"{profile.get('name', 'Unknown')} ({profile.get('email', 'No email')})"
            profile_options[display_name] = user_id
        
        selected_profile = st.selectbox(
            "Choose an existing profile:",
            ["Create New Profile"] + list(profile_options.keys())
        )
        
        if selected_profile != "Create New Profile":
            selected_user_id = profile_options[selected_profile]
            
            # Show profile actions
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("✅ Use This Profile", type="primary"):
                    return selected_user_id
            
            with col2:
                if st.button("🗑️ Delete This Profile", type="secondary"):
                    st.session_state[f'confirm_delete_{selected_user_id}'] = True
            
            # Handle delete confirmation
            if st.session_state.get(f'confirm_delete_{selected_user_id}', False):
                profile_name = all_profiles[selected_user_id].get('name', 'Unknown')
                
                st.warning(f"⚠️ Delete profile for **{profile_name}**?")
                st.write("This will permanently remove all data including ratings and preferences.")
                
                col_yes, col_no = st.columns(2)
                
                with col_yes:
                    if st.button("Yes, Delete", key=f"final_delete_{selected_user_id}"):
                        if self.data_manager.delete_user_profile(selected_user_id):
                            st.success(f"Profile for {profile_name} deleted successfully.")
                            del st.session_state[f'confirm_delete_{selected_user_id}']
                            st.rerun()
                        else:
                            st.error("Failed to delete profile.")
                
                with col_no:
                    if st.button("Cancel", key=f"cancel_delete_{selected_user_id}"):
                        del st.session_state[f'confirm_delete_{selected_user_id}']
                        st.rerun()
        
        return None
    
    def get_or_create_profile(self) -> str:
        """Get existing profile or create new one"""
        # Check if user_id is already in session state
        if 'user_id' in st.session_state:
            return st.session_state.user_id
        
        # Show enhanced profile selector with management options
        existing_user_id = self.show_profile_selector_with_management()
        
        if existing_user_id:
            st.session_state.user_id = existing_user_id
            return existing_user_id
        else:
            # Show onboarding form
            new_profile = self.show_onboarding_form()
            if new_profile:
                st.session_state.user_id = new_profile['user_id']
                return new_profile['user_id']
        
        return None
