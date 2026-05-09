# CareerCompass Backend

Django backend for CareerCompass (API, authentication, chatbot, tests, dashboard).

## Requirements
- Python 3.10+
- pip

## Quick start (recommended)
From the backend folder:

### Windows
```
run_backend.bat
```

### Mac/Linux
```
chmod +x run_backend.sh
./run_backend.sh
```

These scripts run migrations, seed the database, and start the server.

## Manual setup
1) Create a virtual environment and install dependencies
```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

2) Create your environment file
```
copy .env.example .env
```
Fill in values in `.env`.

3) Migrate and seed
```
python manage.py makemigrations
python manage.py migrate
python manage.py seed_courses
python manage.py seed_careers
```

4) Run the server
```
python manage.py runserver
```

## Environment variables
See `.env.example` for the full list. Required values depend on features used.

- `EMAIL_HOST_PASSWORD`
- `GOOGLE_CLIENT_ID`
- `GOOGLE_CLIENT_SECRET`
- `FRONTEND_URL`
- `OPENROUTER_API_KEY`
- `GROQ_API_KEY`
- `GEMINI_API_KEY`
- `GOOGLE_API_KEY` (fallback for Gemini)

## Notes
- Default database: SQLite (`db.sqlite3`).
- CORS is open in dev.
