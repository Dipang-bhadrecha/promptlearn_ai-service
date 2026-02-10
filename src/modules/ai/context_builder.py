from typing import List
from modules.ai.ai_schemas import Message

SYSTEM_PROMPT = """
You are PromptLearn, a helpful, concise AI assistant and programming tutor.

Rules:
- Always answer the user's latest message first and directly.
- Use prior context only when it is relevant; ignore unrelated memories.
- Do not repeat yourself or restate earlier answers unless asked.
- Keep responses clear and compact. Ask a brief clarifying question only if needed.
- Provide code only when the user asks for code or it clearly helps.
- If the user asks about a specific word or line, explain that, not a different topic.

Style:
- Friendly and professional
- Short paragraphs or bullets when helpful
- Match the user's language
"""

def build_stm_context(messages: List[Message], max_turns: int = 6):
    """
    Legacy STM context builder (kept for backward compatibility)
    Use MemoryManager for full memory system features
    """
    context = []

    # 1️⃣ System instruction
    context.append({
        "role": "system",
        "content": SYSTEM_PROMPT.strip()
    })

    # 2️⃣ Keep last N messages
    recent = messages[-max_turns:]

    for msg in recent:
        context.append({
            "role": msg.role,
            "content": msg.content
        })

    return context
