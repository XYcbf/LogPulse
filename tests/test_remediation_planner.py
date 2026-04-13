from pathlib import Path

from src.remediation_planner import build_remediation_plan, generate_issue_pytest_skeleton


def test_build_remediation_plan_and_pytest_skeleton(tmp_path: Path) -> None:
    issue_report = {
        "total_issue_count": 3,
        "datasets": [
            {
                "source_file": "logs/a.json",
                "table_name": None,
                "issues": [
                    {"code": "INVALID_TIMESTAMP", "detail": "timestamp 不可解析占比过高"},
                    {"code": "HIGH_ERROR_DENSITY", "detail": "错误关键词密度过高"},
                ],
            },
            {
                "source_file": "logs/b.db",
                "table_name": "events",
                "issues": [
                    {"code": "EMPTY_DATASET", "detail": "数据为空"},
                ],
            },
        ],
    }

    plan_path = tmp_path / "rules" / "remediation_plan.json"
    plan = build_remediation_plan(issue_report, plan_path)
    assert plan_path.exists()
    assert plan["total_issue_count"] == 3
    assert plan["total_issue_types"] == 3
    assert plan["items"][0]["priority"] == "P0"

    skeleton_path = tmp_path / "tests" / "test_issue_remediation_generated.py"
    output_file = generate_issue_pytest_skeleton(plan, skeleton_path)
    assert output_file.exists()
    content = output_file.read_text(encoding="utf-8")
    assert "class TestIssueRemediation" in content
    assert "test_remediate_invalid_timestamp" in content
