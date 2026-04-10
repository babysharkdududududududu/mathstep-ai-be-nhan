# 🚀 Quick Reference Guide

## ⚡ 5-Minute Startup

```bash
# 1. Install
pip install -r requirements.txt

# 2. Setup
copy .env.example .env
# Edit DATABASE_URL in .env

# 3. Database (Docker)
docker-compose up -d

# 4. Run
uvicorn app.main:app --reload

# 5. Test
http://localhost:8000/docs
```

---

## 📡 API Quick Commands

### Register
```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email":"user@test.com",
    "password":"password123",
    "role":"STUDENT"
  }'
```

### Login
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email":"user@test.com",
    "password":"password123"
  }'
```

### Protected Endpoint
```bash
curl -X GET http://localhost:8000/auth/me \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 🗂️ File Location Quick Reference

| What | File |
|------|------|
| Main app | `app/main.py` |
| Routes | `app/api/auth.py` |
| Business logic | `app/services/auth_service.py` |
| Database models | `app/models/` |
| Schemas (validation) | `app/schemas/auth.py` |
| Security setup | `app/core/security.py` |
| Config | `app/core/config.py` |
| Database connection | `app/db/session.py` |
| Dependencies | `app/utils/dependencies.py` |

---

## 🔧 Common Tasks

### Add a New Endpoint

```python
# In app/api/auth.py

@router.get("/new-endpoint")
def new_endpoint(current_user: User = Depends(get_current_user)):
    return {"user": current_user.email}
```

### Add Role-Based Access

```python
# In app/api/auth.py

@router.post("/student-only")
def student_only(current_user: User = Depends(get_student_user)):
    return {"message": "Student access only"}
```

### Access Database

```python
from sqlalchemy.orm import Session
from app.db.session import get_db

@router.get("/example")
def example(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return users
```

### Hash Password

```python
from app.core.security import hash_password, verify_password

hashed = hash_password("mypassword")
is_valid = verify_password("mypassword", hashed)
```

### Create JWT Token

```python
from app.core.security import create_access_token

token = create_access_token({"sub": "user_id", "email": "user@test.com"})
```

---

## 🐛 Debug Mode

```bash
# Set DEBUG=True in .env
DEBUG=True

# Run with reload
uvicorn app.main:app --reload

# View logs in terminal
```

---

## 🧪 Test Endpoints

### Python Script
```bash
python test_api.py
```

### Swagger UI
```
http://localhost:8000/docs
```

### ReDoc
```
http://localhost:8000/redoc
```

---

## ✅ Pre-Deployment Checklist

- [ ] Change SECRET_KEY
- [ ] Set DATABASE_URL
- [ ] Set GOOGLE_CLIENT_ID
- [ ] Set GOOGLE_CLIENT_SECRET
- [ ] Set GOOGLE_REDIRECT_URI
- [ ] Set DEBUG=False
- [ ] Test all endpoints
- [ ] Test error cases
- [ ] Setup HTTPS

---

## 📝 Key Concepts

### User Roles
- **STUDENT**: Student account
- **PARENT**: Parent account

### Authentication Methods
- Email + Password
- Google OAuth

### JWT
- Format: `Bearer token`
- Expiration: Configurable
- Algorithm: HS256

### Password
- Min 8 characters
- Bcrypt hashed
- Never stored as plaintext

---

## 🚨 Common Errors

### 1. "Invalid credentials"
→ Check email and password are correct

### 2. "Email already registered"
→ Try different email or login instead

### 3. "Invalid or expired token"
→ Generate new token via login

### 4. "Database connection failed"
→ Check DATABASE_URL and PostgreSQL running

### 5. "Invalid Google token"
→ Check GOOGLE_CLIENT_ID and REDIRECT_URI

---

## 📊 Database Queries

### Find User
```python
user = db.query(User).filter(User.email == "test@example.com").first()
```

### Get Student Info
```python
student = db.query(Student).filter(Student.user_id == user_id).first()
```

### List All Users
```python
users = db.query(User).all()
```

### Count by Role
```python
count = db.query(User).filter(User.role == "STUDENT").count()
```

---

## 🔐 Security Tips

- ✅ Never commit .env files
- ✅ Use strong SECRET_KEY (32+ chars)
- ✅ Use HTTPS in production
- ✅ Keep dependencies updated
- ✅ Use environment-specific configs
- ✅ Log security events
- ✅ Rate limit endpoints
- ✅ Validate all input

---

## 📱 Mobile Integration

### Get OAuth Token
1. Get authorization code from Google
2. Exchange for ID token
3. Send token to: `POST /auth/google/login`
4. Get JWT back

### Use JWT
```
Authorization: Bearer eyJhbGc...
```

---

## 🌐 CORS Configuration

In `app/main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 📚 File Reference

- **Main App**: `app/main.py`
- **Setup**: `SETUP.md`
- **Schema**: `DATABASE_SCHEMA.md`
- **Examples**: `ADVANCED_EXAMPLES.md`
- **Docker**: `DOCKER.md`
- **Project Info**: `PROJECT_SUMMARY.md`

---

## 🎯 Next Steps

1. ✅ Follow SETUP.md for installation
2. ✅ Test with Swagger UI
3. ✅ Integrate with frontend
4. ✅ Setup database backups
5. ✅ Configure monitoring
6. ✅ Deploy to production

---

**Need Help?**
- Check SETUP.md for installation issues
- Check DATABASE_SCHEMA.md for schema questions
- Check ADVANCED_EXAMPLES.md for code patterns
- Review code comments
- Check error messages in logs

**Status**: Production Ready ✅
