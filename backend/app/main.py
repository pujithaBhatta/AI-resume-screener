"""
main.py - FastAPI Application Entry Point
==========================================
This is the heart of our backend. It:
1. Creates the FastAPI app
2. Configures CORS (allows our React frontend to call our API)
3. Registers all route handlers (auth, resumes, jobs, etc.)
4. Manages startup/shutdown events (connect/disconnect MongoDB)

HOW FASTAPI WORKS:
- You define functions decorated with @app.get(), @app.post(), etc.
- FastAPI automatically generates API docs at /docs (Swagger UI)
- FastAPI validates request/response data using Pydantic models
- Async functions (async def) run concurrently for better performance

RUN THIS FILE WITH:
    uvicorn app.main:app --reload --port 8000
    
    - app.main = the module path (app/main.py)
    - :app = the FastAPI() instance variable name
    - --reload = auto-restart when code changes (development only)
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from app.config import settings
from app.database import connect_to_mongo, close_mongo_connection

# Import all our route modules
from app.api import auth, resumes, jobs, screening, reports, analytics


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager — runs code on startup and shutdown.
    
    The code BEFORE 'yield' runs when the app starts.
    The code AFTER 'yield' runs when the app stops.
    
    This is the modern FastAPI way (replaces @app.on_event("startup")).
    """
    # --- STARTUP ---
    print(f"🚀 Starting {settings.app_name}...")
    
    # Connect to MongoDB
    await connect_to_mongo()
    
    # Create uploads directory if it doesn't exist
    os.makedirs(settings.upload_dir, exist_ok=True)
    print(f"📁 Upload directory ready: {settings.upload_dir}")
    
    yield  # App is now running and handling requests
    
    # --- SHUTDOWN ---
    print("🛑 Shutting down...")
    await close_mongo_connection()


# Create the FastAPI application
app = FastAPI(
    title=settings.app_name,
    description="AI-powered resume screening and candidate ranking system",
    version="1.0.0",
    docs_url="/docs",       # Swagger UI available at http://localhost:8000/docs
    redoc_url="/redoc",     # ReDoc UI available at http://localhost:8000/redoc
    lifespan=lifespan
)


# ============================================================
# CORS Configuration
# ============================================================
# CORS = Cross-Origin Resource Sharing
# Browsers block requests from one domain to another by default (security)
# We need to explicitly allow our React frontend (localhost:3000) to 
# call our FastAPI backend (localhost:8000)

allowed_origins = settings.allowed_origins.split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,      # Which domains can call our API
    allow_credentials=True,              # Allow cookies/auth headers
    allow_methods=["*"],                 # Allow GET, POST, PUT, DELETE, etc.
    allow_headers=["*"],                 # Allow all headers (including Authorization)
)


# ============================================================
# Serve Uploaded Files
# ============================================================
# This makes files in ./uploads accessible at /uploads/filename.pdf
# Useful for previewing uploaded resumes

if os.path.exists(settings.upload_dir):
    app.mount("/uploads", StaticFiles(directory=settings.upload_dir), name="uploads")


# ============================================================
# Register API Routes
# ============================================================
# Each router handles a group of related endpoints.
# prefix="/api/auth" means all auth routes start with /api/auth/...

app.include_router(auth.router,       prefix="/api/auth",      tags=["Authentication"])
app.include_router(jobs.router,       prefix="/api/jobs",       tags=["Jobs"])
app.include_router(resumes.router,    prefix="/api/resumes",    tags=["Resumes"])
app.include_router(screening.router,  prefix="/api/screening",  tags=["Screening"])
app.include_router(reports.router,    prefix="/api/reports",    tags=["Reports"])
app.include_router(analytics.router,  prefix="/api/analytics",  tags=["Analytics"])


# ============================================================
# Health Check Endpoint
# ============================================================

@app.get("/", tags=["Health"])
async def root():
    """Root endpoint — confirms the API is running."""
    return {
        "status": "running",
        "app": settings.app_name,
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint for monitoring and deployment verification."""
    return {"status": "healthy"}
