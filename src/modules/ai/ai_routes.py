from fastapi import APIRouter
from modules.ai.ai_controller import generate
from modules.ai.ai_schemas import GenerateRequest, GenerateResponse

router = APIRouter(prefix="/ai", tags=["AI"])


@router.post("/generate", response_model=GenerateResponse)
async def generate_route(req: GenerateRequest):
    return await generate(req)