# api/routes.py
import logging
from fastapi import APIRouter, HTTPException
from services.graph_service import run_graph
from database.models import QueryRequest

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/query")
async def query_travel_agent(request: QueryRequest):
    try:
        logger.info(f"Received query for session {request.session_id}: {request.query}")

        if not request.query or not request.session_id:
            raise HTTPException(
                status_code=400, detail="Query and session_id are required."
            )

        result = run_graph(request)

        if not result:
            raise HTTPException(
                status_code=404, detail="No results found for the given query."
            )

        # Log the result for debugging
        logger.debug(f"Result for session {request.session_id}: {result}")

        return result

    except Exception as e:
        logger.exception("Error handling query")
        raise HTTPException(status_code=500, detail=str(e))
