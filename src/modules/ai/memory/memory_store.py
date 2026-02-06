"""
Memory Store - Persistent storage for conversation memory
Uses JSON files for simplicity (can be swapped with Redis/PostgreSQL)
"""
import os
import json
import asyncio
from typing import List, Dict, Optional
from datetime import datetime
from pathlib import Path


class MemoryStore:
    """
    Handles persistent storage of:
    - Conversation turns
    - Summaries
    - User context
    - Memory embeddings
    """

    def __init__(self, storage_path: str = None):
        if storage_path is None:
            base_dir = Path(__file__).resolve().parent.parent.parent.parent.parent
            storage_path = base_dir / "data" / "memory"

        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

        self.conversations_dir = self.storage_path / "conversations"
        self.summaries_dir = self.storage_path / "summaries"
        self.embeddings_dir = self.storage_path / "embeddings"

        self.conversations_dir.mkdir(exist_ok=True)
        self.summaries_dir.mkdir(exist_ok=True)
        self.embeddings_dir.mkdir(exist_ok=True)

    def _get_conversation_file(self, user_id: str, conversation_id: str) -> Path:
        """Get file path for conversation"""
        user_dir = self.conversations_dir / str(user_id)
        user_dir.mkdir(exist_ok=True)
        return user_dir / f"{conversation_id}.json"

    def _get_summary_file(self, user_id: str, conversation_id: str) -> Path:
        """Get file path for summary"""
        user_dir = self.summaries_dir / str(user_id)
        user_dir.mkdir(exist_ok=True)
        return user_dir / f"{conversation_id}.json"

    async def save_turn(
        self,
        user_id: str,
        conversation_id: str,
        message: str,
        role: str
    ):
        """Save a conversation turn"""
        file_path = self._get_conversation_file(user_id, conversation_id)

        # Load existing
        data = {"turns": [], "metadata": {}}
        if file_path.exists():
            with open(file_path, "r") as f:
                data = json.load(f)

        # Add new turn
        turn = {
            "role": role,
            "content": message,
            "timestamp": datetime.utcnow().isoformat()
        }
        data["turns"].append(turn)
        data["metadata"]["last_updated"] = datetime.utcnow().isoformat()
        data["metadata"]["turn_count"] = len(data["turns"])

        # Save
        with open(file_path, "w") as f:
            json.dump(data, f, indent=2)

    async def get_conversation_history(
        self,
        user_id: str,
        conversation_id: str,
        limit: Optional[int] = None
    ) -> List[Dict]:
        """Get conversation history"""
        file_path = self._get_conversation_file(user_id, conversation_id)

        if not file_path.exists():
            return []

        with open(file_path, "r") as f:
            data = json.load(f)

        turns = data.get("turns", [])

        if limit:
            return turns[-limit:]
        return turns

    async def save_summary(
        self,
        user_id: str,
        conversation_id: str,
        summary: str
    ):
        """Save conversation summary"""
        file_path = self._get_summary_file(user_id, conversation_id)

        data = {
            "summary": summary,
            "created_at": datetime.utcnow().isoformat(),
            "conversation_id": conversation_id,
            "user_id": user_id
        }

        with open(file_path, "w") as f:
            json.dump(data, f, indent=2)

    async def get_summary(
        self,
        user_id: str,
        conversation_id: str
    ) -> Optional[str]:
        """Get conversation summary"""
        file_path = self._get_summary_file(user_id, conversation_id)

        if not file_path.exists():
            return None

        with open(file_path, "r") as f:
            data = json.load(f)

        return data.get("summary")

    async def get_conversation_state(
        self,
        user_id: str,
        conversation_id: str
    ) -> Dict:
        """Get conversation state (summary, metadata, etc.)"""
        summary = await self.get_summary(user_id, conversation_id)

        return {
            "summary": summary,
            "consolidation_count": 0
        }

    async def update_conversation_state(
        self,
        user_id: str,
        conversation_id: str,
        state: Dict
    ):
        """Update conversation state"""
        file_path = self._get_summary_file(user_id, conversation_id)

        data = {}
        if file_path.exists():
            with open(file_path, "r") as f:
                data = json.load(f)

        data.update(state)
        data["updated_at"] = datetime.utcnow().isoformat()

        with open(file_path, "w") as f:
            json.dump(data, f, indent=2)

    async def clear_conversation(
        self,
        user_id: str,
        conversation_id: str
    ):
        """Clear all memory for a conversation"""
        conv_file = self._get_conversation_file(user_id, conversation_id)
        summary_file = self._get_summary_file(user_id, conversation_id)

        if conv_file.exists():
            conv_file.unlink()

        if summary_file.exists():
            summary_file.unlink()

    async def get_all_conversations(self, user_id: str) -> List[Dict]:
        """Get all conversations for a user"""
        user_dir = self.conversations_dir / str(user_id)

        if not user_dir.exists():
            return []

        conversations = []
        for file_path in user_dir.glob("*.json"):
            with open(file_path, "r") as f:
                data = json.load(f)
                conversations.append({
                    "conversation_id": file_path.stem,
                    "turn_count": len(data.get("turns", [])),
                    "last_updated": data.get("metadata", {}).get("last_updated")
                })

        return conversations
