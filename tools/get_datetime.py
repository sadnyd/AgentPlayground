from datetime import datetime
from langchain.tools import tool

@tool
def get_current_datetime() -> str:
    """Get the current date and time."""
    return datetime.now().strftime("%A, %B %d, %Y %I:%M %p")
