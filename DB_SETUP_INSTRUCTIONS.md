# Database Setup Instructions

## Step 1: Create your .env file

Copy the `.env.example` to `.env` and update with your actual password:

```bash
cp .env.example .env
```

Then edit `.env` and replace `your_password_here` with your actual database password.

## Step 2: Install PostgreSQL dependencies

```bash
pip install psycopg2-binary
```

## Step 3: Test the database connection

```bash
python test_db_connection.py
```

## Your Database Configuration

Based on your credentials, your `.env` file should look like this:

```
# Database Configuration - DigitalOcean PostgreSQL
DB_HOST=adsforafrica-do-user-16063394-0.i.db.ondigitalocean.com
DB_PORT=25060
DB_NAME=defaultdb
DB_USERS_NAME=defaultdb
DB_USERNAME=doadmin
DB_PASSWORD=your_actual_password_here
DB_SSLMODE=require

# Flask Configuration
FLASK_SECRET_KEY=your_secret_key_here

# Email Configuration (if needed)
EMAIL_USERNAME=your_email_here
EMAIL_PASSWORD=your_email_password_here

# Development/Production
FLASK_ENV=development
FLASK_CONFIG=development
```

## Step 4: Run the application

```bash
python app.py
```

The application will now connect to your DigitalOcean PostgreSQL database!
