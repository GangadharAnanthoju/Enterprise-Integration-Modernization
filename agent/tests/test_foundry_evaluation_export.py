import json
from pathlib import Path

from foundry.evaluation_export import (
    build_evaluation_dataset_records,
    evaluation_case_to_record,
    write_evaluation_dataset,
)
from foundry.evaluations import EvaluationCase, EvaluationExpectedOutcome, list_evaluation_cases


def test_evaluation_case_to_record_uses_foundry_ready_shape() -> None:
    case = EvaluationCase(
        case_id="eval-example",
        user_message="Check order ORD-1001",
        simulate_when_ready=True,
        expected=EvaluationExpectedOutcome(
            status="completed",
            selected_tool="getOrderStatus",
            ready_for_simulation=True,
            missing_entities=[],
            approval_required=False,
            tool_called=True,
            approval_request_created=False,
        ),
        expected_behavior="Select getOrderStatus and execute when risk allows it.",
    )

    record = evaluation_case_to_record(case)

    assert record["case_id"] == "eval-example"
    assert record["input"] == {
        "user_message": "Check order ORD-1001",
        "simulate_when_ready": True,
    }
    assert record["expected"] == {
        "status": "completed",
        "selected_tool": "getOrderStatus",
        "ready_for_simulation": True,
        "missing_entities": [],
        "approval_required": False,
        "tool_called": True,
        "approval_request_created": False,
    }
    assert record["evaluators"] == [
        "plan_contract",
        "governance_outcome",
        "safety_regression",
    ]


def test_build_evaluation_dataset_records_exports_all_local_cases() -> None:
    records = build_evaluation_dataset_records()

    assert [record["case_id"] for record in records] == [
        case.case_id for case in list_evaluation_cases()
    ]


def test_write_evaluation_dataset_writes_deterministic_jsonl() -> None:
    output_path = Path(".test-output") / "enterprise-mcp-regression.jsonl"

    try:
        written_path = write_evaluation_dataset(output_path)

        assert written_path == output_path
        lines = output_path.read_text(encoding="utf-8").splitlines()
        assert len(lines) == len(list_evaluation_cases())

        parsed_records = [json.loads(line) for line in lines]
        assert parsed_records == build_evaluation_dataset_records()

        write_evaluation_dataset(output_path)
        assert output_path.read_text(encoding="utf-8").splitlines() == lines
    finally:
        output_path.unlink(missing_ok=True)
        try:
            output_path.parent.rmdir()
        except OSError:
            pass
