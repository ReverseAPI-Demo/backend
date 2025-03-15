# Backend

This is the FastAPI backend for the HAR File API Analyzer tool.

## Overview

My backend has 4 main responsibilities:

- HAR file parsing and extraction of API requests
- Using LLM (open ai) to identify the correct API requests
- Generates curl commands for the identified requests
- Executing API requests

## Project Structure

- `main.py` - Entry point with the fastapi app.
- `app/`
  - `services/` - Contains the service classes:
    - `HarParserService` - Extracts API requests from .har files
    - `LLMService` - Handles ai request identification
    - `CurlGeneratorService` - Generates curl commands
  - `routes/` - API endpoints
  - `models/` - Models for requests (although I only ended up making one, forgot to make the other one)

## API Endpoints

- `GET /api/health` - Health check endpoint
- `POST /api/process-har` - Main endpoint that processes HAR files
- `POST /api/execute-request` - Execute endpoint for executing API requests

## How to Run

1. Install dependencies: `pip install -r requirements.txt`
2. Set environment variable for OPENAI_API_KEY
3. Run the server: `fastapi run main.py`

## Note

- To prevent token overuse, I tried to limit the size of the HAR file in the frontend and also removed a lot of the extra headers/details from the har request before sending to llm
