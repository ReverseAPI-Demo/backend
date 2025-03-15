from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import app as api_router

app = FastAPI(
    title="HAR Parser API",
    description="API for reverse engineering API requests from HAR files",
    version="1.0.0",
)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.mount("/", api_router)
