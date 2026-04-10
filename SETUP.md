# MathStep AI - Authentication API Setup Guide

## 📋 Prerequisites

- Python 3.10+
- PostgreSQL 12+
- pip or poetry

---

## 🚀 Installation

### 1. Clone Repository
```bash
cd d:\mathstep-ai
```

### 2. Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Setup Environment Variables
```bash
# Copy example to .env
copy .env.example .env

# Edit .env with your configuration
# - Database URL
# - Secret key (generate: python -c "import secrets; print(secrets.token_urlsafe(32))")
# - Google OAuth credentials
```

### 5. Create PostgreSQL Database
```bash
# Connect to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE mathstep_db;
CREATE USER mathstep_user WITH PASSWORD 'your_password';
ALTER ROLE mathstep_user SET client_encoding TO 'utf8';
ALTER ROLE mathstep_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE mathstep_user SET default_transaction_deferrable TO on;
ALTER ROLE mathstep_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE mathstep_db TO mathstep_user;
\q
```

### 6. Run Database Migrations
```bash
# Tables are automatically created on app startup
# If needed, run:
python -c "from app.db.base import Base; from app.db.session import engine; Base.metadata.create_all(bind=engine)"
```

---

## 🏃 Running the Server

### Development Mode
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode
```bash
gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:8000
```

The API will be available at: `http://localhost:8000`

API Documentation: `http://localhost:8000/docs` (Swagger UI)
Alternative Docs: `http://localhost:8000/redoc` (ReDoc)

---

## 🧪 Testing the API

### 1. Register Student
```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "student@example.com",
    "password": "password123",
    "role": "STUDENT"
  }'
```

### 2. Register Parent
```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "parent@example.com",
    "password": "password123",
    "role": "PARENT"
  }'
```

### 3. Login
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "student@example.com",
    "password": "password123"
  }'
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "student@example.com",
  "role": "STUDENT"
}
```

### 4. Get Current User (Protected Endpoint)
```bash
curl -X GET "http://localhost:8000/auth/me" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 5. Google OAuth Login (Web Flow)
```
Open: http://localhost:8000/auth/google/login
```
This redirects to Google login, then back to `/auth/google/callback` with the token.

---

## 📚 API Endpoints

### Authentication Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|-----------------|
| POST | `/auth/register` | Register new user | ❌ |
| POST | `/auth/login` | Login with email/password | ❌ |
| GET | `/auth/google/login` | Redirect to Google login | ❌ |
| GET | `/auth/google/callback` | Handle Google OAuth callback | ❌ |
| POST | `/auth/google/login` | Login with Google ID token | ❌ |
| GET | `/auth/me` | Get current user info | ✅ |
| GET | `/health` | Health check | ❌ |
| GET | `/` | Root/Status | ❌ |

---

## 🏗️ Project Structure Explanation

```
app/
├── main.py                    # FastAPI app entry point
├── core/
│   ├── config.py             # Configuration management
│   ├── security.py           # Password hashing & JWT
│   └── oauth.py              # Google OAuth utilities
├── db/
│   ├── session.py            # Database session management
│   └── base.py               # SQLAlchemy base
├── models/
│   ├── user.py               # User model
│   ├── student.py            # Student model
│   └── parent.py             # Parent model
├── schemas/
│   └── auth.py               # Pydantic schemas
├── services/
│   └── auth_service.py       # Business logic
├── api/
│   └── auth.py               # API routes
└── utils/
    └── dependencies.py       # Dependency injection
```

---

## 🔐 Security Best Practices Implemented

✅ Passwords hashed with bcrypt
✅ JWT tokens with expiration
✅ CORS middleware configured
✅ Environment variables for secrets
✅ Role-based access control ready
✅ HTTP Bearer authentication
✅ SQL injection prevention (SQLAlchemy ORM)
✅ Password validation (minimum 8 characters)

---

## 🐛 Troubleshooting

### Database Connection Error
```
Error: could not translate host name "localhost" to address
```
**Solution:** Ensure PostgreSQL is running and DATABASE_URL is correct in .env

### Google OAuth Not Working
```
Error: Invalid Google token
```
**Solution:**
1. Verify GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET in .env
2. Add redirect URI to Google Cloud Console
3. Generate new credentials if needed

### Port Already in Use
```
Address already in use
```
**Solution:** Change port with `--port 9000` or kill process on port 8000

---

## 📝 Environment Variables Reference

| Variable | Description | Example |
|----------|-------------|---------|
| DATABASE_URL | PostgreSQL connection | postgresql://user:pass@localhost/db |
| SECRET_KEY | JWT signing key | random-string-32-chars-minimum |
| ALGORITHM | JWT algorithm | HS256 |
| ACCESS_TOKEN_EXPIRE_MINUTES | Token expiration | 60 |
| GOOGLE_CLIENT_ID | Google OAuth client ID | xxx.apps.googleusercontent.com |
| GOOGLE_CLIENT_SECRET | Google OAuth secret | xxx |
| GOOGLE_REDIRECT_URI | OAuth callback URL | http://localhost:8000/auth/google/callback |
| DEBUG | Debug mode | False |

---

## 🚀 Deployment

### Using Gunicorn + Nginx

1. Install production dependencies:
```bash
pip install gunicorn
```

2. Run with Gunicorn:
```bash
gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:8000
```

3. Configure Nginx as reverse proxy pointing to `localhost:8000`

---

## 📦 Next Steps

### Future Features (Not Implemented Yet)
- [ ] Email verification
- [ ] Password reset flow
- [ ] Two-factor authentication
- [ ] Refresh tokens
- [ ] Parent-Student linking
- [ ] Learning features

### To Add Role-Based Endpoints
Use the provided dependencies in `app/utils/dependencies.py`:

```python
from app.utils.dependencies import get_student_user, get_parent_user

@router.get("/student/profile")
def get_student_profile(current_user: User = Depends(get_student_user)):
    # Only accessible by STUDENT role
    pass

@router.get("/parent/profile")
def get_parent_profile(current_user: User = Depends(get_parent_user)):
    # Only accessible by PARENT role
    pass
```

---

## 📞 Support

For issues or questions, check:
1. API documentation: http://localhost:8000/docs
2. Error messages in console logs
3. .env configuration
4. Database connection status

---

## 📄 License

This project is part of MathStep AI.
