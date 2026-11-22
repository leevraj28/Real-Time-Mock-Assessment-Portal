# MockExam Pro – Real-Time Mock Assessment Portal

A web platform for taking professional mock exams with real-time analytics, anti-cheating measures and AI-driven insights.

## Features

- Timed mock exams and assessments
- Real-time analytics and performance tracking
- Anti-cheating monitoring
- AI-driven insights on results
- Interactive API documentation (Swagger UI)
- Docker support for easy deployment

## Tech Stack

- **Backend:** Python, FastAPI
- **Database:** SQLite (`exam_portal.db`) with Alembic migrations
- **Containerization:** Docker, Docker Compose
- **Testing:** pytest

## Project Structure

```
├── app/                 # Application code (routes, models, services)
├── alembic/             # Database migration environment
├── migrations/          # Migration scripts
├── tests/               # Test suite
├── config.py            # App configuration
├── main.py              # Application entry point
├── run.py               # Script to start the server
├── seed.py              # Seeds the database with sample data
├── requirements.txt     # Python dependencies
├── Dockerfile
└── docker-compose.yml
```

## Getting Started

### Prerequisites

- Python 3.10 or newer
- Git
- (Optional) Docker Desktop

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/leevraj28/Real-Time-Mock-Assessment-Portal.git
cd Real-Time-Mock-Assessment-Portal

# 2. Create and activate a virtual environment
python -m venv venv
# Windows (PowerShell)
venv\Scripts\Activate.ps1
# macOS / Linux
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt
```

### Configuration

Create a `.env` file in the project root for any secrets or settings your app needs (database URL, secret key, API keys, etc.). This file is ignored by Git and must never be committed.

### Set Up the Database

```bash
# Apply migrations
alembic upgrade head

# (Optional) Load sample data
python seed.py
```

### Run the Application

```bash
python run.py
```

Or run it directly with Uvicorn:

```bash
uvicorn main:app --reload
```

Then open:

| Page | URL |
|------|-----|
| Application | http://127.0.0.1:8000 |
| API docs (Swagger) | http://127.0.0.1:8000/docs |

## Run with Docker

```bash
docker-compose up --build
```

The app will be available at http://127.0.0.1:8000.

## Running Tests

```bash
pytest
```

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -m "Add your feature"`
4. Push the branch: `git push origin feature/your-feature`
5. Open a Pull Request

## Author

**leevraj28** – [GitHub](https://github.com/leevraj28)

## License

Add a license of your choice (for example MIT) in a `LICENSE` file.
