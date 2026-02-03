from modules.ai.ai_schemas import GenerateRequest, GenerateResponse
from modules.ai.ai_service import generate_response


async def generate(req: GenerateRequest) -> GenerateResponse:
    return await generate_response(req)
