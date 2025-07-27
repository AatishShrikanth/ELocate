"""
Qloo-Demo Mapper Service
Maps Qloo API insights to demo venue data for enhanced recommendations
"""

from typing import List, Dict, Optional
import random

class QlooDemoMapper:
    """Maps Qloo entity insights to demo venues"""
    
    def __init__(self):
        # Category mapping from Qloo entities to venue types
        self.category_mapping = {
            'restaurant': ['restaurant', 'meal_takeaway', 'food'],
            'bar': ['bar', 'night_club', 'liquor_store'],
            'coffee': ['cafe', 'coffee_shop'],
            'museum': ['museum', 'art_gallery'],
            'entertainment': ['movie_theater', 'bowling_alley', 'amusement_park', 'night_club'],
            'art': ['art_gallery', 'museum'],
            'shopping': ['shopping_mall', 'store'],
            'park': ['park', 'zoo']
        }
    
    def enhance_venues_with_qloo_insights(self, 
                                        demo_venues: List[Dict], 
                                        qloo_insights: Dict[str, List[Dict]]) -> List[Dict]:
        """Enhance demo venues with Qloo popularity and category insights"""
        
        enhanced_venues = []
        
        for venue in demo_venues:
            enhanced_venue = venue.copy()
            
            # Find matching Qloo insights for this venue
            qloo_match = self._find_qloo_match(venue, qloo_insights)
            
            if qloo_match:
                # Apply Qloo insights
                enhanced_venue = self._apply_qloo_insights(enhanced_venue, qloo_match)
                enhanced_venue['qloo_enhanced'] = True
                enhanced_venue['qloo_category'] = qloo_match.get('matched_category')
            else:
                # No Qloo match, use base scoring
                enhanced_venue['qloo_enhanced'] = False
                enhanced_venue['qloo_category'] = 'unknown'
            
            enhanced_venues.append(enhanced_venue)
        
        return enhanced_venues
    
    def _find_qloo_match(self, venue: Dict, qloo_insights: Dict[str, List[Dict]]) -> Optional[Dict]:
        """Find the best Qloo entity match for a venue"""
        
        venue_types = venue.get('types', [])
        
        # Try to match venue types to Qloo categories
        for qloo_category, entities in qloo_insights.items():
            mapped_types = self.category_mapping.get(qloo_category, [])
            
            # Check if venue types match this Qloo category
            if any(vtype in mapped_types for vtype in venue_types):
                # Find the best entity from this category
                if entities:
                    # Sort by popularity and take the top one
                    best_entity = max(entities, key=lambda x: x.get('popularity', 0))
                    return {
                        'entity': best_entity,
                        'matched_category': qloo_category,
                        'match_confidence': self._calculate_match_confidence(venue_types, mapped_types)
                    }
        
        return None
    
    def _calculate_match_confidence(self, venue_types: List[str], mapped_types: List[str]) -> float:
        """Calculate confidence score for venue-category matching"""
        if not venue_types or not mapped_types:
            return 0.0
        
        matches = sum(1 for vtype in venue_types if vtype in mapped_types)
        return matches / len(venue_types)
    
    def _apply_qloo_insights(self, venue: Dict, qloo_match: Dict) -> Dict:
        """Apply Qloo insights to enhance venue recommendation score"""
        
        entity = qloo_match['entity']
        match_confidence = qloo_match['match_confidence']
        
        # Get Qloo popularity score (0-1 range)
        qloo_popularity = entity.get('popularity', 0.5)
        
        # Get venue's base score
        base_score = venue.get('recommendation_score', venue.get('rating', 3.0))
        
        # Calculate Qloo enhancement
        qloo_boost = qloo_popularity * match_confidence * 0.5  # Max 0.5 point boost
        
        # Apply enhancement
        enhanced_score = base_score + qloo_boost
        
        # Add Qloo metadata
        venue['recommendation_score'] = enhanced_score
        venue['qloo_popularity'] = qloo_popularity
        venue['qloo_entity_id'] = entity.get('entity_id')
        venue['qloo_entity_name'] = entity.get('name')
        venue['match_confidence'] = match_confidence
        
        # Add Qloo properties if available
        properties = entity.get('properties', {})
        if properties:
            venue['qloo_description'] = properties.get('description', '')
            venue['qloo_style'] = properties.get('presentation_style', '')
        
        return venue
    
    def create_qloo_enhanced_recommendations(self, 
                                           demo_venues: List[Dict],
                                           qloo_insights: Dict[str, List[Dict]],
                                           user_preferences: Dict,
                                           filters: Dict = None) -> List[Dict]:
        """Create final recommendations enhanced with Qloo insights"""
        
        # Enhance venues with Qloo insights
        enhanced_venues = self.enhance_venues_with_qloo_insights(demo_venues, qloo_insights)
        
        # Apply additional personalization based on Qloo categories
        personalized_venues = self._apply_qloo_personalization(enhanced_venues, user_preferences)
        
        # Sort by enhanced recommendation score
        personalized_venues.sort(key=lambda x: x.get('recommendation_score', 0), reverse=True)
        
        return personalized_venues
    
    def _apply_qloo_personalization(self, venues: List[Dict], user_preferences: Dict) -> List[Dict]:
        """Apply additional personalization based on Qloo category matching"""
        
        user_interests = user_preferences.get('interests', [])
        
        # Interest to Qloo category mapping
        interest_category_map = {
            'Fine Dining': 'restaurant',
            'Casual Dining': 'restaurant',
            'Bars & Nightlife': 'bar', 
            'Coffee Shops': 'coffee',
            'Museums': 'museum',
            'Art Galleries': 'art',
            'Entertainment': 'entertainment',
            'Shopping': 'shopping',
            'Outdoor Activities': 'park'
        }
        
        for venue in venues:
            qloo_category = venue.get('qloo_category', '')
            
            # Boost score if venue's Qloo category matches user interests
            for interest in user_interests:
                if interest_category_map.get(interest) == qloo_category:
                    current_score = venue.get('recommendation_score', 0)
                    venue['recommendation_score'] = current_score + 0.3  # Interest match boost
                    venue['interest_match'] = True
                    break
            else:
                venue['interest_match'] = False
        
        return venues
    
    def get_qloo_insights_summary(self, qloo_insights: Dict[str, List[Dict]]) -> Dict:
        """Generate summary of Qloo insights for debugging"""
        
        summary = {
            'total_categories': len(qloo_insights),
            'total_entities': sum(len(entities) for entities in qloo_insights.values()),
            'categories': {}
        }
        
        for category, entities in qloo_insights.items():
            if entities:
                avg_popularity = sum(e.get('popularity', 0) for e in entities) / len(entities)
                top_entity = max(entities, key=lambda x: x.get('popularity', 0))
                
                summary['categories'][category] = {
                    'entity_count': len(entities),
                    'avg_popularity': avg_popularity,
                    'top_entity': {
                        'name': top_entity.get('name'),
                        'popularity': top_entity.get('popularity'),
                        'entity_id': top_entity.get('entity_id')
                    }
                }
        
        return summary
