from pathlib import Path
from dotenv import load_dotenv

# 🔥 ABSOLUTE path to .env (this is the key)
BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"

load_dotenv(dotenv_path=ENV_PATH)

from fastapi import FastAPI
from modules.ai.ai_routes import router as ai_router
from modules.ai.memory_routes import router as memory_router

app = FastAPI(title="PromptLearn AI Service")

app.include_router(ai_router)
app.include_router(memory_router)



# I want you to explain from first principles how my Python AI backend (FastAPI + Uvicorn) is structured, started, and executed at runtime.

# Context:

# I am coming from an Express / Node.js background

# I built a separate Python AI service for PromptLearn

# The project uses:
   
# FastAPI

# Uvicorn

# src/-based project layout

# Makefile with make dev

# .venv virtual environment

# absolute imports like modules.* and shared.*

# Explain step by step, in depth:

# What happens when I run make dev

# What uvicorn main:app --reload --app-dir src actually does internally

# How Python decides where to import modules from (why src/ matters)

# Why mixed imports (src.* vs modules.*) break the app

# How FastAPI discovers routes and builds /docs

# How request → controller → service → response flows

# Why this architecture is production-safe and scalable

# How this maps mentally to Express (server.ts, routes, controllers, services)

# Common mistakes (like dots in filenames, reload subprocess issues)

# How this setup prepares the system for AI features like memory and RAG

# Do not summarize quickly.
# Explain like I’m learning to become a backend + AI systems engineer, with:

# clear mental models

# comparisons to Node.js

# internal execution order

# why each decision matters

# Treat this as a deep technical walkthrough, not a tutorial.