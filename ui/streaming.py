"""
ui.streaming
~~~~~~~~~~~~

Streaming execution loop and rendering helpers.

Exports:
    run_streaming()              - drives agent.stream() and renders live UI
    render_internals_expander()  - renders the collapsed debug expander for history replay
"""

import json
from datetime import datetime, timezone
from typing import Any

import streamlit as st


# ------------------------------------------------------------------
# JSON helper
# ------------------------------------------------------------------

def _safe_json(obj: Any) -> str:
    """JSON-serialize obj, falling back to repr() for non-serializable types."""

    def _default(o: Any) -> Any:
        if hasattr(o, "model_dump"):
            return o.model_dump()
        if hasattr(o, "dict"):
            return o.dict()
        return repr(o)

    try:
        return json.dumps(obj, indent=2, default=_default)
    except Exception:
        return repr(obj)


# ------------------------------------------------------------------
# Tool card renderer
# ------------------------------------------------------------------

def _render_tool_card(
    tool_name: str,
    tool_input: Any,
    tool_output: Any | None,
    placeholder,
) -> None:
    """Render a tool call card into a placeholder."""

    status = "⏳ running..." if tool_output is None else "✅ done"

    input_str = (
        _safe_json(tool_input)
        if isinstance(tool_input, (dict, list))
        else str(tool_input)
    )

    output_str = (
        str(tool_output)
        if tool_output is not None
        else "_waiting_"
    )

    md = (
        f"### 🔧 Tool call: `{tool_name}` — {status}\n\n"
        f"<details><summary>Input</summary>\n\n```json\n{input_str}\n```\n</details>\n\n"
        f"<details {'open' if tool_output else ''}><summary>Output</summary>\n\n"
        f"{output_str}\n\n</details>"
    )

    placeholder.markdown(md, unsafe_allow_html=True)


# ------------------------------------------------------------------
# Internals expander
# ------------------------------------------------------------------

def render_internals_expander(internals: dict) -> None:
    """Render the collapsed 'How it reasoned' expander from stored internals."""

    steps = internals.get("steps", [])
    tool_calls = internals.get("tool_calls", [])
    event_log = internals.get("event_log", [])

    label_parts = []

    if steps:
        label_parts.append(" ➜ ".join(f"`{s}`" for s in steps))

    if tool_calls:
        names = ", ".join(f"`{t['name']}`" for t in tool_calls)
        label_parts.append(f"🔧 {names}")

    label = (
        "🔍 " + (" · ".join(label_parts))
        if label_parts
        else "See internal workings"
    )

    with st.expander(label, expanded=False):

        if steps:
            st.markdown(
                "**Node steps:** "
                + " ➜ ".join(f"`{s}`" for s in steps)
            )
            st.divider()

        if tool_calls:
            st.markdown("**Tool calls:**")

            for tc in tool_calls:
                inp = (
                    _safe_json(tc["input"])
                    if isinstance(tc["input"], (dict, list))
                    else str(tc["input"])
                )

                out = (
                    str(tc["output"])
                    if tc["output"] is not None
                    else "_no output_"
                )

                with st.container(border=True):
                    st.markdown(f"### 🔧 **{tc['name']}**")

                    col_i, col_o = st.columns(2)

                    with col_i:
                        st.markdown("**Input**")
                        st.code(inp, language="json")

                    with col_o:
                        st.markdown("**Output**")
                        st.markdown(out)

            st.divider()

        if event_log:
            _render_event_log(event_log)


# ------------------------------------------------------------------
# Event log renderer
# ------------------------------------------------------------------

def _render_event_log(event_log: list) -> None:
    """Render the raw event log as color-coded cards."""

    _MODE_COLORS = {
        "messages": ("#1a6b3c", "#d4edda"),
        "updates": ("#7a4f00", "#fff3cd"),
        "tasks": ("#0c4a8a", "#cce5ff"),
        "debug": ("#5a2d82", "#e8d5f5"),
    }

    _entries_to_show = event_log[-300:]

    cards_html = ""

    for idx, entry in enumerate(_entries_to_show, 1):

        if isinstance(entry, dict):
            mode_val = entry.get("mode", "?")
            ts_val = entry.get("ts", "")
            raw_data = entry.get("data", "")
        else:
            raw_str = str(entry)
            mode_val = (
                raw_str[1:raw_str.index("]")]
                if raw_str.startswith("[") and "]" in raw_str
                else "?"
            )
            ts_val = ""
            raw_data = raw_str

        fg, bg = _MODE_COLORS.get(
            mode_val,
            ("#333", "#f0f0f0"),
        )

        safe_data = (
            raw_data
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
        )

        cards_html += (
            f"<div style='border-left: 4px solid {fg}; background-color: {bg}; "
            f"padding: 8px; margin-bottom: 8px; border-radius: 4px;'>"
            f"<div style='font-size: 0.8em; color: {fg}; margin-bottom: 4px; font-family: monospace;'>"
            f"<b>[{mode_val}]</b> <span style='opacity: 0.7;'>{ts_val}</span></div>"
            f"<pre style='margin: 0; font-size: 0.85em; background: transparent; "
            f"border: none; padding: 0; color: #333; white-space: pre-wrap; word-wrap: break-word;'>"
            f"{safe_data}</pre></div>"
        )

    with st.expander(
        f"📜 Raw event log ({len(event_log)} entries)",
        expanded=False,
    ):
        st.markdown(
            f"<div style='max-height:420px;overflow-y:auto;padding-right:4px;'>{cards_html}</div>",
            unsafe_allow_html=True,
        )


# ------------------------------------------------------------------
# Main streaming runner
# ------------------------------------------------------------------

def run_streaming(
    agent,
    user_message: str,
    thread_id: str,
    stream_placeholder,
) -> tuple[str, dict]:

    config = {
        "configurable": {
            "thread_id": thread_id,
        }
    }

    live = stream_placeholder.container()

    steps_ph = live.empty()
    token_ph = live.empty()

    final_text = ""
    token_buf = ""
    updates_text = ""

    steps: list[str] = []

    active_tools: dict[str, dict] = {}

    event_log: list[dict] = []

    def _refresh_steps():
        if steps:
            steps_ph.markdown(
                "**Steps:** "
                + " ➜ ".join(f"`{s}`" for s in steps)
            )

    for mode, data in agent.stream(
        {"messages": [{"role": "user", "content": user_message}]},
        config=config,
        stream_mode=["messages", "updates", "tasks", "debug"],
    ):

        event_log.append(
            {
                "mode": mode,
                "data": _safe_json(data),
                "ts": datetime.now(timezone.utc)
                .strftime("%H:%M:%S.%f")[:-3],
            }
        )

        if mode == "messages":
            chunk, metadata = data
            
            content_str = ""
            if hasattr(chunk, "content") and chunk.content:
                if isinstance(chunk.content, str):
                    content_str = chunk.content
                elif isinstance(chunk.content, list):
                    content_str = "".join(b.get("text", "") if isinstance(b, dict) else (b if isinstance(b, str) else "") for b in chunk.content)
            
            if content_str:
                token_buf += content_str
                token_ph.markdown(token_buf + "▌")
            
            # Record tool calls if any
            if hasattr(chunk, "tool_calls") and chunk.tool_calls:
                for tc in chunk.tool_calls:
                    tc_id = tc.get("id")
                    if tc_id and tc_id not in active_tools:
                        active_tools[tc_id] = {
                            "name": tc.get("name", "Unknown"),
                            "input": tc.get("args", {}),
                            "output": None
                        }
                        
        elif mode == "updates":
            for node_name, state in data.items():
                if node_name not in steps:
                    steps.append(node_name)
                    _refresh_steps()
                
                if isinstance(state, dict) and "messages" in state:
                    messages = state["messages"]
                    if messages:
                        last_msg = messages[-1]
                        if getattr(last_msg, "type", "") == "tool":
                            tc_id = getattr(last_msg, "tool_call_id", "")
                            if tc_id in active_tools:
                                active_tools[tc_id]["output"] = last_msg.content
                        elif getattr(last_msg, "type", "") == "ai":
                            if not token_buf and last_msg.content:
                                c = last_msg.content
                                if isinstance(c, list):
                                    c = "".join(b.get("text", "") if isinstance(b, dict) else (b if isinstance(b, str) else "") for b in c)
                                updates_text = c

    if token_buf:
        final_text = token_buf
    elif updates_text:
        final_text = updates_text

    stream_placeholder.empty()

    tool_call_records = [
        {
            "name": v["name"],
            "input": v["input"],
            "output": v["output"],
        }
        for v in active_tools.values()
    ]

    internals = {
        "steps": steps,
        "tool_calls": tool_call_records,
        "event_log": event_log,
    }

    return final_text, internals