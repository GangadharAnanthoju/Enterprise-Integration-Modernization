"""Structured planning contract for Foundry agent responses.

Foundry can reason over the user's request, but backend execution still needs a
deterministic contract. This module validates the plan shape before later steps
connect it to FastAPI governance and MCP execution.
"""

import json
import re
from dataclasses import dataclass
from typing import Any

from tools.registry import get_tool


CONFIDENCE_LEVELS = {"low", "medium", "high"}


class FoundryPlanContractError(ValueError):
    """Raised when a Foundry response does not match the planning contract."""


@dataclass(frozen=True)
class FoundryActionPlan:
    """Validated structured action plan proposed by the Foundry agent."""

    selected_tool: str | None
    entities: dict[str, str]
    requires_clarification: bool
    clarification_question: str | None
    confidence: str
    reason: str


@dataclass(frozen=True)
class FoundryPlanValidation:
    """Validation result for a Foundry plan against the approved tool registry."""

    selected_tool: str | None
    selected_tool_supported: bool
    missing_entities: list[str]
    ready_for_governance: bool


def parse_foundry_action_plan(response_text: str) -> FoundryActionPlan:
    """Parse and validate a structured Foundry planning response."""

    payload = _load_json_object(response_text)
    required_fields = {
        "selected_tool",
        "entities",
        "requires_clarification",
        "confidence",
        "reason",
    }
    missing_fields = sorted(required_fields - set(payload))
    if missing_fields:
        raise FoundryPlanContractError(
            "Foundry plan is missing required fields: " + ", ".join(missing_fields)
        )

    selected_tool = _optional_string(payload["selected_tool"], "selected_tool")
    if selected_tool is not None and get_tool(selected_tool) is None:
        raise FoundryPlanContractError(f"Foundry selected unsupported tool: {selected_tool}")

    entities = _entities(payload["entities"])
    requires_clarification = _bool(payload["requires_clarification"], "requires_clarification")
    clarification_question = _optional_string(
        payload.get("clarification_question"),
        "clarification_question",
    )
    confidence = _string(payload["confidence"], "confidence").lower()
    if confidence not in CONFIDENCE_LEVELS:
        raise FoundryPlanContractError(
            "Foundry plan confidence must be low, medium, or high."
        )

    reason = _string(payload["reason"], "reason")
    if not reason.strip():
        raise FoundryPlanContractError("Foundry plan reason must not be empty.")

    if requires_clarification and not clarification_question:
        raise FoundryPlanContractError(
            "Foundry plan requires a clarification_question when clarification is required."
        )

    if not requires_clarification and selected_tool is None:
        raise FoundryPlanContractError(
            "Foundry plan must select a tool unless clarification is required."
        )

    return FoundryActionPlan(
        selected_tool=selected_tool,
        entities=entities,
        requires_clarification=requires_clarification,
        clarification_question=clarification_question,
        confidence=confidence,
        reason=reason,
    )


def validate_foundry_action_plan(plan: FoundryActionPlan) -> FoundryPlanValidation:
    """Validate an already parsed Foundry plan against tool required entities."""

    if plan.selected_tool is None:
        return FoundryPlanValidation(
            selected_tool=None,
            selected_tool_supported=True,
            missing_entities=[],
            ready_for_governance=False,
        )

    tool = get_tool(plan.selected_tool)
    if tool is None:
        return FoundryPlanValidation(
            selected_tool=plan.selected_tool,
            selected_tool_supported=False,
            missing_entities=[],
            ready_for_governance=False,
        )

    missing_entities = [
        entity_name
        for entity_name in tool.required_entities
        if entity_name not in plan.entities
    ]
    return FoundryPlanValidation(
        selected_tool=plan.selected_tool,
        selected_tool_supported=True,
        missing_entities=missing_entities,
        ready_for_governance=not plan.requires_clarification and not missing_entities,
    )


def _load_json_object(response_text: str) -> dict[str, Any]:
    json_text = _extract_json_text(response_text)
    try:
        payload = json.loads(json_text)
    except json.JSONDecodeError as exc:
        raise FoundryPlanContractError("Foundry plan response is not valid JSON.") from exc

    if not isinstance(payload, dict):
        raise FoundryPlanContractError("Foundry plan response must be a JSON object.")

    return payload


def _extract_json_text(response_text: str) -> str:
    stripped = response_text.strip()
    fenced_match = re.search(
        r"```(?:json)?\s*(\{.*?\})\s*```",
        stripped,
        flags=re.DOTALL | re.IGNORECASE,
    )
    if fenced_match:
        return fenced_match.group(1)

    start_index = stripped.find("{")
    end_index = stripped.rfind("}")
    if start_index == -1 or end_index == -1 or end_index <= start_index:
        raise FoundryPlanContractError("Foundry plan response must contain a JSON object.")

    return stripped[start_index : end_index + 1]


def _entities(value: Any) -> dict[str, str]:
    if not isinstance(value, dict):
        raise FoundryPlanContractError("Foundry plan entities must be an object.")

    entities: dict[str, str] = {}
    for key, entity_value in value.items():
        if not isinstance(key, str) or not isinstance(entity_value, str):
            raise FoundryPlanContractError(
                "Foundry plan entities must use string keys and string values."
            )
        entities[key] = entity_value

    return entities


def _optional_string(value: Any, field_name: str) -> str | None:
    if value is None:
        return None
    return _string(value, field_name)


def _string(value: Any, field_name: str) -> str:
    if not isinstance(value, str):
        raise FoundryPlanContractError(f"Foundry plan field {field_name} must be a string.")
    return value


def _bool(value: Any, field_name: str) -> bool:
    if not isinstance(value, bool):
        raise FoundryPlanContractError(f"Foundry plan field {field_name} must be a boolean.")
    return value
