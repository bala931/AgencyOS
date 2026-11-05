# AgencyOS

**An AI-powered agency workflow platform.**

AgencyOS helps businesses organize client requests, coordinate AI-assisted workflows, and review generated deliverables.

## Current Features

- Create, view, update, and delete client briefs.
- Store brief records in PostgreSQL.
- Validate brief titles and descriptions.
- Reject empty and whitespace-only input.
- Handle missing brief IDs with HTTP 404 responses.
- Automated API tests using pytest.

## Technology Stack

- **Backend:** Python, FastAPI
- **Database:** PostgreSQL
- **ORM:** SQLAlchemy
- **Validation:** Pydantic
- **Database Driver:** Psycopg
- **Testing:** Pytest, HTTPX
- **Version Control:** Git and GitHub

## Project Setup

### 1. Clone the repository

    git clone https://github.com/bala931/AgencyOS.git
    cd AgencyOS

### 2. Create a virtual environment

    python -m venv .venv
    .\.venv\Scripts\Activate.ps1

### 3. Install dependencies

    python -m pip install -r requirements.txt

### 4. Configure PostgreSQL

Create a PostgreSQL database named `agencyos`.

Create a `.env` file in the project root:

    DB_HOST=localhost
    DB_PORT=5432
    DB_NAME=agencyos
    DB_USER=postgres
    DB_PASSWORD=your_local_postgres_password

Replace the password placeholder with your local password. Never commit `.env` or expose database credentials.

### 5. Create database tables

    python create_tables.py

### 6. Start the API

    python -m uvicorn main:app --reload

- API: http://127.0.0.1:8000
- Interactive documentation: http://127.0.0.1:8000/docs

## API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/` | API welcome message |
| GET | `/health` | Health check |
| POST | `/briefs` | Create a brief |
| GET | `/briefs` | List all briefs |
| GET | `/briefs/{brief_id}` | Retrieve one brief |
| PUT | `/briefs/{brief_id}` | Update a brief |
| DELETE | `/briefs/{brief_id}` | Delete a brief |

## Testing

Run automated tests:

    python -m pytest -v

The current test suite contains 17 tests covering CRUD operations, input validation, and missing records.

Automated API tests use an isolated SQLite test database. PostgreSQL connectivity and CRUD operations have also been tested separately.

## Development Roadmap

- [x] Initialize the project and Git workflow.
- [x] Build the FastAPI backend.
- [x] Implement client brief CRUD APIs.
- [x] Integrate PostgreSQL persistence.
- [x] Add input validation and automated tests.
- [ ] Implement task management.
- [ ] Integrate AI-powered workflows.
- [ ] Add human review and approval.
- [ ] Build the React and TypeScript dashboard.
- [ ] Deploy the application.

## Engineering Principles

- Keep code maintainable and understandable.
- Test important functionality.
- Protect credentials and sensitive information.
- Document design decisions and limitations.
- Validate data before processing it.

---

**Development status:** Backend brief management and PostgreSQL persistence implemented. Further workflow features are in progress.