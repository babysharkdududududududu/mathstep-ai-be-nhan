"""
Main FastAPI application.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import logging

from app.api import auth
from app.api import setup
from app.api import user_profile
from app.db.session import engine
from app.db.base import Base
# Import all models to ensure tables are created
from app.models import user, student, parent, password_reset

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="MathStep AI - Authentication API",
    description="Production-ready authentication system with JWT and Google OAuth",
    version="1.0.0"
)

# Define allowed origins
ALLOWED_ORIGINS = [
    "https://mathstep-ai-fe-7z28.vercel.app",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

# ✅ Add CORS middleware FIRST (before routes)
# This ensures ALL responses get CORS headers, including error responses
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
    max_age=3600,  # Cache preflight requests for 1 hour
)

# Global exception handler for validation errors
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    """Handle validation errors with proper CORS headers."""
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "message": "Validation error",
            "error_code": "VALIDATION_ERROR",
            "details": exc.errors(),
        },
    )

# Include routes
app.include_router(auth.router)
app.include_router(
    setup.router,
    prefix="/setup",
    tags=["Setup"]
)
app.include_router(
    user_profile.router,
    prefix="/profile",
    tags=["profile"]
)

@app.get("/")
def read_root():
    """Health check endpoint."""
    return {
        "message": "MathStep AI Authentication API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
def health_check():
    """Health check endpoint for monitoring."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
