# Deployment Guide

This project is now prepared for deployment with Docker and PostgreSQL.

The app has two deployable parts:

- **Backend:** FastAPI API
- **Frontend:** React/Vite static site served by Nginx

For production, use PostgreSQL instead of SQLite.

---

## Files Added for Deployment

```text
docker-compose.yml
.env.production.example
backend/Dockerfile
backend/.dockerignore
frontend/Dockerfile
frontend/.dockerignore
frontend/nginx.conf
deployment/README.md
```

---

## Option 1: Run with Docker Compose Locally

From the project root, run:

```powershell
docker compose up --build
```

This starts:

```text
PostgreSQL: localhost:5432
Backend:    http://localhost:8000
Frontend:   http://localhost:8080
```

Open:

```text
http://localhost:8080
```

Backend Swagger docs:

```text
http://localhost:8000/docs
```

Admin login:

```text
Username: admin
Password: Admin123!
```

For real deployment, change the admin password and secret key.

---

## Option 2: Deploy Backend and Frontend Separately

A common deployment setup is:

```text
Backend:  Render, Railway, Fly.io, Azure, AWS, or any Docker host
Database: PostgreSQL
Frontend: Vercel, Netlify, Render Static Site, or Nginx Docker container
```

### Backend Build Command

If deploying without Docker:

```bash
pip install -r requirements.txt
```

### Backend Start Command

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

If your platform does not provide `$PORT`, use:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Frontend Build Command

```bash
npm install
npm run build
```

### Frontend Output Directory

```text
dist
```

---

## Required Backend Environment Variables

```env
DATABASE_URL=postgresql://user:password@host:5432/database_name
CORS_ORIGINS=https://your-frontend-domain.com
ADMIN_USERNAME=admin
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=replace-with-a-strong-admin-password
ADMIN_SECRET_KEY=replace-with-a-long-random-secret-key
ADMIN_ACCESS_TOKEN_EXPIRE_MINUTES=120
```

---

## Required Frontend Environment Variable

```env
VITE_API_BASE_URL=https://your-backend-domain.com
```

This must be set before building the frontend because Vite uses this value at build time.

---

## Production Checklist

Before deploying publicly:

- Replace `ADMIN_PASSWORD` with a strong password.
- Replace `ADMIN_SECRET_KEY` with a long random secret.
- Use PostgreSQL for `DATABASE_URL`.
- Set `CORS_ORIGINS` to your real frontend URL.
- Set `VITE_API_BASE_URL` to your real backend URL.
- Run backend tests.
- Run frontend lint and build checks.
- Do not commit `.env` files.
- Do not commit local SQLite database files.

---

## Test Before Deployment

Backend:

```powershell
cd backend
.venv\Scripts\activate
pytest
```

Frontend:

```powershell
cd frontend
npm run lint
npm run build
```

Docker:

```powershell
docker compose up --build
```

---

## Notes About the Database

The project still supports SQLite for local development.

For production, PostgreSQL is recommended because it is safer for a hosted multi-user application.

The backend creates tables automatically on startup for this portfolio version. A future improvement would be to replace this lightweight approach with Alembic migrations.
