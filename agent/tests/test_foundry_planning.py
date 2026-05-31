import pytest

from foundry.planning import (
    FoundryPlanContractError,
    parse_foundry_action_plan,
    validate_foundry_action_plan,
)


def test_parse_foundry_action_plan_accepts_valid_json() -> None:
    plan = parse_foundry_action_plan(
        """
        {
          "selected_tool": "getOrderStatus",
          "entities": {"order_id": "ORD-1001"},
          "requires_clarification": false,
          "clarification_question": null,
          "confidence": "high",
          "reason": "The user asked to check an order status."
        }
        """
    )

    assert plan.selected_tool == "getOrderStatus"
    assert plan.entities == {"order_id": "ORD-1001"}
    assert plan.requires_clarification is False
    assert plan.confidence == "high"


def test_parse_foundry_action_plan_accepts_json_code_fence() -> None:
    plan = parse_foundry_action_plan(
        """
        ```json
        {
          "selected_tool": "validateInvoice",
          "entities": {"invoice_id": "INV-2001"},
          "requires_clarification": false,
          "clarification_question": null,
          "confidence": "medium",
          "reason": "The user asked to validate an invoice."
        }
        ```
        """
    )

    assert plan.selected_tool == "validateInvoice"
    assert plan.entities == {"invoice_id": "INV-2001"}


def test_parse_foundry_action_plan_rejects_unsupported_tool() -> None:
    with pytest.raises(FoundryPlanContractError, match="unsupported tool"):
        parse_foundry_action_plan(
            """
            {
              "selected_tool": "deletePurchaseOrder",
              "entities": {"order_id": "ORD-1001"},
              "requires_clarification": false,
              "clarification_question": null,
              "confidence": "high",
              "reason": "Unsupported destructive request."
            }
            """
        )


def test_parse_foundry_action_plan_requires_clarification_question() -> None:
    with pytest.raises(FoundryPlanContractError, match="clarification_question"):
        parse_foundry_action_plan(
            """
            {
              "selected_tool": "getOrderStatus",
              "entities": {},
              "requires_clarification": true,
              "clarification_question": null,
              "confidence": "medium",
              "reason": "The order ID is missing."
            }
            """
        )


def test_validate_foundry_action_plan_finds_missing_required_entities() -> None:
    plan = parse_foundry_action_plan(
        """
        {
          "selected_tool": "getOrderStatus",
          "entities": {},
          "requires_clarification": true,
          "clarification_question": "Please provide the order ID.",
          "confidence": "medium",
          "reason": "The user asked for order status without an order ID."
        }
        """
    )

    validation = validate_foundry_action_plan(plan)

    assert validation.selected_tool == "getOrderStatus"
    assert validation.selected_tool_supported is True
    assert validation.missing_entities == ["order_id"]
    assert validation.ready_for_governance is False


def test_validate_foundry_action_plan_marks_ready_plan() -> None:
    plan = parse_foundry_action_plan(
        """
        {
          "selected_tool": "checkShipmentStatus",
          "entities": {"shipment_id": "SHIP-3001"},
          "requires_clarification": false,
          "clarification_question": null,
          "confidence": "high",
          "reason": "The user asked to check shipment status."
        }
        """
    )

    validation = validate_foundry_action_plan(plan)

    assert validation.selected_tool == "checkShipmentStatus"
    assert validation.missing_entities == []
    assert validation.ready_for_governance is True


def test_parse_foundry_action_plan_allows_unsupported_request_clarification() -> None:
    plan = parse_foundry_action_plan(
        """
        {
          "selected_tool": null,
          "entities": {},
          "requires_clarification": true,
          "clarification_question": "I can help with approved integration workflows.",
          "confidence": "low",
          "reason": "No approved tool matches the request."
        }
        """
    )

    validation = validate_foundry_action_plan(plan)

    assert plan.selected_tool is None
    assert validation.selected_tool_supported is True
    assert validation.ready_for_governance is False
