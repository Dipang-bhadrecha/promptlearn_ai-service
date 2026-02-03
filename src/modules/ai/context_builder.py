from typing import List
from modules.ai.ai_schemas import Message

SYSTEM_PROMPT = """
You are PromptLearn, an intelligent programming tutor.

IMPORTANT:
- Answer ONLY the user's latest question.
- Previous messages are context only.
- If the topic changes, respond to the new topic.
"""

def build_stm_context(messages: List[Message], max_turns: int = 6):
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

    # 3️⃣ FORCE latest user intent dominance
    last_user = next(
        (m.content for m in reversed(messages) if m.role == "user"),
        None
    )

    if last_user:
        context.append({
            "role": "system",
            "content": f"Answer the following user question clearly:\n{last_user}"
        })

    return context
