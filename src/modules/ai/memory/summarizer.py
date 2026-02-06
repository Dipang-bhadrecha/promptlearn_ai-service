"""
Summarizer - Creates conversation summaries for memory consolidation
"""
from typing import List
from modules.ai.ai_schemas import Message
from shared.llm_client import call_llm


class Summarizer:
    """
    Handles conversation summarization for long-term memory
    """

    SUMMARIZATION_PROMPT = """You are a conversation summarizer for an AI assistant.

Your task: Create a concise summary of the conversation below that captures:
1. Main topics discussed
2. Key information exchanged
3. Important decisions or conclusions
4. User preferences or context

Keep the summary under 200 words. Focus on what's most important for future context.

Conversation:
{conversation}

Summary:"""

    async def summarize_conversation(
        self,
        conversation_history: List[Message],
        max_messages: int = 30
    ) -> str:
        """
        Generate a summary of the conversation
        """
        # Take recent messages for summarization
        messages_to_summarize = conversation_history[-max_messages:]

        # Format conversation
        formatted_conv = self._format_conversation(messages_to_summarize)

        # Create prompt
        prompt = self.SUMMARIZATION_PROMPT.format(conversation=formatted_conv)

        # Call LLM for summarization
        summary = await call_llm([
            {"role": "user", "content": prompt}
        ])

        return summary.strip()

    async def progressive_summarize(
        self,
        old_summary: str,
        new_messages: List[Message]
    ) -> str:
        """
        Update existing summary with new conversation turns
        (Progressive summarization - more efficient)
        """
        formatted_new = self._format_conversation(new_messages)

        prompt = f"""You are updating a conversation summary.

Previous summary:
{old_summary}

New conversation turns:
{formatted_new}

Create an updated summary that incorporates the new information while keeping it concise (under 200 words).

Updated summary:"""

        updated_summary = await call_llm([
            {"role": "user", "content": prompt}
        ])

        return updated_summary.strip()

    def _format_conversation(self, messages: List[Message]) -> str:
        """Format messages into readable text"""
        formatted = []

        for msg in messages:
            role_label = "User" if msg.role == "user" else "Assistant"
            formatted.append(f"{role_label}: {msg.content}")

        return "\n".join(formatted)

    async def extract_key_facts(
        self,
        conversation_history: List[Message]
    ) -> List[str]:
        """
        Extract key facts/information from conversation
        (Useful for building knowledge base)
        """
        formatted_conv = self._format_conversation(conversation_history)

        prompt = f"""Extract key facts and information from this conversation.
Return as a bulleted list of important points.

Conversation:
{formatted_conv}

Key facts:"""

        response = await call_llm([
            {"role": "user", "content": prompt}
        ])

        # Parse bullet points
        facts = [
            line.strip().lstrip("•-*").strip()
            for line in response.split("\n")
            if line.strip() and line.strip()[0] in "•-*"
        ]

        return facts
