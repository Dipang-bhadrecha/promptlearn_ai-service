"""
AI Service - Main business logic for AI generation
Now with full memory system integration
"""
import asyncio
from modules.ai.ai_schemas import GenerateRequest, GenerateResponse
from modules.ai.memory.memory_manager import MemoryManager
from modules.ai.context_builder import SYSTEM_PROMPT
from shared.llm_client import call_llm

# Initialize memory manager (singleton)
memory_manager = MemoryManager()
_user_locks = {}


def _get_user_lock(user_id: str) -> asyncio.Lock:
    lock = _user_locks.get(user_id)
    if lock is None:
        lock = asyncio.Lock()
        _user_locks[user_id] = lock
    return lock


async def generate_response(req: GenerateRequest) -> GenerateResponse:
    """
    Generate AI response with full memory system

    Flow:
    1. Process conversation through memory manager
    2. Get enriched context (STM + LTM + summaries)
    3. Call LLM with smart context
    4. Save assistant response to memory
    """

    # Serialize requests per user to avoid API bursts/rate limits
    user_lock = _get_user_lock(str(req.user_id))
    async with user_lock:
        # 1️⃣ Process conversation through memory system
        memory_result = await memory_manager.process_conversation(
            user_id=str(req.user_id),
            conversation_id=str(req.conversation_id),
            new_message=req.message,
            conversation_history=req.messages,
            max_context_tokens=3000
        )

        # 2️⃣ Get enriched context
        enriched_context = memory_result["context"]

        # 3️⃣ Add system prompt if not present
        if not any(msg.get("role") == "system" for msg in enriched_context):
            enriched_context.insert(0, {
                "role": "system",
                "content": SYSTEM_PROMPT.strip()
            })

        # 4️⃣ Call LLM with sensible defaults for "smart" responses
        options = req.options or {
            "temperature": 0.4,
            "top_p": 0.9,
            "response_length": "long",
        }
        assistant_text = await call_llm(enriched_context, options=options)

        # 5️⃣ Save assistant response to memory
        await memory_manager.save_assistant_response(
            user_id=str(req.user_id),
            conversation_id=str(req.conversation_id),
            response=assistant_text
        )

    # 6️⃣ Return response with rich metadata
    return GenerateResponse(
        assistant_message=assistant_text,
        meta={
            "pipeline_version": "memory_v2",
            "memory": memory_result["metadata"],
            "context_tokens": memory_result["metadata"]["total_tokens"],
            "stm_enabled": True,
            "ltm_enabled": True,
            "smart_retrieval": memory_result["metadata"]["ltm_memories_retrieved"] > 0
        }
    )


async def get_conversation_summary(user_id: str, conversation_id: str) -> str:
    """Get summary of a conversation"""
    return await memory_manager.get_conversation_summary(
        user_id=str(user_id),
        conversation_id=str(conversation_id)
    )


async def clear_conversation(user_id: str, conversation_id: str):
    """Clear all memory for a conversation"""
    await memory_manager.clear_conversation_memory(
        user_id=str(user_id),
        conversation_id=str(conversation_id)
    )
