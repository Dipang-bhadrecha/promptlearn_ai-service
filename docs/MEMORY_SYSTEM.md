# AI Memory System Documentation

## Overview

The AI Memory System provides intelligent context management and conversation memory for the PromptLearn chatbot. It enables the AI to remember past conversations, retrieve relevant context, and provide more personalized responses.

## Features

### 1. **Short-Term Memory (STM)**
- Keeps recent conversation turns in active context
- Automatically manages token limits
- Prioritizes most recent messages

### 2. **Long-Term Memory (LTM)**
- Stores conversation summaries
- Enables retrieval of relevant past context
- Persists across sessions

### 3. **Context Window Management**
- Intelligent token counting
- Dynamic context building
- Automatic context prioritization

### 4. **Semantic Retrieval**
- Uses embeddings for semantic search
- Finds relevant past conversations
- Contextually aware memory retrieval

### 5. **Memory Consolidation**
- Automatic summarization of long conversations
- Progressive summarization
- Efficient memory usage

## Architecture

```
Memory System
├── memory_manager.py      # Main orchestrator
├── memory_store.py        # Persistent storage
├── context_manager.py     # Context window management
├── summarizer.py          # Conversation summarization
└── retriever.py           # Semantic memory retrieval
```

## How It Works

### Request Flow

```
1. User sends message
   ↓
2. Memory Manager processes request
   ↓
3. Check if consolidation needed
   ↓
4. Retrieve relevant memories (LTM)
   ↓
5. Build optimal context (STM + LTM + Summary)
   ↓
6. Send to LLM
   ↓
7. Save assistant response
   ↓
8. Return response with metadata
```

### Context Building Priority

1. **System Prompt** (Highest priority)
2. **Conversation Summary** (If exists, max 20% of tokens)
3. **Relevant Memories** (LTM, max 30% of tokens)
4. **Recent Messages** (STM, remaining tokens)

## API Endpoints

### Generate Response (with Memory)
```
POST /ai/generate
{
  "user_id": "user123",
  "conversation_id": "conv456",
  "message": "What did we discuss about Python?",
  "messages": [...]
}
```

Response includes memory metadata:
```json
{
  "assistant_message": "...",
  "meta": {
    "pipeline_version": "memory_v2",
    "memory": {
      "stm_turns": 10,
      "ltm_memories_retrieved": 2,
      "has_summary": true,
      "consolidation_count": 1,
      "total_tokens": 2500
    }
  }
}
```

### Get Conversation History
```
POST /ai/memory/history
{
  "user_id": "user123",
  "conversation_id": "conv456",
  "limit": 10
}
```

### Get Memory Stats
```
POST /ai/memory/stats
{
  "user_id": "user123",
  "conversation_id": "conv456"
}
```

### Get Conversation Summary
```
POST /ai/memory/summary
{
  "user_id": "user123",
  "conversation_id": "conv456"
}
```

### Clear Memory
```
POST /ai/memory/clear
{
  "user_id": "user123",
  "conversation_id": "conv456"
}
```

## Configuration

### Memory Manager Settings

```python
# In memory_manager.py
max_context_tokens = 3000  # Maximum tokens for context
consolidation_threshold = 20  # Turns before consolidation
max_ltm_memories = 3  # Max memories from LTM
```

### Context Manager Settings

```python
# In context_manager.py
avg_tokens_per_char = 0.3  # Token estimation
summary_max_ratio = 0.2  # 20% max for summary
ltm_max_ratio = 0.3  # 30% max for LTM
```

## Storage

Memories are stored in JSON files:

```
data/memory/
├── conversations/
│   └── user123/
│       └── conv456.json
├── summaries/
│   └── user123/
│       └── conv456.json
└── embeddings/
    └── cache.json
```

### Conversation File Format
```json
{
  "turns": [
    {
      "role": "user",
      "content": "Hello",
      "timestamp": "2024-02-06T10:00:00"
    }
  ],
  "metadata": {
    "last_updated": "2024-02-06T10:00:00",
    "turn_count": 1
  }
}
```

### Summary File Format
```json
{
  "summary": "User asked about Python...",
  "created_at": "2024-02-06T10:00:00",
  "conversation_id": "conv456",
  "user_id": "user123",
  "consolidation_count": 1
}
```

## Memory Consolidation

Consolidation happens when:
- Conversation exceeds 20 turns
- Context exceeds token limits

Process:
1. Identify old messages
2. Summarize using LLM
3. Store summary
4. Update conversation state
5. Free up context space

## Semantic Retrieval

Uses Gemini Embedding API for semantic search:

1. Get embedding for current query
2. Compare with stored conversation embeddings
3. Calculate cosine similarity
4. Return top N most similar contexts

## Best Practices

### For API Users

1. **Always provide user_id and conversation_id** for proper memory tracking
2. **Send full conversation history** in messages array
3. **Monitor memory metadata** to understand AI's context
4. **Clear memory** when starting new topics

### For Developers

1. **Token budgets**: Adjust based on LLM model limits
2. **Consolidation threshold**: Balance between memory and summarization
3. **LTM retrieval count**: More memories = richer context but more tokens
4. **Embedding cache**: Keep cache warm for frequently accessed conversations

## Performance

### Token Usage
- Average context: 2000-3000 tokens
- Summary overhead: ~200 tokens
- LTM memories: ~300 tokens total

### Response Times
- Without LTM: ~1-2s
- With LTM (cold): ~2-4s
- With LTM (cached): ~1-3s

### Storage
- 100 conversations: ~5MB
- 1000 conversations: ~50MB
- Embeddings cache: ~10MB per 1000 queries

## Troubleshooting

### Memory not persisting
- Check `data/memory/` directory permissions
- Verify JSON files are being created
- Check logs for storage errors

### Context too large
- Reduce `max_context_tokens`
- Lower `consolidation_threshold`
- Limit LTM retrieval count

### Slow retrieval
- Check embedding API latency
- Enable embedding cache
- Reduce similarity calculations

## Future Enhancements

1. **Vector Database**: Replace JSON with Pinecone/Weaviate
2. **Advanced RAG**: Integrate with knowledge base
3. **Multi-modal Memory**: Support images, code snippets
4. **Memory Decay**: Implement forgetting curve
5. **User Preferences**: Store persistent user preferences
6. **Cross-conversation Learning**: Learn from all user conversations

## Migration from Old System

Old system (STM v1.5):
```python
messages = build_stm_context(req.messages)
```

New system (Memory v2):
```python
memory_result = await memory_manager.process_conversation(...)
context = memory_result["context"]
```

The new system is backward compatible - if no memory exists, it behaves like the old STM system.

## Contributing

When adding new memory features:
1. Add new module in `modules/ai/memory/`
2. Integrate with `MemoryManager`
3. Update documentation
4. Add tests
5. Update API endpoints if needed

## License

Part of PromptLearn AI Service - See main LICENSE file
