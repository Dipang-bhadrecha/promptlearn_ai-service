import os
import asyncio
import httpx
from typing import List, Dict, Optional, Any

DEFAULT_GEMINI_MODELS = [
    "models/gemini-1.5-flash",
    "models/gemini-1.5-pro",
    "models/gemini-2.0-flash",
]

def _get_model_list() -> list[str]:
    env_models = os.getenv("GEMINI_MODELS")
    if env_models:
        return [m.strip() for m in env_models.split(",") if m.strip()]
    return DEFAULT_GEMINI_MODELS


def _get_provider() -> str:
    return (os.getenv("LLM_PROVIDER") or "gemini").strip().lower()


def _get_grok_config() -> tuple[str, str, str]:
    base_url = os.getenv("GROK_BASE_URL", "https://api.x.ai/v1").rstrip("/")
    model = os.getenv("GROK_MODEL", "grok-2-mini")
    api_key = os.getenv("GROK_API_KEY")
    if not api_key:
        raise RuntimeError("GROK_API_KEY is not set")
    return base_url, model, api_key


class ModelBusyError(RuntimeError):
    """Raised when the model is rate-limited or unavailable after retries."""


def get_api_key() -> str:
    key = os.getenv("GOOGLE_API_KEY")
    if not key:
        raise RuntimeError("GOOGLE_API_KEY is not set")
    return key


def _normalize_generation_config(options: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    if not options:
        return None

    cfg: Dict[str, Any] = {}

    # Response length helper (only sets maxOutputTokens if not explicitly provided)
    length = options.get("response_length")
    length_map = {
        "short": 256,
        "medium": 512,
        "long": 1024,
    }

    # Accept snake_case or camelCase inputs
    if "temperature" in options:
        cfg["temperature"] = options["temperature"]
    if "top_p" in options:
        cfg["topP"] = options["top_p"]
    if "topP" in options:
        cfg["topP"] = options["topP"]
    if "top_k" in options:
        cfg["topK"] = options["top_k"]
    if "topK" in options:
        cfg["topK"] = options["topK"]
    if "max_output_tokens" in options:
        cfg["maxOutputTokens"] = options["max_output_tokens"]
    if "maxOutputTokens" in options:
        cfg["maxOutputTokens"] = options["maxOutputTokens"]

    # Apply response_length if no explicit maxOutputTokens
    if "maxOutputTokens" not in cfg and length in length_map:
        cfg["maxOutputTokens"] = length_map[length]

    # Stop sequences
    if "stop" in options and isinstance(options["stop"], list):
        cfg["stopSequences"] = options["stop"]
    if "stopSequences" in options and isinstance(options["stopSequences"], list):
        cfg["stopSequences"] = options["stopSequences"]

    return cfg or None


async def call_llm(messages: List[Dict[str, str]], options: Optional[Dict[str, Any]] = None) -> str:
    provider = _get_provider()
    if provider == "grok":
        return await _call_grok(messages, options)

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

    # Ensure conversation starts with user message (Gemini requirement)
    if contents and contents[0]["role"] != "user":
        # If first message is model, add a placeholder user message
        contents.insert(0, {
            "role": "user",
            "parts": [{"text": "Hello"}]
        })

    payload = {"contents": contents}
    if system_parts:
        payload["systemInstruction"] = {
            "parts": [{"text": "\n\n".join(system_parts)}]
        }

    generation_config = _normalize_generation_config(options)
    if generation_config:
        payload["generationConfig"] = generation_config

    models = _get_model_list()

    last_error: Optional[str] = None

    async with httpx.AsyncClient(timeout=60) as client:
        for model in models:
            endpoint = (
                "https://generativelanguage.googleapis.com/v1beta/"
                f"{model}:generateContent"
            )
            for attempt in range(3):
                response = await client.post(
                    endpoint,
                    params={"key": api_key},
                    headers={"Content-Type": "application/json"},
                    json=payload,
                )

                if response.status_code in (429, 503):
                    last_error = f"{model} returned {response.status_code}: {response.text}"
                    if attempt < 2:
                        await asyncio.sleep(0.5 * (2 ** attempt))
                        continue
                    # Try next model if available
                    break

                if response.status_code in (404, 400, 403):
                    # Model not available or invalid request for this model
                    last_error = f"{model} returned {response.status_code}: {response.text}"
                    break

                response.raise_for_status()
                data = response.json()
                text = (
                    data.get("candidates", [{}])[0]
                    .get("content", {})
                    .get("parts", [{}])[0]
                    .get("text", "")
                )
                if not text:
                    last_error = f"{model} returned empty response"
                    raise ModelBusyError("Model returned empty response. Please retry.")
                return text

    raise ModelBusyError(last_error or "All models are busy or unavailable. Please retry.")


async def _call_grok(messages: List[Dict[str, str]], options: Optional[Dict[str, Any]] = None) -> str:
    base_url, model, api_key = _get_grok_config()
    url = f"{base_url}/chat/completions"

    chat_messages = []
    for msg in messages:
        role = msg.get("role")
        if role == "assistant":
            role = "assistant"
        elif role == "system":
            role = "system"
        else:
            role = "user"
        chat_messages.append({"role": role, "content": msg.get("content", "")})

    payload: Dict[str, Any] = {
        "model": model,
        "messages": chat_messages,
    }

    if options:
        if "temperature" in options:
            payload["temperature"] = options["temperature"]
        if "top_p" in options:
            payload["top_p"] = options["top_p"]
        if "topP" in options:
            payload["top_p"] = options["topP"]
        if "max_output_tokens" in options:
            payload["max_tokens"] = options["max_output_tokens"]
        if "maxOutputTokens" in options:
            payload["max_tokens"] = options["maxOutputTokens"]
        if "response_length" in options and "max_tokens" not in payload:
            length_map = {"short": 256, "medium": 512, "long": 1024}
            if options["response_length"] in length_map:
                payload["max_tokens"] = length_map[options["response_length"]]
        if "stop" in options and isinstance(options["stop"], list):
            payload["stop"] = options["stop"]
        if "stopSequences" in options and isinstance(options["stopSequences"], list):
            payload["stop"] = options["stopSequences"]

    async with httpx.AsyncClient(timeout=60) as client:
        for attempt in range(3):
            response = await client.post(
                url,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {api_key}",
                },
                json=payload,
            )

            if response.status_code in (429, 503):
                if attempt < 2:
                    await asyncio.sleep(0.5 * (2 ** attempt))
                    continue
                raise ModelBusyError("Model is busy. Please retry.")

            response.raise_for_status()
            data = response.json()
            text = (
                data.get("choices", [{}])[0]
                .get("message", {})
                .get("content", "")
            )
            if not text:
                raise ModelBusyError("Model returned empty response. Please retry.")
            return text

    raise ModelBusyError("Model is busy. Please retry.")
