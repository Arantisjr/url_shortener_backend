

# URL Shortener API

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/flask-2.0+-green.svg)
![PostgreSQL](https://img.shields.io/badge/postgresql-13+-blue.svg)

A high-performance URL shortening service with JWT authentication and analytics tracking.

## Features

- 🔗 Create short URLs from long URLs
- 🔐 JWT Authentication
- 📊 Click analytics tracking
- 🗑️ URL management (CRUD operations)
- 👤 User-specific URL collections
- ⚡ PostgreSQL backend
- 🔄 RESTful API design

## Prerequisites

- Python 3.8+
- PostgreSQL 13+
- pip

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/url-shortener.git
   cd url-shortener
   ```

2. **Set up virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   nano .env  # Edit with your credentials
   ```

5. **Database setup**
   ```bash
   flask db upgrade
   ```

## Configuration

Create `.env` file with these variables:

```ini
# Flask
FLASK_APP=run.py
FLASK_ENV=development

# Database
DATABASE_URI=postgresql://user:password@localhost/dbname

# Security
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-here

# URL Shortener
SHORT_DOMAIN=http://localhost:5000

# Google OAuth (Optional)
GOOGLE_CLIENT_ID=your-client-id
GOOGLE_CLIENT_SECRET=your-client-secret
```

## API Documentation

### Authentication

| Endpoint          | Method | Description          |
|-------------------|--------|----------------------|
| `/auth/register`  | POST   | Register new user    |
| `/auth/login`     | POST   | Login existing user  |

### URL Management

| Endpoint                | Method | Description                      |
|-------------------------|--------|----------------------------------|
| `/shorten`              | POST   | Create short URL                 |
| `/<short_code>`         | GET    | Redirect to original URL         |
| `/api/url/<short_code>` | GET    | Get URL details                  |
| `/api/url/<short_code>` | PUT    | Update URL destination           |
| `/api/url/<short_code>` | DELETE | Delete short URL                 |
| `/api/user/urls`        | GET    | List all user's shortened URLs   |

## Example Requests

**Create Short URL**
```bash
curl -X POST http://localhost:5000/shorten \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{"url":"https://example.com/very/long/url"}'
```

**Access Short URL**
```bash
curl -v http://localhost:5000/abc123
```

## Running the Server

Development:
```bash
flask run
```

Production:
```bash
gunicorn -w 4 -b :5000 'app:create_app()'
```

## Deployment

1. Set up PostgreSQL server
2. Configure production environment variables
3. Set up reverse proxy (Nginx/Apache)
4. Enable HTTPS

