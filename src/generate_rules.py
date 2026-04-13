import argparse
import json
from pathlib import Path

from src.issue_detector import detect_log_issues
from src.remediation_planner import build_remediation_plan, generate_issue_pytest_skeleton
from src.rule_generator import generate_tdd_rules
from src.root_cause_analyzer import analyze_root_cause


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--log-dir", dest="log_dir", default=None, metavar="FILE_OR_DIR")
    parser.add_argument("--output-dir", dest="output_dir", default=None)
    parser.add_argument("--tests-dir", dest="tests_dir", default=None)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    project_root = Path(__file__).resolve().parents[1]
    log_dir = Path(args.log_dir) if args.log_dir else project_root / "logs"
    output_dir = Path(args.output_dir) if args.output_dir else project_root / "rules"
    tests_dir = Path(args.tests_dir) if args.tests_dir else project_root / "tests"
    rules_output = output_dir / "generated_tdd_rules.json"
    report_output = output_dir / "detected_issues.json"
    plan_output = output_dir / "remediation_plan.json"
    analysis_output = output_dir / "root_cause_analysis.json"
    pytest_output = tests_dir / "test_issue_remediation_generated.py"

    generate_tdd_rules(log_dir, rules_output)
    report = detect_log_issues(log_dir, report_output)
    
    # Perform root cause analysis
    analysis = analyze_root_cause(report)
    analysis_output.write_text(json.dumps(analysis, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n{analysis['summary']}")
    for detail in analysis['details']:
        print(f" - {detail}")
    
    plan = build_remediation_plan(report, plan_output)
    generate_issue_pytest_skeleton(plan, pytest_output)


if __name__ == "__main__":
    main()
