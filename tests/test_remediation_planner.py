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
    assert "test_remediate_high_error_density" in content

    # 模拟第二次生成，包含一个新问题
    new_issue_report = {
        "total_issue_count": 1,
        "datasets": [
            {
                "source_file": "logs/c.json",
                "table_name": None,
                "issues": [
                    {"code": "MISSING_CORE_COLUMNS", "detail": "缺失核心字段"},
                ],
            }
        ],
    }
    new_plan = build_remediation_plan(new_issue_report, tmp_path / "rules" / "new_plan.json")
    
    # 再次生成，应该保留旧的测试用例，并添加新的
    output_file_2 = generate_issue_pytest_skeleton(new_plan, skeleton_path)
    content_2 = output_file_2.read_text(encoding="utf-8")
    
    # 验证历史用例是否还在
    assert "test_remediate_invalid_timestamp" in content_2
    assert "test_remediate_high_error_density" in content_2
    # 验证新用例是否已添加
    assert "test_remediate_missing_core_columns" in content_2
