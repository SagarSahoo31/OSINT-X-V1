"""Vercel Serverless Python entrypoint for OSINT-X FastAPI."""

import sys
import os

# Add backend directory to Python path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKEND_DIR = os.path.join(ROOT_DIR, "backend")

if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

# Import the configured FastAPI app from OSINT-X backend
from app.main import app

# Vercel ASGI Handler
app_handler = app
