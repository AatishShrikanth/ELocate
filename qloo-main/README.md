# 🎯 Entertainment Recommender

A Streamlit-based web application that provides personalized entertainment recommendations using Qloo's Taste AI™ engine, with weather awareness, budget filtering, interactive mapping, and an **AI-powered assistant**.

## ✨ Features

### 🎯 Personalized Recommendations
- **Taste Profile Creation**: Build personalized profiles using Qloo's AI engine
- **Learning System**: Improves recommendations based on user feedback
- **Multi-source Data**: Combines Qloo recommendations with Google Places data

### 🤖 AI Assistant (NEW!)
- **Claude Haiku Integration**: Powered by AWS Bedrock's Claude Haiku model
- **Context-Aware Chat**: Understands your current recommendations and preferences
- **Real-time Help**: Ask questions about venues, filters, and recommendations
- **Quick Actions**: One-click explanations and suggestions
- **Scrollable Interface**: Full chat history with intuitive UI

### 🌤️ Smart Filtering
- **Weather Awareness**: Indoor/outdoor suggestions based on current weather
- **Budget Filtering**: Filter venues by price range ($, $$, $$$, $$$$)
- **Time-based Recommendations**: Different suggestions for day/evening/weekend
- **Distance Control**: Adjustable search radius

### 🗺️ Interactive Interface
- **Map Visualization**: Interactive maps with venue markers
- **Multiple Views**: List and map display modes
- **Real-time Feedback**: Swipe-like rating interface
- **Clustering**: Grouped venue display for better navigation

### 📊 Analytics
- **Taste Analytics**: Track your rating patterns and preferences
- **Progress Tracking**: See how your taste profile evolves
- **Favorite Venues**: Keep track of highly-rated places

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- API keys for Qloo, Google Places, and OpenWeatherMap
- **AWS Account with Bedrock access** (for AI assistant)

### Installation

1. **Clone or download the project**
   ```bash
   cd qloo-main
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up API keys**
   - The `.env` file contains your existing API keys
   - **NEW**: Add AWS credentials for the AI assistant

4. **Configure AWS Bedrock (for AI Assistant)**
   ```bash
   python setup_aws.py
   ```
   Or manually add to `.env`:
   ```
   AWS_ACCESS_KEY_ID=your_access_key
   AWS_SECRET_ACCESS_KEY=your_secret_key
   AWS_DEFAULT_REGION=us-east-1
   ```

5. **Run the application**
   ```bash
   streamlit run app.py
   ```

6. **Open your browser**
   - Navigate to `http://localhost:8501`
   - Start creating your taste profile!

## 🎮 How to Use

### 1. Create Your Profile
- Enter your basic information (name, age, interests)
- List places you've enjoyed in the past
- Specify dietary preferences and restrictions
- The app will create a personalized taste profile using Qloo's AI

### 2. Set Your Location
- Use the default San Francisco location, or
- Enter custom coordinates in the sidebar
- Location is used for nearby venue discovery

### 3. Get Recommendations
- Navigate to the "Recommendations" page
- Adjust filters (budget, category, distance, etc.)
- Enable weather-aware recommendations
- Click "Get Recommendations" to see personalized suggestions

### 4. Use the AI Assistant (NEW!)
- **Right Panel**: AI assistant appears on the recommendations page
- **Quick Actions**: Click buttons for instant help
  - "💡 Explain my recommendations"
  - "🎯 Improve my results"
  - "📍 Tell me about top venue"
  - "🔄 Suggest new filters"
- **Chat Interface**: Type questions naturally
  - "Why was this restaurant recommended?"
  - "How can I find cheaper options?"
  - "What makes this venue special?"
- **Context Awareness**: AI knows your current recommendations and preferences

### 5. Explore Venues
- **List View**: Compact table format for quick browsing
- **Map View**: Interactive map with venue markers

### 6. Rate and Learn
- Rate venues using the 1-5 star system
- Your ratings improve future recommendations
- Check analytics to see your taste evolution

## 🏗️ Architecture

### Frontend
- **Streamlit**: Web application framework
- **Folium**: Interactive mapping
- **Plotly**: Analytics visualizations

### Backend Services
- **Qloo Service**: Taste AI™ integration
- **Google Places**: Venue data enrichment
- **OpenWeatherMap**: Weather-aware recommendations
- **AWS Bedrock**: AI assistant powered by Claude Haiku

### Data Storage
- **Local JSON**: User profiles and preferences
- **Session State**: Temporary data and UI state

## 📁 Project Structure

```
entertainment-recommender/
├── app.py                 # Main Streamlit application
├── .env                   # API keys (including AWS)
├── requirements.txt       # Python dependencies
├── setup_aws.py          # AWS configuration helper
├── config/
│   └── settings.py       # Configuration management
├── services/
│   ├── qloo_service.py   # Qloo API integration
│   ├── weather_service.py # Weather API integration
│   ├── places_service.py # Google Places integration
│   └── bedrock_service.py # NEW: AWS Bedrock AI service
├── utils/
│   ├── data_manager.py   # User data persistence
│   └── helpers.py        # Utility functions
├── components/
│   ├── user_profile.py   # Profile management UI
│   ├── recommendations.py # Recommendation engine UI
│   ├── ai_assistant.py   # NEW: AI chat interface
│   └── map_view.py       # Map visualization
└── data/
    └── user_profiles.json # User data storage
```

## 🔧 Configuration

### API Keys
The following APIs are integrated:
- **Qloo API**: Taste AI™ recommendations
- **Google Places API**: Venue details and photos
- **OpenWeatherMap API**: Weather data for smart filtering
- **AWS Bedrock**: Claude Haiku AI assistant

### AWS Bedrock Setup
1. **Enable Bedrock Access**: In your AWS console, request access to Claude models
2. **Create IAM User**: With `bedrock:InvokeModel` permissions
3. **Configure Credentials**: Use `setup_aws.py` or manually edit `.env`
4. **Test Connection**: The setup script will verify your configuration

### Settings
Key settings can be modified in `config/settings.py`:
- Search radius (default: 5km)
- Maximum recommendations (default: 20)
- Weather thresholds for indoor/outdoor suggestions
- Budget price level mappings
- AI assistant model and parameters

## 🎨 Features in Detail

### AI Assistant Deep Dive
- **Model**: Claude Haiku via AWS Bedrock for fast, cost-effective responses
- **Context Integration**: Automatically includes current recommendations and user preferences
- **Quick Actions**: Pre-built prompts for common questions
- **Chat History**: Maintains conversation context with scrollable interface
- **Error Handling**: Graceful fallbacks for API issues
- **Security**: Uses AWS IAM for secure API access

### Taste Profile Creation
- Uses Qloo's entity analysis to understand preferences
- Learns from past venue experiences
- Incorporates dietary restrictions and lifestyle preferences

### Weather-Aware Recommendations
- Fetches real-time weather data
- Suggests indoor venues during bad weather
- Considers temperature, precipitation, and wind conditions

### Smart Filtering System
- **Budget**: Filter by price level with visual indicators
- **Category**: Restaurant, bars, entertainment, culture, etc.
- **Distance**: Adjustable search radius
- **Rating**: Minimum rating threshold
- **Time**: Context-aware suggestions (morning, evening, weekend)

### Interactive Map Features
- Color-coded markers based on venue ratings
- Detailed popups with venue information
- Clustering for dense areas
- Heatmap view for venue density analysis

### Analytics Dashboard
- Rating distribution charts
- Taste evolution over time
- Favorite venues tracking
- Personal statistics and insights

## 🔍 Troubleshooting

### Common Issues

1. **API Key Errors**
   - Check that all API keys are correctly set in `.env`
   - Verify API quotas and billing status

2. **AI Assistant Not Working**
   - Run `python setup_aws.py` to configure AWS credentials
   - Ensure you have Bedrock access enabled in AWS console
   - Check that Claude Haiku model is available in your region
   - Verify IAM permissions for `bedrock:InvokeModel`

3. **No Recommendations**
   - Ensure location is set correctly
   - Try adjusting filters (budget, distance, rating)
   - Check internet connection for API calls

4. **Map Not Loading**
   - Install folium and streamlit-folium: `pip install folium streamlit-folium`
   - Check browser JavaScript is enabled

5. **Profile Creation Issues**
   - Ensure the `data/` directory exists and is writable
   - Check that user_profiles.json is accessible

### AWS Bedrock Troubleshooting
- **Access Denied**: Request model access in AWS Bedrock console
- **Region Issues**: Ensure Claude Haiku is available in your region
- **Rate Limits**: Claude Haiku has generous limits, but check usage
- **Billing**: Verify AWS account has billing enabled

### Performance Tips
- Limit recommendation requests to avoid API rate limits
- Use caching for repeated venue lookups
- Consider reducing search radius for faster results
- AI assistant responses are typically fast (< 2 seconds)

## 🚀 Advanced Usage

### AI Assistant Tips
- **Be Specific**: Ask detailed questions about venues or preferences
- **Use Context**: The AI knows your current recommendations
- **Quick Actions**: Use buttons for common queries
- **Follow-up**: Ask follow-up questions for deeper insights

### Custom Location Input
- Enter precise coordinates for any location worldwide
- Useful for travel planning and exploring new cities

### Bulk Rating
- Use the list view for quick rating of multiple venues
- Ratings immediately update your taste profile

### Export Data
- User profiles are stored in JSON format
- Easy to backup or transfer between instances

## 🔮 Future Enhancements

Potential improvements for the application:
- **AI Assistant Enhancements**:
  - Voice input/output
  - Image recognition for venue photos
  - Multi-language support
  - Integration with calendar for event planning
- **Social Features**: Share recommendations with friends
- **Advanced AI**: GPT-4 or Claude Opus for more sophisticated responses
- **Mobile App**: Native iOS/Android versions
- **Reservation Integration**: Direct booking capabilities

## 📞 Support

For issues or questions:
1. Check the troubleshooting section above
2. Verify API key configuration (including AWS)
3. Ensure all dependencies are installed correctly
4. Run `python setup_aws.py` for AI assistant issues

## 🎉 Getting Started Tips

1. **Start Simple**: Create a basic profile and get your first recommendations
2. **Try the AI**: Ask the assistant to explain your recommendations
3. **Rate Actively**: The more you rate, the better your recommendations become
4. **Explore Filters**: Try different combinations to discover new types of venues
5. **Use Weather Awareness**: Great for planning activities based on conditions
6. **Chat with AI**: Ask questions like "Why this venue?" or "Find me cheaper options"
7. **Check Analytics**: Monitor how your taste profile evolves over time

## 🆕 What's New in This Version

### AI Assistant Integration
- **Real-time Chat**: Instant responses to your questions
- **Context Awareness**: Understands your current recommendations
- **Quick Actions**: One-click help for common queries
- **AWS Bedrock**: Enterprise-grade AI infrastructure
- **Claude Haiku**: Fast, accurate, and cost-effective AI model

### Enhanced User Experience
- **Split Layout**: Recommendations on left, AI assistant on right
- **Improved Error Handling**: Better feedback for API issues
- **Setup Automation**: Easy AWS configuration with `setup_aws.py`
- **Performance Optimizations**: Faster loading and response times
