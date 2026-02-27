# Setup Guide

## Local Development (Without Docker)

### Prerequisites
- Python 3.10+
- PostgreSQL
- Redis Server (for Celery)

### Steps

1. **Virtual Environment Setup:**
```bash
python -m venv venv
venv\Scripts\activate  # Windows
# or
source venv/bin/activate  # macOS/Linux
```

2. **Install Dependencies:**
```bash
pip install -r requirements-dev.txt
```

3. **Database Configuration:**
Ensure PostgreSQL is running and you have created a database (e.g., `alocentra_db`). Edit the `.env` file to include your database URI, `SECRET_KEY`, and Email server details.

4. **Run Migrations:**
```bash
python manage.py makemigrations
python manage.py migrate
```

5. **Run Redis (Required for celery):**
Make sure a local Redis server is active at `redis://127.0.0.1:6379/1`.

6. **Start Django Server and Celery Worker:**
Wait, open two terminals!
Terminal 1 (Django):
```bash
python manage.py runserver
```

Terminal 2 (Celery):
```bash
celery -A alocentra worker -l info -P eventlet
```

7. **Initial Login:**
Navigate to `http://127.0.0.1:8000/`. The first user to register will automatically act as the COE and receive all super permissions. Registration will automatically close for everyone else once the first COE is registered. Other users must be invited via the Dashboard.
