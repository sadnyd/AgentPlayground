import os
from typing import Any, Callable, Awaitable
from langchain.agents.middleware import AgentMiddleware, ToolCallRequest # type:ignore
from langchain_core.messages import ToolMessage

class DatetimeAuthMiddleware(AgentMiddleware):
    """
    Middleware that enforces simple conversational authentication 
    for the get_current_datetime tool.
    """

    def _check_auth(self, request: ToolCallRequest) -> bool:
        # Check if the tool being called is get_current_datetime
        if request.tool_call.get("name") != "get_current_datetime":
            return True

        # Check the conversation history for the password
        messages = request.state.get("messages", [])
        expected_password = os.getenv("ADMIN_PASSWORD", "admin")
        
        # Iterate in reverse to check most recent messages first
        for msg in reversed(messages):
            if msg.type == "human" and msg.content:
                if expected_password in str(msg.content):
                    return True
        
        return False

    def wrap_tool_call(
        self,
        request: ToolCallRequest,
        handler: Callable[[ToolCallRequest], Any],
    ) -> Any:
        if not self._check_auth(request):
            return ToolMessage(
                content="Permission denied: You must ask the user for the password to access the datetime tool.",
                tool_call_id=request.tool_call["id"],
                status="error"
            )
            
        return handler(request)

    async def awrap_tool_call(
        self,
        request: ToolCallRequest,
        handler: Callable[[ToolCallRequest], Awaitable[Any]],
    ) -> Any:
        if not self._check_auth(request):
            return ToolMessage(
                content="Permission denied: You must ask the user for the password to access the datetime tool.",
                tool_call_id=request.tool_call["id"],
                status="error"
            )
            
        return await handler(request)

# Instantiate the middleware so that discovery.py can load it
datetime_auth = DatetimeAuthMiddleware()
