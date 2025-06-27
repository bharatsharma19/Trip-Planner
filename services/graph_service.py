import os
import logging
from agents.agentic_workflow import GraphBuilder

logger = logging.getLogger(__name__)

try:
    # Build the graph once at startup
    graph_builder = GraphBuilder(model_provider="google")
    graph = graph_builder()  # Compiled LangGraph
    trip_planner_app = graph  # Alias for consistency

    # Draw and save Mermaid PNG once
    try:
        png_graph = trip_planner_app.get_graph().draw_mermaid_png()
        graph_path = os.path.join(os.getcwd(), "my_graph.png")
        with open(graph_path, "wb") as f:
            f.write(png_graph)
        logger.info(f"Graph saved as Mermaid PNG at: {graph_path}")
    except Exception as e:
        logger.warning(f"Graph drawing failed: {e}")

except Exception as e:
    logger.exception("Failed to build or save graph at startup")
    raise RuntimeError("Critical: Failed to initialize graph.")
