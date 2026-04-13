import json
from pathlib import Path

from src.issue_detector import detect_log_issues


def test_detect_log_issues_finds_high_risk_signals(tmp_path: Path) -> None:
    logs_dir = tmp_path / "logs"
    rules_dir = tmp_path / "rules"
    logs_dir.mkdir()
    rules_dir.mkdir()

    records = [
        {
            "timestamp": "bad-time",
            "level": "INFO",
            "message": "request timeout error",
            "event": None,
            "trace_id": "t-1",
        },
        {
            "timestamp": "still-bad",
            "level": "BROKEN_LEVEL",
            "message": "fatal exception happened",
            "event": None,
            "trace_id": None,
        },
    ]
    (logs_dir / "risk.json").write_text(
        json.dumps(records, ensure_ascii=False),
        encoding="utf-8",
    )

    output_path = rules_dir / "detected_issues.json"
    report = detect_log_issues(logs_dir, output_path)

    assert output_path.exists()
    assert report["dataset_count"] == 1
    assert report["total_issue_count"] >= 4
    codes = {issue["code"] for issue in report["datasets"][0]["issues"]}
    assert "INVALID_TIMESTAMP" in codes
    assert "HIGH_ERROR_DENSITY" in codes
    assert "INVALID_LOG_LEVEL" in codes
