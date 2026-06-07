"""
ui.sidebar
~~~~~~~~~~

Sidebar configuration panel.

Exports:
    render_sidebar(registry) - draws all sidebar widgets, returns config dict.
"""

import ast
import importlib.util as _ilu
import inspect as _inspect
from pathlib import Path
from typing import Any

import streamlit as st

from ui.model_params import render_model_settings


def render_sidebar(registry: dict[str, Any]) -> dict[str, Any]:
    """
    Render the full sidebar and return the current configuration.

    Returns a dict with keys:
        model, tools, middleware, checkpointer,
        agent_name, system_prompt, model_overrides
    """

    with st.sidebar:
        st.header("⚙️ Agent Configuration")

        # Refresh button
        if st.button(
            "🔄 Refresh Components",
            help="Re-scan clients/, tools/, middleware/ folders",
        ):
            st.session_state["discover_bust"] = (
                st.session_state.get("discover_bust", 0) + 1
            )
            st.cache_resource.clear()
            st.rerun()

        # --- Model ----------------------------------------------------
        client_names = list(registry["clients"].keys())

        selected_model = st.selectbox(
            "🧠 Model",
            options=client_names,
            index=0,
            help="Client module stem → maps to a pre-configured AzureChatOpenAI instance.",
        )

        # Per-model parameter settings
        if selected_model:
            render_model_settings(selected_model)

        # --- Tools ----------------------------------------------------
        tool_names = list(registry["tools"].keys())

        def _tool_label(name: str) -> str:
            desc = getattr(
                registry["tools"].get(name),
                "description",
                "",
            ) or ""

            desc = desc.strip().splitlines()[0] if desc.strip() else ""

            return f"{name} — {desc[:90]}" if desc else name

        selected_tools = st.multiselect(
            "🛠 Tools",
            options=tool_names,
            default=[],
            format_func=_tool_label,
            help="Select one or more tools to equip the agent with.",
        )

        # --- Middleware ----------------------------------------------
        mw_names = list(registry["middleware"].keys())

        def _mw_label(name: str) -> str:
            obj = registry["middleware"].get(name)
            doc = ""

            try:
                unwrapped = (
                    _inspect.unwrap(obj)
                    if callable(obj)
                    else obj
                )
                doc = _inspect.getdoc(unwrapped) or ""
            except Exception:
                pass

            if not doc:
                try:
                    spec = _ilu.find_spec(f"middleware.{name}")

                    if spec and spec.origin:
                        src = Path(spec.origin).read_text(
                            encoding="utf-8"
                        )

                        tree = ast.parse(src)

                        for node in ast.walk(tree):
                            if (
                                isinstance(
                                    node,
                                    (
                                        ast.FunctionDef,
                                        ast.AsyncFunctionDef,
                                    ),
                                )
                                and node.name == name
                            ):
                                first = (
                                    node.body[0]
                                    if node.body
                                    else None
                                )

                                if (
                                    isinstance(first, ast.Expr)
                                    and isinstance(
                                        first.value,
                                        ast.Constant,
                                    )
                                ):
                                    doc = (
                                        str(first.value.value)
                                        .strip()
                                    )
                                    break

                except Exception:
                    pass

            first_line = (
                doc.strip().splitlines()[0]
                if doc.strip()
                else ""
            )

            return (
                f"{name} — {first_line[:90]}"
                if first_line
                else name
            )

        selected_middleware = st.multiselect(
            "🔀 Middleware",
            options=mw_names,
            default=[],
            format_func=_mw_label,
            help="Middleware hooks that intercept model calls.",
        )

        # --- Checkpointer --------------------------------------------
        cp_names = list(registry["checkpointers"].keys())

        selected_checkpointer = st.selectbox(
            "💾 Checkpointer",
            options=cp_names,
            index=0 if not cp_names else (1 if len(cp_names) > 1 else 0),
            help="Conversation memory backend.",
        )

        st.divider()

        # --- Agent name & system prompt ------------------------------
        agent_name = st.text_input(
            "🏷 Agent Name",
            value="FirstAgent",
            help="Logical name for the agent instance.",
        )

        system_prompt = st.text_area(
            "📝 System Prompt",
            value="You are a helpful assistant",
            height=140,
            help="The system prompt sent to the model at the start of every conversation.",
        )

        st.divider()

        # --- Thread ID -----------------------------------------------
        col1, col2 = st.columns([3, 1])

        with col1:
            st.caption(
                f"🧵 Thread: {st.session_state.thread_id[:18]}..."
            )

        with col2:
            if st.button(
                "♻️ New",
                help="Start a fresh conversation thread",
            ):
                from langchain_core.utils.uuid import uuid7

                st.session_state.thread_id = str(uuid7())
                st.session_state.chat_history = []
                st.rerun()

        st.divider()
        st.caption(
            "Changes take effect on the **next** message sent."
        )

    return {
        "model": selected_model,
        "tools": selected_tools,
        "middleware": selected_middleware,
        "checkpointer": selected_checkpointer,
        "agent_name": agent_name,
        "system_prompt": system_prompt,
    }