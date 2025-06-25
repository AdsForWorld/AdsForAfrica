#!/bin/bash

# Exit if any command fails
set -e

# Add Microsoft ODBC repository
curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
curl https://packages.microsoft.com/config/debian/10/prod.list > /etc/apt/sources.list.d/mssql-release.list

# Update package lists
apt-get update

# Install SQL Server ODBC driver
ACCEPT_EULA=Y apt-get install -y msodbcsql17

# Install required build tools and ODBC dev libraries
apt-get install -y unixodbc-dev gcc g++ python3-dev

# Upgrade pip just in case
pip install --upgrade pip

# Install pyodbc inside the app's virtual environment
pip install pyodbc
