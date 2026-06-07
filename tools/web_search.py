from langchain.tools import tool
from ddgs import DDGS


@tool
def web_search_ddg(query: str) -> str:
    """Search the web using DuckDuckGo and return the top results."""

    try:
        with DDGS() as ddgs:
            results = list(
                ddgs.text(
                    query,
                    max_results=5,
                )
            )

        if not results:
            return "No results found."

        return "\n\n".join(
            f"Title: {r['title']}\n"
            f"URL: {r['href']}\n"
            f"Snippet: {r['body']}"
            for r in results
        )

    except Exception as e:
        return f"Search failed: {e}"