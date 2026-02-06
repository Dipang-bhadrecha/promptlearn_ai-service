"""
Memory Retriever - Finds relevant context from long-term memory
Uses semantic similarity to retrieve contextually relevant past conversations
"""
import os
import json
import httpx
from typing import List, Dict, Optional
from pathlib import Path


class MemoryRetriever:
    """
    Retrieves relevant memories from long-term storage
    Uses embeddings for semantic search
    """

    def __init__(self, memory_store):
        self.store = memory_store
        self.embeddings_cache = {}
        self.gemini_embedding_endpoint = (
            "https://generativelanguage.googleapis.com/v1beta/"
            "models/text-embedding-004:embedContent"
        )

    async def find_relevant_context(
        self,
        user_id: str,
        conversation_id: str,
        current_query: str,
        max_memories: int = 3
    ) -> List[Dict]:
        """
        Find relevant memories from past conversations

        Strategy:
        1. Get current query embedding
        2. Compare with stored conversation embeddings
        3. Return top N most similar contexts
        """
        # Get all conversations for user
        all_conversations = await self.store.get_all_conversations(user_id)

        # Filter out current conversation
        other_conversations = [
            c for c in all_conversations
            if c["conversation_id"] != conversation_id
        ]

        if not other_conversations:
            return []

        # Get query embedding
        query_embedding = await self._get_embedding(current_query)

        if not query_embedding:
            return []

        # Find most similar conversations
        similarities = []

        for conv in other_conversations:
            conv_id = conv["conversation_id"]

            # Get conversation summary
            summary = await self.store.get_summary(user_id, conv_id)

            if not summary:
                continue

            # Get summary embedding
            summary_embedding = await self._get_embedding(summary)

            if not summary_embedding:
                continue

            # Calculate similarity
            similarity = self._cosine_similarity(query_embedding, summary_embedding)

            similarities.append({
                "conversation_id": conv_id,
                "summary": summary,
                "similarity": similarity
            })

        # Sort by similarity and return top N
        similarities.sort(key=lambda x: x["similarity"], reverse=True)
        top_memories = similarities[:max_memories]

        # Format memories
        formatted_memories = []
        for mem in top_memories:
            formatted_memories.append({
                "content": mem["summary"],
                "similarity": mem["similarity"],
                "source": f"conversation_{mem['conversation_id']}"
            })

        return formatted_memories

    async def _get_embedding(self, text: str) -> Optional[List[float]]:
        """
        Get embedding for text using Gemini Embedding API
        """
        # Check cache first
        if text in self.embeddings_cache:
            return self.embeddings_cache[text]

        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            return None

        try:
            async with httpx.AsyncClient(timeout=15) as client:
                response = await client.post(
                    self.gemini_embedding_endpoint,
                    params={"key": api_key},
                    headers={"Content-Type": "application/json"},
                    json={
                        "model": "models/text-embedding-004",
                        "content": {
                            "parts": [{"text": text}]
                        }
                    }
                )

                response.raise_for_status()
                data = response.json()

                embedding = data.get("embedding", {}).get("values", [])

                # Cache it
                self.embeddings_cache[text] = embedding

                return embedding

        except Exception as e:
            print(f"Error getting embedding: {e}")
            return None

    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        if not vec1 or not vec2 or len(vec1) != len(vec2):
            return 0.0

        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude1 = sum(a * a for a in vec1) ** 0.5
        magnitude2 = sum(b * b for b in vec2) ** 0.5

        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0

        return dot_product / (magnitude1 * magnitude2)

    async def get_conversation_context(
        self,
        user_id: str,
        conversation_id: str,
        query: str
    ) -> Optional[str]:
        """
        Get the most relevant context from a specific conversation
        """
        turns = await self.store.get_conversation_history(user_id, conversation_id)

        if not turns:
            return None

        # Get embeddings for query and all turns
        query_emb = await self._get_embedding(query)

        if not query_emb:
            return None

        best_match = None
        best_similarity = -1

        for turn in turns:
            turn_text = turn.get("content", "")
            turn_emb = await self._get_embedding(turn_text)

            if not turn_emb:
                continue

            similarity = self._cosine_similarity(query_emb, turn_emb)

            if similarity > best_similarity:
                best_similarity = similarity
                best_match = turn_text

        return best_match
