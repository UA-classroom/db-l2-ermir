# Bokadirekt Clone - Backend API

FastAPI backend for a booking platform for beauty and health services.

## Tech Stack

- **FastAPI** - Modern Python web framework
- **PostgreSQL** - Database with UUID v7 support
- **Psycopg 3** - PostgreSQL adapter
- **Pydantic** - Data validation and settings
- **JWT** - Authentication
- **UV** - Fast Python package manager

## Project Structure

```
backend/
├── app/
│   ├── api/
│   │   ├── deps.py              # Dependency injection
│   │   └── v1/                  # API v1 routes
│   │       ├── admin.py         # Admin endpoints
│   │       ├── auth.py          # Authentication
│   │       ├── bookings.py      # Booking management
│   │       ├── businesses.py    # Business & locations
│   │       ├── employees.py     # Employee management
│   │       ├── orders.py        # Order processing
│   │       ├── products.py      # Product management
│   │       ├── reviews.py       # Review system
│   │       ├── services.py      # Service catalog
│   │       └── users.py         # User management
│   ├── models/                  # Pydantic models
│   ├── repositories/            # Database repositories
│   ├── services/                # Business logic
│   ├── config.py                # Configuration
│   ├── database.py              # Database connection
│   └── main.py                  # FastAPI app entry
├── sql/
│   └── schema.sql               # Database schema
├── scripts/
│   └── reset_db.py              # Database reset & seed
├── tests/                       # Tests
└── pyproject.toml               # Dependencies
```

## Setup

### 1. Install Dependencies

This project uses **UV** for Python package management:

```bash
# Install UV if you haven't already
# Windows (PowerShell):
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# macOS/Linux:
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync
```

### 2. Database Setup

Create a PostgreSQL database and configure environment variables:

```bash
# Create .env file
cp .env.example .env
```

Edit `.env`:

```env
DATABASE_URL=postgresql://username:password@localhost:5432/dbname
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 3. Initialize Database

```bash
# Run schema creation
psql -U username -d dbname -f sql/schema.sql

# Seed database with sample data
uv run python scripts/reset_db.py
```

## Start Server
```bash
uvicorn app.main:app --reload
```

**Options:**
- `--reload` - Auto-restart on code changes (dev only)
- `--host 0.0.0.0` - Allow external connections
- `--port 8000` - Custom port (default: 8000)

**Access:**
- API: http://localhost:8000
- Swagger docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Reset Database & Seed Data
```bash
python scripts/reset_db.py
```
