import json
import os
from typing import Dict, List, Optional
from datetime import datetime

class DataManager:
    def __init__(self, data_file: str = "data/user_profiles.json"):
        self.data_file = data_file
        self.ensure_data_file_exists()
    
    def ensure_data_file_exists(self):
        """Ensure the data file and directory exist"""
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
        if not os.path.exists(self.data_file):
            with open(self.data_file, 'w') as f:
                json.dump({}, f)
    
    def save_user_profile(self, user_id: str, profile_data: Dict) -> bool:
        """Save user profile data"""
        try:
            data = self.load_all_data()
            
            profile_data['last_updated'] = datetime.now().isoformat()
            data[user_id] = profile_data
            
            with open(self.data_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            return True
        except Exception as e:
            print(f"Error saving user profile: {str(e)}")
            return False
    
    def load_user_profile(self, user_id: str) -> Optional[Dict]:
        """Load user profile data"""
        try:
            data = self.load_all_data()
            return data.get(user_id)
        except Exception as e:
            print(f"Error loading user profile: {str(e)}")
            return None
    
    def load_all_data(self) -> Dict:
        """Load all data from the file"""
        try:
            with open(self.data_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading data: {str(e)}")
            return {}
    
    def update_user_preferences(self, user_id: str, preferences: Dict) -> bool:
        """Update specific user preferences"""
        try:
            profile = self.load_user_profile(user_id)
            if profile:
                profile['preferences'].update(preferences)
                return self.save_user_profile(user_id, profile)
            return False
        except Exception as e:
            print(f"Error updating preferences: {str(e)}")
            return False
    
    def add_user_feedback(self, user_id: str, venue_id: str, rating: int, feedback: str = "") -> bool:
        """Add user feedback for a venue"""
        try:
            profile = self.load_user_profile(user_id)
            if not profile:
                return False
            
            if 'feedback_history' not in profile:
                profile['feedback_history'] = []
            
            feedback_entry = {
                'venue_id': venue_id,
                'rating': rating,
                'feedback': feedback,
                'timestamp': datetime.now().isoformat()
            }
            
            profile['feedback_history'].append(feedback_entry)
            
            # Keep only last 100 feedback entries
            profile['feedback_history'] = profile['feedback_history'][-100:]
            
            return self.save_user_profile(user_id, profile)
        except Exception as e:
            print(f"Error adding feedback: {str(e)}")
            return False
    
    def get_user_feedback_history(self, user_id: str) -> List[Dict]:
        """Get user's feedback history"""
        try:
            profile = self.load_user_profile(user_id)
            if profile:
                return profile.get('feedback_history', [])
            return []
        except Exception as e:
            print(f"Error getting feedback history: {str(e)}")
            return []
    
    def update_taste_profile_id(self, user_id: str, taste_profile_id: str) -> bool:
        """Update user's Qloo taste profile ID"""
        try:
            profile = self.load_user_profile(user_id)
            if profile:
                profile['taste_profile_id'] = taste_profile_id
                return self.save_user_profile(user_id, profile)
            return False
        except Exception as e:
            print(f"Error updating taste profile ID: {str(e)}")
            return False
    
    def get_user_statistics(self, user_id: str) -> Dict:
        """Get user statistics"""
        try:
            profile = self.load_user_profile(user_id)
            if not profile:
                return {}
            
            feedback_history = profile.get('feedback_history', [])
            
            if not feedback_history:
                return {'total_ratings': 0}
            
            ratings = [f['rating'] for f in feedback_history]
            
            return {
                'total_ratings': len(ratings),
                'average_rating': sum(ratings) / len(ratings),
                'last_activity': max([f['timestamp'] for f in feedback_history]),
                'favorite_venues': self._get_favorite_venues(feedback_history)
            }
        except Exception as e:
            print(f"Error getting user statistics: {str(e)}")
            return {}
    
    def delete_user_profile(self, user_id: str) -> bool:
        """Delete a user profile completely"""
        try:
            data = self.load_all_data()
            
            if user_id in data:
                del data[user_id]
                
                with open(self.data_file, 'w') as f:
                    json.dump(data, f, indent=2)
                
                return True
            else:
                return False  # Profile doesn't exist
                
        except Exception as e:
            print(f"Error deleting user profile: {str(e)}")
            return False
    
    def get_all_user_profiles(self) -> Dict[str, Dict]:
        """Get all user profiles for selection/management"""
        try:
            return self.load_all_data()
        except Exception as e:
            print(f"Error getting all profiles: {str(e)}")
            return {}
    
    def _get_favorite_venues(self, feedback_history: List[Dict]) -> List[str]:
        """Get user's favorite venues (rated 4 or 5)"""
        favorites = []
        for feedback in feedback_history:
            if feedback['rating'] >= 4:
                favorites.append(feedback['venue_id'])
        
        # Return unique favorites
        return list(set(favorites))
