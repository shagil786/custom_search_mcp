#!/bin/bash
# Start the MCP FastAPI server on Render

# Activate virtual environment if present
if [ -d ".venv" ]; then
  source .venv/bin/activate
fi

# Start the server
uvicorn server:app --host 0.0.0.0 --port 8000