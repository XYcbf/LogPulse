import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd
from loguru import logger

from src.log_loader import load_logs


SUPPORTED_EXTENSIONS = {".json", ".jsonl", ".txt", ".log", ".db", ".sqlite", ".sqlite3"}
CORE_COLUMNS = ["timestamp", "time", "level", "message", "event", "trace_id"]
ERROR_KEYWORDS = ["error", "exception", "failed", "fatal", "timeout", "panic"]
LEVEL_VALUES = {
    "trace", "debug", "info", "warn", "warning", "error", "fatal", "critical",
    "v", "d", "i", "w", "e", "f", "s" # 增加 Logcat 常见的单字母级别
}


def detect_log_issues(log_dir: str | Path, output_path: str | Path) -> dict[str, Any]:
    log_root = Path(log_dir)
    if not log_root.exists():
        raise FileNotFoundError(f"日志目录不存在: {log_root}")

    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    datasets: list[dict[str, Any]] = []
    total_issues = 0

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
            for table_name in _list_sqlite_tables(log_file):
                dataframe = load_logs(log_file, table_name=table_name)
                issues, error_samples = _detect_dataset_issues(dataframe)
                total_issues += len(issues)
                datasets.append(
                    {
                        "source_file": str(log_file),
                        "source_type": "sqlite",
                        "table_name": table_name,
                        "row_count": int(len(dataframe)),
                        "issue_count": len(issues),
                        "issues": issues,
                        "error_samples": error_samples,
                    }
                )
            continue

        dataframe = load_logs(log_file)
        issues, error_samples = _detect_dataset_issues(dataframe)
        total_issues += len(issues)
        datasets.append(
            {
                "source_file": str(log_file),
                "source_type": "text",
                "table_name": None,
                "row_count": int(len(dataframe)),
                "issue_count": len(issues),
                "issues": issues,
                "error_samples": error_samples,
            }
        )

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "log_directory": str(log_root),
        "dataset_count": len(datasets),
        "total_issue_count": total_issues,
        "datasets": datasets,
    }
    output_file.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    logger.info("已生成问题排查报告: {}", output_file)
    return report


def _detect_dataset_issues(dataframe: pd.DataFrame) -> tuple[list[dict[str, Any]], list[str]]:
    issues: list[dict[str, Any]] = []
    error_samples: list[str] = []
    row_count = len(dataframe)

    if row_count == 0:
        issues.append(
            {
                "severity": "high",
                "code": "EMPTY_DATASET",
                "detail": "数据集为空，无法进行有效排查",
            }
        )
        return issues, []

    columns = [str(item) for item in dataframe.columns]
    normalized_columns = {column.lower(): column for column in columns}

    # Extract error samples early
    message_col = normalized_columns.get("message")
    if message_col is not None:
        messages = dataframe[message_col].fillna("").astype(str)
        error_mask = messages.str.lower().apply(
            lambda text: any(keyword in text for keyword in ERROR_KEYWORDS)
        )
        error_samples = messages[error_mask].unique()[:5].tolist()

    duplicate_ratio = float(dataframe.duplicated().mean())
    if duplicate_ratio >= 0.2:
        issues.append(
            {
                "severity": "medium",
                "code": "HIGH_DUPLICATION",
                "detail": f"重复行占比过高: {duplicate_ratio:.2%}",
            }
        )

    missing_core = [item for item in CORE_COLUMNS if item not in normalized_columns]
    if len(missing_core) >= 4:
        issues.append(
            {
                "severity": "medium",
                "code": "MISSING_CORE_COLUMNS",
                "detail": f"核心字段缺失较多: {missing_core}",
            }
        )

    for core in ["event", "message", "trace_id"]:
        actual = normalized_columns.get(core)
        if actual is None:
            continue
        null_ratio = float(dataframe[actual].isna().mean())
        if null_ratio > 0.1:
            issues.append(
                {
                    "severity": "high",
                    "code": "HIGH_NULL_RATIO",
                    "detail": f"{actual} 空值占比过高: {null_ratio:.2%}",
                }
            )

    timestamp_col = normalized_columns.get("timestamp") or normalized_columns.get("time")
    if timestamp_col is not None:
        parsed = pd.to_datetime(dataframe[timestamp_col], errors="coerce", format="mixed")
        invalid_ratio = float(parsed.isna().mean())
        if invalid_ratio > 0.2:
            issues.append(
                {
                    "severity": "high",
                    "code": "INVALID_TIMESTAMP",
                    "detail": f"{timestamp_col} 不可解析占比过高: {invalid_ratio:.2%}",
                }
            )

    level_col = normalized_columns.get("level")
    if level_col is not None:
        level_values = (
            dataframe[level_col].dropna().astype(str).str.strip().str.lower()
        )
        invalid_levels = sorted(set(level_values) - LEVEL_VALUES)
        if invalid_levels:
            issues.append(
                {
                    "severity": "medium",
                    "code": "INVALID_LOG_LEVEL",
                    "detail": f"存在未知日志级别: {invalid_levels[:10]}",
                }
            )

    if message_col is not None:
        messages_lower = dataframe[message_col].fillna("").astype(str).str.lower()
        error_hits = messages_lower.apply(
            lambda text: any(keyword in text for keyword in ERROR_KEYWORDS)
        )
        error_ratio = float(error_hits.mean())
        if error_ratio > 0.3:
            issues.append(
                {
                    "severity": "high",
                    "code": "HIGH_ERROR_DENSITY",
                    "detail": f"错误关键词密度过高: {error_ratio:.2%}",
                }
            )

    return issues, error_samples


def _list_sqlite_tables(path: Path) -> list[str]:
    with sqlite3.connect(path) as conn:
        names = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        ).fetchall()
    return [name[0] for name in names]
