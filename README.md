# OpenHealth-Inspired AI Health Assistant

This project is a modular, privacy-focused AI Health Assistant inspired by OpenHealth, featuring a Python FastAPI backend, a TypeScript React/Next.js frontend, and integration with open-source medical LLMs from Hugging Face.

## Features
- Centralized health data entry (upload PDFs, CSVs, images)
- Automated data parsing and normalization
- Personalized AI chat using user health data
- Secure authentication (OAuth2/JWT)
- Data privacy and user control (export/delete)
- Extensible backend for new data sources/models

## Architecture
```
[User Browser]
      |
      v
[TypeScript Frontend]
      |
      v
[Python FastAPI Backend]
 |         |         |
 v         v         v
[Database][Model API][File Parsing]
      |
      v
[Hugging Face Model (local/cloud)]
```

## Quickstart

### Prerequisites
- Docker & Docker Compose
- Node.js (for frontend dev)
- Python 3.10+ (for backend dev)

### Local Development

1. **Clone the repo**
2. **Start all services:**
   ```sh
   docker-compose up --build
   ```
3. **Access frontend:** http://localhost:3000
4. **Access backend API docs:** http://localhost:8000/docs

### Directory Structure
```
Health-Assistant/
  backend/        # FastAPI backend
    routers/      # API route modules
  frontend/       # React/Next.js frontend
  docker-compose.yml
  README.md
```

## Extending the System
- Add new models in `backend/models/`
- Add new data parsers in `backend/parsers/`
- Add new UI features in `frontend/`

## Security & Privacy
- All health data is encrypted at rest and in transit
- User controls for data export and deletion
- Local deployment supported for maximum privacy

## License
Open source, MIT License.
