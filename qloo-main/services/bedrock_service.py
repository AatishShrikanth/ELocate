import boto3
import json
import logging
import os
from typing import List, Dict, Optional
from botocore.exceptions import ClientError, BotoCoreError
from config.settings import Config

logger = logging.getLogger(__name__)

class BedrockService:
    def __init__(self, region_name: str = None):
        """Initialize Bedrock service with Claude Haiku model."""
        try:
            # Use region from config or parameter
            region = region_name or Config.AWS_DEFAULT_REGION
            
            # Set AWS credentials if provided in config
            if Config.AWS_ACCESS_KEY_ID and Config.AWS_SECRET_ACCESS_KEY:
                os.environ['AWS_ACCESS_KEY_ID'] = Config.AWS_ACCESS_KEY_ID
                os.environ['AWS_SECRET_ACCESS_KEY'] = Config.AWS_SECRET_ACCESS_KEY
                os.environ['AWS_DEFAULT_REGION'] = region
            
            self.client = boto3.client('bedrock-runtime', region_name=region)
            self.model_id = Config.BEDROCK_MODEL_ID
            self.max_tokens = Config.AI_MAX_TOKENS
            self.temperature = Config.AI_TEMPERATURE
            
            logger.info(f"Bedrock service initialized with model: {self.model_id}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Bedrock client: {e}")
            raise
    
    def get_response(self, messages: List[Dict], context: Optional[str] = None) -> str:
        """
        Get response from Claude Haiku model.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            context: Optional context about current recommendations
            
        Returns:
            Assistant response as string
        """
        try:
            # Prepare system message with context
            system_message = self._build_system_message(context)
            
            # Format messages for Claude
            formatted_messages = self._format_messages(messages)
            
            # Prepare request body
            request_body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": self.max_tokens,
                "temperature": self.temperature,
                "system": system_message,
                "messages": formatted_messages
            }
            
            logger.debug(f"Sending request to Bedrock: {json.dumps(request_body, indent=2)}")
            
            # Make API call
            response = self.client.invoke_model(
                modelId=self.model_id,
                body=json.dumps(request_body),
                contentType='application/json'
            )
            
            # Parse response
            response_body = json.loads(response['body'].read())
            logger.debug(f"Bedrock response: {json.dumps(response_body, indent=2)}")
            
            if 'content' in response_body and len(response_body['content']) > 0:
                return response_body['content'][0]['text']
            else:
                return "I apologize, but I couldn't generate a response. Please try again."
                
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            error_message = e.response.get('Error', {}).get('Message', str(e))
            logger.error(f"AWS Bedrock API error [{error_code}]: {error_message}")
            
            if error_code == 'AccessDeniedException':
                return "I don't have access to the AI service. Please check your AWS credentials and permissions."
            elif error_code == 'ThrottlingException':
                return "The AI service is currently busy. Please try again in a moment."
            else:
                return "I'm having trouble connecting to the AI service. Please try again later."
                
        except BotoCoreError as e:
            logger.error(f"AWS SDK error: {e}")
            return "There was a connection issue. Please check your AWS configuration."
        except Exception as e:
            logger.error(f"Unexpected error in Bedrock service: {e}")
            return "An unexpected error occurred. Please try again."
    
    def _build_system_message(self, context: Optional[str] = None) -> str:
        """Build system message with context about the entertainment recommender."""
        base_system = """You are an AI assistant integrated into an Entertainment Recommender application. 
        You help users discover and explore entertainment venues based on their personalized taste profiles.
        
        Your role is to:
        - Help users understand their recommendations
        - Answer questions about specific venues
        - Provide insights about their taste preferences
        - Suggest ways to refine their search filters
        - Explain why certain venues were recommended
        - Be enthusiastic about entertainment discovery
        
        Guidelines:
        - Be conversational, helpful, and enthusiastic
        - Keep responses concise but informative (2-3 sentences typically)
        - If asked about venues not in the current recommendations, politely redirect to available options
        - Use emojis sparingly but appropriately
        - Focus on actionable advice and insights
        - If no recommendations are available, encourage the user to get recommendations first"""
        
        if context:
            return f"{base_system}\n\nCurrent context:\n{context}"
        
        return base_system
    
    def _format_messages(self, messages: List[Dict]) -> List[Dict]:
        """Format messages for Claude API format."""
        formatted = []
        for msg in messages:
            if msg['role'] in ['user', 'assistant']:
                formatted.append({
                    'role': msg['role'],
                    'content': msg['content']
                })
        return formatted
    
    def get_venue_explanation(self, venue_name: str, user_preferences: Dict) -> str:
        """Get explanation for why a specific venue was recommended."""
        context = f"User preferences: {json.dumps(user_preferences, indent=2)}"
        
        messages = [{
            'role': 'user',
            'content': f"Why was {venue_name} recommended for me based on my preferences?"
        }]
        
        return self.get_response(messages, context)
    
    def get_filter_suggestions(self, current_filters: Dict, recommendations_count: int) -> str:
        """Suggest filter adjustments based on current results."""
        context = f"Current filters: {json.dumps(current_filters, indent=2)}\nRecommendations found: {recommendations_count}"
        
        messages = [{
            'role': 'user',
            'content': "Can you suggest how I might adjust my filters to get better recommendations?"
        }]
        
        return self.get_response(messages, context)
    
    def test_connection(self) -> bool:
        """Test if the Bedrock service is properly configured and accessible."""
        try:
            test_messages = [{
                'role': 'user',
                'content': 'Hello, can you respond with just "OK"?'
            }]
            
            response = self.get_response(test_messages)
            return "error" not in response.lower() and len(response) > 0
            
        except Exception as e:
            logger.error(f"Bedrock connection test failed: {e}")
            return False
