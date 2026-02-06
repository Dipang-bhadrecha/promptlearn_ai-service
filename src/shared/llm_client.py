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

    # Extract system messages and combine them
    system_parts = []
    contents = []

    for msg in messages:
        if msg["role"] == "system":
            # Collect system messages separately
            system_parts.append(msg["content"])
        elif msg["role"] == "user":
            contents.append({
                "role": "user",
                "parts": [{"text": msg["content"]}],
            })
        elif msg["role"] == "assistant":
            contents.append({
                "role": "model",
                "parts": [{"text": msg["content"]}],
            })

    # If no user/assistant messages, create a user message from system
    if not contents:
        if system_parts:
            contents.append({
                "role": "user",
                "parts": [{"text": "\n\n".join(system_parts)}],
            })
        else:
            raise ValueError("No messages to send to LLM")
    else:
        # Prepend system instructions to the first user message if system messages exist
        if system_parts:
            system_instruction = "\n\n".join(system_parts)
            # Find first user message and prepend system instruction
            for content in contents:
                if content["role"] == "user":
                    original_text = content["parts"][0]["text"]
                    content["parts"][0]["text"] = f"{system_instruction}\n\n{original_text}"
                    break

    # Ensure conversation starts with user message (Gemini requirement)
    if contents and contents[0]["role"] != "user":
        # If first message is model, add a placeholder user message
        contents.insert(0, {
            "role": "user",
            "parts": [{"text": "Hello"}]
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
