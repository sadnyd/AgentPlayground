"""
ui.logging_setup
~~~~~~~~~~~~~~~~

Centralised logging configuration for the Agent Playground.

Exports:
    ROOT      - project root Path
    logger    - pre-configured Logger instance
    _log_exc  - helper to write detailed error entries
"""

import logging
import traceback

from pathlib import Path


# -------------------------------------------------------------------
# Project root (shared by other ui modules)
# -------------------------------------------------------------------

ROOT: Path = Path(__file__).resolve().parent.parent


# -------------------------------------------------------------------
# Log directory & file
# -------------------------------------------------------------------

_LOG_DIR = ROOT / "logs"
_LOG_DIR.mkdir(exist_ok=True)

_LOG_FILE = _LOG_DIR / "app.log"


# -------------------------------------------------------------------
# Handler & formatter
# -------------------------------------------------------------------

_file_handler = logging.FileHandler(
    _LOG_FILE,
    encoding="utf-8",
)

_file_handler.setLevel(logging.DEBUG)

_file_handler.setFormatter(
    logging.Formatter(
        fmt=(
            "%(asctime)s | %(levelname)-8s | %(name)s\n"
            "  File: %(pathname)s  Line: %(lineno)d\n"
            "  Message: %(message)s\n"
        ),
        datefmt="%Y-%m-%d %H:%M:%S",
    )
)


# -------------------------------------------------------------------
# Logger instance
# -------------------------------------------------------------------

logger = logging.getLogger("agent_playground")
logger.setLevel(logging.DEBUG)

if not logger.handlers:  # avoid duplicate handlers on Streamlit hot-reload
    logger.addHandler(_file_handler)


def _log_exc(
    context: str,
    exc: BaseException,
    **extra,
) -> None:
    """
    Write an elaborate error entry to the log file.

    Each entry includes:
        • UTC timestamp (also in the formatter)
        • Context description (where the error occurred)
        • Exception type + message
        • Full traceback
        • Any extra keyword arguments passed by the caller
    """

    tb = traceback.format_exc()

    extra_lines = ""

    if extra:
        extra_lines = "\n".join(
            f"    {k}: {v!r}"
            for k, v in extra.items()
        )

        extra_lines = (
            f"  Extra context:\n"
            f"{extra_lines}\n"
        )

    logger.error(
        "[%s]\n"
        "  Exception : %s: %s\n"
        "%s"
        "  Traceback :\n%s",
        context,
        type(exc).__name__,
        exc,
        extra_lines,
        tb,
    )