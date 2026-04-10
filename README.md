# MathStep AI - Authentication API

Production-ready authentication system built with FastAPI, featuring user registration, email/password login, and Google OAuth integration.

## ✨ Features

- ✅ **User Registration** - Register as STUDENT or PARENT
- ✅ **Email/Password Authentication** - Secure login with JWT tokens
- ✅ **Google OAuth 2.0** - Single sign-on via Google
- ✅ **Role-Based Access** - Support for STUDENT and PARENT roles
- ✅ **JWT Tokens** - Stateless authentication with expiration
- ✅ **Bcrypt Password Hashing** - Industry-standard security
- ✅ **SQLAlchemy ORM** - Type-safe database operations
- ✅ **Pydantic Validation** - Request/response validation
- ✅ **Dependency Injection** - Clean, testable code
- ✅ **Auto-Generated Documentation** - Swagger UI + ReDoc

## 🎯 Core Entities

### User
- UUID primary key
- Email (unique)
- Password hash (optional for OAuth)
- Google ID (for OAuth login)
- Role: STUDENT or PARENT
- Timestamps

### Student
- Linked to User via user_id
- Name (optional)
- Grade level (optional)
- Created at timestamp

### Parent
- Linked to User via user_id
- Name (optional)
- Created at timestamp

## 🏗️ Architecture

```
┌─────────────────┐
│   FastAPI App   │
├─────────────────┤
│  API Routes     │ ← Auth endpoints
│  (api/auth.py)  │
└────────┬────────┘
         │
┌────────▼────────┐
│   Services      │ ← Business logic
│(auth_service.py)│
└────────┬────────┘
         │
┌────────▼────────┐
│   Database      │ ← SQLAlchemy models
│   (db/session)  │
└─────────────────┘
```

## 🚀 Quick Start

### 1. Install
```bash
pip install -r requirements.txt
```

### 2. Setup .env
```bash
cp .env.example .env
# Edit .env with your configuration
```

### 3. Create Database
```bash
psql -U postgres
CREATE DATABASE mathstep_db;
CREATE USER mathstep_user WITH PASSWORD 'password';
GRANT ALL PRIVILEGES ON DATABASE mathstep_db TO mathstep_user;
```

### 4. Run Server
```bash
uvicorn app.main:app --reload
```

### 5. Visit Documentation
- Swagger: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 📡 API Examples

### Register as Student
```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "securepass123",
    "role": "STUDENT"
  }'
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "john@example.com",
  "role": "STUDENT"
}
```

### Login
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "securepass123"
  }'
```

### Get Current User
```bash
curl -X GET "http://localhost:8000/auth/me" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### Google OAuth
```bash
# Redirect user to
http://localhost:8000/auth/google/login
```

## 🔐 Security Features

- **Password Hashing**: Bcrypt with salt
- **JWT Tokens**: HS256 algorithm with expiration
- **CORS**: Configurable cross-origin requests
- **Input Validation**: Pydantic schemas
- **SQL Injection Prevention**: SQLAlchemy ORM
- **Role-Based Access**: Optional role enforcement

## 📦 Tech Stack

- **Framework**: FastAPI 0.109
- **Database**: PostgreSQL + SQLAlchemy
- **Authentication**: JWT + Bcrypt + Google OAuth
- **Validation**: Pydantic v2
- **Server**: Uvicorn

## 🗂️ Project Structure

```
app/
├── main.py                 # FastAPI application
├── core/
│   ├── config.py          # Configuration & settings
│   ├── security.py        # JWT & password hashing
│   └── oauth.py           # Google OAuth utilities
├── db/
│   ├── session.py         # Database connection
│   └── base.py            # SQLAlchemy base
├── models/
│   ├── user.py            # User model
│   ├── student.py         # Student model
│   └── parent.py          # Parent model
├── schemas/
│   └── auth.py            # Pydantic schemas
├── services/
│   └── auth_service.py    # Business logic
├── api/
│   └── auth.py            # API endpoints
└── utils/
    └── dependencies.py    # Dependency injection
```

## 🔑 Environment Variables

```env
# Database
DATABASE_URL=postgresql://user:password@localhost/mathstep_db

# JWT
SECRET_KEY=your-secret-key-minimum-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# Google OAuth
GOOGLE_CLIENT_ID=xxx.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=xxx
GOOGLE_REDIRECT_URI=http://localhost:8000/auth/google/callback

# Server
DEBUG=False
```

## 💡 Usage Examples

### Role-Based Endpoints

```python
from fastapi import APIRouter, Depends
from app.utils.dependencies import get_student_user, get_parent_user

router = APIRouter()

@router.get("/dashboard")
def student_dashboard(current_user = Depends(get_student_user)):
    """Only accessible by students"""
    return {"student": current_user.email}

@router.get("/parent/reports")
def parent_reports(current_user = Depends(get_parent_user)):
    """Only accessible by parents"""
    return {"parent": current_user.email}
```

### Protected Endpoints

```python
from app.utils.dependencies import get_current_user

@router.get("/profile")
def get_profile(current_user = Depends(get_current_user)):
    """Requires valid JWT token"""
    return {"profile": current_user.email}
```

## 🚀 Production Deployment

### Using Gunicorn
```bash
pip install gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:8000
```

### Environment Variables for Production
- Use strong SECRET_KEY
- Set DEBUG=False
- Configure proper database URL
- Use environment-specific GOOGLE_REDIRECT_URI

### Docker Ready
Can be containerized with any Docker image with Python 3.10+

## 📚 API Reference

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/auth/register` | POST | ❌ | Register new user |
| `/auth/login` | POST | ❌ | Login with credentials |
| `/auth/google/login` | GET | ❌ | Redirect to Google |
| `/auth/google/callback` | GET | ❌ | OAuth callback |
| `/auth/google/login` | POST | ❌ | Login with token |
| `/auth/me` | GET | ✅ | Get current user |
| `/health` | GET | ❌ | Health check |

## 🎓 Learning Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy ORM](https://docs.sqlalchemy.org/)
- [JWT Guide](https://jwt.io/introduction)
- [Google OAuth 2.0](https://developers.google.com/identity/protocols/oauth2)

## 📋 Checklist for Setup

- [ ] Python 3.10+ installed
- [ ] PostgreSQL running
- [ ] Virtual environment created
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] `.env` file created with valid values
- [ ] Database created
- [ ] Server running (`uvicorn app.main:app --reload`)
- [ ] API accessible at `http://localhost:8000`
- [ ] Swagger docs accessible at `http://localhost:8000/docs`

## 🤝 Contributing

1. Create a feature branch
2. Make your changes
3. Test thoroughly
4. Submit a pull request

## 📝 License

MathStep AI - All Rights Reserved

## 📞 Support

For detailed setup instructions, see [SETUP.md](SETUP.md)

---
**Ready to use in production.** Built with security, scalability, and developer experience in mind. ⚡








<!-- Fix lỗi pg per -->
<!-- psql -U postgres
** cấp quyền database
GRANT ALL PRIVILEGES ON DATABASE mathstep_db TO odoo;

-- chuyển qua DB
\c mathstep_db

-- cấp quyền schema
GRANT USAGE, CREATE ON SCHEMA public TO odoo;

-- set owner (quan trọng)
ALTER SCHEMA public OWNER TO odoo; -->

<!-- uvicorn app.main:app --reload -->