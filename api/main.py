# api/main.py
import logging
from fastapi import FastAPI
from api.routes import router as trip_router
from core.config import settings  # To ensure settings are loaded

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Advanced Trip Planner API",
    description="The backend for the best trip planner on Earth.",
    version="1.0.0",
)

app.include_router(trip_router, prefix="/api")


@app.get("/")
def read_root():
    return {"message": "Welcome to the Trip Planner API"}


# To run: uvicorn api.main:app --reload
