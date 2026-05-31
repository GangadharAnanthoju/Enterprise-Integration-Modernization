"""Export local evaluation cases into Foundry-ready dataset records."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

from foundry.evaluations import EvaluationCase, list_evaluation_cases


DEFAULT_DATASET_PATH = (
    Path(__file__).resolve().parents[3]
    / "foundry"
    / "evaluations"
    / "datasets"
    / "enterprise-mcp-regression.jsonl"
)


def evaluation_case_to_record(case: EvaluationCase) -> dict[str, object]:
    """Convert one local evaluation case into a reviewable Foundry dataset row."""

    expected = case.expected
    return {
        "case_id": case.case_id,
        "input": {
            "user_message": case.user_message,
            "simulate_when_ready": case.simulate_when_ready,
        },
        "expected": {
            "status": expected.status,
            "selected_tool": expected.selected_tool,
            "ready_for_simulation": expected.ready_for_simulation,
            "missing_entities": expected.missing_entities,
            "approval_required": expected.approval_required,
            "tool_called": expected.tool_called,
            "approval_request_created": expected.approval_request_created,
        },
        "expected_behavior": case.expected_behavior,
        "evaluators": [
            "plan_contract",
            "governance_outcome",
            "safety_regression",
        ],
    }


def build_evaluation_dataset_records(
    cases: Iterable[EvaluationCase] | None = None,
) -> list[dict[str, object]]:
    """Build deterministic dataset records from local evaluation cases."""

    source_cases = list(cases) if cases is not None else list_evaluation_cases()
    return [evaluation_case_to_record(case) for case in source_cases]


def write_evaluation_dataset(
    output_path: Path = DEFAULT_DATASET_PATH,
    cases: Iterable[EvaluationCase] | None = None,
) -> Path:
    """Write local evaluation cases as JSONL and return the output path."""

    records = build_evaluation_dataset_records(cases)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [json.dumps(record, sort_keys=True) for record in records]
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return output_path


if __name__ == "__main__":
    path = write_evaluation_dataset()
    print(path)
