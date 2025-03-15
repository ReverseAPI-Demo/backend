from fastapi import FastAPI
from app.api.routes import app as api_router

app = FastAPI(
    title="HAR Parser API",
    description="API for reverse engineering API requests from HAR files",
    version="1.0.0",
)

app.mount("/", api_router)
