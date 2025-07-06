#!/usr/bin/env python3
"""
Configuration Test Script
This script tests that the configuration is properly reading environment variables
"""

import os
from dotenv import load_dotenv
from config import config

def test_configuration():
    """Test that configuration is reading environment variables correctly"""
    
    # Load environment variables
    load_dotenv()
    
    print("=== Configuration Test ===\n")
    
    # Get the development config
    dev_config = config['development']()
    
    print("Environment Variables:")
    print(f"DB_HOST: {os.getenv('DB_HOST')}")
    print(f"DB_PORT: {os.getenv('DB_PORT')}")
    print(f"DB_NAME: {os.getenv('DB_NAME')}")
    print(f"DB_USERNAME: {os.getenv('DB_USERNAME')}")
    print(f"DB_SSLMODE: {os.getenv('DB_SSLMODE')}")
    print(f"FLASK_SECRET_KEY: {os.getenv('FLASK_SECRET_KEY')[:10]}..." if os.getenv('FLASK_SECRET_KEY') else "Not set")
    
    print("\nGenerated Connection Strings:")
    print(f"Main DB URI: {dev_config.SQLALCHEMY_DATABASE_URI}")
    print(f"Users DB URI: {dev_config.USERS_DATABASE_URI}")
    
    print("\n✅ Configuration test completed!")
    print("\nTo complete the setup:")
    print("1. Edit your .env file and replace 'your_password_here' with your actual database password")
    print("2. Replace 'your_secret_key_here' with a secure secret key")
    print("3. Run: python3 app.py")

if __name__ == '__main__':
    test_configuration()
