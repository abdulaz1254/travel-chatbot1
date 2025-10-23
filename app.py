from flask import Flask, request, jsonify, render_template
from models.gemini_client import GeminiTravelAssistant
from models.data_processor import TravelDataProcessor
from config import Config
import json
import os
import sys

# Add current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

try:
    from flask import Flask, request, jsonify, render_template
    from config import Config
    from models.gemini_client import GeminiTravelAssistant
    from models.data_processor import TravelDataProcessor
    import json
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure all required packages are installed and virtual environment is activated")
    sys.exit(1)

# Validate configuration
config_errors = Config.validate_config()
if config_errors:
    print("Configuration errors found:")
    for error in config_errors:
        print(f"  - {error}")
    print("\nPlease fix these issues before running the application.")
    sys.exit(1)

app = Flask(__name__)
app.config.from_object(Config)

# Initialize components
gemini_assistant = GeminiTravelAssistant()
data_processor = TravelDataProcessor()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    """Enhanced chat endpoint with human-like responses"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        user_message = data.get('message', '').strip()
        user_country = data.get('user_country', 'US')
        
        if not user_message:
            return jsonify({
                'response': 'I\'d love to help you plan your trip! What are you curious about? 😊',
                'error': 'Please ask me something!'
            }), 400
        
        print(f"🗨️  User ({user_country}): {user_message}")
        
        # Get relevant data from datasets
        relevant_data = data_processor.get_relevant_data(user_message)
        
        # Add user context
        if relevant_data:
            relevant_data['user_country'] = user_country
        
        # Get human-like response
        response = gemini_assistant.get_response(user_message, relevant_data)
        
        print(f"🤖 Emma: {response[:100]}...")
        
        return jsonify({
            'response': response,
            'data_used': list(relevant_data.keys()) if relevant_data else [],
            'user_country': user_country,
            'assistant_name': 'Emma'
        })
    
    except Exception as e:
        print(f"❌ Error in chat: {e}")
        return jsonify({
            'response': 'I\'m having a tiny technical moment, but I\'m still here to help! Could you ask your question again? I\'m excited to help you plan something amazing! ✈️😊'
        }), 200

@app.route('/search_packages', methods=['POST'])
def search_packages():
    try:
        query_params = request.json
        packages = data_processor.search_packages(query_params)
        return jsonify({'packages': packages})
    
    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

@app.route('/weather/<destination>')
def get_weather(destination):
    try:
        season = request.args.get('season')
        weather_info = data_processor.get_weather_info(destination, season)
        
        if weather_info:
            return jsonify({'weather': weather_info})
        else:
            return jsonify({'error': 'Weather information not found'}), 404
    
    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

@app.route('/visa_info')
def get_visa_info():
    try:
        destination = request.args.get('destination')
        user_country = request.args.get('user_country', 'US')
        visa_type = request.args.get('visa_type', 'tourist_visa')
        
        visa_info = data_processor.get_visa_info(destination, user_country, visa_type)
        
        if visa_info:
            return jsonify({'visa_info': visa_info})
        else:
            return jsonify({'error': 'Visa information not found'}), 404
    
    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

@app.route('/reset_chat', methods=['POST'])
def reset_chat():
    try:
        gemini_assistant.reset_chat()
        return jsonify({'message': 'Chat reset successfully'})
    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True)
