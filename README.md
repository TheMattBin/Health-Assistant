# AI Health Assistant

A modern, scalable AI Health Assistant application featuring a Python FastAPI backend and Next.js/TypeScript frontend. The application provides medical AI chat functionality using Hugging Face's MedGemma model with robust file upload capabilities and JWT authentication.

## Features
- **AI Medical Chat**: Interactive chat with MedGemma-4b model for medical queries
- **File Upload Support**: Upload and analyze medical documents (PDFs, images)
- **Persistent Chat History**: Organized sessions with image storage and retrieval
- **Scalable File Storage**: User-specific upload directory with automatic cleanup
- **Secure Authentication**: JWT-based authentication system
- **Real-time Processing**: Vision-language model integration for image analysis
- **Modern UI**: Responsive Next.js interface with real-time chat updates

## Architecture
```
┌─────────────────┐    HTTP/WebSocket    ┌─────────────────┐
│   Next.js       │ ◄──────────────────► │   FastAPI       │
│   Frontend      │                      │   Backend       │
│                 │                      │                 │
│ - Chat UI       │                      │ - Auth Service  │
│ - File Upload   │                      │ - Chat Logic    │
│ - Session Mgmt  │                      │ - File Storage  │
└─────────────────┘                      │ - Model API     │
                                         └─────────────────┘
                                                │
                                                ▼
                                     ┌─────────────────┐
                                     │  Hugging Face   │
                                     │  MedGemma-4b    │
                                     │  (VLM Model)    │
                                     └─────────────────┘

File Storage Structure:
uploads/
└── users/
    └── {user_id}/
        ├── {timestamp}_{uuid}.jpg
        ├── {timestamp}_{uuid}.pdf
        └── ...

Chat Storage:
chat_history_db/
└── {user_id}.json
```

## Quickstart

### Prerequisites
- Docker & Docker Compose
- Node.js 18+ (for frontend dev)
- Python 3.10+ (for backend dev)
- Hugging Face API token (for MedGemma model)

### Environment Setup
1. **Create a `.env` file in `backend/`:**
   ```
   HF_TOKEN=your_hugging_face_token_here
   SECRET_KEY=your-secret-key-change-in-production
   ALGORITHM=HS256
   ```

2. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd Health-Assistant
   ```

### Running the Application

#### Option 1: Docker (Recommended)
```bash
docker-compose up --build
```

#### Option 2: Manual Development

**Backend:**
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

### Access Points
- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Documentation:** http://localhost:8000/docs

### Directory Structure
```
Health-Assistant/
├── backend/                    # FastAPI backend
│   ├── routers/               # API route modules
│   │   ├── auth.py           # Authentication endpoints
│   │   ├── chat.py           # Chat functionality
│   │   ├── chat_history.py   # Session management
│   │   ├── file_upload.py    # File handling
│   │   └── model_api.py      # AI model integration
│   ├── utils/                # Utility functions
│   │   └── file_storage.py   # File storage management
│   ├── uploads/              # User file storage
│   └── chat_history_db/      # Chat history storage
├── frontend/                  # Next.js frontend
│   ├── components/           # React components
│   │   ├── auth/            # Authentication components
│   │   └── chat/            # Chat interface components
│   ├── pages/               # Next.js pages
│   └── styles/              # CSS modules
├── docker-compose.yml
└── README.md
```

## Extending the System

### Adding New Features
- **New AI Models**: Add to `backend/routers/model_api.py`
- **File Types**: Update `backend/routers/file_upload.py`
- **UI Components**: Create in `frontend/components/`
- **Authentication**: Extend `backend/routers/auth.py`

### API Integration
- Database integration: Replace JSON storage in `chat_history.py`
- External APIs: Add new routers in `backend/routers/`
- Model providers: Extend `backend/routers/model_api.py`

## Future Enhancements

### 🚀 Performance & Scaling
- **Caching Layer**: Redis for chat sessions and frequent queries
- **Database Migration**: Move from JSON files to PostgreSQL/MongoDB
- **CDN Integration**: Global content delivery for uploaded files
- **Load Balancing**: Multi-instance backend deployment

### 🧠 AI & Intelligence
- **RAG (Retrieval-Augmented Generation)**:
  - Vector database integration (Pinecone, ChromaDB)
  - Medical document embedding and semantic search
  - Context-aware responses from user's medical history
- **Multi-Model Support**:
  - Switch between different medical AI models
  - Model selection based on query type
- **Fine-tuned Models**: Custom training on specific medical domains

### 🏥 Medical Features
- **Health Data Integration**:
  - EHR/EMR system connections
  - Wearable device data (Apple Health, Google Fit)
  - Lab results parsing and analysis
- **Clinical Decision Support**:
  - Drug interaction checking
  - Symptom analysis with differential diagnosis
  - Treatment recommendations
- **Medical Report Generation**:
  - Automated summary generation
  - Structured medical documentation
  - Insurance claim form assistance

### 🔒 Security & Compliance
- **HIPAA Compliance**: Enhanced security measures for healthcare data
- **Data Encryption**: End-to-end encryption for sensitive information
- **Audit Logging**: Complete activity tracking for compliance
- **Patient Privacy**: Advanced consent management features

### 🌐 Integration & Ecosystem
- **Telemedicine Platform**: Video call integration
- **Appointment Scheduling**: Calendar integration with healthcare providers
- **Pharmacy Integration**: Prescription management and ordering
- **Insurance Integration**: Claims processing and coverage verification

### 📱 Enhanced User Experience
- **Mobile Applications**: React Native/iOS/Android apps
- **Voice Interface**: Speech-to-text and text-to-speech capabilities
- **Real-time Notifications**: Appointment reminders, health alerts
- **Multi-language Support**: Global accessibility with translation

## Security & Privacy
- **Data Protection**: All health data encrypted at rest and in transit
- **User Control**: Complete control over data export and deletion
- **Privacy-first Design**: Local deployment supported for maximum privacy
- **Compliance Ready**: Framework for healthcare regulations (HIPAA, GDPR)

## License
Open source, MIT License.
