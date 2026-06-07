"""
ui.discovery
~~~~~~~~~~~~

Dynamic component discovery for the Agent Playground.

Scans the workspace for:
    - Models         -> clients/
    - Tools          -> tools/
    - Middleware     -> middleware/
    - Checkpointers  -> well-known options

Exports:
    discover()          - cached top-level entry point returning the full registry
    _discover_cached()  - inner cached loader (also used by agent_factory)
"""

import importlib
import sys
import streamlit as st#type:ignore

from pathlib import Path
from types import ModuleType
from typing import Any
from langchain.agents.middleware import AgentMiddleware#type:ignore
from langgraph.checkpoint.memory import InMemorySaver#type:ignore
from ui.logging_setup import ROOT, _log_exc


# Ensure project root is importable
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


# -------------------------------------------------------------------
# Helpers
# -------------------------------------------------------------------

def _iter_module_stems(pkg_dir: str) -> list[str]:
    """Return all non-dunder .py stems inside a package directory."""

    path = ROOT / pkg_dir
    stems = []

    for f in sorted(path.glob("*.py")):
        if f.stem.startswith("_"):
            continue

        stems.append(f.stem)

    return stems


def _load_clients() -> tuple[dict[str, object], list[str]]:
    """
    Import every client module and grab the top-level LLM object
    (same name as stem).
    """

    clients: dict[str, object] = {}
    errors: list[str] = []

    for stem in _iter_module_stems("clients"):
        try:
            mod_name = f"clients.{stem}"

            if mod_name in sys.modules:
                mod = importlib.reload(sys.modules[mod_name])
            else:
                mod = importlib.import_module(mod_name)

            obj = getattr(mod, stem, None)

            if obj is not None:
                clients[stem] = obj

        except Exception as exc:  # noqa: BLE001
            _log_exc(
                f"_load_clients / clients.{stem}",
                exc,
                stem=stem,
            )
            errors.append(f"clients.{stem}: {exc}")

    return clients, errors


def _load_tools() -> tuple[dict[str, object], list[str]]:
    """
    Scan every .py in tools/ and collect @tool-decorated objects.
    """

    result: dict[str, object] = {}
    errors: list[str] = []

    try:
        from langchain_core.tools import BaseTool
    except ImportError:
        BaseTool = None  # type: ignore

    for stem in _iter_module_stems("tools"):

        if "test" in stem:
            continue

        try:
            mod: ModuleType = importlib.import_module(
                f"tools.{stem}"
            )

            for attr_name in dir(mod):

                if attr_name.startswith("_"):
                    continue

                obj = getattr(mod, attr_name)

                is_tool = (
                    (BaseTool is not None and isinstance(obj, BaseTool))
                    or (
                        callable(obj)
                        and hasattr(obj, "name")
                        and hasattr(obj, "invoke")
                    )
                )

                if is_tool and attr_name not in result:
                    result[attr_name] = obj

        except Exception as exc:  # noqa: BLE001
            _log_exc(
                f"_load_tools / tools.{stem}",
                exc,
                stem=stem,
            )
            errors.append(f"tools.{stem}: {exc}")

    return result, errors


def _load_middleware() -> tuple[dict[str, object], list[str]]:
    """
    Import every middleware module and collect
    AgentMiddleware instances.
    """

    mw: dict[str, object] = {}
    errors: list[str] = []

    try:

        _mw_base = AgentMiddleware

    except ImportError:
        _mw_base = None  # type: ignore

    def _is_middleware(obj: object) -> bool:
        if _mw_base is not None and isinstance(obj, _mw_base):
            return True

        return callable(obj) or hasattr(type(obj), "__call__")

    for stem in _iter_module_stems("middleware"):

        try:
            mod: ModuleType = importlib.import_module(
                f"middleware.{stem}"
            )

            obj = getattr(mod, stem, None)

            if obj is not None and _is_middleware(obj):
                mw[stem] = obj
                continue

            for attr_name in dir(mod):

                if attr_name.startswith("_"):
                    continue

                candidate = getattr(mod, attr_name)

                candidate_mod = (
                    getattr(type(candidate), "__module__", "")
                    or getattr(candidate, "__module__", "")
                )

                if (
                    _is_middleware(candidate)
                    and mod.__name__ in candidate_mod
                ):
                    mw[attr_name] = candidate
                    break

        except Exception as exc:  # noqa: BLE001
            _log_exc(
                f"_load_middleware / middleware.{stem}",
                exc,
                stem=stem,
            )

            errors.append(f"middleware.{stem}: {exc}")

    return mw, errors


def _checkpointer_options() -> dict[str, object]:
    """Return known checkpointer options."""

    options: dict[str, object] = {
        "None (no memory)": None
    }

    try:
        options["InMemorySaver (in-process)"] = InMemorySaver()

    except ImportError:
        pass

    return options


# -------------------------------------------------------------------
# Cached discovery
# -------------------------------------------------------------------

@st.cache_resource(
    show_spinner="Discovering workspace components..."
)
def _discover_cached(_bust: int) -> dict[str, Any]:
    """
    Inner cached loader.
    Pass a changing _bust value to invalidate.
    """

    clients, c_errs = _load_clients()
    tools, t_errs = _load_tools()
    middleware, m_errs = _load_middleware()

    return {
        "clients": clients,
        "tools": tools,
        "middleware": middleware,
        "checkpointers": _checkpointer_options(),
        "errors": c_errs + t_errs + m_errs,
    }


def discover() -> dict[str, Any]:
    """
    Top-level discovery entry point.
    Uses session_state bust counter for invalidation.
    """

    bust = st.session_state.get("discover_bust", 0)
    return _discover_cached(bust)