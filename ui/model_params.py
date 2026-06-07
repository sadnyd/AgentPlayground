"""
ui.model_params
~~~~~~~~~~~~~~~

Per-model parameter schemas and the sidebar settings renderer.

Exports:
    MODEL_PARAM_SCHEMAS      - dict mapping model_key -> list of field specs
    render_model_settings()  - renders the expander and returns bind()-ready overrides
"""

import streamlit as st

# --- Schema definitions -------------------------------------------------------
# spec keys:
#   key      - kwarg name for .bind() (prefix "_reasoning_" = nested in reasoning dict)
#   label    - human-readable label
#   type     - "float"|"int"|"bool"|"select"|"int_or_none"
#   default  - shown when unchanged
#   min/max  - for numeric types
#   step     - slider step
#   options  - for "select" type
#   help     - tooltip

_F = dict  # alias for readability

MODEL_PARAM_SCHEMAS: dict[str, list[dict]] = {

    "gpt_4o": [
        _F(
            key="temperature",
            label="Temperature",
            type="float",
            default=1.0,
            min=0.0,
            max=2.0,
            step=0.05,
            help="Randomness (0=deterministic, 2=max creative). Alter either temperature OR top_p, not both.",
        ),
        _F(
            key="top_p",
            label="Top-p",
            type="float",
            default=1.0,
            min=0.0,
            max=1.0,
            step=0.05,
            help="Nucleus sampling. Alter either top_p OR temperature, not both.",
        ),
        _F(
            key="max_tokens",
            label="Max tokens",
            type="int_or_none",
            default=None,
            min=1,
            max=16384,
            help="Hard cap on output tokens. None = model decides (up to 16384).",
        ),
        _F(
            key="presence_penalty",
            label="Presence penalty",
            type="float",
            default=0.0,
            min=-2.0,
            max=2.0,
            step=0.1,
            help="Positive = encourage new topics. Range -2 to +2.",
        ),
        _F(
            key="frequency_penalty",
            label="Frequency penalty",
            type="float",
            default=0.0,
            min=-2.0,
            max=2.0,
            step=0.1,
            help="Positive = reduce repeated tokens. Range -2 to +2.",
        ),
        _F(
            key="n",
            label="Completions (n)",
            type="int",
            default=1,
            min=1,
            max=8,
            help="Number of independent completions. Values >1 multiply cost.",
        ),
        _F(
            key="seed",
            label="Seed",
            type="int_or_none",
            default=None,
            min=0,
            max=2**31,
            help="Integer for reproducibility. None = non-deterministic.",
        ),
        _F(
            key="logprobs",
            label="Log-probs",
            type="bool",
            default=False,
            help="Return log-probabilities for each output token.",
        ),
        _F(
            key="top_logprobs",
            label="Top log-probs",
            type="int_or_none",
            default=None,
            min=0,
            max=20,
            help="Top-N candidate tokens per position. Requires logprobs=True.",
        ),
        _F(
            key="max_retries",
            label="Max retries",
            type="int",
            default=6,
            min=0,
            max=20,
            help="Automatic retries on transient failures.",
        ),
        _F(
            key="stream_usage",
            label="Stream usage stats",
            type="bool",
            default=True,
            help="Append token-usage chunk to every streaming response.",
        ),
    ],

    "gpt_5": [
        _F(
            key="max_tokens",
            label="Max tokens",
            type="int_or_none",
            default=None,
            min=1,
            max=32768,
            help="Hard cap on total output tokens (includes reasoning).",
        ),
        _F(
            key="service_tier",
            label="Service tier",
            type="select",
            default="default",
            options=["default", "flex"],
            help='"default" = standard latency. "flex" = lower-priority (cheaper).',
        ),
        _F(
            key="store",
            label="Store response",
            type="bool",
            default=False,
            help="Opt in to Azure Stored Completions / fine-tuning.",
        ),
        _F(
            key="max_retries",
            label="Max retries",
            type="int",
            default=6,
            min=0,
            max=20,
            help="Automatic retries on transient failures.",
        ),
        _F(
            key="stream_usage",
            label="Stream usage stats",
            type="bool",
            default=True,
            help="Append token-usage chunk to every streaming response.",
        ),
    ],

    "gpt_5_1": [
        _F(key="temperature", label="Temperature", type="float",
           default=1.0, min=0.0, max=2.0, step=0.05),

        _F(key="top_p", label="Top-p", type="float",
           default=1.0, min=0.0, max=1.0, step=0.05),

        _F(key="max_tokens", label="Max tokens",
           type="int_or_none", default=None, min=1, max=65536),

        _F(key="presence_penalty", label="Presence penalty",
           type="float", default=0.0, min=-2.0, max=2.0, step=0.1),

        _F(key="frequency_penalty", label="Frequency penalty",
           type="float", default=0.0, min=-2.0, max=2.0, step=0.1),

        _F(key="n", label="Completions (n)",
           type="int", default=1, min=1, max=8),

        _F(key="seed", label="Seed",
           type="int_or_none", default=None, min=0, max=2**31),

        _F(key="logprobs", label="Log-probs",
           type="bool", default=False),

        _F(key="top_logprobs", label="Top log-probs",
           type="int_or_none", default=None, min=0, max=20),

        _F(
            key="service_tier",
            label="Service tier",
            type="select",
            default="default",
            options=["default", "flex"],
        ),

        _F(key="store", label="Store response",
           type="bool", default=False),

        _F(key="max_retries", label="Max retries",
           type="int", default=6, min=0, max=20),

        _F(key="stream_usage", label="Stream usage stats",
           type="bool", default=True),
    ],

    "gpt_5_1_codex": [
        _F(
            key="_reasoning_effort",
            label="Reasoning effort",
            type="select",
            default="medium",
            options=["low", "medium", "high"],
            help='"low" = fast/cheap. "medium" = balanced. "high" = deepest, slowest, most expensive.',
        ),
        _F(
            key="_reasoning_summary",
            label="Reasoning summary",
            type="select",
            default="auto",
            options=["auto", "detailed"],
            help='"auto" = model decides. "detailed" = always include full reasoning trace.',
        ),
        _F(
            key="max_tokens",
            label="Max tokens (total)",
            type="int_or_none",
            default=None,
            min=1,
            max=131072,
            help="Budget for BOTH reasoning tokens + visible output.",
        ),
        _F(key="store", label="Store response",
           type="bool", default=False),

        _F(key="max_retries", label="Max retries",
           type="int", default=6, min=0, max=20),

        _F(key="stream_usage", label="Stream usage stats",
           type="bool", default=True),
    ],

    "minstral": [
        _F(
            key="temperature",
            label="Temperature",
            type="float",
            default=0.0,
            min=0.0,
            max=1.0,
            step=0.1,
            help="Randomness (0=deterministic).",
        ),
        _F(
            key="max_tokens",
            label="Max tokens",
            type="int_or_none",
            default=None,
            min=1,
            max=32768,
            help="Hard cap on output tokens.",
        ),
    ],
}

# --- Renderer ----------------------------------------------------------------

def render_model_settings(model_key: str) -> dict:
    """
    Render the model-parameter expander for the currently selected model.
    Returns a bind()-ready overrides dict.
    """

    schema = MODEL_PARAM_SCHEMAS.get(model_key)
    if not schema:
        return {}

    state_key = f"model_cfg_{model_key}"

    if state_key not in st.session_state:
        st.session_state[state_key] = {
            f["key"]: f["default"] for f in schema
        }

    cfg: dict = st.session_state[state_key]

    with st.expander("⚙️ Model parameters", expanded=False):
        for field in schema:
            k = field["key"]
            label = field["label"]
            ftype = field["type"]
            default = field["default"]
            help_ = field.get("help", "")
            wkey = f"_mset_{model_key}_{k}"
            current = cfg.get(k, default)

            if ftype == "float":
                val = st.slider(
                    label,
                    min_value=float(field["min"]),
                    max_value=float(field["max"]),
                    value=float(current),
                    step=float(field.get("step", 0.1)),
                    key=wkey,
                    help=help_,
                )

            elif ftype == "int":
                val = st.slider(
                    label,
                    min_value=int(field["min"]),
                    max_value=int(field["max"]),
                    value=int(current),
                    step=1,
                    key=wkey,
                    help=help_,
                )

            elif ftype == "bool":
                val = st.toggle(
                    label,
                    value=bool(current),
                    key=wkey,
                    help=help_,
                )

            elif ftype == "select":
                opts = field["options"]
                idx = opts.index(current) if current in opts else 0

                val = st.selectbox(
                    label,
                    options=opts,
                    index=idx,
                    key=wkey,
                    help=help_,
                )

            elif ftype == "int_or_none":
                enabled = st.toggle(
                    f"Override {label}",
                    value=(current is not None),
                    key=wkey + "_en",
                    help=help_,
                )

                if enabled:
                    val = st.number_input(
                        label,
                        min_value=int(field.get("min", 1)),
                        max_value=int(field.get("max", 2**31)),
                        value=int(current)
                        if current is not None
                        else int(field.get("min", 1)),
                        step=1,
                        key=wkey + "_v",
                        help=help_,
                    )
                else:
                    val = None

            else:
                val = current

            cfg[k] = val

    st.session_state[state_key] = cfg

    if st.button(
        "🔄 Reset to defaults",
        key=f"_mset_reset_{model_key}",
    ):
        st.session_state[state_key] = {
            f["key"]: f["default"] for f in schema
        }
        st.rerun()

    # Build bind()-ready dict
    overrides: dict = {}

    for field in schema:
        k = field["key"]

        if k.startswith("_reasoning_"):
            continue

        v = cfg.get(k, field["default"])
        overrides[k] = v

    if model_key == "gpt_5_1_codex":
        overrides["reasoning"] = {
            "effort": cfg.get("_reasoning_effort", "medium"),
            "summary": cfg.get("_reasoning_summary", "auto"),
        }

    return overrides