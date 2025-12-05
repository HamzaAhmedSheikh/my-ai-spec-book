import logging
import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .qdrant_client import qdrant_client_instance

# Load environment variables from the .env file
load_dotenv()


logger = logging.getLogger(__name__)

api_key = os.getenv("OPENAI_API_KEY")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Connect to Qdrant
    logger.info("Connecting to Qdrant...")
    try:
        # Accessing the instance ensures client is initialized and collection created
        _ = qdrant_client_instance.get_client()

        logger.info("Successfully connected to Qdrant and ensured collection exists.")
    except Exception as e:
        logger.error(f"Failed to connect to Qdrant: {e}")
        # Depending on criticality, you might want to raise the exception
        # or have a fallback mechanism. For now, we log it.
    yield
    # Shutdown: No specific cleanup needed for Qdrant client connection currently
    logger.info("FastAPI application shutting down.")


app = FastAPI(title="Physical AI Book RAG Backend", version="0.1.0", lifespan=lifespan)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.computed_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from .routes import chat_router, health_router, index_router

app.include_router(health_router)
app.include_router(chat_router)
app.include_router(index_router)
