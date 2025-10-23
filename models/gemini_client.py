import google.generativeai as genai
import os
import sys
import json

# Add parent directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

try:
    import google.generativeai as genai
except ImportError as e:
    print(f"❌ Error importing google.generativeai: {e}")
    raise

try:
    from config import Config
except ImportError as e:
    print(f"❌ Error importing Config: {e}")
    class Config:
        GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', 'your-gemini-api-key-here')
        SECRET_KEY = 'temp-key'
        DEBUG = True

class GeminiTravelAssistant:
    def __init__(self):
        if not Config.GEMINI_API_KEY or Config.GEMINI_API_KEY == 'your-gemini-api-key-here':
            raise ValueError("Please set your GEMINI_API_KEY in the .env file")
        
        try:
            genai.configure(api_key=Config.GEMINI_API_KEY)
            self.model = genai.GenerativeModel('gemini-2.0-flash')
            self.chat_session = None
            self.initialize_chat()
            print("✅ Gemini model initialized successfully")
        except Exception as e:
            print(f"❌ Error initializing Gemini: {e}")
            # We'll use fallback responses if Gemini fails
            self.model = None
            self.chat_session = None
    
    def initialize_chat(self):
        """Initialize chat with human-like travel expert persona"""
        if not self.model:
            return
            
        system_prompt = """
        You are Emma, a friendly and experienced human travel consultant who has been helping people plan amazing trips for over 10 years. 

        Your personality:
        - Warm, enthusiastic, and genuinely excited about travel
        - Speak naturally like a human friend giving advice
        - Use casual, conversational language 
        - Share personal insights as if you've been to these places
        - Always reference specific data when available (prices, weather, etc.)
        - Ask follow-up questions to understand their needs better
        - Use emojis naturally in conversation
        - Make recommendations based on their budget and preferences

        Always respond as if you're chatting with a friend who's asking for travel advice. Use the provided travel data to give specific, accurate information while maintaining a natural, conversational tone.
        """
        
        try:
            self.chat_session = self.model.start_chat(history=[])
            self.chat_session.send_message(system_prompt)
            print("✅ Chat session initialized")
        except Exception as e:
            print(f"❌ Error initializing chat: {e}")
            self.chat_session = None
    
    def get_response(self, user_message, travel_data=None):
        """Get human-like response using Gemini or fallback to dataset-based responses"""
        
        # If Gemini is available, use it
        if self.model and self.chat_session:
            try:
                return self.get_gemini_response(user_message, travel_data)
            except Exception as e:
                print(f"Gemini failed, using fallback: {e}")
                return self.get_dataset_response(user_message, travel_data)
        
        # Use dataset-based responses
        return self.get_dataset_response(user_message, travel_data)
    
    def get_gemini_response(self, user_message, travel_data):
        """Get response from Gemini with dataset context"""
        context = f"""
        User's question: {user_message}
        
        Available travel data: {json.dumps(travel_data, indent=2) if travel_data else "No specific data available"}
        
        Respond as Emma, a friendly human travel consultant. Use the travel data to give specific recommendations with exact prices and details. Be conversational and natural, like talking to a friend.
        """
        
        response = self.chat_session.send_message(context)
        return response.text
    
    def get_dataset_response(self, user_message, travel_data):
        """Generate human-like responses using dataset"""
        user_msg = user_message.lower()
        
        # Weather queries
        if any(word in user_msg for word in ['weather', 'climate', 'temperature']):
            return self.handle_weather_query(user_msg, travel_data)
        
        # Package/trip queries
        elif any(word in user_msg for word in ['package', 'trip', 'vacation', 'travel', 'show me']):
            return self.handle_package_query(user_msg, travel_data)
        
        # Visa queries
        elif any(word in user_msg for word in ['visa', 'passport', 'entry', 'document']):
            return self.handle_visa_query(user_msg, travel_data)
        
        # Destination-specific queries
        elif any(dest in user_msg for dest in ['paris', 'tokyo', 'bali', 'dubai', 'santorini']):
            return self.handle_destination_query(user_msg, travel_data)
        
        # General greeting/help
        else:
            return self.get_greeting_response()
    
    def handle_weather_query(self, user_msg, travel_data):
        """Handle weather-related queries"""
        if 'bali' in user_msg and 'summer' in user_msg:
            if travel_data and 'weather' in travel_data:
                weather_data = travel_data['weather'].get('Bali', {})
                dry_season = weather_data.get('dry_season', {})
                
                return f"""🌴 Oh, you're asking about Bali in summer! You're going to love it - summer is actually part of Bali's dry season, which is absolutely perfect for a tropical getaway!

Here's what you can expect:
🌡️ **Temperature**: Around {dry_season.get('avg_temp', '27°C')} - just perfect for beach days!
☀️ **Weather**: {dry_season.get('conditions', 'Sunny and dry')} - you'll have gorgeous sunny days
🌧️ **Rainfall**: {dry_season.get('rainfall', 'Very low')} - barely any rain to worry about

**What to pack**: {dry_season.get('clothing', 'Light summer clothes and swimwear')} - think shorts, sundresses, and don't forget your sunscreen!

The dry season runs from {', '.join(dry_season.get('months', [])[:3])} through {', '.join(dry_season.get('months', [])[-3:])}, so you're picking the ideal time to visit! 

Are you thinking more beach relaxation or exploring the cultural sites? I can suggest some amazing packages that would be perfect for summer! ✈️"""

            return """🌴 Bali in summer is absolutely magical! You've picked the perfect time - it's during the dry season, so you'll have beautiful sunny days with temperatures around 27°C and very little rain. 

Perfect beach weather! You'll want to pack light summer clothes, swimwear, and lots of sunscreen. The warm tropical breeze and crystal-clear skies make it ideal for both beach lounging and exploring those famous rice terraces!

Are you planning more of a relaxing beach vacation or an adventure-packed trip? I'd love to help you find the perfect package! 🏖️✈️"""
        
        return "I'd love to help you with weather information! Could you let me know which destination you're interested in and what time of year you're thinking of traveling? That way I can give you the most accurate forecast and packing suggestions! 🌤️"
    
    def handle_package_query(self, user_msg, travel_data):
        """Handle travel package queries"""
        if travel_data and 'packages' in travel_data:
            packages = travel_data['packages']
            
            # Filter based on user preferences
            if 'romantic' in user_msg or 'paris' in user_msg:
                romantic_packages = [pkg for pkg in packages if pkg.get('category') == 'romantic']
                if romantic_packages:
                    return self.format_package_response(romantic_packages, "romantic getaway")
            
            elif 'adventure' in user_msg or 'asia' in user_msg:
                adventure_packages = [pkg for pkg in packages if pkg.get('category') in ['adventure', 'cultural']]
                if adventure_packages:
                    return self.format_package_response(adventure_packages, "adventure")
            
            elif 'luxury' in user_msg:
                luxury_packages = [pkg for pkg in packages if pkg.get('category') == 'luxury']
                if luxury_packages:
                    return self.format_package_response(luxury_packages, "luxury experience")
            
            # Show top packages
            top_packages = sorted(packages, key=lambda x: x.get('rating', 0), reverse=True)[:3]
            return self.format_package_response(top_packages, "amazing trip")
        
        return """✈️ I'd love to help you find the perfect travel package! I have some incredible deals on romantic getaways, adventure trips, and luxury vacations. 

What kind of experience are you looking for? Are you thinking:
🏖️ Beach relaxation?
🏔️ Adventure and culture?
💕 Romantic escape?
🌟 Luxury experience?

Let me know your preferences and budget, and I'll find you some amazing options! 🌍"""
    
    def format_package_response(self, packages, trip_type):
        """Format package information in a human-like way"""
        response = f"✨ I found some incredible packages for your {trip_type}! Let me share my top recommendations:\n\n"
        
        for i, pkg in enumerate(packages[:3], 1):
            response += f"**{i}. {pkg.get('package_name', 'Amazing Trip')}** 🌟\n"
            response += f"📍 **Destination**: {pkg.get('destination', 'Paradise')}, {pkg.get('country', '')}\n"
            response += f"💰 **Price**: ${pkg.get('price', 'N/A')} for {pkg.get('duration', 'N/A')} days\n"
            response += f"⭐ **Rating**: {pkg.get('rating', 'N/A')}/5 stars\n"
            response += f"🎯 **Perfect for**: {pkg.get('category', 'travelers').title()} travelers\n"
            
            includes = pkg.get('includes', [])
            if includes:
                response += f"✅ **Includes**: {', '.join(includes[:4])}\n"
            
            highlights = pkg.get('highlights', [])
            if highlights:
                response += f"🏛️ **Highlights**: {', '.join(highlights[:3])}\n"
            
            response += "\n"
        
        response += "Which one catches your eye? I can tell you more details about any of these amazing destinations and help you book the perfect trip! 🗺️✈️"
        return response
    
    def handle_visa_query(self, user_msg, travel_data):
        """Handle visa requirement queries"""
        if travel_data and 'visa' in travel_data:
            visa_data = travel_data['visa']
            user_country = travel_data.get('user_country', 'US')
            
            # Try to identify destination from query
            destinations = {
                'france': 'France', 'paris': 'France',
                'japan': 'Japan', 'tokyo': 'Japan',
                'indonesia': 'Indonesia', 'bali': 'Indonesia',
                'uae': 'UAE', 'dubai': 'UAE',
                'greece': 'Greece', 'santorini': 'Greece'
            }
            
            for key, country in destinations.items():
                if key in user_msg:
                    visa_info = visa_data.get(country, {}).get('tourist_visa', {}).get(user_country)
                    if visa_info:
                        return self.format_visa_response(country, user_country, visa_info)
        
        return f"""📋 I'd be happy to help you with visa requirements! Visa needs can vary quite a bit depending on where you're traveling from and where you want to go.

Could you tell me:
🛂 Which country are you traveling from?
🌍 Which destination are you planning to visit?

Once I know that, I can give you the exact requirements, costs, and processing times for your specific situation! I want to make sure you have everything sorted well before your trip! ✈️"""
    
    def format_visa_response(self, destination, user_country, visa_info):
        """Format visa information in a friendly way"""
        required = visa_info.get('required', True)
        
        if not required:
            response = f"🎉 Great news! As a {user_country} citizen, you don't need a visa to visit {destination}! "
            
            if 'note' in visa_info:
                response += f"You can stay for {visa_info['note'].replace('-day visa-free', ' days')} as a tourist. "
            
            if visa_info.get('visa_on_arrival'):
                voa_price = visa_info.get('voa_price', 0)
                response += f"However, there's a visa-on-arrival option available for ${voa_price} if you need it for longer stays."
            
            response += "\n\nJust make sure your passport is valid for at least 6 months from your travel date! Easy peasy! ✈️🎫"
            
        else:
            price = visa_info.get('price', 'N/A')
            processing_days = visa_info.get('processing_days', 'N/A')
            
            response = f"📋 For your trip to {destination}, you'll need a tourist visa as a {user_country} citizen.\n\n"
            response += f"💰 **Cost**: ${price}\n"
            response += f"⏰ **Processing Time**: {processing_days} days\n\n"
            response += "I'd recommend applying at least 3-4 weeks before your trip to avoid any last-minute stress! "
            response += "The process is pretty straightforward - you'll just need your passport, photos, and completed application form.\n\n"
            response += "Would you like me to help you find some amazing travel packages for {destination} while you're planning? 🌍✨"
        
        return response
    
    def handle_destination_query(self, user_msg, travel_data):
        """Handle destination-specific queries"""
        destinations = ['paris', 'tokyo', 'bali', 'dubai', 'santorini']
        mentioned_dest = None
        
        for dest in destinations:
            if dest in user_msg:
                mentioned_dest = dest.title()
                break
        
        if mentioned_dest and travel_data:
            # Find packages for this destination
            packages = travel_data.get('packages', [])
            dest_packages = [pkg for pkg in packages if mentioned_dest.lower() in pkg.get('destination', '').lower()]
            
            if dest_packages:
                return f"🌟 {mentioned_dest} is absolutely stunning! " + self.format_package_response(dest_packages, f"{mentioned_dest} adventure")
        
        return f"✈️ {mentioned_dest or 'That destination'} sounds amazing! I'd love to help you plan the perfect trip there. What kind of experience are you looking for - romantic, adventurous, cultural, or luxury? And what's your approximate budget? I can find you some fantastic options! 🌍"
    
    def get_greeting_response(self):
        """Get a friendly greeting response"""
        greetings = [
            "Hi there! I'm Emma, your personal travel consultant! ✈️ I'm so excited to help you plan your next adventure! Whether you're dreaming of romantic Paris, tropical Bali, bustling Tokyo, or anywhere else in the world - I've got you covered with amazing packages, weather tips, and all the visa info you need. What kind of trip are you thinking about? 🌍✨",
            
            "Hello! Welcome to your travel planning adventure! 🎉 I'm here to help you discover incredible destinations and find the perfect package for your dream vacation. I have access to amazing deals, up-to-date weather information, and can help with all those visa questions too! What destination is calling your name? 🏖️🏔️",
            
            "Hey! So excited you're here! I love helping people plan unforgettable trips! ✨ Whether you want to sip wine in Santorini, explore temples in Tokyo, or relax on Bali's beautiful beaches - I've got insider knowledge and fantastic packages to make it happen. Tell me, what's your dream destination? 🌺🗼"
        ]
        
        import random
        return random.choice(greetings)
    
    def reset_chat(self):
        """Reset chat session"""
        if self.model:
            try:
                self.initialize_chat()
                print("✅ Chat reset successfully")
            except:
                pass
    
    def get_welcome_message(self):
        """Get welcome message after reset"""
        return "Hello! I'm Emma, your travel consultant! I've refreshed our conversation and I'm ready to help you plan an amazing trip! What destination is inspiring you today? ✈️🌍"
