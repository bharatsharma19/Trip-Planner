from langchain.tools import tool


@tool("calculator", return_direct=True)
def calculator(expression: str) -> str:
    """Performs basic arithmetic calculations."""
    try:
        result = eval(expression, {"__builtins__": {}})
        return f"Result: {result}"
    except Exception as e:
        return f"Calculation error: {e}"
