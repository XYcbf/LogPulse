import json
import sqlite3
from pathlib import Path

from src.rule_generator import generate_tdd_rules


def test_generate_tdd_rules_creates_output_for_mixed_logs(tmp_path: Path) -> None:
    logs_dir = tmp_path / "logs"
    rules_dir = tmp_path / "rules"
    logs_dir.mkdir()
    rules_dir.mkdir()

    (logs_dir / "biz.json").write_text(
        json.dumps([{"event": "login", "message": "ok", "level": "INFO"}]),
        encoding="utf-8",
    )
    (logs_dir / "plain.txt").write_text("line-1\nline-2", encoding="utf-8")

    db_path = logs_dir / "events.db"
    conn = sqlite3.connect(db_path)
    conn.execute("CREATE TABLE t_events(id INTEGER, event TEXT)")
    conn.execute("INSERT INTO t_events VALUES(1, 'pay')")
    conn.commit()
    conn.close()

    output_path = rules_dir / "generated_tdd_rules.json"
    result = generate_tdd_rules(logs_dir, output_path)

    assert output_path.exists()
    assert result["dataset_count"] == 3
    assert len(result["datasets"]) == 3
    assert any(item["source_type"] == "sqlite" for item in result["datasets"])
