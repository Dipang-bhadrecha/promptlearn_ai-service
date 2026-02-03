import os
import httpx
from typing import List, Dict

GEMINI_ENDPOINT = (
    "https://generativelanguage.googleapis.com/v1beta/"
    "models/gemini-2.0-flash:generateContent"
)


def get_api_key() -> str:
    key = os.getenv("GOOGLE_API_KEY")
    if not key:
        raise RuntimeError("GOOGLE_API_KEY is not set")
    return key


async def call_llm(messages: List[Dict[str, str]]) -> str:
    api_key = get_api_key()

    contents = []
    for msg in messages:
        contents.append({
            "role": "user" if msg["role"] == "user" else "model",
            "parts": [{"text": msg["content"]}],
        })

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(
            GEMINI_ENDPOINT,
            params={"key": api_key},
            headers={"Content-Type": "application/json"},
            json={"contents": contents},
        )

        response.raise_for_status()
        data = response.json()

    return (
        data.get("candidates", [{}])[0]
        .get("content", {})
        .get("parts", [{}])[0]
        .get("text", "")
        or "No response from model"
    )
