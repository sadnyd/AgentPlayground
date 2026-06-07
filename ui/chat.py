from typing import Any

import streamlit as st #type:ignore

from ui.agent_factory import build_agent
from ui.logging_setup import _log_exc
from ui.streaming import render_internals_expander, run_streaming


def render_chat_history() -> None:
    """Render all messages in session_state.chat_history."""

    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            if msg.get("content"):
                st.markdown(msg["content"])

            if msg["role"] == "assistant" and msg.get("internals"):
                render_internals_expander(msg["internals"])


def handle_user_input(
    registry: dict[str, Any],
    config: dict[str, Any],
) -> None:
    """
    Handle st.chat_input, build agent,
    stream response, and store in history.

    Args:
        registry:
            The discovery registry dict.

        config:
            The sidebar config dict
            (model, tools, middleware, etc.).
    """

    user_input = st.chat_input("Ask the agent something...")

    if not user_input:
        return

    selected_tools = config["tools"]
    selected_model = config["model"]
    selected_checkpointer = config["checkpointer"]

    if not selected_tools:
        st.warning(
            "⚠️ No tools selected — the agent will respond "
            "without tool access."
        )

    if not selected_model or not selected_checkpointer:
        st.error(
            "❌ Select a model and checkpointer "
            "before sending a message."
        )
        st.stop()

    # Show user bubble immediately
    st.session_state.chat_history.append(
        {
            "role": "user",
            "content": user_input,
            "internals": None,
        }
    )

    with st.chat_message("user"):
        st.markdown(user_input)

    # Build (or retrieve cached) agent
    bust = st.session_state.get("discover_bust", 0)

    try:
        agent = build_agent(
            model_key=selected_model,
            tool_keys=tuple(selected_tools),
            middleware_keys=tuple(config["middleware"]),
            checkpointer_key=selected_checkpointer,
            agent_name=config["agent_name"],
            system_prompt=config["system_prompt"],
            cache_bust=bust,
        )

    except Exception as exc:
        _log_exc(
            "build_agent (UI)",
            exc,
            model_key=selected_model,
            tool_keys=tuple(selected_tools),
            middleware_keys=tuple(config["middleware"]),
            checkpointer_key=selected_checkpointer,
            agent_name=config["agent_name"],
        )

        st.error(f"❌ Failed to build agent: {exc}")
        st.stop()

    # Stream the response live, then render clean output + expander
    with st.chat_message("assistant"):
        stream_ph = st.empty()

        try:
            response, internals = run_streaming(
                agent=agent,
                user_message=user_input,
                thread_id=st.session_state.thread_id,
                stream_placeholder=stream_ph,
            )

        except Exception as exc:  # noqa: BLE001
            _log_exc(
                "run_streaming (UI)",
                exc,
                thread_id=st.session_state.thread_id,
                user_message=user_input,
                model_key=selected_model,
            )

            response = f"❌ **Error:** {exc}"
            internals = {}

            stream_ph.empty()
            st.error(response)

        # Final clean render
        if response:
            st.markdown(response)

        if internals:
            render_internals_expander(internals)

    st.session_state.chat_history.append(
        {
            "role": "assistant",
            "content": response,
            "internals": internals,
        }
    )
