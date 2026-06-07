# 🤖 Agent Playground


Welcome to the **Agent Playground**! This is a Streamlit-based web application designed to act as a dynamic, interactive playground for building, testing, and interacting with custom LangChain agents.

## 🌟 Features

- **Interactive UI**: A rich Streamlit interface with chat history, streaming responses, and an intuitive sidebar for configuration.
- **Dynamic Component Discovery**: Automatically scans your workspace for custom agents, models (`clients/`), tools (`tools/`), middleware (`middleware/`), and checkpointers. This allows you to easily plug and play with different components without touching the core orchestrator code.
- **Observability Built-in**: Integrated with **Phoenix** for OpenTelemetry (OTEL) tracing out-of-the-box (`phoenix.otel`), providing deep visibility into your agent's thought processes and tool executions.
- **Modular Architecture**: 
  - `app.py`: A thin orchestrator.
  - `ui/`: Contains all the logic for component discovery, sidebar rendering, agent factory caching, chat handling, and streaming output.
  - `agents/`: Drop in your custom LangGraph or LangChain agents here.
  - `tools/`: Build custom tools (e.g., weather lookup, web search) and they will be auto-discovered.

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- `pip` or your preferred Python package manager.

### Installation

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd AgentPlayground
   ```

2. **Set up a virtual environment:**
   ```bash
   python -m venv venv
   # On Windows
   .\venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies:**
   *(Assuming there's a `requirements.txt` or you can install via `pip`)*
   ```bash
   pip install streamlit langchain langchain-core python-dotenv arize-phoenix[experimental]
   ```

4. **Environment Variables:**
   Create a `.env` file in the root of the project and add your necessary API keys (e.g., OpenAI, Anthropic, or Phoenix settings).
   ```env
   OPENAI_API_KEY=your_openai_api_key
   # Add other required API keys here
   ```

## 🛠️ Usage

Run the Streamlit app:

```bash
streamlit run app.py
```

This will open the Agent Playground in your default web browser (typically at `http://localhost:8501`). You can use the sidebar to select different models, adjust parameters, and choose which agent to chat with.

## 📁 Project Structure

- `app.py`: The main Streamlit entrypoint.
- `ui/`: UI components and core business logic (logging, discovery, chat rendering, sidebar).
- `agents/`: Directory for custom LangChain agents (e.g., `test_create_agent.py`).
- `tools/`: Directory for custom tools (currently includes `web_search.py`, `weather.py`, `get_datetime.py`, `agent_scratchpad.py`).
- `prompts/`: Store your custom system prompts.
- `clients/`: Directory for model client integrations.
- `middleware/`: Directory for custom AgentMiddleware.
- `tests/`: Additional directories for tests.

## 🤝 Contributing

Feel free to fork the repository and submit pull requests. Add your own custom tools to the `tools/` directory and custom agents to `agents/` to extend the playground's capabilities!
