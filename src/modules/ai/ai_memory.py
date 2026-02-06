"""
AI Memory - Public API for memory operations
Provides simple interface for managing conversation memory
"""
from modules.ai.memory.memory_manager import MemoryManager
from typing import Dict, List, Optional

# Global memory manager instance
_memory_manager = None


def get_memory_manager() -> MemoryManager:
    """Get or create memory manager singleton"""
    global _memory_manager
    if _memory_manager is None:
        _memory_manager = MemoryManager()
    return _memory_manager


async def save_message(
    user_id: str,
    conversation_id: str,
    message: str,
    role: str
):
    """
    Save a message to memory

    Args:
        user_id: User identifier
        conversation_id: Conversation identifier
        message: Message content
        role: 'user' or 'assistant'
    """
    manager = get_memory_manager()
    await manager.store.save_turn(user_id, conversation_id, message, role)


async def get_conversation_history(
    user_id: str,
    conversation_id: str,
    limit: Optional[int] = None
) -> List[Dict]:
    """
    Get conversation history

    Args:
        user_id: User identifier
        conversation_id: Conversation identifier
        limit: Maximum number of turns to retrieve

    Returns:
        List of conversation turns
    """
    manager = get_memory_manager()
    return await manager.store.get_conversation_history(
        user_id, conversation_id, limit
    )


async def get_memory_stats(
    user_id: str,
    conversation_id: str
) -> Dict:
    """
    Get memory statistics for a conversation

    Returns:
        Dictionary with memory stats
    """
    manager = get_memory_manager()

    history = await manager.store.get_conversation_history(user_id, conversation_id)
    state = await manager.store.get_conversation_state(user_id, conversation_id)

    return {
        "total_turns": len(history),
        "has_summary": bool(state.get("summary")),
        "consolidation_count": state.get("consolidation_count", 0),
        "last_updated": history[-1]["timestamp"] if history else None
    }


async def clear_memory(user_id: str, conversation_id: str):
    """
    Clear all memory for a conversation

    Args:
        user_id: User identifier
        conversation_id: Conversation identifier
    """
    manager = get_memory_manager()
    await manager.clear_conversation_memory(user_id, conversation_id)


async def get_summary(user_id: str, conversation_id: str) -> Optional[str]:
    """
    Get conversation summary

    Args:
        user_id: User identifier
        conversation_id: Conversation identifier

    Returns:
        Conversation summary or None
    """
    manager = get_memory_manager()
    return await manager.get_conversation_summary(user_id, conversation_id)
