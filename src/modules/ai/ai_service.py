
# from modules.ai.ai_schemas import GenerateRequest, GenerateResponse
# from modules.ai.context_builder import build_stm_context
# from shared.llm_client import call_llm


# async def generate_response(req: GenerateRequest) -> GenerateResponse:
#     messages = build_stm_context(req.messages)

#     assistant_text = await call_llm(messages)

#     return GenerateResponse(
#         assistant_message=assistant_text,
#         meta={
#             "pipeline_version": "stm_v1",
#             "memory_used": len(messages) > 1,
#         },
#     )

from modules.ai.context_builder import build_stm_context
from shared.llm_client import call_llm

async def generate_response(req):
    messages = build_stm_context(req.messages)

    assistant_text = await call_llm(messages)

    return {
        "assistant_message": assistant_text,
        "meta": {
            "pipeline_version": "stm_v1.5",
            "memory_used": len(messages) > 1,
        },
    }
