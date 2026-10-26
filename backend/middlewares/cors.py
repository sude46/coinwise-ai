from fastapi.middleware.cors import CORSMiddleware
from core.config import settings


def setup_cors(app):
    origins = ["http://localhost:5173", "http://localhost:3000", "http://localhost:8080", "http://127.0.0.1:8080"]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["Authorization"],
    )
