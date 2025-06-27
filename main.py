import logging
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from models.query import QueryRequest
from services.graph_service import trip_planner_app
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()


@app.post("/query")
async def query_travel_agent(query: QueryRequest):
    try:
        logger.info(f"Received query: {query.query}")

        messages = {"messages": [query.query]}
        output = trip_planner_app.invoke(messages)

        if isinstance(output, dict) and "messages" in output:
            final_output = output["messages"][-1].content
        else:
            final_output = str(output)

        return {"answer": final_output}
    except Exception as e:
        logger.exception("Error handling query")
        return JSONResponse(status_code=500, content={"error": str(e)})
