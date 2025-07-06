# Database Configuration Setup

Your Flask application is now configured to use environment variables for database connection. Here's how to set it up:

## Step 1: Create Your .env File

Copy the example file and customize it:

```bash
cp .env.example .env
```

Then edit the `.env` file with your actual database credentials:

```bash
# Database Configuration
DB_SERVER=adsforafrica-server.database.windows.net
DB_PORT=1433
DB_NAME=ads
DB_USERS_NAME=userstorage
DB_USERNAME=adsforafrica-server-admin
DB_PASSWORD=YOUR_ACTUAL_PASSWORD_HERE

# Flask Configuration
FLASK_SECRET_KEY=YOUR_ACTUAL_SECRET_KEY_HERE

# Email Configuration (if needed)
EMAIL_USERNAME=your_email_here
EMAIL_PASSWORD=your_email_password_here

# Development/Production
FLASK_ENV=development
FLASK_CONFIG=development
```

## Step 2: Test Your Configuration

Run the test script to verify everything is set up correctly:

```bash
python test_db_config.py
```

This will check:
- ✅ All required environment variables are set
- ✅ Connection strings are properly formatted
- ✅ Flask app can be created with the configuration

## Step 3: Run Your Application

Once the test passes, you can run your app:

```bash
python app.py
```

## Environment Configurations

The app supports different configurations based on `FLASK_CONFIG`:

- **`development`** (default): Debug mode enabled, full logging
- **`production`**: Debug mode disabled, optimized for production
- **`testing`**: Uses in-memory SQLite database for testing

## Database Connection Details

The configuration automatically creates two database connections:

1. **Main Database** (`SQLALCHEMY_DATABASE_URI`):
   - Server: `DB_SERVER`
   - Database: `DB_NAME` (default: 'ads')
   - Used for: Ad data, campaigns, etc.

2. **Users Database** (`SQLALCHEMY_BINDS['users']`):
   - Server: `DB_SERVER` (same server)
   - Database: `DB_USERS_NAME` (default: 'userstorage')
   - Used for: User accounts, authentication

## Security Features

- ✅ Password URL encoding for special characters
- ✅ SSL encryption (`Encrypt=yes`)
- ✅ Connection pooling with pre-ping
- ✅ Connection timeout (30 seconds)
- ✅ Secret key from environment

## Troubleshooting

If you encounter issues:

1. **Missing .env file**: Make sure you created `.env` from `.env.example`
2. **Database connection errors**: Verify your credentials in `.env`
3. **Import errors**: Ensure all blueprint files are in place
4. **Permission errors**: Check if the `reqmod/logging_storage/` directory exists

## Production Deployment

For production, set:
```bash
FLASK_CONFIG=production
FLASK_ENV=production
```

This will:
- Disable debug mode
- Use production-optimized settings
- Require proper secret key and database credentials
