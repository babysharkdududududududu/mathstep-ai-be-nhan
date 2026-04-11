"""
Main FastAPI application.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import auth
from app.api import setup
from app.db.session import engine
from app.db.base import Base

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="MathStep AI - Authentication API",
    description="Production-ready authentication system with JWT and Google OAuth",
    version="1.0.0"
)

origins = [
    "https://mathstep-ai-fe-7z28.vercel.app",
    "http://localhost:3000",  # nếu dev local
]

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(auth.router)
app.include_router(
    setup.router,
    prefix="/setup",
    tags=["Setup"]
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
