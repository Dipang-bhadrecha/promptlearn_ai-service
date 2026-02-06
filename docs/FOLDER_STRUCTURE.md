# Folder Structure - Complete Overview

## 📁 Directory Tree

```
promptlearn_ai-service/
│
├── 📄 Configuration Files
│   ├── .env                        # Environment variables (GOOGLE_API_KEY)
│   ├── .gitignore                  # Git ignore patterns
│   ├── requirements.txt            # Python dependencies
│   ├── Makefile                    # Development commands
│   ├── dockerfile                  # Docker configuration
│   └── LICENSE                     # License file
│
├── 📚 Documentation
│   ├── README.md                   # Main project README
│   ├── MEMORY_README.md            # Memory system overview
│   └── docs/
│       ├── MEMORY_SYSTEM.md        # Complete memory documentation
│       ├── QUICKSTART.md           # Quick start guide
│       ├── ARCHITECTURE.md         # System architecture
│       └── FOLDER_STRUCTURE.md     # This file
│
├── 🧪 Testing
│   └── test_memory_system.py       # Comprehensive test suite
│
├── 💾 Data Storage (Auto-created)
│   └── data/
│       └── memory/
│           ├── conversations/       # User conversation history
│           │   └── {user_id}/
│           │       └── {conversation_id}.json
│           ├── summaries/          # Conversation summaries
│           │   └── {user_id}/
│           │       └── {conversation_id}.json
│           └── embeddings/         # Embedding cache
│               └── cache.json
│
└── 💻 Source Code
    └── src/
        │
        ├── 🚀 Main Application
        │   ├── main.py             # FastAPI app entry point
        │   └── __init__.py
        │
        ├── ⚙️ Configuration
        │   └── config/
        │       └── settings.py      # App configuration
        │
        ├── 🗄️ Database
        │   └── db/
        │       ├── model.py         # Database models
        │       └── session.py       # Database session
        │
        ├── 🤝 Shared Utilities
        │   └── shared/
        │       ├── llm_client.py    # Gemini API client
        │       └── __init__.py
        │
        └── 📦 Modules
            └── modules/
                │
                ├── 🧠 AI Module (Core Intelligence)
                │   └── ai/
                │       │
                │       ├── 📝 Core AI Components
                │       │   ├── ai_routes.py         # API routes
                │       │   ├── ai_controller.py     # Request handlers
                │       │   ├── ai_service.py        # Business logic (with memory)
                │       │   ├── ai_schemas.py        # Pydantic models
                │       │   ├── context_builder.py   # Context building
                │       │   └── __init__.py
                │       │
                │       ├── 🧠 Memory System (Smart Brain)
                │       │   ├── memory/
                │       │   │   ├── memory_manager.py    # Central orchestrator
                │       │   │   ├── memory_store.py      # Persistence layer
                │       │   │   ├── context_manager.py   # Context window management
                │       │   │   ├── summarizer.py        # Conversation summarization
                │       │   │   ├── retriever.py         # Semantic retrieval
                │       │   │   └── __init__.py
                │       │   │
                │       │   ├── ai_memory.py         # Public memory API
                │       │   └── memory_routes.py     # Memory management endpoints
                │       │
                │       └── 🗃️ Repository Layer
                │           └── ai_repository.py     # Data access (future)
                │
                ├── 📚 Knowledge Module (Future - RAG)
                │   └── knowledge/
                │       └── (planned for RAG implementation)
                │
                └── 🔧 Logic Module (Future - Business Logic)
                    └── logic/
                        └── (planned for advanced logic)
```

## 📊 Component Hierarchy

```
┌─────────────────────────────────────────────────────┐
│                   FastAPI App                        │
│                    (main.py)                         │
└────────────────┬─────────────────┬──────────────────┘
                 │                 │
        ┌────────▼────────┐   ┌───▼──────────────┐
        │   AI Routes     │   │  Memory Routes   │
        │  /ai/generate   │   │ /ai/memory/*     │
        └────────┬────────┘   └───┬──────────────┘
                 │                │
        ┌────────▼────────┐   ┌───▼──────────────┐
        │  AI Controller  │   │  Memory API      │
        └────────┬────────┘   └───┬──────────────┘
                 │                │
        ┌────────▼────────────────▼──────────────┐
        │           AI Service                    │
        │      (Business Logic)                   │
        └────────────┬────────────────────────────┘
                     │
        ┌────────────▼────────────────────────────┐
        │        Memory Manager                    │
        │     (Central Orchestrator)               │
        └─┬─────────┬──────────┬─────────┬────────┘
          │         │          │         │
    ┌─────▼───┐ ┌──▼──────┐ ┌─▼──────┐ ┌▼────────┐
    │ Memory  │ │ Context │ │Summary │ │Retriever│
    │  Store  │ │ Manager │ │  -izer │ │         │
    └─────────┘ └─────────┘ └────────┘ └─────────┘
          │                      │           │
    ┌─────▼──────────────────────▼───────────▼─────┐
    │           Memory Storage                      │
    │    (data/memory/conversations/...)            │
    └──────────────────────────────────────────────┘
```

## 🎯 Request Flow

```
1. Client Request
   │
   ├─→ POST /ai/generate
   │   │
   │   ▼
   │   ai_routes.py::generate_route()
   │   │
   │   ▼
   │   ai_controller.py::generate()
   │   │
   │   ▼
   │   ai_service.py::generate_response()
   │   │
   │   ├─→ Memory Manager
   │   │   ├─→ Check consolidation
   │   │   ├─→ Retrieve LTM
   │   │   ├─→ Build context
   │   │   └─→ Save turn
   │   │
   │   ├─→ LLM Client
   │   │   └─→ Gemini API
   │   │
   │   └─→ Save response
   │
   └─→ POST /ai/memory/*
       │
       ▼
       memory_routes.py
       │
       ▼
       ai_memory.py
       │
       ▼
       Memory Manager
```

## 📦 Module Breakdown

### 1. **AI Module** (`src/modules/ai/`)
Core AI functionality with memory system

**Files:**
- `ai_routes.py`: API endpoints
- `ai_controller.py`: Request handling
- `ai_service.py`: Business logic with memory integration
- `ai_schemas.py`: Request/response models
- `context_builder.py`: Context building utilities
- `ai_memory.py`: Public memory API
- `memory_routes.py`: Memory management endpoints

### 2. **Memory System** (`src/modules/ai/memory/`)
Intelligent conversation memory

**Files:**
- `memory_manager.py`: Central orchestrator
- `memory_store.py`: File-based persistence
- `context_manager.py`: Token and context management
- `summarizer.py`: Conversation summarization
- `retriever.py`: Semantic memory retrieval

### 3. **Shared Utilities** (`src/shared/`)
Common utilities across modules

**Files:**
- `llm_client.py`: Gemini API client

### 4. **Configuration** (`src/config/`)
Application configuration

**Files:**
- `settings.py`: Settings and environment variables

### 5. **Database** (`src/db/`)
Database models and connections (future)

**Files:**
- `model.py`: Database models
- `session.py`: Database sessions

## 🗂️ File Purposes

### Core Files

| File | Purpose | Key Functions |
|------|---------|---------------|
| `main.py` | App entry point | FastAPI initialization, route registration |
| `ai_service.py` | Business logic | `generate_response()`, memory integration |
| `memory_manager.py` | Memory orchestration | `process_conversation()`, coordination |
| `memory_store.py` | Data persistence | `save_turn()`, `get_conversation_history()` |
| `context_manager.py` | Context management | `build_context()`, `count_tokens()` |
| `summarizer.py` | Summarization | `summarize_conversation()` |
| `retriever.py` | Semantic search | `find_relevant_context()` |
| `llm_client.py` | LLM communication | `call_llm()` |

### Configuration Files

| File | Purpose |
|------|---------|
| `.env` | Environment variables (API keys) |
| `requirements.txt` | Python dependencies |
| `Makefile` | Development commands (`make dev`) |
| `dockerfile` | Docker container setup |

### Documentation Files

| File | Purpose |
|------|---------|
| `MEMORY_README.md` | Memory system overview |
| `docs/MEMORY_SYSTEM.md` | Complete documentation |
| `docs/QUICKSTART.md` | Quick start guide |
| `docs/ARCHITECTURE.md` | Architecture details |
| `docs/FOLDER_STRUCTURE.md` | This file |

## 🚀 Getting Started

### 1. Environment Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment variables
echo "GOOGLE_API_KEY=your_key_here" > .env
```

### 2. Start Server
```bash
make dev
```

### 3. Test System
```bash
python test_memory_system.py
```

## 📝 File Naming Conventions

- **Routes**: `*_routes.py` - API endpoints
- **Controllers**: `*_controller.py` - Request handlers
- **Services**: `*_service.py` - Business logic
- **Schemas**: `*_schemas.py` - Data models
- **Memory**: `memory/*.py` - Memory system components
- **Tests**: `test_*.py` - Test files
- **Docs**: `*.md` - Documentation

## 🔄 Development Workflow

```
1. User Request → main.py
2. Route Handler → ai_routes.py
3. Controller → ai_controller.py
4. Service Layer → ai_service.py
   ├─→ Memory Manager
   └─→ LLM Client
5. Response → Client
```

## 🎨 Design Principles

### Separation of Concerns
- **Routes**: HTTP handling
- **Controllers**: Request/response mapping
- **Services**: Business logic
- **Memory**: Context management
- **Store**: Data persistence

### Single Responsibility
Each module has one clear purpose:
- `memory_manager`: Orchestration
- `memory_store`: Persistence
- `context_manager`: Context logic
- `summarizer`: Summarization
- `retriever`: Retrieval

### Dependency Injection
Services depend on interfaces, not implementations:
```python
# Easy to swap storage backend
class MemoryManager:
    def __init__(self, store=MemoryStore()):
        self.store = store  # Can be JsonStore, RedisStore, etc.
```

## 🔮 Future Structure

```
src/modules/
├── ai/                     # Current
│   └── memory/
├── knowledge/              # Planned
│   ├── rag/
│   ├── vector_db/
│   └── documents/
├── logic/                  # Planned
│   ├── workflows/
│   └── rules/
└── analytics/              # Planned
    ├── metrics/
    └── monitoring/
```

## 📏 Code Organization Rules

1. **One module = One responsibility**
2. **Public API in `__init__.py`**
3. **Private helpers start with `_`**
4. **Async functions for I/O**
5. **Type hints for all functions**
6. **Docstrings for public methods**

## 🎓 Understanding the Structure

### For Backend Developers
- Routes → Controllers → Services (MVC pattern)
- Memory system is a service layer
- Storage is abstracted (easy to swap)

### For AI Engineers
- Memory Manager = Orchestrator
- Store = Long-term storage
- Context Manager = Working memory
- Retriever = Semantic search

### For DevOps
- `data/` directory needs persistence
- Environment variables in `.env`
- Health checks at `/ai/memory/health`
- Logs go to stdout (Docker-friendly)

---

**Last Updated**: 2024-02-06
**Version**: 2.0
