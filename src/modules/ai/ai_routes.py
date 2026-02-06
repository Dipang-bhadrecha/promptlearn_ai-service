from fastapi import APIRouter, HTTPException
from modules.ai.ai_controller import generate
from modules.ai.ai_schemas import GenerateRequest, GenerateResponse
import traceback

router = APIRouter(prefix="/ai", tags=["AI"])


@router.post("/generate", response_model=GenerateResponse)
async def generate_route(req: GenerateRequest):
    try:
        return await generate(req)
    except Exception as e:
        print(f"ERROR in /ai/generate: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))