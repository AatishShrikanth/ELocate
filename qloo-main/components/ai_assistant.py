import streamlit as st
import json
from datetime import datetime
from typing import Dict, List, Optional
from services.bedrock_service import BedrockService

def initialize_chat_state():
    """Initialize chat-related session state variables with better error handling."""
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    if 'bedrock_service' not in st.session_state:
        try:
            st.session_state.bedrock_service = BedrockService()
        except Exception as e:
            st.error(f"Failed to initialize AI service: {str(e)}")
            st.session_state.bedrock_service = None
    
    if 'chat_context' not in st.session_state:
        st.session_state.chat_context = {}
    
    # Add chat session ID to track restarts
    if 'chat_session_id' not in st.session_state:
        st.session_state.chat_session_id = datetime.now().strftime("%Y%m%d_%H%M%S")

def render_ai_assistant(recommendations_data: Optional[Dict] = None, user_preferences: Optional[Dict] = None):
    """
    Render the AI assistant chat interface.
    
    Args:
        recommendations_data: Current recommendations and filters
        user_preferences: User's taste profile and preferences
    """
    initialize_chat_state()
    
    # Update context with current recommendations
    if recommendations_data:
        st.session_state.chat_context = {
            'recommendations': recommendations_data.get('venues', []),
            'filters': recommendations_data.get('filters', {}),
            'user_preferences': user_preferences or {},
            'timestamp': datetime.now().isoformat()
        }
    
    # Chat container with custom styling
    st.markdown("""
    <style>
    .chat-container {
        height: 400px;
        overflow-y: auto;
        padding: 10px;
        border: 1px solid #ddd;
        border-radius: 10px;
        background-color: #f9f9f9;
        margin-bottom: 10px;
    }
    .user-message {
        background-color: #007bff;
        color: white;
        padding: 8px 12px;
        border-radius: 15px;
        margin: 5px 0;
        margin-left: 20%;
        text-align: right;
    }
    .assistant-message {
        background-color: #e9ecef;
        color: #333;
        padding: 8px 12px;
        border-radius: 15px;
        margin: 5px 0;
        margin-right: 20%;
    }
    .message-time {
        font-size: 0.8em;
        color: #666;
        margin-top: 5px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Chat header
    st.markdown("### 🤖 AI Assistant")
    st.markdown("*Ask me about your recommendations, venues, or how to improve your results!*")
    
    # Quick action buttons
    render_quick_actions()
    
    # Chat messages container
    chat_container = st.container()
    
    with chat_container:
        # Display chat history with proper HTML escaping
        if st.session_state.chat_history:
            messages_html = ""
            for message in st.session_state.chat_history:
                message_class = "user-message" if message['role'] == 'user' else "assistant-message"
                timestamp = message.get('timestamp', '')
                
                # Properly escape HTML in message content to prevent HTML injection
                import html
                escaped_content = html.escape(message['content'])
                
                messages_html += f"""
                <div class="{message_class}">
                    {escaped_content}
                    <div class="message-time">{timestamp}</div>
                </div>
                """
            
            st.markdown(f'<div class="chat-container">{messages_html}</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="chat-container"><p style="text-align: center; color: #666; margin-top: 50px;">Ask me anything about your recommendations!</p></div>', unsafe_allow_html=True)
    
    # Chat input
    render_chat_input()

def render_quick_actions():
    """Render quick action buttons for common queries."""
    st.markdown("**Quick Actions:**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("💡 Explain my recommendations", key="explain_recs"):
            handle_quick_action("explain_recommendations")
        
        if st.button("🎯 Improve my results", key="improve_results"):
            handle_quick_action("improve_results")
    
    with col2:
        if st.button("📍 Tell me about top venue", key="top_venue"):
            handle_quick_action("top_venue")
        
        if st.button("🔄 Suggest new filters", key="new_filters"):
            handle_quick_action("suggest_filters")

def render_chat_input():
    """Render chat input area with service validation."""
    # Check if Bedrock service is available
    if not st.session_state.bedrock_service:
        st.error("AI service is not available. Please check your AWS configuration.")
        if st.button("🔄 Retry AI Service", key="retry_service"):
            try:
                st.session_state.bedrock_service = BedrockService()
                st.success("AI service reconnected!")
                st.rerun()
            except Exception as e:
                st.error(f"Failed to reconnect: {str(e)}")
        return
    
    # Create input form
    with st.form(key="chat_form", clear_on_submit=True):
        col1, col2 = st.columns([4, 1])
        
        with col1:
            user_input = st.text_input(
                "Ask me anything...",
                placeholder="e.g., Why was this restaurant recommended?",
                label_visibility="collapsed",
                max_chars=500  # Limit input length
            )
        
        with col2:
            send_button = st.form_submit_button("Send", use_container_width=True)
        
        if send_button and user_input.strip():
            # Validate input
            if len(user_input.strip()) < 3:
                st.warning("Please enter a longer message.")
                return
            
            handle_user_message(user_input.strip())

def handle_user_message(message: str):
    """Handle user message and get AI response - single conversation approach."""
    # Add user message (this clears previous history)
    add_message_to_history("user", message)
    
    # Show typing indicator
    with st.spinner("AI is thinking..."):
        try:
            # Prepare context for AI
            context = build_context_string()
            
            # Create a single message for the AI (no conversation history)
            current_messages = [{"role": "user", "content": message}]
            
            # Get AI response
            response = st.session_state.bedrock_service.get_response(
                messages=current_messages,
                context=context
            )
            
            # Check if response indicates an error
            if "I'm having trouble" in response or "error" in response.lower():
                # Try a simpler request without context
                simple_messages = [{"role": "user", "content": message}]
                response = st.session_state.bedrock_service.get_response(
                    messages=simple_messages,
                    context="You are a helpful AI assistant for an entertainment recommendation app."
                )
            
            # Add AI response (this keeps only user message + AI response)
            add_message_to_history("assistant", response)
            
        except Exception as e:
            error_message = f"I apologize, but I encountered an issue. Please try asking your question differently."
            add_message_to_history("assistant", error_message)
            st.error(f"Chat Error: {str(e)}")
    
    # Rerun to update the chat display
    st.rerun()

def handle_quick_action(action_type: str):
    """Handle quick action button clicks."""
    action_messages = {
        "explain_recommendations": "Can you explain why these venues were recommended for me?",
        "improve_results": "How can I improve my recommendation results?",
        "top_venue": "Tell me more about the top recommended venue.",
        "suggest_filters": "Can you suggest better filter settings for me?"
    }
    
    if action_type in action_messages:
        handle_user_message(action_messages[action_type])

def add_message_to_history(role: str, content: str):
    """Add a message to the chat history - keep only current conversation pair."""
    timestamp = datetime.now().strftime("%H:%M")
    
    message = {
        'role': role,
        'content': content,
        'timestamp': timestamp
    }
    
    # If this is a user message, clear everything and start fresh
    if role == 'user':
        st.session_state.chat_history = [message]
    else:
        # If this is an assistant message, keep only the last user message and this response
        if st.session_state.chat_history:
            st.session_state.chat_history = [st.session_state.chat_history[-1], message]
        else:
            st.session_state.chat_history = [message]

def build_context_string() -> str:
    """Build context string from current recommendations and user data."""
    context_parts = []
    
    if 'chat_context' in st.session_state:
        ctx = st.session_state.chat_context
        
        # Add recommendations info
        if 'recommendations' in ctx and ctx['recommendations']:
            venues = ctx['recommendations'][:3]  # Only top 3 venues to keep context manageable
            venue_info = []
            for venue in venues:
                venue_info.append(f"- {venue.get('name', 'Unknown')}: {venue.get('rating', 'N/A')} stars, {venue.get('price_level', 'N/A')} price level")
            
            context_parts.append(f"Current top recommendations:\n" + "\n".join(venue_info))
        
        # Add filter info
        if 'filters' in ctx and ctx['filters']:
            filters = ctx['filters']
            filter_info = []
            for key, value in filters.items():
                if value and key in ['budget', 'category', 'distance', 'weather_aware']:  # Only key filters
                    filter_info.append(f"- {key}: {value}")
            
            if filter_info:
                context_parts.append(f"Current filters:\n" + "\n".join(filter_info))
        
        # Add basic user preferences (simplified)
        if 'user_preferences' in ctx and ctx['user_preferences']:
            prefs = ctx['user_preferences']
            if prefs.get('interests'):
                context_parts.append(f"User interests: {', '.join(prefs['interests'][:3])}")  # Only first 3 interests
    
    return "\n\n".join(context_parts) if context_parts else "No current context available."
