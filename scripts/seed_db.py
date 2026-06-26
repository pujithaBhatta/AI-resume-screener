"""
scripts/seed_db.py - Database Seeder
======================================
Creates the initial admin user in MongoDB.
Run this ONCE after setting up the project:

    cd backend
    python ../scripts/seed_db.py

DEFAULT CREDENTIALS:
    Username: admin
    Password: admin@123
    
CHANGE THE PASSWORD after first login!
"""

import asyncio
import sys
import os

# Add backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext
from datetime import datetime

# Configuration
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "resume_screener")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def seed():
    print("🌱 Seeding database...")
    
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client[DATABASE_NAME]
    
    # Check if admin already exists
    existing = await db.users.find_one({"username": "admin"})
    
    if existing:
        print("ℹ️  Admin user already exists. Skipping.")
    else:
        admin_user = {
            "username": "admin",
            "email": "admin@company.com",
            "password_hash": pwd_context.hash("admin@123"),
            "role": "admin",
            "created_at": datetime.utcnow()
        }
        
        result = await db.users.insert_one(admin_user)
        print(f"✅ Admin user created (ID: {result.inserted_id})")
        print("   Username: admin")
        print("   Password: admin@123")
        print("   ⚠️  Change this password in production!")
    
    # Create sample job
    existing_job = await db.jobs.find_one({"title": "Senior Python Developer"})
    
    if not existing_job:
        sample_job = {
            "title": "Senior Python Developer",
            "description": """
We are looking for a Senior Python Developer to join our backend engineering team.

Requirements:
- 3+ years of Python development experience
- Strong experience with FastAPI or Django
- Proficiency in SQL and NoSQL databases (PostgreSQL, MongoDB)
- Experience with Docker and Kubernetes
- Knowledge of machine learning libraries (scikit-learn, TensorFlow)
- Experience with REST API design and development
- Familiarity with AWS or GCP cloud services
- Strong understanding of Git version control
- Experience with CI/CD pipelines

Nice to have:
- Experience with React.js for frontend development
- Knowledge of Redis for caching
- Familiarity with message queues (RabbitMQ, Kafka)

Responsibilities:
- Design and implement scalable backend services
- Write clean, maintainable Python code
- Collaborate with frontend developers and data scientists
- Participate in code reviews and technical discussions
- Mentor junior developers
            """.strip(),
            "required_skills": [
                "Python", "FastAPI", "Django", "Docker", "Kubernetes",
                "PostgreSQL", "MongoDB", "AWS", "Git", "REST API",
                "Scikit-Learn", "Redis"
            ],
            "experience_years": 3,
            "created_by": "system",
            "created_at": datetime.utcnow(),
            "resume_count": 0
        }
        
        result = await db.jobs.insert_one(sample_job)
        print(f"✅ Sample job created: 'Senior Python Developer' (ID: {result.inserted_id})")
    else:
        print("ℹ️  Sample job already exists. Skipping.")
    
    client.close()
    print("\n🎉 Database seeding complete!")
    print("   Start the backend: uvicorn app.main:app --reload --port 8000")


if __name__ == "__main__":
    asyncio.run(seed())
