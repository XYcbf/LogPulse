import json
import sqlite3
import re
from pathlib import Path
from typing import Any

import pandas as pd
from loguru import logger

# 常用的 Logcat 模式定义
LOGCAT_PATTERNS = [
    # 模式 1: 03-26 10:15:33 3310 7694 [info.red.virtual, DefaultDispatcher-worker-5] Message
    re.compile(r"^(?P<time>\d{2}-\d{2}\s\d{2}:\d{2}:\d{2})\s+(?P<pid>\d+)\s+(?P<tid>\d+)\s+\[(?P<tag>[^,\]]+).*?\]\s+(?P<message>.*)$"),
    
    # 模式 2: 03-26 10:14:40.139 E/LoadedApk( 3310): Message
    re.compile(r"^(?P<time>\d{2}-\d{2}\s\d{2}:\d{2}:\d{2}\.\d{3})\s+(?P<level>[A-Z])/(?P<tag>[^\(]+)\(\s*(?P<pid>\d+)\):\s+(?P<message>.*)$"),
    
    # 模式 3: I/ActivityManager(  585): Message
    re.compile(r"^(?P<level>[A-Z])/(?P<tag>[^\(]+)\(\s*(?P<pid>\d+)\):\s+(?P<message>.*)$"),
]

def load_json_logs(file_path: str | Path) -> pd.DataFrame:
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"日志文件不存在: {path}")

    raw_text = _read_text(path)
    if not raw_text:
        logger.warning("日志文件为空: {}", path)
        return pd.DataFrame()

    records = _load_json_text(raw_text, path)
    logger.info("已从 {} 读取 {} 条 JSON 日志", path, len(records))
    return pd.DataFrame(records)


def load_logs(file_path: str | Path, table_name: str | None = None) -> pd.DataFrame:
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"日志文件不存在: {path}")

    suffix = path.suffix.lower()
    if suffix in {".json", ".jsonl"}:
        return load_json_logs(path)

    if suffix in {".txt", ".log"}:
        raw_text = _read_text(path)
        if not raw_text:
            logger.warning("日志文件为空: {}", path)
            return pd.DataFrame()
        try:
            records = _load_json_text(raw_text, path)
            logger.info("已按 JSON/TXT 解析 {}，共 {} 条", path, len(records))
            return pd.DataFrame(records)
        except ValueError:
            # 如果不是 JSON，尝试使用 Logcat 模式解析
            rows = []
            for index, line in enumerate(raw_text.splitlines(), start=1):
                if not line.strip():
                    continue
                
                # 尝试匹配已知的 Logcat 模式
                parsed = _parse_logcat_line(line)
                if parsed:
                    parsed["line_no"] = index
                    rows.append(parsed)
                else:
                    # 无法匹配任何模式，作为普通文本行
                    rows.append({"line_no": index, "message": line})
            
            logger.info("已通过智能 Logcat 解析 {}，共 {} 行", path, len(rows))
            return pd.DataFrame(rows)

    if suffix in {".db", ".sqlite", ".sqlite3"}:
        return _load_sqlite_logs(path, table_name)

    raise ValueError(f"不支持的日志文件类型: {suffix}")


def _parse_logcat_line(line: str) -> dict[str, Any] | None:
    """尝试使用预定义的正则模式解析 Logcat 行。"""
    for pattern in LOGCAT_PATTERNS:
        match = pattern.match(line)
        if match:
            return match.groupdict()
    return None


def _normalize_records(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        if all(isinstance(item, dict) for item in payload):
            return payload
        raise ValueError("JSON 数组中的每一项必须是对象")

    if isinstance(payload, dict):
        if "logs" in payload and isinstance(payload["logs"], list):
            logs = payload["logs"]
            if all(isinstance(item, dict) for item in logs):
                return logs
            raise ValueError("logs 字段中的每一项必须是对象")
        return [payload]

    raise ValueError("不支持的 JSON 日志结构，需为对象或对象数组")


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore").lstrip("\ufeff").strip()


def _load_json_text(raw_text: str, path: Path) -> list[dict[str, Any]]:
    try:
        parsed = json.loads(raw_text)
        return _normalize_records(parsed)
    except json.JSONDecodeError:
        return _load_json_lines(raw_text, path)


def _load_json_lines(raw_text: str, path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for index, line in enumerate(raw_text.splitlines(), start=1):
        line = line.strip()
        if not line:
            continue
        try:
            item = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"无效的 JSON Lines 格式: 第 {index} 行") from exc
        if not isinstance(item, dict):
            raise ValueError(f"JSON Lines 第 {index} 行不是对象: {path}")
        records.append(item)
    return records


def _load_sqlite_logs(path: Path, table_name: str | None) -> pd.DataFrame:
    with sqlite3.connect(path) as conn:
        tables = pd.read_sql_query(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name",
            conn,
        )["name"].tolist()

        if not tables:
            logger.warning("SQLite 文件无数据表: {}", path)
            return pd.DataFrame()

        if table_name is None:
            target_table = tables[0]
        else:
            if table_name not in tables:
                raise ValueError(
                    f"指定表不存在: {table_name}，可用表: {', '.join(tables)}"
                )
            target_table = table_name

        data = pd.read_sql_query(f"SELECT * FROM [{target_table}]", conn)
        logger.info(
            "已从 {} 的表 {} 读取 {} 条日志",
            path,
            target_table,
            len(data),
        )
        return data
