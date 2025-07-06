#!/usr/bin/env python3
"""
Database Connection Test Script
This script tests the database connection using your .env configuration
"""

import os
from dotenv import load_dotenv
from urllib.parse import quote_plus

# Load environment variables
load_dotenv()

def test_env_variables():
    """Test that all required environment variables are set"""
    required_vars = [
        'DB_SERVER', 'DB_PORT', 'DB_NAME', 'DB_USERS_NAME', 
        'DB_USERNAME', 'DB_PASSWORD', 'FLASK_SECRET_KEY'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var) or os.getenv(var) == 'your_password_here' or os.getenv(var) == 'your_secret_key_here':
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ Missing or default environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nPlease create a .env file based on .env.example and set proper values.")
        return False
    else:
        print("✅ All required environment variables are set")
        return True

def test_connection_string():
    """Test that the connection string is properly formatted"""
    try:
        # Database configuration from environment
        db_server = os.getenv('DB_SERVER')
        db_port = os.getenv('DB_PORT')
        db_name = os.getenv('DB_NAME')
        db_users_name = os.getenv('DB_USERS_NAME')
        db_username = os.getenv('DB_USERNAME')
        db_password = os.getenv('DB_PASSWORD')
        
        # Create connection strings
        main_db_uri = f"mssql+pyodbc://{db_username}:{quote_plus(db_password)}@{db_server}:{db_port}/{db_name}?driver=ODBC+Driver+17+for+SQL+Server"
        users_db_uri = f"mssql+pyodbc://{db_username}:{quote_plus(db_password)}@{db_server}:{db_port}/{db_users_name}?driver=ODBC+Driver+17+for+SQL+Server"
        
        print("✅ Connection strings generated successfully:")
        print(f"   Main DB: {main_db_uri[:50]}...")
        print(f"   Users DB: {users_db_uri[:50]}...")
        
        return True
    except Exception as e:
        print(f"❌ Error generating connection strings: {e}")
        return False

def test_flask_app():
    """Test that the Flask app can be created with the configuration"""
    try:
        from app import create_app
        
        app = create_app()
        
        with app.app_context():
            print("✅ Flask app created successfully")
            print(f"   Config: {app.config.get('SQLALCHEMY_DATABASE_URI', 'Not set')[:50]}...")
            print(f"   Secret Key: {'Set' if app.config.get('SECRET_KEY') else 'Not set'}")
            
        return True
    except Exception as e:
        print(f"❌ Error creating Flask app: {e}")
        return False

if __name__ == '__main__':
    print("🔍 Testing Database Configuration\n")
    
    # Test 1: Environment variables
    if not test_env_variables():
        exit(1)
    
    print()
    
    # Test 2: Connection strings
    if not test_connection_string():
        exit(1)
    
    print()
    
    # Test 3: Flask app creation
    if not test_flask_app():
        exit(1)
    
    print("\n🎉 All tests passed! Your database configuration is ready.")
    print("\nTo run your app:")
    print("   python app.py")
