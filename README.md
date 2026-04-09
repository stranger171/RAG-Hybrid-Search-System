# RAG Based Hybrid Search System - Student AI Chatbot

A sophisticated AI-powered chatbot system that combines Retrieval-Augmented Generation (RAG) with traditional SQL querying to provide intelligent responses about student data. The system leverages semantic search and hybrid querying capabilities for comprehensive information retrieval.

## 🎯 Features

- **Hybrid Search**: Combines vector-based semantic search with traditional SQL queries
- **Memory Management**: Maintains conversation history for context-aware responses
- **Real-time Chat**: Streamlit-based user interface for interactive conversations
- **RAG Integration**: Retrieves relevant documents before generating responses
- **Token Optimization**: Efficient handling of the LLM context windows

## 📋 How to Query/Ask Questions

The chatbot accepts natural language queries about student data. Examples:

**Information Retrieval:**
- "Tell me about student with ID 123"
- "What are the courses taken by Alice?"
- "Show me students from Computer Science"

**Aggregations and Analytics:**
- "How many students are in the Science department?"
- "What's the average GPA of engineering students?"

**Semantic Search:**
- "Find students with high performance"
- "Who are the top performing students?"

**Follow-ups:**
- Ask related questions and the system maintains context from previous messages
- Use "Clear Chat Memory" in the sidebar to start a fresh conversation

## 🛠️ Tech Stack

### Backend
- **Django** - Web framework
- **Django REST Framework** - RESTful API development
- **LangChain** - LLM orchestration framework
- **Ollama** - Local LLM inference engine
- **PostgreSQL + pgvector** - Database with vector extensions
- **sentence-transformers** - Embedding generation
- **python-dotenv** - Environment variable management

### Frontend
- **Streamlit** - Interactive web UI
- **Requests** - HTTP client library

### Data Processing
- **Pandas** - Data manipulation and analysis
- **dj-database-url** - Database URL parsing

## 📦 Installation

### Prerequisites
- Python 3.8+
- PostgreSQL with pgvector extension
- Ollama (for local LLM deployment)
- Git

### Setup Instructions

#### 1. Clone the Repository
```bash
git clone <repository-url>
cd hybrid-student-ai
```

#### 2. Create Virtual Environment
```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows:
.venv\Scripts\Activate.ps1
# On macOS/Linux:
source .venv/bin/activate
```

#### 3. Install Dependencies

#### Backend
```bash
cd backend
pip install -r requirment.txt
```

#### Frontend (Optional, if separate environment needed)
```bash
cd frontend
pip install streamlit requests
```

#### 4. Environment Configuration

Create a `.env` file in the project root directory:
```env
# Django Configuration
DJANGO_SECRET_KEY=your-secret-key-here
DJANGO_DEBUG=True

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/student_db

# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=mistral

# API Configuration
API_BASE_URL=http://127.0.0.1:8000
```

#### 5. Database Setup

```bash
cd backend

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Load sample data (optional)
python manage.py shell
# Inside Django shell:
# from django.core.management import call_command
# call_command('loaddata', 'students_data')
```

## 🚀 Running the Application

### Step 1: Start Ollama (if not already running)
```bash
ollama serve
```

### Step 2: Start Backend Server
```bash
cd backend
python manage.py runserver
```
Backend will run at: `http://127.0.0.1:8000`

### Step 3: Start Frontend (Streamlit)
```bash
cd frontend
streamlit run streamlit_app.py
```
Frontend will open at: `http://localhost:8501`

## 📁 Project Structure

```
hybrid-student-ai/
├── backend/
│   ├── manage.py
│   ├── requirment.txt
│   ├── config/
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   ├── apps/
│   │   ├── agents/
│   │   │   └── sql_agent.py
│   │   ├── api/
│   │   │   ├── urls.py
│   │   │   └── views.py
│   │   ├── memory/
│   │   │   └── chat_memory.py
│   │   └── students/
│   │       ├── models.py
│   │       ├── apps.py
│   │       └── migrations/
│   └── services/
│       ├── langchain_chain.py
│       ├── ollama_llm.py
│       ├── router.py
│       └── vector_store.py
├── frontend/
│   └── streamlit_app.py
├── data/
│   ├── data.csv
│   └── students_5000.csv
└── README.md
```

## 🔑 Key API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/chat/` | POST | Send a query and get AI response |
| `/memory-status/` | GET | Check current conversation memory |
| `/reset-session/` | POST | Clear chat memory and start fresh |

## 🧠 Architecture Overview

1. **Frontend (Streamlit)**: User interface for chat interactions
2. **Backend API (Django REST)**: Handles API requests and routing
3. **LangChain Agent**: Orchestrates SQL queries and LLM calls
4. **Vector Store**: Manages embeddings for semantic search
5. **Ollama LLM**: Generates responses locally
6. **PostgreSQL**: Stores student data and embeddings

## 🔧 Available Commands

### Backend Commands
```bash
cd backend

# Run development server
python manage.py runserver

# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Access Django shell
python manage.py shell

# Load data
python manage.py shell < load_data.py
```

### Frontend Commands
```bash
cd frontend

# Run Streamlit app
streamlit run streamlit_app.py

# Run with specific port
streamlit run streamlit_app.py --server.port 8502
```

## 📊 Loading Sample Data

The project includes sample datasets:
- `data/data.csv` - Initial dataset
- `data/students_5000.csv` - Large dataset with 5000 student records

Load data into database:
```bash
cd backend
python manage.py shell
>>> from apps.students.models import Student
>>> import pandas as pd
>>> df = pd.read_csv('../data/students_5000.csv')
>>> # Process and save to database
```

## 🛡️ Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `DJANGO_SECRET_KEY` | Django secret key for security | Auto-generated |
| `DJANGO_DEBUG` | Debug mode (True/False) | True |
| `DATABASE_URL` | PostgreSQL connection string | postgresql://user:pass@localhost/db |
| `OLLAMA_BASE_URL` | Ollama API endpoint | http://localhost:11434 |
| `OLLAMA_MODEL` | Model name to use | mistral |

## ⚠️ Important Notes

- Ensure PostgreSQL is running with pgvector extension installed
- Ollama must be running on http://localhost:11434 (default)
- Backend must be running before using the Streamlit frontend
- All chat history is stored in session memory - clear it to start fresh

## 🤝 Contributing

Feel free to submit issues and enhancement requests!

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📧 Support

For issues, questions, or suggestions, please open an issue in the repository.
