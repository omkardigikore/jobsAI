# config/asgi.py
import logging
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import jwt
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

from config.settings import (
    API_PREFIX,
    API_TITLE,
    API_DESCRIPTION,
    API_VERSION,
    CORS_ORIGINS,
    SECRET_KEY,
    JWT_ALGORITHM,
    JWT_EXPIRATION,
    ADMIN_USERNAME,
    ADMIN_PASSWORD
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=API_TITLE,
    description=API_DESCRIPTION,
    version=API_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Job Updates Bot API", "docs": "/docs"}

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}

# Authentication endpoint
@app.post("/auth/token")
async def login_for_access_token(username: str, password: str):
    """
    Get access token for API authentication
    
    Args:
        username: Admin username
        password: Admin password
        
    Returns:
        Access token
    """
    from utils.auth import create_access_token
    
    if username != ADMIN_USERNAME or password != ADMIN_PASSWORD:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=JWT_EXPIRATION)
    access_token = create_access_token(
        data={"sub": username, "is_admin": True},
        expires_delta=access_token_expires,
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"},
    )

# Include API routes after app is defined
from api.routes import users, subscriptions, payments, jobs, admin

# Include API routes
app.include_router(users.router, prefix=f"{API_PREFIX}/users", tags=["Users"])
app.include_router(subscriptions.router, prefix=f"{API_PREFIX}/subscriptions", tags=["Subscriptions"])
app.include_router(payments.router, prefix=f"{API_PREFIX}/payments", tags=["Payments"])
app.include_router(jobs.router, prefix=f"{API_PREFIX}/jobs", tags=["Jobs"])
app.include_router(admin.router, prefix=f"{API_PREFIX}/admin", tags=["Admin"])

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run("config.asgi:app", host="0.0.0.0", port=8000, reload=True)