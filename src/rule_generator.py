import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from loguru import logger

from src.log_loader import load_logs


SUPPORTED_EXTENSIONS = {".json", ".jsonl", ".txt", ".log", ".db", ".sqlite", ".sqlite3"}


def generate_tdd_rules(log_dir: str | Path, output_path: str | Path) -> dict[str, Any]:
    log_root = Path(log_dir)
    if not log_root.exists():
        raise FileNotFoundError(f"日志目录不存在: {log_root}")

    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    datasets: list[dict[str, Any]] = []
    log_files: list[Path] = []
    if log_root.is_file():
        log_files.append(log_root)
    elif log_root.is_dir():
        for log_file in sorted(log_root.iterdir()):
            if not log_file.is_file():
                continue
            log_files.append(log_file)
    else:
        raise ValueError(f"不支持的日志路径类型: {log_root}")

    for log_file in log_files:
        if log_file.suffix.lower() not in SUPPORTED_EXTENSIONS:
            continue

        if log_file.suffix.lower() in {".db", ".sqlite", ".sqlite3"}:
            tables = _list_sqlite_tables(log_file)
            for table_name in tables:
                dataframe = load_logs(log_file, table_name=table_name)
                datasets.append(
                    {
                        "source_file": str(log_file),
                        "source_type": "sqlite",
                        "table_name": table_name,
                        "row_count": int(len(dataframe)),
                        "rules": _build_rules(dataframe),
                    }
                )
            continue

        dataframe = load_logs(log_file)
        datasets.append(
            {
                "source_file": str(log_file),
                "source_type": "text",
                "table_name": None,
                "row_count": int(len(dataframe)),
                "rules": _build_rules(dataframe),
            }
        )

    result = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "log_directory": str(log_root),
        "dataset_count": len(datasets),
        "datasets": datasets,
    }
    output_file.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    logger.info("已生成 TDD 规则文件: {}", output_file)
    return result


def _build_rules(dataframe) -> list[dict[str, Any]]:
    if dataframe.empty:
        return [
            {
                "rule": "dataset_not_empty",
                "check": "row_count > 0",
                "severity": "high",
            }
        ]

    columns = [str(name) for name in dataframe.columns]
    null_ratios = (dataframe.isna().mean().to_dict() if len(dataframe) > 0 else {})
    unique_ratios = (
        (dataframe.nunique(dropna=False) / max(len(dataframe), 1)).to_dict()
        if len(dataframe.columns) > 0
        else {}
    )

    core_columns = []
    for candidate in ["timestamp", "time", "level", "message", "event", "trace_id"]:
        if candidate in columns:
            core_columns.append(candidate)

    rules: list[dict[str, Any]] = [
        {
            "rule": "dataset_not_empty",
            "check": "row_count > 0",
            "severity": "high",
        },
        {
            "rule": "required_columns_present",
            "check": f"columns include {columns}",
            "severity": "high",
        },
    ]

    if core_columns:
        rules.append(
            {
                "rule": "core_columns_not_null",
                "check": f"{core_columns} null_ratio < 0.05",
                "severity": "high",
            }
        )

    quality_targets = [
        column for column, ratio in null_ratios.items() if isinstance(ratio, (int, float))
    ]
    if quality_targets:
        rules.append(
            {
                "rule": "null_ratio_threshold",
                "check": f"all columns null_ratio <= 0.3, observed={null_ratios}",
                "severity": "medium",
            }
        )

    stable_keys = [
        column
        for column, ratio in unique_ratios.items()
        if isinstance(ratio, (int, float)) and ratio < 0.98
    ]
    if stable_keys:
        rules.append(
            {
                "rule": "categorical_stability",
                "check": f"distribution drift check on columns={stable_keys}",
                "severity": "medium",
            }
        )

    return rules


def _list_sqlite_tables(path: Path) -> list[str]:
    with sqlite3.connect(path) as conn:
        names = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        ).fetchall()
    return [name[0] for name in names]
