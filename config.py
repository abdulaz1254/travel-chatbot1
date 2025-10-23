import os
import secrets
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Configuration class for the Travel AI Assistant application"""
    
    # Gemini AI Configuration
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', 'your-gemini-api-key-here')
    
    # Flask Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', secrets.token_hex(16))
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
    
    # Application Configuration
    FLASK_APP = 'app.py'
    FLASK_ENV = 'development' if DEBUG else 'production'
    
    # Data Configuration
    DATA_DIR = 'data'
    
    # API Configuration
    API_TIMEOUT = 30
    MAX_TOKENS = 2048
    
    @staticmethod
    def validate_config():
        """Validate that required configuration is present"""
        errors = []
        
        if not Config.GEMINI_API_KEY or Config.GEMINI_API_KEY == 'your-gemini-api-key-here':
            errors.append("GEMINI_API_KEY is not set. Please add your Gemini API key to your .env file")
        
        return errors
