#!/usr/bin/env python3
"""
PostgreSQL Connection Command Generator
This script generates the psql command to connect to your DigitalOcean database
"""

import os
from dotenv import load_dotenv

def generate_psql_command():
    """Generate the psql command for connecting to the database"""
    
    # Load environment variables
    load_dotenv()
    
    # Get database credentials from environment
    host = os.getenv('DB_HOST', 'adsforafrica-do-user-16063394-0.i.db.ondigitalocean.com')
    port = os.getenv('DB_PORT', '25060')
    database = os.getenv('DB_NAME', 'defaultdb')
    username = os.getenv('DB_USERNAME', 'doadmin')
    sslmode = os.getenv('DB_SSLMODE', 'require')
    
    print("=== PostgreSQL Connection Commands ===\n")
    
    # Method 1: Using connection string format
    print("Method 1: Using PostgreSQL connection string")
    print("Replace 'YOUR_PASSWORD' with your actual database password:")
    print()
    connection_string = f"postgresql://{username}:YOUR_PASSWORD@{host}:{port}/{database}?sslmode={sslmode}"
    print(f"psql '{connection_string}'")
    print()
    
    # Method 2: Using individual parameters
    print("Method 2: Using individual parameters")
    print("Replace 'YOUR_PASSWORD' with your actual database password:")
    print()
    psql_command = f"psql -h {host} -p {port} -U {username} -d {database} --set=sslmode={sslmode}"
    print(f"{psql_command}")
    print("(You will be prompted to enter your password)")
    print()
    
    # Method 3: With password in environment variable
    print("Method 3: Using environment variable for password (more secure)")
    print("First set your password as an environment variable:")
    print("export PGPASSWORD='your_actual_password_here'")
    print("Then run:")
    print(f"{psql_command}")
    print()
    
    # Method 4: Test connection only
    print("Method 4: Quick connection test")
    print("To just test if you can connect (will exit immediately):")
    print(f'{psql_command} -c "SELECT version();"')
    print()
    
    print("=== Database Information ===")
    print(f"Host: {host}")
    print(f"Port: {port}")
    print(f"Database: {database}")
    print(f"Username: {username}")
    print(f"SSL Mode: {sslmode}")
    print()
    
    print("=== Prerequisites ===")
    print("Make sure you have PostgreSQL client installed:")
    print("macOS: brew install postgresql")
    print("Ubuntu/Debian: sudo apt-get install postgresql-client")
    print("CentOS/RHEL: sudo yum install postgresql")

if __name__ == '__main__':
    generate_psql_command()
