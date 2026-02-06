"""
Context Manager - Manages context window and token limits
Ensures optimal use of available context space
"""
from typing import List, Dict, Optional
from modules.ai.ai_schemas import Message


class ContextManager:
    """
    Manages context window constraints:
    - Token counting
    - Context prioritization
    - Dynamic context building
    """

    def __init__(self, avg_tokens_per_char: float = 0.3):
        """
        avg_tokens_per_char: Rough estimate for token counting
        (actual tokenization would use tiktoken, but this is good enough)
        """
        self.avg_tokens_per_char = avg_tokens_per_char

    def count_tokens(self, messages: List[Dict]) -> int:
        """Estimate token count for messages"""
        total_chars = sum(len(msg.get("content", "")) for msg in messages)
        return int(total_chars * self.avg_tokens_per_char)

    def should_consolidate(
        self,
        conversation_history: List[Message],
        threshold_turns: int = 20
    ) -> bool:
        """
        Determine if conversation should be consolidated/summarized
        """
        return len(conversation_history) >= threshold_turns

    def build_context(
        self,
        conversation_history: List[Message],
        conversation_summary: Optional[str] = None,
        relevant_memories: List[Dict] = None,
        max_tokens: int = 3000,
        system_prompt: str = None
    ) -> List[Dict]:
        """
        Build optimal context within token limits

        Priority order:
        1. System prompt
        2. Conversation summary (if exists)
        3. Relevant memories (LTM)
        4. Recent conversation (STM)
        """
        context = []
        token_budget = max_tokens
        seen_content = set()  # Track content to avoid duplication

        # 1. System prompt (highest priority)
        if system_prompt:
            system_msg = {"role": "system", "content": system_prompt}
            system_tokens = self.count_tokens([system_msg])

            if system_tokens < token_budget:
                context.append(system_msg)
                token_budget -= system_tokens

        # 2. Conversation summary (if exists)
        if conversation_summary:
            summary_msg = {
                "role": "system",
                "content": f"[Previous conversation summary]\n{conversation_summary}"
            }
            summary_tokens = self.count_tokens([summary_msg])

            if summary_tokens < token_budget * 0.2:  # Max 20% for summary
                context.append(summary_msg)
                token_budget -= summary_tokens

        # 3. Relevant memories (LTM)
        if relevant_memories:
            memory_content = self._format_memories(relevant_memories)
            if memory_content:
                memory_msg = {
                    "role": "system",
                    "content": f"[Relevant context from past conversations]\n{memory_content}"
                }
                memory_tokens = self.count_tokens([memory_msg])

                if memory_tokens < token_budget * 0.3:  # Max 30% for memories
                    context.append(memory_msg)
                    token_budget -= memory_tokens

        # 4. Recent conversation (STM) - most important
        recent_messages = self._fit_recent_messages(
            conversation_history,
            token_budget
        )

        for msg in recent_messages:
            # Deduplicate: only add if content hasn't been seen
            content_hash = msg.content.strip().lower()[:100]  # Hash first 100 chars
            if content_hash not in seen_content:
                context.append({
                    "role": msg.role,
                    "content": msg.content
                })
                seen_content.add(content_hash)

        return context

    def _format_memories(self, memories: List[Dict]) -> str:
        """Format retrieved memories into readable text"""
        if not memories:
            return ""

        formatted = []
        for i, memory in enumerate(memories, 1):
            formatted.append(f"{i}. {memory.get('content', '')}")

        return "\n".join(formatted)

    def _fit_recent_messages(
        self,
        conversation_history: List[Message],
        token_budget: int
    ) -> List[Message]:
        """
        Fit as many recent messages as possible within token budget
        Always prioritize the latest messages
        """
        if not conversation_history:
            return []

        # Work backwards from most recent
        fitted_messages = []
        remaining_budget = token_budget

        for msg in reversed(conversation_history):
            msg_tokens = self.count_tokens([{"content": msg.content}])

            if msg_tokens <= remaining_budget:
                fitted_messages.insert(0, msg)
                remaining_budget -= msg_tokens
            else:
                break

        return fitted_messages

    def get_context_stats(self, context: List[Dict]) -> Dict:
        """Get statistics about the built context"""
        return {
            "total_messages": len(context),
            "total_tokens": self.count_tokens(context),
            "system_messages": sum(1 for m in context if m["role"] == "system"),
            "user_messages": sum(1 for m in context if m["role"] == "user"),
            "assistant_messages": sum(1 for m in context if m["role"] == "assistant"),
        }
