# 🤖 AI Resume Screener

An intelligent Applicant Tracking System (ATS) that uses NLP and Machine Learning to screen resumes, rank candidates, and provide actionable insights.

---

## 📋 Table of Contents
1. [Project Overview](#overview)
2. [Tech Stack](#tech-stack)
3. [Folder Structure](#folder-structure)
4. [Database Schema](#database-schema)
5. [Installation](#installation)
6. [Running the Project](#running)
7. [API Reference](#api-reference)
8. [Deployment](#deployment)
9. [Testing](#testing)

---

## 📌 Project Overview <a name="overview"></a>

The AI Resume Screener automates candidate screening by:
- **Parsing** resumes (PDF/DOCX) to extract Name, Email, Phone, Skills, Education, Experience
- **Scoring** resumes using NLP (TF-IDF + BERT Sentence Transformers) against a job description
- **Ranking** candidates on a dashboard with visual analytics
- **Highlighting** missing skills and keywords for gap analysis
- **Generating** AI-powered resume summaries and interview recommendations

---

## 🛠️ Tech Stack <a name="tech-stack"></a>

| Layer         | Technology                                      |
|---------------|--------------------------------------------------|
| Frontend      | React.js 18, Tailwind CSS 3, Recharts           |
| Backend       | Python FastAPI, Uvicorn                          |
| Database      | MongoDB (via Motor async driver)                 |
| ML/NLP        | spaCy, NLTK, Scikit-learn, Sentence Transformers |
| Auth          | JWT (JSON Web Tokens)                            |
| PDF Export    | ReportLab                                        |
| Excel Export  | openpyxl                                         |
| Resume Parse  | PyMuPDF (fitz), python-docx                     |

---

## 📁 Folder Structure <a name="folder-structure"></a>

```
ai-resume-screener/
├── backend/
│   ├── app/
│   │   ├── api/              # FastAPI route handlers
│   │   │   ├── auth.py       # Login/logout endpoints
│   │   │   ├── resumes.py    # Upload & manage resumes
│   │   │   ├── jobs.py       # Job description endpoints
│   │   │   ├── screening.py  # ATS scoring endpoints
│   │   │   └── reports.py    # PDF/Excel export endpoints
│   │   ├── models/           # Database models (MongoDB schemas)
│   │   │   ├── user.py
│   │   │   ├── resume.py
│   │   │   └── job.py
│   │   ├── services/         # Business logic layer
│   │   │   ├── auth_service.py
│   │   │   ├── resume_service.py
│   │   │   └── report_service.py
│   │   ├── ml/               # Machine Learning modules
│   │   │   ├── parser.py     # Resume text extraction & NLP parsing
│   │   │   ├── scorer.py     # ATS scoring algorithm
│   │   │   └── summarizer.py # AI summary generation
│   │   ├── config.py         # App configuration & env vars
│   │   ├── database.py       # MongoDB connection
│   │   └── main.py           # FastAPI app entry point
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── components/       # Reusable React components
│   │   │   ├── auth/         # Login form
│   │   │   ├── dashboard/    # Charts, stats cards
│   │   │   ├── resume/       # Upload, list, detail views
│   │   │   └── layout/       # Navbar, sidebar
│   │   ├── pages/            # Full page views
│   │   ├── hooks/            # Custom React hooks
│   │   ├── utils/            # API client, helpers
│   │   └── App.jsx
│   ├── package.json
│   └── tailwind.config.js
├── docs/
│   └── architecture.md
├── sample-data/
│   ├── sample_resume_1.txt   # Sample resume text
│   ├── sample_resume_2.txt
│   └── sample_job_description.txt
├── scripts/
│   ├── seed_db.py            # Seed initial admin user
│   └── download_models.py    # Download NLP models
└── README.md
```

---

## 🗄️ Database Schema <a name="database-schema"></a>

### MongoDB Collections

#### `users` Collection
```json
{
  "_id": "ObjectId",
  "username": "admin",
  "email": "admin@company.com",
  "password_hash": "bcrypt_hash",
  "role": "admin",
  "created_at": "ISODate"
}
```

#### `jobs` Collection
```json
{
  "_id": "ObjectId",
  "title": "Senior Python Developer",
  "description": "Full job description text...",
  "required_skills": ["Python", "FastAPI", "Docker"],
  "experience_years": 3,
  "created_by": "user_id",
  "created_at": "ISODate"
}
```

#### `resumes` Collection
```json
{
  "_id": "ObjectId",
  "filename": "john_doe_resume.pdf",
  "raw_text": "Extracted resume text...",
  "parsed_data": {
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "+1-555-0100",
    "skills": ["Python", "React", "SQL"],
    "education": [
      { "degree": "B.Tech Computer Science", "institution": "MIT", "year": 2020 }
    ],
    "experience": [
      { "title": "Software Engineer", "company": "TechCorp", "duration": "2 years" }
    ],
    "total_experience_years": 2
  },
  "job_id": "ObjectId",
  "ats_score": 78.5,
  "skill_match": ["Python", "React"],
  "missing_skills": ["Docker", "Kubernetes"],
  "recommendation": "Selected",
  "summary": "AI-generated candidate summary...",
  "uploaded_at": "ISODate",
  "uploaded_by": "user_id"
}
```

---

## ⚙️ Installation <a name="installation"></a>

### Prerequisites
- Python 3.10+
- Node.js 18+
- MongoDB 6.0+ (local or Atlas)

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Download NLP models
python -m spacy download en_core_web_sm
python scripts/download_models.py

# Configure environment
cp .env.example .env
# Edit .env with your MongoDB URI and secret key

# Seed admin user
python scripts/seed_db.py
```

### Frontend Setup
```bash
cd frontend
npm install
cp .env.example .env.local
# Edit .env.local with your backend URL
```

---

## 🚀 Running the Project <a name="running"></a>

### Start Backend
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

### Start Frontend
```bash
cd frontend
npm start
# Opens at http://localhost:3000
```

### Default Admin Credentials
```
Username: admin
Password: admin@123
```

---

## 📡 API Reference <a name="api-reference"></a>

| Method | Endpoint                    | Description                    |
|--------|-----------------------------|--------------------------------|
| POST   | /api/auth/login             | Admin login, returns JWT       |
| POST   | /api/jobs                   | Create job description         |
| GET    | /api/jobs                   | List all jobs                  |
| POST   | /api/resumes/upload         | Upload resumes (multipart)     |
| GET    | /api/resumes                | List resumes with scores       |
| GET    | /api/resumes/{id}           | Get resume detail              |
| POST   | /api/screening/score        | Trigger ATS scoring            |
| GET    | /api/reports/pdf/{job_id}   | Download PDF report            |
| GET    | /api/reports/excel/{job_id} | Download Excel report          |
| GET    | /api/analytics/stats        | Dashboard statistics           |

---

## 🌐 Deployment <a name="deployment"></a>

### Docker Deployment
```bash
docker-compose up --build
```

### Manual Cloud Deployment (AWS/GCP/Azure)

**Backend (FastAPI):**
```bash
# On your server
pip install gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

**Frontend (React):**
```bash
npm run build
# Deploy the build/ folder to Netlify, Vercel, or serve via Nginx
```

**Nginx Config** (save to `/etc/nginx/sites-available/resume-screener`):
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        root /var/www/resume-screener/build;
        try_files $uri /index.html;
    }
    
    location /api {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## 🧪 Testing <a name="testing"></a>

```bash
# Backend tests
cd backend
pytest tests/ -v

# Test with sample data
python tests/test_parser.py
python tests/test_scorer.py
```

---

## 🔐 Security Notes
- Change the `SECRET_KEY` in `.env` before production
- Use HTTPS in production
- MongoDB credentials should never be committed to git
- Enable MongoDB Atlas IP whitelisting for production

---

## 📄 License
MIT License — free to use, modify, and distribute.
