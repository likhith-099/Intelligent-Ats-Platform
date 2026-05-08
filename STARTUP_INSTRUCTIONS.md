# ATS Platform Startup Instructions

## Project Structure
- `backend/` - Python FastAPI backend
- `ats-frontend/` - React frontend
- `requirements.txt` - Python dependencies
- `.env` - Environment variables

## Prerequisites
1. Python 3.9+ installed
2. Node.js 18+ installed (for frontend)
3. PostgreSQL database (or update DATABASE_URL in .env)

## Backend Setup

### 1. Create and activate virtual environment
```bash
cd backend
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate
```

### 2. Install dependencies
```bash
pip install -r ../requirements.txt
```

### 3. Download spaCy model
```bash
python -m spacy download en_core_web_sm
```

### 4. Set up environment variables
Ensure `.env` file exists in the root directory with:
```
DATABASE_URL=postgresql://postgres:password@localhost:5432/resume_ai
SECRET_KEY=supersecretkey123
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:4173
```

### 5. Start the backend server
```bash
# IMPORTANT: Run from the ROOT directory (d:/resume_ai), NOT from backend directory

# Option 1: Using the batch file from root (Windows)
start_backend.bat

# Option 2: Using Python module syntax from root directory
cd /d d:\resume_ai
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload

# Option 3: If you're in the backend directory, go up one level first
cd ..
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

The backend will be available at `http://localhost:8000`

## Frontend Setup

### 1. Navigate to frontend directory
```bash
cd ats-frontend
```

### 2. Install dependencies
```bash
npm install
```

### 3. Start the development server
```bash
npm run dev
```

The frontend will be available at `http://localhost:5173`

## Database Setup

### 1. Create PostgreSQL database
```sql
CREATE DATABASE resume_ai;
```

### 2. The application will automatically create tables on first run
Tables are created via SQLAlchemy's `Base.metadata.create_all()`

## Testing the Application

1. Open `http://localhost:5173` in your browser
2. Register as either a "recruiter" or "candidate"
3. Recruiters can create jobs and rank applicants
4. Candidates can upload resumes and apply to jobs

## API Documentation
Once the backend is running, visit:
- `http://localhost:8000/docs` - Swagger UI
- `http://localhost:8000/redoc` - ReDoc documentation

## Troubleshooting

### Common Issues

1. **Database connection errors**
   - Check DATABASE_URL in `.env` file
   - Ensure PostgreSQL is running

2. **CORS errors**
   - Check ALLOWED_ORIGINS in `.env` matches frontend URL
   - Default is `http://localhost:5173`

3. **Missing dependencies**
   - Run `pip install -r requirements.txt` again
   - For spaCy: `python -m spacy download en_core_web_sm`

4. **File upload errors**
   - Ensure `uploads/` directory exists in backend
   - Check file size (max 10MB)

## Production Deployment Notes

1. **Security**
   - Change SECRET_KEY to a strong random value
   - Use HTTPS in production
   - Set proper ALLOWED_ORIGINS for your domain

2. **Performance**
   - Use PostgreSQL connection pooling
   - Consider Redis for rate limiting in production
   - Implement proper file storage (S3, etc.)

3. **Monitoring**
   - Check `logs/` directory for application logs
   - Enable proper error tracking

## Updated Features (After Code Review Fixes)

✅ **Security Improvements**
- Password strength validation
- File upload security with UUIDs
- Rate limiting (60 requests/minute)
- Environment variable validation

✅ **Performance Improvements**
- Database indexes for faster queries
- Semantic chunking for better embeddings
- Structured JSON logging

✅ **Code Quality**
- Pydantic validation schemas
- Proper error handling
- Logging for key operations

✅ **Frontend Updates**
- Fixed API calls for job creation
- Improved error messages
- Loading states