import json
import os

from datetime import datetime, timezone
from typing import Literal

from langchain.tools import tool


SCRATCHPAD_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..",
    "scratchpad.json",
)
SCRATCHPAD_PATH = os.path.normpath(SCRATCHPAD_PATH)


SuggestionCategory = Literal[
    "new_tool",
    "logic_flow",
    "system_prompt",
    "middleware",
    "capability_gap",
    "other",
]


def _load_scratchpad() -> list[dict]:
    if os.path.exists(SCRATCHPAD_PATH):
        with open(SCRATCHPAD_PATH, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []


def _save_scratchpad(entries: list[dict]) -> None:
    with open(SCRATCHPAD_PATH, "w", encoding="utf-8") as f:
        json.dump(entries, f, indent=2, ensure_ascii=False)


@tool
def scratchpad_suggest(
    category: str,
    title: str,
    description: str,
    priority: str = "medium",
) -> str:
    """
    Record a self-improvement suggestion into the agent scratchpad.

    Use this tool whenever you identify something that would make you more
    capable, accurate, or efficient. Be specific and actionable.

    Args:
        category: One of
            new_tool | logic_flow | system_prompt |
            middleware | capability_gap | other

        title:
            Short (<10 words) summary of the suggestion.

        description:
            Detailed explanation of what is missing,
            why it matters, and how it could be implemented.

        priority:
            low | medium | high
    """

    valid_categories = {
        "new_tool",
        "logic_flow",
        "system_prompt",
        "middleware",
        "capability_gap",
        "other",
    }

    valid_priorities = {"low", "medium", "high"}

    category = category.strip().lower()
    priority = priority.strip().lower()

    if category not in valid_categories:
        return (
            f"Invalid category '{category}'. "
            f"Choose from: {', '.join(sorted(valid_categories))}."
        )

    if priority not in valid_priorities:
        return (
            f"Invalid priority '{priority}'. "
            "Choose from: low, medium, high."
        )

    entries = _load_scratchpad()

    suggestion_id = f"SUG-{len(entries) + 1:04d}"

    entry = {
        "id": suggestion_id,
        "category": category,
        "title": title.strip(),
        "description": description.strip(),
        "priority": priority,
        "status": "open",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    entries.append(entry)
    _save_scratchpad(entries)

    return (
        f"💡 Suggestion recorded as {suggestion_id}.\n"
        f"  Category : {category}\n"
        f"  Priority : {priority}\n"
        f"  Title    : {title}"
    )


@tool
def scratchpad_read(
    category: str = "all",
    status: str = "open",
) -> str:
    """
    Read suggestions from the agent scratchpad.

    Args:
        category:
            Filter by category, or 'all'.

        status:
            open | resolved | all
    """

    entries = _load_scratchpad()

    if not entries:
        return (
            "The scratchpad is empty — "
            "no suggestions recorded yet."
        )

    filtered = [
        e
        for e in entries
        if (
            category == "all"
            or e.get("category") == category.lower()
        )
        and (
            status == "all"
            or e.get("status") == status.lower()
        )
    ]

    if not filtered:
        return (
            f"No suggestions found for "
            f"category='{category}' "
            f"status='{status}'."
        )

    lines = [
        f"Agent Scratchpad — {len(filtered)} suggestion(s):\n"
    ]

    for e in filtered:
        lines.append(
            f"[{e['id']}] "
            f"({e['priority'].upper()}) "
            f"[{e['category']}] "
            f"{e['title']}\n"
            f"  Status : {e['status']}\n"
            f"  Created: {e['created_at']}\n"
            f"  Detail : {e['description']}\n"
        )

    return "\n".join(lines)


@tool
def scratchpad_resolve(suggestion_id: str) -> str:
    """
    Mark a scratchpad suggestion as resolved.

    Args:
        suggestion_id:
            The ID of the suggestion to resolve
            (e.g. SUG-0001).
    """

    entries = _load_scratchpad()

    suggestion_id = suggestion_id.strip().upper()

    for entry in entries:
        if entry["id"] == suggestion_id:

            if entry["status"] == "resolved":
                return (
                    f"{suggestion_id} is already "
                    "marked as resolved."
                )

            entry["status"] = "resolved"
            entry["resolved_at"] = (
                datetime.now(timezone.utc).isoformat()
            )

            _save_scratchpad(entries)

            return (
                f"✅ {suggestion_id} marked as resolved."
            )

    return (
        f"No suggestion found with ID "
        f"'{suggestion_id}'."
    )