"""
Memory Manager - Orchestrates the entire AI memory system
Handles STM, LTM, retrieval, and consolidation
"""
from typing import List, Dict, Optional
from modules.ai.ai_schemas import Message
from modules.ai.memory.memory_store import MemoryStore
from modules.ai.memory.context_manager import ContextManager
from modules.ai.memory.summarizer import Summarizer
from modules.ai.memory.retriever import MemoryRetriever


class MemoryManager:
    """
    Central orchestrator for AI memory system

    Manages:
    - Short-term memory (recent turns)
    - Long-term memory (summarized context)
    - Context window limits
    - Memory retrieval and consolidation
    """

    def __init__(self):
        self.store = MemoryStore()
        self.context_manager = ContextManager()
        self.summarizer = Summarizer()
        self.retriever = MemoryRetriever(self.store)

    async def process_conversation(
        self,
        user_id: str,
        conversation_id: str,
        new_message: str,
        conversation_history: List[Message],
        max_context_tokens: int = 3000
    ) -> Dict:
        """
        Main entry point for processing a conversation turn

        Returns enriched context with:
        - Recent messages (STM)
        - Relevant old context (LTM)
        - Conversation summary
        - Metadata about memory usage
        """

        # Ensure the latest user message is included in context
        effective_history = list(conversation_history or [])
        if not effective_history or not (
            effective_history[-1].role == "user"
            and effective_history[-1].content == new_message
        ):
            effective_history.append(Message(role="user", content=new_message))

        # 1. Load or create conversation state
        conv_state = await self.store.get_conversation_state(user_id, conversation_id)

        # 2. Check if we need to consolidate memory (context too large)
        if self.context_manager.should_consolidate(effective_history):
            summary = await self.summarizer.summarize_conversation(effective_history)
            await self.store.save_summary(user_id, conversation_id, summary)
            conv_state["summary"] = summary
            conv_state["consolidation_count"] = conv_state.get("consolidation_count", 0) + 1

        # 3. Retrieve relevant memories from LTM
        relevant_memories = await self.retriever.find_relevant_context(
            user_id=user_id,
            conversation_id=conversation_id,
            current_query=new_message,
            max_memories=3
        )

        # 4. Build optimal context within token limits
        context = self.context_manager.build_context(
            conversation_history=effective_history,
            conversation_summary=conv_state.get("summary"),
            relevant_memories=relevant_memories,
            max_tokens=max_context_tokens
        )

        # 5. Save current turn to memory store
        await self.store.save_turn(
            user_id=user_id,
            conversation_id=conversation_id,
            message=new_message,
            role="user"
        )

        # 6. Update conversation state
        await self.store.update_conversation_state(user_id, conversation_id, conv_state)

        return {
            "context": context,
            "metadata": {
                "stm_turns": len(effective_history),
                "ltm_memories_retrieved": len(relevant_memories),
                "has_summary": bool(conv_state.get("summary")),
                "consolidation_count": conv_state.get("consolidation_count", 0),
                "total_tokens": self.context_manager.count_tokens(context)
            }
        }

    async def save_assistant_response(
        self,
        user_id: str,
        conversation_id: str,
        response: str
    ):
        """Save assistant's response to memory"""
        await self.store.save_turn(
            user_id=user_id,
            conversation_id=conversation_id,
            message=response,
            role="assistant"
        )

    async def get_conversation_summary(
        self,
        user_id: str,
        conversation_id: str
    ) -> Optional[str]:
        """Get the current conversation summary"""
        state = await self.store.get_conversation_state(user_id, conversation_id)
        return state.get("summary")

    async def clear_conversation_memory(
        self,
        user_id: str,
        conversation_id: str
    ):
        """Clear all memory for a conversation"""
        await self.store.clear_conversation(user_id, conversation_id)
