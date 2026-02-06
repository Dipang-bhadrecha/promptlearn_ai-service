# AI Memory System Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         Client Request                           │
│                    (Frontend/API Call)                          │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      FastAPI Routes                              │
│                  /ai/generate (POST)                             │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    AI Controller                                 │
│               (Route Handler Layer)                              │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                     AI Service                                   │
│            (Business Logic Layer)                                │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Memory Manager                              │  │
│  │         (Central Orchestrator)                           │  │
│  └────┬──────────────┬──────────────┬───────────────┬──────┘  │
│       │              │              │               │          │
│       ▼              ▼              ▼               ▼          │
│  ┌─────────┐  ┌──────────┐  ┌──────────┐  ┌─────────────┐    │
│  │ Memory  │  │ Context  │  │Summarizer│  │  Retriever  │    │
│  │  Store  │  │ Manager  │  │          │  │             │    │
│  └─────────┘  └──────────┘  └──────────┘  └─────────────┘    │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      LLM Client                                  │
│                  (Gemini 2.0 Flash)                             │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Response + Metadata                           │
│               (Back to Client)                                   │
└─────────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. Memory Manager (Orchestrator)
**Location**: `src/modules/ai/memory/memory_manager.py`

**Responsibilities**:
- Orchestrate all memory operations
- Coordinate STM, LTM, and summarization
- Build enriched context
- Manage conversation state

**Key Methods**:
```python
process_conversation()      # Main entry point
save_assistant_response()   # Save AI response
get_conversation_summary()  # Get summary
clear_conversation_memory() # Clear memory
```

### 2. Memory Store (Persistence)
**Location**: `src/modules/ai/memory/memory_store.py`

**Responsibilities**:
- Store conversation turns
- Persist summaries
- Manage conversation state
- Handle file I/O operations

**Storage Structure**:
```
data/memory/
├── conversations/
│   └── {user_id}/
│       └── {conversation_id}.json
├── summaries/
│   └── {user_id}/
│       └── {conversation_id}.json
└── embeddings/
    └── cache.json
```

**Key Methods**:
```python
save_turn()                 # Save message
get_conversation_history()  # Load history
save_summary()              # Save summary
get_conversation_state()    # Get state
```

### 3. Context Manager (Token Management)
**Location**: `src/modules/ai/memory/context_manager.py`

**Responsibilities**:
- Manage context window
- Count tokens
- Prioritize context elements
- Build optimal context

**Context Building Algorithm**:
```
1. Reserve space for system prompt (highest priority)
2. Add conversation summary (20% max)
3. Add relevant LTM memories (30% max)
4. Fill remaining space with recent STM (50%+)
```

**Key Methods**:
```python
count_tokens()          # Estimate tokens
should_consolidate()    # Check if summarization needed
build_context()         # Build optimal context
```

### 4. Summarizer (Consolidation)
**Location**: `src/modules/ai/memory/summarizer.py`

**Responsibilities**:
- Summarize long conversations
- Progressive summarization
- Extract key facts
- Compress context

**Summarization Triggers**:
- Conversation > 20 turns
- Context approaching token limit
- Manual trigger

**Key Methods**:
```python
summarize_conversation()    # Create summary
progressive_summarize()     # Update summary
extract_key_facts()         # Extract facts
```

### 5. Retriever (Semantic Search)
**Location**: `src/modules/ai/memory/retriever.py`

**Responsibilities**:
- Find relevant memories
- Semantic similarity search
- Embedding management
- Cache embeddings

**Retrieval Process**:
```
1. Get query embedding
2. Load all user conversations
3. Get embeddings for summaries
4. Calculate cosine similarity
5. Return top N matches
```

**Key Methods**:
```python
find_relevant_context()     # Find relevant memories
get_conversation_context()  # Get specific context
_get_embedding()            # Get embeddings
_cosine_similarity()        # Calculate similarity
```

## Data Flow

### Request Processing Flow

```
1. User Message Arrives
   ↓
2. Memory Manager.process_conversation()
   │
   ├─→ Check if consolidation needed
   │   └─→ Summarizer.summarize_conversation()
   │       └─→ Memory Store.save_summary()
   │
   ├─→ Retrieve relevant memories
   │   └─→ Retriever.find_relevant_context()
   │       ├─→ Get embeddings
   │       └─→ Calculate similarity
   │
   ├─→ Build optimal context
   │   └─→ Context Manager.build_context()
   │       ├─→ Add system prompt
   │       ├─→ Add summary
   │       ├─→ Add LTM memories
   │       └─→ Add recent STM
   │
   └─→ Save user message
       └─→ Memory Store.save_turn()
   ↓
3. Call LLM with enriched context
   ↓
4. Save assistant response
   └─→ Memory Store.save_turn()
   ↓
5. Return response + metadata
```

### Memory Lifecycle

```
┌──────────────────────────────────────────────────────┐
│              New Conversation                         │
│         (Turns 1-19: Pure STM)                       │
└────────────────────┬─────────────────────────────────┘
                     │
                     ▼
┌──────────────────────────────────────────────────────┐
│         Turn 20: Consolidation Triggered             │
│    • Summarize conversation                          │
│    • Save summary                                    │
│    • Update conversation state                       │
└────────────────────┬─────────────────────────────────┘
                     │
                     ▼
┌──────────────────────────────────────────────────────┐
│     Turns 21+: STM + LTM + Summary                   │
│    • Recent turns in context                         │
│    • Summary provides earlier context                │
│    • Relevant memories retrieved                     │
└────────────────────┬─────────────────────────────────┘
                     │
                     ▼
┌──────────────────────────────────────────────────────┐
│    Turn 40: Second Consolidation                     │
│    • Update summary with new turns                   │
│    • Progressive summarization                       │
└──────────────────────────────────────────────────────┘
```

## Token Budget Allocation

For a 3000 token context window:

```
┌─────────────────────────────────────────┐
│  System Prompt (~100 tokens)            │  3-5%
├─────────────────────────────────────────┤
│  Conversation Summary (~200 tokens)     │  ~7%
├─────────────────────────────────────────┤
│  LTM Memories (~300 tokens)             │  ~10%
├─────────────────────────────────────────┤
│  Recent STM (~2400 tokens)              │  ~80%
└─────────────────────────────────────────┘
```

## Memory Types

### Short-Term Memory (STM)
- **Scope**: Current conversation turns
- **Lifespan**: Until consolidation
- **Purpose**: Immediate context
- **Storage**: In context window

### Long-Term Memory (LTM)
- **Scope**: Summarized past conversations
- **Lifespan**: Persistent
- **Purpose**: Historical context
- **Storage**: JSON files + embeddings

### Working Memory
- **Scope**: Built for each request
- **Lifespan**: Single request
- **Purpose**: Optimal context for LLM
- **Storage**: Temporary (in-memory)

## Performance Characteristics

### Time Complexity
- Save turn: O(1)
- Load history: O(n) where n = turns
- Build context: O(m) where m = context items
- Semantic retrieval: O(k*d) where k = conversations, d = embedding dim

### Space Complexity
- Per conversation: ~5-10KB
- Per summary: ~1KB
- Embedding cache: ~5KB per query
- Total for 1000 conversations: ~50MB

### Latency Breakdown
```
Memory Manager processing:  ~100ms
├─ Load conversation state:  10ms
├─ Semantic retrieval:       50ms
│  ├─ Get embeddings:        30ms
│  └─ Similarity calc:       20ms
├─ Build context:            20ms
└─ Save turn:                10ms

LLM call:                   ~1000ms

Total:                      ~1100ms
```

## Scalability Considerations

### Current (File-Based)
- **Pros**: Simple, no dependencies
- **Cons**: Slow for many users
- **Limit**: ~1000 active conversations

### Production (Database)
- **Pros**: Fast, scalable
- **Cons**: More complex
- **Options**:
  - PostgreSQL + pgvector
  - Redis + RedisSearch
  - Pinecone/Weaviate

## Error Handling

```
┌─────────────────────────────────────────┐
│         Memory Manager                  │
│                                         │
│  try:                                   │
│    process_conversation()               │
│  except MemoryError:                    │
│    • Log error                          │
│    • Fallback to basic STM              │
│    • Return partial context             │
│  except StorageError:                   │
│    • Log error                          │
│    • Use in-memory fallback             │
│  except EmbeddingError:                 │
│    • Log error                          │
│    • Skip semantic retrieval            │
│    • Continue with STM only             │
└─────────────────────────────────────────┘
```

## Configuration

### Memory Manager
```python
max_context_tokens = 3000      # Total context limit
consolidation_threshold = 20   # Turns before summarization
max_ltm_memories = 3          # Max retrieved memories
```

### Context Manager
```python
avg_tokens_per_char = 0.3     # Token estimation
summary_max_ratio = 0.2       # 20% for summary
ltm_max_ratio = 0.3           # 30% for LTM
```

### Retriever
```python
embedding_model = "text-embedding-004"
embedding_dim = 768
cache_size = 1000
```

## Extension Points

### 1. Custom Memory Store
```python
class RedisMemoryStore(MemoryStore):
    def __init__(self, redis_url):
        self.redis = Redis(redis_url)

    async def save_turn(self, ...):
        # Implement Redis storage
        pass
```

### 2. Custom Retriever
```python
class VectorDBRetriever(MemoryRetriever):
    def __init__(self, pinecone_api_key):
        self.index = pinecone.Index(...)

    async def find_relevant_context(self, ...):
        # Use vector DB for retrieval
        pass
```

### 3. Custom Summarizer
```python
class HierarchicalSummarizer(Summarizer):
    async def summarize_conversation(self, ...):
        # Multi-level summarization
        pass
```

## Monitoring & Observability

### Key Metrics
- Memory operations per second
- Average context tokens used
- LTM retrieval hit rate
- Summarization frequency
- Storage usage

### Logging
```python
logger.info("Memory processed", extra={
    "user_id": user_id,
    "conversation_id": conversation_id,
    "stm_turns": len(history),
    "ltm_retrieved": len(memories),
    "has_summary": bool(summary),
    "total_tokens": tokens
})
```

## Testing Strategy

### Unit Tests
- Memory Store: File operations
- Context Manager: Token counting, context building
- Summarizer: Summary generation
- Retriever: Similarity calculations

### Integration Tests
- End-to-end conversation flow
- Memory consolidation
- Semantic retrieval accuracy

### Load Tests
- 1000 concurrent conversations
- Memory persistence under load
- Context building performance

---

**Last Updated**: 2024-02-06
**Version**: 2.0
**Status**: Production Ready
