import os
from dotenv import load_dotenv
from langchain_mistralai import ChatMistralAI

# Load environment variables
load_dotenv()

def get_mistral_llm(
    temperature: float = 0.0,
    max_tokens: int | None = None,
):
    """
    Returns a configured Mistral LLM client.
    """

    api_key = os.getenv("MISTRAL_API_KEY")
    model_name = "ministral-8b-2512"

    if not api_key:
        raise ValueError(
            "MISTRAL_API_KEY not found in environment variables."
        )

    llm = ChatMistralAI(
        model=model_name,
        temperature=temperature,
        max_tokens=max_tokens,
        api_key=api_key,
    )

    return llm


minstral = get_mistral_llm()

if __name__ == "__main__":
    llm = get_mistral_llm()

    response = llm.invoke(
        "Explain LangGraph in one sentence."
    )

    print(response.content)