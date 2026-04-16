import json
from pathlib import Path
from typing import Any

from loguru import logger


ISSUE_LIBRARY = {
    "EMPTY_DATASET": {
        "priority": "P0",
        "owner": "data-pipeline",
        "action": "检查采集链路、过滤条件和入库任务，确保日志数据可落盘",
        "pytest_assertion": "assert row_count > 0",
    },
    "HIGH_NULL_RATIO": {
        "priority": "P0",
        "owner": "schema-owner",
        "action": "修复关键字段写入逻辑，补齐 event/message/trace_id",
        "pytest_assertion": "assert null_ratio <= 0.1",
    },
    "INVALID_TIMESTAMP": {
        "priority": "P0",
        "owner": "logging-sdk",
        "action": "统一时间戳格式与时区，保证可被 pandas.to_datetime 解析",
        "pytest_assertion": "assert invalid_timestamp_ratio <= 0.2",
    },
    "HIGH_ERROR_DENSITY": {
        "priority": "P1",
        "owner": "service-owner",
        "action": "排查异常栈与超时路径，降低错误关键词密度",
        "pytest_assertion": "assert error_density <= 0.3",
    },
    "INVALID_LOG_LEVEL": {
        "priority": "P1",
        "owner": "logging-sdk",
        "action": "限制日志级别枚举，确保只输出合法 level 值",
        "pytest_assertion": "assert invalid_level_count == 0",
    },
    "HIGH_DUPLICATION": {
        "priority": "P2",
        "owner": "data-pipeline",
        "action": "去重或增加去重键，避免重复日志污染分析结果",
        "pytest_assertion": "assert duplicate_ratio < 0.2",
    },
    "MISSING_CORE_COLUMNS": {
        "priority": "P1",
        "owner": "schema-owner",
        "action": "补齐核心字段 timestamp/level/message/event/trace_id",
        "pytest_assertion": "assert missing_core_columns_count < 4",
    },
}


def build_remediation_plan(
    issue_report: dict[str, Any], output_path: str | Path
) -> dict[str, Any]:
    datasets = issue_report.get("datasets", [])
    issue_aggregate: dict[str, dict[str, Any]] = {}

    for dataset in datasets:
        source_file = dataset.get("source_file")
        table_name = dataset.get("table_name")
        issues = dataset.get("issues", [])
        for issue in issues:
            code = issue.get("code", "UNKNOWN")
            detail = issue.get("detail", "")
            info = ISSUE_LIBRARY.get(
                code,
                {
                    "priority": "P2",
                    "owner": "unknown",
                    "action": "补充该问题类型的修复策略",
                    "pytest_assertion": "assert True",
                },
            )
            if code not in issue_aggregate:
                issue_aggregate[code] = {
                    "issue_code": code,
                    "priority": info["priority"],
                    "owner": info["owner"],
                    "recommended_action": info["action"],
                    "pytest_assertion": info["pytest_assertion"],
                    "affected_targets": [],
                    "samples": [],
                    "count": 0,
                }
            issue_aggregate[code]["count"] += 1
            issue_aggregate[code]["affected_targets"].append(
                {"source_file": source_file, "table_name": table_name}
            )
            if detail and len(issue_aggregate[code]["samples"]) < 3:
                issue_aggregate[code]["samples"].append(detail)

    priority_order = {"P0": 0, "P1": 1, "P2": 2}
    items = sorted(
        issue_aggregate.values(),
        key=lambda item: (priority_order.get(item["priority"], 3), -item["count"]),
    )

    plan = {
        "total_issue_count": issue_report.get("total_issue_count", 0),
        "total_issue_types": len(items),
        "items": items,
    }

    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8")
    logger.info("已生成修复计划: {}", output_file)
    return plan


def generate_issue_pytest_skeleton(
    plan: dict[str, Any], output_path: str | Path
) -> Path:
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    # 读取现有测试文件内容（如果存在）
    existing_content = ""
    if output_file.exists():
        existing_content = output_file.read_text(encoding="utf-8")

    lines = []
    if not existing_content:
        lines.extend([
            "import pytest",
            "",
            "",
            "class TestIssueRemediation:",
        ])
    else:
        lines.extend(existing_content.splitlines())

    items = plan.get("items", [])
    if not items and not existing_content:
        lines.extend(
            [
                "    def test_no_detected_issues(self) -> None:",
                "        assert True",
            ]
        )
    else:
        for item in items:
            code = str(item.get("issue_code", "unknown")).lower()
            code = "".join(char if char.isalnum() else "_" for char in code).strip("_")
            test_name = f"test_remediate_{code}"
            
            # 检查是否已经存在该测试函数
            if any(f"def {test_name}" in line for line in lines):
                logger.info(f"测试用例 {test_name} 已存在，跳过。")
                continue

            priority = item.get("priority", "P2")
            action = item.get("recommended_action", "")
            assertion = item.get("pytest_assertion", "assert True")
            
            # 如果是新发现的问题，添加带 skip 的测试用例
            lines.extend(
                [
                    f'    @pytest.mark.skip(reason="{priority} 待修复: {action}")',
                    f"    def {test_name}(self) -> None:",
                    f"        {assertion}",
                    "",
                ]
            )

    content = "\n".join(lines).rstrip() + "\n"
    output_file.write_text(content, encoding="utf-8")
    logger.info("已增量更新 pytest 骨架: {}", output_file)
    return output_file
