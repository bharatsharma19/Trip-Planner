# database/database.py
from .models import TripPlan

# In-memory database for simplicity.
# For a production app, replace this with a real database connection.
# from sqlmodel import create_engine, SQLModel, Session
# from core.config import settings
# engine = create_engine(settings.DATABASE_URL)
# def create_db_and_tables():
#     SQLModel.metadata.create_all(engine)

db: dict[str, TripPlan] = {}


def get_trip_plan(session_id: str) -> TripPlan:
    """Retrieves or creates a trip plan for a given session."""
    if session_id not in db:
        db[session_id] = TripPlan(session_id=session_id)
    return db[session_id]


def save_trip_plan(plan: TripPlan):
    """Saves the trip plan to the database."""
    db[plan.session_id] = plan
