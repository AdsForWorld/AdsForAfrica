# Flask Blueprints Refactor

This document explains how your monolithic Flask application has been segmented into blueprints for better organization and maintainability.

## New Project Structure

```
AdsForAfrica/
├── app/
│   ├── __init__.py          # Application factory and configuration
│   ├── models.py            # Database models (Ad, User)
│   ├── utils.py             # Utility functions (dateunix, etc.)
│   ├── main/
│   │   └── __init__.py      # Main blueprint (public pages)
│   ├── auth/
│   │   └── __init__.py      # Authentication blueprint
│   ├── ads/
│   │   └── __init__.py      # Ad management blueprint
│   ├── admin/
│   │   └── __init__.py      # Admin/reviewer blueprint
│   └── api/
│       └── __init__.py      # API endpoints blueprint
├── config.py                # Configuration classes
├── run.py                   # Application entry point
├── requirements.txt         # Dependencies
└── [existing directories...]
```

## Blueprint Segmentation

### 1. Main Blueprint (`/`)
- **Routes**: `/`, `/about`, `/devlog`, `/robots.txt`, `/volunteer`, `/apply`, `/datares`
- **Purpose**: Public-facing pages and general information
- **Templates**: `index.html`, `abt.html`, `devlogs.html`

### 2. Auth Blueprint (`/auth`)
- **Routes**: `/auth/login`, `/auth/signup`, `/auth/credentialschk`, `/auth/register/user`, `/auth/emailverify/<id>`
- **Purpose**: User authentication and registration
- **Templates**: `login.html`, `signup.html`

### 3. Ads Blueprint (`/ads`)
- **Routes**: `/ads/click/<adid>`, `/ads/show/<adid>/`, `/ads/impressions/<ad>`
- **Purpose**: Ad display, tracking, and management
- **Templates**: `viewad.html`, `notfound.html`

### 4. Admin Blueprint (`/admin`)
- **Routes**: `/admin/adreview`, `/admin/registerad`, `/admin/register/admin`
- **Purpose**: Administrative functions and ad review
- **Templates**: `adview/index.html`, `register_ad.html`

### 5. API Blueprint (`/api`)
- **Routes**: `/api/register/ad`, `/api/getallads`, `/api/uptime`, `/api/accessleasekey`
- **Purpose**: Backend API endpoints for data operations
- **Returns**: JSON responses

## Key Benefits

1. **Separation of Concerns**: Each blueprint handles a specific domain
2. **Better Organization**: Related routes are grouped together
3. **Maintainability**: Easier to locate and modify specific functionality
4. **Scalability**: New features can be added as separate blueprints
5. **Testing**: Individual blueprints can be tested in isolation
6. **Team Development**: Different developers can work on different blueprints

## Configuration Management

The new structure uses environment-based configuration:
- `DevelopmentConfig`: For local development
- `ProductionConfig`: For production deployment
- `TestingConfig`: For running tests

## Migration from Original Structure

### URL Changes
- Login: `app.py:login()` → `/auth/login`
- API endpoints: `/backend/*` → `/api/*`
- Admin functions: Direct routes → `/admin/*`
- Ad operations: Direct routes → `/ads/*`

### Global Variables
All global variables (`keys`, `adminkeys`, `userkeys`, etc.) are still accessible but now centralized in `app/__init__.py`.

## Running the Application

Instead of running `app.py` directly:

```bash
python run.py
```

Or for production:
```bash
export FLASK_CONFIG=production
python run.py
```

## Next Steps for Further Improvement

1. **Move global variables to a proper session/cache system** (Redis/Memcached)
2. **Implement proper error handlers** in each blueprint
3. **Add API versioning** (`/api/v1/...`)
4. **Create separate template directories** for each blueprint
5. **Add comprehensive logging** per blueprint
6. **Implement blueprint-specific middleware**
7. **Add unit tests** for each blueprint

This refactoring maintains all existing functionality while providing a much more maintainable and scalable code structure.
