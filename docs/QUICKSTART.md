# Memory System Quick Start Guide

## 🚀 Get Started in 5 Minutes

### 1. Start the Server

```bash
make dev
```

### 2. Test Basic Chat (No Memory)

```bash
curl -X POST "http://localhost:8000/ai/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user",
    "conversation_id": "test_conv",
    "message": "Hello! Can you explain what Python is?",
    "messages": []
  }'
```

### 3. Continue Conversation (Memory Active)

```bash
curl -X POST "http://localhost:8000/ai/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user",
    "conversation_id": "test_conv",
    "message": "What are its main features?",
    "messages": [
      {
        "role": "user",
        "content": "Hello! Can you explain what Python is?"
      },
      {
        "role": "assistant",
        "content": "Python is a high-level programming language..."
      }
    ]
  }'
```

### 4. Check Memory Stats

```bash
curl -X POST "http://localhost:8000/ai/memory/stats" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user",
    "conversation_id": "test_conv"
  }'
```

### 5. View Conversation History

```bash
curl -X POST "http://localhost:8000/ai/memory/history" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user",
    "conversation_id": "test_conv",
    "limit": 10
  }'
```

## 🧠 See Memory in Action

### Long Conversation Test

Send 25+ messages to trigger automatic summarization:

```python
import requests

url = "http://localhost:8000/ai/generate"

for i in range(30):
    response = requests.post(url, json={
        "user_id": "test_user",
        "conversation_id": "long_conv",
        "message": f"Tell me fact #{i} about programming",
        "messages": []  # Backend tracks full history
    })

    meta = response.json()["meta"]
    print(f"Turn {i}: Has summary: {meta['memory']['has_summary']}")
```

After 20 turns, you'll see `has_summary: true` indicating memory consolidation!

### Check the Generated Summary

```bash
curl -X POST "http://localhost:8000/ai/memory/summary" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user",
    "conversation_id": "long_conv"
  }'
```

## 🎯 Integration Examples

### Frontend Integration (React/Next.js)

```javascript
// chat.ts
export async function sendMessage(userId, conversationId, message, history) {
  const response = await fetch('http://localhost:8000/ai/generate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      user_id: userId,
      conversation_id: conversationId,
      message: message,
      messages: history  // Send full conversation history
    })
  });

  const data = await response.json();

  // data.meta.memory contains memory stats
  console.log('Memory stats:', data.meta.memory);

  return data.assistant_message;
}
```

### Memory Management

```javascript
// Clear conversation memory
async function clearMemory(userId, conversationId) {
  await fetch('http://localhost:8000/ai/memory/clear', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      user_id: userId,
      conversation_id: conversationId
    })
  });
}

// Get conversation stats
async function getMemoryStats(userId, conversationId) {
  const response = await fetch('http://localhost:8000/ai/memory/stats', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      user_id: userId,
      conversation_id: conversationId
    })
  });

  return await response.json();
}
```

## 🔍 Verify Memory Files

Check that memory is being stored:

```bash
# View memory storage
ls -la data/memory/conversations/test_user/

# View a conversation file
cat data/memory/conversations/test_user/test_conv.json

# View summary
cat data/memory/summaries/test_user/test_conv.json
```

## ⚙️ Configuration

Edit settings in `src/modules/ai/memory/memory_manager.py`:

```python
# Adjust these values
max_context_tokens = 3000        # Total tokens allowed
consolidation_threshold = 20     # Turns before summarization
max_ltm_memories = 3            # Max old memories to retrieve
```

## 🧪 Test Semantic Retrieval

Create multiple conversations, then ask about old ones:

```bash
# Conversation 1
curl -X POST "http://localhost:8000/ai/generate" \
  -d '{"user_id": "user1", "conversation_id": "conv1", "message": "Explain React hooks", "messages": []}'

# Conversation 2
curl -X POST "http://localhost:8000/ai/generate" \
  -d '{"user_id": "user1", "conversation_id": "conv2", "message": "Explain Python decorators", "messages": []}'

# New conversation - AI should retrieve relevant context
curl -X POST "http://localhost:8000/ai/generate" \
  -d '{"user_id": "user1", "conversation_id": "conv3", "message": "What did we discuss about React?", "messages": []}'
```

Check the response metadata - it should show `ltm_memories_retrieved > 0`!

## 📊 Monitor Memory Performance

```bash
# API response includes memory metadata
{
  "assistant_message": "...",
  "meta": {
    "memory": {
      "stm_turns": 10,                    # Recent turns in context
      "ltm_memories_retrieved": 2,        # Old conversations retrieved
      "has_summary": true,                # Conversation summarized
      "consolidation_count": 1,           # Times summarized
      "total_tokens": 2500                # Total context tokens
    }
  }
}
```

## 🎓 Next Steps

1. **Read Full Docs**: `docs/MEMORY_SYSTEM.md`
2. **Customize System Prompt**: `src/modules/ai/context_builder.py`
3. **Add Features**: Extend memory modules
4. **Production Setup**: Add Redis/PostgreSQL for scale
5. **Monitoring**: Add logging and metrics

## 🐛 Troubleshooting

**Memory not working?**
- Check `data/memory/` directory exists
- Verify GOOGLE_API_KEY is set
- Check server logs for errors

**Context too large?**
- Reduce `max_context_tokens`
- Lower `consolidation_threshold`

**Slow responses?**
- Enable embedding cache
- Reduce LTM retrieval count

## 💡 Tips

1. Use meaningful `conversation_id` values (e.g., `user123_chat_20240206`)
2. Always send full `messages` history for best context
3. Monitor memory metadata to understand AI behavior
4. Clear memory when switching topics
5. Use `/ai/memory/stats` to debug context issues

---

**Need help?** Check `docs/MEMORY_SYSTEM.md` or open an issue!
