from langchain.tools import tool


@tool("calculator")
def calculator(expression: str) -> str:
    """Performs basic arithmetic calculations."""
    try:
        # Using a safe eval
        result = eval(expression, {"__builtins__": {}}, {})
        return f"Result: {result}"
    except Exception as e:
        return f"Calculation error: {e}"
