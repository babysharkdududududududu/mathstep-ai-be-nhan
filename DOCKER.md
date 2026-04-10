# MathStep AI - Authentication API with Docker

Quick setup using Docker Compose:

```bash
# 1. Start PostgreSQL database
docker-compose up -d

# 2. Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# or
source venv/bin/activate  # macOS/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create .env file
copy .env.example .env

# Update .env with:
DATABASE_URL=postgresql://mathstep_user:postgres_password@localhost:5432/mathstep_db

# 5. Run server
uvicorn app.main:app --reload

# 6. Build Docker image (optional)
docker build -t mathstep-auth:latest .

# 7. Run with Docker
docker run -p 8000:8000 \
  -e DATABASE_URL="postgresql://mathstep_user:postgres_password@postgres:5432/mathstep_db" \
  -e SECRET_KEY="your-secret-key" \
  --network host \
  mathstep-auth:latest
```

## Database

PostgreSQL is pre-configured in docker-compose.yml:
- Host: localhost
- Port: 5432
- Username: mathstep_user
- Password: postgres_password
- Database: mathstep_db
