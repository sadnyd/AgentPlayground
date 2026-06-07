import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from langgraph.checkpoint.memory import InMemorySaver #type:ignore
from langchain_core.utils.uuid import uuid7 #type:ignore
from langchain.agents import create_agent
from tools.weather import get_weather
from tools.web_search import web_search_ddg
from clients.minstral import get_mistral_llm
# from middleware import dynamic_model_selection
from prompts.default_system_prompt import DEFAULT_SYSTEM_PROMPT



agent = create_agent(
    # Apart from create_agent, try different agent types
    # with the same tools and prompts.
    model=get_mistral_llm(),
    tools=[get_weather, web_search_ddg],
    system_prompt=DEFAULT_SYSTEM_PROMPT,
    # middleware=[dynamic_model_selection],
    name="FirstAgent",
    checkpointer=InMemorySaver(),

)

config = {
    "configurable": {
        "thread_id": str(uuid7())
    }
}

result = agent.invoke(
    {
        "messages": [
            {
                "role": "user",
                "content": (
                    "What's the weather in Bangalore? "
                    "Do a web search for a fun fact about that weather."
                ),
            }
        ]
    },
    config=config,
)

print(result["messages"][-1].content_blocks)

# Follow-up turn on the same conversation:
# Reuse the same thread_id to keep history.

result = agent.invoke(
    {
        "messages": [
            {
                "role": "user",
                "content": "What about the weather tomorrow in Bangalore?"
            }
        ]
    },
    config=config,
)

print(result["messages"][-1].content_blocks)