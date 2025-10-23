import json
import os
from datetime import datetime

class TravelDataProcessor:
    def __init__(self):
        self.data_dir = "data"
        self.travel_packages = self.load_json("travel_packages.json")
        self.weather_data = self.load_json("weather_data.json")
        self.visa_data = self.load_json("visa_prices.json")

    def load_json(self, filename):
        """Load JSON data from file"""
        try:
            file_path = os.path.join(self.data_dir, filename)
            with open(file_path, 'r', encoding='utf-8') as file:
                return json.load(file)
        except FileNotFoundError:
            print(f"Warning: {filename} not found")
            return {}
        except json.JSONDecodeError:
            print(f"Warning: Invalid JSON in {filename}")
            return {}

    def filter_packages_by_budget(self, min_budget=0, max_budget=float('inf')):
        """Filter travel packages by budget range"""
        if 'packages' not in self.travel_packages:
            return []
        
        filtered = []
        for package in self.travel_packages['packages']:
            if min_budget <= package.get('price', 0) <= max_budget:
                filtered.append(package)
        
        return sorted(filtered, key=lambda x: x.get('price', 0))

    def filter_packages_by_category(self, category):
        """Filter packages by category (romantic, adventure, cultural, etc.)"""
        if 'packages' not in self.travel_packages:
            return []
        
        filtered = []
        for package in self.travel_packages['packages']:
            if package.get('category', '').lower() == category.lower():
                filtered.append(package)
        
        return filtered

    def filter_packages_by_destination(self, destination):
        """Filter packages by destination"""
        if 'packages' not in self.travel_packages:
            return []
        
        filtered = []
        for package in self.travel_packages['packages']:
            if destination.lower() in package.get('destination', '').lower():
                filtered.append(package)
        
        return filtered

    def get_weather_info(self, destination, season=None):
        """Get weather information for a destination"""
        if 'weather_data' not in self.weather_data:
            return None
        
        dest_weather = self.weather_data['weather_data'].get(destination)
        if not dest_weather:
            return None
        
        if season:
            return dest_weather.get(season.lower())
        
        return dest_weather

    def get_visa_info(self, destination_country, user_country, visa_type="tourist_visa"):
        """Get visa information and costs"""
        if 'visa_data' not in self.visa_data:
            return None
        
        country_visa = self.visa_data['visa_data'].get(destination_country)
        if not country_visa:
            return None
        
        visa_type_data = country_visa.get(visa_type, {})
        return visa_type_data.get(user_country)

    def search_packages(self, query_params):
        """Search packages based on multiple criteria"""
        packages = self.travel_packages.get('packages', [])
        
        # Filter by budget
        if 'min_budget' in query_params or 'max_budget' in query_params:
            min_budget = query_params.get('min_budget', 0)
            max_budget = query_params.get('max_budget', float('inf'))
            packages = [p for p in packages if min_budget <= p.get('price', 0) <= max_budget]
        
        # Filter by category
        if 'category' in query_params:
            category = query_params['category'].lower()
            packages = [p for p in packages if p.get('category', '').lower() == category]
        
        # Filter by destination
        if 'destination' in query_params:
            destination = query_params['destination'].lower()
            packages = [p for p in packages if destination in p.get('destination', '').lower()]
        
        # Filter by duration
        if 'max_duration' in query_params:
            max_duration = query_params['max_duration']
            packages = [p for p in packages if p.get('duration', 0) <= max_duration]
        
        return packages

    def get_relevant_data(self, user_message):
        """Get relevant data based on user message"""
        user_message = user_message.lower()
        relevant_data = {}
        
        # Determine what data to include based on keywords
        if any(word in user_message for word in ['package', 'trip', 'travel', 'vacation', 'holiday']):
            relevant_data['packages'] = self.travel_packages.get('packages', [])
        
        if any(word in user_message for word in ['weather', 'climate', 'temperature', 'rain']):
            relevant_data['weather'] = self.weather_data.get('weather_data', {})
        
        if any(word in user_message for word in ['visa', 'passport', 'entry', 'requirements']):
            relevant_data['visa'] = self.visa_data.get('visa_data', {})
        
        # Extract specific destinations mentioned
        destinations = ['paris', 'tokyo', 'bali', 'france', 'japan', 'indonesia']
        mentioned_destinations = [dest for dest in destinations if dest in user_message]
        
        if mentioned_destinations and not relevant_data:
            # If destinations are mentioned but no specific data type, include all
            relevant_data = {
                'packages': self.travel_packages.get('packages', []),
                'weather': self.weather_data.get('weather_data', {}),
                'visa': self.visa_data.get('visa_data', {})
            }
        
        return relevant_data
