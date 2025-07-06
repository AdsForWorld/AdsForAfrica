#!/usr/bin/env python3
"""
Database Connection Test Script
This script tests the database connection using the environment variables
"""

import os
from dotenv import load_dotenv
from app import create_app, db
from app.models import User, Ad

def test_database_connection():
    """Test the database connection and basic operations"""
    
    # Load environment variables
    load_dotenv()
    
    # Create the Flask app
    app = create_app()
    
    try:
        with app.app_context():
            # Test the database connection
            print("Testing database connection...")
            
            # Try to create tables
            print("Creating database tables...")
            db.create_all()
            print("✅ Database tables created successfully!")
            
            # Test basic query
            print("Testing basic query...")
            user_count = User.query.count()
            ad_count = Ad.query.count()
            print(f"✅ Users in database: {user_count}")
            print(f"✅ Ads in database: {ad_count}")
            
            # Test database info
            print(f"✅ Database URI: {app.config['SQLALCHEMY_DATABASE_URI'][:50]}...")
            print(f"✅ Users Database URI: {app.config['SQLALCHEMY_BINDS']['users'][:50]}...")
            
            print("\n🎉 Database connection test PASSED!")
            return True
            
    except Exception as e:
        print(f"❌ Database connection test FAILED!")
        print(f"Error: {str(e)}")
        print("\nPlease check:")
        print("1. Your .env file has the correct database credentials")
        print("2. The database server is accessible")
        print("3. The database exists")
        print("4. psycopg2-binary is installed: pip install psycopg2-binary")
        return False

if __name__ == '__main__':
    print("=== AdsForAfrica Database Connection Test ===\n")
    test_database_connection()
