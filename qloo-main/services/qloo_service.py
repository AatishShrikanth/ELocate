import requests
import json
import logging
from typing import List, Dict, Optional
from config.settings import Config

# Set up debug logging for Qloo API
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class QlooService:
    def __init__(self):
        self.api_key = Config.QLOO_API_KEY
        self.base_url = "https://hackathon.api.qloo.com"  # Hackathon endpoint
        self.headers = {
            'X-API-Key': self.api_key,  # Use X-API-Key instead of Bearer
            'Content-Type': 'application/json'
        }
        
        # Log initialization (without API key)
        logger.info("🎯 QlooService initialized")
        logger.info(f"📡 Base URL: {self.base_url}")
        logger.info(f"🔑 Authentication: X-API-Key (key length: {len(self.api_key)} chars)")
        
        # Test authentication immediately
        self.test_authentication()
    
    def test_authentication(self):
        """Test Qloo API authentication and log results"""
        logger.info("🔐 TESTING QLOO API AUTHENTICATION")
        logger.info("=" * 60)
        
        try:
            # Test with a simple search to verify authentication
            test_endpoint = "/search"
            test_params = {'query': 'test', 'limit': 1}
            
            logger.debug(f"🧪 Testing authentication with endpoint: {self.base_url}{test_endpoint}")
            logger.debug(f"🧪 Test parameters: {test_params}")
            
            response = requests.get(
                f"{self.base_url}{test_endpoint}",
                headers=self.headers,
                params=test_params,
                timeout=10
            )
            
            logger.info(f"🔐 Authentication Test Response: {response.status_code}")
            
            if response.status_code == 200:
                logger.info("✅ QLOO API AUTHENTICATION SUCCESSFUL")
                data = response.json()
                results = data.get('results', [])
                logger.info(f"✅ Test search returned {len(results)} results")
                
                # Log rate limit info
                if 'X-RateLimit-Remaining-Month' in response.headers:
                    remaining = response.headers['X-RateLimit-Remaining-Month']
                    limit = response.headers.get('X-RateLimit-Limit-Month', 'Unknown')
                    logger.info(f"📊 Rate Limit: {remaining}/{limit} requests remaining this month")
                
            elif response.status_code == 401:
                logger.error("❌ QLOO API AUTHENTICATION FAILED - UNAUTHORIZED")
                logger.error("🔑 Check API key configuration")
                
            elif response.status_code == 403:
                logger.error("❌ QLOO API AUTHENTICATION FAILED - FORBIDDEN")
                logger.error("🔑 API key valid but insufficient permissions")
                
            else:
                logger.error(f"❌ QLOO API AUTHENTICATION FAILED - HTTP {response.status_code}")
                logger.error(f"📦 Response: {response.text}")
                
        except Exception as e:
            logger.error(f"❌ QLOO API AUTHENTICATION TEST FAILED: {str(e)}")
        
        logger.info("=" * 60)
    
    def _log_api_request(self, method: str, endpoint: str, params: Dict = None, json_data: Dict = None):
        """Log API request details without sensitive information"""
        logger.info("=" * 60)
        logger.info("🚀 QLOO API REQUEST")
        logger.info("=" * 60)
        logger.info(f"📍 Method: {method}")
        logger.info(f"🌐 Endpoint: {self.base_url}{endpoint}")
        logger.info(f"📋 Headers: {{'X-API-Key': '[HIDDEN]', 'Content-Type': 'application/json'}}")
        
        if params:
            logger.info(f"🔍 Query Parameters:")
            for key, value in params.items():
                logger.info(f"   {key}: {value}")
        
        if json_data:
            logger.info(f"📦 JSON Body:")
            logger.info(f"   {json.dumps(json_data, indent=2)}")
        
        logger.info("-" * 60)
    
    def _log_api_response(self, response, endpoint: str):
        """Log API response details"""
        logger.info("📥 QLOO API RESPONSE")
        logger.info("=" * 60)
        logger.info(f"📍 Endpoint: {endpoint}")
        logger.info(f"📊 Status Code: {response.status_code}")
        logger.info(f"⏱️ Response Time: {response.elapsed.total_seconds():.3f}s")
        
        # Log response headers (without sensitive info)
        logger.info("📋 Response Headers:")
        for key, value in response.headers.items():
            if key.lower() not in ['authorization', 'x-api-key']:
                logger.info(f"   {key}: {value}")
        
        # Log response body
        try:
            if response.status_code == 200:
                data = response.json()
                logger.info("✅ Response Status: SUCCESS")
                logger.info(f"📦 Response Body Structure:")
                
                if isinstance(data, dict):
                    for key, value in data.items():
                        if key == 'results' and isinstance(value, list):
                            logger.info(f"   {key}: Array[{len(value)}] - {len(value)} entities")
                            
                            # Log first result as example
                            if value:
                                first_result = value[0]
                                logger.info(f"   📋 Sample Entity:")
                                logger.info(f"      name: {first_result.get('name', 'N/A')}")
                                logger.info(f"      entity_id: {first_result.get('entity_id', 'N/A')}")
                                logger.info(f"      popularity: {first_result.get('popularity', 'N/A')}")
                                logger.info(f"      types: {first_result.get('types', [])}")
                                
                                properties = first_result.get('properties', {})
                                if properties:
                                    logger.info(f"      properties: {len(properties)} items")
                                    for prop_key in list(properties.keys())[:3]:  # Show first 3 properties
                                        prop_value = properties[prop_key]
                                        if isinstance(prop_value, str) and len(prop_value) > 100:
                                            logger.info(f"         {prop_key}: {prop_value[:100]}...")
                                        else:
                                            logger.info(f"         {prop_key}: {prop_value}")
                        else:
                            logger.info(f"   {key}: {type(value).__name__} = {value}")
                else:
                    logger.info(f"   Response: {type(data).__name__}")
                    logger.info(f"   Content: {str(data)[:500]}...")
                    
            else:
                logger.error(f"❌ Response Status: ERROR ({response.status_code})")
                logger.error(f"📦 Error Response:")
                try:
                    error_data = response.json()
                    logger.error(f"   {json.dumps(error_data, indent=2)}")
                except:
                    logger.error(f"   {response.text}")
                    
        except Exception as e:
            logger.error(f"❌ Error parsing response: {str(e)}")
            logger.error(f"📦 Raw Response: {response.text[:500]}...")
        
        logger.info("=" * 60)
    
    def create_taste_profile(self, user_preferences: Dict) -> Optional[Dict]:
        """Create a taste profile based on user preferences"""
        try:
            # Extract entities from user preferences
            entities = []
            
            # Add liked venues as entities
            if 'liked_venues' in user_preferences:
                for venue in user_preferences['liked_venues']:
                    entities.append({
                        'name': venue,
                        'type': 'venue'
                    })
            
            # Add interests as entities
            if 'interests' in user_preferences:
                for interest in user_preferences['interests']:
                    entities.append({
                        'name': interest,
                        'type': 'category'
                    })
            
            payload = {
                'entities': entities,
                'user_id': user_preferences.get('user_id', 'anonymous')
            }
            
            response = requests.post(
                f"{self.base_url}/taste/profile",
                headers=self.headers,
                json=payload
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error creating taste profile: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"Error in create_taste_profile: {str(e)}")
            return None
    
    def get_recommendations(self, 
                          taste_profile_id: str, 
                          location: Dict[str, float],
                          filters: Dict = None) -> List[Dict]:
        """Get personalized venue recommendations"""
        try:
            payload = {
                'taste_profile_id': taste_profile_id,
                'location': {
                    'latitude': location['lat'],
                    'longitude': location['lng']
                },
                'radius': Config.DEFAULT_RADIUS,
                'limit': Config.MAX_RECOMMENDATIONS
            }
            
            # Add filters if provided
            if filters:
                if 'budget' in filters:
                    payload['price_level'] = Config.BUDGET_MAPPING.get(filters['budget'])
                if 'category' in filters:
                    payload['category'] = filters['category']
                if 'time_of_day' in filters:
                    payload['time_context'] = filters['time_of_day']
            
            response = requests.post(
                f"{self.base_url}/recommendations/venues",
                headers=self.headers,
                json=payload
            )
            
            if response.status_code == 200:
                return response.json().get('recommendations', [])
            else:
                print(f"Error getting recommendations: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"Error in get_recommendations: {str(e)}")
            return []
    
    def update_taste_profile(self, 
                           taste_profile_id: str, 
                           feedback: Dict) -> bool:
        """Update taste profile based on user feedback"""
        try:
            payload = {
                'taste_profile_id': taste_profile_id,
                'feedback': feedback
            }
            
            response = requests.put(
                f"{self.base_url}/taste/profile/update",
                headers=self.headers,
                json=payload
            )
            
            return response.status_code == 200
            
        except Exception as e:
            print(f"Error updating taste profile: {str(e)}")
            return False
    
    def search_entities_by_category(self, category: str, limit: int = 20) -> List[Dict]:
        """Search Qloo entities by category - WORKING ENDPOINT with detailed logging"""
        endpoint = "/search"
        params = {
            'query': category.lower(),
            'limit': limit
        }
        
        # Log request
        self._log_api_request("GET", endpoint, params=params)
        
        try:
            response = requests.get(
                f"{self.base_url}{endpoint}",
                headers=self.headers,
                params=params,
                timeout=10
            )
            
            # Log response
            self._log_api_response(response, endpoint)
            
            if response.status_code == 200:
                data = response.json()
                results = data.get('results', [])
                
                logger.info(f"✅ Qloo Search SUCCESS: Found {len(results)} entities for '{category}'")
                
                # Log summary statistics
                if results:
                    popularities = [r.get('popularity', 0) for r in results if r.get('popularity')]
                    if popularities:
                        avg_popularity = sum(popularities) / len(popularities)
                        max_popularity = max(popularities)
                        min_popularity = min(popularities)
                        
                        logger.info(f"📊 Popularity Statistics:")
                        logger.info(f"   Average: {avg_popularity:.6f}")
                        logger.info(f"   Maximum: {max_popularity:.6f}")
                        logger.info(f"   Minimum: {min_popularity:.6f}")
                
                return results
            else:
                logger.error(f"❌ Qloo Search FAILED: HTTP {response.status_code}")
                return []
                
        except requests.exceptions.Timeout:
            logger.error("❌ Qloo API Timeout: Request took longer than 10 seconds")
            return []
        except requests.exceptions.ConnectionError:
            logger.error("❌ Qloo API Connection Error: Unable to connect to server")
            return []
        except Exception as e:
            logger.error(f"❌ Qloo API Exception: {str(e)}")
            return []
    
    def get_category_insights(self, categories: List[str]) -> Dict[str, List[Dict]]:
        """Get Qloo insights for multiple categories with detailed logging"""
        logger.info("🎯 QLOO CATEGORY INSIGHTS REQUEST")
        logger.info("=" * 60)
        logger.info(f"📋 Requested Categories: {categories}")
        logger.info(f"📊 Total Categories: {len(categories)}")
        
        insights = {}
        
        for i, category in enumerate(categories, 1):
            logger.info(f"🔍 Processing Category {i}/{len(categories)}: {category}")
            
            entities = self.search_entities_by_category(category)
            if entities:
                insights[category] = entities
                logger.info(f"✅ Category '{category}': {len(entities)} entities retrieved")
            else:
                logger.warning(f"⚠️ Category '{category}': No entities found")
        
        # Log final summary
        logger.info("📊 CATEGORY INSIGHTS SUMMARY")
        logger.info("=" * 60)
        total_entities = sum(len(entities) for entities in insights.values())
        logger.info(f"✅ Successfully processed: {len(insights)}/{len(categories)} categories")
        logger.info(f"📊 Total entities retrieved: {total_entities}")
        
        for category, entities in insights.items():
            if entities:
                top_entity = max(entities, key=lambda x: x.get('popularity', 0))
                logger.info(f"   {category}: {len(entities)} entities (top: {top_entity.get('name')} - {top_entity.get('popularity', 0):.6f})")
        
        logger.info("=" * 60)
        
        return insights
    
    def get_enhanced_recommendations_by_category(self, user_preferences: Dict, filters: Dict = None) -> Dict[str, List[Dict]]:
        """Get Qloo-enhanced recommendations by category with detailed logging"""
        logger.info("🎯 QLOO ENHANCED RECOMMENDATIONS REQUEST")
        logger.info("=" * 60)
        
        try:
            # Map user interests to Qloo search categories
            interest_to_category = {
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
            
            user_interests = user_preferences.get('interests', [])
            logger.info(f"👤 User Interests: {user_interests}")
            
            categories_to_search = []
            
            # Get categories based on user interests
            for interest in user_interests:
                if interest in interest_to_category:
                    category = interest_to_category[interest]
                    if category not in categories_to_search:
                        categories_to_search.append(category)
            
            # If no specific interests, search popular categories
            if not categories_to_search:
                categories_to_search = ['restaurant', 'bar', 'entertainment', 'museum']
                logger.info("ℹ️ No user interests found, using default categories")
            
            # Also add category from filters
            if filters and filters.get('category') != 'All':
                filter_category = filters['category'].lower()
                if filter_category not in categories_to_search:
                    categories_to_search.append(filter_category)
                    logger.info(f"➕ Added filter category: {filter_category}")
            
            logger.info(f"🎯 Final categories to search: {categories_to_search}")
            
            # Get Qloo insights for each category
            insights = self.get_category_insights(categories_to_search)
            
            logger.info("✅ QLOO ENHANCED RECOMMENDATIONS COMPLETE")
            logger.info("=" * 60)
            
            return insights
            
        except Exception as e:
            logger.error(f"❌ Error getting Qloo enhanced recommendations: {str(e)}")
            logger.error("=" * 60)
            return {}
    
    def get_venue_recommendations(self, location_name: str, filters: Dict = None, limit: int = 20) -> List[Dict]:
        """Get venue recommendations directly from Qloo API using v2/insights endpoint - EXACT WORKING CODE"""
        logger.info("🎯 GETTING VENUE RECOMMENDATIONS FROM QLOO V2/INSIGHTS API")
        logger.info("=" * 60)
        logger.info(f"📍 Location: {location_name}")
        
        # Use EXACT working URL structure from your Python code
        url = f"https://hackathon.api.qloo.com/v2/insights/?filter.type=urn:entity:place&filter.location.query={location_name.replace(' ', '')}"
        
        # Use EXACT headers from your working Python code
        headers = {
            "accept": "application/json",
            "X-Api-Key": self.api_key
        }
        
        logger.info(f"🔍 Using EXACT working URL: {url}")
        logger.info(f"🔑 Using EXACT working headers: {headers}")
        
        try:
            # Log request
            logger.info("🚀 QLOO API REQUEST (EXACT WORKING CODE)")
            logger.info("=" * 60)
            logger.info(f"📍 Method: GET")
            logger.info(f"🌐 URL: {url}")
            logger.info(f"📋 Headers: {headers}")
            logger.info("-" * 60)
            
            # Use requests.get exactly like your working code
            response = requests.get(url, headers=headers)
            
            # Log response
            logger.info("📥 QLOO API RESPONSE")
            logger.info("=" * 60)
            logger.info(f"📊 Status Code: {response.status_code}")
            logger.info(f"⏱️ Response Time: {response.elapsed.total_seconds():.3f}s")
            
            if response.status_code == 200:
                # Parse response exactly like your working code
                response_text = response.text
                logger.info(f"✅ SUCCESS! Raw response length: {len(response_text)} characters")
                
                try:
                    data = response.json()
                    # The correct structure is data['results']['entities'], not data['results']
                    results = data.get('results', {})
                    entities = results.get('entities', [])
                    logger.info(f"✅ Parsed JSON: Found {len(entities)} entities")
                    
                    if entities:
                        formatted_venues = self._format_qloo_venues(entities)
                        logger.info(f"✅ Formatted {len(formatted_venues)} venues")
                        return formatted_venues
                    else:
                        logger.warning("⚠️ No entities in response")
                        logger.info(f"📦 Full response: {response_text[:1000]}...")
                        return []
                        
                except json.JSONDecodeError as e:
                    logger.error(f"❌ JSON parsing error: {str(e)}")
                    logger.error(f"📦 Raw response: {response_text[:1000]}...")
                    return []
            else:
                logger.error(f"❌ v2/insights failed: HTTP {response.status_code}")
                logger.error(f"📦 Error response: {response.text}")
                return []
                
        except Exception as e:
            logger.error(f"❌ Error with v2/insights endpoint: {str(e)}")
            return []
    
    def _format_qloo_venues(self, qloo_entities: List[Dict]) -> List[Dict]:
        """Format Qloo API entities into venue format"""
        logger.info(f"🔄 Formatting {len(qloo_entities)} Qloo entities into venue format")
        
        formatted_venues = []
        
        for i, entity in enumerate(qloo_entities):
            try:
                # Extract venue information from Qloo entity
                venue = {
                    'id': entity.get('entity_id', f'qloo_{i}'),
                    'name': entity.get('name', 'Unknown Venue'),
                    'qloo_entity_id': entity.get('entity_id'),
                    'qloo_type': entity.get('type'),
                    'qloo_subtype': entity.get('subtype'),
                    'source': 'qloo_api',
                    'data_source': 'Qloo API v2/insights',
                }
                
                # Extract properties if available
                properties = entity.get('properties', {})
                if properties:
                    venue.update({
                        'address': properties.get('address', ''),
                        'phone': properties.get('phone', ''),
                        'website': properties.get('website', ''),
                        'description': properties.get('description', ''),
                        'rating': properties.get('business_rating'),
                        'google_rating': properties.get('business_rating'),  # Use business_rating as google_rating
                        'is_closed': properties.get('is_closed', False),
                    })
                    
                    # Set recommendation score based on business rating
                    if properties.get('business_rating'):
                        venue['recommendation_score'] = properties['business_rating']
                    else:
                        venue['recommendation_score'] = 3.0  # Default score
                
                # Extract keywords as categories
                keywords = properties.get('keywords', [])
                if keywords:
                    venue['categories'] = [kw.get('name', '') for kw in keywords[:5]]  # Top 5 keywords
                    venue['tags'] = keywords
                
                # Try to extract location from address (basic parsing)
                address = properties.get('address', '')
                if address:
                    venue['vicinity'] = address
                    # Try to extract city/state from address
                    if 'San Francisco' in address:
                        venue['city'] = 'San Francisco'
                    elif 'CA' in address:
                        venue['state'] = 'CA'
                
                # Set default geometry structure for compatibility
                venue['geometry'] = {
                    'location': {
                        'lat': 37.7749,  # Default SF coordinates
                        'lng': -122.4194
                    }
                }
                
                formatted_venues.append(venue)
                logger.debug(f"✅ Formatted venue {i+1}: {venue['name']} (Rating: {venue.get('rating', 'N/A')})")
                
            except Exception as e:
                logger.error(f"❌ Error formatting entity {i}: {str(e)}")
                logger.error(f"📦 Entity data: {entity}")
                continue
        
        logger.info(f"✅ Successfully formatted {len(formatted_venues)} venues")
        return formatted_venues
