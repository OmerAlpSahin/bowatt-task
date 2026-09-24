from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
load_dotenv()
from rest import sources, research
import asyncio
from contextlib import asynccontextmanager

from ingestion.embeddings import get_model
from ingestion.vector_store import get_collection


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Warm up shared resources once, before any request can race to create them
    await asyncio.to_thread(get_model)
    await asyncio.to_thread(get_collection)
    yield


app = FastAPI(title="BoWattApp", lifespan=lifespan)

origins = [
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["POST"],
    allow_headers=["Content-Type"],
)

@app.get("/health")
async def main():
    return {"status": "ok"}



app.include_router(sources.router)
app.include_router(research.router)
