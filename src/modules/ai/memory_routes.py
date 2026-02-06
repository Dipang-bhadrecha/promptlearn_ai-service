"""
Memory Management Routes - API endpoints for memory operations
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict
from modules.ai import ai_memory

router = APIRouter(prefix="/ai/memory", tags=["Memory"])


class GetHistoryRequest(BaseModel):
    user_id: str
    conversation_id: str
    limit: Optional[int] = None


class GetStatsRequest(BaseModel):
    user_id: str
    conversation_id: str


class ClearMemoryRequest(BaseModel):
    user_id: str
    conversation_id: str


@router.post("/history")
async def get_history(req: GetHistoryRequest):
    """Get conversation history"""
    try:
        history = await ai_memory.get_conversation_history(
            req.user_id,
            req.conversation_id,
            req.limit
        )
        return {
            "success": True,
            "history": history,
            "count": len(history)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stats")
async def get_stats(req: GetStatsRequest):
    """Get memory statistics for a conversation"""
    try:
        stats = await ai_memory.get_memory_stats(
            req.user_id,
            req.conversation_id
        )
        return {
            "success": True,
            "stats": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/summary")
async def get_summary(req: GetStatsRequest):
    """Get conversation summary"""
    try:
        summary = await ai_memory.get_summary(
            req.user_id,
            req.conversation_id
        )
        return {
            "success": True,
            "summary": summary
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/clear")
async def clear_memory(req: ClearMemoryRequest):
    """Clear all memory for a conversation"""
    try:
        await ai_memory.clear_memory(
            req.user_id,
            req.conversation_id
        )
        return {
            "success": True,
            "message": "Memory cleared successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """Check if memory system is operational"""
    return {
        "status": "healthy",
        "memory_system": "operational"
    }
