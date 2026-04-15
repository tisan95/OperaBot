# OperaBot MVP - FEATURE-001 Setup & Running Guide

## 🎯 Overview

This guide covers setting up and running **OperaBot FEATURE-001** (User Authentication & Login System) locally on your MacBook Air.

**What's Implemented:**
- Backend: FastAPI + PostgreSQL + JWT authentication
- Frontend: Next.js + React + TypeScript + Tailwind CSS  
- Security: bcrypt passwords + HTTP-only cookies + multi-tenant support
- Testing: Unit + integration tests for auth service

**Setup time:** ~5-10 minutes  
**First test:** ~10 minutes after setup

---

## 📋 Prerequisites Check

Before you start, verify you have:

```bash
# PostgreSQL
psql --version
# Output should be: psql (PostgreSQL) 13+ or higher

# Python
python3 --version
# Output should be: Python 3.11+ or higher

# Node.js & npm
node --version && npm --version
# Output should be: v18+ and 9+
```

If any are missing, install via Homebrew:
```bash
brew install postgresql@15 python@3.11 node
```

---

## 🗄️ Step 1: Database Setup (PostgreSQL)

### 1.1 Ensure PostgreSQL is Running

```bash
# Check if running
brew services list | grep postgresql

# Start PostgreSQL
brew services start postgresql@15

# Verify it's running
psql -c "SELECT version();"
```

### 1.2 Create Development Database

```bash
# Create database
createdb operabot_dev

# Verify creation
psql -l | grep operabot_dev

# You should see:
#  operabot_dev | postgres | UTF8 | C | C |
```

### 1.3 Test Database Connection

```bash
# Connect and verify
psql -d operabot_dev -c "SELECT 1;"

# Output: 
#  ?column? 
# ----------
#        1
```

**If connection fails:**
- Check PostgreSQL is running: `brew services list`
- Check database was created: `psql -l`
- Check connection string format in backend/.env

---

## 🔧 Step 2: Backend Setup (FastAPI)

### 2.1 Navigate to Backend Directory

```bash
cd /path/to/OperaBot/backend

# Verify you're in the right place
ls -la | grep requirements.txt
```

### 2.2 Create Virtual Environment

```bash
# Create venv
python3 -m venv venv

# Activate it
source venv/bin/activate

# You should see (venv) in your terminal prompt
# Verify activation
which python
# Should output: /path/to/OperaBot/backend/venv/bin/python
```

### 2.3 Install Python Dependencies

```bash
# Upgrade pip (recommended)
pip install --upgrade pip

# Install all dependencies
pip install -r requirements.txt

# Verify key packages
python -c "import fastapi, sqlalchemy, pydantic; print('✅ All dependencies installed')"
```

**Dependencies installed:**
- FastAPI (web framework)
- SQLAlchemy (ORM)
- psycopg2 (PostgreSQL adapter)
- PyJWT (JWT tokens)
- bcrypt (password hashing)
- pytest (testing)

### 2.4 Configure Environment File

```bash
# Copy example env file
cp .env.example .env

# Check .env contains:
cat .env

# Expected:
# DATABASE_URL=postgresql://localhost:5432/operabot_dev
# SECRET_KEY=your-secret-key-change-in-production
# DEBUG=True
```

### 2.5 Verify Database Connection

```bash
# Test connection from Python
python -c "from app.db.database import engine; print('✅ Database connected successfully')"
```

If this fails, check:
- PostgreSQL is running: `brew services list`
- Database exists: `psql -l | grep operabot_dev`
- Connection string in `.env`: `DATABASE_URL=postgresql://localhost:5432/operabot_dev`

### 2.6 Start Backend Server

```bash
# Make sure venv is activated (you should see (venv) in prompt)
source venv/bin/activate

# Start uvicorn server
uvicorn app.main:app --reload --port 8000
```

**Expected output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete
```

**Do NOT close this terminal!** Backend should stay running.

**Verify backend is working:**
```bash
# In ANOTHER terminal
curl http://localhost:8000/health

# Expected response:
# {"status":"ok"}
```

---

## 🎨 Step 3: Frontend Setup (Next.js)

### 3.1 Navigate to Frontend Directory

```bash
cd /path/to/OperaBot/frontend

# Verify you're in the right place
ls -la | grep package.json
```

### 3.2 Install Dependencies

```bash
npm install

# This will take 2-3 minutes (downloads packages)
# You'll see progress output
```

**Alternatively with yarn:**
```bash
yarn install
```

### 3.3 Configure Environment File

```bash
# Copy example env file
cp .env.example .env.local

# Check .env.local contains:
cat .env.local

# Expected:
# NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 3.4 Start Frontend Server

```bash
# Start Next.js dev server
npm run dev

# OR with yarn
yarn dev
```

**Expected output:**
```
  ▲ Next.js 14.1.0
  - Local:        http://localhost:3000
  - Environments: .env.local
```

**Do NOT close this terminal!** Frontend should stay running.

---

## ✅ Step 4: Verify Everything Works

### 4.1 Check Both Services Running

In a third terminal, verify both are accessible:

```bash
# Backend health check
curl http://localhost:8000/health
# Expected: {"status":"ok"}

# Frontend check
curl -s http://localhost:3000 | head -20
# Expected: HTML output with Next.js content
```

### 4.2 Open Login Page

1. Open browser: **http://localhost:3000**
2. You should see:
   - OperaBot logo
   - "Login to your account"
   - Email and password fields
   - "Create an account" link

---

## 🧪 Step 5: Test the Complete Flow

### 5.1 Test User Registration

1. Click **"Create an account"** link
2. Fill in the registration form:
   - **Company Name:** `Test Company`
   - **Email:** `user@example.com`
   - **Password:** `SecurePass123!`
   - **Confirm Password:** `SecurePass123!`
3. Click **"Create Account"** button
4. **Expected:** Automatic redirect to dashboard with:
   - Welcome message: "Welcome, user@example.com!"
   - Company name: "Company: Test Company"
   - "Admin Panel" link (first user is admin)
   - "Logout" button

### 5.2 Test Dashboard

1. You're now on the dashboard page
2. Verify:
   - Welcome message displays correctly
   - Company name shown
   - Admin Panel link visible (this user is admin)
   - Logout button is clickable

### 5.3 Test Logout

1. Click **"Logout"** button
2. **Expected:** Redirect back to login page

### 5.4 Test Login

1. On login page, enter:
   - **Email:** `user@example.com`
   - **Password:** `SecurePass123!`
2. Click **"Login"** button
3. **Expected:** Redirect to dashboard (same as registration)

### 5.5 Test Error Cases

1. Try login with wrong password:
   - Email: `user@example.com`
   - Password: `WrongPassword`
   - **Expected:** Error message: "Invalid email or password"

2. Try login with non-existent email:
   - Email: `nonexistent@example.com`
   - Password: `SecurePass123!`
   - **Expected:** Error message: "Invalid email or password"

3. Try register with weak password:
   - Password: `short`
   - **Expected:** Error message: "Password must be at least 8 characters"

### 5.6 Test Multi-Tenancy (Advanced)

1. Register a second company:
   - Company: `Another Company`
   - Email: `user2@example.com` (different email)
   - Password: `AnotherPass123!`
2. Login with `user2@example.com`
3. Verify dashboard shows: "Company: Another Company"
4. Logout, login with `user@example.com`
5. Verify dashboard shows: "Company: Test Company"
6. **This proves multi-tenant isolation works!**

---

## 🧪 Step 6: Run Unit Tests (Optional)

### 6.1 Run Backend Tests

```bash
cd backend

# Make sure venv is activated
source venv/bin/activate

# Run all tests
pytest

# Expected output:
# tests/unit/test_auth_service.py::test_register_success PASSED       [ 10%]
# tests/unit/test_auth_service.py::test_register_invalid_email PASSED [ 20%]
# ...
# tests/integration/test_auth_flow.py::test_health_check PASSED       [ 95%]
# ======================== 15 passed in 0.45s ========================
```

### 6.2 View Test Coverage

```bash
pytest --cov=app --cov-report=html

# This creates htmlcov/index.html with coverage details
# Open in browser: open htmlcov/index.html
```

### 6.3 Run Specific Tests

```bash
# Just unit tests
pytest tests/unit/

# Just integration tests
pytest tests/integration/

# Just one test file
pytest tests/unit/test_auth_service.py

# Verbose output
pytest -v
```

---

## 📡 Step 7: API Testing (Optional)

### 7.1 Test with cURL

```bash
# Test registration
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email":"api-test@example.com",
    "password":"TestPass123!",
    "company_name":"API Test Company"
  }'

# Expected response:
# {"access_token":"eyJ0eXAi...","token_type":"bearer"}

# Test login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -c cookies.txt \
  -d '{
    "email":"api-test@example.com",
    "password":"TestPass123!",
    "company_name":"API Test Company"
  }'

# Test get current user
curl -X GET http://localhost:8000/auth/me \
  -b cookies.txt

# Test logout
curl -X POST http://localhost:8000/auth/logout \
  -b cookies.txt
```

### 7.2 Test with Postman

1. Create POST request to: `http://localhost:8000/auth/register`
2. Body (JSON):
```json
{
  "email": "postman@example.com",
  "password": "PostmanPass123!",
  "company_name": "Postman Test"
}
```
3. Send and view response

### 7.3 Interactive API Docs

1. Go to: **http://localhost:8000/docs**
2. You'll see Swagger UI with all endpoints
3. Click "Try it out" on any endpoint
4. Fill in parameters and click Execute

---

## 🗂️ Project File Structure

```
OperaBot/
├── backend/                          # FastAPI application
│   ├── app/
│   │   ├── main.py                  # App entry point, routes
│   │   ├── config.py                # Environment config
│   │   ├── middleware.py            # CORS middleware
│   │   │
│   │   ├── api/
│   │   │   ├── routes/
│   │   │   │   └── auth.py          # Auth endpoints (register, login, etc.)
│   │   │   ├── schemas/
│   │   │   │   └── auth.py          # Pydantic request/response models
│   │   │   └── dependencies.py      # JWT extraction, current_user
│   │   │
│   │   ├── services/
│   │   │   └── auth_service.py      # Auth business logic
│   │   │
│   │   ├── models/
│   │   │   ├── user.py              # User SQLAlchemy model
│   │   │   └── company.py           # Company SQLAlchemy model
│   │   │
│   │   ├── db/
│   │   │   ├── database.py          # SQLAlchemy engine, session
│   │   │   └── repositories/
│   │   │       └── user_repo.py     # User data access layer
│   │   │
│   │   └── utils/
│   │       ├── security.py          # JWT, bcrypt functions
│   │       └── logging.py           # Logging configuration
│   │
│   ├── tests/
│   │   ├── conftest.py              # Pytest fixtures
│   │   ├── unit/
│   │   │   └── test_auth_service.py # 8 unit tests
│   │   └── integration/
│   │       └── test_auth_flow.py    # 7 integration tests
│   │
│   ├── venv/                        # Virtual environment (created during setup)
│   ├── requirements.txt             # Python dependencies
│   ├── pyproject.toml              # Project config, pytest settings
│   ├── .env.example                # Example env variables
│   ├── .env                        # Actual env (you create this)
│   └── .gitignore
│
├── frontend/                        # Next.js application
│   ├── app/
│   │   ├── layout.tsx              # Root layout with AuthProvider
│   │   ├── page.tsx                # Login page (default route)
│   │   ├── register/
│   │   │   └── page.tsx            # Registration page
│   │   │
│   │   ├── (auth)/                 # Protected routes group
│   │   │   ├── layout.tsx          # Auth check wrapper
│   │   │   ├── dashboard/
│   │   │   │   ├── page.tsx        # User dashboard (welcome)
│   │   │   │   └── layout.tsx
│   │   │   │
│   │   │   └── admin/
│   │   │       ├── page.tsx        # Admin panel (role-gated)
│   │   │       └── layout.tsx
│   │   │
│   │   ├── api/
│   │   │   └── health/route.ts     # Health check endpoint
│   │   │
│   │   └── globals.css             # Tailwind + global styles
│   │
│   ├── components/
│   │   ├── Auth/
│   │   │   ├── AuthProvider.tsx    # Auth context provider
│   │   │   ├── LoginForm.tsx       # Login form
│   │   │   ├── RegisterForm.tsx    # Registration form
│   │   │   └── ProtectedRoute.tsx  # Route protection
│   │   │
│   │   └── Shared/
│   │       ├── Header.tsx          # Header with logout
│   │       ├── LoadingSpinner.tsx  # Loading indicator
│   │       └── Footer.tsx
│   │
│   ├── lib/
│   │   ├── api.ts                  # Fetch wrapper with cookies
│   │   ├── auth.ts                 # Auth utilities
│   │   ├── types.ts                # TypeScript interfaces
│   │   └── hooks/
│   │       └── useAuth.ts          # useAuth custom hook
│   │
│   ├── styles/
│   │   ├── globals.css             # Tailwind imports
│   │   └── theme.css               # CSS variables
│   │
│   ├── node_modules/               # Packages (after npm install)
│   ├── package.json                # Dependencies
│   ├── tsconfig.json               # TypeScript config
│   ├── tailwind.config.js          # Tailwind CSS config
│   ├── postcss.config.js           # PostCSS config
│   ├── next.config.js              # Next.js config
│   ├── .env.example                # Example env variables
│   ├── .env.local                  # Actual env (you create this)
│   └── .gitignore
│
├── _devprocess/                    # Development process docs
│   ├── context/
│   │   ├── 01_business-analysis.md # Business Analysis document
│   │   └── 02_requirements.md      # Feature specifications
│   │
│   └── architecture/
│       ├── decisions/
│       │   ├── ADR-001-backend-framework.md
│       │   ├── ADR-002-database-strategy.md
│       │   ├── ADR-003-vector-store.md
│       │   ├── ADR-004-llm-integration.md
│       │   ├── ADR-005-jwt-authentication.md
│       │   ├── ADR-006-frontend-framework.md
│       │   └── ADR-007-rag-pattern.md
│       │
│       ├── ARC42-architecture.md
│       ├── ARCHITECT-HANDOFF.md
│       └── PROJECT-STRUCTURE.md
│
├── docs/                           # Product documentation
│   ├── 00_vision.md
│   ├── 01_contexto_problema_mercado.md
│   ├── 02_personas_usuarios.md
│   ├── 03_solucion_operabot.md
│   ├── 04_mvp_arquitectura_alta_nivel.md
│   ├── 05_casos_uso_clave.md
│   ├── 06_roles_y_paneles.md
│   └── 07_principios_diseno_ux_ui.md
│
├── README.md
├── SETUP.md                        # This file
└── .gitignore
```

---

## 🐛 Troubleshooting

### Problem: PostgreSQL "could not connect to server"

**Cause:** PostgreSQL not running or database not created

**Solutions:**
```bash
# Check if PostgreSQL is running
brew services list | grep postgresql

# Start PostgreSQL
brew services start postgresql@15

# Verify database exists
psql -l | grep operabot_dev

# If missing, create it
createdb operabot_dev

# Test connection
psql -d operabot_dev -c "SELECT 1;"
```

### Problem: Backend Module "app not found"

**Cause:** Virtual environment not activated

**Solution:**
```bash
cd backend
source venv/bin/activate

# Verify (you should see (venv) in prompt)
which python
# Should show: .../backend/venv/bin/python
```

### Problem: Frontend "Port 3000 already in use"

**Cause:** Another process using port 3000

**Solutions:**
```bash
# Option 1: Find and stop the process
lsof -i :3000
# Then kill the PID shown

# Option 2: Use different port
npm run dev -- -p 3001

# Then access at http://localhost:3001
```

### Problem: Backend "Port 8000 already in use"

**Cause:** Another process using port 8000

**Solutions:**
```bash
# Option 1: Find and stop the process
lsof -i :8000
# Then kill the PID shown

# Option 2: Use different port
uvicorn app.main:app --reload --port 8001

# Then update frontend .env.local:
# NEXT_PUBLIC_API_URL=http://localhost:8001
```

### Problem: CORS Error in Browser

**Cause:** Frontend can't reach backend

**Symptoms:** Error in browser console like:
```
Access to XMLHttpRequest from origin 'http://localhost:3000'
has been blocked by CORS policy
```

**Solutions:**
1. Verify backend is running:
   ```bash
   curl http://localhost:8000/health
   ```

2. Check frontend .env.local:
   ```bash
   cat frontend/.env.local
   # Should show: NEXT_PUBLIC_API_URL=http://localhost:8000
   ```

3. Check backend CORS config in `backend/app/middleware.py`:
   - Should allow `http://localhost:3000`

### Problem: "No module named 'fastapi'" or "Cannot find psycopg2"

**Cause:** Dependencies not installed

**Solution:**
```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt --upgrade

# Verify
python -c "import fastapi, psycopg2; print('✅ OK')"
```

### Problem: Tests fail with "database not found"

**Cause:** Test database not available

**Solution:**
```bash
# Make sure operabot_dev exists
createdb operabot_dev

# Verify
psql -l | grep operabot_dev
```

### Problem: "Cannot import from app"

**Cause:** Running pytest from wrong directory

**Solution:**
```bash
cd backend
source venv/bin/activate
pytest  # NOT pytest from frontend directory
```

---

## 📊 Environment Variables Reference

### Backend (.env)

```bash
# PostgreSQL connection
DATABASE_URL=postgresql://localhost:5432/operabot_dev

# JWT secret (CHANGE IN PRODUCTION!)
SECRET_KEY=your-super-secret-key-change-this

# Environment mode
DEBUG=True  # Should be False in production

# CORS allowed origins (for frontend)
CORS_ORIGINS=["http://localhost:3000"]

# Optional: Password validation
MIN_PASSWORD_LENGTH=8
```

### Frontend (.env.local)

```bash
# Backend API URL
NEXT_PUBLIC_API_URL=http://localhost:8000

# Optional: Debug mode
NEXT_PUBLIC_DEBUG=false
```

---

## ✅ Complete Verification Checklist

Before claiming setup is complete, verify ALL of these:

### Prerequisites
- [ ] PostgreSQL running: `brew services list | grep postgresql`
- [ ] Database created: `createdb operabot_dev`
- [ ] Python 3.11+: `python3 --version`
- [ ] Node 18+: `node --version`

### Backend
- [ ] Virtual environment created: `ls -la backend/venv`
- [ ] Virtual environment activated: `source venv/bin/activate`
- [ ] Dependencies installed: `pip list | grep fastapi`
- [ ] Database connection works: `python -c "from app.db.database import engine"`
- [ ] Backend running on 8000: `curl http://localhost:8000/health`
- [ ] Tests pass: `pytest` shows "15 passed"
- [ ] API docs available: `http://localhost:8000/docs`

### Frontend
- [ ] Node modules installed: `ls -la frontend/node_modules | head -10`
- [ ] Frontend running on 3000: Browser shows login page at `http://localhost:3000`
- [ ] No CORS errors: Check browser console (should be empty)
- [ ] API can be called from frontend

### End-to-End Testing
- [ ] Can register new user
- [ ] Registration redirect to dashboard works
- [ ] Dashboard displays welcome message
- [ ] Can logout
- [ ] Can login again with same credentials
- [ ] Login error for wrong password
- [ ] Multi-tenancy works (2 different companies isolated)

### Documentation
- [ ] Read: `_devprocess/context/01_business-analysis.md`
- [ ] Read: `_devprocess/context/02_requirements.md`
- [ ] Read: `_devprocess/architecture/ARCHITECT-HANDOFF.md`

✅ **If all boxes are checked, you're ready!**

---

## 🚀 Quick Reference Commands

```bash
# Start backend
cd backend && source venv/bin/activate && uvicorn app.main:app --reload

# Start frontend
cd frontend && npm run dev

# Run tests
cd backend && pytest

# Check health
curl http://localhost:8000/health

# View API docs
open http://localhost:8000/docs

# Frontend
open http://localhost:3000
```

---

## 🎯 Next Steps After FEATURE-001

Once you've verified FEATURE-001 works:

1. **Read requirements** for FEATURE-002 onwards
2. **Plan FEATURE-002:** User Panel Dashboard improvements
3. **Start with FAQ database** schema
4. **Implement FAQ CRUD endpoints**
5. **Then:** Chat interface, RAG, Admin analytics

See `_devprocess/context/02_requirements.md` for full feature roadmap.

---

## 📞 Getting Help

If you encounter issues:

1. **Check this Troubleshooting section** above
2. **Check error messages** in terminal output
3. **Run health checks:**
   ```bash
   # Backend health
   curl http://localhost:8000/health
   
   # Frontend check
   curl http://localhost:3000
   
   # Database check
   psql -d operabot_dev -c "SELECT 1;"
   ```
4. **Check logs** in browser console (F12) and terminal
5. **Try a fresh restart** - stop both services, stop PostgreSQL, start all again

---

**🎉 Ready to test FEATURE-001? Open http://localhost:3000 now!**
