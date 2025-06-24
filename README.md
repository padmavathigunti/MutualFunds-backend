# Mutual Fund Broker Backend Application (Django + DRF)

This is the backend application for a mutual fund brokerage system, built using Django, Django REST Framework, PostgreSQL, and JWT authentication. It integrates with RapidAPI to fetch mutual fund data and uses Celery + Redis for asynchronous task processing.

---

## Tech Stack
- Python 3.x
- Django 4.x
- Django REST Framework
- PostgreSQL
- Simple JWT
- Celery + Redis
- python-decouple
- RapidAPI integration
- Postman

---

## Backend Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/padmavathigunti/MutualFunds-backend
cd mutualfund_project

```

### 2. Create Virtual Environment & Activate

```bash
python -m venv env
env\Scripts\activate   # For Windows
source env/bin/activate   # For Ubuntu/macOS
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Setup PostgreSQL and Environment Variables

- Create a PostgreSQL database (e.g., `mutualfund_db`)
- Create a `.env` file in the root directory with the following content:

```env
DB_NAME=your_db_name
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=localhost

RAPIDAPI_KEY=your_rapidapi_key
RAPID_API_HOST=latest-mutual-fund-nav.p.rapidapi.com
```

### 5. Apply Migrations

```bash
Note: The project already includes initial migration files for all required database tables.
You do not need to run makemigrations. Just apply the migrations using the command below.

python manage.py migrate
```

### 6. Run Development Server

```bash
python manage.py runserver
```

---

## Redis Setup Instructions

### Option 1: Use Redis with WSL (Recommended for Windows 10/11)

#### 1. Install WSL

Open PowerShell as Administrator and run:

```bash
wsl --install
```

Restart your PC if prompted.

#### 2. Install Ubuntu from Microsoft Store

Open Microsoft Store → Search for "Ubuntu" → Install → Launch.

#### 3. Install Redis inside WSL

```bash
sudo apt update
sudo apt install redis
```

#### 4. Start Redis Server

```bash
redis-server
```

#### 5. In a New Terminal, Check Redis is Working

```bash
redis-cli ping
```

You should see:

```
PONG
```

---

### Option 2: Redis on Ubuntu

```bash
sudo apt update
sudo apt install redis-server
sudo systemctl start redis
sudo systemctl enable redis
redis-cli ping   # Output should be: PONG
```


---

## Celery Setup

### Celery Commands (OS Specific)

####  Ubuntu/macOS

```bash
celery -A mutualfund_project worker -l info
celery -A mutualfund_project beat -l info
```

####  Windows

```bash
celery -A mutualfund_project worker -l info --pool=solo
celery -A mutualfund_project beat -l info
```

> **Note:** The `--pool=solo` is mandatory for Windows due to multiprocessing limitations.

