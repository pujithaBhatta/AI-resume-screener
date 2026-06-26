# 🚀 AI Resume Screener — Step-by-Step Setup Guide
## (No Docker Required)

---

## ✅ What You Need to Install First

| Tool | Version | Download Link |
|------|---------|---------------|
| Python | 3.10 or higher | https://python.org/downloads |
| Node.js | 18 or higher | https://nodejs.org |
| MongoDB Community | 6.0+ | https://www.mongodb.com/try/download/community |

**How to check if already installed:**
```
python --version        # should say Python 3.10+
node --version          # should say v18+
mongod --version        # should say db version v6+
```

---

## 📁 Project Structure (No Docker)

```
ai-resume-screener/
├── backend/            ← Python FastAPI server
│   ├── app/            ← All backend code
│   ├── .env            ← Your config (MongoDB URL, secret key)
│   ├── requirements.txt
│   └── uploads/        ← Uploaded resume files saved here
├── frontend/           ← React.js app
│   ├── src/
│   └── package.json
├── scripts/
│   ├── seed_db.py      ← Creates admin user in MongoDB
│   └── download_models.py ← Downloads spaCy + NLTK models
├── sample-data/        ← Test resumes and job description
├── start_windows.bat   ← One-click start for Windows
└── start_mac_linux.sh  ← One-click start for Mac/Linux
```

---

## 🪟 Windows Setup

### Option A — One Click (Easiest)
1. Make sure MongoDB is running (search "MongoDB" in Start Menu → Start)
2. Double-click `start_windows.bat`
3. Wait ~5 minutes for first-time setup
4. Browser opens at http://localhost:3000 automatically

### Option B — Manual Step by Step

**Step 1: Start MongoDB**
```
# Open Services (Win+R → services.msc) and start "MongoDB"
# OR run: net start MongoDB
```

**Step 2: Backend setup**
```cmd
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm
python ..\scripts\download_models.py
python ..\scripts\seed_db.py
```

**Step 3: Start Backend**
```cmd
uvicorn app.main:app --reload --port 8000
```
Keep this window open. Visit http://localhost:8000/docs to confirm it works.

**Step 4: Frontend setup (new terminal)**
```cmd
cd frontend
npm install
npm start
```
Browser opens at http://localhost:3000

---

## 🍎 Mac / Linux Setup

### Option A — One Click
```bash
chmod +x start_mac_linux.sh
./start_mac_linux.sh
```

### Option B — Manual

**Step 1: Start MongoDB**
```bash
# Mac (with Homebrew):
brew services start mongodb-community

# Linux (Ubuntu/Debian):
sudo systemctl start mongod
```

**Step 2: Backend**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm
python ../scripts/download_models.py
python ../scripts/seed_db.py
uvicorn app.main:app --reload --port 8000
```

**Step 3: Frontend (new terminal)**
```bash
cd frontend
npm install
npm start
```

---

## 🔑 Default Login

```
URL:      http://localhost:3000
Username: admin
Password: admin@123
```

---

## 🧪 Testing with Sample Data

1. Login at http://localhost:3000
2. Go to **Job Descriptions** → Create New Job → paste content from `sample-data/sample_job_description.txt`
3. Go to **Upload Resumes** → select the job → upload `sample-data/sample_resume_1.txt` and `sample_resume_2.txt`
4. Go to **Dashboard** to see the ATS scores and rankings

---

## ⚠️ Common Problems & Fixes

| Problem | Fix |
|---------|-----|
| `ModuleNotFoundError` | Make sure venv is activated: `venv\Scripts\activate` (Windows) or `source venv/bin/activate` (Mac/Linux) |
| `Connection refused` on MongoDB | Start MongoDB service (see Step 1 above) |
| `spacy model not found` | Run: `python -m spacy download en_core_web_sm` |
| Port 8000 already in use | Change port: `uvicorn app.main:app --port 8001` and update frontend `.env` |
| Port 3000 already in use | React will ask to use 3001 — type `y` |
| `npm install` fails | Delete `node_modules` folder and try again |
| Slow first upload | Sentence Transformer model loads on first use (~30 seconds) |

---

## 🛑 How to Stop the App

- **Windows:** Close the two black terminal windows
- **Mac/Linux:** Press `Ctrl+C` in the terminal running `start_mac_linux.sh`

---

## 🔧 Configuration (.env file)

Edit `backend/.env` to change settings:
```
MONGODB_URL=mongodb://localhost:27017     # Change if MongoDB is on another host
DATABASE_NAME=resume_screener             # MongoDB database name
SECRET_KEY=change-this-in-production      # Change this for security!
ACCESS_TOKEN_EXPIRE_MINUTES=480           # Login session duration (8 hours)
MAX_FILE_SIZE_MB=10                       # Max resume file size
```

---

## 🏃 Running Tests

```bash
cd backend
source venv/bin/activate   # or venv\Scripts\activate on Windows
pytest tests/ -v
```
