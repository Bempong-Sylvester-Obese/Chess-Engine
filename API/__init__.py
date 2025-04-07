"""
Chess Engine API Package

This package provides REST API functionality for the chess engine, including:
- FastAPI server implementation
- API endpoints for engine interactions
- WebSocket support for real-time game updates
"""

from fastapi import FastAPI
from .server import create_app
from .endpoints import router

__all__ = ['create_app', 'router'] 