from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
load_dotenv()
from rest import sources, research



app = FastAPI(title="BoWattApp")

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
