# test_config.py
try:
    from config import Config
    print("✅ Config class imported successfully!")
    print(f"Debug mode: {Config.DEBUG}")
    print(f"Gemini API Key configured: {'Yes' if Config.GEMINI_API_KEY != 'your-gemini-api-key-here' else 'No'}")
    print(f"Secret Key configured: {'Yes' if Config.SECRET_KEY != 'your-secret-key-here' else 'No'}")
    
    # Validate configuration
    errors = Config.validate_config()
    if errors:
        print("\n⚠️  Configuration issues:")
        for error in errors:
            print(f"  - {error}")
    else:
        print("✅ All configuration is valid!")
        
except ImportError as e:
    print(f"❌ Cannot import Config: {e}")
except Exception as e:
    print(f"❌ Error: {e}")
